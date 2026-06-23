import os
import discord
from discord import app_commands
from database import init_db, create_league, get_active_league, get_point_standings, get_leagues_for_guild, get_league_by_id, get_final_podium, update_bracket_img, get_bracket_img
from dotenv import load_dotenv
from database import signup_player

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

#Helper function to show League options contained in the database for autocomplete
async def league_autocomplete(interaction: discord.Interaction, current: str):
    guild_id = str(interaction.guild.id)
    leagues = get_leagues_for_guild(guild_id)
    
    return [
        app_commands.Choice(
            name=f"{league_id} - {name}",
            value=str(league_id)
        )
        for league_id, name in leagues
        if current.lower() in name.lower() ][:25]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    message = (
        "**Commander League Guru Commands**\n\n"
        "/help - Show this menu\n"
        "/signup - Sign up for the current league\n"
        "/update_bracket - Admin only: update bracket URL for a league\n"
        "/standings - View current standings\n"
        "/setup_league - Admin only: Sets up the current league\n"
        "/addpoints - Admin only (points leagues only)\n"
    )

    await interaction.response.send_message(message)


#Allow admins to set up league for the month
@bot.tree.command(name="setup_league", description="Admin only: set up the current league")
@app_commands.choices(
    format=[
        app_commands.Choice(name="Traditional", value="traditional"),
        app_commands.Choice(name="Two-Headed Giant", value="two_headed_giant"),
        app_commands.Choice(name="Pauper", value="pauper")
    ],
    scoring=[
        app_commands.Choice(name="Points League", value="points"),
        app_commands.Choice(name="Bracket League", value="bracket")
    ],
    bracket=[
        app_commands.Choice(name="Bracket 1", value=1),
        app_commands.Choice(name="Bracket 2", value=2),
        app_commands.Choice(name="Bracket 3", value=3),
        app_commands.Choice(name="Bracket 4", value=4),
        app_commands.Choice(name="Bracket 5", value=5)
    ]
)
async def setup_league(interaction: discord.Interaction, name: str, format: app_commands.Choice[str], scoring: app_commands.Choice[str],bracket: app_commands.Choice[int]):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("you do not have permission to use this command",ephemeral= True)
        return 
    
    guild_id = str(interaction.guild.id) #Creates a unique identifier for server
    create_league(guild_id, name, format.value, scoring.value, bracket.value)
    
    league = get_active_league(guild_id)
    
    league_id, league_name, league_format, league_scoring, league_bracket = league

    await interaction.response.send_message(
        f"League Setup Confirmation:\n"
        f"League ID: {league_id}\n"
        f"Name: {league_name}\n"
        f"Format: {league_format}\n"
        f"Scoring: {league_scoring}\n"
        f"Bracket: {league_bracket}"
    )
    

@bot.tree.command(name="signup", description=f"Sign up for our current league")
async def signup(interaction: discord.Interaction, commander: str = None, teammate: str = None, team_name: str = None):
    
    guild_id = str(interaction.guild.id)
    league = get_active_league(guild_id)

    if league is None:
        await interaction.response.send_message(
            "No active league found. Ask an admin to set one up first.",
            ephemeral=True
        )
        return

    league_id, league_name, league_format, scoring, bracket = league

    discord_id = str(interaction.user.id)
    discord_name = interaction.user.display_name

    success = signup_player(
        league_id,
        discord_id,
        discord_name,
        commander,
        teammate,
        team_name
    )

    if not success:
        await interaction.response.send_message(
            f"You are already signed up for **{league_name}**.",
            ephemeral=True
        )
        return

    message = f"✅ **{discord_name}** signed up for **{league_name}**!"

    if commander:
        message += f"\nCommander: {commander}"

    if teammate:
        message += f"\nRequested Teammate: {teammate}"

    await interaction.response.send_message(message)

@bot.tree.command(name="update_bracket", description="Admin only: update bracket image for a league")
@app_commands.autocomplete(league=league_autocomplete)
async def update_bracket(interaction: discord.Interaction, league: str, image: discord.Attachment):
    
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.",ephemeral=True)
        return
    
    selected_league = get_league_by_id(int(league))
    
    if selected_league is None:
        await interaction.response.send_message("League not found. Please check the league ID and try again.",ephemeral=True)
        return
    
    league_id, league_name, league_format, scoring, bracket = selected_league
    
    if scoring != "bracket":
        await interaction.response.send_message(f"Url cannot be updated since **{league_name}** is not a bracket-based league.",ephemeral=True)
        return
    
    if not image.content_type.startswith("image/"):
        await interaction.response.send_message("Please upload a valid image file.",ephemeral=True)
        return
    
    update_bracket_img(league_id, image.url)
    
    await interaction.response.send_message(f"Bracket image for **{league_name}** has been updated.")
    
            
@bot.tree.command(name="standings", description="Show league standings")
@app_commands.autocomplete(league=league_autocomplete)
async def standings(interaction: discord.Interaction, league: str):
    guild_id = str(interaction.guild.id)
    
    if league:
        selected_league = get_league_by_id(int(league))
        
    else:
        selected_league = get_active_league(guild_id)
        
    if selected_league is None:
        await interaction.response.send_message("No active league found. Ask your administrator for assistance.",ephemeral=True)
        return
    
    league_id, league_name, league_format, scoring, bracket = selected_league
    
    if scoring == "bracket":
        bracket_img = get_bracket_img(league_id)
        
        if bracket_img is None:
            await interaction.response.send_message(f"No bracket found for **{league_name}**. Check back later.")
            return
        
        embed = discord.Embed(title=f"🏆 {league_name} Bracket 🏆")
        embed.set_image(url=bracket_img)
        
        await interaction.response.send_message(embed=embed)
        return
    
    if scoring == "points":
        
        standings = get_point_standings(league_id)
        
        if not standings:
            await interaction.response.send_message(f"No standings found for **{league_name}**. Check back later.")
            return
        
        
        message = f"🏆 **{league_name} Standings** 🏆\n"
        message += f"*Format: {league_format} | Bracket {bracket} | Scoring: {scoring}*\n\n"

        podium = get_final_podium(league_id)

        if podium:
            message += "**Final Podium:**\n"

        medals = {
            1: "🥇",
            2: "🥈",
            3: "🥉"
        }

        grouped = {}

        for name, final_place in podium:
            grouped.setdefault(final_place, []).append(name)

        for place in sorted(grouped):
            names = " / ".join(grouped[place])
            message += f"{medals[place]} **{names}**\n"

        message += "\n"
            
        #Print full leaderboard
        message += "\n**Full Leaderboard:**\n"

        for index, player in enumerate(standings, start=1):
            name, commander, points, firsts, seconds, thirds, fourths, no_shows = player

            message += ( #Prtints name, total points, commander, and number of 1st, second, thirds, fourths, and no shows
                f"{index}. **{name}** — {points} pts — {commander} "
                f"(🥇 {firsts}  🥈 {seconds}    🥉 {thirds}     4️⃣ {fourths}     ❌ {no_shows})\n")

    await interaction.response.send_message(message)

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
    
    

   