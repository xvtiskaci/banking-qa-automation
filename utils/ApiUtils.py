import requests

from utils.ParserUtils import ParserUtils


class ApiUtils:
    __base_url = ParserUtils.parse_json("../resources/config.json")["api_url"]

    @classmethod
    def post(cls, endpoint, body):
        headers = {"accept": "application/json",
                   "Content-Type": "application/json"}
        return requests.post(cls.__base_url.format(endpoint), data=body, headers=headers)

    @classmethod
    def get(cls, endpoint, params):
        headers = {"accept": "application/json",
                   "Content-Type": "application/json"}
        return requests.get(cls.__base_url.format(endpoint), params=params, headers=headers)

