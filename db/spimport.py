import logging as log
import os
import re
from collections import namedtuple

from db.model import *
from db.control import *


re_custom_stat_pattern = re.compile('\\(N=\\"(\\w+)\\",V=\\"(\\w+)\\"\\)')


def ftp_player_import(c_game, player_id, stats_str):
    log.info('Loading Player %d', player_id)
    recs = stats_str.split(',', 26)

    perk = recs[0].split(':', 1)  # <perk_name>[:<perk_index>]
    player_defaults = {
        'perk_name': perk[0],
        'perk_index': perk[1] if len(perk) >= 2 else None,
        'model': recs[25].strip("'"),
    }

    with db.atomic():
        c_player = c_game.new_player(player_id, defaults=player_defaults)

        # make fields human-readable
        stats = {
            'DamageHealedStat': int(recs[1]) if recs[1] else 0,
            'WeldingPointsStat': int(recs[2]) if recs[2] else 0,
            'ShotgunDamageStat': int(recs[3]) if recs[3] else 0,
            'HeadshotKillsStat': int(recs[4]) if recs[4] else 0,
            'StalkerKillsStat': int(recs[5]) if recs[5] else 0,
            'BullpupDamageStat': int(recs[6]) if recs[6] else 0,
            'MeleeDamageStat': int(recs[7]) if recs[7] else 0,
            'FlameThrowerDamageStat': int(recs[8]) if recs[8] else 0,
            # 'SelfHealsStat': int(recs[9]) if recs[9] else 0,
            # 'SoleSurvivorWavesStat': int(recs[10]) if recs[10] else 0,
            'CashDonatedStat': int(recs[11]) if recs[11] else 0,
            # 'FeedingKillsStat': int(recs[12]) if recs[12] else 0,
            # 'BurningCrossbowKillsStat': int(recs[13]) if recs[13] else 0,
            # 'GibbedFleshpoundsStat': int(recs[14]) if recs[14] else 0,
            # 'StalkersKilledWithExplosivesStat': int(recs[15]) if recs[15] else 0,
            # 'GibbedEnemiesStat': int(recs[16]) if recs[16] else 0,
            # 'BloatKillsStat': int(recs[17]) if recs[17] else 0,
            # 'SirenKillsStat': int(recs[18]) if recs[18] else 0,
            'TotalZedTimeStat': int(recs[21]) if recs[21] else 0,
            'KillsStat': int(recs[19]) if recs[19] else 0,
            'ExplosivesDamageStat': int(recs[20]) if recs[20] else 0,
            'TotalPlayTime': int(recs[22]) if recs[22] else 0,
            'WinsCount': int(recs[23]) if recs[23] else 0,
            'LostsCount': int(recs[24]) if recs[24] else 0,
        }
        awards = { }

        m = re_custom_stat_pattern.findall(recs[26])
        for N, V in m:
            try:
                stat = c_stats.by_name(N)
                if stat.type == StatType.XP.value:
                    stats[N] = V
                else:
                    awards[N] = V
            except KeyError:
                log.warning('Unknown stat: ' + N)

        for k, v in stats.items():
            c_player.add_xp(k, v)

        for k, v in awards.items():
            c_player.set_award(k, v)



ImportResult = namedtuple('ImportResult', ['total', 'imported', 'game_id'], defaults=(0, 0, 0))


def ftp_import(stat_dir_path, server_name="SP_IMPORT"):
    """
    Imports stats from ServerPerks FTB database. FTP connection is not supported.
    FTP directory must be downloaded
    :param server_name Server name to use for import. Must exist in the db
    :param stat_path Path to stats local directory (where stat files from FTP downloaded to)
    :return game id or 0 if import failed
    """
    dir = os.fsencode(stat_dir_path);
    if not os.path.isdir(dir):
        log.error('Directory ' + stat_dir_path + ' does not exist')
        return None

    result = ImportResult()

    with db.atomic():
        c_server = join_server(server_name)
        c_game = c_server.new_game()
        result.game_id = c_game.model.get_id()
        for file in os.listdir(dir):
            result.total += 1
            file_ext = os.path.splitext(file)
            if file_ext[1] != '.txt':
                log.warning('Unknown file: ' + file)
                continue
            try:
                player_id = int(file_ext[0])
            except ValueError:
                log.warning('Bad player id: ' + file_ext[0])
                continue

            try:
                with open(os.path.join(stat_dir_path, file), 'r') as f:
                    stats_str = f.read()
            except:
                log.warning('Unable to read file: ' + file)
                continue

            try:
                ftp_player_import(c_game, player_id, stats_str)
                result.imported += 1
            except:
                log.warning('Failed to import player ' + str(player_id))

    return result

