# Error Design

class UncaughtError(Exception):
    code = -1
    message = "Uncaught Internal Error"


class MyBaseError(Exception):
    code = 0
    message = "Base error"


# 1000 - 配置类错误
class ManagementError(MyBaseError):
    code = 1
    message = "Management Error"


# 2000 - QA对话类错误
class QAError(MyBaseError):
    code = 2
    message = "Question Answering Error"


# 3000 - 内部错误
class InternalError(MyBaseError):
    code = 3
    message = "Internal error"


################################

class Unauthorized(ManagementError):
    code = 1000
    message = "Unauthorized"


class DataSourceExists(ManagementError):
    code = 1001
    message = "Datasource already exists"


class DataSourceNotFound(ManagementError):
    code = 1002
    message = "Datasource not found"


class ChatNotFound(ManagementError):
    code = 1003
    message = "Chat not found"


class ParameterError(ManagementError):
    code = 1004
    message = "Parameter error"


class DataSourceConfigError(ManagementError):
    code = 1005
    message = "Datasource config error"

class TenantNotFound(ManagementError):
    code = 1006
    message = "Tenant not found"

################################

class QAErrorNoMatchDataSource(QAError):
    code = 2002
    message = "No match datasource"


class QAErrorInsufficientData(QAError):
    code = 2003
    message = "Insufficient data"


class QAErrorIncompleteQuestion(QAError):
    code = 2004
    message = "Incomplete question"


class QAErrorCannotHandle(QAError):
    code = 2005
    message = "Cannot handle"


####################################


class PromptTooLong(InternalError):
    code = 3001
    message = "Prompt too long"


class InvalidStrucQuery(InternalError):
    code = 3002
    message = "Invalid query syntax"

