# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
import aiohttp
from discord.ext.commands import Bot
from discord.voice_client import VoiceClient
from fail_safe import FailSafe
import os, time
import discord
import re
import json
import pymongo
from datetime import datetime
from boto.s3.connection import S3Connection
import unicodedata
from urllib.request import urlopen
from pymongo import MongoClient
from datetime import timedelta 
from datetime import date 
from db import *
from utils import *
import tweepy
import youtube_dl


#4 Heroku
BUNGIE_API_KEY = os.environ['BUNGIE_API_KEY']
BOT_TOKEN = os.environ['BOT_TOKEN']


BOT_PREFIX = ("+") #("+", "!")
client = Bot(command_prefix=BOT_PREFIX)

players = {}
my_queues = {}

@client.event
async def on_member_join(member):  
    server = member.server
    for i in server.channels:
        if "ʙɪᴇɴᴠᴇɴɪᴅᴏ".upper() in i.name.upper() :
            #print(i.name)
            canal_bienvenida = i            
    #fmt = 'Bienvenido {0.mention} a {1.name}!'
    fmt = ':wave: **Bienvenido {0.mention} al Discord de ESCUADRA 2!**'
    await client.send_message(canal_bienvenida, fmt.format(member))
    #await client.send_message(canal_bienvenida, fmt.format(member, server))
    embed2=discord.Embed()
    embed2=discord.Embed(title="", description="• Necesitas permisos para usar los canales de Destiny 2? \n • Escribí debajo el comando **+rol** seguido de tu Battletag! \n **Ejemplo: **\n", color=0x00ff00)
    embed2.set_image(url="https://media.giphy.com/media/vykWBW2wh4URJZ75Uu/giphy.gif")
    await client.send_message(canal_bienvenida, embed=embed2)
    await asyncio.sleep(0.01)


@client.command(name='Rol',
                description="Autoprovisioning de Roles Clan y DJ",
                brief="Autoprovisioning Escuadra X",
                aliases=['rol'],
                pass_context=True)
async def rol(context):
    #print("Entered command ROL!")
    valid_battle_tag_ending = bool(re.match('^.*#[0-9]{4,5}$', context.message.content))
    if len(context.message.content)>=4 and valid_battle_tag_ending:
        #4 Tests
        #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
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
                if i.id == str(544911570258624522):
                    custom_clan_role_id=i.id
                if i.id == str(387742983249985536):
                    custom_destiny_clan_role_id = i.id
                if "DJ" in i.name:
                    custom_dj_role_id=i.id

            role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
            role_DJ = discord.utils.get(my_server.roles, id=custom_dj_role_id)
            role_Destiny_Clan = discord.utils.get(my_server.roles, id=custom_destiny_clan_role_id)

            #4 tests
            #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
            #4 Heroku
            MONGODB_URI = os.environ['MONGO_DB_MLAB']
            #END Heroku
            cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
            db = cursor.get_database("bot_definitivo")

            clanmates = db.clan_members
            discord_users = db.discord_users
            
            if is_discord_id_in_db(context.message.author.id, discord_users) and is_clanmate_in_db(real_battletag, clanmates):
                #User is in users.json AND clanmate in clan.json
                print(str(context.message.author.name) +" with BT = "+ str(real_battletag) +" in clan and in users !")
                name = real_battletag.split('#')[0]
                #Verification if discord api does not work initialy
                user_has_role_clan = await does_user_have_role(user,custom_clan_role_id)
                user_has_role_dj = await does_user_have_role(user,custom_dj_role_id)
                user_has_role_destiny_clan = await does_user_have_role(user,custom_destiny_clan_role_id)
                
                if not user_has_role_clan or not user_has_role_dj:
                    print(str(name)+" missing role ... adding ... ")
                    addroles = [role_Clan, role_DJ, role_Destiny_Clan]
                    await client.add_roles(user, *addroles)
                
                embed = discord.Embed(title="" , description="El Guardian "+str(name)+" ya fue dado de alta y tiene los roles! ", color=0x00ff00)
                await client.send_message(context.message.channel, embed=embed)
                await client.send_message(user, embed=embed)
            else:
                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                #if user_destiny_id and user_clan_name:
                if user_clan_name:
                    if "Escuadra" in user_clan_name:
                        addroles = [role_Clan, role_DJ, role_Destiny_Clan]
                        print(addroles)
                        await client.add_roles(user, *addroles)
                        if not is_discord_id_in_db(context.message.author.id, discord_users):
                            print(real_battletag + " is not in discord_users_DB!!")
                            my_dict = {}
                            my_dict = {"discord_id":user.id, "name":user.name, "nick":user.nick, "last_activity":""}
                            await push_discord_user_db(my_dict, discord_users)
                        else:
                            print(context.message.author.name + " is in users.json!!")
                            pass
                        if not is_clanmate_in_db(real_battletag, clanmates):
                            print(real_battletag + " is not in clan_DB!!")
                            name = real_battletag.split('#')[0]
                            my_dict = {}
                            my_dict = {"battletag":real_battletag, "clan":user_clan_name, "nick":name}
                            await push_clanmate_to_db(my_dict, clanmates)
                        else:
                            print(real_battletag + " is in clan.json!!")
                            pass
                        clan_alias=user_clan_name[0]+user_clan_name[-1]
                        
                        
                        embed = discord.Embed(title="" , description=":white_check_mark: **Listo** "+context.message.author.mention+" \n• Ya podes usar todos los canales!", color=0x00ff00)
                        await client.send_message(context.message.channel, embed=embed)
                        await client.send_message(user, embed=embed)

                        embed2 = discord.Embed(title="" , description="**Aprovechamos para comentarte que en nuestro discord tenemos 2 bots con varias utilidades.**\n \
                        \n\
                        • __**FailSafe:**__\n\
                        \t\tBrinda stadisticas y informacion detallada de Destiny 2. Es necesario una registracíon, para eso escribí en el canal #BOTs: \n \
                        \n\
                        \t\t`!register`\n \
                        \n\
                        \t\tLuego con `!help` podes ver el listado de comandos disponibles.\n\
                        \n\
                        • __**Bot Definitivo:**__\n\
                        \t\tEntrega información sobre las actividades semanales tipicas, escribí en el canal #🎮ᴅᴇsᴛɪɴʏ:\n\
                        \n\
                        \t\t`+semana`\n ", color=0x00ff00)
                        await client.send_message(user, embed=embed2)
                        #print(type(client.id))
                        #print(client.id)
                        #print(type(context.message.author.id))
                        #print(context.message.author)
                        
                        member=my_server.get_member(context.message.author.id)
                        await client.change_nickname(member, str(real_battletag)+" ["+clan_alias+"]")
                    else:
                        embed = discord.Embed(title="" , description=":warning: "+context.message.author.mention+" **Parece que no estas en nuestro clan** \n• Unite y volve a intentarlo!", color=0x00ff00)
                        await client.send_message(context.message.channel, embed=embed)
                else:
                    print("User clan name = "+str(user_clan_name) + "  and  "+ str(user_battletag))
                    embed = discord.Embed(title="" , description=":warning: "+context.message.author.mention+" **Parece que no estas en ningún clan** \n• Unite y volve a intentarlo!", color=0x00ff00)
                    await client.send_message(context.message.channel, embed=embed)
        else:
            print("User Destiny = "+str(user_destiny) + "  and  "+ str(user_battletag))
            embed = discord.Embed(title="" , description=":x: **Battletag invalido / Error al conectar con Bungie.net** \n• Tenes que introducir tu Battletag de Blizzard \n• Si el error sigue persistiendo comuniquese con un admin por favor", color=0x00ff00)
            await client.send_message(context.message.channel, embed=embed)
    else:
        embed2=discord.Embed()
        embed2 = discord.Embed(title="" , description=":warning: **Error!** \n • Tenes que introducir tu Battletag de Blizzard \n• Intentalo de nuevo", color=0x00ff00)
        embed2.set_image(url="https://media.giphy.com/media/vykWBW2wh4URJZ75Uu/giphy.gif")
        await client.send_message(context.message.channel, embed=embed2)
    #delets the message
    #await client.delete_message(context.message)
    await asyncio.sleep(0.01)


@client.command(name='RES',
                description="Responde por PJ si hizo raid esta semana",
                brief="Raid esta semana",
                aliases=['res'],
                pass_context=True)
async def raid_this_week(context):
    valid_battle_tag_ending = bool(re.match('^.*#[0-9]{4,5}$', context.message.content))
    if len(context.message.content)>=4 and valid_battle_tag_ending:
        #4 Tests
        #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
        #4 Heroku
        fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
        #END Heroku
        user_battletag = context.message.content.split(' ', 1)[1]   #separate +rol from message
        user_destiny = fs.get_playerByTagName(fs.format_PlayerBattleTag(user_battletag)) #Search for player battletag NOT Case Sensitive
        if user_destiny:
            #print("Valid User Destiny= "+str(user_destiny))
            user_destiny_id = user_destiny[0]['membershipId'] #From response extract the ID
            real_battletag = user_destiny[0]['displayName']
            #print(user_destiny_id)
            #print(real_battletag)
            profile = fs.get_DestinyUserProfileDetail(user_destiny_id)
            #print(type(profile))
            #print(profile)
            #print(profile['characters']['data'])
            characters = profile['characters']['data']
            for id, info in characters.items():
                #print(key)
                #print(value)
                #print(value['classHash'])
                if info['classHash']==3655393761:
                    print(real_battletag + " has a TITAN !")
                    character_id = info['characterId']
                    raids = fs.get_CharactersRaids(user_destiny_id,character_id)
                    print(type(raids))
                    for key, value in raids.items():
                        print(key)
                        print(value[0])
                        print(value[1])
                    
                elif value['classHash']==2271682572:
                    print(real_battletag + " has a Warlock!")
                    character_id = value['characterId']
                else:
                    print(real_battletag + " has a Hunter!")
                    character_id = value['characterId']


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    await update_discord_user_last_activity(message.author.id)

    #if (client.user.mentioned_in(message)) and not (message.author.mentioned_in(message)):
    #    await client.send_message(message.channel, "Estoy arriba KPO, que necesitas !?")
    
    msg = message.content
    #Normalizo el mensaje
    text = unicodedata.normalize('NFKD', msg).encode('ASCII', 'ignore').decode()
    regex_hola = re.search('^.*H+O+L+A+\s*.*$', text.upper(), re.MULTILINE) 
    regex_chau = re.search('^.*C+H+A+U+$', text.upper(), re.MULTILINE)
    regex_buen_dia = re.search('^.*B+U+E+N+\s+D+I+A+.*$', text.upper(), re.MULTILINE)
    regex_buenos_dias = re.search('^.*B+U+E+N+O+S+\sD+I+A+S.*$', text.upper(), re.MULTILINE)
    regex_buenas_tardes = re.search('^.*B+U+E+N+A+S+\sT+A+R+D+E+S+.*$', text.upper(), re.MULTILINE)
    regex_buenas_noches = re.search('^.*B+U+E+N+A+S+\sN+O+C+H+E+S+.*$', text.upper(), re.MULTILINE)
    regex_buenas = re.search('^B+U+E+N+A+S+$', text.upper(), re.MULTILINE)
    regex_gracias_bot = re.search('^G+R+A+C+I+A+S\s+B+O+T+$', text.upper(), re.MULTILINE)
    if (regex_hola or regex_buenas):
        if read_param_from_aux("number_of_hellos") >=2:
            currentTime = datetime.now()
            salute_time = ""
            if currentTime.hour < 12+3:# Agrego diferencia de horario con el server US de Heroku
                salute_time = " ,buen día!"
            elif 12+3 <= currentTime.hour < 18+3:# Agrego diferencia de horario con el server US de Heroku
                salute_time = " ,buenas tardes!"
            else:
                salute_time = " ,buenas noches!"
            msg = 'Hola {0.author.mention}'.format(message)
            msg = msg + salute_time
            embed = discord.Embed(title="" , description=msg+" :wave:", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)
            reset_param_aux("number_of_hellos")
        else:
            increment_param_in_1_aux("number_of_hellos")
        
        
    if regex_buen_dia and not regex_hola:
        if read_param_from_aux("number_of_good_mornings") >=2:
            embed = discord.Embed(title="" , description="Buen Dia para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)
            reset_param_aux("number_of_good_mornings")
        else:
            increment_param_in_1_aux("number_of_good_mornings")

    if regex_buenos_dias and not regex_hola:
        if read_param_from_aux("number_of_good_mornings") >=2:
            embed = discord.Embed(title="" , description="Buenos Dias para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)
            reset_param_aux("number_of_good_mornings")
        else:
            increment_param_in_1_aux("number_of_good_mornings")


    if regex_buenas_tardes and not regex_hola:
        #if read_param_from_aux("number_of_good_evenings") >=2:
            embed = discord.Embed(title="" , description="Buenas tardes para vos"+message.author.mention+" :wave:", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)
        #    reset_param_aux("number_of_good_evenings")
        #else:
        #    increment_param_in_1_aux("number_of_good_evenings")

    if regex_buenas_noches and not regex_hola :
        #if read_param_from_aux("number_of_good_nights") >=2:
            embed = discord.Embed(title="" , description="Buenas noches para vos"+message.author.mention+" :full_moon_with_face: :coffee: ", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)
        #    reset_param_aux("number_of_good_nights")
        #else:
        #    increment_param_in_1_aux("number_of_good_nights")
      
    if "PUTO" in text.upper():
        embed = discord.Embed(title="" , description="Puto el que lee ... :punch:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if (regex_chau) or ("ADIOS" in text.upper()):
        respuestas_posibles = ["Nos vemos en Disney ", "Hasta prontito ", "Nos re vimos ", "Cuidate, querete, ojito ... ","Hasta la próxima amig@ ", "Chau "]
        await client.send_message(message.channel, random.choice(respuestas_posibles) + message.author.mention )
    
    if regex_gracias_bot:
        embed = discord.Embed(title="" , description="De nada"+message.author.mention+" ! :vulcan:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    await asyncio.sleep(0.01)
    await client.process_commands(message)
    

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.command(name='Ayuda',
                description="Ayuda del bot definitivo",
                brief="ayuda",
                aliases=['ayuda'],
                pass_context=True)
async def ayuda(context):
    msg = 'Hola {0.author.mention} estos son mis comandos : \n \
    `+ayuda` Imprime este mensage \n \
    `+pro` (Calendario Armas Protocolo)\n\
    `+asc` (Calendario Desafío Ascendente)\n\
    `+rol` auto-otorga roles a la gente que esta en el clan Escusara 2,3,4,5 , ejemplo: +rol CNorris#2234\n\
    ´+semana´ informa actividades tipica de esa semana'.format(context.message)
    await client.send_message(context.message.channel, msg )


#######################################################################
################## SPECIAL PERMISIONS COMMANDS  #######################
#######################################################################

@client.command(name='Run blacklist and populate clan',
                description="Genera la lista negra y actualiza la db del clan",
                brief="run",
                aliases=['sync'],
                pass_context=True)
async def run_sync(context):
    my_server = discord.utils.get(client.servers)
    user_id = context.message.author.id
    user=my_server.get_member(user_id)
    for i in my_server.roles:
        if "Admin" in i.name:
                    admin_id=i.id
    if admin_id in [role.id for role in user.roles]:
        #4 tests
        #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))      #Start Fail_Safe 4tests
        #4 Heroku
        fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
        #END Heroku
        t_start = time.perf_counter()
        await client.send_message(context.message.channel, "**Aguantame la mecha :bomb: ... que estoy creando el listado de inactivos y pisando el listado de clan. **")
        await fs.async_clear_clanmates_blacklister_db()
        for clan in fs.our_clans:
            blacklist_EX = []
            #clan_list = await fs.async_get_ClanPlayerList(fs.our_clans[0])
            clan_list = await fs.async_get_ClanPlayerList(clan)
            if not clan_list:
                print("Could not load CLAN LIST!!!!!")
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_LastPlayed(clan_list)
            print("Got last Played for" + str(clan))
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_Battletag(new_clan_list)
            print("Got Battletags for" + str(clan))
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_ClanName(new_clan_list)
            print("Got ClanNames for" + str(clan))
            await asyncio.sleep(0.5)
            
            for clanmate in new_clan_list:
                blacklisted = await fs.async_is_blacklisted(clanmate)
                if blacklisted:
                    blacklist_EX.append(blacklisted)
            print("Got Blacklisters for" + str(clan))
            await asyncio.sleep(0.5)
            definitive_blacklist = await fs.async_filter_blacklist(blacklist_EX)
            if definitive_blacklist:
                await asyncio.sleep(0.5)
                await fs.async_push_blacklist(definitive_blacklist)
            await asyncio.sleep(0.5)
            print("Filtered Blacklisters for" + str(clan))
            for i in new_clan_list:
                del i['last_played']
            await fs.async_push_clanmates_to_db(new_clan_list)
            print("Pushed ClanMates for" + str(clan))
            await asyncio.sleep(0.5)
            await client.send_message(context.message.channel, "**Termine con %s**" % clan[1])
            
        t_stop = time.perf_counter()
        #print("Elapsed time: %.1f [min]" % ((t_stop-t_start)/60))
        await client.send_message(context.message.channel, "**Finalizada la generacion de Inactivos y listado de clan, tardé ... %.1f [min]!**"% ((t_stop-t_start)/60))
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.01)


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
        #4 tests
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = cursor.get_database("bot_definitivo")
        discord_users = db.discord_users
        discord_users.remove({})
        await client.send_message(context.message.channel, "Populación Discord:")
        await client.send_message(context.message.channel, "Total Usuarios: " + str(my_server.member_count))
        bot_num=0
        member_list = []
        for memb in my_server.members:
                if memb.bot:
                    bot_num = bot_num+1
                else:
                    my_dict = {}
                    my_dict = {"discord_id":memb.id, "name":memb.name, "nick":memb.nick, "last_activity":""}
                    member_list.append(my_dict)
        await async_add_discord_users_list(member_list)
        await client.send_message(context.message.channel, "Guardianes = "+str(my_server.member_count-bot_num) + "\n" + "Bots = "+str(bot_num))
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.01)


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
        #4 tests
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #4 Heroku
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        
        cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = cursor.get_database("bot_definitivo")
        blacklisters = db.blacklist
        
        date_blacklist_generated = await get_blacklist_date(blacklisters)
        await client.send_message(context.message.channel,":calendar: **Fecha de ultima modificacion: **"+date_blacklist_generated)
        blacklisters_list = await get_blacklist(blacklisters)
        
        my_dict = {}
        for record in blacklisters_list:
            #await client.send_message(context.message.channel,record["displayName"]+" \t"+ record["clan"]+" \t"+ record["inactive_time"])    
            if record["clan"] in my_dict:
                my_dict[record["clan"]] += record["displayName"]+" ─ "+ record["inactive_time"] +"\n"
            else:
                my_dict[record["clan"]] = record["displayName"]+" ─ "+ record["inactive_time"] +"\n"
                
        for key, value in my_dict.items():
            embed = discord.Embed(
                title = "Inactivos "+str(key),
                description=value,
                color=0x00ff00
            )
            #embed.set_footer(text='Tis is a footer!')
            #embed.set_image(url=client.user.avatar_url.replace("webp?size=1024","png"))
            embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png"))     
            #embed.set_author(name=client.user.name)#,icon_url=client.user.avatar_url.replace("webp?size=1024","png"))
            #embed.add_field(name='Field Name', value='Field Value', inline=False)
            #embed.add_field(name='Field Name', value='Field Value', inline=True)
            #embed.add_field(name='Field Name', value='Field Value', inline=True)
            #await client.say(embed=embed)
            await client.send_message(context.message.channel, embed=embed)
        await asyncio.sleep(0.2)       
        await client.send_message(context.message.channel, "Fin.")
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.05)


#######################################################################
#######################################################################
#######################################################################

@client.command(name='Informe Semanal',
                description="Informe Semanal",
                brief="Informe Semanal",
                aliases=['semana'],
                pass_context=True)
async def informe_semanal(context):
    ascendant_dict={
        2: ["ᴀʟᴛᴀʀ ᴀʙᴀɴᴅᴏɴᴀᴅᴏ - ᴊᴀʀᴅɪɴᴇs ᴅᴇ ᴇsɪʟᴀ","https://cdn.discordapp.com/attachments/508999396835196950/520280444277751828/Jardines_de_Esila.png"],
        3: ["ʀᴜɪɴᴀs ǫᴜᴇsʙʀᴀᴊᴀᴅᴀs – ᴇsᴘɪɴᴀ ᴅᴇ ᴋᴇʀᴇs","https://cdn.discordapp.com/attachments/508999396835196950/520280396366086154/Espina_de_Keres.png"],
        4: ["ғᴏʀᴛᴀʟᴇᴢᴀ ᴅᴇ ғɪʟᴏs ᴄᴏʀᴛᴀɴᴛᴇs - ʀᴇᴛɪʀᴏ ᴅᴇʟ ʜᴇʀᴀʟᴅᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280494722514964/Reclusion_del_Heraldo.png"],
        5: ["ᴀʙɪsᴍᴏ ᴀɢᴏɴᴀʀᴄʜ – ʙᴀʜɪᴀ ᴅᴇ ʟᴏs ᴅᴇsᴇᴏs ᴀʜᴏɢᴀᴅᴏs","https://cdn.discordapp.com/attachments/508999396835196950/520280295413514253/Bahia_de_los_Deseos_Ahogados.png"],
        6: ["ɢᴜᴀʀɴɪᴄɪᴏɴ ᴄɪᴍᴇʀᴀ - ᴄᴀᴍᴀʀᴀ ᴅᴇ ʟᴜᴢ ᴅᴇ ᴇsᴛʀᴇʟʟᴀs","https://cdn.discordapp.com/attachments/508999396835196950/520280358630064149/Camara_de_Luz_Estelar.png"],
        0: ["ᴏᴜʀᴏʙᴏʀᴇᴀ – ʀᴇᴘᴏsᴏ ᴅᴇʟ ᴀғᴇʟɪᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280560724344862/Reposo_de_Afelio.png"],
        1: ["ᴀʟᴛᴀʀ ᴀʙᴀɴᴅᴏɴᴀᴅᴏ - ᴊᴀʀᴅɪɴᴇs ᴅᴇ ᴇsɪʟᴀ","https://cdn.discordapp.com/attachments/508999396835196950/520280444277751828/Jardines_de_Esila.png"]
    }

    protocol_dict={
        3: ["IKELOS_SMG_v1.0.1 (Subfusil)","https://cdn.discordapp.com/attachments/508999396835196950/520269508728979467/Subfusil.png"],
        4: ["IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520269665478508544/Francotirador.png"],
        0: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png"],
        1: ["IKELOS_SG_v1.0.1 (Escopeta),\n IKELOS_SMG_v1.0.1 (Subfusil),\n IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png"],
        2: ["IKELOS_SG_v1.0.1 (Escopeta)","https://cdn.discordapp.com/attachments/508999396835196950/520269571253600271/Escopeta.png"]
    }
    curse_dict={
        0: ["Nivel de Maldicion 1"],
        1: ["Nivel de Maldicion 2"],
        2: ["Nivel de Maldicion 3, esta disponible el Trono Destrozado (Mazmorra)!"]
    }
    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]
    #print(key)

    if date.today().weekday() == 0: #and today.hour >= 14: # 0 is for monday
        #print("Today is Monday !")
        key = key - 1
        if key<0:
            key = 52
    #print(today)
    #print("Week Number: "+str(key))
        
    if date.today().weekday() == 1 and today.hour < 17:
        print("Tuesday Before RESET !! Adjusting week number!!")
        key = key - 1
        if key<0:
            key = 0
        #print("Week Number: "+str(key))
        #print(today.hour)
    #print("**************")
    #print("Next Week")
    #print((key+1)%7)
    #print(ascendant_dict[key%7][0])
    #print(protocol_dict[key%5][0])
    embed = discord.Embed(title="" , description=":calendar: Esta semana el Desafío Ascendente es en: \n **"+ascendant_dict[key%7][0]+"**", color=0x00ff00)
    embed.set_image(url=ascendant_dict[key%7][1])
    await client.send_message(context.message.channel, embed=embed)

    embed = discord.Embed(title="" , description="**"+curse_dict[key%3][0]+"**", color=0x00ff00)
    await client.send_message(context.message.channel, embed=embed)
    
    embed = discord.Embed(title="" , description= ":calendar: Esta semana en  Protocolo Intensificación: \n **"+protocol_dict[key%5][0]+"**", color=0x00ff00)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/508999396835196950/520269693479551004/Protocolo.png")
    embed.set_image(url=protocol_dict[key%5][1])
    await client.send_message(context.message.channel, embed=embed)


@client.command(name='Server Status',
                description="Server Status",
                brief="Server Status",
                aliases=['status'],
                pass_context=True)
async def server(context):
    #offline:https://media.giphy.com/media/ZGarmJwETJ0He/giphy.gif
    #online:   https://media.giphy.com/media/8EmeieJAGjvUI/giphy.gif
    #4 tests
    #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
    #4 Heroku
    MONGODB_URI = os.environ['MONGO_DB_MLAB']
    #END Heroku
    cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = cursor.get_database("bot_definitivo")
    server_status = db.server_status
    status = await get_server_status(server_status)
    embed2=discord.Embed()
    if status["online"]:
        embed2 = discord.Embed(title="" , description=":white_check_mark: **Servidores Destiny2 Online!**", color=0x00ff00)
        embed2.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
        embed2.set_image(url="https://media.giphy.com/media/8EmeieJAGjvUI/giphy.gif")
        await client.send_message(context.message.channel, embed=embed2)
    else:
        embed2 = discord.Embed(title="" , description=":warning: **Servidores Destiny2 Caidos!**", color=0x00ff00)
        embed2.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
        embed2.set_image(url="https://media.giphy.com/media/ZGarmJwETJ0He/giphy.gif")
        await client.send_message(context.message.channel, embed=embed2)


@client.command(name='Get Clans Capacity',
                description="Genera el listado de capacidad del clan",
                brief="capacidad",
                aliases=['cap','clan_cap'],
                pass_context=True)
async def clan_capacity(context):
    #4 tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))      #Start Fail_Safe 4tests
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    capacity = await fs.get_clan_capacity()
    for c in capacity:
        for key,val in c.items():
            await client.send_message(context.message.channel, str(key)+": "+str(val)+"/100" )



#######################################################################
################################# MUSIC ###############################
#######################################################################


@client.command(pass_context=True)
async def play(context,url):
    server = context.message.server
    if is_user_admin(context):
        channel = context.message.author.voice.voice_channel
        print(client.is_voice_connected(channel))
        
        await client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
        
        player = await voice_client.create_ytdl_player(url, after=lambda:check_queue(server.id, my_queues, players))
        players[server.id] = player
        player.start()
        #id = context.message.server.id
        #players[id].start()
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(pass_context=True)
async def pause(context):
    server = context.message.server
    if is_user_admin(context):
        id = context.message.server.id
        players[id].pause()
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(pass_context=True)
async def stop(context):
    server = context.message.server
    if is_user_admin(context):
        voice_client = client.voice_client_in(server)
        id = context.message.server.id
        await voice_client.disconnect()
        players[id].stop()
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    

@client.command(pass_context=True)
async def resume(context):
    server = context.message.server
    if is_user_admin(context):
        id = context.message.server.id
        players[id].resume()
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(pass_context=True)
async def queue(context,url):
    server = context.message.server
    if is_user_admin(context):
        voice_client = client.voice_client_in(server)
        if voice_client:
            player = await voice_client.create_ytdl_player(url, after=lambda:check_queue(server.id, my_queues, players))
            if server.id in my_queues:
                my_queues[server.id].append(player)
            else:
                my_queues[server.id] = [player]
            await client.say("Video encolado KPO !")


@client.command(pass_context=True)
async def skip(context,url):
    server = context.message.server
    if is_user_admin(context):
        voice_client = client.voice_client_in(server)
        if voice_client:
            if server.id in my_queues:
                print(players)
                print(my_queues[server.id])
                if len(my_queues)>1:
                    player = await voice_client.create_ytdl_player(url, after=check_queue(server.id, my_queues, players))
                    #players[id].stop()
                    #players[id].start()
                    await client.say("Salteando KPO !")
                else:
                    await client.say("Nada encolado KPO !")
            

#######################################################################
################################# TEST ################################
#######################################################################

@client.command(name='Test',
                description="Test",
                brief="Test",
                aliases=['test'],
                pass_context=True)
async def testing(context):
    my_server = discord.utils.get(client.servers)

    for i in my_server.roles:
        #print(type(i.name), type(i.id))
        if i.id == str(544911570258624522):
            custom_clan_role_id=i.id
        if i.id == str(387742983249985536):
            custom_destiny_clan_role_id = i.id
        #if "Clan" in i.name:
        #    if "Destiny" in i.name:
        #        custom_destiny_clan_role_id=i.id
        #    else:
        #        custom_clan_role_id=i.id
        #print(i.name, i.id)
        if "DJ" in i.name:
            custom_dj_role_id=i.id

    #custom_clan_role_id=str(544911570258624522)
    #custom_destiny_clan_role_id=str(387742983249985536)
    role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
    role_DJ = discord.utils.get(my_server.roles, id=custom_dj_role_id)
    role_Destiny_Clan = discord.utils.get(my_server.roles, id=custom_destiny_clan_role_id)
    #print("RED ALert !")
    #print(role_Clan,role_DJ,role_Destiny_Clan)

    for memb in my_server.members:
        if memb.bot:
            pass
        else:
            #print(memb.name)
            user_has_role_destiny_clan = await does_user_have_role(memb,custom_destiny_clan_role_id)
            #print(user_has_role_destiny_clan)
            if user_has_role_destiny_clan:
                print(str(memb.name)+" missing role ... adding ... ")
                addroles = [role_DJ]
                await client.add_roles(memb, *addroles)
            

#######################################################################
######################### LOOPS #######################################
#######################################################################


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


async def get_server_status_tweets():
    await client.wait_until_ready()
    while not client.is_closed:
        for i in client.get_all_channels():
            print(i.name, i.id)
            if "ᴀᴠɪsᴏs".upper() in i.name.upper():
                #print(i.name)
                canal_avisos = i
        auth=tweepy.OAuthHandler(os.environ['TWITTER_API_KEY'],os.environ['TWITTER_API_SECRET'])
        auth.set_access_token(os.environ['TWITTER_ACCESS_TOKEN'],os.environ['TWITTER_ACCESS_SECRET'])
        api = tweepy.API(auth)
        #4 tests
        #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
        #4 Heroku   
        MONGODB_URI = os.environ['MONGO_DB_MLAB']
        #END Heroku
        
        cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
        db = cursor.get_database("bot_definitivo")
        server_status = db.server_status

        tweets = api.user_timeline("BungieHelp",page=1)
        status = await get_server_status(server_status)
        #db_date = datetime.strptime(status["last_maintenance"], '%Y-%m-%d %H:%M:%S')
        db_start=status["start_maintenance"]
        db_offline=status["offline_maintenance"]
        db_online=status["online_maintenance"]

        for tweet in tweets:
            if "MAINTENANCE".upper() in tweet.text.upper() :           
                if ("HAS BEGUN".upper() in tweet.text.upper() and "BACKEND".upper() not in tweet.text.upper()):
                    print("--------------------------------")
                    print("Entered begun maitenance")
                    print("Comparing dates: "+str(db_start)+" vs. "+str(tweet.created_at))
                    if db_start < tweet.created_at:
                        print(tweet.text)
                        #print(tweet.created_at)
                        print("New Start Maintenance DETECTED !!")
                        update = {
                            "start_maintenance": tweet.created_at
                        }
                        print("Updating record from "+str(db_start)+" to -> "+str(tweet.created_at))
                        await update_server_status(status, update, server_status)
                        embed2 = discord.Embed(title="" , description=":warning: **Comienzo de Mantenimiento de Destiny2!**", color=0x00ff00)
                        embed2.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
                        await client.send_message(canal_avisos, embed=embed2)
                
                if "being BROUGHT OFFLINE".upper() in tweet.text.upper():
                    print("--------------------------------")
                    print("Entered Server Offline !!")
                    print("being BROUGHT OFFLINE".upper() in tweet.text.upper())
                    #print(tweet.created_at)
                    print(tweet.text)
                    print("Comparing dates: "+str(db_offline)+" vs. "+str(tweet.created_at))
                    if db_offline < tweet.created_at:
                        #print(tweet.text)
                        #print(tweet.created_at)
                        print("New Offline Maintenance DETECTED !!")
                        update = {
                                "offline_maintenance": tweet.created_at
                            }
                        print("Updating record from "+str(db_offline)+" to -> "+str(tweet.created_at))
                        await update_server_status(status, update, server_status)
                        embed2 = discord.Embed(title="Servidores Offline" , description=":x: **Servidores de Destiny2 Offline!**", color=0x00ff00)
                        embed2.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
                        await client.send_message(canal_avisos, embed=embed2)
                        
                if ("HAS OFFICIALLY CONCLUDED".upper() in tweet.text.upper() or "IS COMPLETE".upper() in tweet.text.upper()):
                    print("--------------------------------")
                    print("Entered Maintenance FINISHED !!")
                    print("Comparing dates: "+str(db_online)+" vs. "+str(tweet.created_at))
                    print(tweet.text)
                    #print(tweet.created_at)
                    if db_online < tweet.created_at:
                        print(str(db_online)+"<"+str(tweet.created_at))
                        print("New Online Maintenance DETECTED !!")
                        #print(tweet.text)
                        #print(tweet.created_at)
                        update = {
                            "online_maintenance": tweet.created_at
                        }
                        print("Updating record from "+str(db_online)+" to -> "+str(tweet.created_at))
                        await update_server_status(status, update, server_status)
                        embed2 = discord.Embed(title="Servidores Online" , description=":white_check_mark: **Mantenimiento de Destiny2 Finalizado!**", color=0x00ff00)
                        embed2.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
                        await client.send_message(canal_avisos, embed=embed2)
        await asyncio.sleep(30)
     




#######################################################################
######################### MAIN ########################################
#######################################################################
#client.loop.create_task(list_servers())
#client.loop.create_task(get_server_status_tweets())
client.run(BOT_TOKEN)