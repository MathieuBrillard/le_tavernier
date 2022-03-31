import discord
from PIL import Image
import numpy

### Emote Used ###
# 1️⃣ 2️⃣ 3️⃣ 4️⃣ 5️⃣ 6️⃣ 7️⃣ 🔴 🟡
### Game Board ###
# x = colonnes, y = lignes
# 0 = en bas, 0 = à gauche
# 0,0 = (9,488) | 1,0 = (105,488) --> 96 pixel de décalage pour chaque cases.
# 0,1 = (9,392) --> -96 pixels de décalages.

def is_legal_move(gameboard, column):
    ''' Si le movement est légal, la fonction renvoie la ligne à laquelle une case libre a été trouvée.
        Sinon, elle renvoie -1. 
        Gameboard : array[shape=6,7]
        Column = :  0 <= int <= 6
    '''
    x = 0
    y = 5
    while y >= 0:
        while x <= 6:
            if x == column:
                if gameboard[y,x] == 0:
                    return y
            x += 1
        x = 0
        y -= 1
    return -1


def img_coords(ligne, colonne):
    ligne = ligne - 5
    ligne = abs(ligne)
    x = 9 + 96 * colonne
    y = 488 + (-96 * ligne)
    coords = (x,y)
    return coords


def board_update(old_board, gameboard, color, joueur, ligne, colonne):
    # Création du gameboard
    grille_size = old_board.size
    board = Image.new('RGBA', (grille_size[0], grille_size[1]), (250,250,250, 0))
    board.paste(old_board, (0,0))
    old_board.close()
    jeton = Image.open(color)
    # Choix de la position
    coords = img_coords(ligne, colonne)
    # Affectation du jeton à la position choisie
    board.paste(jeton, coords, jeton.convert('RGBA'))
    # Sauvegarde de l'image
    board.save('ressources/board.png', 'PNG')
    jeton.close()
    if joueur == "j1":
        gameboard[ligne, colonne] = 1
    else:
        gameboard[ligne, colonne] = 2
    return board, gameboard


def is_winner(gameboard, joueur):
    if joueur == "j1":
        jeton = 1
    else:
        jeton = 2
    x = 0
    y = 5
    j_list = 0
    # Parsing des lignes
    while y >= 0:
        while x <= 6:
            if gameboard[y][x] == jeton:
                j_list += 1
                if j_list == 4:
                    return True
            else:
                j_list = 0
            x += 1
        j_list = 0
        x = 0
        y -= 1
    # Parsing des colonnes
    x = 0
    y = 5
    j_list = 0
    while x <= 6:
        while y >= 0:
            if gameboard[y][x] == jeton:
                j_list += 1
                if j_list == 4:
                    return True
            else:
                j_list = 0
            y -= 1
        j_list = 0
        y = 5
        x += 1
    # Parsing Diag (gauche à droite)
    x = 0
    y = 5
    j_list = 0
    while y >= 0:
        while x <= 6:
            if gameboard[y][x] == jeton:
                x1 = x
                y1 = y
                while x1 <= 6:
                    if gameboard[y1][x1] == jeton:
                        j_list += 1
                        if j_list == 4:
                            return True
                    else:
                        j_list = 0
                    y1 -=1
                    x1 +=1
                    if y1 < 0:
                        j_list = 0
                        break
                j_list = 0
            x += 1
        j_list = 0
        x = 0
        y -= 1
    # Parsing Diag (droite à gauche)
    x = 6
    y = 5
    j_list = 0
    while y >= 0:
        while x >= 0:
            if gameboard[y][x] == jeton:
                x1 = x
                y1 = y
                while x1 >= 0:
                    if gameboard[y1][x1] == jeton:
                        j_list += 1
                        if j_list == 4:
                            return True
                    else:
                        j_list = 0
                    y1 -=1
                    x1 -=1
                    if y1 < 0:
                        j_list = 0
                        break
                j_list = 0
            x -= 1
        j_list = 0
        x = 6
        y -= 1
    return False


def is_egalite(gameboard):
    for lignes in gameboard:
        for colonne in lignes:
            if colonne == 0:
                return False
    return True


async def P4(ctx, j2, bot):
    j1 = ctx.author
    gameboard = numpy.array(numpy.zeros(shape=[6,7], dtype=int)) # création du tableau de jeu
    # Choix de la couleur :
    desc = f'{j1}, veuillez choisir votre couleur en réagissant.'
    embed = discord.Embed(title=f'Puissance 4\n{j1} _VS_  {j2}', description=desc, color=0x0062ff)
    color = await ctx.send(embed=embed)
    await color.add_reaction('🔴')
    await color.add_reaction('🟡')
    def check_color(reaction):
        if reaction.user_id == j1.id and color.id == reaction.message_id:
            if reaction.emoji.name == '🔴' or '🟡':
                return reaction
    emote = await bot.wait_for("raw_reaction_add", check=check_color)
    if emote.emoji.name == '🔴':
        color_j1 = 'ressources/rouge.png'
        color_j2 = 'ressources/jaune.png'
    elif emote.emoji.name == '🟡':
        color_j1 = 'ressources/jaune.png'
        color_j2 = 'ressources/rouge.png'
    
    ### Starting the game : ###
    # Création de l'image de départ
    grille = Image.open('ressources/grille.png')
    grille_size = grille.size
    board = Image.new('RGBA', (grille_size[0], grille_size[1]), (250,250,250, 0))
    board.paste(grille, (0,0))
    board.save('ressources/board.png', 'PNG')
    grille.close()
    file = discord.File("ressources/grille.png", filename="grille.png")
    turn = 1
    embed = discord.Embed(title=f'Puissance 4\n{j1} _VS_  {j2}\nTour n°{turn}', color=0x0062ff)
    embed.set_footer(text=f'C\'est au tour de {j1}.\nRéagissez pour jouer.')
    embed.set_image(url="attachment://grille.png")
    global msg
    msg = await ctx.send(embed=embed, file=file)
    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')
    await msg.add_reaction('3️⃣')
    await msg.add_reaction('4️⃣')
    await msg.add_reaction('5️⃣')
    await msg.add_reaction('6️⃣')
    await msg.add_reaction('7️⃣')
    def check_column_j1(reaction):
        if reaction.user_id == j1.id and msg.id == reaction.message_id:
            if reaction.emoji.name == '1️⃣' or '2️⃣' or '3️⃣' or '4️⃣' or '5️⃣' or '6️⃣' or '7️⃣':
                return reaction
    def check_column_j2(reaction):
        if reaction.user_id == j2.id and msg.id == reaction.message_id:
            if reaction.emoji.name == '1️⃣' or '2️⃣' or '3️⃣' or '4️⃣' or '5️⃣' or '6️⃣' or '7️⃣':
                return reaction
    game = True
    while game:
        if turn % 2 != 0:
            coup_j1 = await bot.wait_for("raw_reaction_add", check=check_column_j1)
            jeton = color_j1
            joueur = "j1"
            coup_joue = coup_j1.emoji.name
        else:
            coup_j2 = await bot.wait_for("raw_reaction_add", check=check_column_j2)
            jeton = color_j2
            joueur = "j2"
            coup_joue = coup_j2.emoji.name
        if coup_joue== '1️⃣':
            colonne = 0
        elif coup_joue == '2️⃣':
            colonne = 1
        elif coup_joue == '3️⃣':
            colonne = 2
        elif coup_joue == '4️⃣':
            colonne = 3
        elif coup_joue == '5️⃣':
            colonne = 4
        elif coup_joue == '6️⃣':
            colonne = 5
        elif coup_joue == '7️⃣':
            colonne = 6
        ligne = is_legal_move(gameboard, colonne)
        if ligne == -1:
            await ctx.send("Ce coup est illégal, réessayer.")
        else:
            old_board = board
            board, gameboard = board_update(old_board, gameboard, jeton, joueur, ligne, colonne)
            file = discord.File("ressources/board.png", filename="board.png")
            if is_egalite(gameboard) == True:
                embed = discord.Embed(title=f'Puissance 4\n{j1} _VS_  {j2}\nTour n°{turn}\nEgalité !', color=0x0062ff)
                embed.set_image(url="attachment://board.png")
                msg = await ctx.send(embed=embed, file=file)
                board.close()
                game = False
                return
            if is_winner(gameboard, joueur) == False:
                turn += 1
                embed = discord.Embed(title=f'Puissance 4\n{j1} _VS_  {j2}\nTour n°{turn}', color=0x0062ff)
                if joueur == "j1":
                    embed.set_footer(text=f'C\'est au tour de {j2}.\nRéagissez pour jouer.')
                else:
                    embed.set_footer(text=f'C\'est au tour de {j1}.\nRéagissez pour jouer.')
                embed.set_image(url="attachment://board.png")
                msg = await ctx.send(embed=embed, file=file)
                await msg.add_reaction('1️⃣')
                await msg.add_reaction('2️⃣')
                await msg.add_reaction('3️⃣')
                await msg.add_reaction('4️⃣')
                await msg.add_reaction('5️⃣')
                await msg.add_reaction('6️⃣')
                await msg.add_reaction('7️⃣')
            else:
                if joueur == "j1":
                    embed = discord.Embed(title=f'Puissance 4\n{j1} _VS_  {j2}\nTour n°{turn}\nLe Gagnant est {j1} !', color=0x0062ff)
                else:
                    embed = discord.Embed(title=f'Puissance 4\n{j1} _VS_  {j2}\nTour n°{turn}\nLe Gagnant est {j2} !', color=0x0062ff)
                embed.set_image(url="attachment://board.png")
                msg = await ctx.send(embed=embed, file=file)
                board.close()
                game = False
