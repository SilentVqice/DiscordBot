import discord
import logging
import os
import json
import asyncio
import aiohttp
import random
import html
from discord.ext.commands import Bot
from dotenv import load_dotenv
from discord import AllowedMentions
from discord.ext import commands

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.presences = True

bot = Bot(command_prefix=';', intents=intents)

# BOT START ---------------------------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}! :3")

############################################ R.I.C.H  P.R.E.S.E.N.C.E. ############################################

##################################################### H.E.L.P #####################################################
@bot.command()
async def helpcommands(ctx):
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all the commands you can use:",
        color=discord.Color.blue()
    )

    commands_by_category = {
        "Moderation": {
            ";ban": "Bans a member from the server. - ;ban [@user] [time] [reason]",
            ";unban": "Unbans a member by their Discord user ID. - ;unban [user_id] [reason]",
            ";kick": "Kicks a member from the server. - ;kick [@user] [reason]",
            ";mute": "Mutes a member, optionally for a set time. - ;mute [@user] [time] [reason]",
            ";unmute": "Unmutes a member by removing the Muted role. - ;unmute [@user] [reason]",
        },
        "Utility": {
            ";purge": "Deletes a number of messages from the channel. - ;purge [amount]",
            ";info": "Shows info about a user or yourself. - ;info [@user]"
        },
        "Fun": {
            ";kitty": "Sends a random cat image. - ;kitty",
            ";trivia": "Starts a trivia question. - ;trivia",
            ";flag": "Starts a country flag trivia question. - ;flag"
        }
    }

    # Add each category and its commands to the embed
    for category, commands_dict in commands_by_category.items():
        value = "\n".join(f"`{name}` - {desc}" for name, desc in commands_dict.items())
        embed.add_field(name=category, value=value, inline=False)

    embed.set_footer(text="Type ;help command for more info on a command")
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
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)

    if member.bot:
        return
    emoji_to_role = {
        "<:bed:1483254053227200584>": 1483256278565523608
    }
    if str(payload.emoji) in emoji_to_role:
        role = guild.get_role(emoji_to_role[str(payload.emoji)])
        if role:
            await member.add_roles(role)
            print(f"Added {role.name} to {member.name}")

# REACTION ROLES REMOVE ---------------------------------------------------------------------------------------------
@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    if member.bot:
        return
    emoji_to_role = {
        "<:bed:1483254053227200584>": 1483256278565523608
    }
    if str(payload.emoji) in emoji_to_role:
        role = guild.get_role(emoji_to_role[str(payload.emoji)])
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
async def on_member_join(member):
    await update_member_count(member.guild)

@bot.event
async def on_member_remove(member):
    await update_member_count(member.guild)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")
    for guild in bot.guilds:
        await update_member_count(guild)

# USER MENTION FUN X3 ----------------------------------------------------------------------------------------------
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    special_user_responses = {
        979934316429738035: "Mwah",
        812269541731074078: "#sniped by snow (Farzo is your nightmare)"
    }
    for user in message.mentions:
        if user.id in special_user_responses:
            await message.channel.send(f"{special_user_responses[user.id]}")
    await bot.process_commands(message)

# WELCOME MESSAGE --------------------------------------------------------------------------------------------------
@bot.event
async def on_member_join(member):
    welcome_channel_id = 1483276233818112202
    channel = member.guild.get_channel(welcome_channel_id)

    if channel:
        embed = discord.Embed(
            title=f"Welcome to the server, {member.display_name}!",
            description="We're very happy to have you buh buh buh",
            colour=discord.Color.green()
         )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text="Enjoy your stay!")

        await channel.send(content=f"Welcome {member.mention}!", embed=embed)

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

    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    roles_display = ", ".join(roles) if roles else "No roles."
    roles_count = len(roles)

    created = member.created_at.strftime("%d %b %Y %H:%M:%S")
    joined = member.joined_at.strftime("%d %b %Y %H:%M:%S")

    allowed = AllowedMentions(users=True)
    embed = discord.Embed(
        title=f"Info on {member.display_name}",
        colour=member.color
    )

    embed.set_author(name=str(member),icon_url=member.avatar.url if member.avatar else None)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="Username", value=str(member), inline=True)
    embed.add_field(name="User ID", value=member.id, inline=True)
    embed.add_field(name="Account Created", value=created, inline=False)
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
    except discord.Forbidden:
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
intents = discord.Intents.default()
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
        hint_sent = False

        async def scheduled_hint():
            nonlocal hint_sent
            await asyncio.sleep(10)
            if not hint_sent:
                await ctx.send(f"💡 Hint: Starts with **{correct[0]}**")
                hint_sent = True

        asyncio.create_task(scheduled_hint())

        start_time = asyncio.get_event_loop().time()

        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining = total_time - elapsed
            if remaining <= 0:
                return await ctx.send(f"⏰ Time's up! The answer was **{correct}**.")

            try:
                msg = await bot.wait_for("message", timeout=remaining, check=check)
            except asyncio.TimeoutError:
                return await ctx.send(f"⏰ Time's up! The answer was **{correct}**.")

            if correct.lower() in msg.content.lower():
                return await ctx.send("✅ Correct!")

            await ctx.send(f"❌ Wrong! Try again...")

            if not hint_sent:
                await ctx.send(f"💡 Hint: Starts with **{correct[0]}**")
                hint_sent = True

    except Exception as e:
        await ctx.send(f"Error: {e}")

# RPS --------------------------------------------------------------------------------------------------------------
@bot.command()
async def rps(ctx):
    choices = ["rock", "paper", "scissors"]

    await ctx.send("🪨 📄 ✂️ Type **Rock**, **Paper**, or **Scissors**!")

    def check(m):
        return (
            m.author == ctx.author
            and m.channel == ctx.channel
            and m.content.lower() in choices
        )

    try:
        msg = await bot.wait_for("message", timeout=15, check=check)
    except asyncio.TimeoutError:
        return await ctx.send("⏰ You took too long!")

    user_choice = msg.content.lower()
    bot_choice = random.choice(choices)

    await ctx.send(f"🤖 I chose **{bot_choice}**!")

    if user_choice == bot_choice:
        await ctx.send("🤝 It's a tie!")
    elif(
        (user_choice == "rock" and bot_choice == "scissors") or
        (user_choice == "paper" and bot_choice == "rock") or
        (user_choice == "scissors" and bot_choice == "paper")
    ):
        await ctx.send("✅ You win!")
    else:
        await ctx.send("❌ You lose!")
    return None




bot.run(token, log_handler=handler, log_level=logging.DEBUG)