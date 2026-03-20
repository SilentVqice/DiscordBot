import io
import discord
import logging
import os
import json
import asyncio
import aiohttp
import random
import html
import sys
import time
import re
import yt_dlp as youtube_dl
import yt_dlp.utils as ytdlp_utils
from pathlib import Path
from PIL import Image, ImageFont, ImageOps
from discord.ext.commands import Bot, before_invoke
from dotenv import load_dotenv
from discord import AllowedMentions
from discord.ext import commands
from typing import Any, cast

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.presences = True

bot = Bot(command_prefix=';', intents=intents, help_command=None)

def voice_runtime_info():
    try:
        import nacl
        nacl_status = f"ok ({nacl.__version__})"
    except Exception as e:
        nacl_status = f"missing ({e.__class__.__name__})"
    try:
        import davey
        dave_status = f"ok ({getattr(davey, '__version__', 'installed')})"
    except Exception as e:
        dave_status = f"missing ({e.__class__.__name__})"
    return f"Runtime: `{sys.executable}` | nacl: {nacl_status} | davey: {dave_status}"

############################################ R.I.C.H  P.R.E.S.E.N.C.E. ############################################

##################################################### H.E.L.P #####################################################
help_data = {
    "Moderation": {
        "ban": {
            "usage": ";ban @user [reason]",
            "description": "Bans a member from the server.",
            "example": [";ban @user Breaking rules"]
        },
        "unban": {
            "usage": ";unban <user_id> [reason]",
            "description": "Unbans a member by their Discord user ID.",
            "example": [";unban 123456789012345678 Appeal accepted"]
        },
        "kick": {
            "usage": ";kick @user [reason]",
            "description": "Kicks a member from the server.",
            "example": [";kick @user Spamming"]
        },
        "mute": {
            "usage": ";mute @user [duration] [reason]",
            "description": "Mutes a member, optionally for a set time.",
            "example": [";mute @user 10m Spam"]
        },
        "unmute": {
            "usage": ";unmute @user [reason]",
            "description": "Unmutes a member by removing the muted role.",
            "example": [";unmute @user"]
        }
    },

    "Utility": {
        "help":{
            "usage": ";help [command]",
            "description": "Shows all commands or detailed help for one command.",
            "example": [";help", ";help play"]
        },
        "info": {
            "usage": ";info [@user]",
            "description": "Shows information about you or another user.",
            "example": [";info", ";info @Velourie"]
        },
        "purge": {
            "usage": ";purge <amount>",
            "description": "Deletes a number of messages from the channel.",
            "example": [";purge 10"]
        }
    },
    "Fun": {
        "kitty": {
            "usage": ";kitty",
            "description": "Sends a random cat image.",
            "example": [";kitty"]
        },
        "bunny": {
            "usage": ";bunny",
            "description": "Sends a random bunny image.",
            "example": [";bunny"]
        },
        "trivia": {
            "usage": ";trivia",
            "description": "Starts a trivia question.",
            "example": [";trivia"]
        },
        "flag": {
            "usage": ";flag",
            "description": "Starts a country flag guessing game.",
            "example": [";flag"]
        },
        "connect4": {
            "usage": ";connect4 [@user]",
            "description": "Play Connect 4 against a user or the bot.",
            "example": [";connect4", ";connect4 @user", ";c4 @user"],
            "aliases": ["c4"]
        },
        "rps": {
            "usage": ";rps [@user]",
            "description": "Play Rock, Paper, Scrissors against a user or the bot.",
            "example": [";rps", ";rps @user"]
        },
        "ttt": {
            "usage": ";ttt [@user]",
            "description": "Play Tic Tac Toe against a user or the bot.",
            "example": [";ttt", ";ttt @user"]
        }
    },
    "Music": {
        "join": {
            "usage": ";join",
            "description": "Joins your current voice channel.",
            "example": [";join"]
        },
        "play": {
            "usage": ";play <song name or URL>",
            "description": "Adds a song to the queue or starts playback.",
            "example": [";play Despacito", ";play https://youtube.com/watch?v=..."]
        },
        "pause": {
            "usage": ";pause",
            "description": "Pauses the current song.",
            "example": [";pause"]
        },
        "resume": {
            "usage": ";resume",
            "description": "Resumes the paused song.",
            "example": [";resume"]
        },
        "skip": {
            "usage": ";skip",
            "description": "Skips the current song.",
            "example": [";skip"]
        },
        "queue": {
            "usage": ";queue",
            "description": "Shows the current queue.",
            "example": [";queue"]
        },
        "remove": {
            "usage": ";remove <number>",
            "description": "Removes a song from the queue.",
            "example": [";remove 2"]
        },
        "clear": {
            "usage": ";clear",
            "description": "Clears the queue.",
            "example": [";clear"]
        },
        "leave": {
            "usage": ";leave",
            "description": "Stops playback and disconnects from voice.",
            "example": [";leave"]
        },
        "loop": {
            "usage": ";loop [on/off]",
            "description": "Toggles looping for the current song.",
            "example": [";loop", ";loop on", ";loop off"]
        },
        "shuffle": {
            "usage": ";shuffle",
            "description": "Shuffles the current queue.",
            "example": [";shuffle"]
        },
        "volume": {
            "usage": ";volume <0-200>",
            "description": "Sets playback volume.",
            "example": [";volume 50", ";volume 100"]
        },
        "slowed": {
            "usage": ";slowed [on/off]",
            "description": "Toggles slowed mode.",
            "example": [";slowed", ";slowed on", ";slowed off"]
            },
        "sped": {
            "usage": ";sped [on/off]",
            "description": "Toggles sped mode.",
            "example": [";sped", ";sped on", ";sped off"]
        },
        "bassboost": {
            "usage": ";bassboost [on/off]",
            "description": "Toggles bassboost mode.",
            "example": [";bassboost", ";bassboost on", ";bassboost off"]
        },
        "lyrics": {
            "usage": ";lyrics",
            "description": "Shows lyrics for the current track.",
            "example": [";lyrics"]
        }
    }
}

def find_help_entry(command_name: str):
    command_name = command_name.lower()

    for category, commands_dict in help_data.items():
        for name, info in commands_dict.items():
            aliases = [a.lower() for a in info.get("aliases", [])]
            if command_name == name.lower() or command_name in aliases:
                return category, name, info

    return None, None, None

@bot.command(name="help")
async def help_command(ctx, command_name: str = None):
    if command_name is None:
        embed = discord.Embed(
            title="✨ Bot Help",
            description=(
                "Here are all available commands.\n"
                "Use `;help <command>` for detailed information."
            ),
            colour=discord.Color.blurple()
        )

        embed.set_author(
            name=bot.user.name,
            icon_url=bot.user.display_avatar.url if bot.user else None
        )

        category_emojis = {
            "Utility": "🛠️",
            "Moderation": "🛡️",
            "Fun": "🎮",
            "Music": "🎵"
        }

        for category, commands_dict in help_data.items():
            emoji = category_emojis.get(category, "•")
            value = "\n".join(
                f"`;{name}` — {info['description']}"
                for name, info in commands_dict.items()
            )
            embed.add_field(
                name=f"{emoji} {category}",
                value=value,
                inline=False
            )

        embed.add_field(
            name="Made with love by",
            value=f"<@465610916873109504> and <@812269541731074078>",
            inline=False
        )
        embed.set_footer(text=f"Total commands: {sum(len(x) for x in help_data.values())}")
        return await ctx.send(embed=embed)

    category, name, info = find_help_entry(command_name)

    if info is None:
        return await ctx.send(f"⚠️ No help found for `{command_name}`.")

    embed = discord.Embed(
        title = f"📘 ;{name}",
        description=info["description"],
        colour=discord.Color.blue()
    )

    embed.add_field(name="Usage", value=f"`{info['usage']}`", inline=False)

    examples = "\n".join(f"`{example}`" for example in info.get("example", []))
    if examples:
        embed.add_field(name="Examples", value=examples, inline=False)

    aliases = info.get("aliases")
    if aliases:
        embed.add_field(
            name="Aliases",
            value=", ".join(f"`;{alias}`" for alias in aliases),
            inline=False
        )

    embed.add_field(name="Category", value=category, inline=True)
    embed.set_footer(text="< > = required | [ ] = optional")

    await ctx.send(embed=embed)

#################################################  U.T.I.L.I.T.Y  ##################################################

# REACTION ROLES DEPOSITORY -----------------------------------------------------------------------------------------
async def setup_reaction_message():
    channel = bot.get_channel(1483259632385396926)
    message_file = "reaction_message.json"
    if not channel:
        return
    message_id = None
    if os.path.exists(message_file):
        with open(message_file, "r") as f:
            data = json.load(f)
            message_id = data.get("message_id")

    message = None

    if message_id:
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            message = None
    if message is None:
        embed = discord.Embed(
            title="React to get your roles!",
            description="React with <:bed:1483254053227200584> to get the **RBW** role!",
            colour=discord.Color.red()
        )
        message = await channel.send(embed=embed)
        await message.add_reaction("<:bed:1483254053227200584>")
        with open(message_file, "w") as f:
            json.dump({"message_id": message.id}, f)

# REACTION ROLES ADD ------------------------------------------------------------------------------------------------
@bot.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is None:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
        return

    member = guild.get_member(payload.user_id)
    if member is None:
        try:
            member = await guild.fetch_member(payload.user_id)
        except discord.NotFound:
            return
        except discord.HTTPException:
            return

    if member.bot:
        return
    emoji_to_role = {
        "<:bed:1483254053227200584>": 1483256278565523608
    }

    role_id = emoji_to_role.get(str(payload.emoji))
    if role_id is None:
        return

    role = guild.get_role(emoji_to_role[str(payload.emoji)])
    if role:
        await member.add_roles(role)
        print(f"Added {role.name} to {member.name}")

# REACTION ROLES REMOVE ---------------------------------------------------------------------------------------------
@bot.event
async def on_raw_reaction_remove(payload):
    if payload.guild_id is None:
        return

    guild = bot.get_guild(payload.guild_id)
    if guild is None:
            return

    try:
        member = await guild.fetch_member(payload.user_id)
    except discord.NotFound:
        return
    except discord.HTTPException:
        return

    if member.bot:
        return

    emoji_to_role = {
        "<:bed:1483254053227200584>": 1483256278565523608
    }

    role_id = emoji_to_role.get(str(payload.emoji))
    if role_id is None:
        return

    role = guild.get_role(role_id)
    if role:
        await member.remove_roles(role)
        print(f"Removed {role.name} from {member.name}")

# MEMBER COUNT ------------------------------------------------------------------------------------------------------
member_count_channel_id = 1483268373902000128

async def update_member_count(guild):
    channel = guild.get_channel(member_count_channel_id)
    if channel:
        await channel.edit(name=f"Members: {guild.member_count}")

@bot.event
async def on_member_remove(member):
    await update_member_count(member.guild)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online! :3")
    for guild in bot.guilds:
        await update_member_count(guild)
    await setup_reaction_message()

# RANDOM FUN STUFF -----------------------------------------------------------------------------------------------
@bot.command()
async def support(ctx):
    await ctx.send("🏳️‍⚧️")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    special_user_responses = {
        979934316429738035: "Mwah",
        812269541731074078: "<3",
        465610916873109504: "👑"
    }

    if bot.user in message.mentions:
        await message.channel.send("Hewwo :3")

    handled_mentions = set()
    for user in message.mentions:
        if user.id in special_user_responses and user.id not in handled_mentions:
            await message.channel.send(f"{special_user_responses[user.id]}")
            handled_mentions.add(user.id)
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.BadArgument):
        return await ctx.send("I couldn't read that user. Try `;connect4` or `;connect4 @user`.")
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send("Missing argument for that command.")
    if isinstance(error, commands.CommandInvokeError) and isinstance(error.original, RuntimeError):
        message = str(error.original).lower()
        if "library needed" in message and "voice" in message:
            return await ctx.send(
                embed=error_embed(
                    f"Voice support is missing. Install `PyNaCl` and `davey`, then restart the bot.\n{voice_runtime_info()}",
                    title="Voice Support Missing"
                )
            )
    await ctx.send(f"Command error: {error}")

# WELCOME MESSAGE --------------------------------------------------------------------------------------------------
base_dir = Path(__file__).resolve().parent
assets_dir = base_dir / "assets"

background_path = assets_dir / "welcome_background.png"
font_path = assets_dir / "DejaVuSans-Bold.ttf"

card_width = 1000
card_height = 350
#avatar_size = 180

def load_font(size: int):
    if font_path.exists():
        return ImageFont.truetype(str(font_path), size)
    return ImageFont.load_default()

async def fetch_avatar_bytes(member: discord.Member) -> bytes:
    avatar_asset = member.display_avatar.replace(size=256)
    return await avatar_asset.read()

#def create_circular_avatar(avatar_bytes: bytes, size: int) -> Image.Image:
#    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")
#    avatar = ImageOps.fit(avatar, (size, size), method=Image.Resampling.LANCZOS)

#    mask = Image.new("L", avatar.size, 0)
#    draw = ImageDraw.Draw(mask)
#    draw.ellipse((0, 0, size, size), fill=255)

#    circular_avatar = Image.new("RGBA", (size, size), (0, 0, 0, 0))
#    circular_avatar.paste(avatar, (0,0), mask)
#    return circular_avatar

def fit_background() -> Image.Image:
    background = Image.open(background_path).convert("RGBA")
    return ImageOps.fit(
        background,
        (card_width, card_height),
        method=Image.Resampling.LANCZOS
    )

#def add_overlay(base: Image.Image) -> None:
#    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
#    draw = ImageDraw.Draw(overlay)
#    draw.rounded_rectangle(
#        (30, 30, card_width - 30, card_height - 30),
#        radius = 30,
#        fill=(0, 0, 0, 120),
#    )
#    base.alpha_composite(overlay)

def build_welcome_card(avatar_bytes: bytes, member: discord.Member) -> io.BytesIO:
    card = fit_background()

    output = io.BytesIO()
    card.save(output, format="PNG")
    output.seek(0)
    return output

@bot.event
async def on_member_join(member):
    await update_member_count(member.guild)
    channel = member.guild.get_channel(1483276233818112202)
    if channel is None:
        return

    print(f"Current working directory: {Path.cwd()}")
    print(f"Resolved background path: {background_path}")
    print(f"Background exists: {background_path.exists()}")

    if not background_path.exists():
        embed = discord.Embed(
            title=f"Welcome to the server, {member.display_name}!",
            description="We're very happy to have you here buh buh",
            colour=discord.Color.green(),
        )
        embed.set_footer(text="Missing welcome background image.")
        await channel.send(
            content=f"Welcome {member.mention}!",
            embed=embed
        )
        return

    avatar_bytes = await fetch_avatar_bytes(member)
    welcome_image = build_welcome_card(avatar_bytes, member)

    file = discord.File(fp=welcome_image, filename="welcome.png")

    embed = discord.Embed(
        title=f"Welcome to the server, {member.display_name}!",
        description="buh buh buh",
        colour=discord.Color.green(),
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url="attachment://welcome.png")
    embed.set_footer(text="Enjoy your stay!")

    await channel.send(
        content=f"Welcome {member.mention}!",
        embed=embed,
        file=file,
    )

# AUTO-ROLE --------------------------------------------------------------------------------------------------------
    default_role_id = 1483280765092630669
    role = member.guild.get_role(default_role_id)
    if role:
        await member.add_roles(role)
        print(f"Added {role.name} to {member.name}.")

# WHO IS -----------------------------------------------------------------------------------------------------------
@bot.command()
async def info(ctx, member: discord.Member = None):
    """Usage:
    ;info @Member
    If no member is mentioned, it shows info about the author"""
    member = member or ctx.author

    roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]
    roles_display = ", ".join(roles) if roles else "No roles."
    roles_count = len(roles)

    created = member.created_at.strftime("%d %b %Y %H:%M:%S")
    joined = member.joined_at.strftime("%d %b %Y %H:%M:%S")

    allowed = AllowedMentions(users=True)
    embed = discord.Embed(
        title=f"User info",
        colour=member.color
    )
    embed.add_field(name="Member", value=member.mention, inline=True)

    embed.set_author(name=str(member),icon_url=member.avatar.url if member.avatar else None)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Account Created", value=created, inline=True)
    embed.add_field(name="Joined Server", value=joined, inline=True)
    embed.add_field(name=f"Roles [{roles_count}]", value=roles_display, inline=False)

    await ctx.send(mention_author=True, embed=embed, allowed_mentions=allowed)
################################################ M.O.D.E.RA.T.I.O.N ################################################

# PURGE ------------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Deletes a number of messages from the channel."""
    if amount < 1:
        return
    deleted = await ctx.channel.purge(limit=amount)
    await ctx.send(f"Deleted {len(deleted)} messages.", delete_after=5)

# KICK -------------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kicks a member from the server."""
    try:
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked. Reason: {reason}", delete_after=5)
    except discord.Forbidden:
        await ctx.send("I do not have permission to kick this user!", delete_after=5)

# BAN --------------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Bans a member from the server."""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned. Reason: {reason}", delete_after=5)
    except discord.Forbidden:
        await ctx.send("I do not have permission to ban this user!", delete_after=5)

# UNBAN ------------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int, reason=None):
    """Unbans a member by their Discord user ID
    Usage: ;unban 123456789012345678"""

    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"{user.mention} has been unbanned. Reason: {reason}", delete_after=5)
    except discord.NotFound:
        await ctx.send("This user is not banned.", delete_after=5)
    except discord.Forbidden:
        await ctx.send("I do not have permission to unban this user!", delete_after=5)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", delete_after=5)

# MUTE ------------------------------------------------------------------------------------------------------------
MUTED_ROLE_ID = 1483291125778354176

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str = None, *, reason=None):
    """Mutes a member, optionally for a set time.
    Duration format example: 10s, 5m, 2h, 1d"""
    role = ctx.guild.get_role(MUTED_ROLE_ID)
    if role in member.roles:
        await ctx.send(f"{member.mention} is already muted.", delete_after=5)
        return
    await member.add_roles(role, reason=reason)
    msg = f"{member.mention} has been muted."
    if reason:
        msg += f" Reason: {reason}"
    if duration:
        msg += f" Duration: {duration}"
    await ctx.send(msg, delete_after=5)

    if duration:
        seconds = parse_duration(duration)
        if seconds:
            await asyncio.sleep(seconds)
            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"{member.mention} has been automatically unmuted after {duration}.", delete_after=5)
def parse_duration(duration):
    """Converts a string like '10s', '5m', '2h', '1d' into seconds"""
    try:
        unit = duration[-1]
        amount = int(duration[:-1])
        if unit == "s":
            return amount
        elif unit == "m":
            return amount * 60
        elif unit == "h":
            return amount * 3600
        elif unit == "d":
            return amount * 86400

        return None
    except (ValueError, IndexError):
        return None

# UNMUTE ----------------------------------------------------------------------------------------------------------
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    """Unmutes a member by removing the Muted role."""
    role = ctx.guild.get_role(MUTED_ROLE_ID)
    if role not in member.roles:
        await ctx.send(f"{member.mention} is not muted.", delete_after=5)
        return
    try:
        await member.remove_roles(role, reason=reason)
        await ctx.send(f"{member.mention} has been unmuted.", delete_after=5)
    except discord.Forbidden:
        await ctx.send("I do not have permission to unmute this user!", delete_after=5)

##################################################### F.U.N #######################################################
# PICTURES --------------------------------------------------------------------------------------------------------

# Cat
@bot.command()
async def kitty(ctx):
    """Sends a random cat image."""
    url = "https://api.thecatapi.com/v1/images/search"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send("Could not fetch a cat image right now.. Sorry! 😿")
            data = await resp.json()
            image_url = data[0]["url"]

            embed = discord.Embed(
                title="Kitty!",
                colour=discord.Color.pink()
            )
            embed.set_image(url=image_url)
            await ctx.send(embed=embed)
            return None

# Bunny
@bot.command()
async def bunny(ctx):
    """Sends a random bunny image."""
    url = "https://rabbit-api-two.vercel.app/api/random"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await ctx.send("Could not fetch a bunny right now 🐰")
            data = await resp.json()

    image_url = None

    possible = [
        data.get("image"),
        data.get("url"),
        data.get("link"),
        data.get("src"),
        data.get("image_url"),
    ]

    for p in possible:
        if isinstance(p, str) and p.startswith("http"):
            image_url = p
            break

    if not image_url:
        return await ctx.send("No valid bunny image found in API response 😢")

    embed = discord.Embed(
        title="Bunny!",
        colour=discord.Color.pink()
    )
    embed.set_image(url=image_url)

    await ctx.send(embed=embed)
    return None

# TRIVIA ----------------------------------------------------------------------------------------------------------
@bot.command()
async def trivia(ctx):
    url = "https://opentdb.com/api.php?amount=1&type=multiple"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    question_data = data["results"][0]

    question = html.unescape(question_data["question"])
    correct = html.unescape(question_data["correct_answer"])
    incorrect = [html.unescape(i) for i in question_data["incorrect_answers"]]

    answers = incorrect + [correct]
    random.shuffle(answers)

    letters = ["A", "B", "C", "D"]
    answer_map = dict(zip(letters, answers))

    description = ""
    for letter, answer in answer_map.items():
        description += f"**{letter}**. {answer}\n"

    embed = discord.Embed(
        title="🧠 Trivia Question",
        description=f"**{question}**\n\n{description}",
        colour=discord.Color.green()
    )

    await ctx.send(embed=embed)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.upper() in letters

    try:
        msg = await bot.wait_for("message", timeout=20, check=check)
    except asyncio.TimeoutError:
        return await ctx.send(f"⏰ Time's up! The correct answer was **{correct}**.")

    if answer_map[msg.content.upper()] == correct:
        await ctx.send("✅ Correct!")
    else:
        await ctx.send(f"❌ Wrong! The correct answer was **{correct}**.")
    return None

# FLAG TRIVIA ------------------------------------------------------------------------------------------------------
@bot.command()
async def flag(ctx):
    try:
        url = "https://restcountries.com/v3.1/all?fields=name,flags"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return await ctx.send("⚠️ API failed. Try again later.")
                data = await resp.json()

        valid = [
            c for c in data
            if "name" in c and "common" in c["name"]
            and "flags" in c and "png" in c["flags"]
        ]

        if not valid:
            return await ctx.send("⚠️ No valid countries found.")

        country = random.choice(valid)
        correct = country["name"]["common"]
        flag_url = country["flags"]["png"]

        embed = discord.Embed(
            title="🌍 Guess the Country!",
            description="What country does this flag belong to?",
            colour=discord.Color.blue()
        )
        embed.set_image(url=flag_url)
        await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        total_time = 25
        hint_task = None
        hint_sent = False

        async def scheduled_hint():
            nonlocal hint_sent
            await asyncio.sleep(10)
            if not hint_sent:
                hint_sent = True
                await ctx.send(f"💡 Hint: Starts with **{correct[0]}**")

        hint_task = asyncio.create_task(scheduled_hint())

        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining = total_time - elapsed
            if remaining <= 0:
                if not hint_task.done():
                    hint_task.cancel()
                return await ctx.send(f"⏰ Time's up! The answer was **{correct}**.")

            try:
                msg = await bot.wait_for("message", timeout=remaining, check=check)
            except asyncio.TimeoutError:
                if not hint_task.done():
                    hint_task.cancel()
                return await ctx.send(f"⏰ Time's up! The answer was **{correct}**.")

            if correct.lower() in msg.content.lower():
                if not hint_task.done():
                    hint_task.cancel()
                return await ctx.send("✅ Correct!")

            await ctx.send(f"❌ Wrong! Try again...")

            if not hint_sent:
                await ctx.send(f"💡 Hint: Starts with **{correct[0]}**")
                hint_sent = True

    except Exception as e:
        await ctx.send(f"Error: {e}")

# RPS --------------------------------------------------------------------------------------------------------------
emojis = {
    "rock": "🪨",
    "paper": "📄",
    "scissors": "✂️"
}

class RPSButton(discord.ui.Button):
    def __init__(self, label, view_ref):
        super().__init__(label=f"{emojis[label.lower()]} {label}", style=discord.ButtonStyle.primary)
        self.choice_lower = label.lower()
        self.choice_label = label
        self.view_ref = view_ref

    async def callback(self, interaction: discord.Interaction):
        if self.view_ref.pve:
            if interaction.user != self.view_ref.player1:
                return await interaction.response.send_message("This button isn’t for you!", ephemeral=True)
            player = self.view_ref.player1
        else:
            if interaction.user not in [self.view_ref.player1, self.view_ref.opponent]:
                return await interaction.response.send_message("This button isn’t for you!", ephemeral=True)
            player = interaction.user

        if player in self.view_ref.choices:
            return await interaction.response.send_message("You already chose!", ephemeral=True)

        self.view_ref.choices[player] = (self.choice_lower, self.choice_label)
        await interaction.response.send_message(
            f"You chose {emojis[self.choice_lower]} **{self.choice_label}**!",
            ephemeral=True
        )

        if self.view_ref.pve:
            bot_choice = random.choice(["rock", "paper", "scissors"])
            self.view_ref.choices[self.view_ref.opponent] = (bot_choice, bot_choice.capitalize())
            await self.view_ref.resolve(interaction)
        elif len(self.view_ref.choices) == 2:
            await self.view_ref.resolve(interaction)

class RPSView(discord.ui.View):
    def __init__(self, player1, opponent=None):
        super().__init__(timeout=60)
        self.player1 = player1
        self.opponent = opponent or bot.user
        self.choices = {}
        self.pve = opponent is None or opponent.bot

        for label in ["Rock", "Paper", "Scissors"]:
            self.add_item(RPSButton(label, self))

    async def resolve(self, interaction):
        p1, p2 = self.player1, self.opponent
        (c1_lower, c1_label) = self.choices[p1]
        (c2_lower, c2_label) = self.choices[p2]

        c1_emoji = emojis[c1_lower]
        c2_emoji = emojis[c2_lower]

        if c1_lower == c2_lower:
            result = "🤝 It's a tie!"
        elif (c1_lower == "rock" and c2_lower == "scissors") or \
             (c1_lower == "paper" and c2_lower == "rock") or \
             (c1_lower == "scissors" and c2_lower == "paper"):
            result = f"✅ {p1.mention} wins!"
        else:
            result = f"❌ {p2.mention} wins!"

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Rock, Paper, Scissors",
            description=f"{p1.mention} chose {c1_emoji} **{c1_label}**\n"
                        f"{p2.mention} chose {c2_emoji} **{c2_label}**\n"
                        f"{result}",
            colour=discord.Colour.blurple()
        )

        await interaction.message.edit(embed=embed, view=self)
        self.stop()

@bot.command()
async def rps(ctx, opponent: discord.Member = None):
    if opponent == ctx.author:
        return await ctx.send("You can't play against yourself!")

    view = RPSView(ctx.author, opponent)

    embed=discord.Embed(
        title="Rock, Paper, Scissors",
        description=f"{ctx.author.mention} vs {'🤖 Bot' if view.pve else opponent.mention}\nChoose your move below!",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=view)
    return None

# TIC TAC TOE ------------------------------------------------------------------------------------------------------
def build_ttt_embed(status: str, player_x, player_o):
    embed = discord.Embed(
        title="❌⭕ Tic Tac Toe",
        description=status,
        colour=discord.Color.blurple()
    )
    embed.add_field(name="❌ Player X", value=player_x.mention, inline=True)
    embed.add_field(name="⭕ Player O", value=player_o.mention, inline=True)
    embed.set_footer(text="Press a square to make your move.")
    return embed

WIN_COMBINATIONS = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


class TicTacToeButton(discord.ui.Button):
    def __init__(self, position: int):
        super().__init__(label="\u200b", style=discord.ButtonStyle.secondary, row=position // 3)
        self.position = position

    async def callback(self, interaction: discord.Interaction):
        view: TicTacToeView = self.view

        if interaction.user != view.player_x and interaction.user != view.player_o:
            return await interaction.response.send_message(
                "You are not part of this game.",
                ephemeral=True
            )

        if interaction.user != view.current_player:
            return await interaction.response.send_message(
                "It is not your turn.",
                ephemeral=True
            )

        if view.board[self.position] is not None:
            return await interaction.response.send_message(
                "That spot is already taken.",
                ephemeral=True
            )

        await view.make_move(interaction, self.position, interaction.user)


class TicTacToeView(discord.ui.View):
    def __init__(self, player_x: discord.Member, player_o: discord.abc.User, bot_player: bool = False):
        super().__init__(timeout=120)
        self.player_x = player_x
        self.player_o = player_o
        self.current_player = player_x
        self.board: list[str | None] = [None] * 9
        self.bot_player = bot_player
        self.message: discord.Message | None = None

        for i in range(9):
            self.add_item(TicTacToeButton(i))

    def get_button(self, position: int) -> TicTacToeButton | None:
        for item in self.children:
            if isinstance(item, TicTacToeButton) and item.position == position:
                return item
        return None

    def check_winner(self) -> str | None:
        for a, b, c in WIN_COMBINATIONS:
            if self.board[a] and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return None

    def is_draw(self) -> bool:
        return all(cell is not None for cell in self.board)

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True

    def available_moves(self) -> list[int]:
        return [i for i, cell in enumerate(self.board) if cell is None]

    def choose_bot_move(self) -> int:
        for move in self.available_moves():
            self.board[move] = "O"
            if self.check_winner() == "O":
                self.board[move] = None
                return move
            self.board[move] = None

        for move in self.available_moves():
            self.board[move] = "X"
            if self.check_winner() == "X":
                self.board[move] = None
                return move
            self.board[move] = None

        if 4 in self.available_moves():
            return 4

        corners = [i for i in [0, 2, 6, 8] if i in self.available_moves()]
        if corners:
            return random.choice(corners)

        return random.choice(self.available_moves())

    async def make_move(self, interaction: discord.Interaction, position: int, player: discord.abc.User):
        symbol = "X" if player == self.player_x else "O"
        self.board[position] = symbol

        button = self.get_button(position)
        if button is not None:
            button.label = symbol
            button.disabled = True
            button.style = discord.ButtonStyle.danger if symbol == "X" else discord.ButtonStyle.success

        winner = self.check_winner()
        if winner:
            self.disable_all_buttons()
            await interaction.response.edit_message(
                embed=build_ttt_embed(f"🎉 {player.mention} wins!", self.player_x, self.player_o),
                view=self,
                content=None
            )
            self.stop()
            return

        if self.is_draw():
            self.disable_all_buttons()
            await interaction.response.edit_message(
                embed=build_ttt_embed("It is a draw.", self.player_x, self.player_o),
                view=self,
                content=None
            )
            self.stop()
            return

        self.current_player = self.player_o if self.current_player == self.player_x else self.player_x
        current_symbol = "X" if self.current_player == self.player_x else "O"

        await interaction.response.edit_message(
            embed=build_ttt_embed(
                f"It is now {self.current_player.mention}'s turn ({current_symbol}).",
                self.player_x,
                self.player_o
            ),
            view=self,
            content=None
        )

        if self.bot_player and self.current_player == self.player_o and self.message:
            await self.handle_bot_turn()

    async def handle_bot_turn(self):
        await asyncio.sleep(1)

        move = self.choose_bot_move()
        self.board[move] = "O"

        button = self.get_button(move)
        if button is not None:
            button.label = "O"
            button.disabled = True
            button.style = discord.ButtonStyle.success

        winner = self.check_winner()
        if winner:
            self.disable_all_buttons()
            await self.message.edit(
                embed=build_ttt_embed(f"🎉 {self.player_o.mention} wins!", self.player_x, self.player_o),
                view=self,
                content=None
            )
            self.stop()
            return

        if self.is_draw():
            self.disable_all_buttons()
            await self.message.edit(
                embed=build_ttt_embed("It is a draw.", self.player_x, self.player_o),
                view=self,
                content=None
            )
            self.stop()
            return

        self.current_player = self.player_x
        await self.message.edit(
            embed=build_ttt_embed(
                f"It is now {self.player_x.mention}'s turn (X).",
                self.player_x,
                self.player_o
            ),
            view=self,
            content=None
        )

    async def on_timeout(self):
        self.disable_all_buttons()
        if self.message:
            try:
                await self.message.edit(
                    embed=build_ttt_embed("Game timed out.", self.player_x, self.player_o),
                    view=self,
                    content=None
                )
            except Exception:
                pass

@bot.command()
async def ttt(ctx, opponent: discord.Member = None):
    if opponent is None:
        view = TicTacToeView(ctx.author, ctx.me, bot_player=True)
        message = await ctx.send(
            embed=build_ttt_embed(
                f"It is now {ctx.author.mention}'s turn (X).",
                ctx.author,
                ctx.me
            ),
            view=view
        )
        view.message = message
        return

    if opponent.bot:
        return await ctx.send("You cannot use `;ttt @bot`. Use `;ttt` to play against me.")

    if opponent == ctx.author:
        return await ctx.send("You cannot play against yourself.")

    view = TicTacToeView(ctx.author, opponent, bot_player=False)
    message = await ctx.send(
        embed=build_ttt_embed(
            f"It is now {ctx.author.mention}'s turn (X).",
            ctx.author,
            opponent
        ),
        view=view
    )
    view.message = message

# CONNECT 4 --------------------------------------------------------------------------------------------------------
class Connect4Button(discord.ui.Button):
    def __init__(self, column: int, row: int):
        super().__init__(style=discord.ButtonStyle.secondary, label=str(column + 1), row=row)
        self.column = column

    async def callback(self, interaction: discord.Interaction):
        await self.view.play_turn(interaction, self.column)

class Connect4View(discord.ui.View):
    ROWS = 6
    COLS = 7

    def __init__(self, author: discord.Member, opponent: discord.Member):
        super().__init__(timeout=180)
        self.author = author
        self.opponent = opponent
        self.players = {1: author, 2: opponent}
        self.is_bot_game = opponent.id == bot.user.id
        self.current = 1
        self.board = [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.message = None
        self.lock = asyncio.Lock()
        for col in range(self.COLS):
            button_row = 0 if col < 5 else 1
            self.add_item(Connect4Button(col, button_row))

    def render_board(self):
        pieces = {0: "⚫", 1: "🔴", 2: "🟡"}
        lines = []
        for row in self.board:
            lines.append("".join(pieces[cell] for cell in row))
        lines.append("1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣")
        return "\n".join(lines)

    def get_embed(self, title="Connect 4", description=None):
        embed = discord.Embed(
            title=title,
            description=description if description else self.render_board(),
            colour=discord.Color.red() if self.current == 1 else discord.Color.gold()
        )
        if not description:
            current_player = self.players[self.current]
            piece = "🔴" if self.current == 1 else "🟡"
            embed.add_field(name="Turn", value=f"{current_player.mention} {piece}", inline=False)
            embed.add_field(name="Players", value=f"🔴 {self.author.mention} vs 🟡 {self.opponent.mention}", inline=False)
        return embed

    def available_columns(self):
        return [c for c in range(self.COLS) if self.board[0][c] == 0]

    def drop_piece(self, col, player):
        for row in range(self.ROWS - 1, -1, -1):
            if self.board[row][col] == 0:
                self.board[row][col] = player
                return row
        return None

    def check_winner(self, row, col, player):
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for direction in (1, -1):
                r = row + dr * direction
                c = col + dc * direction
                while 0 <= r < self.ROWS and 0 <= c < self.COLS and self.board[r][c] == player:
                    count += 1
                    r += dr * direction
                    c += dc * direction
            if count >= 4:
                return True
        return False

    def disable_all(self):
        for child in self.children:
            child.disabled = True

    async def finish_game(self, winner=None):
        self.disable_all()
        if winner is None:
            title = "Connect 4 - Draw"
            desc = f"{self.render_board()}\n\nIt's a draw!"
        else:
            title = "Connect 4 - Winner"
            desc = f"{self.render_board()}\n\n{winner.mention} wins!"
        await self.message.edit(embed=self.get_embed(title=title, description=desc), view=self)
        self.stop()

    async def bot_turn(self):
        await asyncio.sleep(1)
        valid = self.available_columns()
        if not valid:
            await self.finish_game()
            return
        col = random.choice(valid)
        row = self.drop_piece(col, 2)
        if self.check_winner(row, col, 2):
            await self.finish_game(winner=self.opponent)
            return
        if not self.available_columns():
            await self.finish_game()
            return
        self.current = 1
        await self.message.edit(embed=self.get_embed(), view=self)

    async def play_turn(self, interaction: discord.Interaction, column: int):
        async with self.lock:
            if interaction.user.id not in (self.author.id, self.opponent.id):
                return await interaction.response.send_message("This game is not yours.", ephemeral=True)

            if interaction.user.id != self.players[self.current].id:
                return await interaction.response.send_message("It's not your turn.", ephemeral=True)

            row = self.drop_piece(column, self.current)
            if row is None:
                return await interaction.response.send_message("That column is full.", ephemeral=True)

            if self.check_winner(row, column, self.current):
                await interaction.response.defer()
                await self.finish_game(winner=self.players[self.current])
                return

            if not self.available_columns():
                await interaction.response.defer()
                await self.finish_game()
                return

            self.current = 2 if self.current == 1 else 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)

            if self.is_bot_game and self.current == 2:
                await self.bot_turn()

    async def on_timeout(self):
        self.disable_all()
        if self.message:
            timeout_embed = self.get_embed(
                title="Connect 4 - Timed Out",
                description=f"{self.render_board()}\n\nGame ended due to inactivity."
            )
            await self.message.edit(embed=timeout_embed, view=self)

@bot.command(aliases=["c4"])
async def connect4(ctx, opponent: discord.User = None):
    if opponent is None:
        opponent = bot.user
    if opponent.bot and opponent != bot.user:
        return await ctx.send("You can only challenge a real user or me.")
    if opponent == ctx.author:
        return await ctx.send("You can't challenge yourself.")

    view = Connect4View(ctx.author, opponent)
    message = await ctx.send(embed=view.get_embed(), view=view)
    view.message = message

    if view.is_bot_game and view.current == 2:
        await view.bot_turn()

# MUSIC -----------------------------------------------------------------------------------------------------------
ytdlp_utils.bug_reports_message = lambda *args, **kwargs: ""

ytdl_format_options: dict[str, Any] = {
    "format": "bestaudio[acodec=opus]/bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
    "js_runtimes": {
        "node": {
            "path": r"C:\Program Files\nodejs\node.exe"
        }
    },
}
ffmpeg_options = {
    "before_options": (
        "-reconnect 1 "
        "-reconnect_streamed 1 "
        "-reconnect_on_network_error 1 "
        "-reconnect_on_http_error 4xx,5xx "
        "-reconnect_delay_max 10"
    ),
    "options": "-vn"
}

ytdl = youtube_dl.YoutubeDL(cast(Any, ytdl_format_options))
song_queue = []
loop_song = False
current_song = None
skip_once = False
now_playing_message = None
now_playing_updater = None
slowed_mode = False
sped_mode = False
bassboost_mode = False
play_started_at = None
paused_at = None
autoplay_mode = False
current_volume = 1.0
paused_total = 0.0

async def get_song_info(query):
    loop = asyncio.get_running_loop()

    info = await loop.run_in_executor(
        None,
        lambda: ytdl.extract_info(query, download=False)
    )
    info = cast(dict[str, Any], info)

    entries = info.get("entries")
    if isinstance(entries, list) and entries:
        first = entries[0]
        if isinstance(first, dict):
            info = cast(dict[str, Any], first)

    webpage_url = info.get("webpage_url") or info.get("original_url") or query

    return {
        "query": query,
        "url": webpage_url,
        "title": info.get("title", "Unknown"),
        "webpage_url": webpage_url,
        "audio_url": info.get("url"),
        "duration": info.get("duration") or 0,
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader") or info.get("channel") or "Unknown",
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
    }

async def get_autoplay_song(seed_song: dict[str, Any], requester=None) -> dict[str, Any] | None:
    title = seed_song.get("title") or ""
    uploader = seed_song.get("uploader") or ""

    search_query = f"{title} {uploader}".strip()
    if not search_query:
        return None

    loop = asyncio.get_running_loop()

    try:
        info = await loop.run_in_executor(
            None,
            lambda: ytdl.extract_info(
                f"ytsearch5:{search_query}",
                download=False
            )
        )
    except Exception:
        return None

    info = cast(dict[str, Any], info)
    entries = info.get("entries")

    if not isinstance(entries, list):
        return None

    current_url = seed_song.get("webpage_url") or seed_song.get("url")
    queued_urls = {song.get("webpage_url") or song.get("url") for song in song_queue}

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        webpage_url = entry.get("webpage_url") or entry.get("original_url")
        if not webpage_url:
            continue

        if current_url and webpage_url == current_url:
            continue

        if webpage_url in queued_urls:
            continue

        return {
        "url": webpage_url,
        "title": entry.get("title", "Unknown"),
        "webpage_url": webpage_url,
        "thumbnail": entry.get("thumbnail"),
        "duration": entry.get("duration") or 0,
        "uploader": entry.get("uploader") or entry.get("channel") or "Unknown",
        "views": entry.get("view_count"),
        "likes": entry.get("like_count"),
        "requester": requester
        }
    return None


def build_now_playing_embed(song):
    global autoplay_mode
    title = song.get("title", "Unknown")
    webpage_url = song.get("webpage_url", "")
    duration = song.get("duration") or 0
    thumbnail = song.get("thumbnail")
    uploader = song.get("uploader") or "Unknown"
    views = song.get("views")
    likes = song.get("likes")
    requester = song.get("requester")

    position = get_current_playback_position()
    progress_bar = build_progress_bar(position, duration)
    duration_text = format_time(duration) if duration > 0 else "LIVE"
    elapsed_text = format_time(position)

    if paused_at is None:
        status_text = "Playing"
    else:
        status_text = "Paused"

    mode_text = get_mode_text()

    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"**[{title}]({webpage_url})**" if webpage_url else f"**{title}**",
        colour=discord.Colour.red(),
        url=webpage_url if webpage_url else None
    )

    embed.add_field(name="⏱️ Duration", value=duration_text, inline=True)
    embed.add_field(name="📺 Uploader", value=uploader, inline=True)
    embed.add_field(name="▶️ Status", value=status_text, inline=True)

    embed.add_field(name="🔁 Loop", value="ON" if loop_song else "OFF", inline=True)
    embed.add_field(name="⚙️ Mode", value=mode_text, inline=True)
    embed.add_field(name="📂 Queue", value=str(len(song_queue)), inline=True)

    if views is not None:
        embed.add_field(name="👀 Views", value=f"{views:,}", inline=True)

    if likes is not None:
        embed.add_field(name="👍 Likes", value=f"{likes:,}", inline=True)

    if requester is not None:
        embed.add_field(name="🙋 Requester", value=requester.mention, inline=True)

    embed.add_field(
        name="📍 Progress",
        value=f"`{elapsed_text} / {duration_text}`\n`{progress_bar}`",
        inline=True
    )

    embed.add_field(name="♾️ Autoplay", value="ON" if autoplay_mode else "OFF", inline=True)

    if thumbnail:
        embed.set_image(url=thumbnail)

    embed.set_footer(text="Use ;queue to view upcoming songs.")
    return embed


async def update_now_playing_embed():
    message = now_playing_message
    song = current_song

    if message is None or song is None:
        return

    try:
        embed = build_now_playing_embed(song)
        await message.edit(embed=embed)
    except Exception as e:
        print(f"Failed to update now playing embed: {e}")

async def now_playing_progress_loop(song_url: str):
    while True:
        await asyncio.sleep(5)

        if now_playing_message is None or current_song is None:
            break
        if current_song.get("url") != song_url:
            break

        vc = None
        if now_playing_message.guild:
            vc = now_playing_message.guild.voice_client

        if vc is None or not vc.is_connected():
            break

        if not (vc.is_playing() or vc.is_paused()):
            break

        try:
            await update_now_playing_embed()
        except Exception:
            break

class MusicControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.message = None

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if str(item.emoji) == "🔁":
                    item.label = f"Loop: {'On' if loop_song else 'Off'}"
                elif str(item.emoji) == "⚙️":
                    item.label = f"Mode: {get_mode_text()}"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        vc = interaction.guild.voice_client if interaction.guild else None

        if not vc or not vc.channel:
            await interaction.response.send_message(
                embed=warning_embed("I'm not in a voice channel.", title="Not Connected"),
                ephemeral=True
            )
            return False

        if not interaction.user.voice or interaction.user.voice.channel != vc.channel:
            await interaction.response.send_message(
                embed=warning_embed(
                    "You must be in my voice channel to use these controls.",
                    title="Access Denied"
                ),
                ephemeral=True
            )
            return False

        return True

    async def on_timeout(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if str(item.emoji) == "🔁":
                    item.label = f"Loop: {'On' if loop_song else 'Off'}"
                elif str(item.emoji) == "⚙️":
                    item.label = f"Mode: {get_mode_text()}"
                item.disabled = True

        if self.message:
            try:
                await self.message.edit(view=self)
            except Exception:
                pass

    @discord.ui.button(label="Pause/Resume", emoji="▶️", style=discord.ButtonStyle.primary)
    async def pause_resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global paused_at, paused_total

        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message(
                embed=warning_embed("Nothing is playing.", title="Nothing Playing"),
                ephemeral=True
            )
            return

        if vc.is_paused():
            vc.resume()
            if paused_at is not None:
                paused_total += time.monotonic() - paused_at
                paused_at = None

        elif vc.is_playing():
            vc.pause()
            paused_at = time.monotonic()

        else:
            await interaction.response.send_message(
                embed=warning_embed("Nothing is playing.", title="Nothing Playing"),
                ephemeral=True
            )
            return

        await interaction.response.edit_message(
            embed=build_now_playing_embed(current_song),
            view=self
        )

    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global skip_once

        vc = interaction.guild.voice_client
        if not vc or not (vc.is_playing() or vc.is_paused()):
            await interaction.response.send_message(
                embed=warning_embed("Nothing is playing.", title="Nothing Playing"),
                ephemeral=True
            )
            return

        skip_once = True
        await interaction.response.defer()
        vc.stop()

    @discord.ui.button(label="Mode", emoji="⚙️", style=discord.ButtonStyle.primary)
    async def mode_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global slowed_mode, sped_mode, bassboost_mode
        vc = interaction.guild.voice_client if interaction.guild else None
        if vc is None or current_song is None:
            return await interaction.response.send_message(
                embed=warning_embed("Nothing is playing.", title="Nothing Playing"),
                ephemeral=True
            )

        if not slowed_mode and not sped_mode:
            slowed_mode = True
            sped_mode = False
        elif slowed_mode:
            slowed_mode = False
            sped_mode = True
        else:
            slowed_mode = False
            sped_mode = False

        ok, error_message = await apply_current_mode(vc)
        if not ok:
            return await interaction.response.send_message(
                embed=error_embed(
                    error_message or "Couldn't change mode.",
                    title="Mode Change Failed"
                ),
                ephemeral=True
            )

        button.label = f"Mode: {get_mode_text()}"

        await interaction.response.edit_message(
            embed=build_now_playing_embed(current_song),
            view=self
        )

    @discord.ui.button(label="Loop", emoji="🔁", style=discord.ButtonStyle.success)
    async def loop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global loop_song
        loop_song = not loop_song

        button.label = f"Loop: {'On' if loop_song else 'Off'}"

        await interaction.response.edit_message(
            embed=build_now_playing_embed(current_song),
            view=self
        )

    @discord.ui.button(label="Stop", emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global song_queue, current_song, now_playing_message, now_playing_updater
        global loop_song, autoplay_mode, play_started_at, paused_at, paused_total, skip_once

        vc = interaction.guild.voice_client
        if not vc:
            await interaction.response.send_message(
                embed=warning_embed("Nothing is playing.", title="Nothing Playing"),
                ephemeral=True
            )
            return

        song_queue.clear()
        current_song = None
        loop_song = False
        autoplay_mode = False
        skip_once = False
        play_started_at = None
        paused_at = None
        paused_total = 0.0

        if now_playing_updater:
            now_playing_updater.cancel()
            now_playing_updater = None

        for item in self.children:
            item.disabled = True

        await interaction.response.edit_message(
            content=None,
            embed=info_embed("Playback stopped.", title="Stopped"),
            view=self
        )

        now_playing_message = None
        vc.stop()

        try:
            await vc.disconnect()
        except  Exception:
            pass

        self.stop()

def make_audio_source(audio_url, start_at=0.0, slowed=False, sped=False, bassboost=False):
    before = ffmpeg_options["before_options"]
    if start_at and start_at > 0:
        before = f"{before} -ss {start_at:.2f}"

    filters = []

    base_resample = "aresample=48000"

    if slowed:
        filters.extend([
            "atempo=0.92",
            "asetrate=48000*0.92",
            "aresample=48000",
            "aecho=0.7:0.75:30:0.05",
        ])
    elif sped:
        filters.extend([
            "atempo=1.08",
            "asetrate=48000*1.08",
            "aresample=48000",
            "treble=g=1.2:f=4500:width_type=o:width=1.0:m=0.35",
        ])
    else:
        filters.append("aresample=48000")

    if bassboost:
        filters.extend([
            "bass=g=2.5:f=90:width_type=o:width=1.2:m=0.35",
            "volume=0.90"
        ])

    if filters:
        options = f'-vn -filter:a "{",".join(filters)}"'
    else:
        options = "-vn"

    source = discord.FFmpegPCMAudio(
        audio_url,
        before_options=before,
        options=options
    )
    return discord.PCMVolumeTransformer(source, volume=current_volume)

def get_current_playback_position():
    global play_started_at, paused_at, paused_total

    if play_started_at is None:
        return 0.0

    if paused_at is not None:
        elapsed = paused_at - play_started_at - paused_total
    else:
        elapsed = time.monotonic() - play_started_at - paused_total

    return max(0.0, elapsed)

def format_time(seconds: float | int) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return (f"{minutes}:{secs:02d}")

def build_progress_bar(position: float, duration: int, length: int = 16) -> str:
    if duration <= 0:
        return "🔴 LIVE"

    position = max(0.0, min(position, float(duration)))
    ratio = position / duration if duration else 0.0
    filled = int(ratio * length)

    if filled >= length:
        filled = length - 1

    bar = "█" * filled + "🔘" + "─" * (length - filled - 1)
    return bar

def get_mode_text() -> str:
    parts = []

    if slowed_mode:
        parts.append("Slowed")
    elif sped_mode:
        parts.append("Sped")

    if bassboost_mode:
        parts.append("BassBoost")

    return " + ".join(parts) if parts else "Normal"

async def apply_current_mode(vc: discord.VoiceClient) -> tuple[bool, str | None]:
    global play_started_at, paused_at, paused_total, current_song

    if current_song is None:
        return False, "Nothing is loaded."

    if not (vc.is_playing() or vc.is_paused()):
        return False, "Nothing is playing."

    try:
        fresh_song = await get_song_info(current_song["url"])
    except Exception as e:
        return False, f"Couldn't reload the current track: {e}"

    audio_url = fresh_song.get("audio_url")
    if not audio_url:
        return False, "Couldn't rebuild the current stream."

    position = get_current_playback_position()
    was_paused = vc.is_paused()

    if was_paused:
        vc.resume()
        if paused_at is not None:
            paused_total += time.monotonic() - paused_at
            paused_at = None

    new_source = make_audio_source(
        audio_url,
        start_at=position,
        slowed=slowed_mode,
        sped=sped_mode,
        bassboost=bassboost_mode
    )

    vc.source = new_source

    play_started_at = time.monotonic() - position
    paused_at = None

    if was_paused:
        vc.pause()
        paused_at = time.monotonic()
    return True, None

def make_embed(
        description: str,
        colour: discord.Color,
        *,
        title: str| None = None
) -> discord.Embed:
    embed = discord.Embed(
        title=title,
        description=description,
        colour=colour
    )
    embed.timestamp = discord.utils.utcnow()
    return embed

def success_embed(description: str, *, title: str = "Success") -> discord.Embed:
    return make_embed(f"✅ {description}", discord.Color.green(), title=title)

def error_embed(description: str, *, title: str = "Error") -> discord.Embed:
    return make_embed(f"❌ {description}", discord.Color.red(), title=title)

def warning_embed(description: str, *, title: str = "Warning") -> discord.Embed:
    return make_embed(f"⚠️ {description}", discord.Color.orange(), title=title)

def info_embed(description: str, *, title: str = "Info") -> discord.Embed:
    return make_embed(f"ℹ️ {description}", discord.Color.blurple(), title=title)


def clean_lyrics_title(title: str) -> str:
    title = re.sub(
        r"\s*[\[(](?:official|lyrics?|lyric video|audio|video|visualizer|sped up|slowed|reverb|nightcore).*?[\])]",
        "",
        title,
        flags=re.IGNORECASE,
    )
    title = title.replace("|", "-")
    return " ".join(title.split()).strip(" -")

def guess_artist_and_track(song: dict[str, Any]) -> tuple[str, str]:
    raw_title = clean_lyrics_title(song.get("title") or "")
    uploader = (song.get("uploader") or "").replace(" - Topic", "").replace("VEVO", "").strip()

    if " - " in raw_title:
        artist, track = raw_title.split(" - ", 1)
        artist = artist.strip()
        track = track.strip()
        if artist and track:
            return artist, track
    return uploader, raw_title

async def fetch_lyrics_data(song: dict[str, Any]) -> dict[str, str] | None:
    artist, track = guess_artist_and_track(song)
    duration = int(song.get("duration") or 0)

    headers = {"User-Agent": "DiscordMusicBot/1.0"}

    async with aiohttp.ClientSession(headers=headers) as session:
        params = {"track_name": track}
        if artist:
            params["artist_name"] = artist
        if duration > 0:
            params["duration"] = duration

        async with session.get("https://lrclib.net/api/get", params=params) as resp:
            if resp.status == 200:
                data = await resp.json()
                lyrics = data.get("plainLyrics") or data.get("syncedLyrics")
                if lyrics:
                    return {
                        "artist": data.get("artistName") or artist or "Unknown",
                        "track": data.get("trackName") or track or song.get("title", "Unknown"),
                        "lyrics": lyrics.strip(),
                    }

        search_params = {"track_name": track}
        if artist:
            search_params["artist_name"] = artist

        async with session.get("https://lrclib.net/api/search", params=search_params) as resp:
            if resp.status == 200:
                results = await resp.json()
                if isinstance(results, list):
                    for item in results:
                        lyrics = item.get("plainLyrics") or item.get("syncedLyrics")
                        if lyrics:
                            return {
                                "artist": item.get("artistName") or artist or "Unknown",
                                "track": item.get("trackName") or track or song.get("title", "Unknown"),
                                "lyrics": lyrics.strip(),
                            }
    return None

def trim_lyrics(text: str, limit: int = 3500) -> tuple[str, bool]:
    text = text.strip()
    if len(text) <= limit:
        return text, False
    return text[: limit - 3].rstrip() + "...", True


def build_lyrics_embed(data: dict[str, str], *, truncated: bool = False) -> discord.Embed:
    lyrics_text, was_trimmed = trim_lyrics(data["lyrics"])

    embed = discord.Embed(
        title=f"🎤 Lyrics — {data['track']}",
        description=lyrics_text,
        colour=discord.Color.purple(),
    )
    embed.add_field(name="Artist", value=data["artist"], inline=True)

    if truncated or was_trimmed:
        embed.set_footer(text="Lyrics were truncated to fit in one message.")

    return embed


async def play_next(ctx):
    global loop_song, current_song, now_playing_message, now_playing_updater
    global play_started_at, paused_at, paused_total, skip_once

    if not ctx.voice_client or not ctx.voice_client.is_connected():
        return

    if loop_song and current_song and not skip_once:
        queued_song = current_song
    else:
        skip_once = False

        if not song_queue:
            if autoplay_mode and current_song is not None:
                auto_song = await get_autoplay_song(current_song, requester=ctx.guild.me if ctx.guild else None)
                if auto_song is not None:
                    song_queue.append(auto_song)

            if not song_queue:
                current_song = None
                now_playing_message = None
                await safe_disconnect(ctx)
                return

        queued_song = song_queue.pop(0)

    try:
        fresh_song = await get_song_info(queued_song["url"])
    except Exception as e:
        await ctx.send(embed=error_embed(f"Couldn't load this track:\n```py\n{e}\n```"))

        if autoplay_mode and current_song is not None and not song_queue:
            auto_song = await get_autoplay_song(current_song, requester=ctx.guild.me if ctx.guild else None)
            if auto_song is not None:
                song_queue.append(auto_song)

        if song_queue:
            await play_next(ctx)
        else:
            current_song = None
            now_playing_message = None
            await safe_disconnect(ctx)
        return

    audio_url = fresh_song.get("audio_url")
    if not audio_url:
        await ctx.send(
            embed=error_embed(
                "Couldn't get a playable stream for this track.",
                title="Playback Source Failed"
            )
        )
        if song_queue:
            await play_next(ctx)
        return

    current_song = {
        "url": fresh_song.get("url", queued_song.get("url")),
        "title": fresh_song.get("title", queued_song.get("title", "Unknown")),
        "webpage_url": fresh_song.get("webpage_url", queued_song.get("webpage_url", "")),
        "thumbnail": fresh_song.get("thumbnail", queued_song.get("thumbnail")),
        "duration": fresh_song.get("duration", queued_song.get("duration", 0)),
        "uploader": fresh_song.get("uploader", queued_song.get("uploader", "Unknown")),
        "views": fresh_song.get("views", queued_song.get("views")),
        "likes": fresh_song.get("likes", queued_song.get("likes")),
        "requester": queued_song.get("requester"),
    }

    try:
        source = make_audio_source(
            audio_url,
            start_at=0.0,
            slowed=slowed_mode,
            sped=sped_mode,
            bassboost=bassboost_mode
        )
    except Exception as e:
        await ctx.send(
            embed=error_embed(
                f"Couldn't create the audio source:\n```py\n{e}\n```",
                title="Audio Source Failed"
            )
        )
        return

    def after_playback(error):
        if error:
            print(f"Playback error: {error}")

        if ctx.voice_client and ctx.voice_client.is_connected():
            future = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
            try:
                future.result()
            except Exception as e:
                print(f"Error in play_next: {e}")

    try:
        ctx.voice_client.play(source, after=after_playback)
    except Exception as e:
        await ctx.send(
            embed=error_embed(
                f"Playback failed:\n```py\n{e}\n```",
                title="Playback Failed"
            )
        )
        return

    play_started_at = time.monotonic()
    paused_at = None
    paused_total = 0.0

    embed = build_now_playing_embed(current_song)

    if now_playing_message:
        try:
            await now_playing_message.delete()
        except Exception:
            pass

    if now_playing_updater:
        now_playing_updater.cancel()
        now_playing_updater = None

    view = MusicControls()
    now_playing_message = await ctx.send(embed=embed, view=view)
    view.message = now_playing_message

    now_playing_updater = asyncio.create_task(
        now_playing_progress_loop(current_song["url"])
    )

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send(
            embed=warning_embed("You must be in a voice channel!", title="Voice Required")
        )

    if ctx.voice_client and ctx.voice_client.channel != ctx.author.voice.channel:
        return await ctx.send(
            embed=warning_embed(
                f"I'm already being used in **{ctx.voice_client.channel}**.",
                title="Bot Is Busy"
            )
        )

    if ctx.voice_client and ctx.voice_client.channel == ctx.author.voice.channel:
        return await ctx.send(
            embed=info_embed("I'm already in your voice channel.", title="Already Connected")
        )

    if not getattr(discord.voice_client, "has_nacl", False):
        return await ctx.send(
            embed=error_embed(
                f"Voice support is missing. Install `PyNaCl` and `davey`, then restart the bot.\n{voice_runtime_info()}",
                title="Voice Support Missing"
            )
        )

    try:
        await ctx.author.voice.channel.connect()
        await ctx.send(
            embed=success_embed("Connected to your voice channel!", title="Voice Connected")
        )
    except RuntimeError as e:
        return await ctx.send(
            embed=error_embed(
                f"Voice connect failed:\n```py\n{e}\n```\n{voice_runtime_info()}",
                title="Connection Failed"
            )
        )

@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send(embed=warning_embed("You must be in a voice channel!", title="Voice Required"))

    if ctx.voice_client and ctx.voice_client.channel != ctx.author.voice.channel:
        return await ctx.send(
            embed=warning_embed(
                f"I'm already being used in **{ctx.voice_client.channel}**.",
                title="Bot Is Busy"
            )
        )

    if not ctx.voice_client:
        await join(ctx)
    if not ctx.voice_client:
        return

    try:
        song = await get_song_info(query)
    except Exception as e:
        return await ctx.send(
            embed=error_embed(f"Couldn't load this track:\n```py\n{e}\n```", title="Track Load Failed")
        )

    if not song.get("webpage_url"):
        return await ctx.send(embed=warning_embed("Couldn't resolve that track.", title="Track Not Found"))

    queue_song = {
        "url": song["webpage_url"],
        "title": song.get("title", "Unknown"),
        "webpage_url": song.get("webpage_url"),
        "thumbnail": song.get("thumbnail"),
        "duration": song.get("duration", 0),
        "uploader": song.get("uploader", "Unknown"),
        "views": song.get("views"),
        "likes": song.get("likes"),
        "requester": ctx.author,
    }

    song_queue.append(queue_song)

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        if song.get("webpage_url"):
            await ctx.send(
                embed=success_embed(
                    f"Added to queue: **[{song['title']}]({song['webpage_url']})**",
                    title="Queued"
                )
            )
        else:
            await ctx.send(
                embed=success_embed(
                    f"Added to queue: **{song['title']}**",
                    title="Queued"
                )
            )
    else:
        await play_next(ctx)
    return None

@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(
            embed=warning_embed(
                "Use `;play <song name or url>`",
                title="Missing Argument"
            )
        )

    raise error

@bot.command()
async def pause(ctx):
    global paused_at

    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        paused_at = time.monotonic()
        await ctx.send(embed=info_embed("Playback has been paused.", title="Paused"))
        await update_now_playing_embed()
    else:
        await ctx.send(embed=warning_embed("No song is playing!", title="Nothing Playing"))

@bot.command()
async def resume(ctx):
    global paused_at, paused_total
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        if paused_at is not None:
            paused_total += time.monotonic() - paused_at
            paused_at = None
        await ctx.send(embed=success_embed("Playback has been resumed.", title="Resumed"))
        await update_now_playing_embed()
    else:
        await ctx.send(embed=warning_embed("No song is paused!", title="Nothing Paused"))

@bot.command()
async def skip(ctx):
    global skip_once

    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        skip_once = True
        ctx.voice_client.stop()
        await ctx.send(embed=info_embed("Skipped the song.", title="Skipped"))
    else:
        await ctx.send(embed=warning_embed("Nothing is playing!", title="Nothing Playing"))

@bot.command()
async def queue(ctx):
    global current_song

    def trim(text, limit=60):
        return text if len(text) <= limit else text[:limit - 3] + "..."

    if not current_song and not song_queue:
        return await ctx.send(embed=warning_embed("Queue is empty!", title="Empty Queue"))

    lines = []

    if current_song:
        lines.append(f"**Now Playing:**\n🎶 **[{trim(current_song['title'])}]({current_song['webpage_url']})**")

    if song_queue:
        queue_text = "\n".join(
            f"`{i:>2}.` **[{trim(song['title'])}]({song['webpage_url']})**"
            for i, song in enumerate(song_queue, start=1)
        )
        lines.append(f"**Up Next:**\n{queue_text}")
    else:
        lines.append("**Up Next:**\nNo songs queued.")

    embed = discord.Embed(
        title="🎼 Music Queue",
        description="\n\n".join(lines),
        colour=discord.Color.blurple()
    )

    embed.set_footer(text=f"Total queued: {len(song_queue)} | Loop: {'On' if loop_song else 'Off'}")

    await ctx.send(embed=embed)

@bot.command()
async def lyrics(ctx):
    if current_song is None:
        return await ctx.send(embed=warning_embed("Nothing is playing!", title="Lyrics Unavailable"))

    data = await fetch_lyrics_data(current_song)
    if data is None:
        return await ctx.send(embed=warning_embed("Couldn't find lyrics for the current track.", title="Lyrics Not Found"))

    embed = build_lyrics_embed(data, truncated=True)
    await ctx.send(embed=embed)

@bot.command()
async def leave(ctx):
    global current_song, now_playing_message, now_playing_updater
    global play_started_at, paused_at, paused_total, skip_once, autoplay_mode

    if now_playing_updater:
        now_playing_updater.cancel()
        now_playing_updater = None

    song_queue.clear()
    current_song = None
    now_playing_message = None
    skip_once = False
    autoplay_mode = False
    play_started_at = None
    paused_at = None
    paused_total = 0.0

    await safe_disconnect(ctx)

@bot.command()
async def loop(ctx, mode: str = None):
    global loop_song
    if mode is None:
        loop_song = not loop_song
    else:
        mode = mode.lower().strip()
        if mode in ("on", "true", "yes", "1"):
            loop_song = True
        elif mode in ("off", "false", "no", "0"):
            loop_song = False
        else:
            return await ctx.send(
                embed=warning_embed(
                    "Use `;loop`, `;loop on`, or `;loop off`.",
                    title="Invalid Usage"
                )
            )

    await ctx.send(
        embed=info_embed(
            f"Loop is now **{'ON' if loop_song else 'OFF'}**.",
            title="Loop Updated"
        )
    )
    await update_now_playing_embed()

@bot.command()
async def shuffle(ctx):
    if not song_queue:
        return await ctx.send(
            embed=warning_embed("Queue is empty!", title="Empty Queue")
        )

    random.shuffle(song_queue)
    await ctx.send(embed=info_embed("Queue shuffled.", title="Shuffled"))
    await update_now_playing_embed()

@bot.command()
async def remove(ctx, position: int):
    if not song_queue:
        return await ctx.send(
            embed=warning_embed("Queue is empty!", title="Empty Queue")
        )

    if position < 1 or position > len(song_queue):
        return await ctx.send(
            embed=warning_embed(
                f"Choose a number between `1` and `{len(song_queue)}`.",
                title="Invalid Queue Position"
            )
        )

    removed_song = song_queue.pop(position - 1)

    title = removed_song.get("title", "Unknown")
    url = removed_song.get("webpage_url")

    if url:
        description = f"Removed **[{title}]({url})** from the queue."
    else:
        description = f"Removed **{title}** from the queue."

    await ctx.send(embed=info_embed(description, title="Removed"))
    await update_now_playing_embed()

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(
            embed=warning_embed(
                "Use `;remove <queue number>`",
                title="Missing Argument"
            )
        )

    if isinstance(error, commands.BadArgument):
        return await ctx.send(
            embed=warning_embed(
                "Queue position must be a number. Example: `;remove 2`",
                title="Invalid Argument"
            )
        )

    raise error

@bot.command()
async def clear(ctx):
    if not song_queue:
        return await ctx.send(
            embed=warning_embed("Queue is already empty!", title="Empty Queue")
        )

    cleared = len(song_queue)
    song_queue.clear()

    await ctx.send(
        embed=info_embed(
            f"Cleared **{cleared}** song(s) from the queue.",
            title="Queue Cleared"
        )
    )
    await update_now_playing_embed()

@bot.command()
async def autoplay(ctx, mode: str | None = None):
    global autoplay_mode

    if mode is None:
        autoplay_mode = not autoplay_mode
    else:
        mode = mode.lower().strip()
        if mode in ("on", "true", "yes", "1"):
            autoplay_mode = True
        elif mode in ("off", "false", "no", "0"):
            autoplay_mode = False
        else:
            return await ctx.send(
                embed=warning_embed(
                    "Use `;autoplay`, `;autoplay on`, or `;autoplay off`.",
                    title="Invalid Usage"
                )
            )

    await ctx.send(
        embed=info_embed(
            f"Autoplay is now **{'ON' if autoplay_mode else 'OFF'}**.",
            title="Autoplay Updated"
        )
    )

    await update_now_playing_embed()

@bot.command()
async def volume(ctx, volume: int):
    global current_volume

    if volume < 0 or volume > 200:
        return await ctx.send(
            embed=warning_embed("Volume must be between `0` and `200`.", title="Invalid Volume")
        )

    if ctx.voice_client and ctx.voice_client.source:
        current_volume = volume / 100

        if isinstance(ctx.voice_client.source, discord.PCMVolumeTransformer):
            ctx.voice_client.source.volume = current_volume
        else:
            ctx.voice_client.source = discord.PCMVolumeTransformer(
                ctx.voice_client.source,
                volume=current_volume
            )

        await ctx.send(embed=success_embed(f"Volume set to {volume}%.", title="Volume Updated"))
    else:
        await ctx.send(embed=warning_embed("No song is playing!", title="Nothing Playing"))

@bot.command()
async def slowed(ctx, mode: str | None = None):
    global slowed_mode, sped_mode, bassboost_mode
    global play_started_at, paused_at, paused_total, current_song

    if mode is None:
        slowed_mode = not slowed_mode
    else:
        mode = mode.lower()
        if mode in ("on", "true", "yes", "1"):
            slowed_mode = True
        elif mode in ("off", "false", "no", "0"):
            slowed_mode = False
        else:
            return await ctx.send(
                embed=warning_embed(
                    "Use `;slowed`, `;slowed on`, or `;slowed off`.",
                    title="Invalid Usage"
                )
            )

    if slowed_mode:
        sped_mode = False

    await ctx.send(
        embed=info_embed(
            f"Slowed mode is now **{'ON' if slowed_mode else 'OFF'}**.",
            title="Mode Updated"
        )
    )

    vc = cast(discord.VoiceClient | None, ctx.voice_client)
    if vc is None or current_song is None:
        return

    if not (vc.is_playing() or vc.is_paused()):
        return

    ok, error_message = await apply_current_mode(vc)
    if not ok:
        return await ctx.send(
            embed=error_embed(
                error_message or "Couldn't apply slowed mode.",
                title="Mode Change Failed"
            )
        )

    await update_now_playing_embed()
    return None

@bot.command()
async def sped(ctx, mode: str = None):
    global sped_mode, slowed_mode, bassboost_mode
    global play_started_at, paused_at, paused_total, current_song

    if mode is None:
        sped_mode = not sped_mode
    else:
        mode = mode.lower().strip()
        if mode in ("on", "true", "yes", "1"):
            sped_mode = True
        elif mode in ("off", "false", "no", "0"):
            sped_mode = False
        else:
            return await ctx.send(
                embed=warning_embed(
                    "Use `;sped`, `;sped on`, or `;sped off`.",
                    title="Invalid Usage"
                )
            )

    if sped_mode:
        slowed_mode = False

    await ctx.send(
        embed=info_embed(
            f"Sped mode is now **{'ON' if sped_mode else 'OFF'}**.",
            title="Mode Updated"
        )
    )

    vc = cast(discord.VoiceClient | None, ctx.voice_client)
    if vc is None or current_song is None:
        return

    if not (vc.is_playing() or vc.is_paused()):
        return

    ok, error_message = await apply_current_mode(vc)
    if not ok:
        return await ctx.send(
            embed=error_embed(
                error_message or "Couldn't apply sped mode.",
                title="Mode Change Failed"
            )
        )

    await update_now_playing_embed()
    return None

@bot.command()
async def bassboost(ctx, mode: str | None = None):
    global bassboost_mode, slowed_mode, sped_mode
    global play_started_at, paused_at, paused_total, current_song

    if mode is None:
        bassboost_mode = not bassboost_mode
    else:
        mode = mode.lower().strip()
        if mode in ("on", "true", "yes", "1"):
            bassboost_mode = True
        elif mode in ("off", "false", "no", "0"):
            bassboost_mode = False
        else:
            return await ctx.send(
                embed=warning_embed(
                    "Use `;bassboost`, `;bassboost on`, or `;bassboost off`.",
                    title="Invalid Usage"
                )
            )

    await ctx.send(
        embed=info_embed(
            f"BassBoost mode is now **{'ON' if bassboost_mode else 'OFF'}**.",
            title="Mode Updated"
        )
    )

    vc = cast(discord.VoiceClient | None, ctx.voice_client)
    if vc is None or current_song is None:
        return

    if not (vc.is_playing() or vc.is_paused()):
        return

    ok, error_message = await apply_current_mode(vc)
    if not ok:
        return await ctx.send(
            embed=error_embed(
                error_message or "Couldn't apply bassboost mode.",
                title="Mode Change Failed"
            )
        )

    await update_now_playing_embed()
    return None

async def safe_disconnect(ctx):
    global now_playing_message, now_playing_updater

    if now_playing_updater:
        now_playing_updater.cancel()
        now_playing_updater = None

    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
        now_playing_message = None
        await ctx.send(embed=info_embed("Disconnected from the voice channel", title="Disconnected"))

@bot.event
async def on_command_error(ctx, error):
    if ctx.command and ctx.command.has_error_handler():
        return

    if isinstance(error, commands.CommandNotFound):
        return await ctx.send(
            embed=warning_embed(
                "That command does not exist. Use `;help` to see available commands.",
                title="Invalid Command"
            )
        )

    if isinstance(error, commands.MissingRequiredArgument):
        if ctx.command and ctx.command.qualified_name == "play":
            return await ctx.send(
                embed=warning_embed(
                    "Use `;play <song name or url>`",
                    title="Missing Argument"
                )
            )
        return await ctx.send(
            embed=warning_embed(
                f"Missing required argument: `{error.param.name}`.",
                title="Missing Argument"
            )
        )

    if isinstance(error, commands.BadArgument):
        return await ctx.send(
            embed=warning_embed(
                "One of the arguments is invalid. Check ;help [command] and try again.",
                title="Invalid Argument"
            )
        )
    raise error

bot.run(token, log_handler=handler, log_level=logging.DEBUG)