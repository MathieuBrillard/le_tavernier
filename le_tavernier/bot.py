# Used to store your token in a .env file
from dotenv import load_dotenv
import os
# init file
import __init__
# discord.py libs
import hikari
import lightbulb
# async task
import asyncio


## Retrieving TOKEN ##
load_dotenv()

class Tavernier:
    def __init__(self):
        self.token = os.getenv("TOKEN")
        self.prefix = ">"
        self.enabled_guilds = __init__.GUILD_ID
        self.extensions = ["./commands/"]
        # self.loop = asyncio.run_coroutine_threadsafe
        self.running = False
    
    def create_bot(self):
        self.bot = lightbulb.BotApp(
            token=self.token,
            prefix=self.prefix,
            case_insensitive_prefix_commands=True,
            intents=hikari.Intents.ALL,
            default_enabled_guilds=self.enabled_guilds,
        )

    def load_extensions(self):
        for ext in self.extensions:
            self.bot.load_extensions_from(ext)

    def reload_extensions(self, extension=None):
        if extension == None:
            for ext in self.extensions:
                self.bot.reload_extensions(ext)
        else:
            self.bot.reload_extensions(extension)

    def run(self):
        self.running = True
        self.bot.run()

    def shutdown(self):
        self.running = False
        self.bot.close()


def retrieve_commands() -> list[str]:
    """ Function used to retrieve all the commands of the Tavernier class.

    Returns:
        list[str]: list of the commands.
    """
    cmd_dict = Tavernier.__dict__
    cmd_dict = cmd_dict.keys()
    cmd_list = []
    for cmd in cmd_dict:
        if cmd.startswith("__"):
            pass
        else:
            cmd_list += [cmd]
    return cmd_list


def command_handler(bot: Tavernier, command: str):
    # retrieve the commands of the class
    cmd_list = retrieve_commands()
    if command not in cmd_list:
        print("Invalid command.")
        return
    else:
        method = getattr(bot, command)
        print(f"Executing {command} ...")
        method()
        print("Done !")


async def running_loop():
    while tavernier.running:
        user_input = input()
        command_handler(tavernier.bot, user_input)


if __name__ == "__main__":
    if os.name != "nt":
        # uvloop is only available on UNIX systems, but instead of
        # coding for the OS, we include this if statement to make life
        # easier.
        import uvloop

        uvloop.install()
    
    # Create the bot.
    tavernier = Tavernier()
    tavernier.create_bot()
    tavernier.load_extensions()
    
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(running_loop())
    asyncio.ensure_future(tavernier.run())
    loop.run_forever()
