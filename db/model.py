from datetime import datetime
from enum import Enum, unique

from peewee import *

from db.driver import init_db

db = init_db()


class SqlEnum(Enum):
    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)

    @classmethod
    def values(cls):
        return [item.value for item in cls]

    @classmethod
    def values_sql(cls):
        return '(' + [item.value for item in cls].__str__()[1:-1] + ')'


@unique
class StatType(SqlEnum):
    XP = 0
    AWARD = 1


@unique
class EndGameCode(SqlEnum):
    UNKNOWN = 0
    LOST = 1
    WIN = 2
    WIN_RED = 3
    WIN_BLUE = 4
    STAT_IMPORT = 1024  # Fake game record to import stats


class BaseModel(Model):
    class Meta:
        database = db


class Server(BaseModel):
    name = CharField(unique=True)
    port = IntegerField(default=7707)


class Mutator(BaseModel):
    name = CharField(unique=True, max_length=64)


class GameType(BaseModel):
    name = CharField()
    game_class = CharField(max_length=64)


class GameTypeMutator(BaseModel):
    game_type = ForeignKeyField(GameType, backref='mutators')
    mutator = ForeignKeyField(Mutator, backref='game_types')


class Game(BaseModel):
    server = ForeignKeyField(Server, backref='games')
    type = ForeignKeyField(GameType, backref='games', null=True)
    difficulty = IntegerField(null=True)
    length = IntegerField(null=True)
    start_time = DateTimeField(default=datetime.now)
    end_time = DateTimeField(null=True)
    end_code = IntegerField(null=True)


class Player(BaseModel):
    id = BigIntegerField(primary_key=True)
    name = CharField(null=True, max_length=64)
    perk_name = CharField(null=True, max_length=64)
    perk_index = IntegerField(null=True)
    model = CharField(null=True, max_length=64)


class Stat(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(unique=True, max_length=64)
    type = IntegerField(default=StatType.XP.value, constraints=[Check('type in ' + StatType.values_sql())])


class StatName(BaseModel):
    name = CharField(primary_key=True, max_length=64)
    stat = ForeignKeyField(Stat, backref='names')


class PlayerXp(BaseModel):
    player = ForeignKeyField(Player, backref='xp')
    stat = ForeignKeyField(Stat)
    xp = BigIntegerField()

    class Meta:
        primary_key = CompositeKey('player', 'stat')


class PlayerAward(BaseModel):
    player = ForeignKeyField(Player, backref='awards')
    stat = ForeignKeyField(Stat)
    value = TextField()

    class Meta:
        primary_key = CompositeKey('player', 'stat')


class GameXp(BaseModel):
    game = ForeignKeyField(Game)
    player = ForeignKeyField(Player)
    stat = ForeignKeyField(Stat)
    xp = BigIntegerField()

    class Meta:
        primary_key = CompositeKey('game', 'player', 'stat')
