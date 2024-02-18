from abc import ABC
from typing import Optional
from lgt_jobs.lgt_common.lgt_logging import log
from lgt_jobs.lgt_common.slack_client.web_client import SlackWebClient
from lgt_jobs.lgt_data.mongo_repository import UserLeadMongoRepository, DedicatedBotRepository
from pydantic import BaseModel
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Send Slack Message
"""


class SendSlackMessageJobData(BaseBackgroundJobData, BaseModel):
    lead_id: str
    user_id: str
    text: Optional[str]
    files_ids: Optional[list]


class SendSlackMessageJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return SendSlackMessageJobData

    def exec(self, data: SendSlackMessageJobData):
        user_leads_repository = UserLeadMongoRepository()
        lead = user_leads_repository.get_lead(user_id=data.user_id, lead_id=data.lead_id)
        if not lead:
            return

        bot = DedicatedBotRepository().get_one(user_id=data.user_id, source_id=data.source_id, only_valid=True)
        if not bot:
            return

        slack_client = SlackWebClient(bot.token, bot.cookies)
        resp = slack_client.im_open(lead.message.sender_id)
        if not resp['ok']:
            log.warning(f"Unable to open im with user: {resp}")
            return

        channel_id = resp['channel']['id']
        if data.files_ids:
            slack_client.share_files(data.files_ids, channel_id, data.text)
        else:
            slack_client.post_message(channel_id, data.text)
