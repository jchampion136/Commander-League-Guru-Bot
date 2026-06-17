import sqlite3

DB_PATH = "database/league.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

    
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leagues (
            league_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id TEXT NOT NULL,
            name TEXT NOT NULL,
            format TEXT NOT NULL,
            scoring TEXT NOT NULL,
            bracket INTEGER NOT NULL,
            active INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_id TEXT NOT NULL UNIQUE,
            discord_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS league_players (
            league_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            active INTEGER DEFAULT 1,
            
            commander TEXT,
            partner_name TEXT,
            team_name TEXT,
            

            points INTEGER DEFAULT 0,
            firsts INTEGER DEFAULT 0,
            seconds INTEGER DEFAULT 0,
            thirds INTEGER DEFAULT 0,
            fourths INTEGER DEFAULT 0,
            no_shows INTEGER DEFAULT 0,

            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            eliminated INTEGER DEFAULT 0,

            PRIMARY KEY (league_id, player_id),
            FOREIGN KEY (league_id) REFERENCES leagues(league_id),
            FOREIGN KEY (player_id) REFERENCES players(player_id)
        )
    """)

    conn.commit()
    conn.close()
    
def create_league(guild_id, name, format, scoring, bracket):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE leagues SET active = 0 WHERE guild_id = ?",
        (guild_id,)
    )

    cursor.execute("""
        INSERT INTO leagues (guild_id, name, format, scoring, bracket, active)
        VALUES (?, ?, ?, ?, ?, 1)
    """, (guild_id, name, format, scoring, bracket))

    conn.commit()
    conn.close()

def get_active_league(guild_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT league_id, name, format, scoring, bracket
        FROM leagues
        WHERE guild_id = ? AND active = 1
    """, (guild_id,))

    league = cursor.fetchone()

    conn.close()
    return league