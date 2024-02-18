import http
import time
from datetime import datetime
from typing import List

from api_management_local.API_Mangement_Manager import APIMangementManager
from api_management_local.Exception_API import (ApiTypeDisabledException,
                                                ApiTypeIsNotExistException,
                                                PassedTheHardLimitException)
from api_management_local.api_limit_status import APILimitStatus
from api_management_local.direct import Direct
from api_management_local.indirect import InDirect
from item_local.item import Item
from logger_local.MetaLogger import MetaLogger
from python_sdk_remote.utilities import our_get_env
from star_local.exception_star import NotEnoughStarsForActivityException

from .ChannelProviderConstants import (AWS_SES_EMAIL_MESSAGE_PROVIDER_ID,
                                       AWS_SNS_SMS_MESSAGE_PROVIDER_ID,
                                       INFORU_MESSAGE_PROVIDER_ID)
from .CompoundMessage import CompoundMessage
from .MessageChannels import MessageChannel
from .MessageConstants import (DEFAULT_HEADERS, SMS_MESSAGE_LENGTH,
                               object_message)
from .MessageImportance import MessageImportance
from .Recipient import Recipient

DEFAULT_SENDER_PROFILE_ID = our_get_env("DEFAULT_SENDER_PROFILE_ID")


class MessageLocal(Item, CompoundMessage, metaclass=MetaLogger, object=object_message):
    """Message Local Class"""

    def __init__(self, *, recipients: List[Recipient], api_type_id: int = None, campaign_id: int = None,
                 message_template_id: int = None,
                 original_body: str = None, original_subject: str = None,
                 importance: MessageImportance = MessageImportance.MEDIUM, message_id: int = None,
                 is_http_api: bool = None, endpoint: str = None,
                 headers: dict = DEFAULT_HEADERS, external_user_id: int = None,
                 sender_profile_id: int = DEFAULT_SENDER_PROFILE_ID, is_test_data: bool = False, **kwargs) -> None:
        """message_dict contains a list of dicts, each with the following keys:
        ["sms_body_template", "email_subject_template", "email_body_html_template",
        "whatsapp_body_template", "question_id", "question_type_id", "question_title", "question_type_name"]"""
        # TODO We should add all fields from message schema in the database
        # (i.e. message_id, scheduled_sent_timestamp, message_sent_status : MessageSentStatus  ...)

        CompoundMessage.__init__(self, message_id=message_id, campaign_id=campaign_id,
                                 message_template_id=message_template_id, body=original_body,
                                 subject=original_subject, recipients=recipients, is_test_data=is_test_data)
        # GenericCRUD.__init__(self, default_schema_name="message", default_table_name="message_table",
        #                      default_view_table_name="message_outbox_view", default_id_column_name="message_id",
        #                      is_test_data=is_test_data)

        # init instance variables
        self.message_id = message_id
        self.__original_body = original_body
        self.__original_subject = original_subject
        self.importance = importance
        self._is_http_api = is_http_api
        self._api_type_id = api_type_id
        self._endpoint = endpoint
        self._headers = headers
        self.__external_user_id = external_user_id
        self.__recipients = recipients
        self._campaign_id = campaign_id
        self.__body_after_html_template = None
        self.__subject_after_html_template = None  # TODO: implement
        self.sender_profile_id = sender_profile_id

        # init instances
        self.__indirect = InDirect()
        self.__direct = Direct()
        self.api_management_manager = APIMangementManager()

        # set body after text template, this most be done before calling get_msg_type
        self.__ordered_message_channels = [message_channel for message_channel in MessageChannel]

        # decide how to send (channel & provider) for each recipient
        self.channel_ids_per_recipient = {recipient.get_profile_id(): self.get_msg_type(recipient)
                                          for recipient in recipients}
        self.provider_id_per_recipient = {recipient.get_profile_id(): self.get_message_provider_id(
            message_channel_id=self.channel_ids_per_recipient[recipient.get_profile_id()], recipient=recipient)
            for recipient in recipients}
        # self.message_template_dict_by_campaign_id = self.get_message_template_dict_by_campaign_id(campaign_id=campaign_id)

        # Old code I might need later:
        # if self._campaign_id:
        #     body = self.message_template_dict_by_campaign_id.get(
        #         self._campaign_id).get(recipient.get_preferred_language())
        #     body = self.message_template.get_message_template_textblock_and_attributes(
        #         message_template_id=body, destination_profile_id=recipient.get_profile_id())

    def get_id(self):
        pass

    def get_msg_type(self, recipient: Recipient) -> MessageChannel:
        # TODO: return msg_type (sms, email, whatsapp) based on hours, provider availability, msg length, etc.
        """TODO: make sure we can access:
        1. size of message
        2. message contains html or not
        3. country of recipient
        4. time of the day
        5. preferences of the recipient
        6. attachments type and size 7. cost of sending the message"""
        for message_channel in self.__ordered_message_channels:
            if recipient.get_email_address() is not None:
                return MessageChannel.EMAIL
            elif len(self.get_body_after_text_template(recipient, message_channel)) < SMS_MESSAGE_LENGTH:
                return MessageChannel.SMS
            else:
                return MessageChannel.WHATSAPP

    def get_message_channel(self, recipient: Recipient) -> MessageChannel:
        if recipient.get_profile_id() in self.channel_ids_per_recipient:
            return self.channel_ids_per_recipient[recipient.get_profile_id()]
        else:
            return self.get_msg_type(recipient)

    @staticmethod
    def get_message_provider_id(message_channel_id: MessageChannel, recipient: Recipient) -> int:
        """return message provider"""

        if message_channel_id == MessageChannel.SMS and recipient.get_normizalied_phone().startswith("972"):
            provider_id = AWS_SNS_SMS_MESSAGE_PROVIDER_ID
        elif message_channel_id == MessageChannel.EMAIL:
            provider_id = AWS_SES_EMAIL_MESSAGE_PROVIDER_ID
        elif message_channel_id == MessageChannel.WHATSAPP:
            # TODO: or vonage
            provider_id = INFORU_MESSAGE_PROVIDER_ID
        else:
            raise Exception("Can't determine the Message Provider for message_channel_id=" + str(message_channel_id))

        return provider_id

    def get_body_after_text_template(self, recipient: Recipient,
                                     message_channel: MessageChannel = None) -> str:
        # TODO: is this the right way to do it?
        if message_channel is None:
            message_channel = self.get_message_channel(recipient)

        body = ""
        for block in self.get_compound_message_dict(message_channel)[message_channel.name]["bodyBlocks"]:
            for profile_block in block["profileBlocks"]:
                if profile_block["profileId"] == recipient.get_profile_id():
                    body += profile_block["processedTemplate"] + "\n"
        return body

    def _get_body_after_html_template(self) -> str:
        return self.__body_after_html_template

    # def _get_number_of_attachment(self) -> int:
    #     return 0

    def get_subject_after_html_template(self) -> str:
        # Unresolved attribute reference '__subject_after_html_template' for class 'MessageLocal'
        return self.__subject_after_html_template

    # def _get_type_of_attachments(self):
    #     return None

    # api_data To know if to API calls are actually the same and do caching.
    # TODO sender_profile_id = None meaning we let the system to decide who is the sender_profile_id?
    # TODO Do we need user_external as parameter?
    def can_send(self, sender_profile_id: int = None, api_data: dict = None, outgoing_body: dict = None) -> bool:
        sender_profile_id = sender_profile_id or self.sender_profile_id
        if self._is_http_api:
            return self.__can_send_direct(sender_profile_id, api_data=api_data)
        else:
            return self.__can_send_indirect(sender_profile_id, outgoing_body=outgoing_body)

    # api_data To know if to API calls are actually the same and do caching.
    def __can_send_direct(self, sender_profile_id: int, api_data: dict = None) -> bool:
        # TODO: implement sender_profile_id logic
        try:
            # TODO: change try_to_call_api typing
            try_to_call_api_result = self.__direct.try_to_call_api(
                external_user_id=self.__external_user_id,
                api_type_id=self._api_type_id,
                endpoint=self._endpoint,
                outgoing_body=api_data,  # data
                outgoing_header=self._headers
            )
            x = try_to_call_api_result['status_code']
            if x != http.HTTPStatus.OK:
                raise Exception(try_to_call_api_result['text'])
            else:
                return True
        except PassedTheHardLimitException:
            sleep_after_passing_the_hard_limit = self.api_management_manager.seconds_to_sleep_after_passing_the_hard_limit(
                api_type_id=self._api_type_id)
            if sleep_after_passing_the_hard_limit > 0:
                self.logger.info("sleeping for sleep_after_passing_the_hard_limit=" + str(
                    sleep_after_passing_the_hard_limit) + " seconds",
                                 {'sleep_after_passing_the_hard_limit': sleep_after_passing_the_hard_limit})
                time.sleep(sleep_after_passing_the_hard_limit)
            else:
                self.logger.info("No sleeping needed : x= " + str(sleep_after_passing_the_hard_limit) + " seconds")
        except NotEnoughStarsForActivityException:
            self.logger.warning("Not Enough Stars For Activity Exception")

        except ApiTypeDisabledException:
            self.logger.error("Api Type Disabled Exception")

        except ApiTypeIsNotExistException:
            self.logger.error("Api Type Is Not Exist Exception")

        except Exception as exception:
            self.logger.exception(object=exception)
        return False

    def __can_send_indirect(self, sender_profile_id: int = None, outgoing_body: dict = None) -> bool:
        # TODO: implement sender_profile_id logic
        http_status_code = None
        try:
            api_check, self.__api_call_id, arr = self.__indirect.before_call_api(
                external_user_id=self.__external_user_id, api_type_id=self._api_type_id,
                endpoint=self._endpoint,
                outgoing_header=self._headers,
                outgoing_body=outgoing_body
            )
            if arr is None:
                self.__used_cache = False
                if api_check == APILimitStatus.BETWEEN_SOFT_LIMIT_AND_HARD_LIMIT:
                    self.logger.warn("You passed the soft limit")
                if api_check != APILimitStatus.GREATER_THAN_HARD_LIMIT:
                    try:
                        # user = user_context.login_using_user_identification_and_password(outgoing_body)
                        http_status_code = http.HTTPStatus.OK.value
                    except Exception as exception:
                        self.logger.exception(object=exception)
                        http_status_code = http.HTTPStatus.BAD_REQUEST.value
                else:
                    self.logger.info("You passed the hard limit")
                    x = self.api_management_manager.seconds_to_sleep_after_passing_the_hard_limit(
                        api_type_id=self._api_type_id)
                    if x > 0:
                        self.logger.info("sleeping : " + str(x) + " seconds")
                        time.sleep(x)
                        # raise PassedTheHardLimitException

                    else:
                        self.logger.info("No sleeping needed : x= " + str(x) + " seconds")
            else:
                self.__used_cache = True
                self.logger.info("result from cache")
                # print(arr)
                http_status_code = http.HTTPStatus.OK.value
        except ApiTypeDisabledException:
            self.logger.error("Api Type Disabled Exception")

        except ApiTypeIsNotExistException:
            self.logger.error("Api Type Is Not Exist Exception")
        self.logger.info("http_status_code: " + str(http_status_code))
        return http_status_code == http.HTTPStatus.OK.value

    def send(self, body: str = None, compound_message_dict: dict = None,
             recipients: List[Recipient] = None, cc: List[Recipient] = None, bcc: List[Recipient] = None,
             scheduled_timestamp_start: datetime = None,
             scheduled_timestamp_end: datetime = None, **kwargs) -> list[int]:
        pass  # this is an abstract method, but we don't want to make this class abstract

    def after_send_attempt(self, sender_profile_id: int = None, outgoing_body: dict = None,
                           incoming_message: str = None, http_status_code: int = None,
                           response_body: str = None) -> None:
        # TODO: implement sender_profile_id logic
        sender_profile_id = sender_profile_id or self.sender_profile_id
        if self._is_http_api:
            self.__after_direct_send()
        else:
            self.__after_indirect_send(outgoing_body=outgoing_body,
                                       incoming_message=incoming_message,
                                       http_status_code=http_status_code,
                                       response_body=response_body)

    def display(self):
        print("MessageLocal: " + str(self.__dict__))

    def __after_indirect_send(self, outgoing_body: dict, incoming_message: str,
                              http_status_code: int, response_body: str):

        self.__indirect.after_call_api(external_user_id=self.__external_user_id,
                                       api_type_id=self._api_type_id,
                                       endpoint=self._endpoint,
                                       outgoing_header=self._headers,
                                       outgoing_body=outgoing_body,
                                       incoming_message=incoming_message,
                                       http_status_code=http_status_code,
                                       response_body=response_body,
                                       api_call_id=self.__api_call_id,
                                       used_cache=self.__used_cache)

    def __after_direct_send(self):
        pass

    def get_importance(self) -> MessageImportance:
        """get method"""
        return self.importance

    def get_recipients(self) -> List[Recipient]:
        return self.__recipients

    # def get_message_template_dict_by_campaign_id(self, campaign_id: int) -> dict:
    #     """Returns [lang_code (such as 'en'):
    #                 {'sms_body_template': ..., 'email_subject_template': ...,
    #                     'email_body_html_template': ..., 'whatsapp_body_template': ...
    #                 }, ...
    #                ]"""
    #     
    #     if campaign_id is None:
    #         return {}
    #     query = "SELECT * FROM campaign_message_template.campaign_message_template_table " \
    #             "JOIN message_template.message_template_ml_table" \
    #             "WHERE campaign_id = %s"
    #     query_parameters = (campaign_id,)
    #     self.cursor.execute(query, query_parameters)
    #     columns = [column[0] for column in self.cursor.description]
    #     results = [dict(zip(columns, row)) for row in self.cursor.fetchall()]
    #     results = {row["lang_code"]: row for row in results}
    #     
    #     return results
