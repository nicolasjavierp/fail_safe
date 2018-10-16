#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
import aiohttp
from discord.ext.commands import Bot
from fail_safe import FailSafe
import os
from fail_safe import FailSafe
import discord
import re
import json
from datetime import datetime


BOT_PREFIX = ("+") #("+", "!")
BOT_TOKEN = ''  # Get at discordapp.com/developers/applications/me

Discord_User_ids = []

client = Bot(command_prefix=BOT_PREFIX)


@client.event
async def on_member_join(member):
    #with open('users.json', 'r') as f:
    #    users = json.load(f)
    #await update_user_data(users, member)
    #with open('users.json', 'w') as f:
    #    json.dump(users,f)
    
    server = member.server
    #print(server)
    #print(dir(server))
    #print(server.default_channel)
    #print(dir(server.default_channel))
    for i in server.channels:
        #print(i.name)
        if "invitados" in i.name :
            canal_bienvenida = i
            
    fmt = 'Bienvenido {0.mention} a {1.name}!'

    await client.send_message(canal_bienvenida, fmt.format(member, server))
    await client.send_message(canal_bienvenida,"Para obtener roles usar el commando: +rol tu_blizard_battletag")
    await client.send_message(canal_bienvenida,"Cualquier duda no dudes en comunicarte con un admin")

@client.command(name='Rol',
                description="Autoprovisioning de Roles Clan y DJ",
                brief="Autoprovisioning Escuadra X",
                aliases=['rol'],
                pass_context=True)
async def rol(context):
        valid_battle_tag_ending = bool(re.match('^.*#[0-9]{4,5}$', context.message.content))
        if len(context.message.content)>=4 and "#" in context.message.content and valid_battle_tag_ending:
            fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"]) 
            my_server = discord.utils.get(client.servers)
            user_id = context.message.author.id
            user=my_server.get_member(user_id)
            user_roles_names=[]
            for i in user.roles:
                user_roles_names.append(i.name)
            
            for i in my_server.roles:
                if "Clan" in i.name:
                    custom_clan_role_id=i.id
            
            role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
            role_DJ = discord.utils.get(my_server.roles, name="DJ")

            #if (role_Clan.name and role_DJ.name) in user_roles_names:
            #print("------------")
            #print(user_id, Discord_User_ids)
            if (user_id in Discord_User_ids):
                await client.send_message(context.message.channel, "El Guardian "+context.message.author.mention+" ya tiene los roles! ")
                #print("Guardian ya tiene roles!!")
            else:
                battletag = context.message.content.split(' ', 1)[1]
                user_destiny_id = fs.get_DestinyUserId(fs.format_PlayerBattleTag(battletag))
                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                if user_destiny_id and user_clan_name:
                    if "Escuadra" in user_clan_name:
                        await client.add_roles(user, role_Clan)
                        await client.add_roles(user, role_DJ)
                        if user_id not in Discord_User_ids:
                            Discord_User_ids.append(user_id)
                        await client.send_message(context.message.channel, "Rol {0} y {1} agregado con exito ".format(role_Clan.name, role_DJ.name))
                    else:
                        await client.send_message(context.message.channel, context.message.content+" no figuras en el clan! No puedo dare los roles si no estas en el clan ¯\\_(ツ)_/¯" )        
                else:
                    await client.send_message(context.message.channel, "Battletag Invalido ó Error al conecatr a Bungie, comunique se con un admin por favor" )        
        else:
            await client.send_message(context.message.channel, "Error de uso! Ejemplo: +rol CNorris#2234" )


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


@client.command(name='Populacion',
                description="Indica los integrantes de discord",
                brief="populacion",
                aliases=['populacion','pop'],
                pass_context=True)
async def populacion(context):
    my_server = discord.utils.get(client.servers)
    user_id = context.message.author.id
    user=my_server.get_member(user_id)
    for i in my_server.roles:
        if "Admin" in i.name:
                    admin_id=i.id
    if admin_id in [role.id for role in user.roles]:
        await client.send_message(context.message.channel, "Populación Discord:")
        #for memb in my_server.members:
        #    print(memb)
        #    print(memb.bot)
        #    print(dir(memb))
        await client.send_message(context.message.channel, "#Guardianes: " + str(my_server.member_count))
        
        for memb in my_server.members:
                #id_discord, battletag , discord_name , begin_date (text)
                if not memb.bot:
                    #print(memb.name+" "+str(idx)+"/"+str(len(my_server.members)))
                    #guardian = (user_id, memb.name, memb.nick, "{:%Y-%M-%d %H:%m:%S}".format(datetime.now()) )
                    #guardian = str(memb.id)+","+str(memb.name)+","+str(memb.nick)+",""{:%Y-%M-%d %H:%m:%S}".format(datetime.now())
                    #print(guardian)
                    #if user_id not in Discord_User_ids:
                    #    Discord_User_ids.append(memb.id)
                    
                    #await update_user_data(users, user)
                    await client.send_message(context.message.channel, str(memb.name)+", "+str(memb.nick))
        users = 'users.json'
        await populate_user_data(users)

    else:
        await client.send_message(context.message.channel, "No tenes permisos para ejecutar este comando")
    


async def populate_user_data(users):
    with open('users.json', 'r') as f:
            users = json.load(f)
    my_server = discord.utils.get(client.servers)
    for memb in my_server.members:
        if not memb.bot and not memb.id in users:
            users[memb.id] = [memb.name, memb.nick]
    with open('users.json', 'w') as f:
            json.dump(users,f)


async def is_user_in_json(users, user):
    if user.id in users:
        return True
    else:
        return False

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
            print(Discord_User_ids)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(BOT_TOKEN)