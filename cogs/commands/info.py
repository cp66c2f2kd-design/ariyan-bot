import discord
from discord.ext import commands
import aiohttp
import asyncio
import io
import json
import os
from datetime import datetime
from utils.Tools import *


# Supported regions for Free Fire
VALID_REGIONS = ["IND", "BR", "SG", "RU", "ID", "TW", "US", "VN", "TH", "ME", "PK", "CIS", "BD"]


def format_dt(ts):
    """Convert a timestamp to a readable date string."""
    try:
        if not ts or str(ts) == "0":
            return "N/A"
        return datetime.fromtimestamp(int(ts)).strftime('%d %b %Y, %I:%M %p')
    except:
        return "N/A"


class Info(commands.Cog):
    """Free Fire player info lookup commands."""

    def __init__(self, bot):
        self.bot = bot
        self.color = 0xFF0000
        self.api_base = os.getenv("INFO_API_URL", "https://api.farhanexe.xyz")
        self.dress_api = os.getenv("DRESS_API_URL", "https://www.farhanexe.xyz/apis/dress")

    @commands.hybrid_command(
        name="ffinfo",
        aliases=["playerinfo", "ff"],
        help="Get Free Fire player info by UID. Usage: ffinfo <uid> [region]",
        usage="ffinfo <uid> [region]"
    )
    @blacklist_check()
    @ignore_check()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx, uid: str = None, region: str = "IND"):
        """Fetch detailed Free Fire player information using a UID."""

        if not uid:
            embed = discord.Embed(
                title="❌ Missing UID",
                description="Please enter a UID: `ffinfo 12345678`\nOptional region: `ffinfo 12345678 IND`\n\n**Regions:** " + ", ".join(f"`{r}`" for r in VALID_REGIONS),
                color=0xF50505
            )
            await ctx.reply(embed=embed, delete_after=15)
            return

        region = region.upper()
        if region not in VALID_REGIONS:
            region = "IND"

        async with ctx.typing():
            api_url = f"{self.api_base}/info?uid={uid}"
            dress_url = f"{self.dress_api}?uid={uid}"

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=20)) as response:
                        if response.status == 200:
                            data = await response.json()

                            if isinstance(data, str):
                                data = json.loads(data)

                            if not data or "basicInfo" not in data:
                                raise Exception("User not found")

                            # Mapping data from JSON structure
                            basic = data.get('basicInfo', {})
                            clan = data.get('clanBasicInfo', {})
                            social = data.get('socialInfo', {})
                            pet = data.get('petInfo', {})
                            credit = data.get('creditScoreInfo', {})
                            profile = data.get('profileInfo', {})

                            # Skills list
                            skills = profile.get('equipedSkills', [])
                            if skills and isinstance(skills[0], dict):
                                skill_list = ", ".join([str(s.get('skillId')) for s in skills])
                            elif skills:
                                skill_list = ", ".join([str(s) for s in skills])
                            else:
                                skill_list = "None"

                            # Weapon skins
                            weapons = basic.get('weaponSkinShows', [])
                            weapon_list = ", ".join([str(w) for w in weapons]) if weapons else "None"

                            # Timestamps
                            created_at = format_dt(basic.get('createAt'))
                            last_login = format_dt(basic.get('lastLoginAt'))

                            embed = discord.Embed(color=self.color)

                            # Extra data
                            diamond = data.get('diamondCostRes', {})
                            prime = basic.get('primePrivilegeDetail', {})
                            achievements = data.get('equippedAch', [])
                            ach_list = ", ".join([str(a.get('achId', '')) for a in achievements]) if achievements else "None"

                            # Account type mapping
                            acc_type = basic.get('accountType', 0)
                            acc_type_str = {1: "Free", 2: "Premium"}.get(acc_type, str(acc_type))

                            # Gender
                            gender_raw = social.get('gender', 'N/A') if social else 'N/A'
                            gender = gender_raw.replace('Gender_', '') if isinstance(gender_raw, str) else str(gender_raw)

                            # Language
                            lang_raw = social.get('language', 'N/A') if social else 'N/A'
                            lang = lang_raw.replace('Language_', '') if isinstance(lang_raw, str) else str(lang_raw)

                            # Prime level
                            prime_level = prime.get('primeLevel', 0) if prime else 0
                            prime_str = f"Level {prime_level}" if prime_level else "None"

                            description = (
                                f"**ARIYAN - FF INFO v2**\n\n"

                                "🩷 **Basic Info** 🩷\n"
                                f"🟣 Nickname: `{basic.get('nickname', 'N/A')}`\n"
                                f"🟣 UID: `{basic.get('accountId', 'N/A')}`\n"
                                f"🟣 Level: {basic.get('level', 'N/A')} (Exp: {basic.get('exp', '0')})\n"
                                f"🟣 Region: {basic.get('region', region)}\n"
                                f"🟣 Account Type: {acc_type_str}\n"
                                f"🟣 Likes: {basic.get('liked', '0')}\n"
                                f"🟣 Honor Score: {credit.get('creditScore', '100')}\n"
                                f"🟣 Title ID: `{basic.get('title', 'None')}`\n\n"

                                "🦋 **Account Activity** 🦋\n"
                                f"🟣 Recent OB: {basic.get('releaseVersion', 'N/A')}\n"
                                f"🟣 Season: {basic.get('seasonId', 'N/A')}\n"
                                f"🟣 BP Badges: {basic.get('badgeCnt', '0')}\n"
                                f"🟣 BR Rank Points: {basic.get('rankingPoints', '0')}\n"
                                f"🟣 CS Rank Points: {basic.get('csRankingPoints', '0')}\n"
                                f"🟣 Max BR Rank: {basic.get('maxRank', 'N/A')}\n"
                                f"🟣 Max CS Rank: {basic.get('csMaxRank', 'N/A')}\n"
                                f"🟣 Created At: **{created_at}**\n"
                                f"🟣 Last Login: **{last_login}**\n\n"

                                "✨ **Guild & Social** ✨\n"
                                f"🟣 Signature: `{social.get('signature', 'No Signature') if social else 'No Signature'}`\n"
                                f"🟣 Gender: {gender}\n"
                                f"🟣 Language: {lang}\n"
                                f"🟣 Guild Name: {clan.get('clanName', 'No Guild')}\n"
                                f"🟣 Guild ID: {clan.get('clanId', 'N/A')}\n"
                                f"🟣 Guild Level: {clan.get('clanLevel', '0')}\n"
                                f"🟣 Live Members: {clan.get('memberNum', '0')}/{clan.get('capacity', '0')}\n"
                                f"🟣 Leader ID: {clan.get('captainId', 'N/A')}\n\n"

                                "⚔️ **Combat & Skills** ⚔️\n"
                                f"🟣 Equipped Skills: `{skill_list}`\n"
                                f"🟣 Weapon Skins: `{weapon_list}`\n"
                                f"🟣 Achievements: `{ach_list}`\n\n"

                                "💎 **Premium & Economy** 💎\n"
                                f"🟣 Diamond Cost: {diamond.get('diamondCost', '0')}\n"
                                f"🟣 Prime Status: {prime_str}\n\n"

                                "🩷 **Pet Details** 🩷\n"
                                f"🟣 Equipped?: {'Yes' if pet and pet.get('isSelected') else 'No'}\n"
                                f"🟣 Pet Name: {pet.get('name', 'N/A') if pet else 'No Pet'}\n"
                                f"🟣 Pet ID: {pet.get('id', 'N/A') if pet else 'N/A'}\n"
                                f"🟣 Pet Level: {pet.get('level', '0') if pet else '0'}\n"
                                f"🟣 Pet Skin: `{pet.get('skinId', 'None') if pet else 'None'}`\n"
                                f"🟣 Pet Skill: `{pet.get('selectedSkillId', 'None') if pet else 'None'}`"
                            )

                            embed.description = description
                            embed.set_thumbnail(url=ctx.author.display_avatar.url)

                            files_to_send = []
                            try:
                                async with session.get(dress_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                                    if resp.status == 200:
                                        dress_data = io.BytesIO(await resp.read())
                                        dress_file = discord.File(dress_data, filename="dress.png")
                                        embed.set_image(url="attachment://dress.png")
                                        files_to_send.append(dress_file)
                            except:
                                pass

                            embed.set_footer(
                                text=f"Requested by {ctx.author.name}",
                                icon_url=ctx.author.display_avatar.url
                            )
                            await ctx.reply(embed=embed, files=files_to_send)

                        else:
                            error_embed = discord.Embed(
                                title="❌ Error",
                                description="API Response Error!",
                                color=0xF50505
                            )
                            await ctx.reply(embed=error_embed)

                except Exception as e:
                    print(f"Info command error: {e}")
                    fail_embed = discord.Embed(
                        title="❌ Failed",
                        description=f"UID: `{uid}` not found or API issue.",
                        color=0xF50505
                    )
                    await ctx.reply(embed=fail_embed)
