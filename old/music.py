import discord
from discord.ext import commands
import asyncio
import json
import youtube_dl
import youtube_search

musics = {}  # musics from each guild will be stored here.
now_playing = {} # music actually playing will be stored here
ytdl_opts = {  # Youtube-dl options to improve the quality
    'format': 'bestaudio/best',
    'quiet': True,
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',
        'preferredquality': '192'
    }]
}
ytdl = youtube_dl.YoutubeDL(ytdl_opts)

bot = commands.Bot(command_prefix=">",
                   case_insensitive=True, help_command=None)


class Video:
    def __init__(self, link):
        video = ytdl.extract_info(link, download=False)
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]
        self.title = video["title"]
        self.duration = video["duration"]


class VideoFromPlaylist:
    def __init__(self, video):
        video_format = video["formats"][0]
        self.url = video["webpage_url"]
        self.stream_url = video_format["url"]
        self.title = video["title"]
        self.duration = video["duration"]


async def Search(ctx, args, robot):
    search = ""
    for mot in args:
        search += mot + " "
    nb_results = 20
    yt = youtube_search.YoutubeSearch(search, max_results=nb_results).to_json()
    try:
        results = json.loads(yt)['videos']
    except:
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Error', value=f"No results", inline=False)
        await ctx.send(embed=embed)
    i = 0

    def to_send(results, i):
        k = 1
        max = i+4
        to_print = "```\n"
        while i <= max and i < len(results):
            music = results[i-1]
            title = music['title']
            duration = music['duration']
            to_print += f"{k}. {title} ({duration})\n"
            i += 1
            k += 1
        to_print += "```"
        return to_print

    to_print = to_send(results, i)
    embed = discord.Embed(color=0x00ffb7)
    embed.add_field(name='Search', value=to_print, inline=False)
    msg = await ctx.send(embed=embed)

    await msg.add_reaction('1️⃣')
    await msg.add_reaction('2️⃣')
    await msg.add_reaction('3️⃣')
    await msg.add_reaction('4️⃣')
    await msg.add_reaction('5️⃣')
    await msg.add_reaction('➡️')

    def check1(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
            if reaction.emoji.name == '1️⃣' or '2️⃣' or '3️⃣' or '4️⃣' or '5️⃣' or '➡️':
                return reaction

    def check2(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
            if reaction.emoji.name == '1️⃣' or '2️⃣' or '3️⃣' or '4️⃣' or '5️⃣' or '⬅️' or '➡️':
                return reaction

    try:
        choice = await robot.wait_for("raw_reaction_add", check=check1, timeout=60)
        choice = choice.emoji.name
    except asyncio.TimeoutError:
        return
    dictio = {
        "1️⃣": 1,
        "2️⃣": 2,
        "3️⃣": 3,
        "4️⃣": 4,
        "5️⃣": 5
    }
    start = 0

    async def add_to_queue(selected):
        client = ctx.guild.voice_client
        title = selected['title']
        id = selected['id']
        url = 'https://www.youtube.com/watch?v=' + id
        to_print = f"**[{title}]({url})**"
        if client and client.channel:
            video = Video(url)
            musics[ctx.guild].append(video)
            embed = discord.Embed(color=0x00ffb7)
            embed.add_field(name='Queued', value=to_print, inline=False)
            await ctx.send(embed=embed)
        else:
            try:
                channel = ctx.author.voice.channel
            except:
                embed = discord.Embed(color=0x00ffb7)
                embed.add_field(
                    name='Error', value="**Please connect to a channel to play musique.**", inline=False)
                await ctx.send(embed=embed)
                return
            video = Video(url)
            musics[ctx.guild] = []
            client = await channel.connect()

    async def next(msg, start):
        i = start
        await msg.delete()
        to_print = to_send(results, i)
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Search', value=to_print, inline=False)
        msg = await ctx.send(embed=embed)
        k = 0
        j = start
        tab = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
        while j < len(results) and k < len(tab):
            await msg.add_reaction(tab[k])
            j += 1
            k += 1
        await msg.add_reaction('⬅️')
        if start < nb_results-5:
            await msg.add_reaction('➡️')
        return msg

    async def prev(msg, start):
        i = start
        await msg.delete()
        to_print = to_send(results, i)
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Search', value=to_print, inline=False)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('1️⃣')
        await msg.add_reaction('2️⃣')
        await msg.add_reaction('3️⃣')
        await msg.add_reaction('4️⃣')
        await msg.add_reaction('5️⃣')
        if start > 4:
            await msg.add_reaction('⬅️')
        await msg.add_reaction('➡️')
        return msg

    async def decision(choice, start, msg):
        added_to_queue = False
        if choice in dictio:
            nb = dictio[choice]
            nb += start
            selected = results[nb]
            await add_to_queue(selected)
            added_to_queue = True
        elif choice == '➡️':
            if start <= len(results):
                start += 5
                msg = await next(msg, start)
        elif choice == '⬅️':
            if start >= 5:
                start -= 5
                msg = await prev(msg, start)
        return msg, start, added_to_queue

    msg, start, added_to_queue = await decision(choice, start, msg)
    while added_to_queue == False:
        try:
            choice = await robot.wait_for("raw_reaction_add", check=check2, timeout=60)
            choice = choice.emoji.name
        except asyncio.TimeoutError:
            return
        msg, start, added_to_queue = await decision(choice, start, msg)


async def Delete(ctx, nb):
    nb = int(nb)
    if len(musics[ctx.guild]) >= nb:
        title = musics[ctx.guild][nb-1].title
        url = musics[ctx.guild][nb-1].url
        del musics[ctx.guild][nb-1]
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(
            name='Queue update', value=f"**[{title}]({url}) is deleted from the queue.**", inline=False)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(
            name='Error', value="**There isn't that many musics in queue or the queue is empty.**", inline=False)
        await ctx.send(embed=embed)


async def Leave(ctx):
    client = ctx.guild.voice_client
    if client:
        await client.disconnect()
        musics[ctx.guild] = []


async def Resume(ctx):
    client = ctx.guild.voice_client
    if client.is_paused():
        client.resume()


async def Pause(ctx):
    client = ctx.guild.voice_client
    if not client.is_paused():
        client.pause()


async def Skip(ctx):
    client = ctx.guild.voice_client
    if client:
        client.stop()


async def Queue(ctx, robot):
    def getTime(duration):
        total_sec = duration
        h = (total_sec - (total_sec % 3600)) / 3600
        sec_min_h = (total_sec - h * 3600)
        min = (sec_min_h - (sec_min_h % 60)) / 60
        sec = sec_min_h - min * 60
        time = '{}:{}:{}'.format(int(h), str(
            min/10).replace('.', ''), int(sec))
        return time

    client = ctx.guild.voice_client
    msg = ""
    def check(reaction):
        if reaction.user_id == ctx.author.id and msg.id == reaction.message_id:
            if reaction.emoji.name == '⬅️' or '➡️':
                return reaction
    if client:
        time = getTime(now_playing[ctx.guild][0].duration)
        to_print = "```\n" + f"Now playing:\n\t{now_playing[ctx.guild][0].title} ({time})\n\n"
        i = 1
        queue = musics[ctx.guild]
        to_print += f"Total queued: {len(queue)} song(s)\n\n"
        if len(queue) > 10:
            index = 0
            y = 0
            page = 1
            while queue[index] != queue[-1]:
                if y > 9:
                    to_print += "```"
                    embed=discord.Embed(color=0x00ffb7)
                    embed.add_field(name=f'Queue (Page {page})', value=to_print, inline=False)
                    msg = await ctx.send(embed=embed)
                    if page > 1:
                        await msg.add_reaction('⬅️')
                    await msg.add_reaction('➡️')
                    y = 0
                    page += 1
                    try:
                        react = await robot.wait_for("raw_reaction_add", check=check, timeout=60)
                    except asyncio.TimeoutError:
                        return
                    emote = react.emoji.name
                    if emote == '⬅️':
                        page -= 1
                        index -= 10
                        i -= 10
                        to_print = "```\n"
                    if emote == '➡️':
                        index += 1
                        to_print = "```\n"
                else:
                    time = getTime(queue[index].duration)
                    to_print += f"{i}. {queue[index].title} ({time})\n"
                    y += 1
                    i += 1
                    index += 1
        else:
            for music in queue:
                time = getTime(music.duration)
                to_print += f"{i}. {music.title} ({time})\n"
                i += 1
            to_print += "```"
            embed=discord.Embed(color=0x00ffb7)
            embed.add_field(name='Music(s) in queue :', value=to_print, inline=False)
            await ctx.send(embed=embed)
    else:
        embed=discord.Embed(color=0x00ffb7)
        to_print = "**Bot not connected**"
        embed.add_field(name='Error', value=to_print, inline=False)
        await ctx.send(embed=embed)


async def play_song(client, queue, song, tab_ctx):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url,
                                                                 before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", executable='ffmpeg/bin/ffmpeg.exe'))

    embed = discord.Embed(color=0x00ffb7)
    embed.add_field(name='Now playing',
                    value=f"**[{song.title}]({song.url})**", inline=False)
    ctx = tab_ctx[0]
    msg = tab_ctx[1]
    await msg.delete()
    msg = await ctx.send(embed=embed)

    def next(_):
        if len(queue) > 0:
            new_song = queue[0]
            del queue[0]
            asyncio.run_coroutine_threadsafe(
                play_song(client, queue, new_song, [ctx, msg]), bot.loop)
        else:
            asyncio.run_coroutine_threadsafe(client.disconnect(), bot.loop)
    try:
        client.play(source, after=next)
    except:
        pass


async def playlist(ctx, url):
    client = ctx.guild.voice_client
    playlist = ytdl.extract_info(url, download=False)
    if client and client.channel:
        for video in playlist['entries']:
            to_append = VideoFromPlaylist(video)
            musics[ctx.guild].append(to_append)
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Playlist queued',
                        value=f"**[{playlist['title']}]({playlist['webpage_url']})**", inline=False)
        await ctx.send(embed=embed)
    else:
        channel = ctx.author.voice.channel
        musics[ctx.guild] = []
        i = 0
        for video in playlist['entries']:
            if i == 0:
                to_play = VideoFromPlaylist(video)
            else:
                to_append = VideoFromPlaylist(video)
                musics[ctx.guild].append(to_append)
            i += 1
        client = await channel.connect()
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Now playing playlist', value=f"**[{playlist['title']}]({playlist['webpage_url']})**",
                        inline=False)
        msg = await ctx.send(embed=embed)
        tab_ctx = [ctx, msg]
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
        yt = youtube_search.YoutubeSearch(search, max_results=1).to_json()
        try:
            yt_id = str(json.loads(yt)['videos'][0]['id'])
            url = 'https://www.youtube.com/watch?v=' + yt_id
        except:
            embed = discord.Embed(color=0x00ffb7)
            embed.add_field(name='Error', value=f"No results", inline=False)
            await ctx.send(embed=embed)
    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].append(video)
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(
            name='Queued', value=f"**[{video.title}]({video.url})**", inline=False)
        await ctx.send(embed=embed)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Now playing',
                        value=f"**[{video.title}]({video.url})**", inline=False)
        msg = await ctx.send(embed=embed)
        await play_song(client, musics[ctx.guild], video, [ctx, msg])


async def Playtop(ctx, args):
    client = ctx.guild.voice_client
    search = ""
    for mot in args:
        search += mot + " "
    if "https://" in search:
        url = search
    else:
        yt = youtube_search.YoutubeSearch(search, max_results=1).to_json()
        try:
            yt_id = str(json.loads(yt)['videos'][0]['id'])
            url = 'https://www.youtube.com/watch?v=' + yt_id
        except:
            embed = discord.Embed(color=0x00ffb7)
            embed.add_field(name='Error', value=f"No results", inline=False)
            await ctx.send(embed=embed)
    if client and client.channel:
        video = Video(url)
        musics[ctx.guild].insert(0, video)
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(
            name='Queued', value=f"**[{video.title}]({video.url})**", inline=False)
        await ctx.send(embed=embed)
    else:
        channel = ctx.author.voice.channel
        video = Video(url)
        musics[ctx.guild] = []
        client = await channel.connect()
        embed = discord.Embed(color=0x00ffb7)
        embed.add_field(name='Now playing',
                        value=f"**[{video.title}]({video.url})**", inline=False)
        msg = await ctx.send(embed=embed)
        await play_song(client, musics[ctx.guild], video, [ctx, msg])
