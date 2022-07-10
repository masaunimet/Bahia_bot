import discord 
from discord.ext import commands
import youtube_dl
from urllib import parse,request
import re
import os
import math
import datetime
from random import random

class music(commands.Cog): 
    def __init__(self, client):
        self.client = client
        self.song_queue = {}
        self.actual_song =""
        self.actual_title = ""
        self.loop = False
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.YDL_OPTIONS = {'format': 'bestaudio'}

    @commands.command() 
    async def join(self,ctx): 
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel!")
        voice_channel = ctx.message.author.voice.channel 
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

    @commands.command() 
    async def disconnect(self,ctx):
        await ctx.voice_client.disconnect()

    @commands.command() 
    async def Meme_clip(self,ctx):
        await self.join(ctx)
        vc = ctx.voice_client
        if not vc.is_playing():
            num_d = len(os.listdir("./assets/Music"))
            random_num = (int) (random() * (num_d))
            vc = ctx.voice_client
            for index, file in enumerate(os.listdir("./assets/Music")):
                if index == random_num:
                    print(f"file: {file} , number: {index}")
                    vc.play(discord.FFmpegPCMAudio(executable="C:/Path_FFmpeg/ffmpeg.exe", source="./assets/Music/"+file))
        else:
            await ctx.send("wait until the bot isn't playing songs")

    @commands.command() 
    async def Meme_clip(self,ctx, random_num):
        await self.join(ctx)
        vc = ctx.voice_client
        if not vc.is_playing():
            vc = ctx.voice_client
            for index, file in enumerate(os.listdir("./assets/Music")):
                if index == int(random_num):
                    print(f"file: {file} , number: {index}")
                    vc.play(discord.FFmpegPCMAudio(executable="C:/Path_FFmpeg/ffmpeg.exe", source="./assets/Music/"+file))
        else:
            await ctx.send("wait until the bot isn't playing songs")
    
    @commands.command() 
    async def play(self,ctx,*, url:str):
        await self.join(ctx)
        vc = ctx.voice_client
        if url[:32] != "https://www.youtube.com/watch?v=" or url[:17] != "https://youtu.be/":
            trueurl = Search(url)
            
        else:
            if url.count < 30:
                trueurl = url[:43]
            else:
                 trueurl = url
        if vc.is_playing():
            await self.ListMusic(ctx,trueurl)
        else:
            with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                info = ydl.extract_info(url=trueurl, download=False)
                id = info["id"]
                url2 = info["formats"][0]['url']
                titulo = info['title']
                try: 
                    autor = info['creator']
                except:
                    autor = "???"
                ano = info['upload_date']
                duration = info['duration']
                view = "{:,}".format(info['view_count'])
                try:
                    like = "{:,}".format(info['like_count'])
                except:
                    like = "???"

                source = await discord.FFmpegOpusAudio.from_probe(url2,**self.FFMPEG_OPTIONS)
                self.actual_song = source
                self.actual_title = titulo
                vc.play(source,after=lambda x=None: self.PlayAfter(ctx,ctx.message.guild.id))
                print(f"playing: {titulo}")

                embed = discord.Embed(title=f"{titulo}",description="now playing...",
                timestamp=datetime.datetime.utcnow(),color=discord.Color.blue())
                embed.add_field(name="Created by: ",value=f"{autor}")
                embed.add_field(name="Year: ",value=f"{Years_Convertion(ano)}")
                embed.add_field(name="duration: ",value=f"{Number_Time(duration)}")
                embed.add_field(name="Views: ",value=f"{view}")
                embed.add_field(name="Likes: ",value=f"{like}")
                embed.set_thumbnail(url=f"https://img.youtube.com/vi/{id}/default.jpg")
                await ctx.send(embed=embed)
    
    async def ListMusic(self,ctx,url:str):
        with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url=url, download=False)
            id = info["id"]
            url2 = info["formats"][0]['url']
            titulo = info['title']
            try: 
                autor = info['creator']
            except:
                autor = "???"
            ano = info['upload_date']
            duration = info['duration']
            view = "{:,}".format(info['view_count'])
            try:
                like = "{:,}".format(info['like_count'])
            except:
                like = "???"

            source = await discord.FFmpegOpusAudio.from_probe(url2,**self.FFMPEG_OPTIONS)

        dictionary = {"Id": id,"Source": source,"Url":url2,"Title": titulo,
        "Autor":autor,"Year":ano,"Duration":duration,"View": view,"Like":like}

        guilt_id = ctx.message.guild.id
        if guilt_id in self.song_queue:
            self.song_queue[guilt_id].append(dictionary)
        else:
            self.song_queue[guilt_id] = [dictionary]
        
        await ctx.send("added to the list!")

        embed = discord.Embed(title=f"{titulo}",description="in queue...",
        timestamp=datetime.datetime.utcnow(),color=discord.Color.blue())
        embed.add_field(name="Created by: ",value=f"{autor}")
        embed.add_field(name="Year: ",value=f"{Years_Convertion(ano)}")
        embed.add_field(name="duration: ",value=f"{Number_Time(duration)}")
        embed.add_field(name="Views: ",value=f"{view}")
        embed.add_field(name="Likes: ",value=f"{like}")
        embed.set_thumbnail(url=f"https://img.youtube.com/vi/{id}/default.jpg")
        await ctx.send(embed=embed)
            
    def PlayAfter(self,ctx,discord_id):
        if not self.loop and (not self.song_queue == {} and self.song_queue[discord_id] !=[]):
            voice = ctx.guild.voice_client
            data = self.song_queue[discord_id].pop(0)
            id = data["Id"]
            titulo = data["Title"]
            self.actual_song= data["Source"]
            self.actual_title = titulo
            ctx.voice_client.play(data["Source"],after=lambda x=None:self.PlayAfter(ctx,ctx.message.guild.id))
            print(f"playing: {titulo}")
        
        elif self.loop:
            ctx.voice_client.play(self.actual_song,after=lambda x=None:self.PlayAfter(ctx,ctx.message.guild.id))
            print(f"playing: {self.actual_title}")

    @commands.command(name="queue")
    async def Queue(self,ctx):
        discord_id = ctx.message.guild.id
        titulos = []
        if not self.song_queue == {} and self.song_queue[discord_id] !=[]:
            for x in range(10):
                if len(self.song_queue[discord_id]) > x:
                    titulos.append(self.song_queue[discord_id][x]["Title"])
                if x == 0:
                    id = self.song_queue[discord_id][x]["Id"]
                    image =f"https://img.youtube.com/vi/{id}/default.jpg"
            
            embed = discord.Embed(title="List of songs",
            timestamp=datetime.datetime.utcnow(),color=discord.Color.blue())
            embed.add_field(name="Titles: ",value=List_Queue(titulos))
            embed.set_thumbnail(url=image)
            await ctx.send(embed=embed)

    @commands.command(name="loop") 
    async def Single_Loop(self,ctx):
        self.loop = not self.loop
        if not self.actual_song == "":
            if self.loop:
                await ctx.send("{} is looped!".format(self.actual_title))
            else:
                await ctx.send("{} is no more looped!".format(self.actual_title))
        else:
            if self.loop:
                await ctx.send("next song is going to be looped!")
            else:
                await ctx.send("next song is not going to be looped!")

    @commands.command() 
    async def pause(self,ctx):
        ctx.voice_client.pause()
        await ctx.send("Pause")

    @commands.command() 
    async def resume(self,ctx):
        ctx.voice_client.resume()
        await ctx.send("resume")

    @commands.command() 
    async def skip(self,ctx):
        ctx.voice_client.stop()
        await ctx.send("skip")


def setup(client):
        client.add_cog(music(client))

def Search(search):
    query_string = parse.urlencode({"search_query": search}) #convierte lo que puso el usuario en codigo url
    html_content = request.urlopen("http://www.youtube.com/results?"+query_string) #agarra la url y lo transforma en un documento html
    search_results=re.findall('watch\?v=(.{11})',html_content.read().decode('utf-8'))# crea un array con los id de los viddeos
    results = "https://www.youtube.com/watch?v="+search_results[0]
    return results

def Number_Time(num:int):
    hours = 0
    while num >= 3600:
        hours +=1
        num -=3600
    min = num/60
    sec = min - math.floor(min)
    if hours == 0:
        return f"{math.floor(min)}:{round(sec*60)}"
    else:
        return f"{hours}:{math.floor(min)}:{round(sec*60)}"
    
def Years_Convertion(message:str):
    year = message[:4]
    month = message[6:8]
    day = message[4:6]
    return f"{day}/{month}/{year}"

def List_Queue(titles):
    text =""
    for index,element in enumerate(titles):
        text += "{}. {}\n".format(index+1,element)
    return text

