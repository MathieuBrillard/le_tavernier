# Used to store your token in a .env file
from dotenv import load_dotenv
import os
# init file
import __init__
# discord.py libs
import hikari
import lightbulb
import asyncio

#TODO: commande de gestion du serveur (avec création de rôles et channel auto)
#TODO: commande pour faire des sondages
#TODO: commande pour faire de la communication (avec un embed, etc)

## Retrieving TOKEN ##
load_dotenv()
token = os.getenv("TOKEN")
## Create the bot ##
bot = lightbulb.BotApp(
    token=token,
    prefix="$",
    case_insensitive_prefix_commands=True,
    intents=hikari.Intents.ALL,
    default_enabled_guilds=__init__.GUILD_ID,
)
## Loading extensions ##
bot.load_extensions_from("./commands/")


#TODO / FIX-ME: bot not stopping with ctrl+c if there is pending event(s)
# you have to kill the shell
@bot.listen(hikari.StartedEvent)
async def on_starting(_: hikari.StartedEvent) -> None:
    # This event fires once, while the BotApp is starting.
    from commands.event import schedule_events
    print("scheduling events...")
    await schedule_events(bot)


if __name__ == "__main__":
    if os.name != "nt":
        # uvloop is only available on UNIX systems, but instead of
        # coding for the OS, we include this if statement to make life
        # easier.
        import uvloop

        uvloop.install()
    
    # run the bot.
    bot.run()
