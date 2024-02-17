from rmbcommon.exceptions.server import DataSourceConfigError

# Excel

class TooLargeFile(DataSourceConfigError):
    code = 10051
    message = "文件大小超过限制"

class TooManyColumns(DataSourceConfigError):
    code = 10052
    message = "表格列数超过限制"

class ExcelEmptyFile(DataSourceConfigError):
    code = 10053
    message = "文件中没有识别到表格"

class InvalidFileExt(DataSourceConfigError):
    code = 10054
    message = "文件扩展名不合法"

