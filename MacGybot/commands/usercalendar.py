# date time and background tasks
import asyncio
import datetime as dt
# manage generated files
import os
# errors and calendar generation
from commands.calendrier.gen_cal import gen_cal
from commands.calendrier.errors import IncorrectFormat
# discord libs
import hikari
import lightbulb
from lightbulb import commands



# The options the command will have.
@lightbulb.option("format", "The format of calendar you want to get.", str)
# Convert the function into a command
@lightbulb.command("usercalendar", "Get a calendar.")
# Define the types of command that this function will implement
@lightbulb.implements(commands.PrefixCommand, commands.SlashCommand)
async def usercalendar(ctx: lightbulb.context.Context) -> None:
    format = ctx.options._options["format"] # get the argument
    try:
        ## generate the name of the file ##
        user_id = str(ctx.author.id)
        file_name = user_id + "_" + str(dt.datetime.now().date()) + "_0.png"
        path = os.getcwd()
        gen_cal(format, file_name, user_id)
    except IncorrectFormat as e: # handle arguments errors
        await ctx.respond(IncorrectFormat.__str__(e))
        return
    ## dropdown creation ##
    select_menu = (
        ctx.bot.rest.build_action_row()
        .add_select_menu("format_selection")
        .set_placeholder("Pick another format here.")
    )
    select_menu_disabled = (
        ctx.bot.rest.build_action_row()
        .add_select_menu("format_selection_disabled")
        .set_placeholder("Pick another format here.")
    ).set_is_disabled(True)
    opts = ("day", "week", "month")
    for opt in opts:
        select_menu.add_option(
            opt.capitalize(),
            opt,
        ).add_to_menu()
        select_menu_disabled.add_option(
            opt.capitalize(),
            opt,
        ).add_to_menu()
    ## generate embed response ##
    embed = (
        hikari.Embed(
            title=f"{format.capitalize()}ly Calendar",
            description="",
            colour=hikari.Colour(0x563275),
            # Doing it like this is important.
            timestamp=dt.datetime.now().astimezone(),
        )
        .set_image(hikari.files.File(f"{path}\\commands\\calendrier\\generated\\{file_name}"))
        .set_author(name="Information")
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url,
        )
    )
    ## send response ##
    resp = await ctx.respond(embed=embed, component=select_menu.add_to_container())
    msg = await resp.message()
    ## handle events ##
    try:
        event = await ctx.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout = 10, #TODO: set it to 60
            predicate = lambda e:
                isinstance(e.interaction, hikari.ComponentInteraction)
                and e.interaction.user.id == ctx.author.id
                and e.interaction.message.id == msg.id
                and e.interaction.component_type == hikari.ComponentType.SELECT_MENU
        )
    except asyncio.TimeoutError:
        await msg.edit(component=select_menu_disabled.add_to_container())
    else:
        await ctx.respond(response_type=5, content="Loading ...")
        await msg.edit(component=select_menu_disabled.add_to_container())
        if event.interaction.values[0] == "month":
            await handle_dropdown(ctx, format="month", old_msg=msg)
        elif event.interaction.values[0] == "week":
            await handle_dropdown(ctx, format="week", old_msg=msg)
        elif event.interaction.values[0] == "day":
            await handle_dropdown(ctx, format="day", old_msg=msg)


async def handle_dropdown(ctx: lightbulb.context.Context, format: str, old_msg: hikari.Message) -> None:
    ## generate the name of the file ##
    user_id = str(ctx.author.id)
    file_name = user_id + str(dt.datetime.now().date()) + "_1.png"
    path = os.getcwd()
    gen_cal(format, file_name, user_id)
    ## dropdown creation ##
    select_menu = (
        ctx.bot.rest.build_action_row()
        .add_select_menu("format_selection_2")
        .set_placeholder("Pick another format here.")
    )
    select_menu_disabled = (
        ctx.bot.rest.build_action_row()
        .add_select_menu("format_selection_disabled_2")
        .set_placeholder("Pick another format here.")
    ).set_is_disabled(True)
    opts = ("day", "week", "month")
    for opt in opts:
        select_menu.add_option(
            opt.capitalize(),
            opt,
        ).add_to_menu()
        select_menu_disabled.add_option(
            opt.capitalize(),
            opt,
        ).add_to_menu()
    ## generate embed response ##
    embed = (
        hikari.Embed(
            title=f"{format.capitalize()}ly Calendar",
            description="",
            colour=hikari.Colour(0x563275),
            # Doing it like this is important.
            timestamp=dt.datetime.now().astimezone(),
        )
        .set_image(hikari.files.File(f"{path}\\commands\\calendrier\\generated\\{file_name}"))
        .set_author(name="Information")
        .set_footer(
            text=f"Requested by {ctx.member.display_name}",
            icon=ctx.member.avatar_url,
        )
    )
    ## send response ##
    old_msg = await old_msg.edit(embed=embed, replace_attachments=True, component=select_menu.add_to_container())
    await ctx.delete_last_response()
    ## handle events ##
    try:
        event = await ctx.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout = 10, #TODO: set it to 60
            predicate = lambda e:
                isinstance(e.interaction, hikari.ComponentInteraction)
                and e.interaction.user.id == ctx.author.id
                and e.interaction.message.id == old_msg.id
                and e.interaction.component_type == hikari.ComponentType.SELECT_MENU
        )
    except asyncio.TimeoutError:
        await old_msg.edit(component=select_menu_disabled.add_to_container())
    else:
        if event.interaction.values[0] == "month":
            await handle_dropdown(ctx, format="month", old_msg=old_msg)
        elif event.interaction.values[0] == "week":
            await handle_dropdown(ctx, format="week", old_msg=old_msg)
        elif event.interaction.values[0] == "day":
            await handle_dropdown(ctx, format="day", old_msg=old_msg)
        

def load(bot: lightbulb.BotApp) -> None:
    bot.command(usercalendar)


def unload(bot: lightbulb.BotApp) -> None:
    bot.remove_command(bot.get_slash_command("usercalendar"))
