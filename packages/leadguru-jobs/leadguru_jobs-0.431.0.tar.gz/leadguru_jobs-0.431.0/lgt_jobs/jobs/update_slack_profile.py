from abc import ABC
from lgt_jobs.lgt_common.slack_client.slack_client import SlackClient
from lgt_jobs.lgt_data.enums import SourceType
from lgt_jobs.lgt_data.model import UserModel
from lgt_jobs.lgt_data.mongo_repository import UserMongoRepository, DedicatedBotRepository
from pydantic import BaseModel
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob


class UpdateExternalUserProfileJobData(BaseBackgroundJobData, BaseModel):
    user_id: str


class UpdateExternalUserProfileJob(BaseBackgroundJob, ABC):

    @property
    def job_data_type(self) -> type:
        return UpdateExternalUserProfileJobData

    def exec(self, data: UpdateExternalUserProfileJobData):
        user = UserMongoRepository().get(data.user_id)
        bots = DedicatedBotRepository().get_all(user_id=data.user_id, only_valid=True, include_deleted=False)
        for bot in bots:
            if bot.type == SourceType.SLACK:
                slack = SlackClient(bot.token, bot.cookies)
                UpdateExternalUserProfileJob.__update_slack_profile(user, slack)

    @staticmethod
    def __update_slack_profile(user: UserModel, slack: SlackClient):
        profile = slack.get_team_profile()
        title_section_id = None
        title_field_id = None
        skype_section_id = None
        for field_data in profile.get('profile', {}).get('fields', []):
            if field_data.get('field_name') == 'title':
                title_section_id = field_data.get('section_id')
                title_field_id = field_data.get('id')
                break
        for section_data in profile.get('profile', {}).get('sections', []):
            if section_data.get('label') == 'About me':
                skype_section_id = section_data.get('id')
                break

        slack.update_profile(user.slack_profile.to_dic())
        auth = slack.test_auth().json()
        user_id = auth.get('user_id')
        title_element_id = title_field_id.replace(title_field_id[:2], 'Pe')
        response = slack.update_section(user_id, title_section_id, title_element_id, user.slack_profile.title)
        sections = response['result']['data']['setProfileSection']['profileSections']
        elements = []
        for section in sections:
            if section['label'] == 'About me':
                elements = section['profileElements']
                break
        skype_element_id = None
        for element in elements:
            if element['label'] == 'Skype':
                skype_element_id = element['elementId']
                break
        slack.update_section(user_id, skype_section_id, skype_element_id, user.slack_profile.title)
        # try to update user photo
        if user.photo_url:
            slack.update_profile_photo(user.photo_url)
