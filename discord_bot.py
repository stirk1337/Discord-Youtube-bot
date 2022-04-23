import asyncio
from table2ascii import table2ascii as t2a, PresetStyle
import discord
from discord.ext import commands
from discord.utils import get
import json
import random
import youtube_dl
from requests import get
from youtube_search import YoutubeSearch

print('Я запустился')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

queue = []
is_skip = False

token = ""
channel_id = 0
emojis = []  # your emoji list, you need to has plus15 and minus15 emojis, for social credit function work!

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
YDL_OPTIONS = {'format': "bestaudio", 'noplaylist': 'True'}


@commands.cooldown(1, 3, commands.BucketType.user)
@bot.command()
async def mycredit(ctx):
    user = ctx.message.author.id
    with open("info.json") as f:
        file = json.load(f)
    credit = 0
    if str(user) in file['users']:
        credit = file['users'][str(user)]
    emoji = discord.utils.get(bot.emojis, name=random.choice(emojis))

    channel = bot.get_channel(channel_id)
    await channel.send("<@" + str(user) + ">" + ", у Вас " + str(credit) + " Social Credit " + str(emoji))


@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()


@bot.command()
async def play(ctx, *urls):
    if ctx.author.voice is None:
        await ctx.send("Вы не в голосовом канале!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

    url = ' '.join(urls)
    if len(url) == 0:
        return

    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(url)
        except:
            results = YoutubeSearch(url, max_results=1)
            results = results.to_dict()
            url = "https://www.youtube.com" + results[0]['url_suffix']
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            duration = info['duration']
            title = info['title']
            author = ctx.author
            queue.append([url, url2, duration, title, author])
            channel = bot.get_channel(channel_id)
            print(author)
            await channel.send("Добавлено в очередь: " + title)
            if not playingaudio(ctx):
                q = queue.pop(0)
                await true_play(q[0], q[1], q[2], q[3], q[4], vc)

        else:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            duration = info['duration']
            title = info['title']
            author = ctx.author
            queue.append([url, url2, duration, title, author])
            channel = bot.get_channel(channel_id)
            await channel.send("Добавлено в очередь: " + title)
            if not playingaudio(ctx):
                q = queue.pop(0)
                await true_play(q[0], q[1], q[2], q[3], q[4], vc)
                await slip(duration, vc)

async def slip(duration, vc):
    global is_skip
    await asyncio.sleep(duration)
    if not is_skip:
        q = queue.pop(0)
        is_skip = False
        await true_play(q[0], q[1], q[2], q[3], q[4], vc)

@bot.command()
async def skip(ctx):
    global is_skip
    is_skip = True
    vc = ctx.voice_client
    vc.stop()
    q = queue.pop(0)
    await true_play(q[0], q[1], q[2], q[3], q[4], vc)

@bot.command()
async def list(ctx):
    table = []
    i = 1
    for q in queue:
        time = str(q[2]//60) + ":" + str(q[2]%60)
        table.append([i, q[3], time, q[4]])
        i+=1
    output = t2a(
        header=["Номер", "Название", "Продолжительность", "Поставил"],
        body=table,
        style=PresetStyle.thin_compact
    )
    channel = bot.get_channel(channel_id)
    await channel.send(f"```\n{output}\n```")


@bot.command()
async def remove(ctx, number):
    q = queue.pop(int(number)-1)
    channel = bot.get_channel(channel_id)
    await channel.send("Удалено из очереди: " + str(q[3]))

async def true_play(url, url2, duration, title, author,  vc):
    source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
    channel = bot.get_channel(channel_id)
    vc.play(source)
    await channel.send("Сейчас играет: " + title + "\n"+url)



def playingaudio(ctx):
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
    return voice_client.is_playing()


@bot.event
async def on_raw_reaction_add(payload):
    aidi = payload.channel_id
    if payload.channel_id > 0:
        channel = bot.get_channel(aidi)
        message = await channel.fetch_message(payload.message_id)
        reaction = discord.utils.get(message.reactions, emoji=payload.emoji)

        with open("info.json") as f:
            file = json.load(f)

        if payload.emoji.name == 'plus15' and reaction.count > 2 and message.id not in file['messages']:

            file['messages'].append(message.id)
            if str(message.author.id) in file['users']:
                file['users'][str(message.author.id)] += 15
            else:
                file['users'][str(message.author.id)] = 15

            with open('info.json', 'w') as f:
                f.write(json.dumps(file))

            channel = bot.get_channel(channel_id)
            emoji = discord.utils.get(bot.emojis, name='plus15')

            await channel.send("<@" + str(message.author.id) + ">" + " получил +15 Social Credit! " + str(emoji))

        if payload.emoji.name == 'minus15' and reaction.count > 2 and message.id not in file['messages']:

            file['messages'].append(message.id)
            if str(message.author.id) in file['users']:
                file['users'][str(message.author.id)] -= 15
            else:
                file['users'][str(message.author.id)] = -15

            with open('info.json', 'w') as f:
                f.write(json.dumps(file))

            channel = bot.get_channel(channel_id)

            emoji = discord.utils.get(bot.emojis, name='minus15')
            await channel.send("<@" + str(message.author.id) + ">" + " получил -15 Social Credit! " + str(emoji))


bot.run(token)
