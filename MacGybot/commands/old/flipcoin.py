import random
import asyncio
import discord

async def Flipcoin(ctx):
    ### Simulation du pile ou face ###
    alea = random.randint(1,100000)
    if alea % 2 == 0:
        coin = "Face"
    else:
        coin = "Pile"
    ### Animation de lancer ###
    file = discord.File("commands/ressources/coin-toss.gif", filename="coin-toss.gif")
    embed = discord.Embed(title='Lancement de la pièce ...', color=discord.Color.gold())
    embed.set_image(url="attachment://coin-toss.gif")
    toss_coin = await ctx.send(embed=embed, file=file)
    await asyncio.sleep(3) # on attends 3 sec
    await toss_coin.delete() # on delete le gif de lancer
    ### Affichage du résultat ###
    if coin == "Face":
        file = discord.File("commands/ressources/face.jpg", filename="face.jpg")
        embed = discord.Embed(title="C'est **face** !", color=discord.Color.gold())
        embed.set_image(url="attachment://face.jpg")
    else:
        file = discord.File("commands/ressources/pile.jpg", filename="pile.jpg")
        embed = discord.Embed(title="C'est **pile** !", color=discord.Color.gold())
        embed.set_image(url="attachment://pile.jpg")
    await ctx.send(embed=embed, file=file)
