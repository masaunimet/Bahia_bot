import music
import discord
from discord.ext import commands
import datetime
import os
from dotenv import load_dotenv

servers ={}

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
bot=commands.Bot(command_prefix="<<", description="esto es un bot prueba")
intends = discord.Intents.all()
cogs = [music]

for i in range(len(cogs)):
    cogs[i].setup(bot)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("pong")

@bot.command(name="add")
async def sum(ctx, num1: int,num2: int):
    await ctx.send(num1 + num2)

@bot.command(name="prueba")
async def info(ctx):
    embed =  discord.Embed(title=f"{ctx.guild.name}",description="asasasasas",
    timestamp=datetime.datetime.utcnow(),color=discord.Color.blue())
    embed.add_field(name="server created at",value=f"{ctx.guild.created_at}")
    embed.add_field(name="server owner: ",value=f"{ctx.guild.owner}")
    embed.add_field(name="Server region: ",value=f"{ctx.guild.region}")
    embed.add_field(name="Server Id: ", value=f"{ctx.guild.id}")
    embed.set_thumbnail(url="http://assets.stickpng.com/images/5848152fcef1014c0b5e4967.png")
    await ctx.send(embed=embed)


@bot.command(name="youtube")
async def youtube(ctx,*,search):
    await ctx.send(music.Search(search))

@bot.command(name="blw")
async def Black_List_Words(ctx):
    message =""
    embed =  discord.Embed(title="Bad Words",
    timestamp=datetime.datetime.utcnow(),color=discord.Color.blue())
    for index in range(10):
        if(len(servers[ctx.guild.id]["black_list_words"])>index):
            message += "{}. {}\n".format(index+1,servers[ctx.guild.id]["black_list_words"][index]["word"])
    embed.add_field(name="List ",value=message)
    await ctx.send(embed=embed)

@bot.command(name="ablw")
async def Add_Black_List_Words(ctx,*,word):
    if ctx.author.guild_permissions.administrator:
        word = word.replace(" ","")
        lista = word.rsplit(",")
        continua = True
        for index, content in enumerate(lista):
            if index == 0:
                continue
            else:
                if not (content.endswith(">") and content.startswith("<#")):
                    continua = False

        if len(lista) == 1 and continua:
            servers[ctx.message.guild.id]["black_list_words"].append({

                "word": word,
                "channels": ["all"]
            })

            await ctx.send("{} was added to the list!".format(word))
        elif continua:
            servers[ctx.message.guild.id]["black_list_words"].append({

                "word": lista[0],
                "channels": lista
            })
            servers[ctx.message.guild.id]["black_list_words"][-1]["channels"].pop(0)
            temp =servers[ctx.message.guild.id]["black_list_words"][-1]["channels"][-1]
            temp2 = temp[2:-1]
            servers[ctx.message.guild.id]["black_list_words"][-1]["channels"][-1] = temp2

            await ctx.send("{} was added to the list!".format(servers[ctx.message.guild.id]["black_list_words"][-1]["word"]))
        else:
            await ctx.send("You have to put the channels with the # symbol")
    else:
        await ctx.send("You don't have the administration role for this")

@bot.command(name="blp")
async def Black_List_People(ctx):
    message =""
    embed =  discord.Embed(title="Bad People",
    timestamp=datetime.datetime.utcnow(),color=discord.Color.blue())
    for index in range(10):
        if(len(servers[ctx.guild.id]["black_list_people"])>index):
            message += "{}. {}\n".format(index+1,servers[ctx.guild.id]["black_list_people"][index]["name"])
    embed.add_field(name="List ",value=message)
    await ctx.send(embed=embed)

#Events
@bot.event
async def on_message(message):

    if(message.author.bot==False):

        guilt_id = message.guild.id
        if not guilt_id in servers:
            servers[guilt_id] = {

                "name":message.guild.name,
                "black_list_people":[],
                "black_list_words":[]
            }
        
        else:
            one_bad_word = False
            found = False
            message_temp = message.content.upper()
            for words in servers[guilt_id]["black_list_words"]:

                if one_bad_word:
                    break

                for number_channels in words["channels"]:

                    if (not message_temp.find(words["word"].upper()) ==-1) and (number_channels== "all" or  str(message.channel.id) == number_channels):
                        await message.delete()
                        await message.channel.send("you can't say that")
                        one_bad_word = True
                        for user in servers[guilt_id]["black_list_people"]:

                            if user["name"] == message.author.name:

                                user["reasons"].append(message.content)
                                found = True
                        
                        if not found:

                            servers[guilt_id]["black_list_people"].append({

                                "name": message.author.name,
                                "reasons":[message.content]
                            })

                        break
    await bot.process_commands(message)

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.dnd,activity=discord.CustomActivity(name="nothing"))
    print("I'm ready")

bot.run(TOKEN)