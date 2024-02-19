from rmbclient.models import DataResourceList, ChatList
from rmbclient.api import APIRequest
from rmbcommon.version import VERSION

class ReliableMetaBrain:
    __version__ = VERSION
    version = VERSION

    def __init__(self, api_url='http://127.0.0.1:5000',
                 token='token1', debug=False):
        self.api = APIRequest(api_url=api_url, token=token, debug=debug)

    @property
    def datasources(self):
        return DataResourceList(api=self.api, endpoint="/datasources/")

    @property
    def chats(self):
        return ChatList(api=self.api, endpoint="/chats/")

    @property
    def token(self):
        return self.api.send(endpoint="/account/token", method="GET")

    def test_clear_all(self):
        return self.api.send(endpoint="/tests/clear_data/all", method="POST")

    def test_clear_brain(self):
        return self.api.send(endpoint="/tests/clear_data/brain", method="POST")

    def test_clear_chat(self):
        return self.api.send(endpoint="/tests/clear_data/chat", method="POST")

