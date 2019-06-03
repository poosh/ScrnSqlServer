from db.model import *

stats = [
    (0, 'medic_xp', StatType.XP.value),
    (1, 'support_xp', StatType.XP.value),
    (2, 'sharp_xp', StatType.XP.value),
    (3, 'commando_xp', StatType.XP.value),
    (4, 'berserk_xp', StatType.XP.value),
    (5, 'firebug_xp', StatType.XP.value),
    (6, 'demo_xp', StatType.XP.value),
    # 7 is off perk, i.e., no XP
    (8, 'gunslinger_xp', StatType.XP.value),
    # 9 is Combat Medic - uses the same XP as medic
    (10, 'hmg_xp', StatType.XP.value),
    (11, 'htec_xp', StatType.XP.value),
    (21, 'weld', StatType.XP.value),
    (23, 'stalkers', StatType.XP.value),
    (28, 'pistol_dmg', StatType.XP.value),
    (30, 'kills', StatType.XP.value),
    (31, 'deaths', StatType.XP.value),
    (32, 'headshots', StatType.XP.value),
    (33, 'wins', StatType.XP.value),
    (34, 'defeats', StatType.XP.value),
    (35, 'playtime', StatType.XP.value),
    (36, 'zedtime', StatType.XP.value),
    (37, 'cashgiven', StatType.XP.value),

    (1000, 'Ach', StatType.AWARD.value),
    (1001, 'AchMaps', StatType.AWARD.value),
    (1002, 'AchObjMaps', StatType.AWARD.value),
    (1003, 'D3Ach', StatType.AWARD.value),
    (1004, 'SWPAch', StatType.AWARD.value),
    (1005, 'FreezeAch', StatType.AWARD.value),
]

stat_names = [
    ('DamageHealedStat', 0),
    ('WeldingPointsStat', 21),
    ('ShotgunDamageStat', 1),
    ('HeadshotKillsStat', 2),
    ('StalkerKillsStat', 23),
    ('BullpupDamageStat', 3),
    ('MeleeDamageStat', 4),
    ('FlameThrowerDamageStat', 5),
    ('CashDonatedStat', 37),
    ('TotalZedTimeStat', 36),
    ('KillsStat', 30),
    ('ExplosivesDamageStat', 6),
    ('TotalPlayTime', 35),
    ('WinsCount', 33),
    ('LostsCount', 34),
    ('ScrnPistolKillProgress', 8),
    ('ScrnPistolDamageProgress', 28),
    ('BruteGunnerPerkProg', 10),
    ('HTecProg', 11),
]


def fill():
    Stat.insert_many(stats, fields=[Stat.id, Stat.name, Stat.type]).execute()
    StatName.insert_many(stat_names, fields=[StatName.name, StatName.stat]).execute()