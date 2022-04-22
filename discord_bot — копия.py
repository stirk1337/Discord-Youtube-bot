import discord
from discord.ext import commands
from discord.utils import get
import json
import random
import youtube_dl
from requests import get
from youtube_search import YoutubeSearch

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@commands.cooldown(1, 3, commands.BucketType.user)

@bot.command()
async def mycredit(ctx):
    user = ctx.message.author.id
    with open("info.json") as f:
            file = json.load(f)
    credit = 0
    if(str(user) in file['users']):
        credit = file['users'][str(user)]
    
    #your emoji list, you need to has plus15 and minus15 emojis, for social credit function work!
    emojis = []


    emoji = discord.utils.get(bot.emojis, name=random.choice(emojis))

    channel = bot.get_channel("")
    await channel.send("<@" + str(user) + ">" + ", у Вас " + str(credit) + " Social Credit " + str(emoji))

@bot.command()
async def join(ctx):
    if ctx.author.voice is None:
        await ctx.send("Вы не в голосовом канале!")
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
    else:
        await ctx.voice_client.move_to(voice_channel)

@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()

@bot.command()
async def stop(ctx):
    vc = ctx.voice_client
    vc.stop()

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
    ctx.voice_client.stop()
    ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}
    YDL_OPTIONS = {'format':"bestaudio", 'noplaylist':'True'}
    vc = ctx.voice_client

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(url)
        except:
            results = YoutubeSearch(url, max_results=1).to_dict()
            url = "https://www.youtube.com" + results[0]['url_suffix']
            info = ydl.extract_info(url, download = False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
            vc.play(source)
            channel = bot.get_channel("")
            await channel.send(url)
        else:
            info = ydl.extract_info(url, download = False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **ffmpeg_options)
            vc.play(source)

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


            channel = bot.get_channel("")
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

            channel = bot.get_channel("")

            emoji = discord.utils.get(bot.emojis, name='minus15')
            await channel.send("<@" + str(message.author.id) + ">" + " получил -15 Social Credit! " + str(emoji))

bot.run("token")