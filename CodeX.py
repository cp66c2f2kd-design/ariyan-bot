import os
os.system("")
import asyncio
import traceback
from threading import Thread
from datetime import datetime
import random
import time

import aiohttp
import discord
from discord import Spotify
from discord.ext import commands, tasks

from core import Context
from core.Cog import Cog
from core.zyrox import zyrox
from utils.Tools import *
from utils.config import *

import jishaku
import cogs

os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
os.environ["JISHAKU_HIDE"] = "True"
os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
os.environ["JISHAKU_FORCE_PAGINATOR"] = "True"

from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("TOKEN")

# --- Configuration ---
# IMPORTANT: Replace these with your actual channel IDs.
SERVER_COUNT_CHANNEL_ID = 1419729255977189467  # Replace with your server count channel ID
USER_COUNT_CHANNEL_ID = 1419729283861184632    # Replace with your user count channel ID
LOG_CHANNEL_ID = 1396794297386532978 # Replace with the channel ID for join/leave logs


client = zyrox()
tree = client.tree

# --- Background Task for Stats ---
async def update_stats():
    """A background task to update server and user stats in channel names."""
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            servers = len(client.guilds)
            users = sum(guild.member_count for guild in client.guilds if guild.member_count is not None)
            
            server_channel = client.get_channel(SERVER_COUNT_CHANNEL_ID)
            user_channel = client.get_channel(USER_COUNT_CHANNEL_ID)
            
            if server_channel:
                await server_channel.edit(name=f"Servers: {servers}")
            
            if user_channel:
                await user_channel.edit(name=f"Users: {users}")
                
        except Exception as e:
            print(f"Error updating stats: {e}")
        
        await asyncio.sleep(600) # Update every 10 minutes

# --- Slash Command (Active Developer Badge) ---
@tree.command(name="activedev", description="Check if Ariyan is active for Developer Badge")
async def slash_activedev(interaction: discord.Interaction):
    latency = round(client.latency * 1000)
    embed = discord.Embed(
        title="✅ Active Developer",
        description=f"Ariyan is active! **Latency:** `{latency}ms`",
        color=0x87CEEB
    )
    embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- Event Handlers ---
@client.event
async def on_ready():
    await client.wait_until_ready()
    
    print("""
    _          _                   
   / \   _ __ (_) _   _  __ _ _ __  
  / _ \ | '__|| || | | |/ _` | '_ \ 
 / ___ \| |   | || |_| | (_| | | | |
/_/   \_\_|   |_| \__, |\__,_|_| |_|
                  |___/
       """)
    print("Loaded & Online!")
    print(f"Logged in as: {client.user}")
    print(f"Connected to: {len(client.guilds)} guilds")
    print(f"Connected to: {len(client.users)} users")
    try:
        synced = await client.tree.sync()
        all_commands = list(client.commands)
        print(f"Synced Total {len(all_commands)} Client Commands and {len(synced)} Slash Commands")
    except Exception as e:
        print(e)
        
    client.loop.create_task(update_stats())


@client.event
async def on_guild_join(guild: discord.Guild):
    # Log when the bot joins a server
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(f"Ariyan has been added to the server: **{guild.name}** (ID: `{guild.id}`)")

@client.event
async def on_command_completion(context: commands.Context) -> None:
    if context.author.id == 870179991462236170:
        return

    full_command_name = context.command.qualified_name
    split = full_command_name.split("\n")
    executed_command = str(split[0])
    webhook_url = "https://discord.com/api/webhooks/1393938120575029278/DZfp7Irx4oQprKZ1LjouSCZGKawEesXo4YMuIj7x5XspS24WTamTzKG4TqQan125_Qfw"
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(webhook_url, session=session)

        embed_color = 0x87CEEB
        embed = discord.Embed(color=embed_color)
        avatar_url = context.author.display_avatar.url

        embed.set_author(name=f"Cmd Executed: {executed_command}", icon_url=avatar_url)
        embed.set_thumbnail(url=avatar_url)

        if context.guild is not None:
            embed.add_field(name="User", value=f"{context.author.mention} (`{context.author.id}`)", inline=False)
            embed.add_field(name="Server", value=f"{context.guild.name} (`{context.guild.id}`)", inline=False)
            embed.add_field(name="Channel", value=f"{context.channel.mention} (`{context.channel.id}`)", inline=False)
        else:
            embed.add_field(name="User (DM)", value=f"{context.author.mention} (`{context.author.id}`)", inline=False)
        
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text="Powered by Ariyan ❤️", icon_url=client.user.display_avatar.url)
        
        try:
            await webhook.send(embed=embed)
        except Exception as e:
            print(f'Command log webhook failed: {e}')


# --- Utility Commands ---
@client.command(name='spotify')
async def spotify(ctx: Context, user: discord.Member = None):
    """Shows what a user is listening to on Spotify."""
    user = user or ctx.author
    spotify_activity = next((activity for activity in user.activities if isinstance(activity, Spotify)), None)

    if not spotify_activity:
        return await ctx.send(f"{user.name} is not listening to Spotify.")
    
    embed = discord.Embed(
        title=f"{user.name}'s Spotify",
        description=f"**Listening to:** {spotify_activity.title}",
        color=0x1DB954 # Spotify Green
    )
    embed.set_thumbnail(url=spotify_activity.album_cover_url)
    embed.add_field(name="Artist", value=spotify_activity.artist)
    embed.add_field(name="Album", value=spotify_activity.album)
    embed.set_footer(text=f"Song started at {spotify_activity.created_at.strftime('%H:%M')}")
    await ctx.send(embed=embed)


@client.command(name='makeinvite', aliases=['createinvite', 'makeinv'])
@commands.is_owner()
async def make_invite(ctx: Context, guild_id: int = None):
    """Creates an invite for a specified server (owner only)."""
    if guild_id is None:
        return await ctx.send("Please provide a Guild ID.")
        
    guild = client.get_guild(guild_id)
    if not guild:
        return await ctx.send("Invalid Guild ID. I am not in that server.")

    if guild.system_channel and guild.system_channel.permissions_for(guild.me).create_instant_invite:
        try:
            invite = await guild.system_channel.create_invite(max_age=0, max_uses=0, unique=True, reason="Owner requested invite.")
            return await ctx.send(f"Invite for **{guild.name}**:\n{invite.url}")
        except Exception:
            pass

    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).create_instant_invite:
            try:
                invite = await channel.create_invite(max_age=0, max_uses=0, unique=True, reason="Owner requested invite.")
                return await ctx.send(f"Invite for **{guild.name}** (from #{channel.name}):\n{invite.url}")
            except Exception:
                continue
                
    await ctx.send(f"I don't have 'Create Instant Invite' permission in any channel in **{guild.name}**.")


# --- Webhook Management Commands ---
@client.command(name='create_hook', aliases=['makehook'])
@commands.has_permissions(administrator=True)
async def create_hook(ctx: Context, *, name: str = None):
    """Creates a webhook in the current channel."""
    if name is None:
        return await ctx.send("Please provide a name for the webhook.")
    
    try:
        webhook = await ctx.channel.create_webhook(name=name, reason=f"Created by {ctx.author}")
        embed = discord.Embed(
            title="✅ Webhook Created",
            description=f"A webhook named **{webhook.name}** was created.",
            color=0x87CEEB
        )
        await ctx.author.send(f"Webhook URL for **{webhook.name}** in **{ctx.channel.name}**:\n||{webhook.url}||", embed=embed)
        await ctx.send("Webhook created. I've sent the URL to your DMs.")
    except discord.Forbidden:
        await ctx.send("I don't have permission to create webhooks here.")
    except Exception:
        await ctx.send(f"Webhook created: **{webhook.name}**\n||{webhook.url}||\n(I could not DM you the URL.)")


@client.command(name='delete_hook', aliases=['delhook'])
@commands.has_permissions(administrator=True)
async def delete_hook(ctx: Context, webhook_url: str = None):
    """Deletes a webhook using its URL."""
    if webhook_url is None:
        return await ctx.send("Please provide the webhook URL to delete.")

    try:
        async with aiohttp.ClientSession() as session:
            webhook = await discord.Webhook.from_url(webhook_url, session=session)
            await webhook.delete(reason=f"Deleted by {ctx.author}")
        await ctx.send("✅ Webhook deleted successfully.")
    except (discord.NotFound, ValueError):
        await ctx.send("❌ Webhook not found or URL is invalid.")


@client.command(name='list_hooks', aliases=['hooks'])
@commands.has_permissions(administrator=True)
async def list_hooks(ctx: Context):
    """Lists all webhooks in the current channel."""
    try:
        webhooks = await ctx.channel.webhooks()
        if not webhooks:
            return await ctx.send("No webhooks found in this channel.")

        embed = discord.Embed(title=f"Webhooks in #{ctx.channel.name}", color=0x87CEEB)
        description = "\n".join([f"**Name:** {wh.name} | **ID:** `{wh.id}`" for wh in webhooks])
        embed.description = description
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have permission to view webhooks in this channel.")


# --- Game Command ---
@client.command()
async def reaction(ctx: Context):
    """See how fast you can react to the correct emoji."""
    emojis = ["🍪", "🎉", "🧋", "🍒", "🍑", "💸", "🌙", "💕"]
    correct_emoji = random.choice(emojis)
    random.shuffle(emojis)
    
    embed = discord.Embed(
        title="Reaction Test",
        description="I will show an emoji in a few seconds. Get ready to click it!",
        color=0x87CEEB
    )
    message = await ctx.send(embed=embed)
    
    for emoji in emojis:
        await message.add_reaction(emoji)
        
    await asyncio.sleep(random.uniform(2.0, 7.0))
    
    embed.description = f"**GET THE {correct_emoji} EMOJI!**"
    await message.edit(embed=embed)
    start_time = time.time()

    def check(reaction, user):
        return (
            reaction.message.id == message.id
            and str(reaction.emoji) == correct_emoji
            and user == ctx.author
        )

    try:
        reaction, user = await client.wait_for("reaction_add", timeout=15.0, check=check)
        end_time = time.time()
        reaction_time = end_time - start_time
        
        embed.description = f"{user.mention} got the {correct_emoji} in **{reaction_time:.2f} seconds**!"
        await message.edit(embed=embed)
    except asyncio.TimeoutError:
        embed.description = "Timeout! You were too slow."
        await message.edit(embed=embed)


# --- Keep Alive Server + Dashboard ---
from flask import Flask, jsonify, send_from_directory
from threading import Thread
import time

# Try multiple paths for dashboard
_base = os.path.dirname(os.path.abspath(__file__))
_candidates = [
    os.path.join(_base, 'web'),               # Same dir (cloud deploy)
    os.path.join(_base, '..', '..', 'web'),    # BOT/bot/ZyroX -> BOT/web
    os.path.join(_base, '..', 'web'),           # BOT/bot -> BOT/web
    r'C:\Users\senpai\Documents\exe\BOT\web',  # Absolute fallback
]
DASHBOARD_DIR = next((p for p in _candidates if os.path.isdir(p)), _candidates[0])
app = Flask(__name__, static_folder=DASHBOARD_DIR)
bot_start_time = time.time()

@app.route('/')
def home():
    return send_from_directory(DASHBOARD_DIR, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(DASHBOARD_DIR, filename)

@app.route('/api/stats')
def api_stats():
    try:
        uptime_sec = int(time.time() - bot_start_time)
        hours, remainder = divmod(uptime_sec, 3600)
        minutes, _ = divmod(remainder, 60)
        uptime_str = f"{hours}h {minutes}m"
        
        import psutil
        process = psutil.Process(os.getpid())
        ram = round(process.memory_info().rss / 1024 / 1024)
    except:
        ram = 0
        uptime_str = "0h 0m"

    guild_count = len(client.guilds) if client.is_ready() else 0
    user_count = sum(g.member_count or 0 for g in client.guilds) if client.is_ready() else 0
    latency = round(client.latency * 1000) if client.is_ready() else 0
    cog_count = len(client.cogs) if client.is_ready() else 0

    return jsonify({
        "status": "online" if client.is_ready() else "offline",
        "botUser": str(client.user) if client.is_ready() else "Ariyan Bot",
        "botId": str(client.user.id) if client.is_ready() else "1498197753774473308",
        "avatar": str(client.user.avatar.url) if client.is_ready() and client.user.avatar else "",
        "servers": guild_count,
        "users": user_count,
        "ping": latency,
        "ram": ram,
        "uptime": uptime_str,
        "commands": "350+",
        "cogs": cog_count,
        "slashCommands": 89,
        "runtime": "Python 3.12 / discord.py",
        "prefix": "!",
        "language": "hi",
        "timezone": "Asia/Kolkata",
        "founder": "Ariyan",
        "founderId": "1383672814820655215",
        "supportServer": "https://discord.gg/PkDre8Juhp"
    })

def run():
    app.run(host='0.0.0.0', port=19346)

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()

# --- Main Bot Execution ---
async def main():
    async with client:
        os.system("clear")
        await client.load_extension("jishaku")
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                await client.start(TOKEN)
                break
            except discord.HTTPException as e:
                if e.status == 429: # Rate limited
                    wait_time = min((2 ** attempt) + random.random(), 60)
                    print(f"Rate limited. Retrying in {wait_time:.2f} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
        else:
            raise Exception("Bot failed to start after multiple retries due to rate limiting.")

if __name__ == "__main__":
    asyncio.run(main())
