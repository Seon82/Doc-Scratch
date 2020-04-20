import discord
from discord.ext import commands, tasks
import asyncio
import random
import json
import re
import os
import time
from music_loader import get_music
from pxls_image import get_progress
from wiki_search import get_wiki

## Global variables
with open('replies') as f:
    REPLIES = json.load(f)

DEFAULT_CHANNEL = 0

VARS = {}

KEYWORDS = [
[("lord english", "caliborn", "lord of time"), ("He who is already here shall come when this Universe ends.","Nobody can outrun my master.")],
[("time lord", "the doctor"), ("My master is the one and only Lord of Time.",)],
[("honk",), ("http://tiny.cc/hOnK","hOnK")],
[("hussie",), ("https://imgur.com/ZMszE75","https://imgur.com/tmGONPE")],
[("the mayor",), ("I must admit, even I am quite fond of him.",)],
[("lil cal",), ("The poor thing, treated like nothing more than a puppet.", "He is already here.")],
[(r"\bcal\b",), ("Such familiarity towards my master is quite insulting.", "You shall pay your irreverence with your blood.", "https://imgur.com/ceGQm3g")],
[("sucker",),("Please refrain from such vulgarity in my home.",)],
[(r"\bdoc\?",), ("Yes?", "I am listening.", "I am listening.\nI am always listening.", "I already know what you shall say, but by all means, go ahead.")],
[("8 ball", "8-ball", "cue ball"), ("https://imgur.com/y9XQ0lB", "I have always found the shape of these magic cue balls quite dashing.", "I believe the sphere to be the shape closest to perfection.")],
[("good night doc", "good night, doc"), ("I do not sleep, but thank you.\nGood night, dear guest.", "Feel free to have a last candy before heading to bed.", "Thank you, but I do not need sleep.\nI shall prepare you a cup of tea before you head to bed.")],
[("good night",), ("Good night, dear guest.", "Feel free to take a last candy before heading to bed.", "Please, help yourself to a cup of tea going to bed.", "If you want a bedtime story, do not hesitate.\After all, it is what one can expect from their host.", "Good night. Do not forget to look up at the clouds.", "Tired already? You humans have the weakest constitution.","Good night. I shall be glad to tell you more stories tomorrow, when you are refreshed.")],
[(r"\btick\b",), ("Tock.",)]
]

## Creating bot

prefix = "!"
bot = commands.Bot(command_prefix=prefix)

## Functions

def generate_story():
    global REPLIES
    phrases_to_use = random.choices(REPLIES, k = random.randint(50,70))
    story = [x for phrase in phrases_to_use for x in phrase.split('\n')]
    return story

async def tell_story(channel):
    global VARS
    story = generate_story()
    message = story.pop()
    while story!=[] and not VARS[channel.id]['stop']:
            await channel.send(message)
            sleep_time = int(random.uniform(2,7) + len(message)/30)
            with channel.typing():
                i = 0
                while i<sleep_time and not VARS[channel.id]['stop']:
                    await asyncio.sleep(1)
                    i+=1
                message = story.pop(0)
    message = random.choice(["Fine. You are, after all, my guest.", "I hope I was able to entertain you.", "As a perfect host, I shall oblige."])
    await channel.send(message)


def get_answer(message):
    global KEYWORDS
    message_content = message.content.lower()
    for keywords_list, answers_list in KEYWORDS:
        for keyword in keywords_list:
            if re.search(keyword, message_content):
                return random.choice(answers_list)


def init_vars(channel_id):
    global VARS
    VARS[channel_id] = {'stop':False,'num_stops':0, 'telling_story':False}


## Events
@bot.event
async def on_ready():
    print("Everything's all ready to go~")


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    ctx = await bot.get_context(message)
    if message.author != bot.user and not ctx.valid:
        if any(x in message.content.lower() for x in ("thank you", "thanks")) and\
        [x async for x in message.channel.history(limit=2)][1].author == bot.user:
            await message.channel.send("You are most welcome.")
        else:
            answer = get_answer(message)
            if answer:
                await message.channel.send(answer)


## Tasks


## Commands

@bot.command()
async def story(ctx):
    '''I shall be glad to tell you a story. It is the duty of a good host'''
    global VARS
    if ctx.channel.id not in VARS:
        init_vars(ctx.channel.id)
    if not VARS[ctx.channel.id]['telling_story']:
        VARS[ctx.channel.id]['stop'] = False
        VARS[ctx.channel.id]['telling_story'] = True
        await tell_story(ctx.channel)

@bot.command(aliases = ['stfu'])
async def stop(ctx):
    '''A useless command'''
    global VARS
    if not VARS[ctx.channel.id]['stop']:
        VARS[ctx.channel.id]['num_stops']+=1
        num_stops = VARS[ctx.channel.id]['num_stops']
        if num_stops==1:
            message = random.choice(["I am not yet done. Please have a candy and listen on.", "I am hearing some haters asking me to stop. Be kind enough to ignore them.", "Have a candy, and listen on. I am still far from done."])
            await ctx.send(message)
        if num_stops==2:
            message = random.choice(["As a good host, I shall not let this story be interrupted", "Please shut up and let me do the talking.", "Interrupting in such an untimely fashion is terribly rude.", "Please pay attention, I am still only starting."])
            await ctx.send(message)
        if num_stops==3:
            message = random.choice(["https://imgur.com/oM4gvOU", "I AM NOT DONE. S U C K E R", "https://imgur.com/tmGONPE"])
            await ctx.send(message)
        if num_stops==4:
            VARS[ctx.channel.id]['num_stops'] = 0
            VARS[ctx.channel.id]['stop'] = True
            VARS[ctx.channel.id]['telling_story'] = False
    else:
        await ctx.send("I am not saying a thing.")

@bot.command()
async def music(ctx, *music_name):
    '''Find an official Homestuck music'''
    message = await get_music(" ".join(music_name))
    await ctx.channel.send(message)

@bot.command()
async def progress(ctx, template_url):
    '''Show the progress on a template'''
    message = await get_progress(template_url)
    await ctx.channel.send(message)

@bot.command()
async def wiki(ctx, *search_terms):
    '''Searches the wiki'''
    message = await get_wiki(" ".join(search_terms))
    await ctx.channel.send(message)


@commands.is_owner()
@bot.command()
async def channels(ctx):
    '''[Owner] Lists all available text channels'''
    for channel in bot.get_all_channels():
        if channel.type == channel.type == discord.ChannelType.text:
            await ctx.channel.send(f"{channel.guild.name} - {channel.name} ({channel.id})")

@commands.is_owner()
@bot.command()
async def say(ctx, msg: str, channel_id:int=0):
    '''[Owner] Says as message on a given channel'''
    global DEFAULT_CHANNEL
    if channel_id == 0:
        channel_id = DEFAULT_CHANNEL
    await bot.wait_until_ready()
    await bot.get_channel(channel_id).send(msg)

@commands.is_owner()
@bot.command()
async def set_channel(ctx, channel_id:int):
    '''[Owner] Sets default channel for the !say command'''
    global DEFAULT_CHANNEL
    DEFAULT_CHANNEL = channel_id

## Wrap-up

bot.run("Njk5MjkwMzU0MDU4NTI2Nzgw.XpSUhQ.3G5f_7GzPir0ftVGpLYkCuBipdY")