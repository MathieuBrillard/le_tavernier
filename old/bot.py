# Used to store your token in a .env file
from dotenv import load_dotenv
from os import getenv
# discord.py libs
import discord
from discord.ext import commands
# Functions in *.py files
from help import *
from agenda import *
from flipcoin import *
from jankenpon import *
from p4 import *
from poll import *
from emote import *
from music import *
from scans import *


load_dotenv()
token = getenv("TOKEN")

bot = commands.Bot(command_prefix=">",
                   case_insensitive=True, help_command=None)


@bot.event
async def on_ready():
    print('{0.user} est connecté !'.format(bot))
    await eventTimer(bot)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    #print('Message from {0.author}: {0.content}'.format(message))
    await bot.process_commands(message)


# From help.py
@bot.command(name='help', aliases=['h'], description="Commande affichant le message d'aide.")
async def help(ctx, cmd_name=None):
    await Help(ctx, cmd_name)


# From agenda.py
@bot.command(name='agenda', aliases=['a'], description="Commande pour utiliser l'agenda.")
async def agenda(ctx, *args):
    if len(args) == 1:
        if args[0] == "list":
            await AgendaList(ctx)
    elif len(args) == 3 or 4:
        await Agenda(ctx, args, bot)
    else:
        await ctx.send("Erreur de syntaxe, écrivez '>help agenda' pour obtenir de l'aide.")


# From flipcoin.py
@bot.command(name='flipcoin', aliases=['fc'], description="Commande pour simuler un pile ou face.")
async def flipcoin(ctx):
    await Flipcoin(ctx)


# From jankenpon.py
@bot.command(name='jankenpon', aliases=['jkp', 'pierrefeuilleciseaux'],
                description="Commande pour jouer au pierre feuille ciseau.")
async def jankenpon(ctx, joueur2: discord.User):
    await Jankenpon(ctx, joueur2, bot)


# From p4.py
@bot.command(name='p4', aliases=['puissance4'], description="Commande pour jouer au puissance 4.")
async def p4(ctx, joueur2: discord.User):
    await P4(ctx, joueur2, bot)


# From poll.py
@bot.command(name='poll', aliases=['sondage'], description="Commande pour faire un sondage.")
async def poll(ctx, *args):
    await Poll(ctx, args, bot)


# From emote.py (dev command)
@bot.command(name='emote', description="Commande pour print des emotes.")
async def emote(ctx):
    await Emote(ctx, bot)


# From music.py
@bot.command(name='leave', aliases=['l', 'stop'], description="Commande pour faire quitter le bot du channel vocal.")
async def leave(ctx):
    await Leave(ctx)


# From music.py
@bot.command(name='resume', aliases=['r'], description="Commande pour sortir le bot du mode pause.")
async def resume(ctx):
    await Resume(ctx)


# From music.py
@bot.command(name='pause', description="Commande pour mettre le bot en pause.")
async def pause(ctx):
    await Pause(ctx)


# From music.py
@bot.command(name='skip', aliases=['s', 'n', 'next'], description="Commande pour passer à la prochaine musique.")
async def skip(ctx):
    await Skip(ctx)


# From music.py
@bot.command(name='play', aliases=['p'], description="Commande pour jouer une musique sur le bot.")
async def play(ctx, *args):
    await Play(ctx, args)


# From music.py
@bot.command(name='playtop', aliases=['pt'], description="Commande pour ajouter une musique au début de la file.")
async def playtop(ctx, *args):
    await Playtop(ctx, args)


# From music.py
@bot.command(name='queue', aliases=['q'], description="Commande afficher la liste des prochaines musiques.")
async def queue(ctx):
    await Queue(ctx)


# From music.py
@bot.command(name='delete', aliases=['d', 'del'], description="Commande pour enlever une musique de la liste d'attente.")
async def delete(ctx, nb):
    await Delete(ctx, nb)


# From music.py
@bot.command(name='search', aliases=['se'], description="Commande pour chercher une musique sur youtube.")
async def search(ctx, *args):
    await Search(ctx, args, bot)


# From scans.py
@bot.command(name='scans-list', aliases=['sc-l'], description="Commande pour afficher la liste des scans téléchargés.")
async def scans_list(ctx):
    await Scans_list(ctx)


# From scans.py
@bot.command(name='scan-read', aliases=['sc-r'], description="Commande pour lire un scan téléchargés.")
async def scan_read(ctx, *args):
    await Scan_read(args, ctx, bot)


@bot.command(name='shutdown', aliases=['off'], description="Commande pour éteindre le bot.")
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("*Shutting down...*")
    try:
        await ctx.guild.voice_client.disconnect()
    except:
        pass
    exit()


bot.run(token)
