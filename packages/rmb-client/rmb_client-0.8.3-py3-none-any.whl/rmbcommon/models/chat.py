from rmbcommon.models.base import BaseCoreModel
from rmbcommon.tools import format_time_ago


class ChatCore(BaseCoreModel):
    __properties_init__ = ['tenant_id', 'id', 'created', 'datasource_ids', 'human_msgs', 'ai_msgs', 'latest_msg']

    def __repr__(self):
        return f"<Chat {self.id} [{format_time_ago(self.created)}]>"


class MessageCore(BaseCoreModel):

    # role: human | ai
    __properties_init__ = ['id', 'chat_id', 'created', 'role', 'content']

    def __repr__(self):
        return f"<Message {self.id}: {self.role}: {self.content} [{format_time_ago(self.created)}]>"


class RunCore(BaseCoreModel):
    # status: running | finished | failed | canceled
    __properties_init__ = ['id', 'chat_id', 'created', 'status', 'steps']

    def __repr__(self):
        return f"<ChatRun {self.id} [{format_time_ago(self.created)}]>"
