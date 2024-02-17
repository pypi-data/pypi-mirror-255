import requests
from rmbclient.exceptions import UploadFileError
from rmbclient import log
from requests.exceptions import HTTPError


def upload_to_oss(oss_info, local_file_path, oss_file_uri):
    # 解析oss_info字典
    bucket_name = oss_info['bucket']
    oss_params = oss_info['params']
    oss_endpoint = oss_info['url']

    # 构建完整的OSS URL
    oss_url = f'http://{bucket_name}.{oss_endpoint}'

    # 准备表单数据
    data = {
        'OSSAccessKeyId': oss_params['OSSAccessKeyId'],
        'policy': oss_params['policy'],
        'signature': oss_params['signature'],
        'key': oss_file_uri,  # OSS中的文件路径和名称
    }

    # 打开要上传的文件
    with open(local_file_path, 'rb') as file:
        files = {'file': file}

        # 发送POST请求上传文件
        response = requests.post(oss_url, data=data, files=files)

    try:
        response.raise_for_status()
    except HTTPError as e:
        raise UploadFileError(f"OSS Upload Failed: {e}")

    download_url = f'https://{bucket_name}.{oss_endpoint}/{oss_file_uri}'
    return download_url


if __name__ == '__main__':
    # 示例用法
    oss_info1 = {
        'bucket': 'xxx',
        'params': {
            'OSSAccessKeyId': 'xxx',
            'policy': 'xxx=',
            'signature': 'xxx+o8='
        },
        'url': 'oss-cn-shanghai.aliyuncs.com'
    }
    local_file_path1 = '/Users/sdk.log'
    oss_file_uri1 = 'a/sdk.log'

    # 调用函数
    upload_to_oss(oss_info1, local_file_path1, oss_file_uri1)
