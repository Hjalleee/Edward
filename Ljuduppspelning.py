import discord
import os
import youtube_dl
from discord.ext import commands
import calendar
import asyncio
from discord.utils import get
from discord import FFmpegPCMAudio
from os import system
import shutil
import random
import glob
import math
import re
from tinytag import TinyTag
import mutagen
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
import urllib.request
from bs4 import BeautifulSoup
import requests
import time

#spara låtar i en mapp så man slipper ladda ner dom
queue_number = 1

class Ljuduppspelning(commands.Cog):

    async def flytta(self, från, till):
        från=int(från)
        till=int(till)
        files=glob.glob("queue/*.m4a")
        flyttnummer=int(os.path.splitext(os.path.basename(files[till]))[0],10)
        file_som_flyttas=files[från]
        file_som_flyttas_name = "{0:03}a.m4a".format(flyttnummer)
        os.rename(file_som_flyttas, file_som_flyttas_name)
        shutil.move(file_som_flyttas_name, "queue/")

        for i in range(till,från):
            nummer=int(os.path.splitext(os.path.basename(files[i+1]))[0],10)
            filename = "{0:03}a.m4a".format(nummer)
            os.rename(files[i], filename)
            shutil.move(filename, "queue/")

        for i in range(till,från+1): 
            nummer=int(os.path.splitext(os.path.basename(files[i]))[0],10)
            filename = "{0:03}.m4a".format(nummer)
            os.rename("{}a.m4a".format(os.path.splitext(files[i])[0]), filename)
            shutil.move(filename, "queue/")

    def __init__(self, bot):
        self.bot = bot
        #self.bot.loop.create_task(self.queue_sak())

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

    @commands.command(pass_context = True)
    async def play(self, ctx, *, song: str = None):
        global queue_number
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()

        def playsong():
            try:
                if not voice.is_playing():
                    songs = glob.glob('queue/*.m4a')
                    song = songs[0]
                    voice.play(discord.FFmpegPCMAudio(song), after = lambda e:(os.remove(song), playsong()))
                    voice.is_playing()
            except:
                pass

        if song == None:
            playsong()

        if not song == None:
            #låtnerladdning
            ydl_opts = {
                    'default_search': 'auto',
                    'format': '140',
                    'extractaudio': True,
                    'audioformat': 'best',
                    'age_limit': 30,
				    'noplaylist': True,
                }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(song,download = False)
                except:
                    pass
                try:
                    result =result['entries'][0]
                except:
                    pass
            try:
                if result['duration']<6000:
                    fails=0
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([result['webpage_url']])
                        for file in os.listdir("./"):
                            if file.endswith(".m4a"):
                                tags = MP4(file).tags
                                tags["\xa9nam"] = "{}".format(result['title'])
                                tags["\xa9cmt"] = "{}".format(result['webpage_url'])
                                tags.save(file)
                            
                                #filename= "{} {}.m4a".format(queue_number,result['title'])
                                #filename=re.sub('[^a-zA-Z0-9-_.åäö]', ' ', filename)
                                filename = "{0:03}.m4a".format(queue_number)
                                os.rename(file, filename)
                                shutil.move(filename, "queue/")

                    print(result['title'],result['webpage_url'])
                    embed=discord.Embed(title="Lade till en video i kön", description='')
                    embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
                    embed.add_field(name='Video', value="[{}]({})".format(result['title'],result['webpage_url']), inline=True)
                    embed.add_field(name='Längd', value='{}:{}'.format(math.floor(int(result['duration'])/60),int(result['duration'])%60), inline=True)
                    await ctx.send(embed=embed)
                    queue_number+=1
                    playsong()
                else:
                    await ctx.send("För lång video")
            except Exception as e: await ctx.send(e)

    @commands.command(pass_context = True)
    async def playtop(self, ctx, *, song: str = None):
        global queue_number
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()

        def playsong():
            try:
                if not voice.is_playing():
                    songs = glob.glob('queue/*.m4a')
                    song = songs[0]
                    voice.play(discord.FFmpegPCMAudio(song), after = lambda e:(os.remove(song), playsong()))
                    voice.is_playing()
            except:
                pass

        if song == None:
            playsong()

        if not song == None:
            #låtnerladdning
            ydl_opts = {
                    'default_search': 'auto',
                    'format': '140',
                    'extractaudio': True,
                    'audioformat': 'best',
                    'age_limit': 30,
				    'noplaylist': True,
                }
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(song,download = False)
                except:
                    pass
                try:
                    result =result['entries'][0]
                except:
                    pass
            try:
                if result['duration']<1800:
                    fails=0
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([result['webpage_url']])
                        for file in os.listdir("./"):
                            if file.endswith(".m4a"):
                                tags = MP4(file).tags
                                tags["\xa9nam"] = "{}".format(result['title'])
                                tags["\xa9cmt"] = "{}".format(result['webpage_url'])
                                tags.save(file)
                            
                                #filename= "{} {}.m4a".format(queue_number,result['title'])
                                #filename=re.sub('[^a-zA-Z0-9-_.åäö]', ' ', filename)
                                filename = "{0:03}.m4a".format(queue_number)
                                os.rename(file, filename)
                                shutil.move(filename, "queue/")

                                files=glob.glob("queue/*.m4a")
                                await self.flytta(files.index("queue\\{}".format(filename)),1)

                    print(result['title'],result['webpage_url'])
                    embed=discord.Embed(title="Lade till en video först i kön", description='')
                    embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
                    embed.add_field(name='Video', value="[{}]({})".format(result['title'],result['webpage_url']), inline=True)
                    embed.add_field(name='Längd', value='{}:{}'.format(math.floor(int(result['duration'])/60),int(result['duration'])%60), inline=True)
                    await ctx.send(embed=embed)
                    queue_number+=1
                    playsong()
                else:
                    await ctx.send("För lång video")
            except:
                await ctx.send(Exception)

    @commands.command(pass_context = True)
    async def playlist(self, ctx, url, index=1):
        global queue_number
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
            channel = ctx.message.author.voice.channel
            voice = await channel.connect()
        def playsong():
            try:
                if not voice.is_playing():
                    songs = glob.glob('queue/*.m4a')
                    song = songs[0]
                    voice.play(discord.FFmpegPCMAudio(song), after = lambda e:(os.remove(song), playsong()))
                    voice.is_playing()
            except:
                print(Exception)
        
        idlista = []
        sourceCode = requests.get(url).text
        soup = BeautifulSoup(sourceCode, 'html.parser')
        domain = 'https://www.youtube.com'
        for link in soup.find_all("a", {"dir": "ltr"}):
            href = link.get('href')
            if href.startswith('/watch?'):
                idlista.append(domain + href)
        print(idlista)

        ydl_opts = {
                'default_search': 'auto',
                'format': '140',
                'extractaudio': True,
                'audioformat': 'best',
                'age_limit': 30,
	            'noplaylist': True,
                }
            
        for i in idlista[(index-1)*10:index*10]:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(i,download = True)
                    for file in os.listdir("./"):
                        if file.endswith(".m4a"):
                            tags = MP4(file).tags
                            tags["\xa9nam"] = "{}".format(result['title'])
                            tags["\xa9cmt"] = "{}".format(result['webpage_url'])
                            tags.save(file)
                            
                            filename = "{0:03}.m4a".format(queue_number)
                            os.rename(file, filename)
                            shutil.move(filename, "queue/")
                            print(queue_number, ":", result['title'], result['webpage_url'])
                except:
                    pass
                queue_number+=1
                playsong()
        embed=discord.Embed(title="Lade till låt {} - {} från spellistan i kön".format((index-1)*10,index*10), description='')
        embed.set_thumbnail(url="https://media.giphy.com/media/iKHHyziV1ju7nmxywh/giphy.gif")
        embed.add_field(name='Spellista:', value=url)
        await ctx.send(embed=embed)

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
        files=glob.glob("queue/*.m4a")
        for f in files[1:]:
            try:
                os.remove(f)
            except:
                pass
        await ctx.send("Rensade kön")

    @commands.command(pass_context = True)
    async def move(self, ctx, från, till):
        await self.flytta(från, till)
        await ctx.send("flyttade låt")

    @commands.command(pass_context = True)
    async def remove(self, ctx, nummer):
        files=glob.glob("queue/*.m4a")
        fil=files[int(nummer)]
        file=TinyTag.get(fil)
        titel="[{}]({})".format(file.title,file.comment)
        lenght = '{}:{}'.format(math.floor(int(file.duration)/60),int(file.duration)%60)
        embed=discord.Embed(title="Tog bort en video från kön")
        embed.set_thumbnail(url="https://media.giphy.com/media/Y2yEuEKZWhXpdR4QsC/giphy.gif")
        embed.add_field(name='\u200b', value="{}. {} | {}".format(nummer,titel,lenght), inline=False)
        await ctx.send(embed=embed)
        os.remove(fil)

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
