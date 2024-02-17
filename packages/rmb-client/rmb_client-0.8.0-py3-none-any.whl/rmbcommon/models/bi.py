from rmbcommon.models.base import BaseCoreModel

class BIQuestion:

    def __init__(self, content):
        self.content = content

    def __str__(self):
        return self.content

class BIQueryPlan:
    pass


class NaturalQuery:

    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return self.content


class StrucQuery:

    def __init__(self, content: str, params: dict = None):
        self.content = content
        self.params = params or {}

    def __str__(self):
        if self.params:
            params_formatted = "\n".join([f"{key}={value}" for key, value in self.params.items()])
            return f"Query: \n{self.content}\nParams:\n{params_formatted}"
        else:
            return f"Query: \n{self.content}"

    def __repr__(self):
        return self.__str__()


class QueryResult:

    def __init__(self, query: StrucQuery, result):  # result: DataFrame
        self.query = query
        self.result = result

    def __str__(self):
        return self.to_string(top_n=3)

    def __repr__(self):
        return f"Data Result: {self.row_count} 行 {self.column_count} 列"

    def to_string(self, top_n=100):
        # 截取 前N行
        query_str = str(self.query)
        result_str = self.result.head(top_n).to_string(index=False)
        return f"\nQuery: \n{query_str}\nResult({top_n} of {self.row_count}rows):\n{result_str}"


    @property
    def rows(self):
        return self.result.to_numpy()

    @property
    def columns(self):
        return self.result.columns

    @property
    def row_count(self):
        return len(self.result)

    @property
    def column_count(self):
        return len(self.columns)


class BIAnswer(BaseCoreModel):
    __properties_init__ = [
        'status',
        'elapsed_time',
        'answer_text',
        'answer_file',
        'answer_image',
        'structure_queries',
    ]

    def __str__(self):
        return (f"[{self.status}-{self.elapsed_time}s]|{'[File]' if self.answer_file else ''}"
                f"|{'[Image]' if self.answer_image else ''} "
                f"{self.answer_text}")

    def __repr__(self):
        return self.__str__()

