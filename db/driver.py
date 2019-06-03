from peewee import *


def init_db():
    return SqliteDatabase('scrn.db', pragmas={'foreign_keys': 1})