## Imports
from collections import Counter
from datetime import datetime

## Discord Imports
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

## Database Imports
import database
import requests
from database import *

## Tokens
load_dotenv()
token = os.getenv('DISCORD_TOKEN')



## Manually Give Bot Permissions (INTENTS)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

## Command To Communicate With Bot
bot = commands.Bot(command_prefix='$', intents=intents)


## EVENTS ##

## Bot Ready
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")

## Message Events
@bot.event
async def on_message(message):
    ## If message is bot, return
    if message.author == bot.user:
        return
    ## For every other message...

    ## Job Checker
    if "job" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} don't say the 'j' word in here lil bro...")

    ## Zest Counter
    zest_list = ["zest"]
    zest_count = 0

    with open("txt files/zests.txt", "a") as zest_file:
        if any(word in message.content.lower() for word in zest_list):
            zest_count += 1
        zest_file.write(f"+{zest_count}")
    zest_file.close()
    await bot.process_commands(message) ## Helps Bot Process Other Commands

## Bot Join Event
@bot.event
async def on_guild_join(guild):
    join_embed = discord.Embed(
        title = "shwanny bot has joined!",
        description = "Thank you for adding it to the server!",
        color = discord.Color.yellow()
    )

    join_embed.add_field(
        name = "What does shwanny bot do?",
        value = "It provides basic commands that can help make your server more efficient!",
        inline = False
    )

    join_embed.add_field(
        name = "How do I use it?",
        value = "Type $commands to get started!",
        inline = False
    )

    join_embed.timestamp = datetime.datetime.utcnow()
    await ctx.send(embed=join_embed)

## Table Check
if not table_exist_check('data'):
    ## Checks if table exists, if not it creates one
    create_table()

else:
    print("Table exists.")

@bot.event
async def on_guild_join(guild):
    ## When bot joins the server, record all usernames and assign their vc time to 0
    members = guild.members
    for member in members:
        record.insert("data", f"{member.display_name}", 0, 0, 0)

@bot.event
async def on_member_join(member):
    ## Add their name to their record with a time of 0
    record_insert("data", f"{member.display_name}", 0, 0, 0)

    ## Fetch results and print the table
    c.execute("SELECT * FROM data")
    items = c.fetchall()
    for item in items:
        print(item)

@bot.event
async def on_disconnect():
    c.close()


@bot.event
async def on_voice_state_update(member, before, after):
    ## Variables
    user_name = member.display_name

    if before.channel is None and after.channel is not None:
        ## Get Time When They Join
        t_now = datetime.now()
        seconds = (t_now.hour * 3600) + (t_now.minute * 60) + t_now.second
        c.execute(f"UPDATE data SET start_time={seconds}, end_time=0 WHERE user= '{user_name}'")
        print(f"{user_name} is being recorded")

    if before.channel is not None and after.channel is None:
        ## Get Time When They Leave
        t_now = datetime.now()
        seconds = (t_now.hour * 3600) + (t_now.minute * 60) + t_now.second
        c.execute(f"UPDATE data SET end_time={seconds} WHERE user= '{user_name}'")

        ## Get NEW Duration
        c.execute(f"SELECT start_time, end_time FROM data where user= '{user_name}'")
        t = c.fetchall()
        list_1 = []
        list_2 = []

        for item in t:
            for item in item:
                list_1.append(item)
        dur = list_1[1] - list_1[0]
        if dur > 0:
            dur = dur
        if dur < 0:
            dur = dur + 86400

        ## Get OLD Duration
        c.execute(f"SELECT duration FROM data where user= '{user_name}'")
        t= c.fetchall()
        for item in t:
            for item in item:
                list_2.append(item)
        new_dur = dur+list_2[0]
        c.execute(f"UPDATE data SET duration={new_dur} WHERE user= '{user_name}'")
    conn.commit()


## BASIC COMMANDS ##
@bot.command()
async def commands(ctx):
    commands_present = discord.Embed(
        title= "All shwannybot Commands",
        description= "Use $ to activate the bot",
        color=discord.Color.dark_blue()
    )

    with open("txt files/commands.txt", "r") as file:
        lines = file.readlines()
    file.close()

    commands_present.add_field(
        name = "Basic Commands",
        value = "",
        inline = False
    )

    for line in lines[0:3]:
        commands_present.add_field(
            name = "",
            value = line,
            inline = False
        )

    commands_present.add_field(
        name = "Unique Commands",
        value = "",
        inline = False
    )

    for line in lines[4:9]:
        commands_present.add_field(
            name="",
            value=line,
            inline= False
        )

    await ctx.send(embed=commands_present)

@bot.command()
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)


## PERSONALISED COMMANDS ##

## Watch List Entry
@bot.command()
async def towatch_entry(ctx, *, entry):
    with open("txt files/towatch_list.txt", "a", encoding="utf-8") as file:
        file.write(f"{entry}: {ctx.author}" + "\n")
        file.close()
    await ctx.send(f"{ctx.author.mention} has added {entry} to the watch-list!")

## Watch List Remove
@bot.command()
async def towatch_clear(ctx, *, entry):
    with open("txt files/towatch_list.txt", "r", encoding="utf-8") as file:
        line_list = []
        for line in file:
            if entry.lower() in line.lower():
                line_list = line_list
            else:
                line_list.append(line)
        file.close()

    with open("txt files/towatch_list.txt", "w", encoding="utf-8") as file:
        for movie in line_list:
            file.write(movie)
        file.close()
        await ctx.send(f"{ctx.author.mention} has removed {entry} from the watch-list!")

## Watch List Print
@bot.command()
async def towatch_list(ctx):
    count = 1

    with open("txt files/towatch_list.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    if not lines:
        await ctx.send(f"There is nothing on the watch list!")
        return

    else:
        list_present = discord.Embed(
            title="Watch List",
            description="We NEED To Watch These!",
            color=discord.Color.dark_purple()
        )

        for line in lines:
            list_present.add_field(
                name="",
                value=f"{count}. {line}",
                inline=False
            )
            count += 1
        file.close()
        await ctx.send(embed=list_present)

## Zest Counter
@bot.command()
async def zest_count(ctx):
    with open("txt files/zests.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        count=eval(lines[0])
    file.close()

    zest_embed = discord.Embed(
        title="Zest Count",
        description="This is how many times this server been zesty!",
        color=discord.Color.pink()
    )
    zest_embed.add_field(
        name="Count",
        value= str(count),
        inline=False
        )
    await ctx.send(embed=zest_embed)

## ADMIN COMMANDS ##
@bot.command()
async def table(ctx):
    c.execute("SELECT * FROM data")
    items = c.fetchall()
    for item in items:
        print(item)

@bot.command()
async def tablewipe(ctx):
    table_wipe('data')
    print("Table Wiped")

@bot.command()
async def vc_time(ctx, user: discord.Member):
    ## Variables
    c.execute(f"SELECT * FROM data WHERE user= '{user.id}'")
    d_name = user.display_name

    if c.fetchone() is None:
        dur_display = discord.Embed(
            title=f"{d_name}'s Total VC-Time",
            description="",
            color=discord.Color.purple()
        )
        dur_display.add_field(
            name="",
            value=f"Has no VC-Time!",
            inline=False
        )
        await ctx.send(embed=dur_display)


    else:
        c.execute(f"SELECT duration FROM data WHERE user= '{d_name}'")
        duration = c.fetchone()[0]

        dur_display = discord.Embed(
            title=f"{d_name}'s Total VC-Time",
            description="",
            color=discord.Color.purple()
        )
        dur_display.add_field(
            name="",
            value=f"A total of: {round(duration/3600, 2)} hours!",
            inline=False
        )
        await ctx.send(embed=dur_display)

## Bot Run: Token, The Handler, The Debug File
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
