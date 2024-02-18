from .. import db_settings
from .. import DataTypes

class empty:
    pass


def for_size(content, request):
    try:
        if content.size:
            request += f'({content.size})'
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


def for_pk(content, request):
    try:
        if content.primary_key:
            request += f'PRIMARY KEY '
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


def for_auto_increment(content, request):
    try:
        if content.auto_increment:
            request += f'AUTOINCREMENT '
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


def for_null(content, request):
    try:
        if not content.nullable:
            request += f'NOT NULL '
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


def for_unique(content, request):
    try:
        if content.unique:
            request += f'UNIQUE '
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


def for_default(content, request):
    try:
        if content.default:
            request += f'DEFAULT "{content.default}"'
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


def for_check(content, request):
    try:
        if content.check:
            request += f'CHECK {content.check} '
        return ['ok', request]
    except Exception as ex:
        return ['error', ex]


CHECKS = [for_size, for_pk, for_auto_increment,
          for_null, for_unique, for_default, for_check]

def get_table(table_name: str, table: dict):
    returned = f'CREATE TABLE IF NOT EXISTS "{table_name}"('
    for column, info_column in table.items():
        try:
            if info_column.__class__.__weakref__.__objclass__ == DataTypes.DataType:
                returned += f'"{column}" {info_column.name} '
                if info_column.__class__.__name__ == 'ForeignKey':
                    returned += info_column.column + ' '
                else:
                    for check in CHECKS:
                        res = check(info_column, returned)
                        if res[0] == 'ok':
                            returned = res[1]
                returned = returned+', '

        except Exception as ex:
            raise Exception(
                "Fuck you ugly motherless. Do you understand that in file models.py you need have only table name as class?")
    if 'PRIMARY KEY' not in returned:
        returned += f'"id" INTEGER PRIMARY KEY  '
    returned = returned[:-2]+')'
    return returned

def create_execute():
    request = ''
    for mod_name, value in db_settings.models.__dict__.items():
        if hasattr(value, '__module__') and 'models' in value.__module__:
            table_name = mod_name
            mod = dict(value.__dict__)
            for i in empty.__dict__:
                if i in mod:
                    mod.pop(i)
            request += get_table(table_name, mod)+';\n'
    return request

def clear_default(obj):
    ret = {}
    negative_value = empty.__dict__
    for k, v in obj.__dict__.items():
        if k not in negative_value:
            ret[k] = v
    return ret