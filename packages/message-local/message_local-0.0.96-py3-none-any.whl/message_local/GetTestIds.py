from database_mysql_local.generic_crud import GenericCRUD
from logger_local.MetaLogger import MetaLogger

from .MessageConstants import object_message


# MessageLocal init is too heavy
class GetTestIds(GenericCRUD, metaclass=MetaLogger, object=object_message):
    def __init__(self):
        super().__init__(default_schema_name="message", default_table_name="message_table",
                         default_view_table_name="message_outbox_view", default_id_column_name="message_id")

    def insert_message(self, **kwargs) -> int:
        """Inserts a message into the database"""
        data_json = {}
        for arg in kwargs.items():
            if arg[1] is not None:
                data_json[arg[0]] = arg[1]

        message_id = self.insert(schema_name="message", data_json=data_json)
        return message_id

    def get_test_message_id(self) -> int:
        return self.get_test_entity_id(entity_name="message",
                                       insert_function=self.insert_message)
