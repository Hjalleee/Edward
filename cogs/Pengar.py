# 1. Standard library imports
import asyncio
import json
import random
import os
from random import randint

# 2. Third-party imports
import discord
from discord.ext import commands

#butik
butik = {
    'lambsauce' : 50,
    'brest' : 100,
    'golden nut' : 999999
}

flex = {
    'lambsauce' : "https://www.chefnotrequired.com/wp-content/uploads/2021/04/lamb-gravy-blog-hero.jpg",
    'brest' : "https://image.shutterstock.com/image-photo/chicken-breast-stuffed-garlic-spinach-260nw-1353766883.jpg",
    'golden nut' : "https://preview.redd.it/today-i-found-out-3d-printing-a-golden-nut-takes-much-less-v0-qs3bx49571161.jpg?width=640&crop=smart&auto=webp&s=b7be3d3522fcc18d115f7fa07201b5551950e640"
}

tmp = 'users.json.tmp'

class Pengar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.save_lock = asyncio.Lock()

        with open('users.json', 'r') as f:
            self.users = json.load(f)

    async def save_users(self):
        async with self.save_lock:
            with open('users.json.tmp', 'w') as f:
                json.dump(self.users, f, indent=4)
            os.replace('users.json.tmp', 'users.json')

    async def ge_pengar(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            print(self.users)
            await asyncio.sleep(1)

    async def check_pengar(self, id):
        id = str(id)
        return self.users[id]["pengar"]
    
    async def check_vara(self, id, vara):
        id = str(id)
        return self.users[id][vara]

    async def add_pengar(self, id, antal):
        id = str(id)
        antal = int(antal)
        if id not in self.users:
            self.users[id] = {}
            self.users[id]["pengar"] = 0
        self.users[id]["pengar"] += antal
        await self.save_users()
        return

    async def add_vara(self, id, vara):
        id = str(id)
        if vara not in self.users[id]:
            self.users[id][vara] = 0
        self.users[id][vara] += 1
        self.save_users()
        return

    async def cog_unload(self):
        await self.save_users()

    @commands.Cog.listener()
    async def on_message(self, message):
        id = message.author.id
        await self.add_pengar(id,1)
        msg = f"{message.author} har {await self.check_pengar(id)} pengar"
        print(msg)

    @commands.command()
    async def roulette(self, ctx, färg = None, bet = None):
        valid_bet = (
            färg in {'röd', 'svart', 'grön'}
            and bet is not None 
            and bet.isdigit() 
            and int(bet) in range(1,1000001)
        )

        if not valid_bet:
            await ctx.send("Skriv korrekt! #help roulette, om du behöver hjälp "+ ctx.message.author.mention)
            return
        
        bet = int(bet)
        
        if await self.check_pengar(ctx.message.author.id) < bet:
            await ctx.send("Så rik är du inte " + ctx.message.author.mention)
            return

        x = random.randint(1,37)
        if 1 <= x <= 18:
            rättFärg = 'röd'
        elif 19 <= x <= 36:
            rättFärg = 'svart'
        else:
            rättFärg = 'grön'
        print(x)
        await self.add_pengar(ctx.message.author.id, -bet)

        if rättFärg == färg:
            multiplier = 30 if rättFärg == 'grön' else 2
            vinst = bet * multiplier
            await ctx.send(f"Rätt färg: {rättFärg}\nJackpot, du vann {vinst} pengar {ctx.message.author.mention}")
            await self.add_pengar(ctx.message.author.id, vinst)
        else:
            await ctx.send(f"Rätt färg: {rättFärg}\nDu förlorade {bet} pengar {ctx.message.author.mention}") 

    @commands.command()
    async def pengar(self, ctx, user : discord.Member = None, add=None, antal=None):
        auth_id = ctx.message.author.id

        valid_swish = (
            auth_id == 200568828801974272
            and antal is not None
            and antal.isdigit()
            and add in {'add','remove'}
            and 1 <= int(antal) <= 1000000
        )

        # No user = show own balance
        if user is None:
            balance = await self.check_pengar(auth_id)
            await ctx.send(f"Du har {balance} pengar! {ctx.message.author.mention}")
            return

        # Just show balance
        if add is None:
            balance = await self.check_pengar(user.id)
            await ctx.send(f"{user.mention} har {balance} pengar!")
            return

        # Admin add/remove
        if not valid_swish:
            await ctx.send("Skriv korrekt! #help pengar")
            return
        if add == 'add':
            await self.add_pengar(user.id, antal)
            await ctx.send(
                f"{user.mention} fick {int(antal)} pengar\n"
                f"Nytt saldo: {await self.check_pengar(user.id)}"
            )
        if add == 'remove':
            await self.add_pengar(user.id, -antal)
            await ctx.send(
                f"{user.mention} blev av med {antal} pengar\n"
                f"Nytt saldo: {await self.check_pengar(user.id)}"
            )            

    @pengar.error
    async def pengar_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{error.argument} är inte en giltig användare {ctx.author.mention}")

    @commands.command()
    async def butik(self, ctx):
        msg = "Edwards butik:\n"
        for k, v in butik.items():
            msg += f'{k}: {v} pengar\n'
        await ctx.send(msg)

    @commands.command()
    async def köp(self, ctx, *, vara: str = None):
        id = ctx.message.author.id
        if not vara:
            await ctx.send("Välj vad du ska köpa! " + ctx.message.author.mention)
            return
        
        if vara not in butik:
            await ctx.send(f"{vara} är inte en vara! Se butiken med #butik {ctx.message.author.mention}")
            return

        pris = butik[vara]
        if await self.check_pengar(id) < pris:
            await ctx.send("Så rik är du inte " + ctx.message.author.mention)
            return

        await self.add_vara(id, vara)
        await self.add_pengar(id, -pris)
        await ctx.send(f"Du köpte {vara} för {pris}! {ctx.message.author.mention}")
        print(f"{ctx.message.author} har {await self.check_vara(id,vara)} {vara}")

    @commands.command()
    async def inventarie(self, ctx, user : discord.Member = None):
        if not user:
            user = ctx.message.author
        id = user.id
        msg = f"{user.mention}s Inventarie: \n"
        for k, v in self.users[str(id)].items():
            msg += f'{k}: {v}\n'
        await ctx.send(msg)

    @inventarie.error
    async def inventarie_error(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{error.argument} är inte en giltig användare {ctx.author.mention}")

    @commands.command()
    async def flex(self,ctx, *, sak: str = None):
        id = ctx.message.author.id
        if sak is None or sak not in flex:
            await ctx.send(f"{sak} är inte en giltig sak {ctx.author.mention}")
            return
        if await self.check_vara(id, sak) > 0:
            await ctx.send(f"{ctx.author.mention}s {sak}")
            await ctx.send(flex[sak])
        else:
            await ctx.send(f"Du har ingen {sak} {ctx.author.mention}")

async def setup(bot):
    await bot.add_cog(Pengar(bot))
