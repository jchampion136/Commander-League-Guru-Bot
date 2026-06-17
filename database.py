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

def get_point_standings(league_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
    """SELECT
            p.discord_name,
            lp.commander,
            lp.points,
            lp.firsts,
            lp.seconds,
            lp.thirds,
            lp.fourths,
            lp.no_shows
        FROM league_players lp
        JOIN players p ON lp.player_id = p.player_id
        WHERE lp.league_id = ?
        ORDER BY
            lp.points DESC,
            lp.firsts DESC,
            lp.seconds DESC,
            lp.thirds DESC,
            lp.fourths DESC
    """, (league_id,))
    
    standings = cursor.fetchall()
    conn.close()
    
    return standings 

def get_final_podium(league_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.discord_name, lp.final_place
        FROM league_players lp
        JOIN players p ON lp.player_id = p.player_id
        WHERE lp.league_id = ?
        AND lp.final_place IS NOT NULL
        ORDER BY lp.final_place ASC
    """, (league_id,))
    
    podium = cursor.fetchall()
    conn.close()
    return podium

def get_leagues_for_guild(guild_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT league_id, name
        FROM leagues
        WHERE guild_id = ?
        ORDER BY league_id DESC
    """, (guild_id,))

    leagues = cursor.fetchall()
    conn.close()
    return leagues

def get_league_by_id(league_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT league_id, name, format, scoring, bracket
        FROM leagues
        WHERE league_id = ?
    """, (league_id,))

    league = cursor.fetchone()
    conn.close()
    return league
