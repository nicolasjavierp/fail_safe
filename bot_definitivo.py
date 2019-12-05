# -*- coding: utf-8 -*-
# Works with Python 3.6

import random
import asyncio
from discord.ext.commands import Bot
#from discord.voice_client import VoiceClient
from fail_safe import FailSafe
import time
import discord
import re
import json
import urllib.request
from datetime import datetime
from datetime import timedelta 
from datetime import date 
import unicodedata
from db import *
from utils import *
#import tweepy
import youtube_dl
import math
from PIL import Image
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
    user_id = message.author.id
    user=await client.fetch_user(user_id)
    
    msg = message.content
    #Normalizo el mensaje
    text = unicodedata.normalize('NFKD', msg).encode('ASCII', 'ignore').decode()
    regex_hola = re.search('^.*H+O+L+A+\s*.*$', text.upper(), re.MULTILINE) 
    regex_buen_dia = re.search('^.*B+U+E+N+\s+D+I+A+.*$', text.upper(), re.MULTILINE)
    regex_buenos_dias = re.search('^.*B+U+E+N+O+S+\sD+I+A+S.*$', text.upper(), re.MULTILINE)
    regex_buenas_tardes = re.search('^.*B+U+E+N+A+S+\sT+A+R+D+E+S+.*$', text.upper(), re.MULTILINE)
    regex_buenas_noches = re.search('^.*B+U+E+N+A+S+\sN+O+C+H+E+S+.*$', text.upper(), re.MULTILINE)
    regex_buenas = re.search('^B+U+E+N+A+S+$', text.upper(), re.MULTILINE)
    regex_gracias_bot = re.search('^G+R+A+C+I+A+S\s+S+A+L+A+D+I+N+.*$', text.upper(), re.MULTILINE)
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
            await message.channel.send(embed=embed)
            #await userDMChannel.send(embed=embed)
            reset_param_aux("number_of_hellos")
        else:
            increment_param_in_1_aux("number_of_hellos")
        
    if regex_buen_dia and not regex_hola:
        if read_param_from_aux("number_of_good_mornings") >=2:
            embed = discord.Embed(title="" , description="Buen Dia para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
            await message.channel.send( embed=embed)
            reset_param_aux("number_of_good_mornings")
        else:
            increment_param_in_1_aux("number_of_good_mornings")

    if regex_buenos_dias and not regex_hola:
        if read_param_from_aux("number_of_good_mornings") >=2:
            embed = discord.Embed(title="" , description="Buenos Dias para vos"+message.author.mention+" :wave: :sun_with_face:", color=0x00ff00)
            await message.channel.send( embed=embed)
            reset_param_aux("number_of_good_mornings")
        else:
            increment_param_in_1_aux("number_of_good_mornings")


    if regex_buenas_tardes and not regex_hola:
            embed = discord.Embed(title="" , description="Buenas tardes para vos"+message.author.mention+" :wave:", color=0x00ff00)
            await message.channel.send( embed=embed)


    if regex_buenas_noches and not regex_hola :
            embed = discord.Embed(title="" , description="Buenas noches para vos"+message.author.mention+" :full_moon_with_face: :coffee: ", color=0x00ff00)
            await message.channel.send(embed=embed)

    
    if regex_gracias_bot:
        embed = discord.Embed(title="" , description="De nada"+message.author.mention+" ! :vulcan:", color=0x00ff00)
        #print(dir(user))
        #print(dir(user.dm_channel))
        #await user.dm_channel.send(embed=embed)
        private_channel = await user.create_dm()
        await private_channel.send(embed=embed)
        await message.channel.send(embed=embed)

    await asyncio.sleep(0.01)
    await client.process_commands(message)


@client.event
async def on_member_join(member):  
    server = member.server
    for i in server.channels:
        if "ʙɪᴇɴᴠᴇɴɪᴅᴏ".upper() in i.name.upper() :
            canal_bienvenida = i            
    for i in server.roles:
        if "DJ" in i.name:
            custom_dj_role_id=i.id
    
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
    await asyncio.sleep(0.01)


#######################################################################
################## COMMON COMMANDS  ###################################
#######################################################################

@client.command(name='RES',
                description="Responde por PJ si hizo raid esta semana",
                brief="Raid esta semana",
                aliases=['raids'],
                pass_ctx=True)
async def raid_this_week(ctx):
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    if await fs.async_isBungieOnline():
        if len(ctx.message.content)>=4:
            user_steam_tag = ctx.message.content.split(' ',1)[1]
            embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing por la migracion a Steam, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
            await private_channel.send(embed=embed)
            embed = discord.Embed(title=":warning: Warning" , description="Este comando toma datos directamente de Bungie, que a veces tarda unos minutos en registrar las Raids recientes. Un momento por favor ...", color=0x00ff00)
            await private_channel.send(embed=embed)
            user_destiny = fs.get_playerBySteamTag(user_steam_tag) #Search for player Steam tag
            if user_destiny:
                if len(user_destiny)==1:
                    user_destiny_id = user_destiny[0]['membershipId'] #From response extract the ID
                    profile = fs.get_DestinyUserProfileDetail(user_destiny_id)
                    characters = profile['characters']['data']
                    res = "\n"
                    for id, info in characters.items():
                        report = "**"+str(fs.guardian_class[info['classHash']])+" "+str(fs.guardian_race[info['raceHash']])+" "+str(fs.guardian_gender[info['genderHash']])+":** \n"
                        character_id = info['characterId']
                        raids = fs.get_CharactersRaids(user_destiny_id,character_id)
                        if raids:    
                            raids_complete = get_completed_raids(info,user_destiny_id,raids)
                            raids_complete_filtered = filter_completed_raids(raids_complete, fs)
                            definitive_complete_raids=get_unique_raids(raids_complete_filtered, fs)
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
                    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/499231830235414529/587653954117173249/9k.png")
                    await private_channel.send(embed=embed)
                else:
                    embed = discord.Embed(title="Error!", description="Tu SteamTag es muy generico hay multiples Guardianes con el mismo nombre, por favor actualizalo a algo mas especifico para usar el comando. \n\
                        Ejemplo: Javu --> Titan Javu", color=0x00ff00)
                    await private_channel.send(embed=embed)
            else:
                embed = discord.Embed(title="Error!", description="No pude encontrar la info relacionada con tu SteamTag: Verifica y proba quitando iconos", color=0x00ff00)
                await private_channel.send(embed=embed)
    else:
        embed = discord.Embed(title=":x: Servidores de Destiny estan deshabilitados! Intenta mas tarde ...", description="¯\\_(ツ)_/¯", color=0x00ff00)
        await private_channel.send(embed=embed)


@client.command(name='Ayuda',
                description="Ayuda del Bot definitivo",
                brief="ayuda",
                aliases=['ayuda', 'help'],
                pass_ctx=True)
async def ayuda(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    msg = 'Hola {0.author.mention} estos son mis comandos :\n\
    `+ayuda` Imprime este mensage.\n\
    `+semana` Reporte de todas las actividades del reset.\n\
    `+marte` Reporte de Armas Protocolo.\n\
    `+ascendente` Reporte de Desafio Ascendente en Dreaming City (Ciudad Ensoñada).\n\
    `+horacero` Informe de rotación elemental semanal de Hora Zero.\n\
    `+decision` Información de rotación semanal de las armas farmeables de Decision.\n\
    `+forja` Información de rotación diaria de Forjas y su orden.\n\
    `+luna` Información de rotación diaria del arma de Altar del Dolor y la rotación semanal de las Pesadillas Deambulantes.\n\
    `+calus` Dialogo random del Emperador Calus.\n\
    `+riven` Dialogo random de la Sirena de Riven.\n\
    `+lore` Elemento de lore de Destiny random.\n\
    `+xur` Informe de la ubicacion y inventario semanal de Xur.\n\
    `+raids` Reporte de las raids realizadas despues del reset semanal. Este es un comando que necesita de un dato adicional que es el SteamTag.\n\
    \t \t \t Ejemplo: `+raids Titan Javu`\n'.format(ctx.message)
    await private_channel.send(msg)


@client.command(name='Informe Semanal',
                description="Informe Semanal",
                brief="Informe Semanal",
                aliases=['semana'],
                pass_ctx=True)
async def informe_semanal(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    ascendant_dict={
        4: ["ʀᴜɪɴᴀs ǫᴜᴇsʙʀᴀᴊᴀᴅᴀs – ᴇsᴘɪɴᴀ ᴅᴇ ᴋᴇʀᴇs","https://cdn.discordapp.com/attachments/508999396835196950/520280396366086154/Espina_de_Keres.png"],
        5: ["ғᴏʀᴛᴀʟᴇᴢᴀ ᴅᴇ ғɪʟᴏs ᴄᴏʀᴛᴀɴᴛᴇs - ʀᴇᴛɪʀᴏ ᴅᴇʟ ʜᴇʀᴀʟᴅᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280494722514964/Reclusion_del_Heraldo.png"],
        0: ["ᴀʙɪsᴍᴏ ᴀɢᴏɴᴀʀᴄʜ – ʙᴀʜɪᴀ ᴅᴇ ʟᴏs ᴅᴇsᴇᴏs ᴀʜᴏɢᴀᴅᴏs","https://cdn.discordapp.com/attachments/508999396835196950/520280295413514253/Bahia_de_los_Deseos_Ahogados.png"],
        1: ["ɢᴜᴀʀɴɪᴄɪᴏɴ ᴄɪᴍᴇʀᴀ - ᴄᴀᴍᴀʀᴀ ᴅᴇ ʟᴜᴢ ᴅᴇ ᴇsᴛʀᴇʟʟᴀs","https://cdn.discordapp.com/attachments/508999396835196950/520280358630064149/Camara_de_Luz_Estelar.png"],
        2: ["ᴏᴜʀᴏʙᴏʀᴇᴀ – ʀᴇᴘᴏsᴏ ᴅᴇʟ ᴀғᴇʟɪᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280560724344862/Reposo_de_Afelio.png"],
        3: ["ᴀʟᴛᴀʀ ᴀʙᴀɴᴅᴏɴᴀᴅᴏ - ᴊᴀʀᴅɪɴᴇs ᴅᴇ ᴇsɪʟᴀ","https://cdn.discordapp.com/attachments/508999396835196950/520280444277751828/Jardines_de_Esila.png"]
    }

    protocol_dict={
        3: ["IKELOS_SMG_v1.0.1 (Subfusil)","https://cdn.discordapp.com/attachments/508999396835196950/520269508728979467/Subfusil.png","<https://www.light.gg/db/items/1723472487>"],
        4: ["IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520269665478508544/Francotirador.png","<https://www.light.gg/db/items/847450546>"],
        0: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png","<https://www.light.gg/db/items/1887808042>\n<https://www.light.gg/db/items/847450546>\n<https://www.light.gg/db/items/1723472487>"],
        1: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png","<https://www.light.gg/db/items/1887808042>\n<https://www.light.gg/db/items/847450546>\n<https://www.light.gg/db/items/1723472487>"],
        2: ["IKELOS_SG_v1.0.1 (Escopeta)","https://cdn.discordapp.com/attachments/508999396835196950/520269571253600271/Escopeta.png","<https://www.light.gg/db/items/1887808042>"]
    }

    HZ_dict={        
        1: ["Vacio","https://cdn.discordapp.com/attachments/649313400370757666/650353356191170573/ikiCD58.png"],
        2: ["Arco","https://cdn.discordapp.com/attachments/649313400370757666/650353356191170573/ikiCD58.png"],
        0: ["Solar","https://cdn.discordapp.com/attachments/649313400370757666/650353356191170573/ikiCD58.png"]
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

    if date.today().weekday() == 0: #and today.hour >= 14: # 0 is for monday
        #print("Today is Monday !")
        key = key - 1
        if key<0:
            key = 52

        
    if date.today().weekday() == 1 and today.hour < 17:
        key = key - 1
        if key<0:
            key = 0


    embed = discord.Embed(title="" , description=":calendar: Esta semana el Desafío Ascendente es en: \n **"+ascendant_dict[key%6][0]+"**", color=0xff0000)
    embed.set_image(url=ascendant_dict[key%6][1])
    await private_channel.send(embed=embed)
    
    embed = discord.Embed(title="" , description= ":calendar: Esta semana en  Protocolo Intensificación: \n **"+protocol_dict[key%5][0]+"**"+protocol_dict[key%5][2], color=0x00ff00)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/508999396835196950/520269693479551004/Protocolo.png")
    #embed.set_image(url=protocol_dict[key%5][1])
    await private_channel.send(embed=embed)

    embed = discord.Embed(title="**Web App Secuencia Terminales Hora Cero**" , url="http://fiddle.jshell.net/pastuleo23/xu1snrc0/show", color=0xffd700)
    embed.set_thumbnail(url="https://www.bungie.net/common/destiny2_content/icons/f0def60d28b4f2a5a7fe8ec3d4764cfa.jpg")
    embed.set_image(url=HZ_dict[key%3][1])
    embed.add_field(name=':map: __Mapas de Sala de Horno__', value="Esta Semana la configuracion es "+"**"+HZ_dict[key%3][0]+"**", inline=False)
    await private_channel.send(embed=embed)

    embed = discord.Embed(title="" , description=":calendar: Esta semana la pesadilla deambulante es \n **"+lunar_nightmares_dict[key%4][0]+"**", color=0xff0000)
    #embed.set_image(url=ascendant_dict[key%6][1])
    await private_channel.send(embed=embed)
    
    embed = discord.Embed(title="" , description="**Hoy el Altar del Dolor entrega,  "+altar_dict[day_of_year%3][0]+"**", color=0x000000)
    embed.set_image(url=altar_dict[day_of_year%3][1])
    await private_channel.send(embed=embed)


@client.command(name='Informe Marte',
                description="Informe Marte",
                brief="Informe Marte",
                aliases=['marte'],
                pass_ctx=True)
async def informe_marte(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    protocol_dict={
        3: ["IKELOS_SMG_v1.0.1 (Subfusil)","https://cdn.discordapp.com/attachments/508999396835196950/520269508728979467/Subfusil.png","<https://www.light.gg/db/items/1723472487>"],
        4: ["IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520269665478508544/Francotirador.png","<https://www.light.gg/db/items/847450546>"],
        0: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png","<https://www.light.gg/db/items/1887808042>\n<https://www.light.gg/db/items/847450546>\n<https://www.light.gg/db/items/1723472487>"],
        1: ["IKELOS_SG_v1.0.1 (Escopeta), IKELOS_SMG_v1.0.1 (Subfusil), IKELOS_SR_v1.0.1 (Francotirador)","https://cdn.discordapp.com/attachments/508999396835196950/520270412421267456/unknown.png","<https://www.light.gg/db/items/1887808042>\n<https://www.light.gg/db/items/847450546>\n<https://www.light.gg/db/items/1723472487>"],
        2: ["IKELOS_SG_v1.0.1 (Escopeta)","https://cdn.discordapp.com/attachments/508999396835196950/520269571253600271/Escopeta.png","<https://www.light.gg/db/items/1887808042>"]
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
     
    embed = discord.Embed(title="" , description= ":calendar: Esta semana en  Protocolo Intensificación: \n **"+protocol_dict[key%5][0]+"**"+protocol_dict[key%5][2], color=0x00ff00)
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/508999396835196950/520269693479551004/Protocolo.png")
    #embed.set_image(url=protocol_dict[key%5][1])
    await private_channel.send(embed=embed)



@client.command(name='Informe Dreaming City',
                description="Informe Dreaming City",
                brief="Dreaming City",
                aliases=['ascendente'],
                pass_ctx=True)
async def informe_dreaming_city(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    ascendant_dict={
        4: ["ʀᴜɪɴᴀs ǫᴜᴇsʙʀᴀᴊᴀᴅᴀs – ᴇsᴘɪɴᴀ ᴅᴇ ᴋᴇʀᴇs","https://cdn.discordapp.com/attachments/508999396835196950/520280396366086154/Espina_de_Keres.png"],
        5: ["ғᴏʀᴛᴀʟᴇᴢᴀ ᴅᴇ ғɪʟᴏs ᴄᴏʀᴛᴀɴᴛᴇs - ʀᴇᴛɪʀᴏ ᴅᴇʟ ʜᴇʀᴀʟᴅᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280494722514964/Reclusion_del_Heraldo.png"],
        0: ["ᴀʙɪsᴍᴏ ᴀɢᴏɴᴀʀᴄʜ – ʙᴀʜɪᴀ ᴅᴇ ʟᴏs ᴅᴇsᴇᴏs ᴀʜᴏɢᴀᴅᴏs","https://cdn.discordapp.com/attachments/508999396835196950/520280295413514253/Bahia_de_los_Deseos_Ahogados.png"],
        1: ["ɢᴜᴀʀɴɪᴄɪᴏɴ ᴄɪᴍᴇʀᴀ - ᴄᴀᴍᴀʀᴀ ᴅᴇ ʟᴜᴢ ᴅᴇ ᴇsᴛʀᴇʟʟᴀs","https://cdn.discordapp.com/attachments/508999396835196950/520280358630064149/Camara_de_Luz_Estelar.png"],
        2: ["ᴏᴜʀᴏʙᴏʀᴇᴀ – ʀᴇᴘᴏsᴏ ᴅᴇʟ ᴀғᴇʟɪᴏ","https://cdn.discordapp.com/attachments/508999396835196950/520280560724344862/Reposo_de_Afelio.png"],
        3: ["ᴀʟᴛᴀʀ ᴀʙᴀɴᴅᴏɴᴀᴅᴏ - ᴊᴀʀᴅɪɴᴇs ᴅᴇ ᴇsɪʟᴀ","https://cdn.discordapp.com/attachments/508999396835196950/520280444277751828/Jardines_de_Esila.png"]
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
    
    embed = discord.Embed(title="" , description=":calendar: Esta semana el Desafío Ascendente es en: \n **"+ascendant_dict[key%6][0]+"**", color=0xff0000)
    embed.set_image(url=ascendant_dict[key%6][1])
    await private_channel.send(embed=embed)


@client.command(name='Brote',
                description="Informe Brote Semanal",
                brief="Brote Info",
                aliases=['horacero'],
                pass_ctx=True)
async def informe_hora_zero(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    HZ_dict={        
        1: ["Vacio","https://cdn.discordapp.com/attachments/649313400370757666/650353356191170573/ikiCD58.png"],
        2: ["Arco","https://cdn.discordapp.com/attachments/649313400370757666/650353356191170573/ikiCD58.png"],
        0: ["Solar","https://cdn.discordapp.com/attachments/649313400370757666/650353356191170573/ikiCD58.png"]
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
    embed = discord.Embed(title="**Web App Secuencia Terminales Hora Cero**" , url="http://fiddle.jshell.net/pastuleo23/xu1snrc0/show", color=0xffd700)
    embed.set_thumbnail(url="https://www.bungie.net/common/destiny2_content/icons/f0def60d28b4f2a5a7fe8ec3d4764cfa.jpg")
    embed.set_image(url=HZ_dict[key%3][1])
    embed.add_field(name=':map: __Mapas de Sala de Horno__', value="Esta Semana la configuracion es "+"**"+HZ_dict[key%3][0]+"**", inline=False)
    await private_channel.send(embed=embed)


@client.command(name='Informe Lunar',
                description="Informe Lunar",
                brief="Informe Lunar",
                aliases=['luna'],
                pass_ctx=True)
async def informe_lunar(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    lunar_nightmares_dict={
        0: ["Pesadilla de Xortal Sworn of Crota",""],
        2: ["Pesadilla de Jaxx Claw of Xivu Arath",""],
        1: ["Pesadilla de Hokris Fear of Mithrax",""],
        3: ["Fallen Council",""]
    }
    altar_dict={
        2: ["Escopeta","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/2f61559b7c57894703b6aaa52a44630c.jpg","https://www.light.gg/db/items/2782847179"],
        0: ["Francotirador","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/b990412136d220fd641078418a4903fe.jpg","https://www.light.gg/db/items/2164448701"],
        1: ["Lanzacohetes","https://cdn.thetrackernetwork.com/destiny/common/destiny2_content/icons/eaf113dbb5cea03526009e6030b8c8ee.jpg","https://www.light.gg/db/items/3067821200"]
    }
    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]
    day_of_year = int(today.strftime("%j"))

    if date.today().weekday() == 0: 
        key = key - 1
        if key<0:
            key = 52

    if date.today().weekday() == 1 and today.hour < 17:
        key = key - 1
        if key<0:
            key = 0

    if today.hour < 17:
        day_of_year = day_of_year-1
    else:
        pass

    embed = discord.Embed(title="" , description=":calendar: Esta semana la pesadilla deambulante es \n **"+lunar_nightmares_dict[key%4][0]+"**", color=0xff0000)
    #embed.set_image(url=ascendant_dict[key%6][1])
    await private_channel.send(embed=embed)

    embed = discord.Embed(title="" , description="**Hoy el Altar del Dolor entrega,  "+altar_dict[day_of_year%3][0]+"** \n"+altar_dict[day_of_year%3][2], color=0x000000)
    #embed.set_image(url=altar_dict[day_of_year%3][1])
    await private_channel.send(embed=embed)


@client.command(name='Informe Forja',
                description="Informe Forja",
                brief="Informe Forja",
                aliases=['forja'],
                pass_ctx=True)
async def informe_forja(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")

    forge_dict={
        0: ["Volundr","https://cdn.discordapp.com/attachments/649313400370757666/651887840803815464/Volundr.jpg"],
        2: ["Gofannon","https://cdn.discordapp.com/attachments/649313400370757666/651887815197720580/Gofannon.jpg"],
        1: ["Izanami","https://cdn.discordapp.com/attachments/649313400370757666/651887829479325758/Izanami.jpg"],
        3: ["Bergusia","https://cdn.discordapp.com/attachments/649313400370757666/651887795727630357/Bergusia.jpg"]
    }

    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]
    day_of_year = int(today.strftime("%j"))

    if date.today().weekday() == 0: 
        key = key - 1
        if key<0:
            key = 52

    if date.today().weekday() == 1 and today.hour < 17:
        key = key - 1
        if key<0:
            key = 0

    if today.hour < 17:
        day_of_year = day_of_year-1
    else:
        pass
    
    active_forge=forge_dict[key%4][0]
    forge_ordered_list=["Volundr","Gofannon","Izanami","Bergusia"]

    temp_string=""
    for i in forge_ordered_list:
        if i==forge_dict[key%4][0]:
            temp_string = temp_string + ":white_check_mark: "+i+"\n"
        else:
            temp_string = temp_string + ":x: "+i+"\n"
    embed = discord.Embed(title="" , description="Hoy la Forja activa es: \n\n**"+temp_string+"**", color=0xff0000)
    #embed.set_footer(text='Mañana estará disponible '+forge_dict[(key+1)%4][0])
    embed.set_thumbnail(url=forge_dict[key%4][1])
    await private_channel.send(embed=embed)


@client.command(name='Informe Decision',
                description="Informe Decision",
                brief="Informe Decision",
                aliases=['decision'],
                pass_ctx=True)
async def informe_decision(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")

    gambit_decision={
        # 0 = 2 Caballeros / 1 = Oryx
        0: [["Explorador","https://www.bungie.net/common/destiny2_content/icons/f32f6b8896ca5b2684c6e02d447f5182.jpg","<https://www.light.gg/db/items/3504336176/night-watch/>"],["Pistola","https://www.bungie.net/common/destiny2_content/icons/abd91ac904ddb37308898c9a5fd38b02.jpg","<https://www.light.gg/db/items/2199171672/lonesome/>"], ["Escopeta","https://www.bungie.net/common/destiny2_content/icons/d39006fe5498ec8720622da5a31dd066.jpg","<https://www.light.gg/db/items/755130877/last-man-standing/>"], ["Francotirador","https://www.bungie.net/common/destiny2_content/icons/0ae824a841009f28327d905c0610b03c.jpg","<https://www.light.gg/db/items/1115104187/sole-survivor/>"], ["Espada","https://www.bungie.net/common/destiny2_content/icons/c32e9275a505a1e39bfc146dca3702b6.jpg","<https://www.light.gg/db/items/715338174/just-in-case/>"]],
        1: [["Pulsos","https://bungie.net/common/destiny2_content/icons/7967ce5273a19ca50fe3ec1fd1b1b375.jpg","<https://www.light.gg/db/items/299665907/outlast/>"],["Cañon de mano","https://bungie.net/common/destiny2_content/icons/7106d949c81a1b2b281964ae2184d6b2.jpg","<https://www.light.gg/db/items/3116356268/spare-rations/>"], ["SMG","https://bungie.net/common/destiny2_content/icons/870aa58f8314ca60ec3075f937735885.jpg","<https://www.light.gg/db/items/2744715540/bug-out-bag/>"], ["Autorifle","https://bungie.net/common/destiny2_content/icons/48037e6416c3c9da07030a72931e0ca9.jpg","<https://www.light.gg/db/items/821154603/gnawing-hunger/>"], ["Lanza Granadas","https://bungie.net/common/destiny2_content/icons/f689eb2328e786599701352b9c01b64d.jpg","<https://www.light.gg/db/items/736901634/doomsday/>"]]
    }
    
    today = datetime.now()
    key = datetime.date(today).isocalendar()[1]

    if date.today().weekday() == 0: 
        key = key - 1
        if key<0:
            key = 52

    if date.today().weekday() == 1 and today.hour < 17:
        key = key - 1
        if key<0:
            key = 0
    res = ""
    for i in gambit_decision[key%2]:
        res = res + i[0] + ":\n" + i[2] + "\n\n"
    embed = discord.Embed(title="" , description=":small_orange_diamond:**Esta semana La Decisión entrega:** \n **"+res+"**", color=0x003100)
    if key%2 == 0:
        url="https://cdn.discordapp.com/attachments/499231830235414529/649981441001914369/unknown.png"
    else:
        url="https://cdn.discordapp.com/attachments/499231830235414529/649981233270489111/unknown.png"
    embed.set_image(url=url)
    await private_channel.send(embed=embed)


@client.command(name='Get Clans Capacity',
                description="Genera el listado de capacidad del clan",
                brief="capacidad",
                aliases=['cap','clan_cap'],
                pass_ctx=True)
async def clan_capacity(ctx):
    #4 tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))      #Start Fail_Safe 4tests
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    await ctx.message.channel.send("Juntando info. Un momento por favor.")
    capacity = await fs.get_clan_capacity()
    
    if capacity:
        for c in capacity:
            for key,val in c.items():
                await ctx.message.channel.send( str(key)+": "+str(val)+"/100" )
    else:
        await ctx.message.channel.send( "No obtuve respuesta de la API de Bungie ... debe estar en matenimiento ¯\\_(ツ)_/¯" )


@client.command(name='Calus Quotes',
                description="Lineas de Calus",
                brief="Calus",
                aliases=['calus'],
                pass_ctx=True)
async def calus_quotes(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
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
    await private_channel.send(embed=embed)


@client.command(name='Riven Quotes',
                description="Lineas de Riven",
                brief="Riven",
                aliases=['riven'],
                pass_ctx=True)
async def riven_quotes(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
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
    await private_channel.send(embed=embed)


@client.command(name='Lore',
                description="Lore",
                brief="lore",
                aliases=['lore'],
                pass_ctx=True)
async def destiny_lore(ctx):
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    title, destiny_lore, img = get_random_lore()
    if title and destiny_lore:
        api_discord_char_limit = 2000
        if len(destiny_lore) < api_discord_char_limit:
            embed = discord.Embed(title=title, description=destiny_lore, color=0x00FF00)
            if "http" in img:
                embed.set_image(url=img)
            embed.add_field(name='Referencia', value="<https://destiny.fandom.com/es/wiki/>", inline=False)
            await private_channel.send(embed=embed)
        else:
            number_of_parts = math.ceil(len(destiny_lore)/api_discord_char_limit)
            acum = 0
            for i in range(int(number_of_parts)):
                if i == 0:
                    begining = destiny_lore[0:api_discord_char_limit]
                    acum = acum + api_discord_char_limit
                    embed = discord.Embed(title=title, description=begining, color=0x00FF00)
                    await private_channel.send(embed=embed)
                if i == int(number_of_parts)-1:
                    ending = destiny_lore[acum:]
                    embed = discord.Embed(title="", description=ending, color=0x00FF00)
                    if "http" in img:
                        embed.set_image(url=img)
                    embed.add_field(name='Referencia', value="<https://destiny.fandom.com/es/wiki/>", inline=False)
                    await private_channel.send(embed=embed)
                    
                if i !=0 and i !=int(number_of_parts)-1: 
                    middle_part = destiny_lore[acum:acum+api_discord_char_limit]
                    acum = acum + api_discord_char_limit
                    embed = discord.Embed(title="", description=middle_part, color=0x00FF00)
                    await private_channel.send(embed=embed)

    else:
        embed = discord.Embed(title="Error", description="No pude obtener el lore :cry:.\n Intentá en un toque ...", color=0x00FF00)
        await private_channel.send(embed=embed)



#######################################################################
################## SPECIAL PERMISIONS COMMANDS  #######################
#######################################################################

@client.command(name='Run blacklist and populate clan',
                description="Genera la lista negra y actualiza la db del clan",
                brief="run",
                aliases=['sync'],
                pass_ctx=True)
async def run_sync(ctx):
    my_server = discord.utils.get(client.guilds)
    user_id = ctx.message.author.id
    user=my_server.get_member(user_id)
    admin_id = None
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
        await ctx.message.channel.send( "**Aguantame la mecha :bomb: ... que estoy creando el listado de inactivos y pisando el listado de clan. **")
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
            await ctx.message.channel.send( "**Termine con %s**" % clan[1])
            
        t_stop = time.perf_counter()
        #print("Elapsed time: %.1f [min]" % ((t_stop-t_start)/60))
        await ctx.message.channel.send( "**Finalizada la generacion de Inactivos y listado de clan, tardé ... %.1f [min]!**"% ((t_stop-t_start)/60))
    else:
        await ctx.message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.01)


@client.command(name='Poblacion',
                description="Indica los integrantes de discord",
                brief="poblacion",
                aliases=['poblacion','pob'],
                pass_ctx=True)
async def poblacion(ctx):
    my_server = discord.utils.get(client.guilds)
    user_id = ctx.message.author.id
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
        await ctx.message.channel.send( "Populación Discord:")
        await ctx.message.channel.send( "Total Usuarios: " + str(my_server.member_count))
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
        await ctx.message.channel.send( "Guardianes = "+str(my_server.member_count-bot_num) + "\n" + "Bots = "+str(bot_num))
    else:
        await ctx.message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.01)


@client.command(name='Inactivos',
                description="Expone el listado de inactivos en discord",
                brief="inactivos",
                aliases=['inactivos','inac'],
                pass_ctx=True)
async def inactivos(ctx):
    my_server = discord.utils.get(client.guilds)
    user_id = ctx.message.author.id
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
            await ctx.message.channel.send(":calendar: **Fecha de ultima modificacion: **"+date_blacklist_generated)
            blacklisters_list = await get_blacklist(blacklisters)
            
            my_dict = {}
            for record in blacklisters_list:
                #await message.channel.send(record["displayName"]+" \t"+ record["clan"]+" \t"+ record["inactive_time"])    
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
                embed.set_thumbnail(url=client.user.avatar_url)     
                #embed.set_author(name=client.user.name)#,icon_url=client.user.avatar_url.replace("webp?size=1024","png"))
                #embed.add_field(name='Field Name', value='Field Value', inline=False)
                #embed.add_field(name='Field Name', value='Field Value', inline=True)
                #embed.add_field(name='Field Name', value='Field Value', inline=True)
                #await client.say(embed=embed)
                await ctx.message.channel.send( embed=embed)
            await asyncio.sleep(0.2)       
        await ctx.message.channel.send( "Fin.")
    else:
        await ctx.message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")
    await asyncio.sleep(0.05)


#######################################################################
################################# MUSIC & Sound #######################
#######################################################################


@client.command(pass_ctx=True)
async def play(ctx,url):
    server = message.server
    if is_user_admin(ctx):
        channel = message.author.voice.voice_channel
        print(client.is_voice_connected(channel))
        
        await client.join_voice_channel(channel)
        voice_client = client.voice_client_in(server)
        
        player = await voice_client.create_ytdl_player(url, after=lambda:check_queue(server.id, my_queues, players))
        players[server.id] = player
        player.start()
        #id = message.server.id
        #players[id].start()
    else:
        await message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(pass_ctx=True)
async def pause(ctx):
    server = message.server
    if is_user_admin(ctx):
        id = message.server.id
        players[id].pause()
    else:
        await message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(pass_ctx=True)
async def stop(ctx):
    server = message.server
    if is_user_admin(ctx):
        voice_client = client.voice_client_in(server)
        id = message.server.id
        await voice_client.disconnect()
        if players[id]:
            players[id].stop()
    else:
        await message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")
    

@client.command(pass_ctx=True)
async def resume(ctx):
    server = message.server
    if is_user_admin(ctx):
        id = message.server.id
        players[id].resume()
    else:
        await message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(pass_ctx=True)
async def queue(ctx,url):
    server = message.server
    if is_user_admin(ctx):
        voice_client = client.voice_client_in(server)
        if voice_client:
            player = await voice_client.create_ytdl_player(url, after=lambda:check_queue(server.id, my_queues, players))
            if server.id in my_queues:
                my_queues[server.id].append(player)
            else:
                my_queues[server.id] = [player]
            await client.say("Video encolado KPO !")


@client.command(pass_ctx=True)
async def skip(ctx,url):
    server = message.server
    if is_user_admin(ctx):
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


@client.command(pass_ctx=True)
async def quit(ctx):
    server = message.server
    if is_user_admin(ctx):
        voice_client = client.voice_client_in(server)
        id = message.server.id
        await voice_client.disconnect()
    else:
        await message.channel.send( ":no_entry: **No tenés permisos para ejecutar este comando**")


@client.command(
        name='Crickets',
        description="Plays cricket sound in voice channel",
        brief="cricket_sound",
        aliases=['cri'],
        pass_ctx=True)
async def crickets(ctx):
    # grab the user who sent the command
    user = message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel = voice_channel.name
        vc = await client.join_voice_channel(voice_channel)
        player = vc.create_ffmpeg_player('crickets.mp3', after=lambda: print('done'))
        player.start()
        while not player.is_done():
            await asyncio.sleep(1)
        player.stop()
        await vc.disconnect()
    else:
        await message.channel.send('User is not in a channel.')


@client.command(
        name='LoL',
        description="Plays croud laghf sound in voice channel",
        brief="lol_sound",
        aliases=['lol'],
        pass_ctx=True)
async def croud_laghfs(ctx):
    # grab the user who sent the command
    user = message.author
    voice_channel = user.voice.voice_channel
    channel = None
    if voice_channel != None:
        channel = voice_channel.name
        await ctx.message.channel.send('Playin claps sound in channel: ' + channel)
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
        pass_ctx=True)
async def croud_laghfs_claps(ctx):
    # grab the user who sent the command
    user = message.author
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
        pass_ctx=True)
async def sad_violin(ctx):
    # grab the user who sent the command
    user = message.author
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


@client.command(
        name='Javu',
        description="Plays Javu's intro in voice channel",
        brief="javu_intro",
        aliases=['javu'],
        pass_ctx=True)
async def intro_javu(ctx):
    # grab the user who sent the command
    user = ctx.message.author
    
    voice_channel = None
    if not ctx.author.voice is None:
        voice_channel = ctx.author.voice.channel
    if not voice_channel is None:
        vc = await voice_channel.connect()
        print(dir(vc))
        my_intros = ["https://youtu.be/RmbXT_-Vw00","https://youtu.be/4gf82Qli2XM","https://youtu.be/UXp59oWuuFQ","https://youtu.be/2VN3X95uu_4"]
        #vc.play(discord.FFmpegPCMAudio(executable="/home/njp/Documents/warmind/warmind/lib/python3.6/site-packages/ffmpeg",source=random.choice(my_intros)))
        player = await YTDLSource.from_url(random.choice(my_intros))
        ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
        await ctx.send('Now playing: {}'.format(player.title))

        #vc.play(discord.FFmpegPCMAudio(random.choice(my_intros)))
        #player = await vc.create_ytdl_player(random.choice(my_intros))
        #player.volume = 0.5
        #player.start()
        #while not player.is_done():
        #    await asyncio.sleep(1)
        #player.stop()
        #await vc.disconnect()
        #vc.play(discord.FFmpegPCMAudio('https://youtu.be/RmbXT_-Vw00'))
    '''
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
            await client.say('Tu no eres **Javu the Titan** ,'+str(message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')
    '''

@client.command(
        name='Kernell',
        description="Plays Kernell's intro in voice channel",
        brief="kernell_intro",
        aliases=['kernell'],
        pass_ctx=True)
async def intro_kernell(ctx):
    user = message.author
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
            await client.say('Tu no eres **Kernell** ,'+str(message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='Sonker',
        description="Plays Sonker's intro in voice channel",
        brief="sonker_intro",
        aliases=['sonker'],
        pass_ctx=True)
async def intro_sonker(ctx):
    user = message.author
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
            await client.say('Tu no eres **Sonker** ,'+str(message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


@client.command(
        name='Elenita',
        description="Plays Elenitas's intro in voice channel",
        brief="elenita_intro",
        aliases=['elenita'],
        pass_ctx=True)
async def intro_elenita(ctx):
    user = message.author
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
            await client.say('Tu no eres **Elenita** ,'+str(message.author.name)+ ', no podes usar su intro ...' )
    else:
        await client.say('User is not in a channel.')


#######################################################################
################################# TEST ################################
#######################################################################


@client.command(name='Test',
                description="Test",
                brief="Test",
                aliases=['test'],
                pass_ctx=True)
async def testing(ctx):
    #embed = discord.Embed(title=":warning: Warning" , description="Este comando esta en periodo de beta testing, ante cualquier inconveniente informar a un admin. Gracias", color=0x00ff00)
    #await message.channel.send( embed=embed)
    #4 Tests
    #fs = FailSafe(load_param_from_config('BUNGIE_API_KEY'))
    #4 Heroku
    fs = FailSafe(BUNGIE_API_KEY)         #Start Fail_Safe 4 Heroku
    #END Heroku
    #canal_info=None
    user_id = ctx.message.author.id
    user=await client.fetch_user(user_id)
    private_channel = await user.create_dm()
    await ctx.message.channel.send(":white_check_mark: Mensaje directo enviado.")
    print(await fs.async_isBungieOnline())
    embed = discord.Embed(title=":warning: Warning" , description="Este comando toma datos directamente de Bungie ... Un momento por favor ...", color=0x00ff00)
    await private_channel.send(embed=embed)
    xurs_items_ids = await fs.async_get_XurInventory()
    #print("-----------------")
    #print(xurs_items_ids)
    #print("-----------------")
    #4 Testing
    xurs_items_ids = [{'itemHash':1508896098},{'itemHash':2428181146},{'itemHash':1474735277},{'itemHash':2578771006},{'itemHash':312904089}]
    
    final_items={}
    for i in xurs_items_ids:
        #print("============")
        #print(i['itemHash'])
        #print("============")
        valid = await fs.async_get_item_info(str(i['itemHash']))
        if valid and valid['itemCategoryHashes']:
                for key, value in fs.guardian_category_gear.items():
                    if key in valid['itemCategoryHashes'] and valid['itemType']==2:
                        #print("Adding "+str(key) " a "+ str())
                        #print(value)
                        if str(value) == "Titan" :
                            final_items[value] = [valid['displayProperties']['name'], 'https://www.bungie.net/' + valid['displayProperties']['icon'], 'https://www.light.gg/db/items/'+str(i['itemHash']),(250, 105)]
                        if str(value) == "Hechicero" :
                            final_items[value] = [valid['displayProperties']['name'], 'https://www.bungie.net/' + valid['displayProperties']['icon'], 'https://www.light.gg/db/items/'+str(i['itemHash']),(380, 105)]
                        if str(value) == "Cazador" :
                            final_items[value] = [valid['displayProperties']['name'], 'https://www.bungie.net/' + valid['displayProperties']['icon'], 'https://www.light.gg/db/items/'+str(i['itemHash']),(520, 105)]
                    if (key not in fs.guardian_category_gear.items()) and valid['itemType']==3:
                        final_items['Arma'] = [valid['displayProperties']['name'], 'https://www.bungie.net/' + valid['displayProperties']['icon'], 'https://www.light.gg/db/items/'+str(i['itemHash']),(55, 105)]
        else:
            #print("Removing ..."+str(i)+"Contracts of the 9")
            xurs_items_ids.remove(i)
    #print(final_items)
    background = Image.open('./misc/xur_bg.png')
    backgroundCopy = background.copy()
    #print("////////////// BG //////////////")
    #print(background.format, background.size, background.mode)
    #print("////////////////////////////////")
    test=""
    for key, value in final_items.items():
        test = test + key +": **"+ value[0] + "** <"+value[2]+">\n"
        #print(test)
        image = Image.open(urllib.request.urlopen(value[1]))
        #print("////////////// Web IMG //////////////")
        #print(image.format, image.size, image.mode, value[3])
        #print("////////////"+str(value[3])+"///////////////////")
        backgroundCopy.paste(image, value[3])
        backgroundCopy.save("./misc/test.png", "PNG")
    #background.save("./misc/xur_bg", "PNG")
    await private_channel.send('', file=discord.File("./misc/test.png"))
    embed = discord.Embed(title="Iventario Xur" , description=test, color=0x00ff00)
    
    await private_channel.send(embed=embed)


#######################################################################
######################### LOOPS #######################################
#######################################################################

async def list_servers():
    await client.wait_until_ready() 
    while not client.is_closed:
        print("Current servers:")
        for server in client.guilds:
            print(server.name)
        await asyncio.sleep(600)


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
client.loop.create_task(change_status())
#client.run(load_param_from_config('BOT_TOKEN'))
client.run(BOT_TOKEN)