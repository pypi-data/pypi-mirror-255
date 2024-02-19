# 通用的数据源类，提供了各种数据源均需要的基本属性和方法，比如Original MetaData以及获取MetaData的方法
from rmbcommon.models.base import BaseCoreModel


class DataSourceCore(BaseCoreModel):

    __properties_init__ = ['tenant_id', 'id', 'created_at', 'name', 'type', 'access_config', 'sample_questions']

    def __repr__(self):
        if self.id:
            return f"<{self.id}: {self.name} >"
        else:
            return f"<{self.type}: {self.name} (not saved)>"

    def __str__(self):
        return self.__repr__()

    @property
    def safe_access_config(self):
        # TODO: 保护敏感信息
        return self.access_config

