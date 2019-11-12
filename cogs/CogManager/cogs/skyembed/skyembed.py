from discord.ext import commands
import discord
import random
import re
from redbot.core import Config, commands, checks


colors = {
  'DEFAULT': 0x000000,
  'WHITE': 0xFFFFFF,
  'AQUA': 0x1ABC9C,
  'GREEN': 0x2ECC71,
  'BLUE': 0x3498DB,
  'PURPLE': 0x9B59B6,
  'LUMINOUS_VIVID_PINK': 0xE91E63,
  'GOLD': 0xF1C40F,
  'ORANGE': 0xE67E22,
  'RED': 0xE74C3C,
  'GREY': 0x95A5A6,
  'NAVY': 0x34495E,
  'DARK_AQUA': 0x11806A,
  'DARK_GREEN': 0x1F8B4C,
  'DARK_BLUE': 0x206694,
  'DARK_PURPLE': 0x71368A,
  'DARK_VIVID_PINK': 0xAD1457,
  'DARK_GOLD': 0xC27C0E,
  'DARK_ORANGE': 0xA84300,
  'DARK_RED': 0x992D22,
  'DARK_GREY': 0x979C9F,
  'DARKER_GREY': 0x7F8C8D,
  'LIGHT_GREY': 0xBCC0C0,
  'DARK_NAVY': 0x2C3E50,
  'BLURPLE': 0x7289DA,
  'GREYPLE': 0x99AAB5,
  'DARK_BUT_NOT_BLACK': 0x2C2F33,
  'NOT_QUITE_BLACK': 0x23272A
}

bot = commands.Bot
BaseCog = getattr(commands, "Cog", object)
listener = getattr(commands.Cog, "listener", None) 
if listener is None:
  
    def listener(name=None):
        return lambda x: x
    
class Skyembed(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        


    
  #  
#    async def on_message(self, message):
#  #   if guild:
#            path = "chatlogs/{}.txt".format(guild.id)  
 #           with open(path, 'a+') as f:
 #               print("{0.timestamp} : {0.author.name} : {0.content}".format(message), file=f)
   #     await bot.process_commands(message)
    @listener()
    async def on_message(client):
        filename = "allmessages_logs.txt"
        attachments = message.attachments
        links=[]
        for item in attachments:
            links += item['url']
        linktext="".join(links)
        text = str(message.author)+","+str(message.author.id)+","+str(message.channel)+","+str(message.content)+","+str(message.timestamp)+","+str(linktext)+"\n"
        with open(filename,"a+",encoding="utf-8") as file:
            file.write(text)
    


    @commands.command(
        name='sembed',
        description='The embed command',
    )
    async def embed_command(self, ctx):

        # Defined check function  
        def check(ms):        
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

         #title
        await ctx.send(content='What would you like the title to be?')

        # Wait for a response and get the title
        msg = await self.bot.wait_for('message', check=check)
        title = msg.content # Set the title

        # content
        await ctx.send(content='What would you like the Description to be?')
        msg = await self.bot.wait_for('message', check=check)
        desc = msg.content

        # make and send it
        msg = await ctx.send(content='Now generating the embed...')

        color_list = [c for c in colors.values()]
        # Convert
        # random

        embed = discord.Embed(
            title=title,
            description=desc,
            color=random.choice(color_list)
        )
        # thumbnail to be the bot's pfp
        embed.set_thumbnail(url=self.bot.user.avatar_url)

        # user
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url
        )

        await msg.edit(
            embed=embed,
            content=None
        )
        
        
        

        return
        
        
       

def setup(bot):
    bot.add_cog(Skyembed(Bot))
