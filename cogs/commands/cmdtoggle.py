import discord
from discord.ext import commands
import aiosqlite
from utils.Tools import *

DB_PATH = "db/disabled_commands.db"

# Protected commands that can NEVER be disabled
PROTECTED_COMMANDS = {"enable", "disable", "disabledlist", "help", "jsk", "jishaku"}


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS disabled_commands (
                guild_id INTEGER,
                command_name TEXT,
                disabled_by INTEGER,
                PRIMARY KEY (guild_id, command_name)
            )
        """)
        await db.commit()


async def is_command_disabled(guild_id: int, command_name: str) -> bool:
    """Check if a command is disabled in a guild."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT 1 FROM disabled_commands WHERE guild_id = ? AND command_name = ?",
            (guild_id, command_name)
        ) as cursor:
            return await cursor.fetchone() is not None


class CommandToggle(commands.Cog):
    """Enable/Disable commands per server - persists across bot restarts."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(init_db())

    async def cog_load(self):
        # Add global check for disabled commands
        self.bot.add_check(self.global_disabled_check)

    async def cog_unload(self):
        # Remove global check when cog is unloaded
        self.bot.remove_check(self.global_disabled_check)

    async def global_disabled_check(self, ctx):
        """Global check that runs before every command."""
        if not ctx.guild:
            return True  # DMs always allowed

        cmd_name = ctx.command.qualified_name.lower()

        # Protected commands can never be disabled
        if cmd_name in PROTECTED_COMMANDS:
            return True

        # Owner bypass
        if ctx.author.id in self.bot.owner_ids:
            return True

        disabled = await is_command_disabled(ctx.guild.id, cmd_name)
        if disabled:
            embed = discord.Embed(
                description=f"<:warning:1448951779353038949> `{cmd_name}` command is **disabled** in this server.",
                color=0xFF0000
            )
            await ctx.send(embed=embed, delete_after=5)
            return False
        return True

    @commands.command(name="disable", usage="disable <command>", help="Disable a command in this server.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def disable_cmd(self, ctx, *, command_name: str):
        command_name = command_name.lower().strip()

        # Check if command exists
        cmd = self.bot.get_command(command_name)
        if not cmd:
            embed = discord.Embed(
                description=f"<:warning:1448951779353038949> Command `{command_name}` not found.",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        # Check if protected
        if command_name in PROTECTED_COMMANDS:
            embed = discord.Embed(
                description=f"<:warning:1448951779353038949> `{command_name}` is a protected command and **cannot be disabled**.",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        # Check if already disabled
        if await is_command_disabled(ctx.guild.id, command_name):
            embed = discord.Embed(
                description=f"<:warning:1448951779353038949> `{command_name}` is already **disabled** in this server.",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        # Disable it
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "INSERT INTO disabled_commands (guild_id, command_name, disabled_by) VALUES (?, ?, ?)",
                (ctx.guild.id, command_name, ctx.author.id)
            )
            await db.commit()

        embed = discord.Embed(
            description=f"<:ztick:1448951767990796298> `{command_name}` has been **disabled** in this server.\n"
                        f"Use `{ctx.prefix}enable {command_name}` to re-enable it.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="enable", usage="enable <command>", help="Enable a previously disabled command.")
    @blacklist_check()
    @ignore_check()
    @commands.has_permissions(administrator=True)
    async def enable_cmd(self, ctx, *, command_name: str):
        command_name = command_name.lower().strip()

        # Check if it's actually disabled
        if not await is_command_disabled(ctx.guild.id, command_name):
            embed = discord.Embed(
                description=f"<:warning:1448951779353038949> `{command_name}` is not disabled in this server.",
                color=0xFF0000
            )
            return await ctx.send(embed=embed)

        # Enable it
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "DELETE FROM disabled_commands WHERE guild_id = ? AND command_name = ?",
                (ctx.guild.id, command_name)
            )
            await db.commit()

        embed = discord.Embed(
            description=f"<:ztick:1448951767990796298> `{command_name}` has been **enabled** in this server.",
            color=0x00FF00
        )
        await ctx.send(embed=embed)

    @commands.command(name="disabledlist", aliases=["disabledcmds", "dcmds"], usage="disabledlist", help="Shows all disabled commands.")
    @blacklist_check()
    @ignore_check()
    async def disabled_list(self, ctx):
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT command_name FROM disabled_commands WHERE guild_id = ?",
                (ctx.guild.id,)
            ) as cursor:
                rows = await cursor.fetchall()

        if not rows:
            embed = discord.Embed(
                description="<:ztick:1448951767990796298> No commands are disabled in this server.",
                color=0x87CEEB
            )
            return await ctx.send(embed=embed)

        cmd_list = "\n".join([f"❌ `{row[0]}`" for row in rows])
        embed = discord.Embed(
            title="Disabled Commands",
            description=cmd_list,
            color=0xFF0000
        )
        embed.set_footer(text=f"Use {ctx.prefix}enable <command> to re-enable")
        await ctx.send(embed=embed)
