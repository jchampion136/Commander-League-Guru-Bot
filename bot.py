import os
import discord
from discord import app_commands
from database import init_db
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

class LeagueBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents = intents) #Initializes Discord
        self.tree = app_commands.CommandTree(self) #initializes all commands we will create later s
    
    async def setup_hook(self):
        await self.tree.sync()

bot = LeagueBot()

#Empty Dictionary
players = {}

current_league = { #Default League Settings
    "name": "Current League",
    "format": "Unknown Format",
    "scoring": "points"
}


# Helper Functions to set up players based on game format
def create_player_record(username):

    player = {
        "discord_name": username,
        "active": True
    }

    if current_league["scoring"] == "points":
        player["points"] = 0
        player["firsts"] = 0
        player["seconds"] = 0
        player["thirds"] = 0
        player["fourths"] = 0
        player["no_shows"] = 0

    elif current_league["scoring"] == "bracket":
        player["wins"] = 0
        player["losses"] = 0
        player["eliminated"] = False

    return player

def get_points_standings():
    return sorted(
        players.items(),
        key=lambda item: (
            item[1]["points"],
            item[1]["firsts"],
            item[1]["seconds"],
            item[1]["thirds"],
            item[1]["fourths"]
        ),
        reverse=True
    )

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    message = (
        "**Commander League Guru Commands**\n\n"
        "/help - Show this menu\n"
        "/signup - Sign up for the current league\n"
        "/standings - View current standings\n"
        "/setup_league - Admin only\n"
        "/addpoints - Admin only (points leagues only)\n"
    )

    await interaction.response.send_message(message)


#Allow admins to set up league for the month
@bot.tree.command(name="setup_league", description="Admin only: set up the current league")
async def setup_league(interaction: discord.Interaction, name: str, format: str, scoring: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("you do not have permission to use this command",ephemeral= True)
        return 
    
    current_league["name"] = name
    current_league["format"] = format
    current_league["scoring"] = scoring.lower()
    
    await interaction.response.send_message(
        f"League Setup Confirmation:\n"
        f"Name: {name}\n"
        f"Format: {format}\n"
        f"Scoring: {current_league['scoring']}"
    )
    

@bot.tree.command(name="signup", description=f"Sign up for {current_league['name']}")
async def signup(interaction: discord.Interaction): #Leave out commander for now. May alter later
    username = interaction.user.name
    
    if username in players:
        await interaction.response.send_message(f"{username}, you are already signed up!")
        return 
    
    players[username] = create_player_record(username)
    
    await interaction.response.send_message(
        f"Thank you {username}. You are signed up for **{current_league['name']}** "
        f"({current_league['format']})!"
    )

@bot.tree.command(name="standings", description="Show league standings")
async def standing(interaction: discord.Interaction):
    if current_league["scoring"] == "bracket":
        #TODO Will complete later
        await interaction.response.send_message("Bracket standings are not implemented yet. Check back later")
        return
    
    if current_league["scoring"] == "points":
        if not players:
            await interaction.response.send_message("No players have signed up yet.")
            return
        
        sorted_players = get_points_standings()
        
        message = f"**{current_league['name']} Standings**\n"
        message += f"*Format: {current_league['format']}*\n\n"

        for index, (name, data) in enumerate(sorted_players, start=1):
            message += (
                f"{index}. {name} — "
                f"{data['points']} pts "
                f"({data['firsts']} 1st, "
                f"{data['seconds']} 2nd, "
                f"{data['thirds']} 3rd, "
                f"{data['fourths']} 4th)\n"
            )
        
        await interaction.response.send_message(message)
        return
    
    await interaction.response.send_message("Unknown scoring type: Please consult an admin to run '/setup_league' .")

@bot.tree.command(name="addpoints", description="Add points to a player")
async def addpoints(interaction: discord.Interaction, player: str, points: int):
    if current_league["scoring"] != "points":
        await interaction.response.send_message( "Current league is not using a points-based scoring system.",ephemeral=True)
        return
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command", ephemeral=True)
        return
    
    if player not in players:
        await interaction.response.send_message("Player not found.")
        return

    players[player]["points"] += points
    
    await interaction.response.send_message(
        f"Added {points} points to {player}."
    )

init_db()
bot.run(TOKEN)
    
    

   