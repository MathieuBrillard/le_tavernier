import discord
import os
from lxml import etree
from discord.ext import commands
import asyncio, json
import youtube_dl
import youtube_search

playlists = {} # playlists loaded from each guild will be stored here
musics = {} # musics from each guild will be stored here.
now_playing = {} # music actually playing will be stored here
ytdl_opts = { # Youtube-dl options to improve the quality
    'format' : 'bestaudio/best',
    'quiet' : True,
    'postprocessors' : [{
        'key' : 'FFmpegExtractAudio',
        'preferredcodec' : 'wav',
        'preferredquality' : '192'
    }]
}
ytdl = youtube_dl.YoutubeDL(ytdl_opts)

bot = commands.Bot(command_prefix=">", case_insensitive=True, help_command=None)

async def sendMsg(ctx, str_to_send, title=None, color=None, old_msg=None):
    ''' Function used to send discord message.
        return: (discord.Message)
        ctx: context from discord.py
        str_to_send: (str) --> message content
        title: (str) --> title of the embed. if None, message will not be a discord.Embed but a discord.Message
        color: (hexa) --> value of the embed color in hexa. If none, embed will not have a color.
        old_msg: (discord.Message) --> message that will be suppressed before sending the new one
    '''
    if title == None:
        await ctx.send(str_to_send)
    else:
        if color == None:
            embed = discord.Embed()
        else:
            embed = discord.Embed(color=color)
        embed.add_field(name=title, value=str_to_send, inline=False)
        if old_msg != None:
            await old_msg.delete()
        msg = await ctx.send(embed=embed)
        return msg

async def addReactions(msg, tab):
    ''' Function used to add reactions to a message.
        msg: (discord.Message) --> message to add reactions to.
        tab: (list) --> list of reaction to add
    '''
    for reaction in tab:
        await msg.add_reaction(reaction)

def isPlaylist(ctx, name):
        """ Return True if the named playlist exists.
            False if not.
        """
        ### CREATING/OPENING STORAGE FILE ###
        if not os.path.exists('commands/playlists'):
            os.makedirs('commands/playlists')
        STORAGE_FOLDER = os.path.dirname('commands/playlists/')
        REL_PATH = f'{ctx.guild}.xml'  # name of the output file
        abs_file_path = os.path.join(STORAGE_FOLDER, REL_PATH)
        try:
            f = open(abs_file_path, "r+")  # open the file in read+write
        except:
            f = open(abs_file_path, "w+")
        f.close()
        #####################################
        # Parse xml file
        try:
            tree = etree.parse(f'commands/playlists/{ctx.guild}.xml')
            root = tree.getroot()
            noms = []
            for playlist in root:
                noms.append(playlist.values()[0])
            if name not in noms:
                return False
            else:
                return True
        except:
            return False

class Video:
    def __init__(self, ctx, link=None, video=None):
        if video == None and link == None:
            raise ValueError
        else:
            if video:
                video_format = video["formats"][0]
                self.url = video["webpage_url"]
                self.stream_url = video_format["url"]
                self.title = video["title"]
                self.duration = video["duration"]
            if link:
                try:
                    video = ytdl.extract_info(link, download=False)
                    video_format = video["formats"][0]
                    self.url = video["webpage_url"]
                    self.stream_url = video_format["url"]
                    self.title = video["title"]
                    self.duration = video["duration"]
                except Exception as e:
                    to_print = """Impossible de charger la vidéo
                        à cause des erreurs suivantes :\n"""
                    to_print += e.args[0][e.args[0].index(' '):]
                    msg = asyncio.run_coroutine_threadsafe(sendMsg(ctx,
                        str_to_send=to_print, title="Error", color=0x00ffb7), bot.loop)
                    raise e

class Music:
    def __init__(self, title, url, stream_url, duration):
        self.title = title
        self.url = url
        self.stream_url = stream_url
        self.duration = duration

class Playlist:
    def __init__(self, ctx, name, video_list, load=False):
        """ Init a playlist
        ctx: context from discord.py
        name: (str)
        video_list: (list) of Video object
        """
        if load == False:
            if isPlaylist(ctx, name) == True:
                asyncio.run_coroutine_threadsafe(sendMsg(ctx, 
                    f"Playlist {name} already exists.", "Playlist",
                    0x00ffb7), bot.loop)
                raise ValueError
            else:
                self.name = name
                self.author = ctx.author
                self.lenght = len(video_list)
                self.list = video_list
        else:
            self.name = name
            self.lenght = len(video_list)
            self.list = video_list
            asyncio.run_coroutine_threadsafe(sendMsg(ctx, 
                f"Playlist {name} created.", "Playlist",
                    0x00ffb7), bot.loop)
    @staticmethod
    def load(ctx):
        try:
            tree = etree.parse(f'commands/playlists/{ctx.guild}.xml')
        except:
            asyncio.run_coroutine_threadsafe(sendMsg(ctx,
                "No playlist to load from this server.",
                "Playlist", 0x00ffb7), bot.loop)
            return
        if ctx.guild not in playlists:
            playlists[ctx.guild] = []
        root = tree.getroot()
        for playlist in root:
            p_name = playlist.values()[0]
            music_list = []
            for music in playlist:
                elems = []
                for elem in music:
                    elems.append(elem.text)
                music_list.append(Music(elems[0], elems[1], elems[2],
                    elems[3]))
            playlists[ctx.guild].append(Playlist(p_name, music_list,
                load=True))
    def save(self, ctx):
        try:
            parser = etree.XMLParser(remove_blank_text=True)
            tree = etree.parse(f'commands/playlists/{ctx.guild}.xml', parser)
            root = tree.getroot()
            playlist = root.find(f"Playlist[@name='{self.name}']")
            if not playlist:
                playlist = etree.SubElement(root, "Playlist", name=f"{self.name}",
                lenght=f"{self.lenght}", author=f"{self.author}")
            existing_music = []
            for music in playlist:
                for elem in music:
                    if elem.tag == "title":
                        existing_music.append(elem.text)
        except:
            root = etree.Element("data")
            playlist = etree.SubElement(root, "Playlist", name=f"{self.name}",
                lenght=f"{self.lenght}", author=f"{self.author}")
        for music in self.list:
            if music.title not in existing_music:
                e = etree.Element("Music")
                etree.SubElement(e, "title").text = f"{music.title}"
                etree.SubElement(e, "url").text = f"{music.url}"
                etree.SubElement(e, "stream_url").text = f"{music.stream_url}"
                etree.SubElement(e, "duration").text = f"{music.duration}"
                playlist.append(e)
        tree = etree.ElementTree(element=root)
        tree.write("tests/playlists/864029702708264960.xml", pretty_print=True,
            xml_declaration=True, encoding="utf-8")
    def addMusic(self, ctx, name, video):
        if name not in self.playlist[ctx.guild]:
            asyncio.run_coroutine_threadsafe(sendMsg(ctx,
                "Specified playlist does not exist.",
                "Error", 0x00ffb7), bot.loop)
        else:
            if video.title not in self.playlist[ctx.guild][name]:
                self.playlist[ctx.guild][name][video.title] = [video.url,
                    video.stream_url, video.duration]
            else:
                asyncio.run_coroutine_threadsafe(sendMsg(ctx,
                    f"{video.title} is already in the playlist.",
                    "Error", 0x00ffb7), bot.loop)

def buildStrFromArgs(args):
    ''' Function used to transform a tab of str into one str with spaces.
        return: (str)
        args: (tab)[(str)]
    '''
    string = ""
    for mot in args:
        string += mot + " "
    return string

async def add_to_queue(ctx, selected):
    ''' Function used to add the selected music in the queue.
        selected: (dict) of the video from youtub_dl
    '''
    client = ctx.guild.voice_client
    title = selected['title']
    id = selected['id']
    url = 'https://www.youtube.com/watch?v=' + id
    to_print = f"**[{title}]({url})**"
    if client and client.channel: # if bot already connected to a channel
        video = Video(ctx, link=url)
        musics[ctx.guild].append(video)
        to_print += f"\n\n`Position in queue : {len(musics[ctx.guild])}`"
        msg = await sendMsg(ctx, str_to_send=to_print, title="Queued", color=0x00ffb7)
    else:
        try: # try to retrieve the channel of the author of the msg
            channel = ctx.author.voice.channel
        except:
            msg = await sendMsg(ctx, str_to_send="**You have to be connected to a channel to play music.**",
                title="Error", color=0x00ffb7)
            return
        video = Video(ctx, link=url)
        musics[ctx.guild] = []
        now_playing[ctx.guild] = [video]
        msg = await sendMsg(ctx, str_to_send=to_print, title="Now playing", color=0x00ffb7)
        try:
            client = await channel.connect()
            await play_song(client, musics[ctx.guild], video, [ctx, msg])
        except:
            msg = await sendMsg(ctx, str_to_send="**Unable to connect to the channel.**",
                title="Error", color=0x00ffb7)

async def Search(ctx, args, robot):
    ''' Function used to search musics with youtube_search.
        ctx: context from discord.py
        args: (list)[(str)]
        robot: (object) --> commands.Bot from bot.py
    '''
    search = buildStrFromArgs(args) # Parsing args
    nb_results = 20 # Define how many musics will be fetched from youtube_search api
    try: # Retrieving data
        yt = youtube_search.YoutubeSearch(search, max_results=nb_results).to_json()
        results = json.loads(yt)['videos']
    except:
        msg = await sendMsg(ctx, str_to_send="No results", title="Error", color=0x00ffb7)
        return
    i = 0
    def to_send(results, i):
        ''' Function to build a string from the data retrieved earlier.
            return: (str)
            results: (list) --> list of videos from json
            i: (int) --> starting index of the "results" list
        '''
        k = 1
        max = i+4
        to_print = "```\n"
        while i <= max and i < len(results):
            music = results[i]
            title = music['title']
            duration = music['duration']
            to_print += f"{k}. {title} ({duration})\n"
            i += 1
            k += 1
        to_print += "```"
        return to_print

    # Send first results
    msg = await sendMsg(ctx, str_to_send=to_send(results, i), title="Search", color=0x00ffb7)
    await addReactions(msg, ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '➡️']) # Add reactions to first msg
    # Handler of reaction events of first message
    def check1(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
            if reaction.emoji.name in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '➡️']:
                return reaction
    # Handler of reaction events of next messages
    def check2(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
            if reaction.emoji.name in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '⬅️', '➡️']:
                return reaction

    try:
        choice = await robot.wait_for("raw_reaction_add", check=check1, timeout=60) # Handling events
        choice = choice.emoji.name # retrieving emote
    # In case user does not react, handle TimeoutError and exit the function.
    except asyncio.TimeoutError:
        return
    dictio = { # Emote-to-value matching dictionary
                "1️⃣" : 1,
                "2️⃣" : 2,
                "3️⃣" : 3,
                "4️⃣" : 4,
                "5️⃣" : 5
            }
    start = 0

    async def next(msg, start, results, nb_results):
        ''' Function used to define what will be send when the RIGHT_ARROW emote is pressed,
            and which emote should be added.
            return: (discord.Message)
            msg: (discord.Message) --> old message
            start: (int) --> starting index of the results list
            results: (list) --> list of videos from json
            nb_results: (int) --> len(results)
        '''
        new_msg = await sendMsg(ctx, str_to_send=to_send(results, start),
            title="Search", color=0x00ffb7, old_msg=msg)
        k = 0
        i = start
        tab = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        emote_to_add = []
        while i < len(results) and k < len(tab):
            emote_to_add += [tab[k]]
            i += 1
            k += 1
        emote_to_add += ['⬅️']
        if start < nb_results-5:
            emote_to_add += ['➡️']
        await addReactions(new_msg, emote_to_add)
        return new_msg

    async def prev(msg, start, results):
        ''' Function used to define what will be send when the LEFT_ARROW emote is pressed,
            and which emote should be added.
            return: (discord.Message)
            msg: (discord.Message) --> old message
            start: (int) --> starting index of the results list
            results: (list) --> list of videos from json
        '''
        new_msg = await sendMsg(ctx, str_to_send=to_send(results, start),
            title="Search", color=0x00ffb7, old_msg=msg)
        tab = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        if start > 4:
            tab += ['⬅️']
        tab += ['➡️']
        await addReactions(new_msg, tab)
        return new_msg

    async def decision(choice, start, msg, results, nb_results):
        ''' Function used to decide what to do according to the "choice" variable. 
            return: (discord.Message) --> actual msg,
                    (int) --> actual index of "results" list,
                    (bool) --> True if a music got added to the queue
            choice: (str) --> emote from the reaction of the user
            msg: (discord.Message) --> last message sent
            results: (list) --> list of videos from json
            nb_results: (int) --> len(results)
        '''
        added_to_queue = False
        if choice in dictio:
            nb = dictio[choice] - 1
            nb += start
            selected = results[nb]
            await add_to_queue(ctx, selected)
            added_to_queue = True
        elif choice == '➡️':
            if start < len(results):
                start += 5
                msg = await next(msg, start, results, nb_results)
        elif choice == '⬅️':
            if start >= 5:
                start -= 5
                msg = await prev(msg, start, results)
        return msg, start, added_to_queue
    
    # Choose what to do
    msg, start, added_to_queue = await decision(choice, start, msg, results, nb_results)
    # Continue this until user select a music to add to the queue
    while added_to_queue == False:
        try: # Handling events
            choice = await robot.wait_for("raw_reaction_add", check=check2, timeout=60)
            choice = choice.emoji.name # retreiving emote
        except asyncio.TimeoutError:
            return
        # Choose what to do
        msg, start, added_to_queue = await decision(choice, start, msg, results, nb_results)

async def Delete(ctx, nb):
    ''' Function used to delete a music from the queue.
        ctx: context from discord.py
        nb: (str) --> index of the music to delete
    '''
    nb = int(nb) # casting str to int
    if len(musics[ctx.guild]) >= nb:
        title = musics[ctx.guild][nb-1].title
        url = musics[ctx.guild][nb-1].url
        del musics[ctx.guild][nb-1]
        msg = await sendMsg(ctx, str_to_send=f"**[{title}]({url}) is deleted from the queue.**",
            title="Queue update", color=0x00ffb7)
    else:
        msg = await sendMsg(ctx, str_to_send="**There isn't as much musics in the queue or the queue is empty.**",
            title="Error", color=0x00ffb7)

async def Leave(ctx):
    ''' Function used to make the bot quit the audio channel. (Empty the queue at the same time)
        ctx: context from discord.py
    '''
    client = ctx.guild.voice_client
    if client:
        await client.disconnect()
        musics[ctx.guild] = []

async def Resume(ctx):
    ''' Function used to resume the music on the bot.
        ctx: context from discord.py
    '''
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()

async def Pause(ctx):
    ''' Function used to pause the music on the bot.
        ctx: context from discord.py
    '''
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()

async def Skip(ctx):
    ''' Function used to skip the music currently playing on the bot.
        ctx: context from discord.py
    '''
    client = ctx.guild.voice_client
    if client:
        client.stop()

async def Queue(ctx, robot):
    def getTime(duration):
        ''' Function used to transform a duration(int) in sec into a duration(str) like hh:mm:ss.
            return: (str)
            duration: (int)
        '''
        total_sec = duration
        h = (total_sec - (total_sec % 3600)) / 3600
        sec_min_h = (total_sec - h * 3600)
        min = (sec_min_h - (sec_min_h % 60)) / 60
        sec = sec_min_h - min * 60
        time = '{}:{}:{}'.format(int(h), str(
            min/10).replace('.', ''), int(sec))
        return time

    # Check if the bot is connected to a vocal channel
    client = ctx.guild.voice_client
    pages = [] # if the queue is split into pages, each page will be inside this list
    def check(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
            if reaction.emoji.name in ['⬅️', '➡️']:
                return reaction

    if client: # if connected
        # retrieve duration in desired format
        time = getTime(now_playing[ctx.guild][0].duration)
        # starting to build the string to send
        to_print = "```\n" + f"Now playing:\n\t{now_playing[ctx.guild][0].title} ({time})\n\n"
        i = 1
        queue = musics[ctx.guild]
        to_print += f"Total queued: {len(queue)} song(s)\n\n"
        if len(queue) > 10: # if queue is too long
            y = 1
            actual_page = to_print
            for music in queue:
                time = getTime(music.duration) # retrieve duration
                actual_page += f"{i}. {music.title} ({time})\n" # build string to send
                if y == 10 or music == queue[-1]: # each 10 music, or at the end of the queue, we end the page
                    actual_page += "```" # ending actual page
                    pages += [actual_page] # adding the page to the list of pages
                    actual_page = "```\n" # starting a new page
                    y = 1
                else:
                    y += 1
                i += 1
            i = 0
            nb_page = 1
            msg = await sendMsg(ctx, str_to_send=pages[i],
                title=f"Queue (Page {nb_page})", color=0x00ffb7)
            while True:
                old = msg
                msg = await sendMsg(ctx, str_to_send=pages[i],
                    title=f"Queue (Page {nb_page})", color=0x00ffb7,
                    old_msg=old)
                if nb_page > 1 and nb_page < len(pages):
                    emotes = ['⬅️', '➡️']
                elif nb_page >= len(pages):
                    emotes = ['⬅️']
                else:
                    emotes = ['➡️']
                await addReactions(msg, emotes)
                try: # handling events
                    react = await robot.wait_for("raw_reaction_add", check=check, timeout=60)
                except asyncio.TimeoutError:
                    return # exit the function if user stop reacting
                emoji = react.emoji.name
                if emoji == '⬅️':
                    nb_page -= 1
                    i -= 1
                if emoji == '➡️':
                    nb_page += 1
                    i += 1
        else: # if queue isn't too loong
            for music in queue:
                time = getTime(music.duration) # retrieve duration
                to_print += f"{i}. {music.title} ({time})\n" # build string to send
                i += 1
            to_print += "```" # end of the string
            msg = await sendMsg(ctx, str_to_send=to_print, title="Music(s) in queue :",
                color=0x00ffb7)
    else: # if bot not connected
        msg = await sendMsg(ctx, str_to_send="**Bot should be connected to your channel to print the queue.**",
            title="Error", color=0x00ffb7)

async def play_song(client, queue, song, tab_ctx):
    ''' Function used to play a music on the bot.
        client: (ctx.author.voice.channel.connect())
        queue: (list) --> list of musics from youtube_dl
        song: ((class)Video) --> Video object
        tab_ctx: (list)[ctx, old_msg]
    '''
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url,
        before_options= "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"))
    ctx = tab_ctx[0]
    msg = await sendMsg(ctx, str_to_send=f"**[{song.title}]({song.url})**",
        title="Now playing", color=0x00ffb7, old_msg=tab_ctx[1])

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            now_playing[ctx.guild] = [queue[0]]
            del queue[0]
            asyncio.run_coroutine_threadsafe(play_song(client, queue, new_song, [ctx, msg]), bot.loop)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)
    try:
        client.play(source, after=next)
    except:
        pass

async def playlist(ctx, url):
    ''' Function used to add a playlist to the queue.
        ctx: context from discord.py
        url: (str) --> link of a youtube playlist
    '''
    client = ctx.guild.voice_client
    status = await sendMsg(ctx, "***downloading playlist...***",
        "Status", 0x00ffb7)
    playlist = ytdl.extract_info(url, download=False)
    if client and client.channel: # if bot connected
        for video in playlist['entries']: # for each music of the playlist
            to_append = Video(ctx, video=video)
            musics[ctx.guild].append(to_append) # add each music of the playlist inside the queue
        msg = await sendMsg(ctx, f"**[{playlist['title']}]({playlist['webpage_url']})**",
            "Playlist queued", 0x00ffb7, status)
    else: # if bot not connected
        try: # try to connect
            channel = ctx.author.voice.channel
        except: # if error
            msg = await sendMsg(ctx, str_to_send="***You must join a channel for that !***",
                old_msg=status)
            return
        musics[ctx.guild] = [] # creating the queue
        now_playing[ctx.guild] = [] # creating now playing
        i = 0
        for video in playlist['entries']: # for each video of the playlist
            if i == 0:
                to_play = Video(ctx, video=video)
                now_playing[ctx.guild] = [to_play] # currently playing music is stored in there
            else:
                to_append = Video(ctx, video=video)
                musics[ctx.guild].append(to_append) # add each music to queue
            i+=1
        try: # try to connect to the channel of the user
            client = await channel.connect()
        except: # if error
            msg = await sendMsg(ctx, "**Unable to connect to voice channel**",
                "Error", 0x00ffb7)
            return
        msg = await sendMsg(ctx, f"**[{playlist['title']}]({playlist['webpage_url']})**",
            "Now playing playlist", 0x00ffb7)
        tab_ctx = [ctx, msg]
        # start to play the song
        await play_song(client, musics[ctx.guild], to_play, tab_ctx)

async def Play(ctx, args):
    client = ctx.guild.voice_client
    search = ""
    for mot in args:
        search += mot + " "
    if "https://youtube.com/playlist" in search:
        await playlist(ctx, search)
        return
    elif "https://" in search:
        url = search
    else:
        try:
            yt = youtube_search.YoutubeSearch(search, max_results=1).to_json()
        except Exception as e:
            to_print = "Impossible de charger la vidéo à cause des erreurs suivantes :\n"
            to_print += e.args[0][e.args[0].index(' '):]
            msg = await sendMsg(ctx, to_print, "Error", 0x00ffb7)
            return
        try:
            yt_id = str(json.loads(yt)['videos'][0]['id'])
            url = 'https://www.youtube.com/watch?v=' + yt_id
        except:
            msg = await sendMsg(ctx, "No results", "Error", 0x00ffb7)
            return
    if client and client.channel:
        video = Video(ctx, url)
        musics[ctx.guild].append(video)
        msg = await sendMsg(ctx, f"**[{video.title}]({video.url})**\n\n`Position in queue : {len(musics[ctx.guild])}`",
            "Queued", 0x00ffb7)
    else:
        try:
            video = Video(ctx, url)
        except:
            return
        try:
            channel = ctx.author.voice.channel
        except:
            msg = await sendMsg(ctx, "***You must be connected to a channel to do that.***",
                "Error", 0x00ffb7)
            return
        musics[ctx.guild] = []
        now_playing[ctx.guild] = [video]
        client = await channel.connect()
        msg = await sendMsg(ctx, f"**[{video.title}]({video.url})**",
            "Now playing", 0x00ffb7)
        await play_song(client, musics[ctx.guild], video, [ctx, msg])


async def Playtop(ctx, args):
    client = ctx.guild.voice_client
    search = ""
    for mot in args:
        search += mot + " "
    if "https://" in search:
        url = search
    else:
        try:
            yt = youtube_search.YoutubeSearch(search, max_results=1).to_json()
        except Exception as e:
            to_print = "Impossible de charger la vidéo à cause des erreurs suivantes :\n"
            to_print += e.args[0][e.args[0].index(' '):]
            msg = await sendMsg(ctx, to_print, "Error", 0x00ffb7)
            return
        try:
            yt_id = str(json.loads(yt)['videos'][0]['id'])
            url = 'https://www.youtube.com/watch?v=' + yt_id
        except:
            msg = await sendMsg(ctx, "No results", "Error", 0x00ffb7)
            return
    if client and client.channel:
        try:
            video = Video(url, ctx)
        except:
            return
        musics[ctx.guild].insert(0, video)
        msg = await sendMsg(ctx, f"**[{video.title}]({video.url})**",
            "Queued", 0x00ffb7)
    else:
        try:
            video = Video(url, ctx)
        except:
            return
        try:
            channel = ctx.author.voice.channel
        except:
            msg = await sendMsg(ctx, "***You must be connected to a channel to do that.***",
                "Error", 0x00ffb7)
            return
        musics[ctx.guild] = []
        client = await channel.connect()
        msg = await sendMsg(ctx, f"**[{video.title}]({video.url})**",
            "Now playing", 0x00ffb7)
        await play_song(client, musics[ctx.guild], video, [ctx, msg])
