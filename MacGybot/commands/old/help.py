import discord

async def Help(ctx, cmd_name):
    cmd_list = ["agenda", "delete", "flipcoin", "help", "jankenpon", "leave", "p4", "pause", "play", "playtop", "poll", "queue", "resume", "search","skip"]
    embed = discord.Embed(title="Helper", description="Voici la liste des commandes disponibles ainsi que la syntaxe à utiliser.", color=0xee00ff)
    help_messages = [("agenda", ("Agenda", "```>agenda list ---> Affiche la liste des évènements enregistrer dans l'agenda.\n>agenda \"titre de l'évènement\" date(jj/mm/aaaa) heure(hh:mm) \"commentaire\"(facultatif)' --> Ajoute un nouvel évènement à l'agenda.\n[Aliases: a]```", False)),
                    ("delete", ("Delete", "```>delete (numéro de la musique dans la file d'attente) ---> Supprime la musique spécifiée de la file d'attente.\n[Aliases: d ; del]```", False)),
                    ("flipcoin", ("Flipcoin", "```>flipcoin ---> Simule un pile ou face.\n[Aliases: fc]```", False)),
                    ("help", ("Help", "```>help ---> Affiche ce message.\n>help command_name ---> Affiche le message d'aide pour la commande spécifiée.\n[Aliases: h]```", False)),
                    ("jankenpon", ("Jankenpon", "```>jankenpon @adversaire ---> Créé une partie de pierre feuille ciseau contre l'adversaire mentionné.\n[Aliases: jkp ; pierrefeuilleciseaux]```", False)),
                    ("leave", ("Leave", "```>leave ---> Déconnecte le bot du channel vocal.\n[Aliases: l ; stop]```", False)),
                    ("p4", ("P4", "```>p4 @adversaire ---> Créé une partie de puissance 4 contre l'adversaire mentionné. \n(Seul la personne écrivant la commande pourra choisir sa couleur, et c'est elle qui commencera.)\n[Aliases: puissance4]```", False)),
                    ("pause", ("Pause", "```>pause ---> Si le bot est connecté, mets la musique en pause.```", False)),
                    ("play", ("Play", "```>play (url or music name) ---> Joue une musique sur le bot.\n(Attention, nécessite d'être connecté à un channel vocal.)\n[Aliases: p]```", False)),
                    ("playtop", ("Playtop", "```>playtop (url or music name) ---> Joue une musique sur le bot, ou, s'il est déjà connecté, ajoute la musique en tête de file.\n(Attention, nécessite d'être connecté à un channel vocal.)\n[Aliases: pt]```", False)),
                    ("poll", ("Poll", "```>poll \"durée du sondage (en minutes)\"  \"question\" \"option1\" \"option2\" ... \"option10\" ---> Créé un sondage qui durera le temps spécifié dans le premier argument de la commande.\n(Attention, il doit y avoir 2 options minimum et 10 au maximum.)\n[Aliases: sondage]```", False)),
                    ("queue", ("Queue", "```>queue ---> Affiche les musiques dans la file d'attente.\n[Aliases: q]```", False)),
                    ("resume", ("Resume", "```>resume ---> Si la musique est sur pause, enlève la pause.\n[Aliases: r]```", False)),
                    ("search", ("Search", "```>search ---> Commande pour rechercher une musique.\n[Aliases: se]```", False)),
                    ("skip", ("Skip", "```>skip ---> Passe à la musique suivante (s'il n'y en a pas, déconnecte le bot).\n[Aliases: s ; n ; next]```", False)),
                    ]
    if cmd_name == None:
        for command in help_messages:
            args = command[1]
            embed.add_field(name=args[0], value=args[1], inline=args[2])
        embed.set_footer(text="D'autres commandes sont susceptibles d'être ajoutée au cours du temps. Pour toute question ou suggestion, veuillez contacter @ippei#3784.")
    else:
        if cmd_name in cmd_list:
            embed = discord.Embed(title="Helper", description=f'Menu d\'aide pour la commande \"{cmd_name}\".', color=0xee00ff)
            i = 0
            while i < len(help_messages):
                if cmd_name == help_messages[i][0]:
                    args = help_messages[i][1]
                    embed.add_field(name=args[0], value=args[1], inline=args[2])
                i+=1
            embed.set_footer(text="D'autres commandes sont susceptibles d'être ajoutée au cours du temps. Pour toute question ou suggestion, veuillez contacter @ippei#3784.")        
        else:
            embed=discord.Embed(title="Helper", description="Erreur. Cette commande n'existe pas (attention à ne pas mettre de majuscule).", color=0xee00ff)
    await ctx.send(embed=embed)