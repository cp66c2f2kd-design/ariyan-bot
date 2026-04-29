import discord
from discord.ext import commands


class _ffinfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """FF Info commands"""
  
    def help_custom(self):
		      emoji = '<:zyroxthunder:1448949415200034907>'
		      label = "FF Info"
		      description = "Show you Commands of FF Info"
		      return emoji, label, description

    @commands.group()
    async def __FFInfo__(self, ctx: commands.Context):
        """`ffinfo <uid>` , `playerinfo <uid>` , `ff <uid>`"""
        pass
