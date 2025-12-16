# 1. Standard library imports
import asyncio
import calendar
import datetime
from datetime import date
import glob
import json
import os
from os import system
import random
from random import randint
import re
import shutil

# 2. Third-party imports
import discord
from discord.ext import commands
from discord.utils import get
from discord import FFmpegPCMAudio
import praw
import pybible


with open('tokens.json', 'r') as file:
    tokens = json.load(file)

redditxd = praw.Reddit(client_id=tokens['reddit_client_id'],
                       client_secret=tokens['reddit_client_secret'],
                       user_agent=tokens['reddit_user_agent'])

print(redditxd.read_only)

class Roligt(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def xd(self, ctx):
        await ctx.send('https://media.discordapp.net/attachments/420974041625526273/532238249180266496/xd.gif')

    @commands.command()
    async def fredag(self, ctx):
        my_date = date.today()
        calendar.day_name[my_date.weekday()]

        if calendar.day_name[my_date.weekday()] == 'Friday':
            await ctx.send('de freda')
            sverige = redditxd.subreddit("sweden")
            for i in sverige.search("mina bekanta", limit=5,time_filter='day'):
                await ctx.send(i.url)
        else:
            await ctx.send('Det är inte fredag')

    @commands.command(pass_context = True)
    async def gnome(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        try:
            await ctx.send(file=discord.File('gnome.jpg'))            
            voice.play(discord.FFmpegPCMAudio("songs\\gnome.mp3"))
            voice.volume = 100
            voice.is_playing()

        except:
            await ctx.send("Något spelas")

    @commands.command(pass_context = True)
    async def pm(self, ctx, user: discord.Member, *, message: str):
        await user.send("{}".format(message))
        #await ctx.send('något är fel')

    @commands.command(pass_context = True)
    async def fungerande(self, ctx):
        x = random.randint(0,100)
        await ctx.send('Jag är ' + str(x) + '% fungerande')

    @commands.command(pass_context = True)
    async def äger(self, ctx, ägare = None, objekt = None):
        x = random.randint(0,1)
        if ägare and objekt:
            if x == 1:
                await ctx.send("{} äger {}".format(ägare, objekt))
            else:
                await ctx.send("{} äger inte {}".format(ägare, objekt))
        else:
                await ctx.send("Skriv korrekt! " + ctx.message.author.mention)

    @commands.command(pass_context = True)
    async def fortnite(self, ctx):
        default_dances =   ['https://tenor.com/view/oof-fortnite-dance-default-baldy-gif-13259613',
                            'https://tenor.com/view/cj-default-dance-fortnite-gta-san-andreas-gif-14146206',
                            'https://tenor.com/view/minecraft-fortnite-default-dance-funny-steve-gif-13329851',
                            'https://tenor.com/view/fortnite-annoying-gif-11773776',
                            'https://tenor.com/view/roblox-dance-fortnite-moves-gif-12055860',
                            'https://tenor.com/view/sans-undertale-dance-gif-12730380',
                            'https://tenor.com/view/fornite-dance-animate-thanos-fortnite-gif-13317407']

        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()

        try:
            voice.play(discord.FFmpegPCMAudio("songs\\fortnite.mp3"))
            voice.volume = 100
            voice.is_playing()
            await ctx.send(random.choice(default_dances))
        except:
            await ctx.send("Något spelas")

    @commands.command(pass_context = True)
    async def este(self, ctx):
        voice = get(self.bot.voice_clients, guild = ctx.guild)
        if not voice:
             channel = ctx.message.author.voice.channel
             voice = await channel.connect()
        try:     
            voice.play(discord.FFmpegPCMAudio("este\\ljud.mp3"))
            voice.volume = 100
            voice.is_playing()
            await ctx.send("https://cdn.discordapp.com/attachments/670736146447204385/671072650688331796/este.gif")      
        except:
            await ctx.send("Något spelas")

    @commands.command(pass_context = True)
    async def thanos(self, ctx):
        await ctx.send('https://cdn.discordapp.com/attachments/550763415002546186/608083177600319656/tlzf7otr80911.png')

    @commands.command(pass_context = True)
    async def thanosnsfw(self, ctx):
        await ctx.send('https://cdn.discordapp.com/attachments/586136636807577601/607728951841783808/vdzlrrpebnk11.png')
        	
    @commands.command(pass_context = True)
    async def holup(self, ctx):
        await ctx.send('https://cdn.discordapp.com/attachments/519560516751065114/647925726913232918/wNVvkwK.png')

    @commands.command(pass_context = True)
    async def rensa(self, ctx):
        await ctx.send('https://cdn.discordapp.com/attachments/550763415002546186/647926295539482635/cat-2083492_1280.png')
        await ctx.send('https://cdn.discordapp.com/attachments/550763415002546186/647926295539482635/cat-2083492_1280.png')
        await ctx.send('https://cdn.discordapp.com/attachments/550763415002546186/647926295539482635/cat-2083492_1280.png')

    @commands.command()
    async def skoj(self,ctx, reset = None):
        await ctx.send("Ordet används ofta i förorten, brukar komma efter en mening där man skojat eller inte varit riktigt allvarlig. Kan också användas när man sagt något och sedan ångrat det eller känt sig osäker, men används oftast efter ett skämt. Kan också användas som ifrågasättning av något någon annan har sagt ungefär som \"allvar?\"")
    @commands.command()
    async def bild(self,ctx):
        await ctx.send("https://imgur.com/random")

    @commands.command()
    async def reddit(self,ctx,sub = None):
        try:
            sub_hot = redditxd.subreddit(sub).hot()
            post_to_pick = random.randint(1,20)
            for i in range(0, post_to_pick):
                submission = next(x for x in sub_hot if not x.stickied)

            await ctx.send(submission.url)
        except Exception as e:
            await ctx.send("Error")

    @commands.command(aliases=['g'])
    async def gudstjänst(self,ctx):
        with open('bsb.txt', 'r') as text:
            book = text.readlines()
            verse = book[random.randint(0,31101)]
            references = re.findall('[0-9]+:[0-9]+', verse)
            verse_text = str(re.split(' [0-9]+:[0-9]+ ',verse))
            verse_färdig = "{} {}".format(verse_text.split(' ', 1)[0], verse_text.split(' ',1)[1])
            print(verse_färdig)
            verse_färdig = verse_färdig.replace("[",'')
            verse_färdig = verse_färdig.replace("]",'')
            verse_färdig = verse_färdig.replace("'",'')
            verse_färdig = verse_färdig.replace("\\n", "")
            verse_färdig = verse_färdig.replace("\\t", " ")

        await ctx.send(verse_färdig)

    # @commands.command()
    # async def bibel(self,ctx):
    #     bible = pybible_load.load()
    #     await ctx.send(bible)

async def setup(bot):
    await bot.add_cog(Roligt(bot))
