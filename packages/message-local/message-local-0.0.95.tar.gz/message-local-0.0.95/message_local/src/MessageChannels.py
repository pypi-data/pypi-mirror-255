from enum import Enum


# TODO Let's generate with Sql2Code
# Values are from the database message_channel_table
class MessageChannel(Enum):
    EMAIL = 1
    SMS = 2
    WHATSAPP = 11
