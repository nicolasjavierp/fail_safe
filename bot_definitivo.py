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
from fail_safe import FailSafe
import discord
import re

BOT_PREFIX = ("+") #("+", "!")
BOT_TOKEN = ''  # Get at discordapp.com/developers/applications/me

client = Bot(command_prefix=BOT_PREFIX)

@client.event
async def on_member_join(member):
    server = member.server
    fmt = 'Bienvenido {0.mention} a {1.name}!'
    await client.send_message(server, fmt.format(member, server))
    await client.send_message(server,"Para autoprovisionarte roles usar el commando: +rol tu_blizard_battletag")
    await client.send_message(server,"Cualquier duda no dudes en comunicarte con un admin")

@client.command(name='Rol',
                description="Autoprovisioning de Roles Clan y DJ",
                brief="Autoprovisioning Escuadra X",
                aliases=['rol'],
                pass_context=True)
async def rol(context):
        valid_battle_tag_ending = bool(re.match('^.*#[0-9][0-9][0-9][0-9]$', context.message.content))
        if len(context.message.content)>=4 and "#" in context.message.content and valid_battle_tag_ending:
            fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) 
            my_server = discord.utils.get(client.servers)
            user_id = context.message.author.id
            user=my_server.get_member(user_id)
            user_roles_names=[]
            for i in user.roles:
                user_roles_names.append(i.name)

            role_E2 = discord.utils.get(my_server.roles, name="E2")
            role_E3 = discord.utils.get(my_server.roles, name="E3")

            if (role_E2.name and role_E3.name) in user_roles_names:
                await client.send_message(context.message.channel, "El Guardian "+context.message.author.mention+" ya tiene el rol "+role_E2.name+" !" )
                await client.send_message(context.message.channel, "El Guardian "+context.message.author.mention+" ya tiene el rol "+role_E3.name+" !" )
            else:
                battletag = context.message.content.split(' ', 1)[1]
                user_destiny_id = fs.get_DestinyUserId(fs.format_PlayerBattleTag(battletag))
                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                #print(user_destiny_id)
                #print(user_clan_name)
                #print("//////////////")
                if user_destiny_id and user_clan_name:
                    if user_clan_name == "Escuadra 5":
                        await client.add_roles(user, role_E2)
                        await client.add_roles(user, role_E3)
                        await client.send_message(context.message.channel, "Successfully added role {0}".format(role_E2.name))
                        await client.send_message(context.message.channel, "Successfully added role {0}".format(role_E3.name))
                    else:
                        await client.send_message(context.message.channel, "No figuras en el clan, ya van los sicarios para tu casa..." )        
                else:
                    await client.send_message(context.message.channel, "Battletag Invalido ó Error al conecatr a Bungie, comunique se con un admin por favor" )        
        else:
            await client.send_message(context.message.channel, "Error de uso! Ejemplo:" )
            await client.send_message(context.message.channel, "+rol Javu#2632" )


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