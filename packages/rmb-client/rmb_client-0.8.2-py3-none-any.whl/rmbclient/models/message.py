from rmbcommon.models import (MessageCore)
from rmbclient.models.base import convert_to_object, BaseResourceList


class MessageClientModel(MessageCore):
    pass


class MessageList(BaseResourceList):
    @convert_to_object(cls=MessageClientModel)
    def _get_all_resources(self):
        # 获取所有资源
        return self.api.send(endpoint=self.endpoint, method="GET")

    @convert_to_object(cls=MessageClientModel)
    def get(self, id):
        # 通过ID来获取
        return self.api.send(endpoint=f"{self.endpoint}/{id}", method="GET")

    @convert_to_object(cls=MessageClientModel)
    def create(self, content):
        # 发送消息
        data = {"content": content}
        return self.api.send(endpoint=f"{self.endpoint}", method="POST", data=data)

