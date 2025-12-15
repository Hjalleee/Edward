import discord
import os
import yt_dlp
from discord.ext import commands
import calendar
import asyncio
from discord.utils import get
from discord import FFmpegPCMAudio
import shutil
import random
import glob
import math
import re
from tinytag import TinyTag
import mutagen
from mutagen.mp4 import MP4
from urllib.parse import parse_qs, urlparse
import googleapiclient.discovery
import nacl
import json

with open('tokens.json', 'r') as file:
    tokens = json.load(file)

queue_number = 1
gachi = False

class Ljuduppspelning(commands.Cog):

    async def flytta(self, från, till):
        från = int(från)
        till = int(till)
        files = glob.glob("queue/*.m4a")
        flyttnummer = int(os.path.splitext(os.path.basename(files[till]))[0], 10)
        file_som_flyttas = files[från]
        file_som_flyttas_name = "{0:03}a.m4a".format(flyttnummer)
        os.rename(file_som_flyttas, file_som_flyttas_name)
        shutil.move(file_som_flyttas_name, "queue/")

        for i in range(till, från):
            nummer = int(os.path.splitext(os.path.basename(files[i + 1]))[0], 10)
            filename = "{0:03}a.m4a".format(nummer)
            os.rename(files[i], filename)
            shutil.move(filename, "queue/")

        for i in range(till, från + 1): 
            nummer = int(os.path.splitext(os.path.basename(files[i]))[0], 10)
            filename = "{0:03}.m4a".format(nummer)
            os.rename("{}a.m4a".format(os.path.splitext(files[i])[0]), filename)
            shutil.move(filename, "queue/")

    def __init__(self, bot):
        self.bot = bot

    async def playsong(self, voice):
            try:
                if not voice.is_playing():
                    songs = glob.glob('queue/*.m4a')
                    if songs:
                        song = songs[0]
                        print("{} spelas".format(song))
                        voice.play(discord.FFmpegPCMAudio(song), after=lambda e: self.bot.loop.create_task(self.after_play(song, voice)))
            except Exception as e:
                print(f"Playsong error: {e}")

    async def after_play(self, song, voice):
        os.remove(song)
        await self.playsong(voice)    

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ljud Redo')

    @commands.command(pass_context=True)
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        if not channel:
            await ctx.send("Du är inte i en röstkanal")
        voice = await channel.connect()

    @commands.command(pass_context=True)
    async def leave(self, ctx):
        channel = ctx.message.author.voice.channel
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        gachi = False
        if voice and voice.is_connected():
            await voice.disconnect()
        else:
            await ctx.send("Jag är inte i en röstkanal")

    @commands.command(pass_context=True)
    async def play(self, ctx, *, song: str = None):
        gachi = False
        global queue_number
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        try:
            voice.resume()
        except:
            print("Couldn't resume voice")

        if song is None:
            await self.playsong(voice)
        else:
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'default_search': 'auto',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(song, download=False)
                    result = result['entries'][0] if 'entries' in result else result
                    if result['duration'] < 6000:
                        ydl.download([result['webpage_url']])
                        for file in os.listdir("./"):
                            if file.endswith(".m4a"):
                                tags = MP4(file).tags
                                tags["\xa9nam"] = "{}".format(result['title'])
                                tags["\xa9cmt"] = "{}".format(result['webpage_url'])
                                tags.save(file)
                                filename = "{0:03}.m4a".format(queue_number)
                                os.rename(file, filename)
                                shutil.move(filename, "queue/")
                        embed = discord.Embed(title="Lade till en video i kön", description='')
                        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
                        embed.add_field(name='Video', value="[{}]({})".format(result['title'], result['webpage_url']), inline=True)
                        embed.add_field(name='Längd', value='{}:{}'.format(math.floor(int(result['duration'])/60), int(result['duration'])%60), inline=True)
                        await ctx.send(embed=embed)
                        queue_number += 1
                        await self.playsong(voice)
                    else:
                        await ctx.send("För lång video")
                except Exception as e:
                    await ctx.send(f"Play error occurred: {e}")

    @commands.command(pass_context=True)
    async def playtop(self, ctx, *, song: str = None):
        global queue_number
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()

        if song is None:
            await self.playsong(voice)
        else:
            ydl_opts = {
                'format': 'm4a/bestaudio/best',
                'default_search': 'auto',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                }]
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(song, download=False)
                    result = result['entries'][0] if 'entries' in result else result
                    if result['duration'] < 1800:
                        ydl.download([result['webpage_url']])
                        for file in os.listdir("./"):
                            if file.endswith(".m4a"):
                                tags = MP4(file).tags
                                tags["\xa9nam"] = "{}".format(result['title'])
                                tags["\xa9cmt"] = "{}".format(result['webpage_url'])
                                tags.save(file)
                                filename = "{0:03}.m4a".format(queue_number)
                                os.rename(file, filename)
                                shutil.move(filename, "queue/")
                                files = glob.glob("queue/*.m4a")
                                await self.flytta(files.index("queue\\{}".format(filename)), 1)
                        embed = discord.Embed(title="Lade till en video först i kön", description='')
                        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
                        embed.add_field(name='Video', value="[{}]({})".format(result['title'], result['webpage_url']), inline=True)
                        embed.add_field(name='Längd', value='{}:{}'.format(math.floor(int(result['duration'])/60), int(result['duration'])%60), inline=True)
                        await ctx.send(embed=embed)
                        queue_number += 1
                        await self.playsong(voice)
                    else:
                        await ctx.send("För lång video")
                except Exception as e:
                    await ctx.send(f"Playtop error occurred: {e}")

    @commands.command(pass_context=True)
    async def playlist(self, ctx, url, index=1):
        global queue_number
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        
        query = parse_qs(urlparse(url).query, keep_blank_values=True)
        playlist_id = query["list"][0]

        youtube = googleapiclient.discovery.build("youtube", "v3", developerKey="YOUR_API_KEY")

        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50
        )

        playlist_items = []
        while request is not None:
            response = request.execute()
            playlist_items += response["items"]
            request = youtube.playlistItems().list_next(request, response)

        idlista = [f'https://www.youtube.com/watch?v={t["snippet"]["resourceId"]["videoId"]}' for t in playlist_items]

        ydl_opts = {
            'default_search': 'auto',
            'format': '140',
            'extractaudio': True,
            'audioformat': 'best',
            'age_limit': 30,
            'noplaylist': True,
        }
        
        for i in idlista[(index-1)*10:index*10]:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(i, download=True)
                    for file in os.listdir("./"):
                        if file.endswith(".m4a"):
                            tags = MP4(file).tags
                            tags["\xa9nam"] = "{}".format(result['title'])
                            tags["\xa9cmt"] = "{}".format(result['webpage_url'])
                            tags.save(file)
                            filename = "{0:03}.m4a".format(queue_number)
                            os.rename(file, filename)
                            shutil.move(filename, "queue/")
                except Exception as e:
                    print(f"Playlist error occurred: {e}")
                queue_number += 1
                await self.playsong(voice)
        embed = discord.Embed(title="Lade till låt {} - {} från spellistan i kön".format((index-1)*10, index*10), description='')
        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
        embed.add_field(name='Spellista:', value=url)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def pause(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.pause()

    @commands.command(pass_context=True)
    async def skip(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if gachi:
            if voice and voice.is_playing():
                voice.stop()
                await gachi(self,ctx)  # Play the next song in the queue
            else:
                await ctx.send("Inget spelas för närvarande som kan hoppas över")
        else:
            if voice and voice.is_playing():
                voice.stop()
            else:
                await ctx.send("Inget spelas för närvarande som kan hoppas över")            


    @commands.command(pass_context=True)
    async def resume(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        voice.resume()

    @commands.command(pass_context=True)
    async def clear(self, ctx):
        files = glob.glob("queue/*.m4a")
        try:
            for f in files:
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Clear error occurred: {e}")
        except:
            print("Misslyckades med att rensa allt")
        try:
            for f in files[1:]:
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Clear error occurred: {e}")
        except:
            print("Misslyckades med att rensa nästan allt")
        await ctx.send("Rensade kön")

    @commands.command(pass_context=True)
    async def move(self, ctx, från, till):
        await self.flytta(från, till)
        await ctx.send("flyttade låt")

    @commands.command(pass_context=True)
    async def remove(self, ctx, nummer):
        files = glob.glob("queue/*.m4a")
        fil = files[int(nummer)]
        file = TinyTag.get(fil)
        titel = "[{}]({})".format(file.title, file.comment)
        lenght = '{}:{}'.format(math.floor(int(file.duration)/60), int(file.duration)%60)
        embed = discord.Embed(title="Tog bort en video från kön")
        embed.set_thumbnail(url="https://media.giphy.com/media/Y2yEuEKZWhXpdR4QsC/giphy.gif")
        embed.add_field(name='\u200b', value="{}. {} | {}".format(nummer, titel, lenght), inline=False)
        await ctx.send(embed=embed)
        os.remove(fil)

    @commands.command()
    async def ljudtest(self, ctx):
        audio = MP3("songs/stp.mp3")
        await ctx.send(audio.info.bitrate)

    @commands.command(aliases=['q'])
    async def queue(self, ctx, sida=1):
        queuen = glob.glob("queue/*.m4a")
        embed = discord.Embed(title="Uppspelningskö:")
        queuenummer = (sida-1)*10
        tid_tot = 0
        for file in queuen:
            file = TinyTag.get(file)
            tid_tot += file.duration
        for file in queuen[(sida-1)*10:(sida*10)]:
            file = TinyTag.get(file)
            titel = "[{}]({})".format(file.title, file.comment)
            lenght = '{}:{}'.format(math.floor(int(file.duration)/60), int(file.duration)%60)
            if queuenummer == 0:
                embed.add_field(name='\u200b', value="Spelas nu: {} | {}".format(titel, lenght), inline=False)
                queuenummer += 1
            else:
                embed.add_field(name='\u200b', value="{}. {} | {}".format(queuenummer, titel, lenght), inline=False)
                queuenummer += 1
        embed.add_field(name='\u200b', value="Det finns {} låtar i kön. Total längd: {}:{}".format(len(queuen)-1, math.floor(tid_tot/60), math.floor(tid_tot%60)), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def gachi(self, ctx, extra=None):
        gachi = True
        if extra == "reset":
            source = "gachi/spelad/"
            dest = "gachi/"
            files = os.listdir(source)
            for f in files:
                shutil.move(source+f, dest)
            await ctx.send("Resetadde gachi")
        else:
            async def gachi_loop():
                gachi_songs = glob.glob("gachi/*.m4a")
                if gachi:
                    r = random.choice(gachi_songs)
                    await ctx.send("{} spelas".format(r))
                    print("{} spelas".format(r))
                    voice.play(discord.FFmpegPCMAudio(r), after=lambda e: self.bot.loop.create_task(after_play(r)))
                else:
                    print("No gachi")

            async def after_play(r):
                shutil.move(r, "gachi/spelad/")
                await gachi_loop()

            voice = get(self.bot.voice_clients, guild=ctx.guild)
            if not voice:
                channel = ctx.message.author.voice.channel
                voice = await channel.connect()
            await gachi_loop()

    @commands.command(pass_context=True)
    async def tomtemor(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\tomtemor.mp3"))

    @commands.command(pass_context=True)
    async def howard(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\howard.mp3"))

    @commands.command(pass_context=True)
    async def fanndis(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\fanndis.mp3"))

    @commands.command(pass_context=True)
    async def stp(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\stp.mp3"))

    @commands.command(pass_context=True)
    async def anis(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\anis.mp3"))

    @commands.command(pass_context=True)
    async def shopping(self, ctx):
        voice = get(self.bot.voice_clients, guild=ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        voice.play(discord.FFmpegPCMAudio("songs\\shopping.mp3"))

async def setup(bot):
    await bot.add_cog(Ljuduppspelning(bot))
