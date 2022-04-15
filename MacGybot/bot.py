# Used to store your token in a .env file
from dotenv import load_dotenv
import os
# init file
import __init__
# discord.py libs
import hikari
import lightbulb

#TODO: commande de gestion du serveur (avec création de rôles et channel auto)
#TODO: commande de gestion d'emploi du temps (prise de rdv, consultation du planning de la journée/semaine/mois)
# +gestion des salles avec une base de données
#TODO: commande de partage de Note (en lien avec l'appli ez_notes) => permet de généré une image (ou pdf) qui serait un rendu MarkDown
#TODO: commande pour faire des sondages
#TODO: commande pour faire de la communication (avec un embed, etc)

## Retrieving TOKEN ##
load_dotenv()
token = os.getenv("TOKEN")

def create_bot():
    bot = lightbulb.BotApp(
        token=token,
        prefix="$",
        case_insensitive_prefix_commands=True,
        intents=hikari.Intents.ALL,
        default_enabled_guilds=__init__.GUILD_ID,
    )
    ## Loading extensions ##
    bot.load_extensions_from("./commands/")
    
    return bot

import sqlite3
async def schedule_events():
    connection = connection = sqlite3.connect("assets/db/calendar.db")
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM events JOIN u_to_e ON events.id = u_to_e.event_id JOIN users ON users.uid = u_to_e.uid
        WHERE users.name = 'ippei'""")
    #SELECT events.name, events.desc, events.date, events.time, events.server_id FROM events JOIN u_to_e ON events.id = u_to_e.event_id JOIN users ON users.uid = u_to_e.uid
    #WHERE users.name = 'ippei';
    result = cursor.fetchall()
    print(result)


if __name__ == "__main__":
    if os.name != "nt":
        # uvloop is only available on UNIX systems, but instead of
        # coding for the OS, we include this if statement to make life
        # easier.
        import uvloop

        uvloop.install()
    
    # Create and run the bot.
    bot = create_bot()
    bot.cre
    bot.run()
