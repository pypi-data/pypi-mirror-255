import inspect
import sys
from rmbcommon.exceptions.server import *


class ServerConnectionError(Exception):
    code = 9000
    message = "Server Connection Error"


class ServerError(Exception):
    # 无法解析返回的数据，未知的服务器错误
    code = 9001
    message = "Server Error"


class UnknownServerError(Exception):
    # 服务器返回了错误码，但client端无法识别
    code = 9002
    message = "Unknown Server Error"


class UploadFileError(Exception):
    code = 9003
    message = "Upload File Error"


class UnsupportedFileType(Exception):
    code = 9004
    message = "Unsupported File Type"


def get_exception_by_code(code):
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            if getattr(obj, 'code') == code:
                return obj
    return None


def raise_exception_by_code(code, message):
    ex = get_exception_by_code(code)
    if ex:
        raise ex(message)
    else:
        raise UnknownServerError(f"Unknown error code: {code} {message}")
