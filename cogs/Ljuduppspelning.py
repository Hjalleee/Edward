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
ytdl_pl = yt_dlp.YoutubeDL({
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
})
ytdl_flat = yt_dlp.YoutubeDL({
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": True
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
    
    async def play_command(self, ctx, query, is_play_top = False):
        voice = ctx.voice_client
        if voice is None:
            if not ctx.author.voice:
                await ctx.send("Du är inte i en röstkanal")
                return
            else:
                voice = await ctx.author.voice.channel.connect()

        player = self.get_player(ctx.guild.id)
        result = await self.get_song(query)
        if result.get("_type") == 'playlist':
            count = 0
            for entry in result["entries"]:
                if entry is None:
                    continue
                if is_play_top:
                    player.queue.appendleft(entry)
                else:
                    player.queue.append(entry)
                count += 1
            if is_play_top:
                embed=discord.Embed(title="Lade till en spellista först i kön", description='')
            else:
                embed=discord.Embed(title="Lade till en spellista i kön", description='')
            embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
            embed.add_field(name='Video', value=f"[{result['title']}]({result['webpage_url']})", inline=True)
            embed.add_field(name='Längd', value=f'{count} videos', inline=True)
            await ctx.send(embed=embed)            
        else:
            if not 'duration' in result:
                    result = await self.get_song(result['uploader_url'])
            if is_play_top:
                player.queue.appendleft(result)
            else:
                player.queue.append(result)
            if is_play_top:
                embed=discord.Embed(title="Lade till en video först i kön", description='')
            else:
                embed=discord.Embed(title="Lade till en video i kön", description='')
            embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
            embed.add_field(name='Video', value=f"[{result['title']}]({result['url']})", inline=True)
            embed.add_field(name='Längd', value=f"{math.floor(int(result['duration'])/60)}:{int(result['duration'])%60:02}", inline=True)
            await ctx.send(embed=embed)
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            await self.play_next(ctx)
    
    async def get_song(self, query):
        def extract():
            if 'list=' in query:
                return ytdl_pl.extract_info(query, download=False)
            elif query.startswith("http") and '@' not in query and '/channel/' not in query:
                return ytdl_flat.extract_info(query, download=False)
            else:
                return ytdl_flat.extract_info(f"ytsearch1:{query}", download=False)["entries"][0]
        return await asyncio.to_thread(extract)
    
    async def play_next(self, ctx):
        player = self.get_player(ctx.guild.id)
        if not player.queue:
            await ctx.send("Kön är tom 😔")
            return
        song = player.queue.popleft()
        player.current = song
        voice = ctx.voice_client
        if voice is None:
            if not ctx.author.voice:
                await ctx.send("Du är inte i en röstkanal")
                return
            else:
                voice = await ctx.author.voice.channel.connect()

        info = await asyncio.to_thread(
            lambda: ytdl.extract_info(song["url"], download=False))
        
        source = discord.FFmpegPCMAudio(
            info["url"],
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn"
        )
        def after_playing(error):
            future = self.play_next(ctx)
            asyncio.run_coroutine_threadsafe(
                future,
                self.bot.loop
            )
        embed=discord.Embed(title="Började spela en låt", description='')
        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
        embed.add_field(name='Video', value=f"[{song['title']}]({song['url']})", inline=True)
        embed.add_field(name='Längd', value=f"{math.floor(int(song['duration'])/60)}:{int(song['duration'])%60:02}", inline=True)
        await ctx.send(embed=embed)
        voice.play(source, after=after_playing)

    async def play_dumb_song(self, ctx, song):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio(f"songs\\{song}.mp3"))
        voice.is_playing()        

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ljud Redo')

    @commands.command()
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("Du är inte i en röstkanal")
        voice = await channel.connect()

    @commands.command()
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if voice and voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("Jag är inte i en röstkanal")

    @commands.command()
    async def play(self, ctx, *, query):
        await self.play_command(ctx, query)

    @commands.command()
    async def playtop(self, ctx, *, query):
        await self.play_command(ctx, query, is_play_top=True)

    @commands.command()
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.pause()

    @commands.command()
    async def skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.stop()

    @commands.command()
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.resume()

    @commands.command()
    async def clear(self,ctx):
        player = self.get_player(ctx.guild.id)
        player.queue.clear()
        await ctx.send("Rensade kön")

    @commands.command()
    async def move(self, ctx, från, till):
        player = self.get_player(ctx.guild.id)
        queue = list(player.queue)
        if not (1 <= int(från) <= len(queue)):
            await ctx.send("Felaktig från")
            return
        if not (1 <= int(till) <= len(queue)):
            await ctx.send("Felaktig till")
            return
        song = queue.pop(int(från) - 1)
        queue.insert(int(till) - 1, song)
        player.queue = deque(queue)
        embed=discord.Embed(title=f"Flyttade en låt till plats {till} i kön", description='')
        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
        embed.add_field(name='Video', value=f"[{song['title']}]({song['url']})", inline=True)
        embed.add_field(name='Längd', value=f"{math.floor(int(song['duration'])/60)}:{int(song['duration'])%60:02}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def remove(self, ctx, nummer):
        player = self.get_player(ctx.guild.id)
        queue = list(player.queue)
        if not (1 <= int(nummer) <= len(queue)):
            await ctx.send("Felaktig köposition")
            return
        song = queue.pop(int(nummer) - 1)
        player.queue = deque(queue)
        embed=discord.Embed(title="Tog bort en video från kön", description='')
        embed.set_thumbnail(url="https://media.giphy.com/media/Y2yEuEKZWhXpdR4QsC/giphy.gif")
        embed.add_field(name='Video', value=f"[{song['title']}]({song['url']})", inline=True)
        embed.add_field(name='Längd', value=f"{math.floor(int(song['duration'])/60)}:{int(song['duration'])%60:02}", inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    async def ljudtest(self,ctx):
        audio = MP3("C:/Users/stenb/OneDrive/Dokument/Bot/songs/stp.mp3")
        await ctx.send(audio.info.bitrate)

    @commands.command(aliases=['q'])
    async def queue(self,ctx,sida=1):
        player = self.get_player(ctx.guild.id)
        if not player.queue and player.current == None:
            await ctx.send("Kön är tom 😔")
            return
        embed=discord.Embed(title="Uppspelningskö:")
        tid_tot = 0
        
        # Add current song
        song = player.current
        titel=f"[{song['title']}]({song['url']})"
        length = f"{math.floor(int(song['duration'])/60)}:{int(song['duration'])%60:02}"
        embed.add_field(name='\u200b', value=f"Spelas nu: {titel} | {length}", inline=False)
        tid_tot+=song['duration']

        # Add queue
        if sida == 1:
            start = (sida-1)*10
            queue = list(player.queue)[start:sida*10-1]
        else:
            start = (sida-1)*10-1
            queue = list(player.queue)[start:sida*10-2]

        for i, song in enumerate(player.queue):
            tid_tot+=song['duration']
        for i, song in enumerate(queue, start = start + 1):
                titel=f"[{song['title']}]({song['url']})"
                length = f"{math.floor(int(song['duration'])/60)}:{int(song['duration'])%60:02}"
                embed.add_field(name='\u200b', value=f"{i}. {titel} | {length}", inline=False)
        embed.add_field(name='\u200b', value=f"Det finns {len(player.queue)} låtar i kön. Total längd: {math.floor(tid_tot/60)}:{math.floor(tid_tot%60):02}", inline=False)
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
        await self.play_dumb_song(ctx, 'tomtemor')

    @commands.command(pass_context = True)
    async def howard(self, ctx):
        await self.play_dumb_song(ctx, 'howard')

    @commands.command(pass_context = True)
    async def fanndis(self, ctx):
        await self.play_dumb_song(ctx, 'fanndis')

    @commands.command(pass_context = True)
    async def stp(self, ctx):
        await self.play_dumb_song(ctx, 'stp')

    @commands.command(pass_context = True)
    async def anis(self, ctx):
        await self.play_dumb_song(ctx, 'anis')

    @commands.command(pass_context = True)
    async def shopping(self, ctx):
        await self.play_dumb_song(ctx, 'shopping')

async def setup(bot):
    await bot.add_cog(Ljuduppspelning(bot))
