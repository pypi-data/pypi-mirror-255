from tabulate import tabulate
from rmbclient.log import log
from rmbclient.api import APIRequest




def convert_to_object(cls):
    # 将JSON对象转换为Model对象
    # 只可被用于类方法（因为下面会从函数的第一个参数 self 中获取 API 对象）
    def decorator(func):
        def wrapper(*args, **kwargs):
            json_or_list_data = func(*args, **kwargs)
            # 如果返回的是JSON or List对象
            if isinstance(json_or_list_data, list):
                obj_list = []
                for json_data in json_or_list_data:
                    obj = cls.load_from_dict(json_data)
                    # 将API对象传递给Model对象（从函数的第一个参数 self 中获取）
                    obj.api = args[0].api
                    obj_list.append(obj)
                return obj_list
            elif isinstance(json_or_list_data, dict):
                obj = cls.load_from_dict(json_or_list_data)
                # 将API对象传递给Model对象（从函数的第一个参数 self 中获取）
                obj.api = args[0].api
                return obj
            else:
                log.error(f"Unsupported data type: {type(json_or_list_data)}")
                raise ValueError("Unsupported data type")

        return wrapper

    return decorator


class BaseResourceList:
    __do_not_print_properties__ = []

    def __init__(self, api: APIRequest, endpoint: str):
        self.api = api
        self.endpoint = endpoint

    def __iter__(self):
        # 实现迭代器协议，允许直接迭代资源列表
        self._current = 0
        self._resources = self._get_all_resources() or []
        return self

    def __next__(self):
        if self._current >= len(self._resources):
            raise StopIteration
        resource = self._resources[self._current]
        self._current += 1
        return resource

    def _get_all_resources(self):
        raise NotImplementedError

    def to_dict(self):
        return [resource.to_dict() for resource in self]

    def __repr__(self):
        # 将资源转换为字典列表
        resources_dicts = self.to_dict()

        # 去掉 __do_not_print_properties__ 字段
        if self.__do_not_print_properties__:
            for ds in resources_dicts:
                for i in self.__do_not_print_properties__:
                    ds.pop(i)

        # 使用 tabulate 来生成表格格式的字符串
        return tabulate(resources_dicts, headers="keys", tablefmt="plain")
