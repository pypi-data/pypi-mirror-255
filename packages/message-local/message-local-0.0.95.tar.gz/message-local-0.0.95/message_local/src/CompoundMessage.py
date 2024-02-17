import json
import random

from database_mysql_local.generic_crud import GenericCRUD
from logger_local.MetaLogger import MetaLogger
from profiles_local.profiles_local import ProfilesLocal
from user_context_remote.user_context import UserContext
from variable_local.template import ReplaceFieldsWithValues

from .MessageChannels import MessageChannel
from .MessageConstants import object_message
from .MessageTemplates import MessageTemplates
from .Recipient import Recipient

user_context = UserContext()

lang_code_cache = {}


class CompoundMessage(GenericCRUD, metaclass=MetaLogger, object=object_message):
    def __init__(self, campaign_id: int = None, message_template_id: int = None, body: str = None, subject: str = None,
                 recipients: list[Recipient] = None, message_id: int = None, is_test_data: bool = False):
        super().__init__(default_schema_name="message", default_table_name="message_table",
                         default_view_table_name="message_view", default_id_column_name="message_id",
                         is_test_data=is_test_data)

        self.campaign_id = campaign_id
        self.message_template_id = message_template_id
        self.body = body
        self.subject = subject
        self.recipients = recipients
        self.message_id = message_id
        self.__compound_message = {}

        self.profile_local = ProfilesLocal()
        self.message_template = MessageTemplates()
        self.set_compound_message_after_text_template()
        user_context.login_using_user_identification_and_password()

    def _get_template_ids_by_campaign(self, campaign_id: int) -> list[int]:
        """Returns a random template id from the campaign"""

        possible_template_ids = self.select_multi_tuple_by_id(
            schema_name="campaign", view_table_name="campaign_view",
            id_column_name="campaign_id", id_column_value=campaign_id,
            select_clause_value="message_template_id")

        possible_template_ids = [message_template_id[0] for message_template_id in possible_template_ids]

        return possible_template_ids

    def set_compound_message_after_text_template(
            self, campaign_id: int = None, message_template_id: int = None, body: str = None, subject: str = None,
            recipients: list[Recipient] = None, message_id: int = None) -> None:
        """:returns
    {
        'DEFAULT': {
            'bodyBlocks': [{
                'blockId': ...,
                'blockTypeId': ...,
                'blockTypeName': ...,
                'questionId': ...,
                'questionTypeId': ...,
                'questionTitle': ...,
                'questionTypeName': ...,
                'profileBlocks': [{'profileId': ..., 'template': ..., 'processedTemplate': ...}, ...]
            }, ...],

            'subjuctBlocks': [{...}]  // same as body
        },

        'EMAIL': [{...}],  // same as default
        'SMS': [{...}],
        'WHATSAPP': [{...}]
    }
        """

        # Allow overiding instance vars
        campaign_id = campaign_id or self.campaign_id
        message_template_id = message_template_id or self.message_template_id
        body = body or self.body
        subject = subject or self.subject
        recipients = recipients or self.recipients or []
        message_id = message_id or self.message_id

        compound_message = {"DEFAULT": {},
                            "WEB": {},
                            "EMAIL": {},
                            "SMS": {},
                            "WHATSAPP": {}
                            }

        channels_mapping = {
            MessageChannel.SMS.name: {"body": "sms_body_template", "subject": None},
            MessageChannel.EMAIL.name: {"body": "email_body_html_template", "subject": "email_subject_template"},
            MessageChannel.WHATSAPP.name: {"body": "whatsapp_body_template", "subject": None},
            "DEFAULT": {"body": "default_body_template", "subject": "default_subject_template"},
        }

        if body:
            textblocks_and_attributes = [{}]  # one textblock
            for message_channel, template_header in channels_mapping.items():
                textblocks_and_attributes[0][template_header["body"]] = body
                textblocks_and_attributes[0][template_header["subject"]] = subject

        else:  # If body is not given, get it from the database
            textblocks_and_attributes = self.message_template.get_textblocks_and_attributes()

        if not message_template_id:
            possible_template_ids = self._get_template_ids_by_campaign(campaign_id=campaign_id)
            message_template_id = random.choice(possible_template_ids)
            self.logger.info(object={"message_template_id": message_template_id})

        criteria_json = self.message_template.get_critiria_json(message_template_id=message_template_id)

        self.logger.info(object={"textblocks_and_attributes": textblocks_and_attributes,
                                 "criteria_json": criteria_json})

        for message_template_textblock_and_attributes in textblocks_and_attributes:
            for message_channel, template_header in channels_mapping.items():
                for part in ("body", "subject"):
                    if f"{part}Blocks" not in compound_message[message_channel]:
                        compound_message[message_channel][f"{part}Blocks"] = []

                    block = {
                        "blockId": message_template_textblock_and_attributes.get("blockId"),
                        "blockTypeId": message_template_textblock_and_attributes.get("blockTypeId"),
                        "blockTypeName": message_template_textblock_and_attributes.get("blockTypeName"),
                        "questionId": message_template_textblock_and_attributes.get("questionId"),
                        "questionTypeId": message_template_textblock_and_attributes.get("questionTypeId"),
                        "questionTitle": message_template_textblock_and_attributes.get("questionTitle"),
                        "questionTypeName": message_template_textblock_and_attributes.get("questionTypeName"),
                        "profileBlocks": []
                    }
                    templates = [x for x in (message_template_textblock_and_attributes.get(template_header[part]),
                                             message_template_textblock_and_attributes.get("questionTitle"))
                                 if x]

                    message_template = " ".join(templates)
                    if not message_template:
                        self.logger.warning("message_template is empty", object={
                            "message_template_textblock_and_attributes": message_template_textblock_and_attributes})
                        continue
                    for recipient in recipients:
                        if recipient.get_profile_id() not in lang_code_cache:
                            lang_code_cache[
                                recipient.get_profile_id()] = self.profile_local.get_preferred_lang_code_by_profile_id(
                                recipient.get_profile_id()).value
                        recipient_preferred_lang_code = lang_code_cache[recipient.get_profile_id()]
                        # TODO: critiria doesn't match the recipient
                        if 1 or (self.message_template.get_potentials_receipients(
                                criteria_json, recipient.get_profile_id())
                                 # TODO recipient_preferred_lang_code_str
                                 and recipient_preferred_lang_code == message_template_textblock_and_attributes.get(
                                    "langCode")):
                            block["profileBlocks"].append(
                                # each profile has its own template, because of the language
                                {"profileId": recipient.get_profile_id(),
                                 "template": message_template,
                                 "processedTemplate": self._process_text_block(message_template, recipient=recipient),
                                 })
                    compound_message[message_channel][f"{part}Blocks"].append(block)

        # save in message table
        if message_id:
            self.update_by_id(id_column_value=message_id,
                              data_json={"compound_message_json": json.dumps(compound_message),
                                         "compound_message": json.dumps(compound_message)})
        else:
            self.message_id = self.insert(data_json={"compound_message_json": json.dumps(compound_message),
                                                     "compound_message": json.dumps(compound_message)})

        self.__compound_message = compound_message

    def _process_text_block(self, text_block_body: str, recipient: Recipient) -> str:

        template = ReplaceFieldsWithValues(message=text_block_body,
                                           # TODO language -> lang_code_str ?
                                           language=recipient.get_preferred_lang_code_str(),
                                           variable=recipient.get_profile_variables())
        processed_text_block = template.get_variable_values_and_chosen_option(
            profile_id=user_context.get_effective_profile_id(),
            # TODO profile_id -> effective_profile_id
            kwargs={"recipient.first_name": recipient.get_first_name(),
                    # TODO real -> effective
                    "sender.first_name": user_context.get_real_first_name(),
                    "message_id": self.message_id
                    })
        return processed_text_block

    def get_compound_message_dict(self, channel: MessageChannel = None) -> dict:

        compound_message = {}
        if channel is None:
            compound_message = self.__compound_message
        else:
            compound_message["DEFAULT"] = self.__compound_message["DEFAULT"]
            compound_message[channel.name] = self.__compound_message[channel.name]

        return compound_message

    def get_compound_message_str(self, channel: MessageChannel = None) -> str:
        return json.dumps(self.get_compound_message_dict(channel=channel))

    def get_profile_block(self, profile_id: int, channel: MessageChannel, part: str = "body") -> dict:
        """Returns a dict with the following keys:
        profileId, template, processedTemplate, blockId, blockTypeId, blockTypeName, questionId,
            questionTypeId, questionTitle, questionTypeName
        """

        assert part in ("body", "subject")
        blocks = self.__compound_message.get(channel.name, {}).get(f"{part}Blocks", [])
        for block in blocks:
            for _profile_block in block.get("profileBlocks", []):
                if _profile_block.get("profileId") == profile_id:
                    profile_block = {**_profile_block, **{k: v for k, v in block.items()
                                                          if k != "profileBlocks"}}

                    return profile_block

        return {}

    def get_message_fields(self) -> dict:
        if self.recipients:
            recipients_mapping = {recipient.get_profile_id(): recipient.to_json() for recipient in self.recipients}
        else:
            recipients_mapping = {}
        obj = {
            "campaign_id": self.campaign_id,
            "body": self.body,
            "subject": self.subject,
            "message_id": self.message_id,
            "recipients": recipients_mapping
        }
        return obj
