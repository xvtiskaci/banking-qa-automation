import requests

from utils.ParserUtils import ParserUtils


class MailTrapUtils:
    __config_dictionary = ParserUtils.parse_json("../resources/config.json")
    __account_id = __config_dictionary["account_id"]
    __api_token = __config_dictionary["api_token"]
    __header = {"Api-Token": __api_token}

    @classmethod
    def get_inbox_id(cls):
        response = requests \
            .get(f"https://mailtrap.io/api/accounts/{cls.__account_id}/inboxes", headers=cls.__header)
        response_json = response.json()
        inbox_id = response_json[0]["id"]
        return inbox_id

    @classmethod
    def get_message_id(cls):
        message_response = requests.get(
            f"https://mailtrap.io/api/accounts/{cls.__account_id}/inboxes/{cls.get_inbox_id()}/messages",
            headers=cls.__header)
        message_id = message_response.json()[0]["id"]
        return message_id

    @classmethod
    def get_email_text(cls):
        get_email_response = requests \
            .get(f"https://mailtrap.io/api/accounts/{cls.__account_id}/inboxes/{cls.get_inbox_id()}/"
                 f"messages/{cls.get_message_id()}", headers=cls.__header)
        return get_email_response.text

    @classmethod
    def get_source_response(cls):
        message_source_response = requests \
            .get(f"https://mailtrap.io/api/accounts/{cls.__account_id}/inboxes/{cls.get_inbox_id()}/"
                 f"messages/{cls.get_message_id()}/body.htmlsource",
                 headers=cls.__header)
        return message_source_response.text
