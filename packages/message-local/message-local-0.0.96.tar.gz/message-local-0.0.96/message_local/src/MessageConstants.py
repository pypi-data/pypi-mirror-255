from logger_local.LoggerComponentEnum import LoggerComponentEnum

MESSAGE_LOCAL_PYTHON_COMPONENT_ID = 259
MESSAGE_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME = "message local"
DEVELOPER_EMAIL = 'akiva.s@circ.zone'
object_message = {
    'component_id': MESSAGE_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': MESSAGE_LOCAL_PYTHON_COMPONENT_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}

DEFAULT_HEADERS = {"Content-Type": "application/json"}

# TEST_API_TYPE_ID = 4

# SMS
SMS_MESSAGE_LENGTH = 160
UNICODE_SMS_MESSAGE_LENGTH = 70
