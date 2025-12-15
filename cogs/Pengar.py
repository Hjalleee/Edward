import discord
import json
import random
from random import randint
from discord.ext import commands
import asyncio

#butik
varor = 'lambsauce','brest'

#priser
pris = 50, 100

class Pengar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        self.bot.loop.create_task(self.save_users())
        #self.bot.loop.create_task(self.ge_pengar())

        with open('users.json', 'r') as f:
            self.users = json.load(f)

    async def save_users(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            with open('users.json', 'w') as f:
                json.dump(self.users, f, indent=4)
                f.close()

            await asyncio.sleep(1)

    async def ge_pengar(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            print(self.users)

            await asyncio.sleep(1)

    async def check_pengar(self, id):
        x = self.users[id]["pengar"]
        return x

    async def add_pengar(self, id, antal):
        self.users[id]["pengar"] += antal
        return

    async def add_vara(self, id, vara):
        if vara not in self.users[id]:
            self.users[id][vara] = 0
        self.users[id][vara] += 1
        return


    @commands.Cog.listener()
    async def on_message(self, message):

        id = str(message.author.id)

        if id not in self.users:
            self.users[id] = {}
            self.users[id]["pengar"] = 0
        self.users[id]["pengar"] += 1
        msg = "{} har ".format(message.author) + "{} pengar".format(self.users[id]["pengar"])
        print(msg)
        await self.save_users()

    @commands.command(pass_context = True)
    async def roulette(self, ctx, färg = None, antal = None):
        if (färg=='röd' or färg=='svart' or färg=='grön') and (0 <= int(antal) <= 1000000):
            if await self.check_pengar(str(ctx.message.author.id)) >= int(antal):
                x = random.randint(1,37)
                if 1 <= x <= 18:
                    rättFärg = 'röd'
                elif 19 <= x <= 36:
                    rättFärg = 'svart'
                else:
                    rättFärg = 'grön'

                print(x)

                await self.add_pengar(str(ctx.message.author.id), -int(antal))

                if (str(rättFärg) == färg) and (rättFärg != 'grön'):
                    await ctx.send(" Rätt färg: " + rättFärg + ", Jackpot, Du vann " + str(int(antal)*2) + " pengar " + ctx.message.author.mention)
                    await self.add_pengar(str(ctx.message.author.id), int(antal)*2)
                elif str(rättFärg) == färg and rättFärg == 'grön':
                    await ctx.send(" Rätt färg: " + rättFärg + ", Jackpot, Du vann " + str(int(antal)*30) + " pengar " + ctx.message.author.mention)
                    await self.add_pengar(str(ctx.message.author.id), int(antal)*30)
                else:
                    await ctx.send(" Rätt färg: " + rättFärg + ", Du förlorade " + antal + " pengar " + ctx.message.author.mention)
            else:
                await ctx.send("Så rik är du inte " + ctx.message.author.mention)
        else:
            await ctx.send("Skriv korrekt! !help roulette, om du behöver hjälp "+ ctx.message.author.mention)
        await self.save_users()

    @commands.command(pass_context = True)
    async def pengar(self, ctx, user : discord.Member = None, add = None, antal = None):

        id = str(ctx.message.author.id)
        try:
            userID = str(user.id)
        except:
            print("inget id skrivit")
        if not user:
            await ctx.send("Du har {} pengar! ".format(await self.check_pengar(id) + 1) + ctx.message.author.mention)
        elif user and add == None:
            try:
                await ctx.send("{} har {} pengar!".format(user.mention, await self.check_pengar(userID)))
            except Exception as e:
                await ctx.send(Exception)
                raise e
        elif (add == 'add' and antal.isdigit() and (0 <= int(antal) <= 1000000)):
            if (id == '200568828801974272'):
                await self.add_pengar(userID, int(antal))
                msg = " {} fick {} pengar!".format(user.mention, int(antal)) + " {} har {} pengar!".format(user.mention, await self.check_pengar(userID))
                await ctx.send(msg)
            else:
                msg = "nej " + ctx.message.author.mention
                await ctx.send(msg)
        elif (add == 'remove') and (antal.isdigit()) and (0 <= int(antal) <= 1000000):
            if (id == '200568828801974272'):
                await self.add_pengar(userID, -int(antal))
                msg = " {} blev av med {} pengar!".format(user.mention, int(antal)) + " {} har {} pengar!".format(user.mention, await self.check_pengar(userID))
                await ctx.send(msg)
            else:
                msg = "nej " + ctx.message.author.mention
                await ctx.send(msg)
        else:
            await ctx.send("Skriv korrekt! !help pengar, om du behöver hjälp " + ctx.message.author.mention)
        await self.save_users()

    @commands.command(pass_context = True)
    async def butik(self, ctx):

        for i in range(len(varor)):
            await ctx.send("{}: {} pengar".format(varor[i], pris[i]))

    @commands.command(pass_context = True)
    async def köp(self, ctx, vara: str = None):

        id = str(ctx.message.author.id)

        if not vara:
            await ctx.send("Välj vad du ska köpa! " + ctx.message.author.mention)
        elif (vara == 'lambsauce'):
            if (await self.check_pengar(id) >= pris[0]):
                await self.add_vara(id, vara)
                await self.add_pengar(id, -pris[0])
                await ctx.send("Du köpte {} för {}! ".format(vara, pris[0]) + ctx.message.author.mention)
                print("{} har {} {}".format(ctx.message.author, self.users[id][vara], vara))
            else:
                await ctx.send("Så rik är du inte " + ctx.message.author.mention)
        elif (vara == 'brest'):
            if (await self.check_pengar(id) >= pris[1]):
                await self.add_vara(id, vara)
                await self.add_pengar(id, -pris[1])
                await ctx.send("Du köpte {} för {}! ".format(vara, pris[1]) + ctx.message.author.mention)
                print("{} har {} {}".format(ctx.message.author, self.users[id][vara], vara))
            else:
                await ctx.send("Så rik är du inte " + ctx.message.author.mention)
        else:
            await ctx.send("{} är inte en vara! Se butiken med !butik ".format(vara) + ctx.message.author.mention)
        await self.save_users()

    @commands.command(pass_context = True)
    async def inventarie(self, ctx, user : discord.Member = None):

        id = str(ctx.message.author.id)

        try:
            userID = str(user.id)
        except:
            print("inget id skrivit")
        if not user:
            await ctx.send("{}s Inventarie: {}".format(ctx.message.author.mention, self.users[id]))
        elif user:
            try:
                await ctx.send("{}s Inventarie: {}".format(user.mention, self.users[userID]))
            except Exception as e:
                await ctx.send(Exception)
                raise e
        await self.save_users()

    @commands.command(pass_context = True)
    async def flex(self,ctx, sak: str = None):

        id = str(ctx.message.author.id)

        if (self.users[id][sak] > 0) and (str(sak) == "lambsauce"):
            await ctx.send("https://imagesvc.meredithcorp.io/v3/mm/image?url=https%3A%2F%2Fassets.marthastewart.com%2Fstyles%2Fwmax-300%2Fd21%2Fa99872_0303_lambgravy%2Fa99872_0303_lambgravy_vert.jpg%3Fitok%3Dl70m_1A2")

        if (self.users[id][sak] > 0) and (str(sak) == "brest"):
            await ctx.send("https://image.shutterstock.com/image-photo/chicken-breast-stuffed-garlic-spinach-260nw-1353766883.jpg")
        await self.save_users()

async def setup(bot):
    await bot.add_cog(Pengar(bot))
