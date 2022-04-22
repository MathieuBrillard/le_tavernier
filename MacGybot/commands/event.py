# time and background tasks
import asyncio
import datetime
# sqlite lib
import sqlite3
# discord libs
import hikari
import lightbulb
from lightbulb import commands

# The options the command will have.
@lightbulb.option("due_date", "The due date of the event (like 13-01-2022).",
    str, required=True)
@lightbulb.option("due_time", "The due time of the event (like 08:00).", str,
    required=True)
@lightbulb.option("name", "The name of the event.", str, required=True)
@lightbulb.option("description", "The description of the event.", str,
    required=False)
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
    connection.close()
    ## send response ##
    #TODO: respond with a reaction ?
    resp = await ctx.respond(content="event created.")
    msg = await resp.message()
    ## create task in the bot ##
    event = ctx.bot.create_task(schedule_event(ctx.bot, name, desc, due_date,
        due_time, serv_id, event_id, uid))
    await event


async def schedule_event(bot, name, desc, due_date, due_time, serv_id,
    event_id, uid):
    ## calculate the time to wait ##
    to_wait = datetime_diff(due_date, due_time)
    ## generate embed response ##
    guild = await bot.rest.fetch_guild(int(serv_id))
    embed = (
        hikari.Embed(
            title=f"Your event **`{name}`** from server **`{guild}`**\n" + \
                "is now starting !",
            description=f"{desc}",
            colour=hikari.Colour(0x563275),
            # Doing it like this is important.
            timestamp=datetime.datetime.now().astimezone(),
        )
        .set_author(name="Reminder")
    )
    ## wait the time needed before sending the event message ##
    await asyncio.sleep(to_wait)
    ## send event message ##
    channel = await bot.rest.create_dm_channel(int(uid))
    msg = await bot.rest.create_message(channel=channel,embed=embed)
    ## delete event in database ##
    # create db connection
    connection = sqlite3.connect("assets/db/calendar.db")
    # create cursor to send commands
    cursor = connection.cursor()
    # delete rows in tables
    cursor.execute("""
        DELETE FROM "u_to_e" WHERE uid=(?) AND event_id=(?);""",
        (uid, event_id,))
    cursor.execute("""
        DELETE FROM "events" WHERE id=(?);""",
        (event_id,))
    # save changes
    connection.commit()
    connection.close()


def datetime_diff(due_date: str, due_time: str) -> float:
    """This function is used to calculate the difference in seconds between
    the current date and the due_date + due_time.

    - Args:
        `due_date`(str): date like 14-01-2022
        `due_time`(str): time like 16:20

    - Returns:
        `float`: The total of seconds between the dates.
    """
    now = datetime.datetime.now()
    due_date = due_date.split("-")
    due_time = due_time.split(":")
    future_date = datetime.datetime(int(due_date[2]), int(due_date[1]),
        int(due_date[0]), int(due_time[0]), int(due_time[1]))
    
    diff = future_date - now
    return diff.total_seconds()


async def schedule_events(bot) -> None:
    """Function to schedule every events in the database, using the function
    `schedule_event`.
    
    - Args:
        `bot`(lightbulb.BotApp): The bot application.
    
    - Returns:
        `None`.
    """
    ## retrieve events ##
    connection = connection = sqlite3.connect("assets/db/calendar.db")
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM u_to_e;""")
    datas = cursor.fetchall()
    cursor.execute("""SELECT * FROM events;""")
    events = cursor.fetchall()
    connection.close()
    ## schedule events ##
    tasks = []
    for event in events:
        for data in datas:
            if data[1] == event[0]:
                uid = data[0]
        task = bot.create_task(schedule_event(bot, event[1], event[2], event[3],
            event[4], event[5], event[0], uid))
        tasks += [task]
    print("pending events scheduled.")
    for tsk in tasks:
        await tsk


def load(bot: lightbulb.BotApp) -> None:
    bot.command(event)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_command(bot.get_slash_command("event"))