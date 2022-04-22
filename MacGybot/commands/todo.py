# sqlite lib
import sqlite3
# discord libs
import hikari
import lightbulb
from lightbulb import commands

# The options the command will have.
@lightbulb.option("date", """The date you want to retrieve events from
    (like 13-01-2022).""", str, required=True)
# Convert the function into a command
@lightbulb.command("todo", "Print events from the specified day.")
# Define the types of command that this function will implement
@lightbulb.implements(commands.PrefixCommand, commands.SlashCommand)
async def todo(ctx: lightbulb.context.Context) -> None:
    # retrieve args
    date = ctx.options._options["date"]
    # retrieve user and server info
    uid = str(ctx.author.id)
    uname = ctx.author.username
    serv_id = str(ctx.guild_id)
    # create db connection
    connection = sqlite3.connect("assets/db/calendar.db")
    # create cursor to send commands
    cursor = connection.cursor()
    # retrieve events
    cursor.execute("""
        SELECT events.name, events.desc, events.time, events.server_id
        FROM events JOIN u_to_e ON events.id = u_to_e.event_id
        JOIN users ON users.uid = u_to_e.uid
        WHERE users.uid = (?) AND events.date = (?);""", (uid, date,))
    result = cursor.fetchall()
    connection.close()
    ## build response ##
    if not result:
        embed = (
            hikari.Embed(
                title="Your scheduled events",
                description=f"You have no events scheduled for the {date}.",
                colour=hikari.Colour(0x563275),
            )
            .set_author(name=f"Events from {date}")
            .set_footer(
                text=f"Requested by {ctx.member.display_name}",
                icon=ctx.member.avatar_url,
            )
        )
        resp = await ctx.respond(embed=embed)
    else:
        embed = hikari.Embed(title="Your scheduled events", description="",
            colour=hikari.Colour(0x563275),)
        embed.set_author(name=f"{date}")
        embed.set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url,
        )
        # add a field for each event
        for event in result:
            # retrieve the name of the server by its id
            guild = await ctx.bot.rest.fetch_guild(int(event[3]))
            # embed.add_field(name=f"At `{event[2]}` on server `{guild}`",
            #     value=f"```Name : {event[0]} \nDescription : {event[1]}```")
            embed.add_field(name=f"`{event[0]}`\n" + \
                f"At `{event[2]}` on server `{guild}` :",
                value=f"```{event[1]}```")
        resp = await ctx.respond(embed=embed)
    ## send response ##
    msg = await resp.message()


def load(bot: lightbulb.BotApp) -> None:
    bot.command(todo)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_command(bot.get_slash_command("todo"))