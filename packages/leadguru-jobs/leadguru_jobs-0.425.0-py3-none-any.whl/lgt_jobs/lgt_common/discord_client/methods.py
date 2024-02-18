from enum import Enum


class DiscordMethods(str, Enum):
    USER_GUILDS = 'users/@me/guilds'
    USER_DMS = 'users/@me/channels'
    USER = 'users/@me'
    LOGIN = 'auth/login'

    @staticmethod
    def guild_channels(guild_id: str):
        return f'guilds/{guild_id}/channels'

    @staticmethod
    def channels_invites(channel_id: str):
        return f'channels/{channel_id}/invites'
