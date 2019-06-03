import argparse

from db.model import *

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 2
VERSION = '{}.{}.{}'.format(VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH)


def init():
    db.connect()
    if db.table_exists('server'):
        raise IntegrityError('Database already exist')
    db.create_tables([Server, Mutator, GameType, GameTypeMutator, Game, Player, Stat, StatName,
                      PlayerXp, PlayerAward, GameXp])
    import default_data
    default_data.fill()
    print("Database initialized")


def create_data():
    stats = [
        (0, 'MEDIC_XP', StatType.XP.value )
    ]


if __name__ == "__main__":
    cmd = None
    parser = argparse.ArgumentParser(prog='ScrN SQL Server', description='ScrN SQL Server.')
    parser.add_argument('--version', action='version', version='%(prog)s '+VERSION)
    parser.add_argument('command', choices=['server', 'init', 'import'],
                        help='a command to perform')

    args = parser.parse_args()

    if args.command == 'init':
        init()

