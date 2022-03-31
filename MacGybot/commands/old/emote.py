async def Emote(ctx, bot):
    msg = await ctx.send("régissez ici.")
    def check(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
                return reaction
    react = await bot.wait_for("raw_reaction_add", check=check)
    print(react.emoji.name)
    await msg.delete()