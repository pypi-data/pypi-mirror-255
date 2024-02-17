import os

from rmbcommon.models import DataSourceCore, MetaData
from rmbclient.models.base import convert_to_object, BaseResourceList
from rmbcommon.exceptions.client import DataSourceNotFound, UnsupportedFileType
from rmbclient.upload import upload_to_oss


class MetaDataClientModel(MetaData):

    def sync(self):
        new_meta_dict = self.api.send(endpoint=f"/datasources/{self.datasource_id}/meta", method="POST")
        self.update_from_dict(new_meta_dict)
        return self


class DataSourceClientModel(DataSourceCore):
    @property
    @convert_to_object(cls=MetaDataClientModel)
    def meta(self):
        return self.api.send(endpoint=f"/datasources/{self.id}/meta", method="GET")

    @property
    @convert_to_object(cls=MetaDataClientModel)
    def meta_runtime(self):
        return self.api.send(
            endpoint=f"/datasources/{self.id}/meta",
            method="GET",
            params={"from_where": "runtime"}
        )

    def delete(self):
        return self.api.send(endpoint=f"/datasources/{self.id}", method="DELETE")


class DataResourceList(BaseResourceList):
    __do_not_print_properties__ = ['tenant_id', 'access_config', 'sample_questions']

    @convert_to_object(cls=DataSourceClientModel)
    def _get_all_resources(self):
        return self._get_all_resources_request()

    def _get_all_resources_request(self):
        # 获取所有资源
        datasources = self.api.send(endpoint=self.endpoint, method="GET")
        return datasources

    @property
    @convert_to_object(cls=DataSourceClientModel)
    def last(self):
        # 获取最后一个资源
        return self._get_all_resources_request()[-1]

    @convert_to_object(cls=DataSourceClientModel)
    def get(self, id=None, name=None):
        if name:
            ds_list = self.api.send(endpoint=f"{self.endpoint}?name={name}", method="GET")
            if ds_list:
                return ds_list
            else:
                raise DataSourceNotFound(f"Data Source {name} not found")

        if not id:
            raise ValueError("No ID or Name provided")
        # 通过资源ID来获取
        return self.api.send(endpoint=f"{self.endpoint}{id}", method="GET")

    @convert_to_object(cls=DataSourceClientModel)
    def register(self, ds_type, ds_access_config, ds_name=None):
        data = {
            "type": ds_type, "name": ds_name,
            "access_config": ds_access_config
        }
        return self.api.send(endpoint=self.endpoint, method="POST", data=data)

    def upload_file_to_oss(self, local_file_path):
        oss_info = self.create_upload_params()['oss']
        file_name = os.path.basename(local_file_path)
        oss_file_uri = f"{oss_info['oss_uri_prefix']}{file_name}"
        download_url = upload_to_oss(oss_info, local_file_path, oss_file_uri)
        return download_url

    def create_upload_params(self, expiration=None, file_max_size=None):
        params = {'expiration': expiration, 'file_max_size': file_max_size}
        return self.api.send(endpoint=f"{self.endpoint}upload_params", method="POST", params=params)

    def upload_file_to_server(self, local_file_path):
        # 上传文件到服务器
        return self.api.send(
            endpoint=f"{self.endpoint}upload_file",
            method="POST",
            files={'file': open(local_file_path, 'rb')}
        )

    def create_from_local_file(self, local_file_path, direct_to_oss=True):
        file_ext = os.path.splitext(local_file_path)[-1]
        if file_ext not in ['.csv', '.xls', '.xlsx']:
            raise UnsupportedFileType(f"File type {file_ext} not supported")

        if direct_to_oss:
            download_url = self.upload_file_to_oss(local_file_path)
        else:
            download_url = self.upload_file_to_server(local_file_path)

        if file_ext == '.csv':
            return self.register(ds_type="CSV", ds_access_config={
                "location_type": "http",
                "location_url": download_url,
            })
        elif file_ext in ['.xls', '.xlsx']:
            return self.register(ds_type="Excel", ds_access_config={
                "location_type": "http",
                "location_url": download_url,
            })
        else:
            raise UnsupportedFileType(f"File type {file_ext} not supported")