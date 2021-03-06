import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncio
import random
import re
import urllib.request
from bs4 import BeautifulSoup


EncounterSwitch = False
NumGrant = 2
Ungranted = ['Leading The Attack', 'Charging Minotaur', 'White Raven Tactics', 'Revitalizing Strike', 'Defensive Rebuke']
Granted = []
Expended = []

bot = commands.Bot(command_prefix='$')

class AppURLopener(urllib.request.FancyURLopener):
        version = "Mozilla/5.0"

# Both these sources have different HTML formats so i need to parse them differently
# Ark throws everything into one HTML section while d20 just puts it in all different places
# Both are nightmares, I like therafim better

def PrintPageArk(URL):
        
        opener = AppURLopener()
                    
        page = opener.open(URL)
        soup = BeautifulSoup(page, "html.parser")

        content = soup.find('div', attrs={'id': 'content'})
        print(content)
        content = content.text.strip()
        content = content.replace('\n\n', '\n')
        content = content[:2000] + (content[2000:] and '..')

        return content

def PrintPageD(URL):
        
        opener = AppURLopener()
                    
        page = opener.open(URL)
        soup = BeautifulSoup(page, "html.parser")

        title = soup.find('h1')
        title = title.text.strip()

        stitle = soup.find('h4')
        stitle = stitle.text.strip()

        table = soup.find('table', attrs={'class': 'statBlock'})
        table = table.text.strip()
        table = table.replace('\n\n\n', '\r')
        table = table.replace('\n', ' ')

        desc = soup.findAll('p')
        descp = ''
        for para in desc:
                para = para.text.strip()
                if para.__contains__("Hypertext"):
                        break
                descp += '\n' + para + '\n'
        total = title + '\n' + stitle + '\n' + table + '\n' + descp
        return total

def PrintRoll(roll):
    i = 0
    prev_sep = "+"
    current_num = ""
    roll_result = 0
    dice_num = 1
    raw_roll = ""
    if len(roll) != 0:
        if roll[0] == 'd' or roll[0] == '+' or roll[0] == '-':
            prev_sep = roll[0]
            if prev_sep == "d":
                prev_sep = "+d" 
            i=1
        elif not roll[0].isnumeric():
            return ""
    else:
        return ""
    if not roll[-1].isnumeric():
        return ""
    while i < len(roll):
        if roll[i].isnumeric():
            current_num += roll[i]
        else:
            if len(current_num) == 0 and (roll[i] != "d"  or "d" in prev_sep):
                return ""
    
            if roll[i] == "d":
                if "d" in prev_sep:
                    return ""
                if len(current_num) > 0:
                    dice_num = int(current_num)
                    current_num = ""
                if dice_num == 0:
                    return ""
                prev_sep += "d"

            elif roll[i] == "+" or roll[i] == "-":
                if len(current_num) == 0:
                    return ""
                if "+d" == prev_sep:
                    if (int(current_num) == 0):
                        return ""
                    k = 0
                    while k < dice_num:
                        val = random.randint(1,int(current_num))
                        roll_result += val
                        raw_roll += ("+"+str(val))
                        k+=1
                    current_num = ""
                    dice_num = 1
                elif "-d" == prev_sep:
                    if (int(current_num) == 0):
                        return ""
                    k = 0
                    while k < dice_num:
                        val = random.randint(1,int(current_num))
                        roll_result -= val
                        raw_roll += ("-"+str(roll_result))
                        k+=1
                    current_num = ""
                    dice_num = 1                    
                elif "+" == prev_sep:
                    roll_result += int(current_num)
                    raw_roll += ("+"+current_num)
                    current_num = ""
                elif "-" == prev_sep:
                    roll_result -= int(current_num)
                    raw_roll += ("-"+current_num)
                    current_num = ""
                prev_sep = roll[i]
            else:
                return ""
        i+=1
    if "+d" == prev_sep:
        k = 0
        while k < dice_num:
            val = random.randint(1,int(current_num))
            roll_result += val
            raw_roll += ("+"+str(val))
            k+=1
    elif "-d" == prev_sep:
        k = 0
        while k < dice_num:
            val = random.randint(1,int(current_num))
            roll_result -= val
            raw_roll += ("-"+str(val))      
            k+=1        
    elif "+" == prev_sep:
        roll_result += int(current_num)
        raw_roll += ("+"+current_num)
    elif "-" == prev_sep:
        roll_result -= int(current_num)
        raw_roll += ("-"+current_num)
    if raw_roll[0] == "+":
        raw_roll = raw_roll[1:]
    if roll_result < 0:
        roll_result = 0
    return raw_roll+" : "+str(roll_result)

def PrintRolls(userin):
    rolls = ""
    cleaned_input = userin.replace(" ","").lower().split(",")
    if len(cleaned_input) == 0:
        return "Error: No Input Given"
    i = 0
    total = 0
    while i < len(cleaned_input):
        roll = PrintRoll(cleaned_input[i])
        if len(roll) == 0:
            return "Error: Roll Number " + str(i+1) + " Improperly Formatted"
        rolls += roll + "\n"
        total += int(roll.split(":")[1].replace(" ",""))
        i += 1
    rolls += "Total: "+str(total)
    return rolls

@bot.event
async def on_ready():
	print ("Baaybot Active")

@bot.command(pass_context=True)
async def cru(ctx):
        global EncounterSwitch
        if EncounterSwitch == True:
                await ctx.send("Already in a current encounter")
                return

        global CrUser

        CrUser = ctx.message.author

        EncounterSwitch = True
        output = "Welcome to Baay Crusader Logic {0.author.mention} \nUse the functions $turn, $use, and $rec to proceed and don't forget to $clear after the encounter.  Only one can use!".format(ctx.message)
        await ctx.send(output)
        i = 0
        global NumGrant
        global Ungranted
        global Granted
        global Expended
        while i < NumGrant:
            which = random.randint(0, (len(Ungranted)-1))
            Granted.append(Ungranted[which])
            Ungranted.pop(which)
            i += 1
            await ctx.send(str(Granted[len(Granted)-1] + " Granted"))

@bot.command(pass_context=True)
async def rip(ctx):
        await ctx.send(":dean:")

##@bot.command(pass_context=True)
##async def roll(ctx, *args):
##        #assume xdy
##        die = args[0].split("d")
##        for i in range(int(die[0])):
##                roll[i] = random.randint(1, int(die[1]))
##                total += roll[i]
##
##        await ctx.send(roll)


@bot.command(pass_context=True)
async def man(ctx):

        global EncounterSwitch
        
        if EncounterSwitch == False:
                await ctx.send("Not in an encounter currently")
                return
        
        global Ungranted
        global Granted
        global Expended
        output = "Maneuvers Granted: \n"
        i = 0
        while i < len(Granted):
                i += 1
                output += str(i) + ". " + str(Granted[i-1]) + "\n"

        output += ("Maneuvers Expended: \n")
        i = 0
        while i < len(Expended):
                i += 1
                output += str(i) + ". " + str(Expended[i-1]) + "\n"

        await ctx.send(output)

@bot.command(pass_context=True)
async def turn(ctx):

        global EncounterSwitch
        
        if EncounterSwitch == False:
                await ctx.send("Not in an encounter currently")
                return
        
        global CrUser
        global Ungranted
        global Granted

        if CrUser != ctx.message.author:
                await ctx.send("Crusader Denied")
                return
        
        if len(Ungranted) > 0:
                which = random.randint(0, (len(Ungranted)-1))
                Granted.append(Ungranted[which])
                Ungranted.pop(which)
                await ctx.send(str(Granted[len(Granted)-1] + " Granted"))

@bot.command(pass_context=True)
async def use(ctx, select:int):

        global EncounterSwitch
        
        if EncounterSwitch == False:
                await ctx.send("Not in an encounter currently")
                return
        
        global Granted
        global Expended
        global CrUser

        if CrUser != ctx.message.author:
                await ctx.send("Crusader Denied")
                return
        
        if select <= len(Granted) and select > 0:
                x = select - 1
                await ctx.send("Used " + Granted[x])
                Expended.append(Granted[x])
                Granted.pop(x)


@bot.command(pass_context=True)
async def rec(ctx):

        global EncounterSwitch
        
        if EncounterSwitch == False:
                await ctx.send("Not in an encounter currently")
                return
        
        global CrUser

        if CrUser != ctx.message.author:
                await ctx.send("Crusader Denied")
                return
        
        global Granted
        global Expended
        await ctx.send("Granted Maneuvers Recovered")
        Granted.extend(Expended)
        Expended.clear()

@bot.command(pass_context=True)
async def clear(ctx):

        global EncounterSwitch
        
        if EncounterSwitch == False:
                await ctx.send("Not in an encounter currently")
                return

        global CrUser

        if CrUser != ctx.message.author:
                await ctx.send("Crusader Denied")
                return
        
        global Granted
        global Expended
        global Ungranted

        Ungranted = ['Leading The Attack', 'Charging Minotaur', 'White Raven Tactics', 'Revitalizing Strike', 'Defensive Rebuke']
        Granted = []
        Expended = []
        EncounterSwitch = False

# Haven't successfully implemented voice features yet

##@bot.command(pass_context=True)
##async def join(ctx):
##        channel = ctx.message.author.voice.voice_channel
##        await bot.join_voice_channel(channel)
##
##@bot.command(pass_context=True)
##async def leave(ctx):
##        server = ctx.message.server
##        voice_client = bot.voice_client_in(server)
##        await voice_client.disconnect()

# Search for a spell/maneuver/etc within a few different sites

@bot.command(pass_context=True)
async def search(ctx, *args):
        URLend = '-'.join(args)
        URL = "http://therafimrpg.wikidot.com/" + URLend
        # Plug the search term directly into therafim's URL format
        try:
                page = urllib.request.urlopen(URL)
                soup = BeautifulSoup(page, "html.parser")

                title = soup.find('div', attrs={'id': 'page-title'})
                titlep = title.text.strip() 

                content = soup.find('div', attrs={'id': 'page-content'})
                contentp = content.text.strip()

                total = titlep + "\n" + contentp
                total = total[:2000] + (total[2000:] and '..')    
                await ctx.send(total)
                return
        except OSError: # If that's not a valid page, we will attempt another site via google search
                await ctx.send('Starting search...')
        except:
                await ctx.send('Well I tried but its all fucked bro')

        class AppURLopener(urllib.request.FancyURLopener):
                version = "Mozilla/5.0"
        try: 
                from googlesearch import search 
        except ImportError:  
                print("No module named 'google' found")
        indic = False
        query = " ".join(args)
        for k in range(2):
            for j in search(query, num=10, stop=1, pause=2): 
                if j.__contains__("dnd.arkalseif.info"):
                    indic = True
                    await ctx.send(PrintPageArk(j))
                    break
                if j.__contains__("d20srd.org"):
                    print(j)
                    indic = True
                    await ctx.send(PrintPageD(j))
                    break
            if indic == True:
                break
            query = URLend + " dnd 3.5"

@bot.command(pass_context=True)
async def roll(ctx, *args):
        rolls = PrintRolls("".join(args))
        await ctx.send(rolls)

bot.run(*TOKEN*)
