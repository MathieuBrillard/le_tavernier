import discord
import urllib.request
import requests
import os

async def nb_pages(codeSrc):
    ''' Function used to count the number of pages in a scan by parsing the web page source code.
        codeSrc: type str of an http.client.HTTPResponse object from urllib.request.urlopen().read()
            (ex: codeSrc = str(urllib.request.urlopen(url_src).read()))
        Returns an int (number of pages).
    '''
    codeSrc = codeSrc[codeSrc.find("Pages:"):]
    l = codeSrc.split("\\n")
    s = l[1]
    s = s[:s.find("Suiv")]
    nb = s.count("</a>") - 1
    return nb


### Bot command
async def download_scan(manga_name, nb_chapitre, ctx, bot):
    ''' Function used to download scans.
        manga_name: type str (ex: one-piece)
        nb_chapitre: type str (ex: 1024)
        ctx: context from discord API
        bot: discord.Client object form discord.commands lib
    '''
    # Bypass HTTP Error 403 (Forbidden)
    opener=urllib.request.build_opener()
    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    urllib.request.install_opener(opener)
    # Création de l'url
    web_site = "https://lelscans.net/mangas"
    url = web_site + "/" + manga_name + "/" + nb_chapitre + '/'
    url_src = 'https://lelscans.net/scan-one-piece/' + nb_chapitre + '/1'
    codeSrc = str(urllib.request.urlopen(url_src).read())
    # Création du dossier
    path = 'scans/' + manga_name
    if nb_chapitre not in os.listdir(path):
        path = 'scans/' + manga_name + '/' + nb_chapitre
        os.mkdir(path)
    path = 'scans/' + manga_name + '/' + nb_chapitre
    os.chdir(path)
    # Si jamais le dossier n'est pas vide
    if len(os.listdir()) != 0:
        print('le scan est déjà téléchargé')
        print('lancement de la lecture...')
        args = [manga_name, nb_chapitre]
        Scan_read(args, ctx, bot)
    else:
        # Téléchargement de toutes les pages
        ## comptage du nombre de pages du chapitre
        nbP = nb_pages(codeSrc)
        for i in range(nbP):
            if i < 10:
                page = '0' + str(i) + '.jpg'
            else:
                page = str(i) + '.jpg'
            # Création de l'url de dl
            to_dl = url + page
            # Sauvegarde du fichier
            f = open(page, 'wb')
            f.write(requests.get(to_dl).content)
            f.close()
            i += 1


### Bot command
async def Scans_list(ctx):
    ''' Function that can list the scans already downloaded.
        ctx: context from discord API
    '''
    scans_dict = {}
    os.chdir('scans/')
    scan_list = os.listdir()
    for scan in scan_list:
        scans_dict[scan] = list()
        chap_l = os.listdir(scan)
        scans_dict[scan].extend(chap_l)
    
    to_print = "```\n"
    for key, values in scans_dict.items():
        to_print += f"{key}: \n\t{values}\n"
    to_print += "```"
    embed=discord.Embed(color=0xffffff)
    embed.add_field(name='List of scans downloaded', value=to_print, inline=False)
    await ctx.send(embed=embed)


###Bot command
async def Scan_read(args, ctx, bot):
    ''' Function that allow you to read your dear scans in a discord embed.
        args: list of str like:
            manga_name: type str (ex: one-piece)
            nb_chapitre: type str (ex: 1024)
        ctx: context from discord API
    '''
    if len(args) != 2:
        embed = discord.Embed(color=0xffffff)
        embed.add_field(name="Error", value="Arguments must be like: \"mange-name\" \"chap-number\".", inline=False)
        await ctx.send(embed=embed)
        return
    manga_name = args[0]
    nb_chapitre = args[1]
    # Affichage de la page
    async def send_pages(file_path, page, i, nbP):
        file = discord.File(file_path, filename=page)
        if i == 0:
            embed = discord.Embed(title=f'Page n°{i+1}/{nbP}', color=0xffffff)
        else:
            embed = discord.Embed(title=f'Page n°{i+1}/{nbP}', color=0xffffff)
        embed.set_image(url=f"attachment://{page}")
        actual_page = await ctx.send(embed=embed, file=file)
        return actual_page
    
    def check1(reaction):
        if reaction.user_id == ctx.author.id and actual_page.id == reaction.message_id:
            if reaction.emoji.name == '➡️' or '⏹️':
                return reaction

    def check2(reaction):
        if reaction.user_id == ctx.author.id and actual_page.id == reaction.message_id:
            if reaction.emoji.name == '⬅️' or '➡️' or '⏹️':
                return reaction

    path = 'scans/' + manga_name + '/' + nb_chapitre
    nbP = len(os.listdir(path))
    for i in range(nbP):
        if i < 10:
            page = f"0{i}.jpg"
        else:
            page = f"{i}.jpg"
        file_path = path + '/' + page
        actual_page = await send_pages(file_path, page, i, nbP)
        if i == 0:
            await actual_page.add_reaction('➡️')
            await actual_page.add_reaction('⏹️')
            choice = await bot.wait_for("raw_reaction_add", check=check1)
            choice = choice.emoji.name
        else:
            await actual_page.add_reaction('⬅️')
            await actual_page.add_reaction('➡️')
            await actual_page.add_reaction('⏹️')
            choice = await bot.wait_for("raw_reaction_add", check=check2)
            choice = choice.emoji.name
        if choice == '➡️':
            i += 1
        elif choice == '⬅️':
            i -= 1
        elif choice == '⏹️':
            await actual_page.delete()
            return
        if choice:
            await actual_page.delete()


# def main():
#     #download_scan('one-piece', '1023')
#     scans_list(ctx=None)

# if __name__ == '__main__':
#     main()
