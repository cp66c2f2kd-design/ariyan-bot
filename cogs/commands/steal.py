import discord
from discord.ext import commands
from discord.ui import View, Button
import aiohttp
from io import BytesIO
import re
from utils.Tools import *

class Steal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Regex for custom emojis
    EMOJI_RE = re.compile(r'<(a?):([a-zA-Z0-9_]+):(\d+)>')

    async def fetch_bytes(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.read()
        return None

    @commands.hybrid_command(name="steal", help="Steal emoji/sticker from message or reply", usage="steal [emoji/url]", aliases=["eadd", "addemoji", "stealemoji"], with_app_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, *, emote: str = None):
        # 1) Check reply first
        if ctx.message.reference:
            try:
                ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            except:
                ref = None

            if ref:
                found = False

                # Stickers in replied message
                if ref.stickers:
                    for s in ref.stickers:
                        await self._steal_sticker_as_emoji(ctx, s)
                    found = True

                # Emojis in replied message text
                emojis_found = self.EMOJI_RE.findall(ref.content)
                if emojis_found:
                    for anim, name, eid in emojis_found:
                        ext = 'gif' if anim == 'a' else 'png'
                        url = f'https://cdn.discordapp.com/emojis/{eid}.{ext}'
                        await self._add_emoji(ctx, url, name, animated=(anim == 'a'))
                    found = True

                # Attachments (images) in replied message
                if ref.attachments:
                    for att in ref.attachments:
                        if any(att.filename.lower().endswith(e) for e in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                            name = att.filename.rsplit('.', 1)[0][:32]
                            animated = att.filename.lower().endswith('.gif')
                            await self._add_emoji(ctx, att.url, name, animated=animated)
                            found = True

                if found:
                    return

        # 2) Check if emoji given as argument
        if emote:
            # Custom emoji like <:name:id> or <a:name:id>
            match = self.EMOJI_RE.search(emote)
            if match:
                anim, name, eid = match.groups()
                ext = 'gif' if anim == 'a' else 'png'
                url = f'https://cdn.discordapp.com/emojis/{eid}.{ext}'
                await self._add_emoji(ctx, url, name, animated=(anim == 'a'))
                return

            # URL given directly
            if emote.startswith('http'):
                name = emote.rsplit('/', 1)[-1].rsplit('.', 1)[0][:32] or 'stolen'
                animated = '.gif' in emote.lower()
                await self._add_emoji(ctx, emote, name, animated=animated)
                return

            # Try as unicode emoji name - not supported
            embed = discord.Embed(description="❌ Default emojis steal nahi ho sakte!\nCustom emoji ya image URL de.", color=0x87CEEB)
            await ctx.send(embed=embed)
            return

        # 3) Check attachments on the command message itself
        if ctx.message.attachments:
            for att in ctx.message.attachments:
                if any(att.filename.lower().endswith(e) for e in ['.png', '.jpg', '.jpeg', '.gif', '.webp']):
                    name = att.filename.rsplit('.', 1)[0][:32]
                    animated = att.filename.lower().endswith('.gif')
                    await self._add_emoji(ctx, att.url, name, animated=animated)
            return

        # 4) Nothing found - show help
        embed = discord.Embed(
            title="🎯 Steal Command",
            description=(
                "**Kaise use kare:**\n\n"
                "**1.** Emoji steal → `!steal <emoji>`\n"
                "**2.** Reply se steal → Kisi message pe reply karo aur `!steal` likho\n"
                "**3.** Image se emoji → Image attach karo aur `!steal` likho\n"
                "**4.** URL se emoji → `!steal <image_url>`"
            ),
            color=0x87CEEB
        )
        embed.set_footer(text="Ariyan Anti-Scam Protection")
        await ctx.send(embed=embed)

    async def _steal_sticker_as_emoji(self, ctx, sticker):
        try:
            url = sticker.url
            name = re.sub(r'[^a-zA-Z0-9_]', '_', sticker.name)[:32]
            animated = sticker.format == discord.StickerFormatType.apng
            await self._add_emoji(ctx, url, name, animated=animated)
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"❌ Sticker steal fail: {e}", color=0x87CEEB))

    async def _add_emoji(self, ctx, url, name, animated=False):
        # Sanitize name
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        if len(name) < 2:
            name = 'stolen_emoji'
        name = name[:32]

        # Check slots
        if not self._has_slot(ctx.guild, animated):
            await ctx.send(embed=discord.Embed(description="❌ Emoji slots full hai! Server boost karo.", color=0x87CEEB))
            return

        try:
            img = await self.fetch_bytes(url)
            if not img:
                await ctx.send(embed=discord.Embed(description="❌ Image download nahi ho paya!", color=0x87CEEB))
                return

            # Check size (256KB limit for emojis)
            if len(img) > 256000:
                # Try to resize if pillow available
                try:
                    from PIL import Image
                    import io
                    pil_img = Image.open(BytesIO(img))
                    pil_img = pil_img.resize((128, 128), Image.LANCZOS)
                    buf = io.BytesIO()
                    fmt = 'GIF' if animated else 'PNG'
                    pil_img.save(buf, format=fmt)
                    img = buf.getvalue()
                except:
                    await ctx.send(embed=discord.Embed(description="❌ Image size bahut bada hai (256KB limit)!", color=0x87CEEB))
                    return

            emote = await ctx.guild.create_custom_emoji(name=name, image=img)
            embed = discord.Embed(description=f"✅ Emoji add ho gaya → {emote} **`:{emote.name}:`**", color=0x87CEEB)
            await ctx.send(embed=embed)

        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(description="❌ Mujhe emoji manage karne ki permission nahi hai!", color=0x87CEEB))
        except Exception as e:
            await ctx.send(embed=discord.Embed(description=f"❌ Fail: {str(e)[:100]}", color=0x87CEEB))

    def _has_slot(self, guild, animated):
        normal = sum(1 for e in guild.emojis if not e.animated)
        anim = sum(1 for e in guild.emojis if e.animated)
        limit = {0: 50, 1: 100, 2: 150, 3: 250}.get(guild.premium_tier, 50)
        return anim < limit if animated else normal < limit

    @commands.hybrid_command(name="stealsticker", help="Steal sticker from replied message", aliases=["stickeradd", "addsticker"], with_app_command=True)
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.has_permissions(manage_emojis=True)
    async def stealsticker(self, ctx):
        if not ctx.message.reference:
            await ctx.send(embed=discord.Embed(description="❌ Kisi sticker wale message pe **reply** karo!", color=0x87CEEB))
            return

        try:
            ref = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except:
            await ctx.send(embed=discord.Embed(description="❌ Message fetch nahi ho paya!", color=0x87CEEB))
            return

        if not ref.stickers:
            await ctx.send(embed=discord.Embed(description="❌ Reply kiye message mein koi sticker nahi hai!", color=0x87CEEB))
            return

        max_stickers = {0: 5, 1: 15, 2: 30, 3: 60}.get(ctx.guild.premium_tier, 5)
        if len(ctx.guild.stickers) >= max_stickers:
            await ctx.send(embed=discord.Embed(description="❌ Sticker slots full hai!", color=0x87CEEB))
            return

        for sticker in ref.stickers:
            try:
                name = re.sub(r'[^a-zA-Z0-9_ ]', '', sticker.name)[:30] or 'stolen'
                img_data = await self.fetch_bytes(sticker.url)
                if not img_data:
                    continue
                img = BytesIO(img_data)
                await ctx.guild.create_sticker(name=name, description="Stolen by Ariyan", file=discord.File(img, filename="sticker.png"), emoji="⭐")
                await ctx.send(embed=discord.Embed(description=f"✅ Sticker **{name}** add ho gaya!", color=0x87CEEB))
            except Exception as e:
                await ctx.send(embed=discord.Embed(description=f"❌ Sticker fail: {str(e)[:100]}", color=0x87CEEB))

