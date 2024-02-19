from datetime import datetime

from rmbcommon.models import ChatCore, BIAnswer
from rmbcommon.tools import format_time_ago
from rmbclient.models.base import convert_to_object, BaseResourceList
from rmbclient.models.run import RunList
from rmbclient.models.message import MessageList
from rmbclient.models.datasource import DataSourceClientModel


class ChatClientModel(ChatCore):

    @property
    @convert_to_object(cls=DataSourceClientModel)
    def datasources(self):
        return self.api.send(endpoint=f"/chats/{self.id}/datasources", method="GET")

    def delete(self):
        return self.api.send(endpoint=f"/chats/{self.id}", method="DELETE")

    @property
    def runs(self):
        return RunList(self.api, endpoint=f"/chats/{self.id}/runs")

    @property
    def messages(self):
        return MessageList(self.api, endpoint=f"/chats/{self.id}/messages")

    @convert_to_object(cls=BIAnswer)
    def ask(self, question):
        # 提问
        data = {"question": question}
        return self.api.send(endpoint=f"/chats/{self.id}", method="POST", data=data)


class ChatList(BaseResourceList):
    __do_not_print_properties__ = ['tenant_id']

    def _my_format_time(self, ts: int or None):
        if not ts:
            return ''
        local_ts = datetime.fromtimestamp(ts)
        local_ts_str = local_ts.strftime('%Y-%m-%d %H:%M:%S')
        local_ts_readable = format_time_ago(ts)
        return local_ts_readable

    @convert_to_object(cls=ChatClientModel)
    def _get_all_resources(self):
        return self._get_all_resources_request()

    def _get_all_resources_request(self):
        # 获取所有资源
        chats = self.api.send(endpoint=self.endpoint, method="GET")

        # 转换 created 字段
        for chat in chats:
            chat['created'] = self._my_format_time(chat['created'])
            chat['latest_msg'] = self._my_format_time(chat['latest_msg'])
        return chats

    @property
    @convert_to_object(cls=ChatClientModel)
    def last(self):
        # 获取最后一个资源
        return self._get_all_resources_request()[-1]

    @convert_to_object(cls=ChatClientModel)
    def get(self, id):
        # 通过资源ID来获取
        return self.api.send(endpoint=f"{self.endpoint}{id}", method="GET")

    @convert_to_object(cls=ChatClientModel)
    def create(self, datasource_ids: list[str]):
        for ds_id in datasource_ids:
            if type(ds_id) != str:
                raise ValueError(f"datasource_ids must be a list of string: {ds_id}")

        data = {"datasource_ids": datasource_ids}
        return self.api.send(endpoint=self.endpoint, method="POST", data=data)
