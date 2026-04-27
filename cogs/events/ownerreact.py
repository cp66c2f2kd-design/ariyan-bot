import discord
from discord.ext import commands

class OwnerReact(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = 1383672814820655215

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id != self.owner_id:
            return
        if message.author.bot:
            return

        try:
            # Find emoji by name "a_owner2" from any server the bot is in
            emoji = discord.utils.get(self.bot.emojis, name="a_owner2")
            if emoji:
                await message.add_reaction(emoji)
            else:
                # Fallback: try partial match
                emoji = discord.utils.find(lambda e: "owner" in e.name.lower(), self.bot.emojis)
                if emoji:
                    await message.add_reaction(emoji)
        except:
            pass

def setup(bot):
    bot.add_cog(OwnerReact(bot))
