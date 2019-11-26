# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
#import aiohttp
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
import math
from itertools import cycle


#4 Heroku
BUNGIE_API_KEY = os.environ['BUNGIE_API_KEY']
BOT_TOKEN = os.environ['BOT_TOKEN']


BOT_PREFIX = ("+") #("+", "!")
client = Bot(command_prefix=BOT_PREFIX)
status = ["Iron Banner", "Cometitive", "Strike", "Ordeal", "Story", "for glimmer", "for shards"]
client.remove_command('help')

players = {}
my_queues = {}
discord_admin_ids = {"javu":376055309657047040,"kernell":198516601497059328, "sonker":219539830055501825, "elenita":239122012767911936, "john":325898163518963712}

#######################################################################
################## EVENTS  ############################################
#######################################################################


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    #await(message.author.id)
    
    msg = message.content
    #Normalizo el mensaje
    text = unicodedata.normalize('NFKD', msg).encode('ASCII', 'ignore').decode()
    regex_hola = re.search('^.*H+O+L+A+\s*.*$', text.upper(), re.MULTILINE) 
    #regex_chau = re.search('^.*C+H+A+U+$', text.upper(), re.MULTILINE)
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
      
    #if "PUTO" in text.upper():
    #    embed = discord.Embed(title="" , description="Puto el que lee ... :punch:", color=0x00ff00)
    #    await client.send_message(message.channel, embed=embed)

    #if (regex_chau) or ("ADIOS" in text.upper()):
    #    respuestas_posibles = ["Nos vemos en Disney ", "Hasta prontito ", "Nos re vimos ", "Cuidate, querete, ojito ... ","Hasta la próxima amig@ ", "Chau "]
    #    await client.send_message(message.channel, random.choice(respuestas_posibles) + message.author.mention )
    
    if regex_gracias_bot:
        embed = discord.Embed(title="" , description="De nada"+message.author.mention+" ! :vulcan:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    await asyncio.sleep(0.01)
    await client.process_commands(message)


@client.event
async def on_member_join(member):  
    server = member.server
    for i in server.channels:
        if "ʙɪᴇɴᴠᴇɴɪᴅᴏ".upper() in i.name.upper() :
            #print(i.name)
            canal_bienvenida = i            
    #fmt = 'Bienvenido {0.mention} a {1.name}!'
    #fmt = ':wave: **Bienvenido {0.mention} al Discord de ESCUADRA 2!**'
    #await client.send_message(canal_bienvenida, fmt.format(member))
    #await client.send_message(canal_bienvenida, fmt.format(member, server))
    #embed2=discord.Embed(title="", description="• Necesitas permisos para usar los canales de Destiny 2? \n • Escribí debajo el comando **+rol** seguido de tu Battletag! \n **Ejemplo: **\n", color=0x00ff00)
    #embed2=discord.Embed(title="", description="• Necesitas permisos para usar los canales de Destiny 2 ó los de Division 2? \n • Escribí debajo el comando **+destiny** o **+division** respectivamente.", color=0x00ff00)
    #embed2.set_image(url="https://media.giphy.com/media/vykWBW2wh4URJZ75Uu/giphy.gif")
    #await client.send_message(canal_bienvenida, embed=embed2)
    for i in server.roles:
        #print(i.id,i.name)
        #if i.id == str(544911570258624522):
        #    custom_clan_role_id=i.id
        if "DJ" in i.name:
            custom_dj_role_id=i.id
    
    #role_Clan = discord.utils.get(server.roles, id=custom_clan_role_id)
    role_DJ = discord.utils.get(server.roles, id=custom_dj_role_id)
    addroles = [role_DJ]
    await client.add_roles(member, *addroles)
    await asyncio.sleep(0.01)


@client.event
async def on_reaction_add(reaction, user):
    pass
    #print("reactioned")
    #channel = reaction.message.channel
    #print(dir(reaction.emoji))
    #print(type(reaction.emoji))
    #print(reaction.emoji)
    #await client.send_message(channel,'{} agregó {} al mensaje: {}'.format(user.name, reaction.emoji, reaction.message.content))
    #if "prestigio" in channel.name:
    #    print(dir(reaction))


@client.event
async def on_member_remove(member):
    #print("Someone Left!!")
    server = member.server
    print("Bye Bye {0} !".format(member.name))
    #for i in server.roles:
        #print(i.id,i.name)
        #if i.id == str(544911570258624522):
        #    custom_clan_role_id=i.id
        #if i.id == str(387742983249985536):
        #    custom_destiny_clan_role_id = i.id
        #if i.id == str(544915941713248267):
            #custom_division_clan_role_id = i.id
        #if "DJ" in i.name:
            #custom_dj_role_id=i.id
    
    #role_Clan = discord.utils.get(server.roles, id=custom_clan_role_id)
    #role_DJ = discord.utils.get(server.roles, id=custom_dj_role_id)
    #role_Destiny_Clan = discord.utils.get(server.roles, id=custom_destiny_clan_role_id)
    #role_Division_Clan = discord.utils.get(server.roles, id=custom_division_clan_role_id)

    #remove_roles = [role_DJ]#, role_Destiny_Clan]#, role_Division_Clan]
    #await client.remove_roles(member, *remove_roles)
    await asyncio.sleep(0.01)
    #msg = "Bye Bye {0}".format(member.mention)
    #await client.send_message(serverchannel, msg)



#######################################################################
################## COMMON COMMANDS  ###################################
#######################################################################
"""
@client.command(name='Free Roles Destiny',
                description="Autoprovisioning de Roles Destiny y DJ",
                brief="Autoprovisioning roles Escuadra X",
                aliases=['destiny'],
                pass_context=True)
async def free_rol_destiny(context):
    my_server = discord.utils.get(client.servers)
    user_id = context.message.author.id
    user=my_server.get_member(user_id)
    user_roles_names=[]
    #Get users roles
    for i in user.roles:
        user_roles_names.append(i.name)
    #Get clan defined roles ids from discord
    for i in my_server.roles:
        print(i.id,i.name)
        #if i.id == str(544911570258624522):
        #    custom_clan_role_id=i.id
        if i.id == str(387742983249985536):
            custom_destiny_clan_role_id = i.id
        if "DJ" in i.name:
            custom_dj_role_id=i.id
    
    #role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
    role_DJ = discord.utils.get(my_server.roles, id=custom_dj_role_id)
    role_Destiny_Clan = discord.utils.get(my_server.roles, id=custom_destiny_clan_role_id)
    addroles = [role_DJ, role_Destiny_Clan]
    await client.add_roles(user, *addroles)
    embed = discord.Embed(title="" , description=":white_check_mark: **Listo** "+context.message.author.mention+" \n• Ya podes usar los canales de Destiny 2!", color=0x00ff00)
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
    \t\tEntrega información sobre las actividades semanales tipicas, escribí en el canal \n \
    #🎮ᴅᴇsᴛɪɴʏ o #💠ʙᴏᴛs:\n\
    \n\
    \t\t`+semana`\n\
    \n\
    \t\tEntrega raids completadas y con que personaje, escribí en el canal #🎮ᴅᴇsᴛɪɴʏ o #💠ʙᴏᴛs:\n \
    \n\
    \t\t`+raids BattleTagUsuario`\n\
     \n\
     \n\
    __Ejemplo:__\n\
    `+raids CNorris#4902`\n\
     \n", color=0x00ff00)
    await client.send_message(user, embed=embed2)
"""
"""
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
        await client.say("Verificando ... un momento por favor.")
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
                #if i.id == str(544911570258624522):
                #    custom_clan_role_id=i.id
                if i.id == str(387742983249985536):
                    custom_destiny_clan_role_id = i.id
                if "DJ" in i.name:
                    custom_dj_role_id=i.id

            #role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
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
                #user_has_role_clan = await does_user_have_role(user,custom_clan_role_id)
                user_has_role_dj = await does_user_have_role(user,custom_dj_role_id)
                user_has_role_destiny_clan = await does_user_have_role(user,custom_destiny_clan_role_id)
                
                #if not user_has_role_clan or not user_has_role_dj:
                if not user_has_role_dj:
                    print(str(name)+" missing role ... adding ... ")
                    addroles = [role_DJ, role_Destiny_Clan]
                    await client.add_roles(user, *addroles)
                
                embed = discord.Embed(title="" , description="El Guardian "+str(name)+" ya fue dado de alta y tiene los roles! ", color=0x00ff00)
                await client.send_message(context.message.channel, embed=embed)
                await client.send_message(user, embed=embed)
            else:
                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                #if user_destiny_id and user_clan_name:
                if user_clan_name:
                    if "Escuadra" in user_clan_name:
                        addroles = [role_DJ, role_Destiny_Clan]
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
                        \t\tEntrega información sobre las actividades semanales tipicas, escribí en el canal #🎮ᴅᴇsᴛɪɴʏ o #BOTS:\n\
                        \n\
                        \t\t`+semana`\n\
                        \t\tEntrega raids completadas y con que personaje, escribí en el canal #🎮ᴅᴇsᴛɪɴʏ o #BOTS:\n \
                        \n\
                        \t\t`+raids BattleTagUsuario`\n ", color=0x00ff00)
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
"""

@client.command(name='RES',
                description="Responde por PJ si hizo raid esta semana",
                brief="Raid esta semana",
                aliases=['raids'],
                pass_context=True)
async def raid_this_week(context):
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    if await fs.async_isBungieOnline():
        #valid_battle_tag_ending = bool(re.match('^.*#[0-9]{4,5}$', context.message.content))
        #if len(context.message.content)>=4 and valid_battle_tag_ending:
        if len(context.message.content)>=4:
            
            #print("Now:")
            #print(datetime.now())
            #user_battletag = context.message.content.split(' ', 1)[1]   #separate +rol from message
            user_steam_tag = context.message.content.split(' ',1)[1]
            #print("USER STEAM TAG:")
            #print("===============")
            #print(user_steam_tag)
            embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing por la migracion a Steam, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
            await client.send_message(user, embed=embed)
            embed = discord.Embed(title=":warning: Warning" , description="Este comando toma datos directamente de Bungie, que a veces tarda unos minutos en registrar las Raids recientes. Un momento por favor ...", color=0x00ff00)
            await client.send_message(user, embed=embed)
            #user_destiny = fs.get_playerByTagName(fs.format_PlayerBattleTag(user_battletag)) #Search for player battletag NOT Case Sensitive
            user_destiny = fs.get_playerBySteamTag(user_steam_tag) #Search for player Steam tag
            #print("User_destiny_length!!!")
            #print(len(user_destiny))
            if user_destiny:
                #print(type(user_destiny))
                #print(user_destiny)
                if len(user_destiny)==1:
                    user_destiny_id = user_destiny[0]['membershipId'] #From response extract the ID
                    #real_battletag = user_destiny[0]['displayName']
                    profile = fs.get_DestinyUserProfileDetail(user_destiny_id)
                    characters = profile['characters']['data']
                    #print("-------------------------")
                    #print(characters)
                    res = "\n"
                    for id, info in characters.items():
                        report = "**"+str(fs.guardian_class[info['classHash']])+" "+str(fs.guardian_race[info['raceHash']])+" "+str(fs.guardian_gender[info['genderHash']])+":** \n"
                        #print(str(fs.guardian_class[info['classHash']])+" "+str(fs.guardian_race[info['raceHash']])+" "+str(fs.guardian_gender[info['genderHash']]))
                        character_id = info['characterId']
                        raids = fs.get_CharactersRaids(user_destiny_id,character_id)
                        if raids:    
                            raids_complete = get_completed_raids(info,user_destiny_id,raids)
                            #print("/***************************************/")
                            #print(len(raids_complete))
                            #print("/***************************************/")
                            raids_complete_filtered = filter_completed_raids(raids_complete,fs)
                            #print("/***************************************/")
                            #print(raids_complete_filtered)
                            #print("/***************************************/")
                            definitive_complete_raids=get_unique_raids(raids_complete_filtered, fs)
                            #print(definitive_complete_raids)
                            #print("/***************************************/")
                            for key, value in definitive_complete_raids.items():
                                if value:
                                    report = report +" :white_check_mark: "+str(key) +"\n"
                                else:
                                    report = report +" :x: "+ str(key) +"\n"
                        else:
                            for key, value in fs.relevant_raids.items():
                                report = report + " :x: "+ value +"\n"
                            
                        res = res + report + "\n"
                    
                    embed = discord.Embed(title=":bell:__Tus Raids este reset:__", description=res, color=0x00ff00)
                    #embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/499231830235414529/587653954117173249/9k.png")
                    #await client.send_message(context.message.channel, embed=embed)
                    await client.send_message(user, embed=embed)
                else:
                    embed = discord.Embed(title="Error!", description="Tu SteamTag es muy generico hay multiples Guardianes con el mismo nombre, por favor actualizalo a algo mas especifico para usar el comando. \n\
                        Ejemplo: Javu --> Titan Javu", color=0x00ff00)
                    #await client.send_message(context.message.channel, embed=embed)
                    await client.send_message(user, embed=embed)
            else:
                embed = discord.Embed(title="Error!", description="No pude encontrar la info relacionada con tu SteamTag: Verifica y proba quitando iconos", color=0x00ff00)
                #await client.send_message(context.message.channel, embed=embed)
                await client.send_message(user, embed=embed)
    else:
        embed = discord.Embed(title=":x: Servidores de Destiny estan deshabilitados! Intenta mas tarde ...", description="¯\\_(ツ)_/¯", color=0x00ff00)
        await client.send_message(user, embed=embed)


@client.command(name='Ayuda',
                description="Ayuda del Bot definitivo",
                brief="ayuda",
                aliases=['ayuda', 'help'],
                pass_context=True)
async def ayuda(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    msg = 'Hola {0.author.mention} estos son mis comandos :\n\
    `+ayuda` Imprime este mensage.\n\
    `+semana` Reporte de todas las actividades del reset.\n\
    `+marte` Reporte de Armas Protocolo.\n\
    `+dc` Reporte de Desafio Ascendente en Dreaming City (Ciudad Ensoñada).\n\
    `+brote` Informe de rotación elemental semanal de Hora Zero.\n\
    `+luna` Información de rotación diaria del arma de Altar del Dolor y la rotación semanal de las Pesadillas Deambulantes.\n\
    `+calus` Dialogo random del Emperador Calus.\n\
    `+riven` Dialogo random de la Sirena de Riven.\n\
    `+lore` Elemento de lore de Destiny random.\n\
    `+xur` Informe de la ubicacion y inventario semanal de Xur.\n\
    `+raids` Reporte de las raids realizadas despues del reset semanal. Este es un comando que necesita de un dato adicional que es el SteamTag.\n\
    \t \t \t Ejemplo: `+raids Titan Javu`\n'.format(context.message)
    await client.send_message(user, msg)


@client.command(name='Informe Semanal',
                description="Informe Semanal",
                brief="Informe Semanal",
                aliases=['semana'],
                pass_context=True)
async def informe_semanal(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    ascendant_dict={
        4: ["ʀᴜɪɴᴀs ǫᴜᴇsʙʀᴀᴊᴀᴅᴀs – ᴇsᴘɪɴᴀ ᴅᴇ ᴋᴇʀᴇs","https://cdn.discordapp.com/attachments/508999396835196950/520280396366086154/Espina_de_Keres.png"],
        5: ["ғᴏʀᴛᴀʟᴇᴢᴀ ᴅᴇ ғɪʟᴏs ᴄᴏʀᴛᴀɴᴛᴇs - ʀᴇᴛɪʀᴏ ᴅᴇʟ ʜᴇʀᴀʟᴅᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280494722514964/Reclusion_del_Heraldo.png"],
        0: ["ᴀʙɪsᴍᴏ ᴀɢᴏɴᴀʀᴄʜ – ʙᴀʜɪᴀ ᴅᴇ ʟᴏs ᴅᴇsᴇᴏs ᴀʜᴏɢᴀᴅᴏs","https://cdn.discordapp.com/attachments/508999396835196950/520280295413514253/Bahia_de_los_Deseos_Ahogados.png"],
        1: ["ɢᴜᴀʀɴɪᴄɪᴏɴ ᴄɪᴍᴇʀᴀ - ᴄᴀᴍᴀʀᴀ ᴅᴇ ʟᴜᴢ ᴅᴇ ᴇsᴛʀᴇʟʟᴀs","https://cdn.discordapp.com/attachments/508999396835196950/520280358630064149/Camara_de_Luz_Estelar.png"],
        2: ["ᴏᴜʀᴏʙᴏʀᴇᴀ – ʀᴇᴘᴏsᴏ ᴅᴇʟ ᴀғᴇʟɪᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280560724344862/Reposo_de_Afelio.png"],
        3: ["ᴀʟᴛᴀʀ ᴀʙᴀɴᴅᴏɴᴀᴅᴏ - ᴊᴀʀᴅɪɴᴇs ᴅᴇ ᴇsɪʟᴀ","https://cdn.discordapp.com/attachments/508999396835196950/520280444277751828/Jardines_de_Esila.png"]
    }

    protocol_dict={
        3: ["IKELOS_SMG_v1.0.1 (Subfusil)","https://cdn.discordapp.com/attachments/508999396835196950/520269508728979467/Subfusil.png"],
        4: ["IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520269665478508544/Francotirador.png"],
        0: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png"],
        1: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png"],
        2: ["IKELOS_SG_v1.0.1 (Escopeta)","https://cdn.discordapp.com/attachments/508999396835196950/520269571253600271/Escopeta.png"]
    }

    HZ_dict={        
        1: ["Vacio","https://images-ext-2.discordapp.net/external/inJak0x078Kpn6K_f50f61zV_7_u92W92Nonkvcc2Rc/https/i.imgur.com/ikiCD58.png"],
        2: ["Arco","https://images-ext-2.discordapp.net/external/inJak0x078Kpn6K_f50f61zV_7_u92W92Nonkvcc2Rc/https/i.imgur.com/ikiCD58.png"],
        0: ["Solar","https://images-ext-2.discordapp.net/external/inJak0x078Kpn6K_f50f61zV_7_u92W92Nonkvcc2Rc/https/i.imgur.com/ikiCD58.png"]
    }

    lunar_nightmares_dict={
        0: ["Pesadilla de Xortal Sworn of Crota",""],
        2: ["Pesadilla de Jaxx Claw of Xivu Arath",""],
        1: ["Pesadilla de Hokris Fear of Mithrax",""],
        3: ["Fallen Council",""]
    }

    altar_dict={
        2: ["Escopeta","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/2f61559b7c57894703b6aaa52a44630c.jpg"],
        0: ["Sniper","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/b990412136d220fd641078418a4903fe.jpg"],
        1: ["Lanza_cohetes","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/eaf113dbb5cea03526009e6030b8c8ee.jpg"]
    }

    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]
    day_of_year = int(today.strftime("%j"))
    #print(key)

    if date.today().weekday() == 0: #and today.hour >= 14: # 0 is for monday
        #print("Today is Monday !")
        key = key - 1
        if key<0:
            key = 52
    #print(today)
    #print("Week Number: "+str(key))
        
    if date.today().weekday() == 1 and today.hour < 17:
        #print("Tuesday Before RESET !! Adjusting week number!!")
        key = key - 1
        if key<0:
            key = 0
        #print("Week Number: "+str(key))
        #print(today.hour)
    #print("**************")
    #print("Next Week")
    #print((key+1)%6)
    #print(ascendant_dict[key%6][0])
    #print(protocol_dict[key%5][0])
    embed = discord.Embed(title="" , description=":calendar: Esta semana el Desafío Ascendente es en: \n **"+ascendant_dict[key%6][0]+"**", color=0xff0000)
    embed.set_image(url=ascendant_dict[key%6][1])
    await client.send_message(user, embed=embed)
    
    embed = discord.Embed(title="" , description= ":calendar: Esta semana en  Protocolo Intensificación: \n **"+protocol_dict[key%5][0]+"**", color=0x00ff00)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/508999396835196950/520269693479551004/Protocolo.png")
    embed.set_image(url=protocol_dict[key%5][1])
    await client.send_message(user, embed=embed)

    embed = discord.Embed(title="**:earth_americas: Web App Secuencia Terminales Hora Cero**" , url="http://fiddle.jshell.net/pastuleo23/xu1snrc0/show", color=0xffd700)
    embed.set_thumbnail(url="https://www.bungie.net/common/destiny2_content/icons/f0def60d28b4f2a5a7fe8ec3d4764cfa.jpg")
    embed.set_image(url=HZ_dict[key%3][1])
    embed.add_field(name=':map: __Mapas de Sala de Horno__', value="Esta Semana Configuración "+"__**"+HZ_dict[key%3][0]+"**__"+":", inline=False)
    await client.send_message(user, embed=embed)

    embed = discord.Embed(title="" , description=":calendar: Esta semana la pesadilla deambulante es \n **"+lunar_nightmares_dict[key%4][0]+"**", color=0xff0000)
    #embed.set_image(url=ascendant_dict[key%6][1])
    await client.send_message(user, embed=embed)
    
    embed = discord.Embed(title="" , description="**Hoy el Altar del Dolor entrega,  "+altar_dict[day_of_year%3][0]+"**", color=0x000000)
    embed.set_image(url=altar_dict[day_of_year%3][1])
    await client.send_message(user, embed=embed)



@client.command(name='Informe Marte',
                description="Informe Marte",
                brief="Informe Marte",
                aliases=['marte'],
                pass_context=True)
async def informe_semanal(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    protocol_dict={
        3: ["IKELOS_SMG_v1.0.1 (Subfusil)","https://cdn.discordapp.com/attachments/508999396835196950/520269508728979467/Subfusil.png"],
        4: ["IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520269665478508544/Francotirador.png"],
        0: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png"],
        1: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png"],
        2: ["IKELOS_SG_v1.0.1 (Escopeta)","https://cdn.discordapp.com/attachments/508999396835196950/520269571253600271/Escopeta.png"]
    }
    
    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]
    #print(key)

    if date.today().weekday() == 0: #and today.hour >= 14: # 0 is for monday
        #print("Today is Monday !")
        key = key - 1
        if key<0:
            key = 52
            
    if date.today().weekday() == 1 and today.hour < 17:
        #print("Tuesday Before RESET !! Adjusting week number!!")
        key = key - 1
        if key<0:
            key = 0
     
    embed = discord.Embed(title="" , description= ":calendar: Esta semana en  Protocolo Intensificación: \n **"+protocol_dict[key%5][0]+"**", color=0x00ff00)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/508999396835196950/520269693479551004/Protocolo.png")
    embed.set_image(url=protocol_dict[key%5][1])
    await client.send_message(user, embed=embed)


@client.command(name='Informe Dreaming City',
                description="Informe Dreaming City",
                brief="Dreaming City",
                aliases=['dc'],
                pass_context=True)
async def dreaming_city(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    ascendant_dict={
        4: ["ʀᴜɪɴᴀs ǫᴜᴇsʙʀᴀᴊᴀᴅᴀs – ᴇsᴘɪɴᴀ ᴅᴇ ᴋᴇʀᴇs","https://cdn.discordapp.com/attachments/508999396835196950/520280396366086154/Espina_de_Keres.png"],
        5: ["ғᴏʀᴛᴀʟᴇᴢᴀ ᴅᴇ ғɪʟᴏs ᴄᴏʀᴛᴀɴᴛᴇs - ʀᴇᴛɪʀᴏ ᴅᴇʟ ʜᴇʀᴀʟᴅᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280494722514964/Reclusion_del_Heraldo.png"],
        0: ["ᴀʙɪsᴍᴏ ᴀɢᴏɴᴀʀᴄʜ – ʙᴀʜɪᴀ ᴅᴇ ʟᴏs ᴅᴇsᴇᴏs ᴀʜᴏɢᴀᴅᴏs","https://cdn.discordapp.com/attachments/508999396835196950/520280295413514253/Bahia_de_los_Deseos_Ahogados.png"],
        1: ["ɢᴜᴀʀɴɪᴄɪᴏɴ ᴄɪᴍᴇʀᴀ - ᴄᴀᴍᴀʀᴀ ᴅᴇ ʟᴜᴢ ᴅᴇ ᴇsᴛʀᴇʟʟᴀs","https://cdn.discordapp.com/attachments/508999396835196950/520280358630064149/Camara_de_Luz_Estelar.png"],
        2: ["ᴏᴜʀᴏʙᴏʀᴇᴀ – ʀᴇᴘᴏsᴏ ᴅᴇʟ ᴀғᴇʟɪᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280560724344862/Reposo_de_Afelio.png"],
        3: ["ᴀʟᴛᴀʀ ᴀʙᴀɴᴅᴏɴᴀᴅᴏ - ᴊᴀʀᴅɪɴᴇs ᴅᴇ ᴇsɪʟᴀ","https://cdn.discordapp.com/attachments/508999396835196950/520280444277751828/Jardines_de_Esila.png"]
    }

    #curse_dict={
    #    0: ["Nivel de Maldicion 1, esta disponible el Trono Destrozado (Mazmorra)!"],
    #    1: ["Nivel de Maldicion 2, esta disponible el Trono Destrozado (Mazmorra)!"],
    #    2: ["Nivel de Maldicion 3, esta disponible el Trono Destrozado (Mazmorra)!"]
    #}
    
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
        #print("Tuesday Before RESET !! Adjusting week number!!")
        key = key - 1
        if key<0:
            key = 0
    
    embed = discord.Embed(title="" , description=":calendar: Esta semana el Desafío Ascendente es en: \n **"+ascendant_dict[key%6][0]+"**", color=0xff0000)
    embed.set_image(url=ascendant_dict[key%6][1])
    #await client.send_message(context.message.channel, embed=embed)
    await client.send_message(user, embed=embed)

    #embed = discord.Embed(title="" , description="**Esta semana la Ciudad Ensoñada tiene,  "+curse_dict[key%3][0]+"**", color=0x000000)
    #await client.send_message(context.message.channel, embed=embed)


@client.command(name='Brote',
                description="Informe Brote Semanal",
                brief="Brote Info",
                aliases=['brote'],
                pass_context=True)
async def hora_zero(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    HZ_dict={        
        1: ["Vacio","https://images-ext-2.discordapp.net/external/inJak0x078Kpn6K_f50f61zV_7_u92W92Nonkvcc2Rc/https/i.imgur.com/ikiCD58.png"],
        2: ["Arco","https://images-ext-2.discordapp.net/external/inJak0x078Kpn6K_f50f61zV_7_u92W92Nonkvcc2Rc/https/i.imgur.com/ikiCD58.png"],
        0: ["Solar","https://images-ext-2.discordapp.net/external/inJak0x078Kpn6K_f50f61zV_7_u92W92Nonkvcc2Rc/https/i.imgur.com/ikiCD58.png"]
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
        #print("Tuesday Before RESET !! Adjusting week number!!")
        key = key - 1
        if key<0:
            key = 0
        #print("Week Number: "+str(key))
        #print(today.hour)
    #print("**************")
    embed = discord.Embed(title="**:earth_americas: Web App Secuencia Terminales Hora Cero**" , url="http://fiddle.jshell.net/pastuleo23/xu1snrc0/show", color=0xffd700)
    embed.set_thumbnail(url="https://www.bungie.net/common/destiny2_content/icons/f0def60d28b4f2a5a7fe8ec3d4764cfa.jpg")
    embed.set_image(url=HZ_dict[key%3][1])
    embed.add_field(name=':map: __Mapas de Sala de Horno__', value="Esta Semana Configuración "+"__**"+HZ_dict[key%3][0]+"**__"+":", inline=False)
    await client.send_message(user, embed=embed)


@client.command(name='Informe Lunar',
                description="Informe Lunar",
                brief="Informe Lunar",
                aliases=['luna'],
                pass_context=True)
async def informe_lunar(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    lunar_nightmares_dict={
        0: ["Pesadilla de Xortal Sworn of Crota",""],
        2: ["Pesadilla de Jaxx Claw of Xivu Arath",""],
        1: ["Pesadilla de Hokris Fear of Mithrax",""],
        3: ["Fallen Council",""]
    }

    altar_dict={
        2: ["Escopeta","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/2f61559b7c57894703b6aaa52a44630c.jpg"],
        0: ["Sniper","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/b990412136d220fd641078418a4903fe.jpg"],
        1: ["Lanza_cohetes","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/eaf113dbb5cea03526009e6030b8c8ee.jpg"]
    }
    
    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]
    day_of_year = int(today.strftime("%j"))
    #print(key)

    if date.today().weekday() == 0: #and today.hour >= 14: # 0 is for monday
        #print("Today is Monday !")
        key = key - 1
        if key<0:
            key = 52
    #print(today)
    #print("Week Number: "+str(key))
    #print("unoficial Day Number: "+str(day_of_year))
        
    if date.today().weekday() == 1 and today.hour < 17:
        #print("Tuesday Before RESET !! Adjusting week number!!")
        key = key - 1
        if key<0:
            key = 0
        #print("Week Number: "+str(key))
        #print(today.hour)
       
    #print(today)
    if today.hour < 17:
        #print("It is BEFORE daily reset !!!")
        day_of_year = day_of_year-1
    else:
        pass
        #print("It is AFTER daily reset !!!")

    #print("Day Number: " +str(day_of_year))
    
    #print("**************")
    #print("Next Week")
    #print((key+1)%6)
    #print(ascendant_dict[key%6][0])
    #print(protocol_dict[key%5][0])
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await client.send_message(user, embed=embed)
    embed = discord.Embed(title="" , description=":calendar: Esta semana la pesadilla deambulante es \n **"+lunar_nightmares_dict[key%4][0]+"**", color=0xff0000)
    #embed.set_image(url=ascendant_dict[key%6][1])
    await client.send_message(user, embed=embed)
    

    embed = discord.Embed(title="" , description="**Hoy el Altar del Dolor entrega,  "+altar_dict[day_of_year%3][0]+"**", color=0x000000)
    embed.set_image(url=altar_dict[day_of_year%3][1])
    await client.send_message(user, embed=embed)

"""
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
"""

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
    
    if capacity:
        for c in capacity:
            for key,val in c.items():
                await client.send_message(context.message.channel, str(key)+": "+str(val)+"/100" )
    else:
        await client.send_message(context.message.channel, "No obtuve respuesta de la API de Bungie ... debe estar en matenimiento ¯\\_(ツ)_/¯" )


@client.command(name='Info Xur',
                description="Entrega la ubicación de Xur en Destiny2",
                brief="Ubicacion Xur",
                aliases=['xur'],
                pass_context=True)
async def xur_info(context):
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await client.send_message(context.message.channel, embed=embed)
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    if await fs.async_isBungieOnline():
        await client.send_message(user, "Juntando información ... un momento por favor.")
        #await client.say("Juntando información ... un momento por favor.")
        is_xur_here, info, inventory, xur_map = get_xur_info(fs)
        if is_xur_here: 
            url_bungie="http://www.bungie.net/"   
            embed = discord.Embed(title=":squid:__XUR:__", description=info, color=0x00ff00)
            embed.add_field(name='Referencia', value="<https://ftw.in/game/destiny-2/find-xur>", inline=False)
            embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png"))
            embed.set_image(url=xur_map)
            await client.send_message(user, embed=embed)
            if inventory and info:
                for idx, val in enumerate(inventory):
                    destiny_class=""
                    index_xur = {0:":gun: **Arma:**",1:":knife: **Cazador:**",2:":punch: **Titan:**",3:":bulb: **Hechicero:**"}
                    destiny_class = index_xur[idx]
                    embed = discord.Embed(title=destiny_class, description="", color=0x00ff00)
                    embed.set_image(url=url_bungie+val)
                    await client.send_message(user, embed=embed)
            else:
                #embed = discord.Embed(title="Error!", description="No pude obtener los datos, intenta mas tarde ...", color=0x00ff00)
                embed = discord.Embed(title="Error!", description="Todavía no esta la info KP@, aguantá la mecha un toque y intenta mas tarde ...", color=0x00ff00)
                await client.send_message(user, embed=embed)
            
        else:
            embed = discord.Embed(title=":x:__XUR:__", description=info, color=0x00ff00)
            embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
            await client.send_message(user, embed=embed)
            #await client.send_message(context.message.channel, embed=embed)
    else:
        embed = discord.Embed(title=":x: Servidores de Destiny estan deshabilitados! Intenta mas tarde ...", description="¯\\_(ツ)_/¯", color=0x00ff00)
        await client.send_message(user, embed=embed)


@client.command(name='Calus Quotes',
                description="Lineas de Calus",
                brief="Calus",
                aliases=['calus'],
                pass_context=True)
async def calus_quotes(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    calus_quotes = ["Everything you know is a lie. There is a truth beyond what your people and your Speaker have told you. I can take you to that truth, if you seek me out. These gifts are a reminder of my words."\
                    ,"If you seek the means to live to your potential, I can guide you to it. There is a power in this universe beyond your feeble Light. I leave you with those words, and these parting gifts. Take them, and grow fat from strength."\
                    ,"Now you’ve seen everything. Do you still believe you’re on the right side? Mull it over, and enjoy my gifts to you. I possess the means to true agency beyond your feeble Light. Seek me out and perhaps I’ll show you how to grow fat from strength."\
                    ,"You’ve accepted my challenge. Good! I would be pleased to see what your Light can do."\
                    ,"Guardians show your selves worthy and I will show you the true means to power!"\
                    ,"The gardens are beautiful, but watch your step. You never know where a beast might lurk!"\
                    ,"The gardens contain the floral emblem of the empire - the plants from which we derive royal nectar. Enjoy them!"\
                    ,"There is beauty to your Light. Let me admire it up close!"]
    embed = discord.Embed(title="", description=random.choice(calus_quotes), color=0xffd700)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/499231830235414529/578589363055755264/unknown.png")
    embed.set_footer(text='Emperor Calus has spoken!')
    await client.send_message(user, embed=embed)


@client.command(name='Riven Quotes',
                description="Lineas de Riven",
                brief="Riven",
                aliases=['riven'],
                pass_context=True)
async def riven_quotes(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    riven_quotes = ["You are finally here, Brother slayer. Spawn killer. All that strength and you're still nothing but a retainer to the Awoken Queen. You could be so much more...all you need do is wish it. Come. I would quite like to meet you."\
                    ,"Have you come to free the Witches? They will resist. Darkness is their shape now ..."\
                    ,"I can give you anything. What is it you want? Weapons? Glory? Peace? Or is it simpler than that?"\
                    ,"Oh ho ho. You are so tiny. Yet you continue to make enemies of so many gods and monsters. You want battle. I'll give you war!"\
                    ,"You sully the sacred architecture of a culture you cannot understand. All so you can say you won today. Could that be what you’re driving toward? Do you have the audacity to wish for my death? Perhaps you and I can work together ..."\
                    ,"The Awoken kept me here for so long. A better fate than my kin suffered. But paradise is a prison when you cannot leave. I would so love to repay the hospitality of those who use my words to carve this city into the screaming surface of reality."\
                    ,"There is no end to the Taken. You have stolen from them more than they could ever take from you. You are destined to fight forever."\
                    ,"You don’t hesitate to reach into the Deep. Your kind is so brave. Those with conviction pair best with my kind. Like you. Like the Awoken prince. Shall we be friends?"\
                    ,"Ah, I've waited so long to fulfill one last wish ..."\
                    ,"I thought they'd never leave. You and I are not done. We're inseparable now. Through your actions, we've forged an age-old-bond between my kind and yours. One wish granted deserves another. And I cannot wait to show you what SHE asked for. O murderer mine..."]
    embed = discord.Embed(title="", description=random.choice(riven_quotes), color=0x000000)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/499231830235414529/578935863992516608/Riven1.png")
    await client.send_message(user, embed=embed)


@client.command(name='Lore',
                description="Lore",
                brief="lore",
                aliases=['lore'],
                pass_context=True)
async def destiny_lore(context):
    user_id = context.message.author.id
    user=await client.get_user_info(user_id)
    await client.say(":white_check_mark: Mensaje directo enviado.")
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await client.send_message(user, embed=embed)
    title, destiny_lore, img = get_random_lore()
    if title and destiny_lore:
        #print("!!!!!!!!!!!!!!!!!!!!!!!!")
        #print(destiny_lore)
        #print(len(destiny_lore))
        #print("IMG:")
        #print(img)
        #print("!!!!!!!!!!!!!!!!!!!!!!!!")
        api_discord_char_limit = 2000
        if len(destiny_lore) < api_discord_char_limit:
            embed = discord.Embed(title=title, description=destiny_lore, color=0x00FF00)
            if "http" in img:
                embed.set_image(url=img)
            embed.add_field(name='Referencia', value="<https://destiny.fandom.com/es/wiki/>", inline=False)
            await client.send_message(user, embed=embed)
        else:
            number_of_parts = math.ceil(len(destiny_lore)/api_discord_char_limit)
            #first_part = int(round(len(destiny_lore)/2))
            #first_half=destiny_lore[0:first_part]
            acum = 0
            #print(int(number_of_parts))
            for i in range(int(number_of_parts)):
                if i == 0:
                    #print("BEGINING: -----------------")
                    begining = destiny_lore[0:api_discord_char_limit]
                    acum = acum + api_discord_char_limit
                    embed = discord.Embed(title=title, description=begining, color=0x00FF00)
                    await client.send_message(user, embed=embed)
                if i == int(number_of_parts)-1:
                    #print("ENDING -----------------")
                    ending = destiny_lore[acum:]
                    embed = discord.Embed(title="", description=ending, color=0x00FF00)
                    if "http" in img:
                        embed.set_image(url=img)
                    embed.add_field(name='Referencia', value="<https://destiny.fandom.com/es/wiki/>", inline=False)
                    await client.send_message(user, embed=embed)
                    
                if i !=0 and i !=int(number_of_parts)-1: 
                    #print("MIDDLE PART -----------------")
                    middle_part = destiny_lore[acum:acum+api_discord_char_limit]
                    acum = acum + api_discord_char_limit
                    embed = discord.Embed(title="", description=middle_part, color=0x00FF00)
                    await client.send_message(user, embed=embed)

                #embed = discord.Embed(title=title, description=first_half, color=0x00FF00)
                #await client.send_message(context.message.channel, embed=embed)
                #second_half=destiny_lore[first_part:]
                #embed = discord.Embed(title="", description=second_half, color=0x00FF00)
                #if "http" in img:
                #    embed.set_image(url=img)
                #embed.add_field(name='Referencia', value="<https://destiny.fandom.com/es/wiki/>", inline=False)
                #await client.send_message(context.message.channel, embed=embed)
    else:
        embed = discord.Embed(title="Error", description="No pude obtener el lore :cry:.\n Intentá en un toque ...", color=0x00FF00)
        await client.send_message(user, embed=embed)


#@client.command(name='Clear',
#                description="Clears messages",
#                brief="clear",
#                aliases=['cl'],
#                pass_context=True)
#async def clear_channel(ctx, number, my_channel):
    #mgs = [] #Empty list to put all the messages in the log
    #number = int(number) #Converting the amount of messages to delete to an integer
    #async for x in client.logs_from(my_channel, limit = number):
        #mgs.append(x)
    #await client.delete_messages(mgs)

"""
@client.command(name='PIE',
                description="Prometheus Inferno Emblem",
                brief="pie",
                aliases=['emblema'],
                pass_context=True)
async def prometheus_inferno_emblem(context):
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await client.send_message(context.message.channel, embed=embed)
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    user_battletag = context.message.content.split(' ', 1)[1]   #separate +rol from message
    embed = discord.Embed(title=":mag_right: Busqueda" , description="Buscando partidas de crisol. Un momento por favor ...", color=0x00ff00)
    await client.send_message(context.message.channel, embed=embed)
    user_destiny = fs.get_playerByTagName(fs.format_PlayerBattleTag(user_battletag)) #Search for player battletag NOT Case Sensitive
    #print(user_destiny)
    if user_destiny:
        user_destiny_id = user_destiny[0]['membershipId'] #From response extract the ID
        #print(user_destiny_id)
        #real_battletag = user_destiny[0]['displayName']
        profile = fs.get_DestinyUserProfileDetail(user_destiny_id)
        characters = profile['characters']['data']
        #print("-------------------------")
        #print(characters)
        res = "\n"
        will_obtain_pi_emblem = False
        for id, info in characters.items():
            character_id = info['characterId']
            #print(character_id)
            page_num=0
            while fs.get_CharactersPVP(user_destiny_id,character_id,page_num):
                page_num = page_num + 1
                if page_num>100:
                    print("WARNING pages > 100 !!!!!!!!!")
                    break
            #print("Number of pages")
            #print(page_num)
            eligable = False
            pvp_matches = fs.get_CharactersPVP(user_destiny_id,character_id,page_num-1)
            await asyncio.sleep(2)
            if pvp_matches:
                for match in pvp_matches:
                    if "2017" in match['period']:
                        eligable=True
                        #print("Player played in 2017 !!!!")
                        break
                    #else:
                    #    print("Player DID NOT play in 2017")
            if eligable:   
                for i in reversed(range(page_num)):
                    pvp_matches = fs.get_CharactersPVP(user_destiny_id,character_id,i)
                    await asyncio.sleep(1)
                    if pvp_matches:
                        #print("/***************************************/")
                        #print("Number of PVP matches in page: "+ str(len(pvp_matches)))
                        #print("/****************Page "+str(i)+"***********************/")
                        #print(pvp_matches_filtered = filter_emblems_pvp(pvp_matches))
                        filtered_matches_list = filter_prismatic_inferno_emblem(pvp_matches)
                        if filtered_matches_list:
                            #print("Will Obtain PIE = TRUE")
                            will_obtain_pi_emblem = True
                            #print(len(filtered_matches_list))
                            break
                        #print("/***************************************/")
                    else:
                        print("No PVP!!")
                        res = "ERROR!"
            else:
                res = ":no_entry: **No sos elegible para el emblema, sorry**"
            await asyncio.sleep(2)
        
        if will_obtain_pi_emblem:
                res = ":white_check_mark: **Recibiras el emblema !! Felicitaciones !!**"
        else:
            res = ":no_entry: **No sos elegible para el emblema, sorry**"
        
        embed = discord.Embed(title=":bell:__Emblema Infierno Prismatico:__", description=res, color=0x00ff00)
        #embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png")) 
        embed.set_image(url="https://cdn.discordapp.com/attachments/499231830235414529/604319122326552586/Prismatic_Inferno_emblem.jpg")
        await client.send_message(context.message.channel, embed=embed)
        await asyncio.sleep(1)


@client.command(name='battle_pass',
                description="BattlePass",
                brief="battlepass",
                aliases=['pass'],
                pass_context=True)
async def battlepass(context):
    img = "https://cdn.discordapp.com/attachments/457673718982901761/624248839297302566/70633858_10157612166659521_8316506064719708160_n.png"
    #img_list = ["https://cdn.discordapp.com/attachments/499231830235414529/623930901302345748/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623930983380418581/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931018323165194/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931077320507392/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931110161907734/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931136850264086/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931158769696799/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931181674528809/unknown.png","https://cdn.discordapp.com/attachments/499231830235414529/623931205854691328/unknown.png"]
    #for i in range(len(img_list)):
        #print(i)
        #embed = discord.Embed(title="", description="", color=0x00ff00)
        #embed.set_image(url=img_list[i])
        #embed.set_thumbnail(url=client.user.avatar_url.replace("webp?size=1024","png"))
        #await client.send_message(context.message.channel, embed=embed)
        #await asyncio.sleep(0.5)
    embed = discord.Embed(title="__**BattlePass**__", description="Recompensas generales:", color=0x00ff00)
    embed.set_image(url=img)
    await client.send_message(context.message.channel, embed=embed)
"""
#######################################################################
################## SPECIAL PERMISIONS COMMANDS  #######################
#######################################################################


@client.command(name='Reset Names',
                description="Reset Names",
                brief="Reset Names",
                aliases=['rn'],
                pass_context=True)
async def reset_names(context):
    my_server = discord.utils.get(client.servers)
    user_id = context.message.author.id
    user=my_server.get_member(user_id)
    for i in my_server.roles:
        if "Admin" in i.name:
                    admin_id=i.id
    if admin_id in [role.id for role in user.roles]:
        await client.send_message(context.message.channel, "**Aguantame la mecha :bomb: ... **")
        print(dir(my_server.members))
        admin_list = ("219539830055501825", "376055309657047040", "198516601497059328", "239122012767911936" )
        for memb in my_server.members:
            #if  ((str(memb.id) == "219539830055501825") or (str(memb.id) == "376055309657047040")):
                #print(dir(memb))
                #print(memb.display_name)
                #print(memb.id)
                #print(memb.name)
                #print(memb.nick)
                #await client.change_nickname(memb, memb.name)
            if ((not memb.bot) or (str(memb.id) not in admin_list)):
                print(memb.name)
                await client.change_nickname(memb, memb.name)
                await asyncio.sleep(1)
        print("Done!")
        await client.send_message(context.message.channel, "**Listo** ")
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")

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
            #print(clan_list)
            if not clan_list:
                print("Could not load CLAN LIST!!!!!")
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_LastPlayed(clan_list)
            print("Got last Played for " + str(clan))
            #await asyncio.sleep(0.5)
            #new_clan_list = await fs.async_add_Clanmembers_Battletag(new_clan_list)
            #print("Got Battletags for" + str(clan))
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_ClanName(new_clan_list)
            print("Got ClanNames for" + str(clan))
            await asyncio.sleep(0.5)
            #print("-----------------------")
            #print("    FINAL CLAN LIST    ")
            #print("-----------------------")
            #print(new_clan_list)
            #print("-----------------------")
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
            #for i in new_clan_list:
            #    del i['last_played']
            if new_clan_list:
                await fs.async_push_clanmates_to_db(new_clan_list)
                print("Pushed ClanMates for" + str(clan))
            else:
                print("Not pushing to DB empty clanmates list for : " + str(clan))
            
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
        #IF date_blacklist_generated do something else no blacklisters
        if date_blacklist_generated:
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
################################# MUSIC & Sound #######################
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
        if players[id]:
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


@client.command(pass_context=True)
async def quit(context):
    server = context.message.server
    if is_user_admin(context):
        voice_client = client.voice_client_in(server)
        id = context.message.server.id
        await voice_client.disconnect()
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(
        name='Crickets',
        description="Plays cricket sound in voice channel",
        brief="cricket_sound",
        aliases=['cri'],
        pass_context=True)
async def crickets(context):
    # grab the user who sent the command
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel = voice_channel.name
        #await client.say('User is in channel: ' + channel)
        vc = await client.join_voice_channel(voice_channel)
        player = vc.create_ffmpeg_player('crickets.mp3', after=lambda: print('done'))
        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
        player.stop()
        await vc.disconnect()
    else:
        await client.say('User is not in a channel.')

"""
@client.command(
        name='LoL',
        description="Plays croud laghf sound in voice channel",
        brief="lol_sound",
        aliases=['lol'],
        pass_context=True)
async def croud_laghfs(context):
    # grab the user who sent the command
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel = voice_channel.name
        await client.say('Playin claps sound in channel: ' + channel)
        vc = await client.join_voice_channel(voice_channel)
        player = await vc.create_ytdl_player("https://youtu.be/Wyzg-hDHpMk", after=lambda: print('done'))
        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
        player.stop()
        await vc.disconnect()
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='LoLC',
        description="Plays croud laghf and clap sound in voice channel",
        brief="lolc_sound",
        aliases=['lolc'],
        pass_context=True)
async def croud_laghfs_claps(context):
    # grab the user who sent the command
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel = voice_channel.name
        #await client.say('User is in channel: ' + channel)
        vc = await client.join_voice_channel(voice_channel)
        player = await vc.create_ytdl_player("https://youtu.be/JOOKK_JG3ho", after=lambda: print('done'))
        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
        player.stop()
        await vc.disconnect()
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='Sad',
        description="Plays sad violin sound in voice channel",
        brief="sad_violin",
        aliases=['sad'],
        pass_context=True)
async def sad_violin(context):
    # grab the user who sent the command
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel = voice_channel.name
        #await client.say('User is in channel: ' + channel)
        vc = await client.join_voice_channel(voice_channel)
        player = await vc.create_ytdl_player("https://youtu.be/yLUxb3eqKh0", after=lambda: print('done'))
        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
        player.stop()
        await vc.disconnect()
    else:
        await client.say('User is not in a channel.')

"""
@client.command(
        name='Javu',
        description="Plays Javu's intro in voice channel",
        brief="javu_intro",
        aliases=['javu'],
        pass_context=True)
async def intro_javu(context):
    # grab the user who sent the command
    user = context.message.author
    voice_channel = user.voice_channel
    channel = None
    if voice_channel != None:
        #print(user.id, type(user.id))
        #print(discord_admin_ids["javu"], type(discord_admin_ids["javu"]))
        if int(user.id) == discord_admin_ids["javu"]:
            channel = voice_channel.name
            #await client.say('LLEGO EL TITAN !!!  ' + channel)
            print('LLEGO EL TITAN !!!  ' + channel)
            vc = await client.join_voice_channel(voice_channel)
            print(vc)
            my_intros = ["https://youtu.be/RmbXT_-Vw00","https://youtu.be/4gf82Qli2XM","https://youtu.be/UXp59oWuuFQ","https://youtu.be/2VN3X95uu_4"]
            #use_avconv = ('use_avconv', False)
            #opts = {'format': 'webm[abr>0]/bestaudio/best','prefer_ffmpeg': not use_avconv}
            #player = await vc.create_ytdl_player(random.choice(my_intros), after=lambda: print('done'))
            #player = await vc.create_ytdl_player(random.choice(my_intros), ytdl_options=opts)
            player = await vc.create_ytdl_player(random.choice(my_intros))
            print(player)
            #player.volume = 0.05
            player.start()
            while not player.is_done():
                await asyncio.sleep(1)
            player.stop()
            await vc.disconnect()
        else:
            await client.say('Tu no eres **Javu the Titan** ,'+str(context.message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='Kernell',
        description="Plays Kernell's intro in voice channel",
        brief="kernell_intro",
        aliases=['kernell'],
        pass_context=True)
async def intro_kernell(context):
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if (voice_channel != None):
        if int(user.id) == discord_admin_ids["kernell"]:
            channel = voice_channel.name
            #await client.say('LLEGO KERNELL !!  ' + channel)
            print('LLEGO KERNELL !!  ' + channel)
            vc = await client.join_voice_channel(voice_channel)
            player = await vc.create_ytdl_player("https://youtu.be/NDCSZEWEcb0", after=lambda: print('done'))
            player.start()
            while not player.is_done():
                await asyncio.sleep(1)
            player.stop()
            await vc.disconnect()
        else:
            await client.say('Tu no eres **Kernell** ,'+str(context.message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='Sonker',
        description="Plays Sonker's intro in voice channel",
        brief="sonker_intro",
        aliases=['sonker'],
        pass_context=True)
async def intro_sonker(context):
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if (voice_channel != None):
        if int(user.id) == discord_admin_ids["sonker"]:
            channel = voice_channel.name
            #await client.say('Sonker is here !!  ' + channel)
            print('Sonker is here !!  ' + channel)
            vc = await client.join_voice_channel(voice_channel)
            player = await vc.create_ytdl_player("https://youtu.be/TrvCtwvILqI", after=lambda: print('done'))
            player.start()
            while not player.is_done():
                await asyncio.sleep(1)
            player.stop()
            await vc.disconnect()
        else:
            await client.say('Tu no eres **Sonker** ,'+str(context.message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='Elenita',
        description="Plays Elenitas's intro in voice channel",
        brief="elenita_intro",
        aliases=['elenita'],
        pass_context=True)
async def intro_elenita(context):
    user = context.message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if (voice_channel != None):
        if int(user.id) == discord_admin_ids["elenita"]:
            channel = voice_channel.name
            print('Elenita is here !!  ' + channel)
            vc = await client.join_voice_channel(voice_channel)
            player = await vc.create_ytdl_player("https://youtu.be/bwB6DG0P0x4", after=lambda: print('done'))
            player.start()
            while not player.is_done():
                await asyncio.sleep(1)
            player.stop()
            await vc.disconnect()
        else:
            await client.say('Tu no eres **Elenita** ,'+str(context.message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


#######################################################################
################################# TEST ################################
#######################################################################


@client.command(name='Test',
                description="Test",
                brief="Test",
                aliases=['test'],
                pass_context=True)
async def testing(context):
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await client.send_message(context.message.channel, embed=embed)
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    #canal_info=None
    print(await fs.async_isBungieOnline())
    xurs_items_ids = await fs.async_get_XurInventory()
    #4 Testing
    xurs_items_ids = [1508896098,2428181146,1474735277,2578771006,312904089]
    
    final_list=[]
    for i in xurs_items_ids:
        valid = await fs.async_get_item_info(str(i))
        if valid:
            #print(type(valid))
            #print(valid['Response']['itemCategoryHashes'])
            for x in valid:
                print(x)
        else:
            print("ERROR")
        
    

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

async def change_status():
    await client.wait_until_ready()
    msgs = cycle(status)
    while not client.is_closed:
        current_status = next(msgs)
        await client.change_presence(game=discord.Game(name=current_status))
        await asyncio.sleep(28800)

#######################################################################
######################### MAIN ########################################
#######################################################################
#client.loop.create_task(list_servers())
#client.loop.create_task(get_server_status_tweets())
client.loop.create_task(change_status())
client.run(BOT_TOKEN)