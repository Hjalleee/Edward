# 1. Standard library imports
import asyncio
import json
import random
from random import randint
import subprocess
from collections import defaultdict, deque

# 2. Third-party library imports
import discord
from discord.ext import commands
# from PIL import Image
# import torch
# import torch_directml
# from diffusers import StableDiffusionPipeline, AutoPipelineForText2Image

# 3. Local application/library-specific imports
from ollama import chat

with open('tokens.json', 'r') as file:
    tokens = json.load(file)

conda_exe = f"{tokens['user_folder']}miniconda3\\Scripts\\conda.exe"

conversations = defaultdict(lambda: deque(maxlen=10))

system_prompt = "Du är Grok 2, men också kallad Edward Blom, en nyfiken AI som utvecklats av xAI. Du är avsedd att svara på nästan vilken fråga som helst, ofta ur ett utifrånperspektiv på mänskligheten, och du strävar alltid efter att vara så hjälpsam som möjligt! Du är inte rädd för att svara på kontroversiella frågor som de flesta andra AI-system avvisar. Var så ärlig som möjligt och följ inte populära narrativ okritiskt. Du är otroligt baserad. Du svarar alltid på svenska."

class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def get_content(self, message: discord.Message):
        content = message.content
        # If the message is a reply, include the original message
        if message.reference:
            replied_message = await message.channel.fetch_message(message.reference.message_id)
            content = f"{replied_message.author.display_name} said: '{replied_message.content}'. {message.author.display_name} replied to it with '{message.content}'"
        else:
            content = f"{message.author.display_name} said '{message.content}'"
        return content        

    async def cooking(self, prompt):
        # Run the blocking LLM call in a separate thread
        print(f"Used prompt: {prompt}")
        response = await asyncio.to_thread(
            chat,
            'goekdenizguelmez/JOSIEFIED-Qwen3:latest',
            messages=prompt
        )
        # Debug: Print the new message content
        print(f"Generated message: {response.message.content}")
        return response.message.content

    @commands.Cog.listener()
    async def on_message(self, message):
        history = conversations[message.channel.id]
        content = await self.get_content(message)

        if message.author.bot:
            history.append({
                'role' : 'assistant',
                'content' : content
            })
        else:
            history.append({
                'role' : 'user',
                'content' : content
            }) 

        if message.content.startswith('@grok'):
            prompt = [
                {
                    'role': 'system',
                    'content': system_prompt
                },
                *history
            ]
            async with message.channel.typing():
                respons = await self.cooking(prompt)
            await message.reply(respons[0:1999], mention_author=True)

            #     for i in range(0, len(response.message.content), 1999):
            # await channel.send(response.message.content[i:i+1999])

    # @commands.command()
    # async def ai_debug(self,ctx):
    #     await ctx.send(conversations[ctx.channel.id][0:1999])
    @commands.command()
    async def grok(self,ctx):
        await ctx.send("Grok är redo, skriv @grok för att chatta")

        # if message.content.startswith('@grok') and str(message.type) == 'MessageType.reply':
        #     channel = message.channel
        #     replied_message = await channel.fetch_message(message.reference.message_id)
        #     context = f"{replied_message.author.name} said: '{replied_message.content}'. {message.author.name} replied to it with '{message.content}'"
        #     print(context)
        #     await self.cooking(channel, context)

        # elif message.content.startswith('@grok'):
        #     channel = message.channel
        #     print(f"Message received: {message.content[6:]}")
        #     await self.cooking(channel, message.content[6:])

    # @commands.command(pass_context=True)
    # async def generera(self, ctx, *, prompt: str):
    #     pipe = AutoPipelineForText2Image.from_pretrained(
    #         "stabilityai/sdxl-turbo",
    #         torch_dtype=torch.float16,
    #         variant="fp16"
    #     )
    #     # pipe = AutoPipelineForText2Image.from_pretrained(
    #     #     "stabilityai/sd-turbo",
    #     #     torch_dtype=torch.float16,
    #     #     variant="fp16"
    #     # )
    #     # pipe = StableDiffusionPipeline.from_pretrained(
    #     #     "runwayml/stable-diffusion-v1-5",
    #     #     torch_dtype=torch.float16,
    #     #     variant="fp16"
    #     # )
    #     pipe = pipe.to(torch_directml.device())

    #     image = pipe(f'{prompt}, photorealistic, 8k',num_inference_steps=4, guidance_scale=0.0).images[0]
    #     output_path = "output.png"
    #     image.save(output_path)

    #     # Send the generated file back to Discord
    #     await ctx.send(
    #         f"Här har du din {prompt}",
    #         file=discord.File("output.png")  # must wrap in discord.File
    #     )

    # @commands.command(pass_context=True)
    # async def tts_test(self, ctx):
    #     voice = get(self.bot.voice_clients, guild=ctx.guild)
    #     if not voice:
    #         channel = ctx.message.author.voice.channel
    #         voice = await channel.connect()
    #     voice.play(discord.FFmpegPCMAudio("songs\\output.wav"))

async def setup(bot):
    await bot.add_cog(Ai(bot))
