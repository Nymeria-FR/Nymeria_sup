import datetime
import discord
import time
import sys
import os

from pytz import timezone
from config import TomlConfig

client = discord.Client()
config = TomlConfig("config.toml", "config.template.toml")
bot = config.bots[sys.argv[1]]

with open(config.extern["pid"], 'a') as pid:
    pid.write(sys.argv[1] + " " + str(os.getpid()) + "\n")

global chrono
chrono = time.time()


@client.event
async def on_ready():
    print("Logged as {}!".format(client.user))
    global guild, cat
    guild = client.get_guild(bot["guild"])
    for category in guild.categories:
        if category.id == bot["sup_cat"]:
            cat = category
    channel = guild.get_channel(bot["ready_chan"])
    date = datetime.datetime.now(timezone('Europe/Berlin'))
    embedVar = discord.Embed(title="Ready",
                             description="Logged as {}".format(client.user),
                             color=0x00ff00,
                             timestamp=date)
    await channel.send(embed=embedVar)


def member_in_cat(member):
    for channel in cat.channels:
        if channel.topic == str(member.id):
            return channel.id
    return None


@client.event
async def on_message(message):
    global chrono
    if message.author.id != client.user.id:
        if(type(message.channel) == discord.DMChannel):
            id = member_in_cat(message.author)
            if(type(id) == int):
                channel = guild.get_channel(id)
            else:
                if time.time() - chrono < 5:
                    await message.author.send("Le service est surchargé veuillez ressayer plus tard")
                else:
                    name = message.author.name + "-mp"
                    channel = await cat.create_text_channel(name)
                    await channel.edit(topic=str(message.author.id))
                    new = discord.Embed(title="Un member demande de l'aide",
                                        description=f"Mention: {message.author.mention}\nUtilisateur: {message.author.name}\n ID: {message.author}")
                    await channel.send(embed=new)
                    chrono = time.time()
            message = discord.Embed(title="Un nouveau message :",
                                    description=f"**Son message :**\n{message.content}")
            await channel.send(embed=message)
        elif(message.channel.category.id == cat.id and
             message.channel.id != bot["ready_chan"]):
            if message.content == "close":
                await message.channel.delete()

            else:
                await message.delete()
                id = int(message.channel.topic)
                user = await client.fetch_user(id)
                admin_message = discord.Embed(title=f"{message.author.name}",
                                              description=f"{message.content}")
                await message.channel.send(embed=admin_message)
                user_message = discord.Embed(title="Réponse du staff",
                                             description=f"{message.content}")
                await user.send(embed=user_message)


client.run(bot["token"], bot=bot["bot"])
