#!/usr/local/bin/python3.6
# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
import aiohttp
from discord.ext.commands import Bot
from fail_safe import FailSafe
import os, time
import discord
import re
import json
from datetime import datetime
from boto.s3.connection import S3Connection
import unicodedata
from urllib.request import urlopen

#4 Heroku
BUNGIE_API_KEY = os.environ['BUNGIE_API_KEY']
BOT_TOKEN = os.environ['BOT_TOKEN']

#4 Tests
#THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
#my_config_file = os.path.join(THIS_FOLDER, 'config.json')

#with open(my_config_file, 'r') as f:
#        config = json.load(f)

#BOT_TOKEN = config['DEFAULT']['BOT_TOKEN']# Get at discordapp.com/developers/applications/me
#END Tests

BOT_PREFIX = ("+") #("+", "!")
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
    await client.send_message(canal_bienvenida,"Para obtener roles usar el commando: +rol tu_blizard_battletag. \n Cualquier duda no dudes en comunicarte con un admin")

@client.command(name='Rol',
                description="Autoprovisioning de Roles Clan y DJ",
                brief="Autoprovisioning Escuadra X",
                aliases=['rol'],
                pass_context=True)
async def rol(context):
    #print("Entered command ROL!")
    valid_battle_tag_ending = bool(re.match('^.*#[0-9]{4,5}$', context.message.content))
    if len(context.message.content)>=4 and valid_battle_tag_ending:
        #print("Valid Battletag format!")
        #4 tests
        #fs = FailSafe(config['DEFAULT']['BUNGIE_API_KEY'])         #Start Fail_Safe 4tests
        #END tests
        #4 Heroku
        fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
        #END Heroku
        user_battletag = context.message.content.split(' ', 1)[1]   #separate +rol from message
        user_destiny = fs.get_playerByTagName(fs.format_PlayerBattleTag(user_battletag)) #Search for player battletag NOT Case Sensitive
        if user_destiny:
            print("Valid User Destiny= "+str(user_destiny))
            user_destiny_id = user_destiny[0]['membershipId'] #From response extract the ID
            real_battletag = user_destiny[0]['displayName']
            #From response extract real_battletag because Bungies api is not case sensitive so it responds to gglol#1234 and to Gglol#1234 we need the latter
            my_server = discord.utils.get(client.servers)
            user_id = context.message.author.id
            user=my_server.get_member(user_id)
            user_roles_names=[]
            #Get users roles
            for i in user.roles:
                user_roles_names.append(i.name)
            #Get clan defined roles ids from discord
            for i in my_server.roles:
                if "Clan" in i.name:
                    custom_clan_role_id=i.id
                if "DJ" in i.name:
                    custom_dj_role_id=i.id

            role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
            role_DJ = discord.utils.get(my_server.roles, id=custom_dj_role_id)

            if is_user_in_users(context.message.author) and is_clanmate_in_clan(real_battletag):
                #User is in users.json AND clanmate in clan.json
                print(str(context.message.author.name) +" with BT= "+ str(real_battletag) +" in clan and in users !")
                name = real_battletag.split('#')[0]
                #Verification if discord api does not work initialy
                user_has_role_clan = await does_user_have_role(user,custom_clan_role_id)
                user_has_role_dj = await does_user_have_role(user,custom_dj_role_id)
                
                #print(user_has_role_clan)
                #print(user_has_role_dj)
                
                if not user_has_role_clan or not user_has_role_dj:
                    await client.send_message(context.message.channel, "El Guardian "+str(name)+" le falta un rol ... reintentando! ")
                    await client.add_roles(user, role_Clan)
                    await client.add_roles(user, role_DJ)       
                await client.send_message(context.message.channel, "El Guardian "+str(name)+" ya fue dado de alta y tiene los roles! ")
            else:
                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                #if user_destiny_id and user_clan_name:
                if user_clan_name:
                    if "Escuadra" in user_clan_name:
                        await client.add_roles(user, role_Clan)
                        await client.add_roles(user, role_DJ)
                        if not is_user_in_users(context.message.author):
                            #print(real_battletag + " is NOT in users.json!!")
                            await add_user_data(context.message.author)
                        else:
                            print(context.message.author.name + " is in users.json!!")
                            pass
                        if not is_clanmate_in_clan(real_battletag):
                            #print(real_battletag + " is NOT in clan.json!!")
                            await add_clanmate_to_clan(real_battletag, user_clan_name)
                        else:
                            print(real_battletag + " is in clan.json!!")
                            pass
                        await client.send_message(context.message.channel, "Rol {0} y {1} agregado con exito. Bienvenido al clan ! ".format(role_Clan.name, role_DJ.name))
                    else:
                        await client.send_message(context.message.channel, name+" no figuras en el clan! No puedo dare los roles si no estas en el clan ¯\\_(ツ)_/¯" )        
                else:
                    print("User clan name = "+str(user_clan_name) + "  and  "+ str(user_battletag))
                    await client.send_message(context.message.channel, "No pude determinar tu clan, comunicate con un admin por favor" )        
        else:
            print("User Destiny = "+str(user_destiny) + "  and  "+ str(user_battletag))
            await client.send_message(context.message.channel, "Battletag Invalido ó Error al conecatr a Bungie, comunique se con un admin por favor" )
    else:
        await client.send_message(context.message.channel, "Error de uso! Ejemplo: +rol CNorris#2234" )
    #delets the message
    await client.delete_message(context.message)
    #await asyncio.sleep(600)


#@client.command(name='Oraculo',
#                description="Responde tus dudas existenciales.",
#                brief="Respuestas de mas alla de la Dreaming City!",
#                aliases=['oraculo', 'odc'],
#                pass_context=True)
#async def oraculo(context):
#    respuestas_posibles = [
#        'Oraculo: El destino indica que NO',
#        'Oraculo: Es muy probable que no',
#        'Oraculo: Todavia no esta definido',
#        #'Oraculo: Preguntame en un rato',
#        # No cuentes con ello
#        # Es cierto
#        # Muy dudoso
#        # No puedo predecirlo ahora
#        # En mi opinión, sí
#        # Sin duda
#        # No
#        # Si
#        'Oraculo: Veo ... que es muy probable',
#        'Oraculo: Definitivamente, SI ... aqui tienes un Edge Transit'
#    ]
#    list_split_message = context.message.content.split(' ', 1)[1]
#    if "?" not in context.message.content:
#        await client.say(context.message.author.mention + " eso no es una pregunta ")
#    elif "?" in context.message.content and len(list_split_message) > 4:
#        await client.say(random.choice(respuestas_posibles) + ", " + context.message.author.mention)
#    elif "?" in context.message.content and len(list_split_message) <= 4:
#        await client.say(context.message.author.mention + " eso no es una pregunta que con mis poderes pueda contestar ...")
#


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
    currentTime = datetime.now()
    salute_time = ""
    if currentTime.hour < 12:
        salute_time = " ,buen día!"
    elif 12 <= currentTime.hour < 18:
        salute_time = " ,buenas tardes!"
    else:
        salute_time = " ,buenas noches!"
    msg = 'Hola {0.author.mention}'.format(context.message)
    msg = msg + salute_time
    await client.send_message(context.message.channel, msg)

@client.command(name='Ayuda',
                description="Ayuda del bot definitivo",
                brief="ayuda",
                aliases=['ayuda'],
                pass_context=True)
async def ayuda(context):
    msg = 'Hola {0.author.mention} estos son mis comandos : \n \
    +ayuda: Imprime este mensage \n \
    +rol: auto-otorga roles a la gente que esta en el clan Escusara 2,3,4,5 , ejemplo: +rol CNorris#2234 \n'.format(context.message)
    #+oraculo: Pregunta con respuesta si o no al oraculo de la Ciudad Onirica, ejemplo: +oraculo Es Escuadra 2 la mejor? \n \
    await client.send_message(context.message.channel, msg )


#######################################################################
################## SPECIAL PERMISIONS COMMANDS  #######################
#######################################################################
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


@client.command(name='Inactivos',
                description="Expone el listado de inactivos en discord",
                brief="inactivos",
                aliases=['inactivos','inac'],
                pass_context=True)
async def inactivos(context):
    my_server = discord.utils.get(client.servers)
    user_id = context.message.author.id
    user=my_server.get_member(user_id)
    for i in my_server.roles:
        if "Admin" in i.name:
                    admin_id=i.id
    if admin_id in [role.id for role in user.roles]:
        await client.send_message(context.message.channel,"Fecha de ultima modificacion: %s" % time.ctime(os.path.getmtime("inactive_list.txt")))
        await client.send_message(context.message.channel, "Inactivos:")
        #inactive_list = []
        with open('inactive_list.txt', 'r') as f:
            for member in f:
                #print(member)
                #inactive_list.append(member)
                await client.send_message(context.message.channel, member)
        #await client.send_message(context.message.channel, inactive_list)
        await client.send_message(context.message.channel, "Fin.")
    else:
        await client.send_message(context.message.channel, "No tenes permisos para ejecutar este comando")

#######################################################################
#######################################################################
#######################################################################

async def populate_user_data(users):
    with open('users.json', 'r') as f:
        users = json.load(f)
        my_server = discord.utils.get(client.servers)
        for memb in my_server.members:
            if not memb.bot and not memb.id in users:
                #print(memb.name+" is not in users.json ... adding ...")
                users[memb.id] = [memb.name, memb.nick]
    with open('users.json', 'w') as f:
            json.dump(users,f,indent=4)


async def add_user_data(member):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if not member.bot and not member.id in users:
            print(member.id+" is not in users.json ... adding ...")
            #print(dir(member))
            my_server = discord.utils.get(client.servers)
            user=my_server.get_member(member.id)
            users[member.id] = [member.name, user.nick]
    with open('users.json', 'w') as f:
            json.dump(users,f,indent=4)


async def add_clanmate_to_clan(clanmate_battletag, his_clan_name):
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        name = clanmate_battletag.split('#')[0]
        if not clanmate_battletag in clan:
            print("From "+ his_clan_name + " " + clanmate_battletag+" battletag is not in clan.json ... adding ...")
            clan[clanmate_battletag] = [his_clan_name, name]
        #if not str(name[0]) in clan:
        #    print(str(name[0])+" name is not in clan.json ... ")
        #    #Do something
    with open('clan.json', 'w') as f:
            json.dump(clan,f,indent=4)


def is_user_in_users(user):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if user.id in users:
            return True
        else:
            return False

def is_clanmate_in_clan(clanmate_battletag):
    #Patch for those who have no battleTag
    #name = clanmate_battletag.split('#')[0]
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        #if clanmate_battletag in clan or name[0] in clan:
        if clanmate_battletag in clan:
            return True
        else:
            return False


def is_special_clanmate_in_clan(clanmate_name):
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        if clanmate_name in clan:
            return True
        else:
            return False


async def does_user_have_role(member,rol_id):
    for role in member.roles:
        #print(str(role.id))
        if rol_id == role.id:
            #print(member.name+" tiene rol " + rol_id + "!")
            return True
    return False
    #if rol_id in [member.id for role in member.roles]:
    #    print(member+" tiene rol " + rol_id + "!")

async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    #print("Entered on message!")
    msg = message.content
    #Normalizo el mensaje
    text = unicodedata.normalize('NFKD', msg).encode('ASCII', 'ignore').decode()
    #print(text)
    regex_hola = re.search('^.*H+O+L+A+\s*.*$', text.upper(), re.MULTILINE) 
    regex_caca = re.search('^C+A+C+A+$', text.upper(), re.MULTILINE)
    regex_chau = re.search('^.*C+H+A+U+$', text.upper(), re.MULTILINE)
    regex_buen_dia = re.search('^.*B+U+E+N+\sD+I+A+\s.*$', text.upper(), re.MULTILINE)
    regex_buenos_dias = re.search('^.*B+U+E+N+O+S+\sD+I+A+S.*$', text.upper(), re.MULTILINE)
    regex_buenas_tardes = re.search('^.*B+U+E+N+A+S+\sT+A+R+D+E+S+$', text.upper(), re.MULTILINE)
    regex_buenas_noches = re.search('^.*B+U+E+N+A+S+\sN+O+C+H+E+S+$', text.upper(), re.MULTILINE)
    regex_buenas = re.search('^B+U+E+N+A+S+$', text.upper(), re.MULTILINE)
    #print("Regex hola = "+str(regex_hola))
    if regex_hola or regex_buenas:
        currentTime = datetime.now()
        salute_time = ""
        if currentTime.hour < 12:
            salute_time = " ,buen día!"
        elif 12 <= currentTime.hour < 18:
            salute_time = " ,buenas tardes!"
        else:
            salute_time = " ,buenas noches!"
        msg = 'Hola {0.author.mention}'.format(message)
        msg = msg + salute_time
        embed = discord.Embed(title="" , description=msg+" :wave:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)
    
    if regex_buen_dia:
        embed = discord.Embed(title="" , description="Buen Dia para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if regex_buenos_dias:
        embed = discord.Embed(title="" , description="Buenos Dias para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if regex_buenas_tardes:
        embed = discord.Embed(title="" , description="Buenas tardes para vos"+message.author.mention+" :wave:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if regex_buenas_noches:
            embed = discord.Embed(title="" , description="Buenas noches para vos"+message.author.mention+" :full_moon_with_face: :coffee: ", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)

    if (regex_caca) or ("mierda".upper() in text.upper()):
        #embed = discord.Embed(title="", description=":poop:", color=0x00ff00)
        embed = discord.Embed()
        #response = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q=poop&api_key=NONE&limit=25").read())
        #embed_list = [d['images']['fixed_width']['url'] for d in response['data']]
        #url = random.choice(embed_list)
        #print(url)
        url="https://media.giphy.com/media/tdnUaMuARmi0o/giphy.gif"
        embed.set_image(url=url)
        await client.send_message(message.channel, embed=embed)

    if "DANCE" in text.upper():
        embed = discord.Embed()
        random_dance=[
        "https://media.giphy.com/media/143OU9tGwdAEb6/giphy.gif",
        "https://media.giphy.com/media/YZD7Z4uZlJQe4/giphy.gif",
        "https://media.giphy.com/media/zWnlBLTbv9QaY/giphy.gif",
        "https://media.giphy.com/media/3oroUrSVloine9dmmA/giphy.gif"
        ]
        url = random.choice(random_dance)
        embed.set_image(url=url)
        await client.send_message(message.channel, embed=embed)

    if "PUTO" in text.upper():
        embed = discord.Embed(title="" , description="Puto el que lee ... :punch:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if "PENE" in text.upper() or "CHOTA" in text.upper() or "PIJA" in text.upper():
        embed = discord.Embed(title="" , description=":eggplant:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    #if message.content.startswith('chau'.upper()) or message.content.startswith('adios'):
    #    await client.send_message(message.channel, "Nos vemos en Disney")
    
    if (regex_chau) or ("ADIOS" in text.upper()):
        respuestas_posibles = ["Nos vemos en Disney ", "Hasta prontito ", "Nos re vimos ", "Cuidate, querete, ojito ... ","Hasta la próxima amig@ ", "Chau "]
        await client.send_message(message.channel, random.choice(respuestas_posibles) + message.author.mention )
        
    await client.process_commands(message)


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

client.loop.create_task(list_servers())
client.run(BOT_TOKEN)