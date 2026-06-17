import discord
import os
import yt_dlp
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
import shutil
import random
import glob
import math
from tinytag import TinyTag
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from collections import deque
import asyncio

ytdl = yt_dlp.YoutubeDL({
    "format": "bestaudio/best",
    "quiet": True,
})

class DJEdward:
    def __init__(self):
        self.queue = deque()
        self.current = None

class Ljuduppspelning(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    def get_player(self, server_id):
        if server_id not in self.players:
            self.players[server_id] = DJEdward()
        return self.players[server_id]
    
    async def get_song(self, query):
        def extract():
            if query.startswith("http"):
                return ytdl.extract_info(
                    query,
                    download=False
                )
            results = ytdl.extract_info(
                f"ytsearch1:{query}",
                download=False
            )
            return results["entries"][0]
        return await asyncio.to_thread(extract)
    
    async def play_next(self, ctx):
        player = self.get_player(ctx.guild.id)
        if not player.queue:
            await ctx.send("Queue is empty.")
            return
        song = player.queue.popleft()
        player.current = song
        voice = ctx.voice_client
        if voice is None:
            voice = await ctx.author.voice.channel.connect()
        source = await discord.FFmpegOpusAudio.from_probe(
            song["url"],
            options="-vn"
        )
        def after_playing(error):
            future = self.play_next(ctx)
            asyncio.run_coroutine_threadsafe(
                future,
                self.bot.loop
            )
        voice.play(source, after=after_playing)
        await ctx.send(
            f"🎵 Now playing: {song['title']}"
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ljud Redo')

    @commands.command(pass_context = True)
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("Du är inte i en röstkanal")
        voice = await channel.connect()

    @commands.command(pass_context = True)
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("Jag är inte i en röstkanal")

    @commands.command()
    async def play(self, ctx, *, query):
        player = self.get_player(ctx.guild.id)
        song = await self.get_song(query)
        player.queue.append(song)
        embed=discord.Embed(title="Lade till en video i kön", description='')
        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
        embed.add_field(name='Video', value="[{}]({})".format(song['title'],song['webpage_url']), inline=True)
        embed.add_field(name='Längd', value='{}:{}'.format(math.floor(int(song['duration'])/60),int(song['duration'])%60), inline=True)
        await ctx.send(embed=embed)

    @commands.command(pass_context = True)
    async def playtop(self, ctx, *, song: str = None):

    @commands.command(pass_context = True)
    async def playlist(self, ctx, url, index=1):

    @commands.command(pass_context = True)
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.pause()

    @commands.command(pass_context = True)
    async def skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()

    @commands.command(pass_context = True)
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.resume()

    @commands.command(pass_context = True)
    async def clear(self,ctx):

    @commands.command(pass_context = True)
    async def move(self, ctx, från, till):

    @commands.command(pass_context = True)
    async def remove(self, ctx, nummer):


    @commands.command()
    async def ljudtest(self,ctx):
        audio = MP3("C:/Users/stenb/OneDrive/Dokument/Bot/songs/stp.mp3")
        await ctx.send(audio.info.bitrate)

    @commands.command(aliases=['q'])
    async def queue(self,ctx,sida=1):
        queuen = glob.glob("queue/*.m4a")
        embed=discord.Embed(title="Uppspelningskö:")
        queuenummer = (sida-1)*10
        #print(queuen)
        tid_tot = 0
        for file in queuen:
            file=TinyTag.get(file)
            tid_tot+=file.duration
        for file in queuen[(sida-1)*10:(sida*10)]:
                file=TinyTag.get(file)
                titel="[{}]({})".format(file.title,file.comment)
                lenght = '{}:{}'.format(math.floor(int(file.duration)/60),int(file.duration)%60)
                if queuenummer==0:
                    embed.add_field(name='\u200b', value="Spelas nu: {} | {}".format(titel,lenght), inline=False)
                    queuenummer+=1
                else:
                    embed.add_field(name='\u200b', value="{}. {} | {}".format(queuenummer,titel,lenght), inline=False)
                    queuenummer+=1
        embed.add_field(name='\u200b', value="Det finns {} låtar i kön. Total längd: {}:{}".format(len(queuen)-1,math.floor(tid_tot/60),math.floor(tid_tot%60)), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def gachi(self,ctx, reset = None):
        if reset == "reset":
            source = "gachi/spelad/"
            dest = "gachi/"
            files = os.listdir(source)
            for f in files:
                shutil.move(source+f, dest)
            await ctx.send("Resetadde gachi")
        else:
            def gachi_loop():
                gachi = glob.glob("gachi/*.m4a")
                if not gachi == []:
                    r = random.choice(gachi)
                    voice.play(discord.FFmpegPCMAudio(r), after = lambda e: (shutil.move(r, "gachi/spelad/"), gachi_loop()))
                    print("{} spelas".format(r))
            voice = get(self.bot.voice_clients, guild = ctx.guild)
            if not voice:
                 channel = ctx.message.author.voice.channel
                 voice = await channel.connect()
            gachi_loop()

    @commands.command(pass_context = True)
    async def tomtemor(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\tomtemor.mp3"))
        voice.is_playing()

    @commands.command(pass_context = True)
    async def howard(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\howard.mp3"))
        voice.is_playing()

    @commands.command(pass_context = True)
    async def fanndis(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\fanndis.mp3"))
        voice.is_playing()

    @commands.command(pass_context = True)
    async def stp(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\stp.mp3"))
        voice.is_playing()

    @commands.command(pass_context = True)
    async def anis(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\anis.mp3"))
        voice.is_playing()

    @commands.command(pass_context = True)
    async def shopping(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\shopping.mp3"))
        voice.is_playing()

def setup(bot):
    bot.add_cog(Ljuduppspelning(bot))
