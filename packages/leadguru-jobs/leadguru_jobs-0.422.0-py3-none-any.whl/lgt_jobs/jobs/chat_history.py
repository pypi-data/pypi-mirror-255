import datetime
from abc import ABC
from typing import Optional, List
from lgt_jobs.lgt_common.lgt_logging import log
from lgt_jobs.lgt_common.slack_client.web_client import SlackWebClient, SlackMessageConvertService
from lgt_jobs.lgt_data.model import ChatMessage, UserModel, UserContact, DedicatedBotModel
from lgt_jobs.lgt_data.mongo_repository import UserMongoRepository, DedicatedBotRepository, UserContactsRepository, \
    ChatRepository
from pydantic import BaseModel
from lgt_jobs.lgt_data.enums import SourceType
from lgt_jobs.runner import BaseBackgroundJob, BaseBackgroundJobData, BackgroundJobRunner
from ..env import portal_url
from ..smtp import SendMailJobData, SendMailJob

"""
Load slack chat history
"""


class LoadChatHistoryJobData(BaseBackgroundJobData, BaseModel):
    user_id: str
    template_path: str = 'lgt_jobs/templates/new_message_mail_template.html'


class LoadChatHistoryJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return LoadChatHistoryJobData

    def exec(self, data: LoadChatHistoryJobData):
        user = UserMongoRepository().get(data.user_id)
        bots = DedicatedBotRepository().get_all(only_valid=True, user_id=user.id, source_type=SourceType.SLACK)
        if not bots:
            return
        last_message = None
        last_message_contact = None
        for bot in bots:
            contacts = UserContactsRepository().find(user.id, spam=False, source_id=bot.source.source_id)
            if not contacts:
                continue

            log.info(f"[LoadChatHistoryJob]: processing {len(contacts)} contacts for user: {user.email}")
            for contact in contacts:
                message = LoadChatHistoryJob._update_history(user=user, contact=contact, bot=bot)

                if not message:
                    continue

                if not last_message:
                    last_message = message
                    last_message_contact = contact

                if message.created_at > last_message.created_at and message.user == contact.sender_id:
                    last_message = message
                    last_message_contact = contact

        has_to_be_notified = (not user.new_message_notified_at or
                              (last_message and last_message.created_at > user.new_message_notified_at))

        if last_message and has_to_be_notified and last_message.user == last_message_contact.sender_id:
            LoadChatHistoryJob._notify_about_new_messages(user, last_message_contact, data.template_path)
            UserMongoRepository().set(data.user_id, new_message_notified_at=datetime.datetime.now(datetime.UTC))

    @staticmethod
    def _get_new_messages(contact: UserContact, bot: DedicatedBotModel, slack_chat: List[ChatMessage]):
        chat_repo = ChatRepository()
        messages = chat_repo.get_list(sender_id=contact.sender_id, bot_id=bot.id)
        new_messages = []
        for message in slack_chat:
            same_messages = [msg for msg in messages if msg.id == message.id]
            if not same_messages:
                new_messages.append(message)
        return new_messages

    @staticmethod
    def _update_history(user: UserModel, contact: UserContact, bot: DedicatedBotModel) -> Optional[ChatMessage]:
        if bot.type == SourceType.SLACK:
            slack_client = SlackWebClient(bot.token, bot.cookies)
            try:
                chat_id = slack_client.im_open(contact.sender_id).get('channel', {}).get('id')
                history = slack_client.chat_history(chat_id)
            except Exception as ex:
                log.error(f'[LoadChatHistoryJob]: Failed to load chat for the contact: {contact.id}. ERROR: {str(ex)}')
                return

            if not history['ok']:
                log.error(f'Failed to load chat for the contact: {contact.id}. ERROR: {history.get("error", "")}')
                return

            messages = history.get('messages', [])
            if not messages:
                return None

            messages = [SlackMessageConvertService.from_slack_response(user.email, "slack_files",
                                                                       bot.token, m, contact.sender_id, bot.id,
                                                                       user.id, bot.cookies) for m in messages]
            new_messages = LoadChatHistoryJob._get_new_messages(contact, bot, messages)
            chat_history = [message.to_dic() for message in new_messages]
            ChatRepository().upsert_messages(chat_history)
            return new_messages[-1] if bot.associated_user != contact.sender_id else None

    @staticmethod
    def _notify_about_new_messages(user: UserModel, contact: UserContact, template_path: str):
        with open(template_path, mode='r') as template_file:
            html = template_file.read()
            html = html.replace("{sender}", contact.name if hasattr(contact, 'name') else contact.real_name)
            html = html.replace("{view_message_link}", f'{portal_url}/')

            message_data = {
                "html": html,
                "subject": 'New message(s) on LEADGURU',
                "recipient": user.email,
                "sender": None
            }

        BackgroundJobRunner.submit(SendMailJob, SendMailJobData(**message_data))
