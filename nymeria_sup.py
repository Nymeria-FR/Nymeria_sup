import datetime
from pytz import timezone
import discord
from config import TomlConfig
import time

client = discord.Client()
config = TomlConfig("config.toml", "config.template.toml")
global chrono
chrono = time.time()

@client.event
async def on_ready():
    global guild, cat
    guild = client.get_guild(int(config.guild))
    for category in guild.categories:
        if(category.id == int(config.sup_cat)):
            cat = category
    channel = guild.get_channel(int(config.ready_chan))
    date = datetime.datetime.now(timezone('Europe/Berlin'))
    embedVar = discord.Embed(title="Ready",
                             description="Logged as {}".format(client.user),
                             color=0x00ff00,
                             timestamp=date)
    await channel.send(embed=embedVar)

def member_in_cat(member):
    for channel in cat.channels:
        if channel.name == member.name.lower() + "_" + str(member.id):
            return channel.id
    return None

def take_id(name):
    id = str()
    for i in range(len(name) - 1, 0, -1):
        if(name[i] == "_"):
            break
        id = name[i] + id
    return int(id)

@client.event
async def on_message(message):
    global chrono
    if message.author.id != int(config.id):
        if(type(message.channel) == discord.DMChannel):
            id = member_in_cat(message.author)
            if(type(id) == int):
                channel = guild.get_channel(id)
                await channel.send(message.content)
                chrono = time.time()
            else:
                if time.time() - chrono < 5:
                    await message.author.send("Le service est surchargé veuillez ressayer plus tard")
                else:
                    name = message.author.name + "_" + str(message.author.id)
                    channel = await cat.create_text_channel(name)
                    await channel.send(message.content)
                    chrono = time.time()
        elif(message.channel.category.id == cat.id and 
            message.channel.id != int(config.ready_chan)):
            if message.content == "close":
                await message.channel.delete()
            else:
                id = take_id(message.channel.name)
                user = await client.fetch_user(id)
                await user.send(message.content)

client.run(config.token, bot=config.bot)
