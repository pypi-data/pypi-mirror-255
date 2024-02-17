from rmbcommon.models import RunCore
from rmbclient.models.base import convert_to_object, BaseResourceList


class RunClientModel(RunCore):

    def cancel(self):
        return self.api.send(
            endpoint=f"/chats/{self.chat_id}/runs/{self.id}",
            method="POST",
            data={"action": "cancel"}
        )


class RunList(BaseResourceList):
    @convert_to_object(cls=RunClientModel)
    def _get_all_resources(self):
        # 获取所有资源
        return self.api.send(endpoint=self.endpoint, method="GET")

    @convert_to_object(cls=RunClientModel)
    def get(self, id):
        # 通过ID来获取
        return self.api.send(endpoint=f"{self.endpoint}/{id}", method="GET")

    @convert_to_object(cls=RunClientModel)
    def create(self):
        # 运行AI生成回复
        return self.api.send(endpoint=f"{self.endpoint}", method="POST")
