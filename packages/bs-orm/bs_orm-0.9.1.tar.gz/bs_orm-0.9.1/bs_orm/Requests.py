import sqlite3
import os
import datetime
from . import db_settings
from .DataTypes import Table
from .logic_assistent import composit_function, base_function

def search(table, **qwargs) -> list[Table]:
    base_function.serach(table, **qwargs)

def update(tables:object, **qwargs) -> bool:
    if type(tables) != list:
        tables = [tables]
    return base_function.update(tables, **qwargs)

def execute(table, execut: str) -> list[any]:
    return base_function.update(table, execute)

def add_if_not_exist(cls, **qwargs) -> bool:
    if len(cls.search(**qwargs)) != 0:
        return False
    obj = qwargs
    new_cls = type(cls.__name__, (Table,), obj)
    return new_cls.save()

def add(cls, **qwargs) -> bool:
    return base_function.add(cls, **qwargs)
    base_function.execute(cls, execut)

def create_tables(models) -> None:
    db_settings.models = models
    conn = sqlite3.connect(db_settings.path)
    cur = conn.cursor()
    cur.executescript(composit_function.create_execute() +
                      'CREATE TABLE IF NOT EXISTS "migrations"(filename TEXT)')
    conn.commit()
    conn.close()

def migrate() -> None:
    conn = sqlite3.connect(db_settings.path)
    cur = conn.cursor()
    cur.execute('SELECT sql FROM sqlite_master WHERE type="table"')
    old_data = ';\n'.join([x[0] for x in cur.fetchall()])
    new_data = composit_function.create_execute()
    for_old = [
        'CREATE TABLE "migrations"(filename TEXT)', 'CREATE TABLE ', ';']
    for_new = ['CREATE TABLE IF NOT EXISTS ', ';']
    for param in for_old:
        old_data = old_data.replace(param, '')
    for param in for_new:
        new_data = new_data.replace(param, '')
    old_data = old_data.replace('\n\n', '\n').strip('\n')
    new_data = new_data.replace('\n\n', '\n').strip('\n')

    add_list = []
    remove_list = []
    update_list_r = []
    update_list_a = []
    FD_add_list = []
    FD_remove_list = []
    FD_update_list_r = []
    FD_update_list_a = []

    def get_line(data, table_name):
        table_name = table_name.replace('"', '')
        for table in data.split('\n'):
            table = table.replace('"', '')
            if table_name in table and not table[table.find(table_name)+\
                                                 len(table_name)].isalnum():
                return table
        return ''

    for old_t in old_data.split('\n'):
        old_table = old_t.split('(')[0]
        if old_table not in new_data:
            remove_list.append(f'DROP TABLE {old_table}')
            FD_remove_list.append(f'CREATE TABLE IF NOT EXISTS {old_t}')
        else:
            if old_t.replace('"', '') not in new_data:
                old_t = old_t.split('(')
                table = get_line(new_data, old_t[0])
                for atr in [x \
                            for x in "(".join(old_t[1:]).strip(')').split(',')\
                                if (x != '' and x != ' ' and x != [])]:
                    if atr.replace('"', '').strip() not in table:
                        col_name = atr.split('"')[1]
                        update_list_r.append(
                            f'ALTER TABLE {old_t[0]} DROP COLUMN {col_name}')
                        FD_update_list_r.append(
                            f'ALTER TABLE {old_t[0]} ADD COLUMN {atr}')

    for new_t in new_data.split('\n'):
        new_table = new_t.split('"')[1]
        if new_t.split('"')[1] not in old_data:
            add_list.append(f'CREATE TABLE IF NOT EXISTS {new_t}')
            FD_add_list.append(f'DROP TABLE {new_table}')
        else:
            if new_t not in old_data:
                new_t = new_t.split('"')
                table = get_line(old_data, new_t[1])
                for atr in ('"'+'"'.join(new_t[3:])[:-1]).split(','):
                    if atr.replace('"', '').strip() not in table:
                        update_list_a.append(
                            f'ALTER TABLE "{new_t[1]}" ADD COLUMN {atr}')
                        atr = atr.split('"')[1]
                        FD_update_list_a.append(
                            f'ALTER TABLE "{new_t[1]}" DROP COLUMN "{atr}"')

    def concatenete_data(string, list_string):
        for i in list_string:
            if string != '\n':
                string += ';\n'
            string += ";\n".join(i)
        return string

    upgrade = '\n'
    upgrade = concatenete_data(
        upgrade, [add_list, remove_list, update_list_r, update_list_a])
    downgrade = '\n'
    downgrade = concatenete_data(
        downgrade, [FD_add_list, FD_remove_list, \
                    FD_update_list_a, FD_update_list_r])

    textFromPattern = f'''import sqlite3
from bs_orm import db_settings

def upgrade():
    upgrade_execut = """{upgrade} """
    conn = sqlite3.connect(db_settings.path)
    cur = conn.cursor()
    cur.executescript(upgrade_execut)

def downgrade():
    downgrade_execut = """{downgrade} """
    conn = sqlite3.connect(db_settings.path)
    cur = conn.cursor()
    cur.executescript(downgrade_execut)'''

    try:
        os.mkdir('migrations')
    except:
        pass

    fileName = str(datetime.datetime.now().timestamp())
    with open(f'./migrations/{fileName}.py', 'w') as f:
        f.write(textFromPattern)

    cur.execute(f'INSERT INTO migrations (filename) VALUES({fileName})')
    print(upgrade)
    cur.executescript(upgrade)
    conn.commit()
    conn.close()