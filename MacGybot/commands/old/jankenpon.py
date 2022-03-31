import discord


def whois_winner(j1, c_j1, j2, c_j2):
    # Détermine le joueur gagnant en fonction du coup joué
    if c_j1 == c_j2 :
        return 0 # égalité
    # pierre contre feuille
    if c_j1 == '👊' and c_j2 == '🍁':
        return j2
    if c_j2 == '👊' and c_j1 == '🍁':
        return j1
    # pierre contre ciseau
    if c_j1 == '👊' and c_j2 == '✂':
        return j1
    if c_j2 == '👊' and c_j1 == '✂':
        return j2
    # feuille contre ciseau
    if c_j1 == '🍁' and c_j2 == '✂':
        return j2
    if c_j2 == '🍁' and c_j1 == '✂':
        return j1

async def Jankenpon(ctx, j2, bot):
    ### Envoi des messages privés aux joueurs ###
    j1 = ctx.author
    desc = "Réagissez pour jouer !"
    embed = discord.Embed(title=f'Pierre Feuille Ciseau _VS_  {j2}', description=desc, color=discord.Color.blue())
    reply_j1 = await j1.send(embed=embed)
    embed = discord.Embed(title=f'Pierre Feuille Ciseau _VS_  {j1}', description=desc, color=discord.Color.blue())
    reply_j2 = await j2.send(embed=embed)
    # Ajout des emotes aux messages
    await reply_j1.add_reaction('\N{FISTED HAND SIGN}') # 👊
    await reply_j1.add_reaction('\N{MAPLE LEAF}') # 🍁
    await reply_j1.add_reaction('\N{BLACK SCISSORS}') # ✂
    await reply_j2.add_reaction('\N{FISTED HAND SIGN}')
    await reply_j2.add_reaction('\N{MAPLE LEAF}')
    await reply_j2.add_reaction('\N{BLACK SCISSORS}')

    # Lancement de la fonction pour détécter les émotes
    def check_j1(reaction):
        if reaction.user_id == j1.id and reply_j1.id == reaction.message_id:
            if reaction.emoji.name == '👊' or '🍁' or '✂':
                return reaction
    
    def check_j2(reaction):
        if reaction.user_id == j2.id and reply_j2.id == reaction.message_id:
            if reaction.emoji.name == '👊' or '🍁' or '✂':
                return reaction

    react_j1 = await bot.wait_for("raw_reaction_add", check=check_j1)
    react_j2 = await bot.wait_for("raw_reaction_add", check=check_j2)
    c_j1 = react_j1.emoji.name
    c_j2 = react_j2.emoji.name
    winner = whois_winner(j1, c_j1, j2, c_j2)
    if winner == 0:
        desc = "**Egalité !**\nUne autre manche sera donc joué !"
        embed = discord.Embed(title=f'{j1} a joué {c_j1} _VS_  {j2} a joué {c_j2}', description=desc, color=discord.Color.blue())
        await ctx.send(embed=embed)
        await Jankenpon(ctx, j2, bot)
    else:
        desc = f'Le vainqueur est **{winner}**\nBravo !'
        embed = discord.Embed(title=f'{j1} a joué {c_j1} _VS_  {j2} a joué {c_j2}', description=desc, color=discord.Color.blue())
        await ctx.send(embed=embed)
