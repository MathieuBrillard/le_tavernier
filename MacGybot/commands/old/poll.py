import discord
from datetime import datetime
import asyncio

async def Poll(ctx, args, bot):
    """
        >poll (int):minutes "question" "option1" "option2" ... "option10"
    """
    global reacted_user, current_time, fin_timer
    ### Création de l'embed ###
    to_wait = int(args[0])
    question = args[1]
    desc = f'Vous avez {to_wait} minute(s) pour participer.'
    embed=discord.Embed(title="Vous propose de répondre à un sondage !",
        description=desc, color=0x00db07)
    embed.set_author(name=str(ctx.author))
    embed.set_footer(text="(Cliquez sur une des emotes dans le temps imparti pour participer !\n Attention, vous ne pourrez plus changer après avoir réagi une fois.)")
    i = 2
    n = len(args)
    emotes = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    # Ajoute les champs en fonction du nb d'args
    embed.add_field(name=question, value="----------", inline=False)
    while i < n:
        opt = args[i]
        emote = emotes[i-2]
        embed.add_field(name=opt, value=emote, inline=False)
        i += 1
    sondage = await ctx.send(embed=embed) # Envoie de l'embed
    # Ajout des réactions en fonction du nb d'args
    i = 0
    while i < n-2:
        await sondage.add_reaction(emotes[i])
        i += 1
    ### Attente des réactions ###
    # Déclaration du timer
    current_time = str(datetime.now()).split(' ')[1].split('.')[0]
    print(f'début sondage : {current_time}')
    hh = current_time.split(':')[0]
    mm = current_time.split(':')[1]
    ss = current_time.split(':')[2]
    mm = int(mm) + to_wait
    while mm >= 60:
        hh = int(hh) + 1
        if hh >= 24:
            hh -= 24
            if hh < 10:
                hh = f'0{hh}'
        mm = int(mm) - 60
    if mm < 10:
        mm = f'0{mm}'
    fin_timer = f'{hh}:{mm}:{ss}'
    print(f'fin sondage : {fin_timer}')
    # Reaction handler
    reacted_user = []
    def check(reaction):
        global reacted_user
        if sondage.id == reaction.message_id and reaction.user_id not in reacted_user and reaction.user_id != bot.user.id:
            reacted_user += [reaction.user_id]
            return reaction
    ### Timer ###
    reactions = []
    while current_time != fin_timer:
        current_time = str(datetime.now()).split(' ')[1].split('.')[0]
        try:
            react = await bot.wait_for("raw_reaction_add", timeout=1.0, check=check)
        except asyncio.TimeoutError:
            pass
        else:
            reactions += [react.emoji.name]
    ### Evaluation des résultats ###
    # Compte le nombre de fois qu'apparaît un élément
    compteur = []
    i = 0
    while i < n-2:
        cnt = reactions.count(emotes[i]) # On compte le nombre de fois qu'apparaît une emote dans le tab reactions
        compteur += [(emotes[i], cnt)] # On créé un tuple avec (emote, occurence)
        i += 1
    compteur.sort(key = lambda x: x[1], reverse=True) # Classe par ordre décroissant en fonction de l'occurence
    winner_index = emotes.index(compteur[0][0])
    winner = args[winner_index+2]
    embed=discord.Embed(title=f'Résultat du sondage de {str(ctx.author)} !', color=0x00db07)
    embed.add_field(name=f'\"{winner}\"', value="est l'option avec le plus de votes !", inline=False)
    embed.set_footer(text="Merci pour votre participation ! 😉")
    await sondage.reply(embed=embed)
