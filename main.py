import os
import nextcord
import time
from nextcord.ext import commands
import asyncio
import youtube_dl

print("Starting bot...")


bot = commands.Bot(command_prefix='$')
game = nextcord.Game("with Python")
usageInfo = '$pomodoro {Number of Sessions} {Pomodoro Time (min)} {Break Time (min)} {Long Break Time (min)}'
usageInfoPlay = '$play [youtube url]'
smugEmoji = bot.get_emoji(974757534894284851)
youtube_dl.utils.bug_reports_message = lambda: ''

"""
Make sure argument list is all valid number types and converts data to integers

class ListConverter(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            # Converting i to a float before converting to an int because in the list all arguments are of string type
            for i in argument:
              print(i+': ' + str(type(i)))
              #int(float(i))
            return argument
        except:
            raise commands.BadArgument('Invalid command:\n Usage: ' + usageInfo)
"""

'''
Notes: It seems the way that python handles concurrency means that having two timers run at the same time will cause signifigant lag in timers, the timers will have to either be added sequentially or forked onto a speerate thread
'''
async def timer(reaction,state="NULL",timeMin=0):
  if(state == "NULL"): 
    return
  if(time == 0):
    return
  if(state == "POMO"):
    embed=nextcord.Embed(title='Pomdoro Timer', color=0x4cee11)
  elif(state == "BREAK"):
    embed=nextcord.Embed(title='Break Timer', color=0x4cee11)
    
  embed.add_field(name='________________', value="Start time: {}:00".format(timeMin), inline=False)
  # Create a new embed that we can use as a template to edit the other embed
  templatebed = embed
  embed.add_field(name='Time Remaining', value='20:00', inline=False)
  msg = await reaction.message.channel.send(embed=embed)

  # Code Modified From:
  # https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
  # TODO: MODIFY TIMER TO HANDLE POSSIBLE DELAYS
  timeSec = timeMin * 60
  while timeSec:
      if(state == "POMO"):
        editbed=nextcord.Embed(title='Pomdoro Timer', color=0x4cee11)
      elif(state == "BREAK"):
        ebitbed=nextcord.Embed(title='Break Timer', color=0x4cee11)
        editbed.add_field(name='________________', value="Start time: {}:00".format(timeMin), inline=False)
      mins, secs = divmod(timeSec, 60)
      timer = '{:02d}:{:02d}'.format(mins, secs)
      editbed.add_field(name='Time Remaining', value=timer, inline=False)
      await msg.edit(embed=editbed)
      await asyncio.sleep(1)
      timeSec -= 1
      
  return

  
  
  

async def buildSessionEmbed(numSession=5,pTime=20,bTime=5,lBTime=15,vc="NULL"):
  embed=nextcord.Embed(title="Pomodoro Session Setup", color=0xf41515)
  #embed.set_author(name="Pomodoro Bot")
  embed.add_field(name="Number of Sessions:", value=numSession, inline=True)
  embed.add_field(name="Pomodoro Time:", value="{} min".format(pTime), inline=True)
  embed.add_field(name="Break Time:", value="{} min".format(bTime), inline=True)
  embed.add_field(name="Long Break Time:", value="{} min".format(lBTime), inline=True)
  embed.set_footer(text="Connected to VC {}".format(vc))
  return embed

@bot.listen()
async def on_ready():
  print('We have logged in as smugbot')
  await bot.change_presence(status=nextcord.Status.idle,activity=game)


"""
@client.event
async def on_message(message):
  if message.author == bot.user:
    return

  if message.content.startswith(prefix + 'pomodoro'):
    embed = await buildSessionEmbed()
    msg = await message.channel.send(embed=embed)
    await msg.add_reaction("🍅")
  elif message.content.startswith(prefix + 'ping'):
    await message.channel.send('Pong')
"""




# Code snippet from https://github.com/Rapptz/discord.py/blob/master/examples/basic_voice.py
YTDL_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }

ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)


class YTDLSource(nextcord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
#End snippet





@bot.command(name='play', help='Plays a song from a specific youtube link')
async def play(ctx,*args) -> bool:
  
  if len(args) != 1:
    await ctx.send('Invalid command:\n Usage: ' + usageInfoPlay)
    return False

  # Add to a join function
  if not ctx.message.author.voice:
    await ctx.send('I would play the song...if you were in a voice channel ')
    return False

  channel = ctx.message.author.voice.channel
  await channel.connect()

  # Join function end
  
  url = args[0]
  await ctx.send('Downloading video...')
  meta = ytdl.extract_info(url, download=False)
  #print(meta)
  await ctx.send('Playing: ```{}```'.format( meta.get('title')))
  
  return True

@bot.command(name='leave', help='Make the bot leave the voice channel')
async def leave(ctx):
  clientVC = ctx.message.guild.voice_client
  if clientVC.is_connected():
    await clientVC.disconnect()
    return True
  ctx.send('Can\'t leave a voice channel I\'m not in')
  return False
  

@bot.command()
async def pomodoro(ctx,*args):
  # TODO: WRITE INTO OWN FUNCTION
  # Checks the number of args passed are valid in amount and int type
  if(len(args)>4):
    await ctx.send('Invalid command:\n Usage: ' + usageInfo)
    return
  try:
    # Converting i to a float before converting to an int because in the list all arguments are of string type
    args = [int(float(i)) for i in args]
  except:
    await ctx.send('Invalid command:\n Usage: ' + usageInfo)
    return

  
  #arguments = ', '.join([str(i) for i in args])
  #await ctx.send(f'{len(args)} arguments: {arguments}')

  
  if(len(args) == 0):
    embed = await buildSessionEmbed()
  elif(len(args) == 1):
    embed = await buildSessionEmbed(args[0])
  elif(len(args) == 2):
    embed = await buildSessionEmbed(args[0],args[1])
  elif(len(args) == 3):
    embed = await buildSessionEmbed(args[0],args[1],args[2])
  else:
    embed = await buildSessionEmbed(args[0],args[1],args[2],args[3])
    
  msg = await ctx.send(embed=embed)
  await msg.add_reaction("🍅")
  # TODO: ADD INTO OWN FUNCTION
  # Asks the user further questions to build the embed
  '''
  infoAmt = len(args)
  if(infoAmt) < 4):
    embed=discord.Embed(title='Session Incomplete', description='Choose a     reaction below to fill in necessary missing session info', color=0xf41515)
    newbed = embed
  newbed.add_field(name='Loading...', value=, inline=True)
  msg = await ctx.send(embed=newbed)
  while(infoAmt < 4):
    if(infoAmt == 0):
      sessionEM = embed
      sessionEM.add_field(name=Number of Sessions:, value=Recommended 4-5 Sessions, inline=True)
    await ctx.send(embed=sessionEM)
    await msg.add_reaction("")
  '''
  
  
@bot.listen()
async def on_reaction_add(reaction, user):
  if user != bot.user:
    if str(reaction.emoji) == "🍅":
      await reaction.message.channel.send('Starting Session!')
      #embed= nextcord.Embed(title='Starting Session', color=0x4cee11)
      #await reaction.message.channel.send(embed=embed)
      
      # TODO: Modify the embed timer to run on delta time
      # TODO: Add async protection if timer goes for too long
      # TODO: Add a session manager to handle sessions
      # Handles the pomodoro timer and embed timer
      task = asyncio.create_task(timer(reaction,"POMO",5))
      await asyncio.sleep(5*60)
      task.cancel()
      
      
      await reaction.message.channel.send('<@{pUser}> has finished their pomodoro'.format(pUser=str(user.id)))



bot.run(os.getenv('TOKEN'))
