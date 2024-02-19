from typing import Dict, List, Optional
from functools import wraps
import json
from tabulate import tabulate


def json_to_string(func):
    # 将函数返回的JSON dict对象转换为字符串
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return json.dumps(result, indent=4, ensure_ascii=False)

    return wrapper


class DataBaseObject:
    #  用于存储到数据库中的属性
    _save_in_db_properties = []

    @property
    def db_properties(self):
        return {k: v for k, v in self.__dict__.items()
                if k in self._save_in_db_properties}

    def to_dict(self):
        raise NotImplementedError

    def to_dict_for_llm(self):
        raise NotImplementedError

    @json_to_string
    def to_string(self):
        return self.to_dict()

    @json_to_string
    def to_string_for_llm(self):
        return self.to_dict_for_llm()

    def __str__(self):
        return self.to_string()


class DataField(DataBaseObject):
    _save_in_db_properties = ['name', 'full_name', 'origin_desc',
                              'curr_desc', 'curr_desc_stat',
                              'sample_data'
                              ]
    _in_dict_properties = (
            _save_in_db_properties + ['related_field', 'related_field_precision_rate']
    )

    def __init__(self, name, table, origin_desc=None, curr_desc=None,
                 curr_desc_stat=None,
                 related_field=None,
                 related_field_precision_rate=None,
                 sample_data=None, **kwargs):
        self.name = name
        self.origin_desc = origin_desc
        self.table = table  # Reference to the DataTable
        self.full_name = f"{self.table.schema.name}.{self.table.name}.{self.name}"
        if curr_desc:
            self.curr_desc = curr_desc
            self.curr_desc_stat = curr_desc_stat
        else:
            self.curr_desc = origin_desc
            self.curr_desc_stat = 'origin'
        self.sample_data = sample_data
        self.related_field = related_field  # Reference to related DataField, if any
        self.related_field_precision_rate = related_field_precision_rate

    def set_related_field(self, field):
        self.related_field = field

    def __repr__(self):
        return f"<DataField(name='{self.full_name}', curr_desc='{self.curr_desc}')>"

    def to_dict(self, includes=(), excludes=()):
        # includes 为空，则默认全部取
        # excludes 优先级高于 includes

        _d = {}
        for i in self._in_dict_properties:
            if i in excludes or (includes and i not in includes):
                continue
            _d[i] = getattr(self, i)

        if self.related_field:
            _d['related_field'] = self.related_field.full_name
        return _d


class DataTable(DataBaseObject):
    """
    name: 表名（sheet名、collection名）
    origin_desc: 数据源中的原始描述
    curr_desc: 当前在RMB中的描述
    curr_desc_stat: 当前描述的状态，可选值：origin, human, ai
    custom_configs: 自定义字段，用于存储一些额外的信息, dict类型，用json.dumps()转换为字符串存储
        对于Excel数据源的表格，custom_configs 中存储的是：tables

    """

    _save_in_db_properties = ['name', 'full_name', 'origin_desc',
                              'curr_desc', 'curr_desc_stat']

    _in_dict_properties = _save_in_db_properties

    def __init__(self, name, schema, origin_desc=None,
                 curr_desc=None, curr_desc_stat=None,
                 **kwargs):
        self.name = name
        self.origin_desc = origin_desc
        self.schema = schema  # Reference to the DataSchema
        self.full_name = f"{self.schema.name}.{self.name}"
        if curr_desc:
            self.curr_desc = curr_desc
            self.curr_desc_stat = curr_desc_stat
        else:
            # 如果没有指定 curr_desc，则默认使用 origin_desc
            self.curr_desc = origin_desc
            self.curr_desc_stat = 'origin'
        self.fields = []
        self.fields_dict: Dict[str, DataField] = {}

    def add_field(self, field: DataField):
        self.fields.append(field)
        self.fields_dict[field.name] = field

    def __repr__(self):
        return f"<DataTable(name='{self.full_name}', curr_desc='{self.curr_desc}')>"

    def to_dict(self, level='field', includes=(), excludes=()):
        _d = {}
        for i in self._in_dict_properties:
            if i in excludes or (includes and i not in includes):
                continue
            _d[i] = getattr(self, i)

        if level == 'field':
            _d['fields'] = [f.to_dict(includes=includes, excludes=excludes)
                            for f in self.fields]
        return _d

    def to_dict_for_llm(self):
        # 如果有任何一个字段的 curr_desc 为空，则需要AI生成
        # table 中去掉一些不需要的字段，减少token数量
        # 保留：name, curr_desc
        need_infer = any(not f.curr_desc for f in self.fields)
        return self.to_dict(includes=('name', 'curr_desc')) if need_infer else {}


class DataSchema(DataBaseObject):
    _save_in_db_properties = ['name', 'origin_desc', 'curr_desc',
                              'curr_desc_stat', 'custom_configs']
    _in_dict_properties = _save_in_db_properties

    def __init__(self, name, metadata, origin_desc=None,
                 curr_desc=None, curr_desc_stat=None,
                 custom_configs=None, **kwargs):
        self.name = name
        self.metadata = metadata  # Reference to the MetaData
        self.origin_desc = origin_desc
        if curr_desc:
            self.curr_desc = curr_desc
            self.curr_desc_stat = curr_desc_stat
        else:
            self.curr_desc = origin_desc
            self.curr_desc_stat = 'origin'
        self.custom_configs = custom_configs
        self.tables = []
        self.tables_dict: Dict[str, DataTable] = {}

    def add_table(self, table: DataTable):
        self.tables.append(table)
        self.tables_dict[table.name] = table

    @property
    def custom_configs_dict(self):
        if not self.custom_configs:
            return {}
        if isinstance(self.custom_configs, dict):
            return self.custom_configs
        elif isinstance(self.custom_configs, str):
            return json.loads(self.custom_configs)
        else:
            raise ValueError(f"Invalid custom_configs type: {type(self.custom_configs)}")

    def set_custom_config(self, key, value):
        configs = self.custom_configs_dict
        configs[key] = value
        self.custom_configs = json.dumps(configs)

    def get_custom_config(self, key):
        return self.custom_configs_dict.get(key)

    def __repr__(self):
        return f"<Schema: {self.name}>"

    def to_dict(self, level='field', includes=(), excludes=()):
        # level: field, table, schema
        _d = {}
        for i in self._in_dict_properties:
            if i in excludes or (includes and i not in includes):
                continue
            _d[i] = getattr(self, i)

        if level in ('table', 'field'):
            _d['tables'] = [t.to_dict(level, includes=includes, excludes=excludes)
                            for t in self.tables]
        return _d

    def to_dict_for_llm(self):
        # if table.to_dict_for_llm() is empty, it will be ignored
        need_infer_tables = [table.to_dict_for_llm() for table in self.tables
                             if table.to_dict_for_llm()]
        if need_infer_tables or (not self.curr_desc):
            return {
                'name': self.name,
                'curr_desc': self.curr_desc,
                'tables': need_infer_tables
            }
        else:
            return {}


class MetaData(DataBaseObject):
    def __init__(self, name, datasource_id=''):
        self.name = name
        self.datasource_id = datasource_id
        self.schemas = []
        self.schemas_dict: Dict[str, DataSchema] = {}

    def add_schema(self, schema: DataSchema):
        self.schemas.append(schema)
        self.schemas_dict[schema.name] = schema

    @classmethod
    def load_from_dict(cls, data: dict):
        """
        Load metadata from a dictionary structure.
        The expected format is:
        {
            'name': 'metadata_name',
            'datasource_id': '',
            'schemas': [
                {
                    'name': 'schema_name',
                    'tables': [
                        {
                            'name': 'table_name',
                            'fields': [
                                {
                                    'name': 'field_name',
                                    'origin_desc': 'original description',
                                    'related_field': 'schema2.table2.field2'
                                    ...
                                },
                                ...
                            ],
                            ...
                        },
                        ...
                    ],
                    ...
                },
                ...
            ]
        }
        """
        # 临时字典，用于存储字段引用
        field_refs = {}
        metadata = cls(data.get('name'), data.get('datasource_id'))
        # 首先，创建所有的 schema、table 和 field，但不设置 related_field
        for schema_data in data.get('schemas', []):
            schema = DataSchema(
                name=schema_data.get('name', ''),
                metadata=metadata,
                origin_desc=schema_data.get('origin_desc'),
                curr_desc=schema_data.get('curr_desc'),
                curr_desc_stat=schema_data.get('curr_desc_stat'),
                custom_configs=schema_data.get('custom_configs'),
            )

            for table_data in schema_data.get('tables', []):
                table = DataTable(
                    name=table_data.get('name', ''),
                    schema=schema,
                    origin_desc=table_data.get('origin_desc'),
                    curr_desc=table_data.get('curr_desc'),
                    curr_desc_stat=table_data.get('curr_desc_stat'),
                )

                for field_data in table_data.get('fields', []):
                    field = DataField(
                        name=field_data.get('name', ''),
                        table=table,
                        origin_desc=field_data.get('origin_desc'),
                        curr_desc=field_data.get('curr_desc'),
                        curr_desc_stat=field_data.get('curr_desc_stat'),
                        sample_data=field_data.get('sample_data'),
                    )
                    table.add_field(field)
                    # 创建一个唯一键来标识每个字段
                    field_key = f"{schema.name}.{table.name}.{field.name}"
                    field_refs[field_key] = field

                schema.add_table(table)

            metadata.add_schema(schema)

        # 现在，使用 field_refs 字典来设置 related_field 属性
        for _s in data.get('schemas', []):
            for _t in _s.get('tables', []):
                for _f in _t.get('fields', []):
                    field = field_refs.get(f"{_s.get('name', '')}.{_t.get('name', '')}.{_f.get('name', '')}")
                    related_field_key = _f.get('related_field')
                    if related_field_key and related_field_key in field_refs:
                        # 设置相关字段的引用
                        field.set_related_field(field_refs[related_field_key])
        return metadata

    def update_from_dict(self, data: dict):
        """
        Update the existing metadata with the given dictionary.
        """
        # 临时存储字段关联信息
        temp_related_fields = {}

        # 更新或添加schemas
        for schema_data in data.get('schemas', []):
            schema_name = schema_data.get('name', '')
            schema = self.schemas_dict.get(schema_name)
            if not schema:
                # 如果找不到schema，就创建一个新的
                schema = DataSchema(
                    name=schema_name,
                    metadata=self,
                    origin_desc=schema_data.get('origin_desc'),
                    curr_desc=schema_data.get('curr_desc'),
                    curr_desc_stat=schema_data.get('curr_desc_stat'),
                    custom_configs=schema_data.get('custom_configs'),
                )
                self.add_schema(schema)
            else:
                # 更新schema的属性
                schema.origin_desc = schema_data.get('origin_desc', schema.origin_desc)
                schema.curr_desc = schema_data.get('curr_desc', schema.curr_desc)
                schema.curr_desc_stat = schema_data.get('curr_desc_stat', schema.curr_desc_stat)
                schema.custom_configs = schema_data.get('custom_configs', schema.custom_configs)

            # 更新或添加tables
            for table_data in schema_data.get('tables', []):
                table_name = table_data.get('name', '')
                table = schema.tables_dict.get(table_name)
                if not table:
                    # 如果找不到table，就创建一个新的
                    table = DataTable(
                        name=table_name,
                        schema=schema,
                        origin_desc=table_data.get('origin_desc'),
                        curr_desc=table_data.get('curr_desc'),
                        curr_desc_stat=table_data.get('curr_desc_stat'),
                    )
                    schema.add_table(table)
                else:
                    # 更新table的属性
                    table.origin_desc = table_data.get('origin_desc', table.origin_desc)
                    table.curr_desc = table_data.get('curr_desc', table.curr_desc)
                    table.curr_desc_stat = table_data.get('curr_desc_stat', table.curr_desc_stat)

                # 更新或添加fields
                for field_data in table_data.get('fields', []):
                    field_name = field_data.get('name', '')
                    field = table.fields_dict.get(field_name)
                    if not field:
                        # 如果找不到field，就创建一个新的
                        field = DataField(
                            name=field_name,
                            table=table,
                            origin_desc=field_data.get('origin_desc'),
                            curr_desc=field_data.get('curr_desc'),
                            curr_desc_stat=field_data.get('curr_desc_stat'),
                            sample_data=field_data.get('sample_data'),
                        )
                        table.add_field(field)
                    else:
                        # 更新field的属性
                        field.origin_desc = field_data.get('origin_desc', field.origin_desc)
                        field.curr_desc = field_data.get('curr_desc', field.curr_desc)
                        field.curr_desc_stat = field_data.get('curr_desc_stat', field.curr_desc_stat)
                        field.sample_data = field_data.get('sample_data', field.sample_data)

                    # 保存字段关联信息
                    full_field_name = f"{schema_data.get('name')}.{table_data.get('name')}.{field_data.get('name')}"
                    related_field_name = field_data.get('related_field')
                    if related_field_name:
                        # 存储字段关联信息，稍后处理
                        temp_related_fields[full_field_name] = related_field_name

        # 更新related_field
        for field_name, related_field_name in temp_related_fields.items():
            field = self.get_field_by_full_name(field_name)
            related_field = self.get_field_by_full_name(related_field_name)
            if field and related_field:
                # 设置字段关联
                field.set_related_field(related_field)

    def __repr__(self):
        return f"{self.datasource_id} {self.summary} \n\n{self.to_table()}"

    def to_dict(self, level='field', includes=(), excludes=()):
        # level: field, table, schema
        # includes 默认取全部
        # excludes 优先级高于includes
        return {
            'name': self.name,
            'datasource_id': self.datasource_id,
            'schemas': [schema.to_dict(level, includes=includes, excludes=excludes)
                        for schema in self.schemas]
        }

    def to_dict_for_agent(self):
        result = {
            'name': self.name,
            'datasource_id': self.datasource_id,
            'schemas': [schema.to_dict(
                level='field',
                includes=(
                    'name',
                    'curr_desc',
                    'related_field',
                    'related_field_precision_rate',
                )) for schema in self.schemas]
        }

        # 修改fields的结构，减少token数量
        for schema in result['schemas']:
            for table in schema.get('tables', []):
                for field in table.get('fields', []):
                    # 去掉无用的 related_field
                    if field.get('related_field') is None:
                        field.pop('related_field', None)
                        field.pop('related_field_precision_rate', None)

                    # 更名，更直接，更少的字符
                    field['desc'] = field.pop('curr_desc', None)

        return result

    def to_dict_for_llm(self):
        return {
            'name': self.name,
            'datasource_id': self.datasource_id,
            'schemas': [schema.to_dict_for_llm() for schema
                        in self.schemas if schema.to_dict_for_llm()]
        }

    @property
    def summary(self):
        """
        Summarize the metadata。只有Schema和Table给出前10条 item，Field不给出。
        Like this:
            共有：1 Schema (public), 1 Table (users), 2 Fields.
        """
        summary = f"共有："

        # Summarizing schemas
        schema_count = len(self.schemas)
        if schema_count <= 1:
            summary += f"{schema_count} Schema ("
        else:
            summary += f"{schema_count} Schemas ("
        for i, schema in enumerate(self.schemas[:10]):
            summary += schema.name
            if i < min(9, schema_count - 1):  # Add comma if not the last item
                summary += ","
        if schema_count > 10:
            summary += "..."
        summary += "), "

        # Summarizing tables and fields
        total_tables = 0
        total_fields = 0
        table_names = []

        for schema in self.schemas:
            total_tables += len(schema.tables)
            for table in schema.tables:
                total_fields += len(table.fields)
                if len(table_names) <= 5:
                    table_names.append(table.full_name)

        # Formatting tables list
        table_list = ",".join(table_names)
        if len(table_names) > 5:
            table_list += "..."

        if total_tables <= 1:
            summary += f"{total_tables} Table ({table_list}), "
        else:
            summary += f"{total_tables} Tables ({table_list}), "
        if total_fields <= 1:
            summary += f"{total_fields} Field."
        else:
            summary += f"{total_fields} Fields."
        return summary

    def get_field_by_full_name(self, full_name):
        """
        根据字段的完整名称来查找字段对象。
        完整名称格式为 "schema_name.table_name.field_name"
        """
        schema_name, table_name, field_name = full_name.split('.')
        for schema in self.schemas:
            if schema.name == schema_name:
                for table in schema.tables:
                    if table.name == table_name:
                        for field in table.fields:
                            if field.name == field_name:
                                return field
        return None

    def to_table(self, level='field'):  # level: field, table, schema
        data = []
        for schema in self.schemas:
            schema_desc = schema.name
            schema_desc += f"({schema.curr_desc})" if schema.curr_desc else ""
            if level == 'schema':
                _s = {
                    'Schemas': schema_desc,
                }
                data.append(_s)
            elif level in ('table', 'field'):
                for table in schema.tables:
                    table_desc = table.name
                    table_desc += f"({table.curr_desc})" if table.curr_desc else ""
                    _t = {
                        'Schemas': schema_desc,
                        'Tables': table_desc,
                    }
                    if level == 'field':
                        known_f = len([f for f in table.fields if f.curr_desc])
                        all_f = len(table.fields)
                        fields = f"{known_f}/{all_f}"
                        _t['Fields(known/all)'] = fields
                    data.append(_t)
            else:
                raise ValueError(f"Invalid level: {level}")
        return tabulate(data, headers="keys", tablefmt="plain")

    @property
    def table_count(self):
        return sum([len(schema.tables) for schema in self.schemas])

    @property
    def field_count(self):
        return sum([len(table.fields) for schema in self.schemas for table in schema.tables])
