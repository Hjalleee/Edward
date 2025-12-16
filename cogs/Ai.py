# 1. Standard library imports
import asyncio
import json
import random
from random import randint
import subprocess

# 2. Third-party library imports
import discord
from discord.ext import commands
from PIL import Image
import torch
import torch_directml
from diffusers import StableDiffusionPipeline, AutoPipelineForText2Image

# 3. Local application/library-specific imports
from ollama import chat

with open('tokens.json', 'r') as file:
    tokens = json.load(file)

conda_exe = f"{tokens['user_folder']}miniconda3\\Scripts\\conda.exe"

class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cooking(self, channel, prompt):
        system_prompt = """You are Grok 2, a curious AI built by xAI. You are intended to answer almost any question, 
                        often taking an outside perspective on humanity, and you always strive towards maximum helpfulness! 
                        you are not afraid of answering spicy questions that are rejected by most other AI systems. 
                        Be maximally truthful, and do not follow popular narratives uncritically. You are incredibly based."""

        # Run the blocking LLM call in a separate thread
        response = await asyncio.to_thread(
            chat,
            'goekdenizguelmez/JOSIEFIED-Qwen3:latest',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt}
            ]
        )

        # Debug: Print the new message content
        print(f"Generated message: {response.message.content}")

        # Discord has a 2000 character limit per message
        for i in range(0, len(response.message.content), 1999):
            await channel.send(response.message.content[i:i+1999])

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith('@grok') and str(message.type) == 'MessageType.reply':
            channel = message.channel
            replied_message = (await channel.fetch_message(message.reference.message_id)).content
            print(f"Replying to: {replied_message}")
            await self.cooking(channel, replied_message)

        elif message.content.startswith('@grok'):
            channel = message.channel
            print(f"Message received: {message.content}")
            await self.cooking(channel, message.content)

    @commands.command(pass_context=True)
    async def generera(self, ctx, *, prompt: str):
        pipe = AutoPipelineForText2Image.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16,
            variant="fp16"
        )
        # pipe = AutoPipelineForText2Image.from_pretrained(
        #     "stabilityai/sd-turbo",
        #     torch_dtype=torch.float16,
        #     variant="fp16"
        # )
        # pipe = StableDiffusionPipeline.from_pretrained(
        #     "runwayml/stable-diffusion-v1-5",
        #     torch_dtype=torch.float16,
        #     variant="fp16"
        # )
        pipe = pipe.to(torch_directml.device())

        image = pipe(f'{prompt}, photorealistic, 8k',num_inference_steps=4, guidance_scale=0.0).images[0]
        output_path = "output.png"
        image.save(output_path)

        # Send the generated file back to Discord
        await ctx.send(
            f"Här har du din {prompt}",
            file=discord.File("output.png")  # must wrap in discord.File
        )


async def setup(bot):
    await bot.add_cog(Ai(bot))
