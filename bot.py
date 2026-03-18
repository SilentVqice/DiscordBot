import discord
import logging
import os
import json
import asyncio
import aiohttp
import random
import html
import sys
import yt_dlp as youtube_dl
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

# BOT START ---------------------------------------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}! :3")

############################################ R.I.C.H  P.R.E.S.E.N.C.E. ############################################

##################################################### H.E.L.P #####################################################
@bot.command()
async def help(ctx):
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
            ";flag": "Starts a country flag trivia question. - ;flag",
            ";connect4": "Starts an interactive Connect 4 game. - ;connect4 [@user]"
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
        812269541731074078: "Cutest girl :3",
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
            return await ctx.send(f"Voice support is missing. Install `PyNaCl` and `davey`, then restart the bot.\n{voice_runtime_info()}")
    await ctx.send(f"Command error: {error}")

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
youtube_dl.utils.bug_reports_message = lambda *args, **kwargs: ""

ytdl_format_options = {
    "format": "bestaudio/best",
    "noplaylist": True,
    "quiet": True,
    "default_search": "auto",
    "js_runtimes": {
        "deno": {}
    },
    "extractor_args": {
        "youtube": {
            "player_skip": ["js"],
        }
    },
}
ffmpeg_options = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
song_queue = []
loop_song = False
current_song = None

async def get_song_info(query):
    loop = asyncio.get_running_loop()

    def extract():
        return ytdl.extract_info(query, download=False)

    info = await loop.run_in_executor(None, extract)

    if "entries" in info and info["entries"]:
        info = info["entries"][0]

    return {
        "query": query,
        "title": info.get("title", "Unknown"),
        "webpage_url": info.get("webpage_url") or info.get("original_url") or "",
        "audio_url": info.get("url"),
        "duration": info.get("duration") or 0,
        "thumbnail": info.get("thumbnail"),
        "uploader": info.get("uploader") or info.get("channel") or "Unknown",
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
    }

async def play_next(ctx):
    global loop_song, current_song

    if not ctx.voice_client or not ctx.voice_client.is_connected():
        return

    if loop_song and current_song:
        song = current_song
    else:
        if not song_queue:
            current_song = None
            await safe_disconnect(ctx)
            return
        song = song_queue.pop(0)
        current_song = song

    audio_url = song.get("audio_url")
    if not audio_url:
        await ctx.send("⚠️ Couldn't get a playable stream for this track.")
        if song_queue:
            await play_next(ctx)
        return

    source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)

    def after_playback(error):
        if error:
            print(f"Playback error: {error}")
        if ctx.voice_client and ctx.voice_client.is_connected():
            future = asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop)
            try:
                future.result()
            except Exception as e:
                print(f"Error in play_next {e}")

    ctx.voice_client.play(source, after=after_playback)

    title = song.get("title", "Unknown")
    webpage_url = song.get("webpage_url", "")
    duration = song.get("duration") or 0
    thumbnail = song.get("thumbnail")
    uploader = song.get("uploader") or "Unknown"
    views = song.get("views")
    likes = song.get("likes")

    minutes, seconds = divmod(duration, 60)
    duration_text = f"{minutes}:{seconds:02d}"

    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"**[{title}]({webpage_url})**",
        colour=discord.Colour.red(),
        url=webpage_url
    )
    embed.add_field(name="⏱ Duration", value=duration_text, inline=True)
    embed.add_field(name="📺 Uploader", value=uploader, inline=True)
    embed.add_field(name="🔁 Loop", value="ON" if loop_song else "OFF", inline=True)

    if views is not None:
        embed.add_field(name="👀 Views", value=f"{views:,}", inline=True)

    if likes is not None:
        embed.add_field(name="👍 Likes", value=f"{likes:,}", inline=True)

    embed.add_field(name="📂 Queue", value=str(len(song_queue)), inline=True)

    if thumbnail:
        embed.set_image(url=thumbnail)

    embed.set_footer(text="Use ;queue to view upcoming songs.")

    await ctx.send(embed=embed)

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        if not getattr(discord.voice_client, "has_nacl", False):
            return await ctx.send(f"Voice support is missing. Install `PyNaCl` and `davey`, then restart the bot.\n{voice_runtime_info()}")
        try:
            await ctx.author.voice.channel.connect()
            await ctx.send("🔊 Joined your voice channel!")
        except RuntimeError as e:
            return await ctx.send(f"Voice connect failed: {e}\n{voice_runtime_info()}")
    else:
        await ctx.send("⚠️ You must be in a voice channel!")

@bot.command()
async def play(ctx, *, query):
    if not ctx.author.voice:
        return await ctx.send("⚠️ You must be in a voice channel!")
    if not ctx.voice_client:
        await join(ctx)
    if not ctx.voice_client:
        return

    try:
        song = await get_song_info(query)
    except Exception as e:
        return await ctx.send(f"Couldn't load this track: {e}")

    if not song.get("audio_url"):
        return await ctx.send("⚠️ Couldn't get a playable stream for that track.")

    song_queue.append(song)

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        if song.get("webpage_url"):
            await ctx.send(f"➕ Added to queue: **[{song['title']}]({song['webpage_url']})**")
        else:
            await ctx.send(f"➕ Added to queue: **{song['title']}**")
    else:
        await play_next(ctx)
    return None

@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸ Paused the song")
    else:
        await ctx.send("⚠️ No song is playing!")

@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed the song")
    else:
        await ctx.send("⚠️ No song is paused!")

@bot.command()
async def skip(ctx):
    if ctx.voice_client and (ctx.voice_client.is_playing() or ctx.voice_client.is_paused()):
        ctx.voice_client.stop()
        await ctx.send("⏭ Skipped the song")
    else:
        await ctx.send("⚠️ Nothing is playing!")

@bot.command()
async def queue(ctx):
    global current_song

    def trim(text, limit=60):
        return text if len(text) <= limit else text[:limit - 3] + "..."

    if not current_song and not song_queue:
        return await ctx.send("📭 Queue is empty!")

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
async def leave(ctx):
    global current_song
    song_queue.clear()
    current_song = None
    await safe_disconnect(ctx)

@bot.command()
async def loop(ctx, mode: str = "off"):
    global loop_song
    if mode is None:
        loop_song = not loop_song
    elif mode.lower() == "on":
        loop_song = True
    elif mode.lower() == "off":
        loop_song = False
    else:
        return await ctx.send("⚠️ Use `on` or `off`.")

    await ctx.send(f"🔁 Loop is now **{'ON' if loop_song else 'OFF'}**")

@bot.command()
async def shuffle(ctx):
    random.shuffle(song_queue)
    await ctx.send("🔀 Queue shuffled")

@bot.command()
async def volume(ctx, volume: int):
    if ctx.voice_client and ctx.voice_client.source:
        if not isinstance(ctx.voice_client.source, discord.PCMVolumeTransformer):
            ctx.voice_client.source = discord.PCMVolumeTransformer(ctx.voice_client.source)
        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"🔊 Volume set to {volume}%")
    else:
        await ctx.send("⚠️ No song is playing!")

async def safe_disconnect(ctx):
    if ctx.voice_client and ctx.voice_client.is_connected():
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Left the voice channel")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)