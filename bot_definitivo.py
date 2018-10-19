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


THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
my_config_file = os.path.join(THIS_FOLDER, 'config.json')

with open(my_config_file, 'r') as f:
        config = json.load(f)

BOT_PREFIX = ("+") #("+", "!")
BOT_TOKEN = config['DEFAULT']['BOT_TOKEN']# Get at discordapp.com/developers/applications/me
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
    if len(context.message.content)>=4 and valid_battle_tag_ending:
        fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"])         #Start Fail_Safe
        user_battletag = context.message.content.split(' ', 1)[1]   #separate +rol from message
        user_destiny = fs.get_playerByTagName(fs.format_PlayerBattleTag(user_battletag)) #Search for player battletag NOT Case Sensitive
        if user_destiny:
            user_destiny_id = user_destiny[0]['membershipId'] #From response extract the ID
            real_battletag = user_destiny[0]['displayName']
            #From response extract real_battletag because Bungies api is not case sensitive so it responds to gglol#1234 and to Gglol#1234 we need the latter
            if is_user_in_users(context.message.author) and is_clanmate_in_clan(real_battletag):
                #User is in users.json AND clanmate in clan.json
                name, number = real_battletag.split('\#')
                await client.send_message(context.message.channel, "El Guardian "+name+" ya fue dado de alta y tiene los roles! ")
            else:
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

                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                #if user_destiny_id and user_clan_name:
                if user_clan_name:
                    if "Escuadra" in user_clan_name:
                        await client.add_roles(user, role_Clan)
                        await client.add_roles(user, role_DJ)
                        if not is_user_in_users(context.message.author):
                            await add_user_data(context.message.author)
                        else:
                            #print(context.message.author.name + " is in users.json!!")
                            pass
                        if not is_clanmate_in_clan(real_battletag):
                            await add_clanmate_to_clan(real_battletag, user_clan_name)
                        else:
                            #print(battletag + " is in clan.json!!")
                            pass
                        await client.send_message(context.message.channel, "Rol {0} y {1} agregado con exito ".format(role_Clan.name, role_DJ.name))
                    else:
                        await client.send_message(context.message.channel, context.message.content+" no figuras en el clan! No puedo dare los roles si no estas en el clan ¯\\_(ツ)_/¯" )        
                else:
                    await client.send_message(context.message.channel, "Battletag Invalido ó Error al conecatr a Bungie, comunique se con un admin por favor" )        
        else:
            await client.send_message(context.message.channel, "Battletag Invalido ó Error al conecatr a Bungie, comunique se con un admin por favor" )
    else:
        await client.send_message(context.message.channel, "Error de uso! Ejemplo: +rol CNorris#2234" )
    #delets the message
    await client.delete_message(context.message)
    #await asyncio.sleep(600)


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


@client.command(name='Poblacion',
                description="Indica los integrantes de discord",
                brief="poblacion",
                aliases=['poblacion','pob'],
                pass_context=True)
async def poblacion(context):
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
        await client.send_message(context.message.channel, "Total Usuarios: " + str(my_server.member_count))
        bot_num=0
        for memb in my_server.members:
                #if is_user_in_users(memb):
                #    print(memb.name + " already in users.json !!")
                #else:
                #    print(memb.name + " NOT in users.json !!")
                #    await add_user_data(memb)
                if memb.bot:
                    bot_num = bot_num+1
        await client.send_message(context.message.channel, "Guardianes = "+str(my_server.member_count-bot_num) + "\n" + "Bots = "+str(bot_num))
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
            print(memb.name+" is not in users.json ... adding ...")
            users[memb.id] = [memb.name, memb.nick]
    with open('users.json', 'w') as f:
            json.dump(users,f)


async def add_user_data(member):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if not member.bot and not member.id in users:
            #print(member.id+" is not in users.json ... adding ...")
            #print(dir(member))
            my_server = discord.utils.get(client.servers)
            user=my_server.get_member(member.id)
            users[member.id] = [member.name, user.nick]
    with open('users.json', 'w') as f:
            json.dump(users,f)

async def add_clanmate_to_clan(clanmate_battletag, clan):
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        if not clanmate_battletag in clan:
            #print(clanmate_battletag+" battletag is not in clan.json ... adding ...")
            clan[clanmate_battletag] = [clan, None]
    with open('clan.json', 'w') as f:
            json.dump(clan,f)


#@client.event
#async def on_message(message):
    # we do not want the bot to reply to itself
    #if message.author == client.user:
    #    return

    #if message.content.startswith('!hello'):
    #    msg = 'Hello {0.author.mention}'.format(message)
    #    await client.send_message(message.channel, msg)


#async def populate_clan_data(clan):
#    our_clans = [(2943900, "Escuadra 2"), (3084439, "Escuadra 3"), (3111393, "Escuadra 4"), (3144839,"Escuadra 5")]
#    fs = FailSafe(api_key=os.environ["BUNGIE_API_KEY"])
#    with open('clan.json', 'r') as f:
#        clan = json.load(f)
#    for clan in our_clans:
#        #get_ClanPlayerList takes too long split in to many little asyncs
#        clan_list = fs.get_ClanPlayerList(clan)
#        for player in clan_list:
#            print("-+-+-+-+-+-+-+-+-+-+")
#            for key in player:
#                print(player[key][0], player[key][1]["profile"]["data"]["userInfo"]["membershipId"])
#                #print(memb.name+" is not in clan.json ... adding ...")
#                #clan[memb.id] = [memb.name, memb.nick]
#        with open('clan.json', 'w') as f:
#                json.dump(clan,f)



def is_user_in_users(user):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if user.id in users:
            return True
        else:
            return False

def is_clanmate_in_clan(clanmate_battletag):
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        if clanmate_battletag in clan:
            return True
        else:
            return False

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


client.loop.create_task(list_servers())
client.run(BOT_TOKEN)