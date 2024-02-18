from . import db_settings
from .logic_assistent import base_function
import datetime

class DataType:
    def __init__(self, size=0, nullable=False, default=None, primary_key=False, check=None, unique=None):
        if primary_key and nullable:
            raise Exception("And so, are you sure you need to make a database? because what you're trying to do reminds me of self-castration. PK must not be null")
        self.size = size
        self.nullable = nullable
        self.default = default
        self.unique = unique
        self.check = check
        self.primary_key = primary_key

class String(DataType):
    name = "TEXT"
    type_r = str
    type_w = str
    inserts = ['"']*2


class Integer(DataType):
    name = "INTEGER"
    type_r = int
    type_w = int
    inserts = ['']*2

class Float(DataType):
    name = "REAL"
    type_r = float
    type_w = float
    inserts = ['']*2

class DataTime(DataType):
    name = "TEXT"
    type_r = lambda self, x : datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S.%f')
    type_w = str
    inserts = ['"']*2

class ForeignKey(DataType):
    name = "REFERENCES"
    def __init__(self, table_column, on_delete=None, on_update=None, size=0, nullable=False, default=None, primary_key=False, check=None, unique=None):
        self.column = ' ('.join(table_column.split('.'))+')'
        if on_delete != None:
            self.column += ' ON DELETE ' + on_delete
        if on_update != None:
            self.column += ' ON UPDATE ' + on_update

class Table:
    def __init__(self, **qwargs):
        for k, v in qwargs.items():
            self.__all__.__setattr__(k, v)
    
    @classmethod
    def search(cls, **qwargs):
        return base_function.serach(cls, **qwargs)
        
    @classmethod
    def save(cls) -> bool:
        return base_function.save(cls)

    @classmethod
    def create(cls, **qwargs):
        return base_function.create(cls, **qwargs)
    
    @classmethod
    def add_if_not_exist(cls, **qwargs) -> bool:
        return base_function.add_if_not_exist(cls, **qwargs)

    @classmethod
    def add(cls, **qwargs) -> bool:
        return base_function.add(cls, **qwargs)

    @classmethod
    def execute(cls, execut: str) -> list[any]:
        return base_function.execute(cls, execut)
    
    @classmethod
    def update(cls, **qwargs) -> bool:
        return base_function.update([cls], **qwargs)
    
    @classmethod
    def __convert_to_write__(self, col, val):
        clas = getattr(db_settings.models, self.__name__)
        value = getattr(clas, col)
        col = f'[{col}]'
        if val != None:
            val = str(value.type_w(val)).join(value.inserts)
        else:
            val = 'NULL'
        return col, val
    
    @classmethod
    def __convert_of_read__(self, col, val):
        value = getattr(self, col)
        val = value.type_r(val)
        return col, val