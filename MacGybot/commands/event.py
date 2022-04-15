import os
import sqlite3
import hikari
import lightbulb
from lightbulb import commands

# The options the command will have.
@lightbulb.option("due_date", "The due date of the event (like 01-01-2022).", str, required=True)
@lightbulb.option("due_time", "The due time of the event (like 08:00).", str, required=True)
@lightbulb.option("name", "The name of the event.", str, required=True)
@lightbulb.option("description", "The description of the event.", str, required=False)
# Convert the function into a command
@lightbulb.command("event", "Schedule an event.")
# Define the types of command that this function will implement
@lightbulb.implements(commands.PrefixCommand, commands.SlashCommand)
async def event(ctx: lightbulb.context.Context) -> None:
    # retrieve args
    due_date = ctx.options._options["due_date"]
    due_time = ctx.options._options["due_time"]
    name = ctx.options._options["name"]
    desc = ctx.options._options["description"]
    # retrieve user and server info
    uid = str(ctx.author.id)
    uname = ctx.author.username
    serv_id = str(ctx.guild_id)
    # create db connection
    connection = sqlite3.connect("assets/db/calendar.db")
    # create cursor to send commands
    cursor = connection.cursor()
    # check if user already exist
    cursor.execute("SELECT uid FROM users WHERE uid = (?)", (uid,))
    result = cursor.fetchall()
    if result:
        pass
    else:
        cursor.execute("""INSERT INTO "users" (uid, name) VALUES (?, ?)""",
            (uid, uname,))
    #TODO: check if the date and time format are correct
    result = cursor.execute("""INSERT INTO "events" (name, desc, date, time,
        server_id) VALUES (?, ?, ?, ?, ?)""", (name, desc, due_date, due_time,
        serv_id,))
    event_id = result.lastrowid
    cursor.execute("""INSERT INTO "u_to_e" (uid, event_id) VALUES (?, ?)""",
        (uid, event_id,))
    # to save the changes in the db
    connection.commit()
    ## send response ##
    resp = await ctx.respond(content="event created.")
    msg = await resp.message()


def load(bot: lightbulb.BotApp) -> None:
    bot.command(event)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_command(bot.get_slash_command("event"))