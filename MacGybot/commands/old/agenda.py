import discord
import os
from datetime import datetime
import asyncio

async def AgendaList(ctx):
    '''
        Fonction pour afficher le contenu de l'agenda.
        Utilisation :
            >agenda list
    '''
    ### CREATING TXT FILE ###
    SCRIPT_PATH = os.path.dirname(__file__) #<-- absolute dir the script is in
    REL_PATH = 'agenda.csv' # name of the output file
    abs_file_path = os.path.join(SCRIPT_PATH, REL_PATH)
    f = open(abs_file_path, "r") # open the file in read
    #########################
    lignes = f.readlines() # put all lignes of the file into a tab
    i = 0
    for ligne in lignes:
        if i == 0:
            i += 1
        else:
            event = ligne.split(';')
            auteur = event[1]
            titre = event[2]
            date = event[3]
            heure = event[4]
            if len(event) == 5:
                to_send = "Auteur : "+auteur+"\nTitre : "+titre+"\nDate : "+date+"\nHeure : "+heure
            elif len(event) == 6:
                comment = event[5]
                to_send = "Auteur : "+auteur+"\nTitre : "+titre+"\nDate : "+date+"\nHeure : "+heure+"\nCommentaire : "+comment
            embed = discord.Embed(title=f'Evènement n°{i}', description=to_send, color=discord.Color.red())
            await ctx.send(embed=embed)
            i += 1
    f.close()


async def eventTimer(bot):
    '''
        Fonction d'alarme pour l'agenda
    '''
    print("Timer started")
    global started
    global ok
    ok = False
    started = True
    ### CREATING TXT FILE ###
    SCRIPT_PATH = os.path.dirname(__file__) #<-- absolute dir the script is in
    REL_PATH = 'agenda.csv' # name of the output file
    abs_file_path = os.path.join(SCRIPT_PATH, REL_PATH)
    try:
        f = open(abs_file_path, "r+") # open the file in read+write
    except:
        f = open(abs_file_path, "w+")
        f.write("channel_id;author;title;date;hour;comment(optional)\n")
    #########################
    lignes = f.readlines() # put all lignes of the file into a tab
    if len(lignes) <= 1:
        started = False
        print("Timer Stopped")
        return
    else:
        continu = True
        while continu:
            # Récupération et formatage de la date et de l'heure
            date_time = str(datetime.now())
            date = date_time.split(' ')[0]
            dd = date.split('-')[2]
            mm = date.split('-')[1]
            yyyy = date.split('-')[0]
            date = dd + "/" + mm + "/" + yyyy
            time = date_time.split(' ')[1]
            time = time.split('.')[0]
            hh = time.split(':')[0]
            minutes = time.split(':')[1]
            time = hh + ":" + minutes
            ###
            # Parsing de chaque ligne de l'agenda
            for ligne in lignes:
                args = ligne.split(';')
                if date == args[3] and time == args[4]:
                    auteur = args[1]
                    if len(args) == 5:
                        to_send = "Auteur : "+auteur+"\n@everyone"
                    elif len(args) == 6:
                        comment = args[5]
                        to_send = "Auteur : "+auteur+"\nCommentaire : "+comment+"\n@everyone"
                    titre = '\N{BELL}'+" "+args[2]
                    embed = discord.Embed(title=titre, description=to_send, color=discord.Color.red())
                    chan = bot.get_channel(int(args[0]))
                    await chan.send(embed=embed)
                    ok = True
                    to_delete = ligne
            ### Supprimer la ligne après le rappel ###
            if ok == True:
                f.close()
                f = open(abs_file_path, "w")
                for ligne in lignes:
                    if ligne != to_delete:
                        f.write(ligne)
                f.close()
                f = open(abs_file_path, "r")
                lignes = f.readlines()
                ok == False
                if len(lignes) <= 1:
                    f.close()
                    continu = False
                    started = False
                    print("Timer Stopped")
                    return
            await asyncio.sleep(30) # pour limiter la consommation de ressource inutilement
    f.close()


async def Agenda(ctx, args, bot):
    '''
        Fonction pour ajouter un évènement à l'agenda :
        Utilisation :
            >agenda titre date(dd/mm/yyyy) heure(hh:mm) "commentaire"(facultatif)
    '''
    ### CREATING TXT FILE ###
    SCRIPT_PATH = os.path.dirname(__file__) #<-- absolute dir the script is in
    REL_PATH = 'agenda.csv' # name of the output file
    abs_file_path = os.path.join(SCRIPT_PATH, REL_PATH)
    f = open(abs_file_path, "r+") # open the file in write
    #########################
    f.readlines() # pour déplacer le curseur à la fin du fichier
    channel_id = ctx.message.channel.id
    auteur = ctx.author
    titre = args[0]
    date = args[1]
    heure = args[2]
    if len(args) == 3:
        to_write = "\n"+str(channel_id)+";"+str(auteur)+";"+titre+";"+date+";"+heure
    elif len(args) == 4:
        comment = args[3]
        to_write = "\n"+str(channel_id)+";"+str(auteur)+";"+titre+";"+date+";"+heure+";"+comment
    f.write(to_write)
    await ctx.message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
    f.close()
    if started == True:
        return
    else:
        await eventTimer(bot)