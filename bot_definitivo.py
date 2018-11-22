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
import pymongo
from datetime import datetime
from boto.s3.connection import S3Connection
import unicodedata
from urllib.request import urlopen
from pymongo import MongoClient


def load_param_from_config(item):
    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
    my_config_file = os.path.join(THIS_FOLDER, 'config.json')
    with open(my_config_file, 'r') as f:
        config = json.load(f)
        return config['DEFAULT'][item]


#4 Heroku
BUNGIE_API_KEY = os.environ['BUNGIE_API_KEY']
BOT_TOKEN = os.environ['BOT_TOKEN']


BOT_PREFIX = ("+") #("+", "!")
client = Bot(command_prefix=BOT_PREFIX)

number_of_hellos=0
greet = False


@client.event
async def on_member_join(member):  
    server = member.server
    for i in server.channels:
        if "ɪɴᴠɪᴛᴀᴅᴏs".upper() in i.name.upper() :
            #print(i.name)
            canal_bienvenida = i
            
    #fmt = 'Bienvenido {0.mention} a {1.name}!'
    fmt = ':wave: **Bienvenido {0.mention} a ESCUADRA 2!**'
    await client.send_message(canal_bienvenida, fmt.format(member))
    #await client.send_message(canal_bienvenida, fmt.format(member, server))
    embed2=discord.Embed()
    embed2=discord.Embed(title="", description="• Necesitas permisos para usar los canales? \n • Escribí debajo el comando **+rol** seguido de tu Battletag! \n **Ejemplo: **\n", color=0x00ff00)
    embed2.set_image(url="https://media.giphy.com/media/fipSNCOjqajUYmHFbC/giphy.gif")
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
                if "Clan" in i.name:
                    custom_clan_role_id=i.id
                if "DJ" in i.name:
                    custom_dj_role_id=i.id

            role_Clan = discord.utils.get(my_server.roles, id=custom_clan_role_id)
            role_DJ = discord.utils.get(my_server.roles, id=custom_dj_role_id)

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
                
                if not user_has_role_clan or not user_has_role_dj:
                    print(str(name)+" missing role ... adding ... ")
                    addroles = [role_Clan, role_DJ]
                    await client.add_roles(user, *addroles)
                
                embed = discord.Embed(title="" , description="El Guardian "+str(name)+" ya fue dado de alta y tiene los roles! ", color=0x00ff00)
                await client.send_message(context.message.channel, embed=embed)
            else:
                user_clan_name = fs.get_PlayerClanName(user_destiny_id)
                #if user_destiny_id and user_clan_name:
                if user_clan_name:
                    if "Escuadra" in user_clan_name:
                        addroles = [role_Clan, role_DJ]
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
                        embed = discord.Embed(title="" , description=":white_check_mark: **Listo** "+context.message.author.mention+" \n• Ya podes usar todos los canales!", color=0x00ff00)
                        await client.send_message(context.message.channel, embed=embed)
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
        embed2.set_image(url="https://media.giphy.com/media/fipSNCOjqajUYmHFbC/giphy.gif")
        await client.send_message(context.message.channel, embed=embed2)
    #delets the message
    #await client.delete_message(context.message)
    await asyncio.sleep(0.01)


async def update_discord_user_last_activity(message_author_id):
    #4 tests
    #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
    #END tests
    #4 Heroku
    MONGODB_URI = os.environ['MONGO_DB_MLAB']
    #END Heroku
    cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = cursor.get_database("bot_definitivo")
    discord_users = db.discord_users
    currentTime = datetime.now()
    update = {
            "last_activity": currentTime
    }
    original_record = get_one_discord_user(message_author_id, discord_users)
    if original_record:
        update_discord_user(original_record,update,discord_users)
    await asyncio.sleep(0.01)
    

@client.event
async def on_message(message, number_of_hellos):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    await update_discord_user_last_activity(message.author.id)
    
    msg = message.content
    #Normalizo el mensaje
    text = unicodedata.normalize('NFKD', msg).encode('ASCII', 'ignore').decode()
    #print(text)
    regex_hola = re.search('^.*H+O+L+A+\s*.*$', text.upper(), re.MULTILINE) 
    #regex_caca = re.search('^C+A+C+A+$', text.upper(), re.MULTILINE)
    regex_chau = re.search('^.*C+H+A+U+$', text.upper(), re.MULTILINE)
    regex_buen_dia = re.search('^.*B+U+E+N+\s+D+I+A+.*$', text.upper(), re.MULTILINE)
    regex_buenos_dias = re.search('^.*B+U+E+N+O+S+\sD+I+A+S.*$', text.upper(), re.MULTILINE)
    regex_buenas_tardes = re.search('^.*B+U+E+N+A+S+\sT+A+R+D+E+S+.*$', text.upper(), re.MULTILINE)
    regex_buenas_noches = re.search('^.*B+U+E+N+A+S+\sN+O+C+H+E+S+.*$', text.upper(), re.MULTILINE)
    regex_buenas = re.search('^B+U+E+N+A+S+$', text.upper(), re.MULTILINE)
    #regex_jaja = re.search('^J+J*A+A*J+J*A+A*$', text.upper(), re.MULTILINE)
    regex_gracias_bot = re.search('^G+R+A+C+I+A+S\s+B+O+T+$', text.upper(), re.MULTILINE)
    #print("Regex jjajajaja = "+str(regex_jaja))
    #print("Regex hola = "+str(regex_hola))
    #print("Regex Buen dia = "+str(regex_buen_dia))
    #print("Regex Buenos dias = "+str(regex_buenos_dias))
    #print("Regex hola = "+str(regex_hola))
    #print("----")
    if (regex_hola or regex_buenas):
        number_of_hellos+=1
        if number_of_hellos>=3:   
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
            number_of_hellos=0
        
    if regex_buen_dia and not regex_hola:
        embed = discord.Embed(title="" , description="Buen Dia para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if regex_buenos_dias and not regex_hola:
        embed = discord.Embed(title="" , description="Buenos Dias para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if regex_buenas_tardes and not regex_hola:
        embed = discord.Embed(title="" , description="Buenas tardes para vos"+message.author.mention+" :wave:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    if regex_buenas_noches and not regex_hola :
            embed = discord.Embed(title="" , description="Buenas noches para vos"+message.author.mention+" :full_moon_with_face: :coffee: ", color=0x00ff00)
            await client.send_message(message.channel, embed=embed)

    #if (regex_caca) or ("mierda".upper() in text.upper()):
        #embed = discord.Embed(title="", description=":poop:", color=0x00ff00)
    #    embed = discord.Embed()
        #response = json.loads(urlopen("http://api.giphy.com/v1/gifs/search?q=poop&api_key=NONE&limit=25").read())
        #embed_list = [d['images']['fixed_width']['url'] for d in response['data']]
        #url = random.choice(embed_list)
        #print(url)
    #    url="https://media.giphy.com/media/tdnUaMuARmi0o/giphy.gif"
    #    embed.set_image(url=url)
    #    await client.send_message(message.channel, embed=embed)

    if "DANCE" in text.upper() or "DANCING" in text.upper():
        embed = discord.Embed()
        random_dance=[
        "",
        "",
        "",
        ""
        ]
        url = random.choice(random_dance)
        embed.set_image(url=url)
        await client.send_message(message.channel, embed=embed)

    if "PUTO" in text.upper():
        embed = discord.Embed(title="" , description="Puto el que lee ... :punch:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    #if "PENE" in text.upper() or "CHOTA" in text.upper() or "PIJA" in text.upper():
    #    embed = discord.Embed(title="" , description=":eggplant:", color=0x00ff00)
    #    await client.send_message(message.channel, embed=embed)
    
    if (regex_chau) or ("ADIOS" in text.upper()):
        respuestas_posibles = ["Nos vemos en Disney ", "Hasta prontito ", "Nos re vimos ", "Cuidate, querete, ojito ... ","Hasta la próxima amig@ ", "Chau "]
        await client.send_message(message.channel, random.choice(respuestas_posibles) + message.author.mention )
    
    if regex_gracias_bot:
        embed = discord.Embed(title="" , description="De nada"+message.author.mention+" ! :vulcan:", color=0x00ff00)
        await client.send_message(message.channel, embed=embed)

    #if regex_jaja:
    #    embed = discord.Embed(title="" , description=":joy:", color=0x00ff00)
    #    await client.send_message(message.channel, embed=embed)
    await asyncio.sleep(0.01)
    await client.process_commands(message)
    

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


#@client.command(name='Saludar',
#                description="Saludo al guardian",
#                brief="saludo",
#                aliases=['hola', 'hello'],
#                pass_context=True)
#async def saludar(context):
#    currentTime = datetime.now()
#    salute_time = ""
#    if currentTime.hour < 12:
#        salute_time = " ,buen día!"
#    elif 12 <= currentTime.hour < 18:
#        salute_time = " ,buenas tardes!"
#    else:
#        salute_time = " ,buenas noches!"
#    msg = 'Hola {0.author.mention}'.format(context.message)
#    msg = msg + salute_time
#    await client.send_message(context.message.channel, msg)

@client.command(name='Ayuda',
                description="Ayuda del bot definitivo",
                brief="ayuda",
                aliases=['ayuda'],
                pass_context=True)
async def ayuda(context):
    msg = 'Hola {0.author.mention} estos son mis comandos : \n \
    +ayuda: Imprime este mensage \n \
    +rol: auto-otorga roles a la gente que esta en el clan Escusara 2,3,4,5 , ejemplo: +rol CNorris#2234'.format(context.message)
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
        await client.send_message(context.message.channel,"Fecha de ultima modificacion: "+date_blacklist_generated)
        blacklisters_list = await get_blacklist(blacklisters)
        for record in blacklisters_list:
            await client.send_message(context.message.channel,record["displayName"]+" \t"+ record["clan"]+" \t"+ record["inactive_time"])
        await client.send_message(context.message.channel, "Fin.")
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.05)


@client.command(name='Run blacklist and populate clan',
                description="Genera la lista negra y actualiza la db del clan",
                brief="run",
                aliases=['run_sync'],
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
            
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_LastPlayed(clan_list)
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_Battletag(new_clan_list)
            await asyncio.sleep(0.5)
            new_clan_list = await fs.async_add_Clanmembers_ClanName(new_clan_list)
            await asyncio.sleep(0.5)
            for clanmate in new_clan_list:
                blacklisted = await fs.async_is_blacklisted(clanmate)
                if blacklisted:
                    blacklist_EX.append(blacklisted)
            await asyncio.sleep(0.5)
            definitive_blacklist = await fs.async_filter_blacklist(blacklist_EX)
            await asyncio.sleep(0.5)
            await fs.async_push_blacklist(definitive_blacklist)
            await asyncio.sleep(0.5)
            
            for i in new_clan_list:
                del i['last_played']
            await fs.async_push_clanmates_to_db(new_clan_list)
            await asyncio.sleep(0.5)
            await client.send_message(context.message.channel, "**Termine con %s**" % clan[1])
            
        t_stop = time.perf_counter()
        #print("Elapsed time: %.1f [min]" % ((t_stop-t_start)/60))
        await client.send_message(context.message.channel, "**Finalizada la generacion de Inactivos y listado de clan, tardé ... %.1f [min]!**"% ((t_stop-t_start)/60))
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.01)


@client.command(name='Get Clans Capacity',
                description="Genera el listado de capacidad del clan",
                brief="capacidad",
                aliases=['clan_capacity','clan_cap'],
                pass_context=True)
async def clan_capacity(context):
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
        capacity = await fs.get_clan_capacity()
        for c in capacity:
            for key,val in c.items():
                await client.send_message(context.message.channel, str(key)+": "+str(val)+"/100" )
    else:
        await client.send_message(context.message.channel, ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.01)


#######################################################################
#######################################################################
#######################################################################
#//////////////////////////////////////////////////////////////////////
#////////////////   DB SECTION           //////////////////////////////
#//////////////////////////////////////////////////////////////////////

######
#Blacklist
######
async def get_blacklist(blacklisters):
    document = blacklisters.find({})
    await asyncio.sleep(0.01)
    return document


async def get_blacklist_date(blacklisters):
    document = blacklisters.find_one()
    await asyncio.sleep(0.01)
    return str(document["date"])


######
#Clanmates
######
async def push_clanmate_to_db(record, clanmates):
    clanmates.insert_one(record)
    await asyncio.sleep(0.01)


def get_one_Clanmate(clanmate_id, clanmates):
        document = clanmates.find_one({'battletag':clanmate_id})
        return document

def is_clanmate_in_db(clanmate_id, clanmates):
        document = clanmates.find_one({'battletag':clanmate_id})
        if document:
            return True
        else:
            return False


######
#Discord
######
async def push_discord_user_db(record, discord_users):
    discord_users.insert_one(record)
    await asyncio.sleep(0.01)



def get_all_discord_users_by_last_activity(discord_users):
        document = discord_users.find({}).sort('last_activity',pymongo.DESCENDING)
        #await asyncio.sleep(0.01)
        return document


def get_one_discord_user(discord_id, discord_users):
        document = discord_users.find_one({'discord_id':discord_id})
        return document


def is_discord_id_in_db(discord_id, discord_users):
        document = discord_users.find_one({'discord_id':discord_id})
        if document:
                return True
        else:
                return False


def update_discord_user(record, updates, discord_users):
        discord_users.update_one({'_id': record['_id']},{
                                '$set': updates
                                }, upsert=False)


#//////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////
#//////////////////////////////////////////////////////////////////////

#OLD WITH FILES
async def add_user_data(member):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if not member.bot and not member.id in users:
            print(member.id+" is not in users.json ... adding ...")
            my_server = discord.utils.get(client.servers)
            user=my_server.get_member(member.id)
            users[member.id] = [member.name, user.nick]
    with open('users.json', 'w') as f:
            json.dump(users,f,indent=4)
    await asyncio.sleep(0.01)


async def add_clanmate_to_clan(clanmate_battletag, his_clan_name):
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        name = clanmate_battletag.split('#')[0]
        if not clanmate_battletag in clan:
            print("From "+ his_clan_name + " " + clanmate_battletag+" battletag is not in clan.json ... adding ...")
            clan[clanmate_battletag] = [his_clan_name, name]
    with open('clan.json', 'w') as f:
            json.dump(clan,f,indent=4)
    await asyncio.sleep(0.01)


def is_user_in_users(user):
    with open('users.json', 'r') as f:
        users = json.load(f)
        if user.id in users:
            return True
        else:
            return False


def is_clanmate_in_clan(clanmate_battletag):
    #Patch for those who have no battleTag
    with open('clan.json', 'r') as f:
        clan = json.load(f)
        #if clanmate_battletag in clan or name[0] in clan:
        if clanmate_battletag in clan:
            return True
        else:
            return False


async def does_user_have_role(member,rol_id):
    for role in member.roles:
        if rol_id == role.id:
            #print(member.name+" tiene rol " + rol_id + "!")
            return True
    await asyncio.sleep(0.01)
    return False



async def async_add_discord_users_list(discord_users_list):
    #4 tests
    #MONGODB_URI = load_param_from_config('MONGO_DB_MLAB')
    #4 Heroku
    MONGODB_URI = os.environ['MONGO_DB_MLAB']
    #END Heroku
    cursor = MongoClient(MONGODB_URI, connectTimeoutMS=30000)
    db = cursor.get_database("bot_definitivo")
    discord_users = db.discord_users
    discord_users.remove({})
    discord_users.insert_many(discord_users_list, ordered=False)


async def list_servers():
    await client.wait_until_ready()
    while not client.is_closed:
        print("Current servers:")
        for server in client.servers:
            print(server.name)
        await asyncio.sleep(600)


#client.loop.create_task(list_servers())
client.run(BOT_TOKEN)