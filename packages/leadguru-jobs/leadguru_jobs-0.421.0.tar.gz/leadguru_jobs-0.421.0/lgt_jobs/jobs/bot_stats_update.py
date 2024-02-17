import random
import time
from abc import ABC
from typing import Optional
from lgt_jobs.lgt_common.discord_client.discord_client import DiscordClient
from lgt_jobs.lgt_common.helpers import get_formatted_bot_name
from lgt_jobs.lgt_common.slack_client.web_client import SlackWebClient
from lgt_jobs.lgt_data.enums import SourceType
from lgt_jobs.lgt_data.model import DedicatedBotModel, Server, Channel, DiscordUser
from lgt_jobs.lgt_data.mongo_repository import DedicatedBotRepository, UserMongoRepository
from pydantic import BaseModel
from lgt_jobs.lgt_data.analytics import get_bots_aggregated_analytics
from lgt_jobs.lgt_common.lgt_logging import log
from lgt_jobs.lgt_common.enums.slack_errors import SlackErrors
from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData

"""
Update bots statistics
"""


class BotStatsUpdateJobData(BaseBackgroundJobData, BaseModel):
    bot_id: Optional[str]


class BotStatsUpdateJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return BotStatsUpdateJobData

    def exec(self, data: BotStatsUpdateJobData):
        bots_rep = DedicatedBotRepository()
        users_rep = UserMongoRepository()
        bot = bots_rep.get_one(id=data.bot_id, include_deleted=True)

        if bot.source.source_type == SourceType.DISCORD:
            client = DiscordClient(bot.token)
            servers_response = client.get_servers()

            if isinstance(servers_response, dict):
                if servers_response.get('message') == '401: Unauthorized':
                    BotStatsUpdateJob.__updated_invalid_creds_flag(bot, True)
                log.warning(f"[BotStatsUpdateJob]: Servers response is not list: {servers_response}")
                return

            discord_servers = [Server.from_dic(server) for server in servers_response]
            user = users_rep.get(bot.user_id)
            discord_user: DiscordUser = user.get_discord_user(bot.user_name)
            if discord_user:
                discord_user.workspaces = discord_servers
                users_rep.set(user.id, discord_users=[user.to_dic() for user in user.discord_users])
            for discord_server in discord_servers:
                server = next(filter(lambda x: x.id == discord_server.id, bot.servers), None)
                if server:
                    discord_server.active = server.active
                    discord_server.deleted = server.deleted
                else:
                    discord_server.deleted = True
                discord_channels = [Channel.from_dic(channel) for channel in client.get_channels(discord_server.id)
                                    if channel.get('type', 0) == 0]
                for discord_channel in discord_channels:
                    if server:
                        channel = next(filter(lambda x: x.id == discord_channel.id, server.channels), None)
                        if channel:
                            discord_channel.active = channel.active
                discord_server.channels = discord_channels
                if discord_server.icon:
                    discord_server.icon = (f'https://cdn.discordapp.com/icons/{discord_server.id}/'
                                           f'{discord_server.icon}.png')
                time.sleep(random.randint(1, 2))

            bot.servers = discord_servers
            bots_rep.add_or_update(bot)

            return

        client = SlackWebClient(bot.token, bot.cookies)
        test_auth_response = client.test_auth()
        if not test_auth_response.status_code == 200:
            log.warning(f"[BotStatsUpdateJob]: Error to auth {data.bot_id}. {test_auth_response.content}")
            return

        if not bot.invalid_creds:
            error = test_auth_response.json().get("error")
            if error == SlackErrors.INVALID_AUTH or error == SlackErrors.TWO_FACTOR_REQUIRED:
                BotStatsUpdateJob.__updated_invalid_creds_flag(bot, True)

        user = test_auth_response.json().get('user_id')
        bot.associated_user = user
        bots_rep.add_or_update(bot)
        team_info = {}
        try:
            team_info = client.get_team_info()
        except:
            log.warning(f"[BotStatsUpdateJob]: Error to get  team info of {data.bot_id}. {test_auth_response.content}")

        if team_info.get('ok'):
            bot_name = get_formatted_bot_name(team_info['team']['domain'])
            if bot.servers:
                bot.servers[0].name = bot_name
            bot.source.source_name = bot_name
            bot.slack_url = bot.registration_link = team_info['team']['url']
            bots_rep.add_or_update(bot)
        received_messages, filtered_messages = get_bots_aggregated_analytics(bot_ids=[bot.id])
        try:
            channels_response = client.channels_list()
        except:
            log.warning(f"[BotStatsUpdateJob]: Error to get channels list for bot {bot.id}.")
            return

        if not channels_response['ok']:
            if channels_response.get("error") == SlackErrors.INVALID_AUTH:
                BotStatsUpdateJob.__updated_invalid_creds_flag(bot, True)
            else:
                log.warning(f"[BotStatsUpdateJob]: Error during update bot {bot.id} stats. Error: {channels_response}")
            return
        channels = channels_response['channels']
        connected_channels = 0
        channels_users = {}
        active_channels = {}
        users_count = 0
        for channel in channels:
            if channel['is_member']:
                active_channels[channel['id']] = channel['name']
                connected_channels += 1
            num_members = channel.get('num_members', 0)
            channels_users[channel['id']] = num_members
            users_count += num_members

        bot.active_channels = active_channels
        bot.messages_received = received_messages.get(bot.source.source_name, 0)
        bot.messages_filtered = filtered_messages.get(bot.source.source_name, 0)
        bot.connected_channels = connected_channels
        bot.channels = len(channels)
        bot.channels_users = channels_users
        if bot.recent_messages is None:
            bot.recent_messages = []
        if bot.servers:
            channels = [Channel.from_dic(channel_dict) for channel_dict in channels]
            for channel in bot.servers[0].channels:
                slack_channel: Channel = next(filter(lambda x: x.id == channel.id, channels), None)
                if slack_channel:
                    slack_channel.active = channel.active
            bot.servers[0].channels = channels
            bot.servers[0].subscribers = users_count

        # save only last 50 messages
        bot.recent_messages = bot.recent_messages[-50:]
        bots_rep.add_or_update(bot)

    @staticmethod
    def __updated_invalid_creds_flag(bot: DedicatedBotModel, invalid_creds: bool):
        if bot.invalid_creds != invalid_creds:
            bot.invalid_creds = invalid_creds
            DedicatedBotRepository().add_or_update(bot)
