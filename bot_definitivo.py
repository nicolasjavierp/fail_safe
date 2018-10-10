#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
import aiohttp
import json
from discord import Game
from discord.ext.commands import Bot
from fail_safe import FailSafe
import os
import discord

BOT_PREFIX = ("+") #("+", "!")
BOT_TOKEN = ''  # Get at discordapp.com/developers/applications/me

client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Bienvenido {0.mention} a {1.name}!'
    await client.send_message(server, fmt.format(member, server))

@client.event
async def on_message(message):
    if message.content.startswith("+rol"):
        my_server = discord.utils.get(client.servers)
        #print(dir(my_server))
        #print(dir(message.author))
        user_id = message.author.id
        user=my_server.get_member(user_id)
        user_roles_names=[]
        for i in user.roles:
            user_roles_names.append(i.name)

        role_E2 = discord.utils.get(my_server.roles, name="E2")
        role_E3 = discord.utils.get(my_server.roles, name="E3")
        if (role_E2.name and role_E3.name) in user_roles_names:
            await client.send_message(message.channel, "El Guardian "+message.author.mention+" ya tiene el rol "+role_E2.name+" !" )
            await client.send_message(message.channel, "El Guardian "+message.author.mention+" ya tiene el rol "+role_E3.name+" !" )
        else:
            #print("Adding role_E2")
            #print("Adding role_E3")
            await client.add_roles(user, role_E2)
            await client.add_roles(user, role_E3)
            await client.send_message(message.channel, "Successfully added role {0}".format(role_E2.name))
            await client.send_message(message.channel, "Successfully added role {0}".format(role_E3.name))




@client.command(name='Oraculo',
                description="Responde tus dudas existenciales.",
                brief="Respuestas de mas alla de la Dreaming City!",
                aliases=['oraculo', 'ora', 'o'],
                pass_context=True)
async def oraculo(context):
   
    respuestas_posibles = [
        'Oraculo: El destino indica un fuerte NO',
        'Oraculo: Es muy probable que no',
        'Oraculo: Deben definirse los caminos de otros Guardianes antes de que pueda responder',
        'Oraculo: Veo a través del plano ascendente que es muy probable',
        'Oraculo: Definitivamente, SI ... aqui tienes un Edge Transit',
    ]
    list_split_message = context.message.content.split(' ', 1)[1]
    if "?" not in context.message.content:
        await client.say(context.message.author.mention + " eso no es una pregunta ")
    elif "?" in context.message.content and len(list_split_message) > 4:
        await client.say(random.choice(respuestas_posibles) + ", " + context.message.author.mention)
    elif "?" in context.message.content and len(list_split_message) <= 4:
        await client.say(context.message.author.mention + " eso no es una pregunta que con mis poderes pueda contestar ...")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')



@client.command(name='Saludar',
                description="Saludo al guardian",
                brief="saludo",
                aliases=['hola', 'hello'],
                pass_context=True)
async def saludar(context):
    msg = 'Hello {0.author.mention}'.format(context.message)
    await client.send_message(context.message.channel, msg)




async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(BOT_TOKEN)