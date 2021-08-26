import datetime
import re
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


def member_in_cat(member: discord.Member):
    """fonction faite pour savoir si un membre à
    déjà un chanel dédié pour lui

    Parameters
    ----------
    member : discord.member
        membre discord

    Return
    ------
    int / None
        revoie l'id du chanel ou None si
        le membre n'a pas de chanel pour lui
    """
    for channel in cat.channels:
        if channel.topic == str(member.id):
            return channel.id
    return None


def is_sup_message(message: discord.Message):
    """fonction qui vérifie si une rection a
    été mise sur un message qui peut close un chanel

    Parameters
    ----------
    chan : discord.message
        message discord

    Return
    ------
    bool
        vrais si c'est un message qui peut
        suprimer un chanel
    """
    if message.pinned:
        reactions = message.reactions
        for reaction in reactions:
            if reaction.emoji == config.extern["close_emoji"] and reaction.me:
                return True
    return False


async def close_chan(chan: discord.TextChannel):
    """fermeture de chanel support

    envoi message au membre et suprim le chanel

    Parameters
    ----------
    chan : discord.TextChannel
        channel discord
    """
    id = int(chan.topic)
    user = await client.fetch_user(id)
    close_message = discord.Embed(title="Ticket fermé",
                                  description=f"Ton ticket a été fermé par le support.")
    await user.send(embed=close_message)
    await chan.delete()


@client.event
async def on_ready():
    """
    event quand le bot est lancé
    """
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


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """
    event quand le bot détecte
    qu'un event à été ajouté

    Parameters
    ----------
    payload : discord.RawReactionActionEvent
        reaction inforamtion
    """
    if (is_sup_message(await client.get_guild(payload.guild_id)
                       .get_channel(payload.channel_id)
                       .fetch_message(payload.message_id)) and
            payload.user_id != client.user.id):
        await close_chan(client.get_guild(payload.guild_id)
                         .get_channel(payload.channel_id))
    return


@client.event
async def on_message(message: discord.Message):
    """
    event quand le bot détecte
    qu'un message à été envoyé

    Parameters
    ----------
    message : discord.Message
        message discord
    """
    global chrono
    if message.author.id != client.user.id:
        if(type(message.channel) == discord.DMChannel):
            id = member_in_cat(message.author)
            if(type(id) == int):
                channel = guild.get_channel(id)
            else:
                if time.time() - chrono < 5:
                    await message.author.send("Le service est surchargé veuillez ressayer plus tard")
                    return
                else:
                    name = message.author.name + "-mp"
                    channel = await cat.create_text_channel(name)
                    await channel.edit(topic=str(message.author.id))
                    new = discord.Embed(title="Un member demande de l'aide",
                                        description=f"Mention: {message.author.mention}\nUtilisateur: {message.author}\n ID: {message.author.id}")
                    new.set_footer(text="Merci de cliquer sur 🔒 pour fermer le ticket.")
                    reponse = await channel.send(embed=new)
                    await reponse.add_reaction(config.extern["close_emoji"])
                    await reponse.pin()
                    chrono = time.time()
                    embed_message = discord.Embed(title="Un nouveau message :",
                                                  description=f"**Son message :**\n{message.content}")
                    await channel.send(embed=embed_message)

        elif(message.channel.category.id == cat.id and
             message.channel.id != bot["ready_chan"]):
            if message.content == "close":
                await close_chan(message.channel)

            else:
                await message.delete()
                id = int(message.channel.topic)
                user = await client.fetch_user(id)
                admin_message = discord.Embed(title=f"{message.author}",
                                              description=f"{message.content}")
                await message.channel.send(embed=admin_message)
                user_message = discord.Embed(title="Réponse du staff",
                                             description=f"{message.content}")
                await user.send(embed=user_message)


client.run(bot["token"], bot=bot["bot"])
