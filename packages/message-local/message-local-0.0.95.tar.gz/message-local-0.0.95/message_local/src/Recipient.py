import json
from enum import Enum, auto

from user_context_remote.user_context import UserContext
from variable_local.variable import VariablesLocal


# TODO Each of them has field_id value in field.field_table, shall we use it?
#   (I didn't find it there)
class ReferenceType(Enum):
    PERSON_ID = auto()
    CONTACT_ID = auto()
    USER_ID = auto()
    PROFILE_ID = auto()


class RecipientType(Enum):
    TELEPHONE_NUMBER = auto()
    EMAIL_ADDRESS = auto()

    UNKNOWN = auto()


class Recipient:
    def __init__(self, contact_id: int = None, person_id: int = None, user_id: int = None, profile_id: int = None,
                 telephone_number: str = None, email_address_str: str = None, preferred_lang_code_str: str = None,
                 first_name: str = None) -> None:
        self.__person_id = person_id
        self.__email_address_str = email_address_str
        self.__contact_id = contact_id
        self.__user_id = user_id
        self.__profile_id = profile_id
        self.__telephone_number = telephone_number
        self.__preferred_lang_code_str = preferred_lang_code_str
        self.__first_name = first_name
        for key, value in self.to_json().items():
            if not key.endswith("id") and key.upper() in RecipientType.__members__:
                self._recipient_type = RecipientType[key.upper()]  # remove the first underscore

        self.user = UserContext()
        self.__variable_local: VariablesLocal | None = None  # To improve performance, we will get it only when needed.

    def get_profile_variables(self) -> VariablesLocal:
        if self.__variable_local is not None:
            return self.__variable_local
        self.__variable_local = VariablesLocal()
        # TODO: make sure those are stored on the effective_profile_id (using global user_context or sending the user_context).
        self.__variable_local.add(self.__contact_id, "contact_id")
        self.__variable_local.add(self.__person_id, "person_id")
        self.__variable_local.add(self.__user_id, "user_id")
        self.__variable_local.add(self.__profile_id, "profile_id")
        self.__variable_local.add(self.__telephone_number, "telephone_number")
        self.__variable_local.add(self.__email_address_str, "email_address")
        return self.__variable_local

    def get_person_id(self) -> int:
        return self.__person_id

    def get_profile_id(self) -> int:
        return self.__profile_id

    def get_contact_id(self) -> int:
        return self.__contact_id

    def get_user_id(self) -> int:
        return self.__user_id

    def get_first_name(self) -> str:
        return self.__first_name

    def is_email_address(self):
        return self.__telephone_number is not None

    def is_telephone_number(self):
        return self.__telephone_number is not None

    def get_email_address(self):
        return self.__email_address_str

    def get_telephone_address(self):
        return self.__telephone_number is not None

    def get_preferred_lang_code_str(self):
        return self.__preferred_lang_code_str

    # TODO Is there a package/library for this that we can use?
    def get_normizalied_phone(self):
        """ normalized/canonical phone, telephone number """
        # TODO I think this function does not cover all cases - I believe we can find one on the internet - I think Sahar found one.
        if self.__telephone_number is None:
            return None
        if self.__telephone_number.startswith("+"):
            country_code = ""
        else:
            # TODO county_code and country_id are two different things
            country_code = self.user.get_country_code()

        # Remove non-numeric characters from the telephone number and leading zeroes
        cleaned_number = int(''.join(char for char in self.__telephone_number if char.isdigit()))

        cleaned_number = f"{country_code}{cleaned_number}"

        return cleaned_number

    def to_json(self):
        init_args = ("contact_id", "person_id", "user_id", "profile_id", "telephone_number",
                     "email_address_str", "preferred_lang_code_str", "first_name")
        return {k.replace("_Recipient__", ""): v for k, v in self.__dict__.items()
                if v is not None and k.replace("_Recipient__", "") in init_args}

    @staticmethod
    def from_json(json_object: dict) -> 'Recipient':
        return Recipient(**json_object)

    def __str__(self):
        return json.dumps(self.to_json())

    def __repr__(self):
        """This is used when we print a list of recipients"""
        return self.__str__()

    @staticmethod
    def recipients_from_json(recipients: list[dict]) -> list['Recipient'] | list | None:
        """get recipients"""
        if not recipients:
            return recipients  # None or []
        return [Recipient.from_json(recipient) for recipient in recipients]

    @staticmethod
    def recipients_to_json(recipients: list['Recipient']) -> list[dict] | list | None:
        """recipients to json"""
        if not recipients:
            return recipients
        return [recipient.to_json() for recipient in recipients]
