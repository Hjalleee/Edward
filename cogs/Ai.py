import asyncio
import io
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor

import aiohttp
import discord
from discord.ext import commands
from ollama import chat
from PIL import Image, ImageOps

# from gtts import gTTS

CHAT_MODEL = 'goekdenizguelmez/JOSIEFIED-Qwen3:latest'
VISION_MODEL = 'qwen2.5vl:7b'  # or 'gemma3:4b' if VRAM is tight

IMAGE_BLOCKED_CHANNEL = 1359579974264422510
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_SIDE = 512

# Image generation (DirectML)
GEN_MODEL = "stabilityai/sd-turbo"  # lighter alternative: "stabilityai/sd-turbo"
GEN_SIZE = 512
GEN_STEPS = 4
GEN_STYLE_SUFFIX = ", photorealistic, 8k"
GEN_MAX_PROMPT = 300

conversations = defaultdict(lambda: deque(maxlen=10))

system_prompt = "Du är Grok 2, men också kallad Edward Blom, en nyfiken AI som utvecklats av xAI. Du är avsedd att svara på nästan vilken fråga som helst, ofta ur ett utifrånperspektiv på mänskligheten, och du strävar alltid efter att vara så hjälpsam som möjligt! Du är inte rädd för att svara på kontroversiella frågor som de flesta andra AI-system avvisar. Var så ärlig som möjligt och följ inte populära narrativ okritiskt. Du är otroligt baserad. Du svarar alltid på svenska."

vision_prompt = (
    "Beskriv kort vad som syns på bilden, på svenska, i max två meningar. "
)


def shrink(data: bytes, max_side: int = MAX_IMAGE_SIDE) -> bytes:
    """Downscale big images before sending them to the vision model.
    Falls back to the original bytes if Pillow can't read them."""
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")
        img.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85)
        return buf.getvalue()
    except Exception as ex:
        print("Image shrink failed:", ex)
        return data


def message_text(msg: discord.Message, limit: int = 500) -> str:
    """Readable text of a message: resolved mentions, truncated, image note."""
    text = msg.clean_content.strip()
    if len(text) > limit:
        text = text[:limit] + "…"
    images = sum(
        1 for a in msg.attachments
        if a.content_type and a.content_type.startswith("image/")
    )
    if images:
        text = f"{text} [bifogade {images} bild(er)]".strip()
    return text or "[tomt meddelande]"


class Ai(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.http = None
        self.gen_pipe = None
        self.gen_lock = asyncio.Lock()
        # One dedicated thread so the pipeline is always loaded and used from the same thread
        self.gen_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="imagegen")

    async def cog_load(self):
        self.http = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15))

        # prompt = ' Du dök precis upp i en discord kanal, introducera dig själv och säg något kul'
        # prompt_full = [{'role': 'system', 'content': system_prompt + prompt}]
        # bot_channel = self.bot.get_channel(1359580144205037728)
        # async with bot_channel.typing():
        #     respons = await self.cooking(prompt_full)
        # await bot_channel.send(respons)

    async def cog_unload(self):
        if self.http:
            await self.http.close()
        self.gen_executor.shutdown(wait=False)
        self.gen_pipe = None

    async def get_content(self, message: discord.Message):
        author = message.author.display_name
        text = message_text(message)

        ref = message.reference
        if ref and ref.message_id:
            replied = None
            resolved = ref.resolved

            if isinstance(resolved, discord.Message):
                replied = resolved  # already cached, no API call
            elif resolved is None:
                try:
                    replied = await message.channel.fetch_message(ref.message_id)
                except discord.HTTPException:
                    pass  # deleted, no permission, or network error
            # DeletedReferencedMessage: skip, fall through

            if replied:
                return (
                    f"{replied.author.display_name} said: '{message_text(replied)}'. "
                    f"{author} replied to it with '{text}'"
                )

        return f"{author} said '{text}'"

    async def cooking(self, prompt):
        # Run the blocking LLM call in a separate thread
        print(f"Used prompt: {prompt}")
        response = await asyncio.to_thread(
            chat,
            CHAT_MODEL,
            messages=prompt
        )
        print(f"Generated message: {response.message.content}")
        return response.message.content

    async def download_image(self, url):
        try:
            async with self.http.get(url) as r:
                if r.status != 200:
                    return None
                if r.content_length and r.content_length > MAX_IMAGE_BYTES:
                    return None
                return await r.read()
        except Exception as ex:
            print("Image download failed:", ex)
            return None

    async def get_image_bytes(self, message: discord.Message):
        for a in message.attachments:
            if a.content_type and a.content_type.startswith("image/") and a.size <= MAX_IMAGE_BYTES:
                try:
                    return await a.read()
                except discord.HTTPException as ex:
                    print("Attachment read failed:", ex)
                    return None
        for e in message.embeds:
            url = (e.image.url if e.image else None) or (e.thumbnail.url if e.thumbnail else None)
            if url:
                return await self.download_image(url)
        return None

    async def recognize_image(self, data: bytes):
        small = await asyncio.to_thread(shrink, data)
        try:
            response = await asyncio.to_thread(
                chat,
                VISION_MODEL,
                messages=[
                    {'role': 'user', 'content': vision_prompt, 'images': [small]},
                ],
                options={'num_predict': 80, 'num_ctx': 2048, 'temperature': 0.3},
                keep_alive='30m',
            )
        except Exception as ex:
            print("Vision model failed:", ex)
            return None
        print(f"Vision result: {response.message.content}")
        return response.message.content

    @commands.Cog.listener()
    async def on_message(self, message):
        history = conversations[message.channel.id]

        # Bot messages (including our own replies) are only stored as plain text
        if message.author.bot:
            history.append({'role': 'assistant', 'content': message_text(message)})
            return

        if message.content.startswith('@grok reset'):
            history.clear()
            await message.reply("Grok forgor 💀")
            return

        content = await self.get_content(message)
        history.append({'role': 'user', 'content': content})

        if message.channel.id != IMAGE_BLOCKED_CHANNEL:
            data = await self.get_image_bytes(message)
            if data:
                async with message.channel.typing():
                    description = await self.recognize_image(data)
                if description:
                    # Our reply comes back through on_message and is stored in the history there
                    await message.reply(description[:1999])

        if message.content.startswith('@grok'):
            prompt = [
                {'role': 'system', 'content': system_prompt},
                *history
            ]
            async with message.channel.typing():
                respons = await self.cooking(prompt)
            await message.reply(respons[0:1999], mention_author=True)

    # @commands.command()
    # async def ai_debug(self, ctx):
    #     await ctx.send(conversations[ctx.channel.id][0:1999])

    @commands.command()
    async def grok(self, ctx):
        await ctx.send("Grok är redo, skriv @grok för att chatta")

    def _load_pipe(self):
        """Blocking: runs in the generation thread. Heavy imports happen here so the bot starts fast."""
        import torch
        import torch_directml
        from diffusers import AutoPipelineForText2Image

        pipe = AutoPipelineForText2Image.from_pretrained(
            GEN_MODEL,
            torch_dtype=torch.float16,
            variant="fp16",
        )
        return pipe.to(torch_directml.device())

    def _generate(self, prompt: str) -> bytes:
        """Blocking: runs in the generation thread. Returns PNG bytes."""
        if self.gen_pipe is None:
            self.gen_pipe = self._load_pipe()
        image = self.gen_pipe(
            f"{prompt}{GEN_STYLE_SUFFIX}",
            num_inference_steps=GEN_STEPS,
            guidance_scale=0.0,
            width=GEN_SIZE,
            height=GEN_SIZE,
        ).images[0]
        buf = io.BytesIO()
        image.save(buf, "PNG")
        return buf.getvalue()

    @commands.command(name="generera", aliases=["gen"])
    async def generera(self, ctx, *, prompt: str = None):
        if not prompt or not prompt.strip():
            await ctx.reply(f"Användning: `{ctx.prefix}generera en katt i rymddräkt`")
            return
        prompt = prompt.strip()[:GEN_MAX_PROMPT]

        if self.gen_lock.locked():
            await ctx.reply("Jag håller redan på att generera en bild, vänta lite.")
            return

        async with self.gen_lock:
            async with ctx.typing():
                loop = asyncio.get_running_loop()
                try:
                    data = await loop.run_in_executor(self.gen_executor, self._generate, prompt)
                except Exception as ex:
                    print("Image generation failed:", repr(ex))
                    await ctx.reply("Något gick fel när jag skulle generera bilden.")
                    return

        await ctx.reply(
            f"Här har du din {prompt}",
            file=discord.File(io.BytesIO(data), filename="generated.png"),
            allowed_mentions=discord.AllowedMentions.none(),
        )

    # @commands.command(pass_context=True)
    # async def tts_test(self, ctx):
    #     voice = get(self.bot.voice_clients, guild=ctx.guild)
    #     if not voice:
    #         channel = ctx.message.author.voice.channel
    #         voice = await channel.connect()
    #     voice.play(discord.FFmpegPCMAudio("songs\\output.wav"))


async def setup(bot):
    await bot.add_cog(Ai(bot))