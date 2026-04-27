import discord
from discord.ext import commands
import re

class AntiScam(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Scam keywords & patterns
    SCAM_PATTERNS = [
        # Crypto / Money scams
        r'(?i)(crypto|bitcoin|btc|eth|usdt|tether).{0,30}(withdraw|bonus|reward|free|claim|promo)',
        r'(?i)(withdraw|withdrawal).{0,20}(success|completed|approved)',
        r'(?i)(claim|get|earn|win).{0,20}(\$\d+|\d+\s*\$|free\s*(money|crypto|btc|eth|usdt))',
        r'(?i)promo\s*code.{0,20}(beast|free|bonus|reward)',
        r'(?i)(giving\s*away|giveaway).{0,30}(\$\d+|\d+\s*\$|crypto|btc|usdt)',
        r'(?i)enter.{0,15}(promo|code|special).{0,15}(beast|free|bonus)',
        r'(?i)(rakeback|cashback).{0,20}(bonus|reward|percent|%)',
        r'(?i)activate\s*code.{0,20}(bonus|reward|free)',
        
        # Bio spam
        r'(?i)(check|see|look).{0,10}(my|the)\s*(bio|profile|link)',
        r'(?i)(sexcam|s3xcam|s\.e\.x|onlyfans|0nlyfans)',
        r'(?i)(nud[e3]s?|n\.u\.d\.e|p[o0]rn|h[o0]rny)\s.{0,15}(bio|profile|link|dm)',
        r'(?i)(18\+|adult).{0,15}(bio|profile|link|content)',
        r'(?i)in\s*my\s*bio',
        r'(?i)link\s*in\s*(bio|profile|description)',
        
        # Fake giveaway / nitro
        r'(?i)(free|f\.r\.e\.e)\s*(discord\s*)?nitro',
        r'(?i)(steam|discord|spotify)\s*(free|gift|premium)',
        r'(?i)gift\s*card.{0,20}(free|claim|get)',
        r'(?i)(airdrop|air\s*drop).{0,20}(claim|free|token)',
        
        # Phishing links
        r'(?i)(discord|discrod|dlscord|disc0rd)\s*\.?(gg|gift|app)\s*/\s*\w+',
        r'(?i)(steamcommunity|steampowered)\s*\.\s*(com|ru|net)',
        r'(?i)dsc\.gg/',
        
        # Investment scam
        r'(?i)(invest|trading).{0,20}(profit|guaranteed|return|daily)',
        r'(?i)(\d+x|\d+%)\s*(profit|return|daily|guaranteed)',
        r'(?i)send\s*(me\s*)?\d+.{0,10}(get|receive|return)\s*\d+',
    ]

    SCAM_WORDS = [
        'sexcam', 'check my bio', 'check bio', 'see my bio',
        'nudes in bio', 'link in bio', 'onlyfans',
        'free nitro', 'free crypto', 'withdrawal success',
        'claim your reward', 'promo code beast',
    ]

    def is_scam(self, content: str) -> bool:
        text = content.lower().strip()
        
        # Check exact scam words
        for word in self.SCAM_WORDS:
            if word in text:
                return True
        
        # Check regex patterns
        for pattern in self.SCAM_PATTERNS:
            if re.search(pattern, content):
                return True
        
        return False

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        
        # Skip if user has manage messages perm
        if message.author.guild_permissions.manage_messages:
            return
        
        if self.is_scam(message.content):
            try:
                await message.delete()
                
                warn_embed = discord.Embed(
                    color=0x87CEEB,
                    description=f"⚠️ **{message.author.mention}** scam/spam message detected aur delete kar diya gaya!\n\n"
                                f"Aise messages yahan allowed nahi hain 🛡️"
                )
                warn_embed.set_footer(text="Ariyan Anti-Scam Protection")
                
                warn_msg = await message.channel.send(embed=warn_embed)
                await warn_msg.delete(delay=5)
            except discord.Forbidden:
                pass

def setup(bot):
    bot.add_cog(AntiScam(bot))
