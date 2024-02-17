from database_mysql_local.generic_crud_ml import GenericCRUDML
from logger_local.MetaLogger import MetaLogger

from .MessageConstants import object_message

cache = {}


class MessageTemplates(GenericCRUDML, metaclass=MetaLogger, object=object_message):
    def __init__(self):
        super().__init__(default_schema_name="field", default_table_name="field_table")

    def get_potentials_receipients(self, criteria_json: dict, profile_id: int) -> dict:
        # TODO Shall we consider to get profile_json instead of profile_id to improve performance?

        where = self.get_where_by_criteria_json(criteria_json)
        if profile_id:
            where += f" AND user.profile_id = {profile_id}"
        self.set_schema(schema_name="profile")
        # TODO Shall we use GenericCrud?
        query_for_potentials_receipients = f"""
SELECT DISTINCT user_id, person_id, user_main_email_address, user.profile_id AS profile_id, 
   profile_phone_full_number_normalized, profile_preferred_lang_code
 FROM user.user_general_view AS user
    JOIN group_profile.group_profile_view AS group_profile on group_profile.profile_id = user.profile_id
  WHERE {where} 
  LIMIT 1  -- TODO: remove
"""
        if "get_potential_receipients" in cache:
            potential_receipients = cache["get_potential_receipients"]
        else:
            self.cursor.execute(query_for_potentials_receipients)
            result = self.cursor.fetchone()
            columns = ("user_id, person_id, user_main_email_address, profile_id,"
                       "profile_phone_full_number_normalized, profile_preferred_lang_code")
            potential_receipients = self.convert_to_dict(result, columns)
            cache["get_potential_receipients"] = potential_receipients

        return potential_receipients

    def get_where_by_criteria_json(self, criteria_json: dict) -> str:
        # TODO add support to user_external_id in criteria_json
        min_age = criteria_json.get("min_age")
        max_age = criteria_json.get("max_age")
        gender_list_id = criteria_json.get("gender_list_id")
        group_list_id = criteria_json.get("group_list_id")
        self.logger.info(object={"min_age": min_age, "max_age": max_age, "gender_list_id": gender_list_id,
                                 "group_list_id": group_list_id})
        # profile_id didn't receive messages from this campaign for campaign.minimal_days
        where = "TRUE "
        if min_age is not None:
            where += f" AND TIMESTAMPDIFF(YEAR, person_birthday_date, CURDATE()) >= {min_age}"
        if max_age is not None:
            where += f" AND TIMESTAMPDIFF(YEAR, person_birthday_date, CURDATE()) <= {max_age}"

        if gender_list_id is not None:
            if ("profile", "gender", gender_list_id) not in cache:
                profile_gender_id_list = self.sql_in_list_by_entity_list_id(
                    schema_name="profile", entity_name="gender", entity_list_id=gender_list_id)
                cache[("profile", "gender", gender_list_id)] = profile_gender_id_list
            else:
                profile_gender_id_list = cache[("profile", "gender", gender_list_id)]

            where += " AND profile_gender_id " + profile_gender_id_list

        if group_list_id is not None:
            if ("group", "group", group_list_id) not in cache:
                group_id_list = self.sql_in_list_by_entity_list_id(
                    schema_name="group", entity_name="group", entity_list_id=group_list_id)
                cache[("group", "group", group_list_id)] = group_id_list
            else:
                group_id_list = cache[("group", "group", group_list_id)]
            where += " AND group_profile.group_id " + group_id_list
        return where

    def get_critiria_json(self, message_template_id: int) -> dict:
        if message_template_id in cache:
            return cache[message_template_id]
        query = """
        SELECT DISTINCT min_age, max_age, gender_list_id, group_list_id
          FROM message_template.message_template_view
            JOIN message_template.message_template_message_template_text_block_view AS message_template_message_template_text_block
                ON message_template_message_template_text_block.message_template_id = message_template_view.message_template_id
            JOIN message_template.message_template_text_block_view AS message_template_text_block
                ON message_template_text_block.message_template_text_block_id = message_template_message_template_text_block.message_template_id
            JOIN criteria.criteria_view AS criteria
                ON criteria.criteria_id = message_template_text_block.criteria_id
          WHERE message_template_view.message_template_id = %s
          LIMIT 1  -- TODO: remove
          """  # noqa
        self.cursor.execute(query, (message_template_id,))

        columns = "min_age, max_age, gender_list_id, group_list_id"
        critiria_json = self.convert_to_dict(self.cursor.fetchone(), columns)
        cache[message_template_id] = critiria_json
        return critiria_json

    def get_textblocks_and_attributes(self) -> list[dict]:
        """Returns the message template text block and attributes for the given message template id and profile id.
        The attributes are:
            - sms_body_template
            - email_subject_template
            - email_body_html_template
            - whatsapp_body_template
            ... TODO: add more attributes here

        The attributes are returned as a list of dictionaries, one dictionary
            for each text block in the message template.
        """
        if "get_textblocks_and_attributes" in cache:
            return cache["get_textblocks_and_attributes"]
        results = []
        # TODO Shall we use GenericCrud?
        query = """
SELECT sms_body_template, email_subject_template, email_body_html_template, whatsapp_body_template,
        default_subject_template, default_body_template,
        question.question_id AS questionId, question.question_type_id AS questionTypeId,
        question_ml.title AS questionTitle, question_type.name AS questionTypeName,
        question_ml.lang_code AS langCode,
        -- answer_expiration_days, criteria_id, label_question_id, message_template_text_block_ml_id,
        message_template_text_block.message_template_text_block_id AS blockId,
        message_template_text_block_type_ml.message_template_text_block_type_id AS blockTypeId,
        message_template_text_block_type_ml.title AS blockTypeName

FROM message_template.message_template_text_block_view AS message_template_text_block
    JOIN message_template.message_template_text_block_ml_view AS message_template_text_block_ml
        ON message_template_text_block_ml.message_template_text_block_id = message_template_text_block.message_template_text_block_id
            -- we filter that later per recipient
            -- AND message_template_text_block_ml.lang_code = %s

    JOIN message_template.message_template_message_template_text_block_view AS message_template_message_template_text_block
        ON message_template_message_template_text_block.message_template_text_block_id = message_template_text_block.message_template_text_block_id

    JOIN message_template.message_template_text_block_type_ml_view AS message_template_text_block_type_ml
        ON message_template_text_block_type_ml.message_template_text_block_type_id = message_template_text_block.message_template_text_block_type_id
            AND message_template_text_block_type_ml.lang_code = message_template_text_block_ml.lang_code

    LEFT JOIN question.question_view AS question
        ON question.question_id = message_template_text_block.question_id

    LEFT JOIN question.question_ml_view AS question_ml
        ON question_ml.question_id = question.question_id
            AND question_ml.lang_code = message_template_text_block_ml.lang_code

    LEFT JOIN question.question_type_view AS question_type
        ON question_type.question_type_id = question.question_type_id
"""  # noqa
        self.cursor.execute(query)
        columns = ("sms_body_template, email_subject_template, email_body_html_template, whatsapp_body_template," +
                   "default_subject_template, default_body_template," +
                   "questionId, questionTypeId, questionTitle, questionTypeName, langCode, blockId, blockTypeId, blockTypeName")
        for inner_row in self.cursor.fetchall():
            text_block_dict = self.convert_to_dict(inner_row, columns)

            text_block_dict["possibleAnswers"] = self._get_possible_answers(
                question_id=text_block_dict["questionId"])
            self.logger.info(object={"text_block_dict": text_block_dict})
            results.append(text_block_dict)
        cache["get_textblocks_and_attributes"] = results

        return results

    def _get_possible_answers(self, question_id: int) -> list[dict]:
        # TODO: get cities etc and insert as possible answer.
        query = "SELECT value FROM question.question_possible_answers_ml_view WHERE question_id = %s"
        self.cursor.execute(query, (question_id,))
        # We will change action in the future.
        return [{"answerValue": row[0], "action": None} for row in self.cursor.fetchall()]
