# bot.py
import os
import discord
from discord.ext import tasks
from dotenv import load_dotenv
from time import time
from spreadsheetdata import Update_Sheet, Authorize, Initial_Read_Data
import datetime
import asyncio

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
#bot = commands.Bot(command_prefix='!')


data_sheet = Authorize()

class memberStudyCounter:
    def __init__(self, ID, name):
        self.ID = ID
        self.userName = name
        self.enterTime=-1
        self.session = 0 #in minutes
        self.today = 0 #in minutes
        self.allTime = 0 #in hours

    def Update(self):
        if(self.enterTime!=-1):
            self.session = time() - self.enterTime
            self.session = self.session / 60
            self.enterTime = time()
        self.today = self.today + self.session
        self.allTime = self.allTime + self.session / 60
        self.session = 0


    def TimeIt(self):
        self.enterTime = time()

    def UpdateThenClear(self):
        self.Update()
        Update_Sheet(self.userName, self.today, data_sheet)
        self.session = 0
        self.today = 0


MemberInfList = []





@client.event
async def on_ready():
    guild = discord.utils.find(lambda g: g.name == GUILD, client.guilds)
    '''print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )'''

    for mem in guild.members:
        if mem.bot == True:
            continue
        MemberInfList.append(mem.id)
        name = mem.name + '#' + mem.discriminator
        mem = memberStudyCounter(mem.id,name)
        MemberInfList.append(mem)

    channel_name='reminder'
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new channel: {channel_name}')
        await guild.create_text_channel(channel_name)

    LoadSheet()
    HourlyUpdate.start()
    await NewDay()


@client.event
async def on_voice_state_update(*args):
    guild = args[0].guild
    channel = discord.utils.get(guild.channels, name='reminder')
    UserID = args[0].id
    newC = args[2].channel
    oldC = args[1].channel
    indx = MemberInfList.index(UserID) + 1

    if newC == None:
        mention = '<@!' + str(UserID) + '>'
        await channel.send(mention + ' has left the ' + oldC.name + ' voice channel!')
        if oldC.name == 'Study':
            MemberInfList[indx].Update()
            MemberInfList[indx].enterTime = -1

    elif oldC == None:
        mention = '<@!' + str(UserID) + '>'
        await channel.send(mention + ' has entered the ' + newC.name + ' voice channel!')
        if newC.name == 'Study':
            MemberInfList[indx].TimeIt()

    elif newC.id != oldC.id:
        mention = '<@!' + str(UserID) + '>'
        await channel.send(mention + ' has entered the ' + newC.name + ' voice channel!')
        if newC.name == 'Study':
            MemberInfList[indx].TimeIt()
        if oldC.name == 'Study':
            MemberInfList[indx].Update()
            MemberInfList[indx].enterTime = -1


@client.event
async def on_message(message):
    if message.author.bot == True:
        return

    if message.content == '!me':

        UserID = message.author.id
        UserName = message.author.name+'#'+str(message.author.discriminator)
        indx = MemberInfList.index(UserID) + 1
        MemberInfList[indx].Update()
        StudyToday =  "{:.2f}".format(MemberInfList[indx].today)
        msg = "```\nName: "+UserName+"\nStudy Counter Today: " +str(StudyToday)+" minutes\n"
        AllTime = "{:.2f}".format(MemberInfList[indx].allTime)
        msg=msg+"Study Counter All Time: "+str(AllTime)+" hours\n```"

        print(msg)
        await message.channel.send(msg)

    if message.content == '!update':
        for mem in MemberInfList:
            if type(mem) == int:
                continue
            mem.Update()
        InitUpdateSheet()
        msg = "```Sheet Updated!```"
        await message.channel.send(msg)




@tasks.loop(seconds=3600)#1 hour
async def HourlyUpdate():
    print("Hourly update started:",datetime.datetime.now())
    for mem in MemberInfList:
        if type(mem) == int:
            continue
        mem.Update()
    InitUpdateSheet()


@tasks.loop(hours=24)#1 day
async def NewDay():
    tt=time_until_end_of_day()
    print("Time left until new day: ", tt)
    await asyncio.sleep(tt.seconds-15)
    for mem in MemberInfList:
        if type(mem)==int:
            continue
        mem.UpdateThenClear()
    print("New day updated at ",datetime.datetime.now())



def InitUpdateSheet():
    for i in MemberInfList:
        if type(i)==int:
            continue
        Update_Sheet(i.userName,i.today,data_sheet)

def LoadSheet():
    for mem in MemberInfList:
        if type(mem)==int:
            continue
        mem.today,mem.allTime = Initial_Read_Data(mem.userName, data_sheet)


def time_until_end_of_day(dt=None):
    """
    Get timedelta until end of day on the datetime passed, or current time.
    """
    if dt is None:
        dt = datetime.datetime.now()
    tomorrow = dt + datetime.timedelta(days=1)
    return datetime.datetime.combine(tomorrow, datetime.time.min) - dt


client.run(TOKEN)


'''
await asyncio.sleep(10)



    def Update(self):
        for i in MemberInfList:
            if type(i) == int:
                continue
            i.today = i.today + i.session
            i.allTime = i.allTime + i.session / 60
            i.session = 0
            if (i.enterTime != -1):
                i.enterTime = time()
            i.session = 0

'''