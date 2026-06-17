import sqlite3

DB_PATH = "../database/league.db"
LEAGUE_ID = 1 #Season 1

season_1_players = [
    ("temerairehawke", "Hawke", "Miirym, Sentinel Wyrm", 17, 3, 1, 0, 1, 0, 1),
    ("m86892", "Jacob", "Pearl-Ear, Imperial Advisor", 16, 3, 1, 0, 1, 0, 3),
    ("thedarknessjacky", "Jackson", "Lorehold, The Historian", 15, 2, 1, 2, 0, 0, 3),
    ("thefakeryan24", "Ryan S.", "Olivia, Opulent Outlaw", 14, 2, 1, 1, 1, 0,2),
    ("daruma462", "Dillon", "Gaddock Teeg", 14, 1, 3, 0, 1, 0, None),
    ("afteraffekt", "Travis", "Blech, Loafing Pest", 14, 1, 2, 2, 0, 0, None),
    ("flatulentbear", "Silas", "Gev, Scaled Scorch", 13, 0, 3, 2, 0, 0, None),
    ("noob_lord_973", "Mason", "Arcades, The Strategist", 11, 1, 2, 0, 1, 1, None),
    ("forgekandrix", "Karl", "Karlach, Fury of Avernus / Hardy Outlander", 10, 1, 1, 1, 1, 1, None),
    ("chopperslice1214", "Cameron", "Kratos, Stoic Father / Atreus, Impulsive Son", 10, 0, 2, 2, 0, 1, None),
    ("zombeasypeasy", "Jamie", "Captain America, First Avenger", 9, 1, 1, 1, 0, 2, None),
    ("pxgolden", "Robbie", "The 9th Doctor / Clara Oswald", 7, 0, 1, 1, 2, 1, None),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

for discord_id, name, commander, points, firsts, seconds, thirds, fourths, no_shows, final_place in season_1_players:
    cursor.execute("""
        INSERT OR IGNORE INTO players (discord_id, discord_name)
        VALUES (?, ?)
    """, (discord_id, name))

    cursor.execute("""
        SELECT player_id
        FROM players
        WHERE discord_id = ?
    """, (discord_id,))

    player_id = cursor.fetchone()[0]

    cursor.execute("""
        INSERT OR REPLACE INTO league_players (
            league_id,
            player_id,
            commander,
            points,
            firsts,
            seconds,
            thirds,
            fourths,
            no_shows,
            final_place,
            active
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
    """, (
        LEAGUE_ID,
        player_id,
        commander,
        points,
        firsts,
        seconds,
        thirds,
        fourths,
        no_shows,
        final_place
    ))
    
conn.commit()
conn.close()
    
print("Season 1 standings seeded successfully") #Successful Message