from fuzzywuzzy import process
import json

with open("music.json","r") as f:
    MUSICS, FLASHES, ALIASES = json.load(f)
NAMES = list(MUSICS.keys())+list(FLASHES.keys())+list(ALIASES.keys())

async def get_music(query):
    global MUSIC, FLASHES, ALIASES, NAMES
    if query == "random":
        name = random.choice(list(MUSICS.keys()))
        message = random.choice(["I think you will like it", "One of my favourites", "Here"])
        return f"{message}: {name}\n{MUSICS[name]}"
    else:
        name, ratio = process.extractOne(query, NAMES)
        if ratio < 85:
            return "I cannot seem to find that music."
        else:
            if name in MUSICS:
                return f"Here you go: {name}\n{MUSICS[name]}"
            elif name in ALIASES:
                return f"Here you go: {ALIASES[name]}\n{MUSICS[ALIASES[name]]}"
            music_list = FLASHES[name]
            if name[-1]==".":
                display_name = name[:-1]
            else:
                display_name=name
            if len(music_list)==1:
                return f"The music featured in the flash _{display_name}_ is: {music_list[0]}\n{MUSICS[music_list[0]]}"
            message = f" _{display_name}_ features a few different musics, please be more specific:"
            for music in music_list:
                message+="\n- "+music
            return message



