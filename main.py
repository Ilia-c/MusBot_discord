import multiprocessing
import discord
import asyncio
import os.path
import os
from similar_text import similar_text
from discord.ext import commands
from discord_components import (
    Button,
    ButtonStyle,
    ComponentsBot,
)
from mutagen.mp3 import MP3
import random
from multiprocessing.pool import ThreadPool
from youtube_dl import YoutubeDL
import time
import re

Tocken = ''
FFmpeg_path = "E:/Документы и файлы/Музыка/Бот/1/bin/ffmpeg.exe"

Path_list = []
Groupe_list = []
Album_list = []
Treck_name_list = []


try:
    cpus = multiprocessing.cpu_count()
except:
    cpus = 2
print(cpus)
pool = ThreadPool(processes=cpus)

len_of_list_music = 100    # Максимальная длина очереди музыки
playback_queue = []        # Очередь музыки
chanel_id = None
channel_pr = None
id = []
stop_playing = False



YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}
YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist':'True', "extract_flat": True}
FFMPEG_OPTIONS_URL = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
FFMPEG_OPTIONS = {'options': '-vn'}

class MusicCog(commands.Cog):
    global id
    global stop_playing
    global playback_queue
    global chanel_id
    global FFmpeg_path
    global Path_list
    global Groupe_list
    global Album_list
    global Treck_name_list
    global FFMPEG_OPTIONS

    def __init__(self, Musbot):
        self.Musbot = Musbot
        self.First = True
        self.push_button_autor = None
        self.nextpl = False
        self.URL_link = ""
        self.PlayNow = ""
        self.voice = None
        self.repeat = False
        self.play_now_link = ""
        self.play_now_id = 0
        self.first = True
        self.URL_time = 0
        self.count_repeat = 0
        self.loop = 0 # 0 - нет цикла 1 - еденичный повтор 2 - непрерывный повтор


    @commands.command(name='pl', help='This command play the song')
    async def play(self, ctx, *, treck):
        global playback_queue
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global id
        global FFMPEG_OPTIONS
        counter = 0
        query = ""

        #voice_state = ctx.member.voice
        #print(voice_state)
        #if voice_state is None:
        #    return


        l = re.findall("(?P<url>https?://[^\s]+)", treck)
        if (l != []):
            print("Это ссылка")
            #l = "https://www.youtube.com/watch?v=tnRxocc7PpA"
            with YoutubeDL(YDL_OPTIONS) as ydl:
                info = ydl.extract_info(l[0], download=False)

            try:
                if (info['_type'] == "playlist"):
                    # Это плейлист
                    ydl = YoutubeDL({'outtmpl': '%(id)s%(ext)s', 'quiet': True, })
                    video = ""
                    result = ydl.extract_info(l[0], download=False)  # We just want to extract the info
                    if 'entries' in result:
                        video = result['entries']
                        for i, item in enumerate(video):
                            video = result['entries'][i]['webpage_url']
                            title = result['entries'][i]['title']
                            dur = result['entries'][i]['duration']
                            info = None
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(video, download=False)
                            URL = info['formats'][0]['url']
                            # URL_video_playlist.append(video)
                            playback_queue.append(["URL - " + str(title), URL, video, dur])

            except:
                print("Это ссылка на видео")
                URL = info['formats'][0]['url']
                title = info.get('title', info.get('id', 'video'))
                print(title)
                dur = info['duration']
                print(dur)
                self.URL_time = dur
                playback_queue.append(["URL - "+str(title), URL, l[0], dur])
                await self.play_order_music(ctx)
            await self.play_order_music(ctx)
        else:
            print("Это не ссылка")
            async_result = pool.apply_async(poisk, (treck, Treck_name_list, 70))
            Name, id = async_result.get()


            if (len(Name) > 1):
                Message = ""
                print(ctx.message.channel)
                for i in id:
                    counter+=1
                    Message +=  "\n" + f"{counter}. Исполнитель: \"" + Groupe_list[i] + "\" - Альбом: \"" + Album_list[i] + "\" - Песня: \"" +Treck_name_list[i] + "\""
                await self.print_message(Message, 0)
                return
            elif len(Name) == 1:
                query = Path_list[id[-1]]
            else:
                await self.print_message("Нет такой песни", 5, "Неверный ввод")
                return

            playback_queue.append([id[0], query])
            await self.play_order_music(ctx)

    # @commands.command()
    @commands.command(name='Ch', help='This command pauses the song')
    async def chose(self, ctx, *, Number, S=None):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global playback_queue
        global id
        query = ""
        if (Number.isdigit()):
            Number = int(Number)
            if (int(Number) <= len(id) and int(Number) > 0):
                query = Path_list[id[int(Number)-1]]
            else:
                await self.print_message("Нет такого номера песни", 5, "Неверный ввод")
                return
            playback_queue.append([id[int(Number)-1], query])
            await self.play_order_music(ctx)
        else:
            await self.print_message("Введите число", 5, "Неверный ввод")

    @commands.command()
    async def exit(self, ctx, S=None):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global playback_queue
        print("exit-1")
        self.First = True
        self.nextpl = False
        self.PlayNow = ""
        self.voice = None
        self.play_now_link = ""
        self.count_repeat = 0
        self.count_repeat_one = 0
        self.push_button_autor = None
        self.repeat = False
        self.Process = None
        self.time_len = ""
        self.loop = 0       # 0 - нет цикла 1 - еденичный повтор 2 - непрерывный повтор
        playback_queue = []
        if (S == None):
            await ctx.voice_client.disconnect()
        else:
            print("exit-2")
            vc = discord.utils.get(self.Musbot.voice_clients, guild=ctx.guild)
            print(vc)
            await vc.disconnect()
        #await self.print_message("", 1)

    @commands.command()
    async def pause(self, ctx, S=None):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        if (S == None):
            ctx.voice_client.pause()
        else:
            ctx.pause()
        await self.print_message(self.time_len, 2, "*Пауза -* ⏸️")

    @commands.command()
    async def resume(self, ctx, S=None):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        if (S == None):
            ctx.voice_client.resume()
        else:
            ctx.resume()
        await self.print_message(self.time_len, 2, "Сейчас играет: ")


    @commands.command(name='next', help='This command play next song')
    async def next(self, ctx, S=None, userid = None):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global playback_queue
        self.repeat = False
        if (len(playback_queue) >= 1) or (self.loop == 1 or self.loop == 2):
            if (S == None):
                ctx.voice_client.stop()
                self.nextpl = True
                await self.play_order_music(ctx)
            else:
                ctx.stop()
                self.nextpl = True
                await self.play_order_music(userid, 1)
        else:
            await self.print_message("", 5, "Очередь пуста")

    @commands.command(name='Clear_message', help='This command clear queue song')
    async def clear(self, ctx, *, Number):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        if ctx.channel.id != chanel_id:
            try:
                await ctx.channel.purge(limit=int(Number)+1)
            except:
                return
        else:
            await ctx.channel.purge(limit=1)

    @commands.command(name='clearAll', help='This command clear queue song')
    async def clear_all(self, ctx):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global playback_queue
        playback_queue = []
        await self.print_message("", 5, "Очередь отчищена")

    @commands.command(name='R_treck', help='This command clear treck in list')
    async def remove_treck_in_list(self, ctx, *, Number):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global playback_queue
        if len(playback_queue)>=int(Number)+1:
            playback_queue.pop(int(Number)-1)
            await self.print_message("", 5, "Трек удален")

    @commands.command()
    async def help(self, ctx):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global channel_pr
        global chanel_id
        if chanel_id is None:
            chanel_id = ctx.channel.id
            channel_pr = self.Musbot.get_channel(chanel_id)
        else:
            await channel_pr.purge(limit=3)
        await self.print_message("", 1)

    @commands.command()
    async def play_order_music(self, ctx, S=None):
        global Path_list
        global Groupe_list
        global FFmpeg_path
        global FFMPEG_OPTIONS
        global Album_list
        global Treck_name_list
        global playback_queue
        global stop_playing
        event = asyncio.Event()
        event.set()
        while True:
            await event.wait()
            event.clear()
            print(self.loop)
            if (len(playback_queue) != 0) or (self.loop == 1 or self.loop == 2):
                print("loop = " + str(self.loop))
                if ((self.count_repeat >= 1)):
                    self.count_repeat = 0
                    if self.loop == 1:
                        print("rerol")
                        self.loop = 0
                        await self.print_message(self.time_len, 2, "Сейчас играет:")

                if stop_playing == True:
                    stop_playing = False
                    break

                voice_channel = None
                autor = None
                print(self.push_button_autor)
                if S == None:
                    voice_channel = ctx.author.voice.channel
                    autor = ctx.author.nick
                    #print(ctx.author.nick)
                else:
                    voice_channel = ctx.voice.channel
                    autor = ctx.nick
                    #print(ctx.nick)

                if voice_channel != None:
                    vc = discord.utils.get(Musbot.voice_clients, guild=voice_channel.guild)
                    if not vc:
                        vc = await voice_channel.connect()

                    if (vc.is_playing()):
                        if (self.nextpl):
                            self.nextpl = False
                        else:
                            await self.print_message("", 5, "Добалено в очередь")
                        return

                    if self.loop == 1 or self.loop == 2 or self.repeat is True:
                        self.count_repeat += 1
                        print("Запуск лупа")
                        print(self.play_now_id)
                        urlstr = re.findall("(?P<url>https?://[^\s]+)", str(self.play_now_id))
                        print(urlstr)
                        if urlstr == []:
                            vc.play(discord.FFmpegPCMAudio(executable=FFmpeg_path, source=self.play_now_link, **FFMPEG_OPTIONS), after=lambda e: event.set())
                        else:
                            vc.play(discord.FFmpegPCMAudio(executable=FFmpeg_path, source=self.play_now_link, **FFMPEG_OPTIONS_URL), after=lambda e: event.set())
                        if self.repeat:
                            self.repeat = False
                            self.loop = 0
                            await self.print_message(self.time_len, 2, "Сейчас играет:")
                    else:
                        self.count_repeat = 0
                        print("Запуск следующей")

                        url_title = str(playback_queue[0][0])
                        print(url_title)
                        print(url_title[:3])
                        if (url_title[:3] == "URL"):
                            vc.play(discord.FFmpegPCMAudio(executable=FFmpeg_path,source=playback_queue[0][1], **FFMPEG_OPTIONS_URL),after=lambda e: event.set())
                            print(playback_queue)
                            self.URL_time = playback_queue[0][3]
                            if (self.URL_time != 0):
                                sec = self.URL_time % (24*3600)
                                hour = str(int(sec//3600))
                                sec = sec % 3600
                                minute = str(int(sec // 60))
                                sec = str(int(sec % 60))

                                if (int(hour) < 10):
                                    hour="0"+hour
                                if (int(minute) < 10):
                                    minute="0"+minute
                                if (int(sec) < 10):
                                    sec="0"+sec
                                self.time_len = "\nПродолжительность: "+ hour +":"+ minute +":"+ sec + "\nИнициатор: " + autor
                            else:
                                self.time_len = "\nИграет трансляция" + "\nИнициатор: " + autor
                            self.voice = vc
                            self.play_now_id = playback_queue[0][2]
                            self.play_now_link = playback_queue[0][1]
                            self.PlayNow = url_title
                        else:
                            print(playback_queue[0][1])
                            vc.play(discord.FFmpegPCMAudio(executable=FFmpeg_path, source=playback_queue[0][1], **FFMPEG_OPTIONS), after=lambda e: event.set())
                            audio = MP3(playback_queue[0][1])
                            print("Start")
                            sec = audio.info.length % (24*3600)
                            hour = str(int(sec//3600))
                            sec = sec % 3600
                            minute = str(int(sec // 60))
                            sec = str(int(sec % 60))

                            if (int(hour) < 10):
                                hour="0"+hour
                            if (int(minute) < 10):
                                minute="0"+minute
                            if (int(sec) < 10):
                                sec="0"+sec
                            self.time_len = "\nПродолжительность: "+ hour +":"+ minute +":"+ sec + "\nПереключил: " + autor

                            self.voice = vc
                            self.play_now_id = playback_queue[0][0]
                            self.play_now_link = playback_queue[0][1]
                            self.PlayNow = "Исполнитель: \"" + Groupe_list[playback_queue[0][0]] + "\" - Альбом: \"" + Album_list[playback_queue[0][0]] + "\" - Песня: \"" +Treck_name_list[playback_queue[0][0]] + "\""

                        await self.print_message(self.time_len, 2, "Сейчас играет:")
                        playback_queue.pop(0)
                else:
                    await self.print_message(str(ctx.author.name) + "is not in a channel", 4)
            else:
                self.First = True
                self.push_button_autor = None
                self.nextpl = False
                self.URL_link = ""
                self.PlayNow = ""
                self.voice = None
                self.repeat = False
                self.play_now_link = ""
                self.play_now_id = 0
                self.URL_time = 0
                self.count_repeat = 0
                self.loop = 0  # 0 - нет цикла 1 - еденичный повтор 2 - непрерывный повтор
                playback_queue = []
                await self.print_message("", 2)
                time.sleep(10)
                if not vc.is_playing():
                    if voice_channel != None:
                        await vc.disconnect()

    @commands.command()
    async def print_message(self, Message, Page, Title = None):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global channel_pr
        global playback_queue
        global id
        if self.first:
            self.first = False
        else:
            await channel_pr.purge(limit=5)
        playNow = self.PlayNow + Message
        if (Page == 2):
            if (self.PlayNow == ""):
                playNow = ""
                Title = "Сейчас ничего не играет"

        listpotentplay = discord.Embed(
            title="Список найденных песен:",
            description=Message,
            colour=discord.Colour.orange()
        )
        help = discord.Embed(
            title="Комманды:",
            description="1. !help - Помощь \n2. !pl Название трека или UR - запуск музыки\n3. "
                        "!Ch Номер песни из списка (после 2ой комманды) \n4. !pause - Пауза\n5. !resume - Продолжить\n6. "
                        "!next - включит следующий трек \n7. !R_treck номер - Удалит выбранный трек из списка воспроизведения\n8. !clearAll - Отчистить очередь воспроизведения\n9. !exit - Отключить бота\n10. !Ch_chenal - поменять канал бота\n11. !Clear_message количество - Удалить сообщения",

            colour=discord.Colour.orange()
        )
        Paly_now = discord.Embed(
            title=Title,
            description=playNow,
            colour=discord.Colour.orange()
        )
        Order_music = discord.Embed(
            title="Список очереди:",
            description=playNow,
            colour=discord.Colour.orange()
        )
        Error = discord.Embed(
            title="Ошибка:",
            description=Message,
            colour=discord.Colour.red()
        )
        other = discord.Embed(
            title=Title,
            description=Message,
            colour=discord.Colour.red()
        )
        pages = [listpotentplay, help, Paly_now, Order_music, Error, other]
        await channel_pr.send(embed=pages[Page])

        if Page == 0:
            button = []
            b_2 = []
            count = 0
            number = 0
            in_gor = int(len(id)/2)
            #print(in_gor)
            for i in range(len(id)):
                if (count>=5):
                    count = 0
                    number += 1
                    button.append(b_2)
                    b_2 = []
                b_2.append(Button(style=ButtonStyle.gray, label=str(i+1), custom_id="b_"+str(i+1)))
                count += 1
            button.append(b_2)
            b_2 = []
            b_2.append(Button(style=ButtonStyle.gray, label="", emoji="⬅", custom_id="last"))
            button.append(b_2)
            await channel_pr.send(components=button)
        elif Page == 1:
            await channel_pr.send(components=[Button(style=ButtonStyle.gray, label="", emoji="⬅", custom_id="last")])
        elif Page == 2:
            Button_1 =Button(style=ButtonStyle.gray, label="", emoji="⏹", custom_id="button_stop")
            Button_2 =Button(style=ButtonStyle.gray, label="", emoji="⏸", custom_id="button_pause")
            Button_3 =Button(style=ButtonStyle.gray, label="", emoji="▶", custom_id="button_play")
            Button_4 =Button(style=ButtonStyle.gray, label="", emoji="⏭", custom_id="button_next")
            Button_5 =Button(style=ButtonStyle.gray, label="", emoji="🎵", custom_id="button_play_my_list")

            Button_6 = None
            Button_7 = None
            if (self.loop == 1):
                Button_6 = Button(style=ButtonStyle.red, label="", emoji="🔁", custom_id="button_repeat")
                Button_7 = Button(style=ButtonStyle.gray, label="", emoji="🔂", custom_id="button_loop_repeat")
            elif self.loop == 2:
                Button_6 = Button(style=ButtonStyle.gray, label="", emoji="🔁", custom_id="button_repeat")
                Button_7 = Button(style=ButtonStyle.red, label="", emoji="🔂", custom_id="button_loop_repeat")
            else:
                Button_6 = Button(style=ButtonStyle.gray, label="", emoji="🔁", custom_id="button_repeat")
                Button_7 = Button(style=ButtonStyle.gray, label="", emoji="🔂", custom_id="button_loop_repeat")

            Button_8 =Button(style=ButtonStyle.gray, label="", emoji="♥", custom_id="button_like")
            Button_9 =Button(style=ButtonStyle.gray, label="", emoji="❓", custom_id="button_help")
            Button_10 =Button(style=ButtonStyle.gray, label="", emoji="🎶", custom_id="button_playlist")

            await channel_pr.send(components=[[
                Button_1,
                Button_2,
                Button_3,
                Button_4,
                Button_5],
                [
                Button_6,
                Button_7,
                Button_8,
                Button_9,
                Button_10
                ]])
        elif (Page == 3):
            await channel_pr.send(components=[[Button(style=ButtonStyle.gray, label="", emoji="⬅", custom_id="last")]])
        elif (Page == 4):
            await channel_pr.send(components=[Button(style=ButtonStyle.gray, label="", emoji="⬅", custom_id="last")])
        else:
            await channel_pr.send(components=[[Button(style=ButtonStyle.gray, label="", emoji="⬅", custom_id="last"), Button(style=ButtonStyle.gray, label="", emoji="❌", custom_id="clear_order_play"), Button(style=ButtonStyle.gray, label="", emoji="🔀", custom_id="rerol")]])

    async def like_reakt(self, res, user, play_now_link):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        s = -1
        lines = []
        with open(str(user)+".data", "r") as file:
            lines = file.readlines()
            for i in range(len(lines)):
                if re.findall("(?P<url>https?://[^\s]+)", lines[i]) == []:
                    index_l = int(lines[i])
                    if index_l == self.play_now_id:
                        s = i
                else:
                    print(self.play_now_id)
                    print(lines[i])
                    if str(lines[i]) == str(self.play_now_id)+"\n":
                        print("Оно")
                        s = i
        if s != -1:
            del lines[s]
            with open(str(user)+".data", "w") as file:
                file.writelines(lines)
                embed = discord.Embed(title='Трек удален из избранного')
                await res.respond(embed=embed, ephemeral=True)
                return
        f = open(str(res.user)+".data", "a")
        f.write(str(self.play_now_id)+"\n")
        f.close()
        embed = discord.Embed(title='Трек добавлен в избранное')
        await res.respond(embed=embed, ephemeral=True)
        return


    @commands.Cog.listener()
    async def on_button_click(self, res):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global playback_queue
        global id
        self.push_button_autor = res.user.nick
        decision_type = res.component.custom_id
        if decision_type == 'button_stop':
            print(self.PlayNow)
            if (self.PlayNow != ""):
                await self.exit(self.voice, 1)
            else:
                await res.respond(type=6)
            return
        elif decision_type == 'button_pause':
            if self.PlayNow == "":
                await res.respond(type=6)
                return
            await self.pause(self.voice, 1)
            return
        elif decision_type == 'button_play':
            if self.PlayNow == "":
                await res.respond(type=6)
                return
            await self.resume(self.voice, 1)
            return
        elif decision_type == 'button_next':
            if (self.PlayNow != ""):
                if self.loop == 1 or self.loop == 2:
                    await res.respond(type=6)
                await self.next(self.voice, 1, res.user)
            else:
                await res.respond(type=6)
            return
        elif decision_type == 'clear_order_play':
            playback_queue = []
            await self.print_message("Очередь пуста", 5, "В очереди:")
            return
        elif decision_type == 'button_like':
            if self.PlayNow != "":
                check_file = os.path.exists(str(res.user)+".data")
                if (check_file):
                    task = asyncio.create_task(self.like_reakt(res, res.user, self.play_now_link))
                else:
                    file = open(str(res.user)+".data", "w")
                    file.write(str(self.play_now_id))
                    file.close()
                    embed = discord.Embed(title='Трек добавлен в избранное')
                    await res.respond(embed=embed, ephemeral=True)
            else:
                await res.respond(type=6)
        elif decision_type == 'button_repeat':
            if self.PlayNow == "":
                await res.respond(type=6)
                return
            else:
                if self.loop == 1:
                    self.repeat = False
                    self.loop = 0
                    self.count_repeat = 0
                else:
                    print("repeat one - 1")
                    self.loop = 1
                    self.repeat = True
                    #self.count_repeat += 1
                await self.print_message(self.time_len, 2, "Сейчас играет:")
            return
        elif decision_type == 'button_loop_repeat':
            if self.PlayNow == "":
                await res.respond(type=6)
                return
            else:
                if self.loop == 2:
                    self.loop = 0
                else:
                    self.loop = 2
                await self.print_message(self.time_len, 2, "Сейчас играет:")
            return
        elif decision_type == 'button_help':
            await self.print_message("", 1)
            return
        elif decision_type == 'rerol':
            if self.PlayNow == "":
                await self.print_message("", 5, "Очередь пуста")
                return
            random.shuffle(playback_queue)

            mes = ""
            for i in range(len(playback_queue)):
                url_title = str(playback_queue[i][0])
                if (url_title[:3] == "URL"):
                    mes += str(i+1)+". "+url_title + " \n"
                else:
                    mes += str(i + 1) + ". Исполнитель: \"" + Groupe_list[playback_queue[i][0]] + "\" - Альбом: \"" + \
                       Album_list[playback_queue[i][0]] + "\" - Песня: \"" + Treck_name_list[
                           playback_queue[i][0]] + "\" \n"
            if mes == "":
                mes = "Очередь пуста"
            await self.print_message(mes, 5, "В очереди:")
            return
        elif decision_type == 'last':
            if (self.PlayNow == ""):
                await self.print_message("", 2, "Сейчас играет:")
            else:
                await self.print_message(self.time_len, 2, "Сейчас играет:")
            return
        elif decision_type == 'button_play_my_list':
            check_file = os.path.exists(str(res.user) + ".data")
            if (check_file):
                playback_queue = []
                with open(str(res.user) + ".data", "r") as file:
                    lines = file.readlines()
                    for i in range(len(lines)):
                        if re.findall("(?P<url>https?://[^\s]+)", lines[i]) == []:
                            index = int(lines[i])
                            playback_queue.append([index, Path_list[index]])
                        else:
                            link = str(lines[i])
                            with YoutubeDL(YDL_OPTIONS) as ydl:
                                info = ydl.extract_info(link, download=False)
                            URL = info['formats'][0]['url']
                            title = info.get('title', info.get('id', 'video'))
                            dur = info['duration']
                            self.URL_time = dur
                            playback_queue.append(["URL - " + str(title), URL, link, dur])
                if (self.PlayNow == ""):
                    await self.play_order_music(res.user, 1)
                else:
                    embed = discord.Embed(title='Ваш плейцлист в очереди')
                    await res.respond(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(title='Ваш плейлист пуст')
                await res.respond(embed=embed, ephemeral=True)

        elif decision_type == 'button_playlist':
            mes = ""
            for i in range(len(playback_queue)):
                url_title = str(playback_queue[i][0])
                if (url_title[:3] == "URL"):
                    mes += str(i+1)+". "+url_title+ " \n"
                else:
                    mes += str(i+1)+". Исполнитель: \"" + Groupe_list[playback_queue[i][0]] + "\" - Альбом: \"" + \
                               Album_list[playback_queue[i][0]] + "\" - Песня: \"" + Treck_name_list[
                                   playback_queue[i][0]] + "\" \n"
            if mes == "":
                mes = "Очередь пуста"
            #print(mes)
            await self.print_message(mes, 5, "В очереди:")

        for i in range(len(id)):
            if (decision_type == "b_"+str(i+1)):
                #print(i+1)
                query = Path_list[id[int(i+1) - 1]]
                playback_queue.append([id[int(i+1) - 1], query])
                await self.play_order_music(res.user, 1)
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global chanel_id
        if message.author != self.Musbot.user:
            if message.channel.id == chanel_id:
                if (message.content[:1] != "!" or message.content[:1] != "!"):
                    ctx = await self.Musbot.get_context(message)
                    await ctx.channel.purge(limit=1)

    @commands.Cog.listener()
    async def on_ready(self):
        global Path_list
        global Groupe_list
        global Album_list
        global Treck_name_list
        global chanel_id
        global channel_pr
        print(f'Logged in as {Musbot.user} (ID: {Musbot.user.id})')
        print('------')
        if chanel_id is None:
            return
        else:
            channel_pr = self.Musbot.get_channel(chanel_id)
            await channel_pr.purge(limit=100)
            await self.print_message("", 1)

    @commands.command(name='Ch_chenal', help='This command play the song')
    async def Сhenal_chose(self, ctx):
        global chanel_id
        global channel_pr
        if chanel_id is not None:
            await channel_pr.purge(limit=5)
        chanel_id = ctx.channel.id
        channel_pr = self.Musbot.get_channel(chanel_id)
        await self.print_message("", 1)

def poisk(input, base, procent):
    global Path_list
    global Groupe_list
    global Album_list
    global Treck_name_list
    v=[]
    id = []
    counter = 0
    for z in base:
        if (similar_text(z, input)) > procent:
            v.append(z)
            id.append(counter)
        counter += 1
        print(counter)
    return v, id


def parser(Path_to_folder):
    global Path_list
    global Groupe_list
    global Album_list
    global Treck_name_list
    os.chdir(Path_to_folder)
    print(os.getcwd())
    for Performers in os.listdir():
        if os.path.isdir(Performers):
            i = Performers
            os.chdir(i)
            for Albom in os.listdir():
                if os.path.isdir(Albom):
                    Albom_str = Albom[Albom.rfind("-") + 2:]
                    os.chdir(Albom)
                    for Treck in os.listdir():
                        if Treck.endswith('.mp3'):
                            Groupe_list.append(Performers)
                            Album_list.append(Albom_str)
                            Treck_name_list.append(Treck[Treck.find(".") + 2: Treck.rfind(".")])
                            Path_list.append(os.path.abspath(Treck))
                            #Path_list.append(os.path.relpath(Treck, start=os.curdir))
                            #Treck
                            #print(os.path.relpath(os.path.abspath(Treck)))

                    os.chdir("..")
            os.chdir("..")
    os.chdir("..")
    os.chdir("Плейлисты")
    print(len(Groupe_list))
    print(len(Album_list))
    print(len(Treck_name_list))
    print(len(Path_list))
   # return Groupe_list, Album_list, Treck_name_list, Path_list



parser("Исполнители")

Musbot = ComponentsBot(command_prefix="!", help_command=None)
Musbot.add_cog(MusicCog(Musbot))
Musbot.run(Tocken)