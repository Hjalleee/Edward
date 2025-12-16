# 1. Standard library imports
import os
import json

# 2. Third-party imports
import discord
from discord.ext import commands
from discord import User, Game
import nacl

with open('tokens.json', 'r') as file:
    tokens = json.load(file)

TOKEN = tokens['discord_token']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='#', intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('Håller gudstjänst'))
    print('Edward Blom är redo.')

    for cog in os.listdir(".\\cogs"):
        if cog.endswith(".py"):
            try:
                cog = f"cogs.{cog.replace('.py', '')}"
                await bot.load_extension(cog)
            except Exception as e:
                print(f"{cog} reeeeeeeeeeeeeear:")
                raise e

@bot.listen()        
async def on_message(message):
    if message.content.startswith('#') and message.channel.id==659563748180099095:
        await message.channel.send('Ditt dumma fan skicka inte i normal chat')  

@bot.command()
async def load(ctx, cog):
    try:
        await bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"{cog} got loaded")
    except Exception as e:
        print(f"{cog} can not be loaded:")
        raise e

@bot.command()
async def unload(ctx, cog):
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await ctx.send(f"{cog} got unloaded")
    except Exception as e:
        print(f"{cog} can not be unloaded:")
        raise e

@bot.command()
async def reload(ctx, cog):
    try:
        await bot.unload_extension(f"cogs.{cog}")
        await bot.load_extension(f"cogs.{cog}")
        await ctx.send(f"{cog} got reloaded")
    except Exception as e:
        print(f"{cog} can not be loaded:")
        raise e

#test
@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

bot.run(TOKEN,reconnect=True)
