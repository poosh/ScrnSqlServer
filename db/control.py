import logging as log

from peewee import IntegrityError

from db.model import *


class Controller:
    def __init__(self, model):
        self.model = model


class ServerCtrl(Controller):
    def __init__(self, model):
        super(ServerCtrl, self).__init__(model)
        self.game = None

    def new_game(self):
        if self.game and not self.game.ended:
            log.warning('Previous game is not ended. Ending it now.')
            self.game.end_game()

        m_game = Game.create(server=self.model)
        self.game = GameCtrl(m_game)
        return self.game


class GameCtrl(Controller):
    def __init__(self, model):
        super(GameCtrl, self).__init__(model)
        self.ended = False
        self.players = []

    def end_game(self, end_code=EndGameCode.UNKNOWN):
        if self.ended:
            pass
        self.model.end_time = datetime.now()
        self.model.end_code = end_code.value
        self.model.save()
        self.ended = True

    def player(self, player_id, **kwargs):
        for c_player in self.players:
            if c_player.model.id == player_id:
                return c_player

        c_player = self.new_player(player_id, **kwargs)
        self.players.append(c_player)
        return c_player

    def new_player(self, player_id, **kwargs):
        m_player, created = Player.get_or_create(id=player_id, **kwargs)
        c_player = PlayerCtrl(m_player, self)
        c_player.new_player = created
        return c_player


class PlayerCtrl(Controller):
    def __init__(self, model, c_game):
        super(PlayerCtrl, self).__init__(model)
        self.c_game = c_game
        self.new_player = None
        self.stats = []

    def add_xp(self, stat_name, xp):
        stat = c_stats.by_name(stat_name)
        try:
            GameXp.create(game=self.c_game.model, player=self.model, stat=stat.id, xp=xp)
        except IntegrityError:
            xp_rec = GameXp.get(game=self.c_game.model, player=self.model, stat=stat.id)
            xp_rec.xp += xp
            xp_rec.save()
        try:
            PlayerXp.create(player=self.model, stat=stat.id, xp=xp)
        except IntegrityError:
            xp_rec = PlayerXp.get(player=self.model, stat=stat.id)
            xp_rec.xp += xp
            xp_rec.save()

    def set_award(self, stat_name, value):
        stat = c_stats.by_name(stat_name)
        PlayerAward.replace(player=self.model, stat=stat.id, value=value).execute()


class StatsCtrl(Controller):
    def __init__(self):
        super().__init__(None)
        self.stats = []
        self._name_index = {}  # name-to-row-index table

    def load(self):
        self.stats = [row for row in Stat.select(Stat.id, Stat.name, Stat.type).order_by(Stat.id).namedtuples()]
        self._name_index.clear()
        i = 0
        for stat in self.stats:
            self._name_index[stat.name.casefold()] = i
            i += 1
        for (row_name, stat_id) in StatName.select(StatName.name, StatName.stat).order_by(StatName.name).tuples():
            self._name_index[row_name.casefold()] = self.stats.index(self.by_id(stat_id))

    def by_id(self, stat_id):
        return next(x for x in self.stats if x.id == stat_id)

    def by_name(self, stat_name):
        s = stat_name.casefold()
        return self.stats[self._name_index[s]]


c_stats = StatsCtrl()


def join_server(server_name):
    m_server = Server.get(Server.name == server_name)
    if not m_server:
        raise ValueError('Server not found: "' + server_name + '"')
    c_server = ServerCtrl(m_server)
    return c_server


