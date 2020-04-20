import aiohttp
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import time
from urllib.parse import parse_qs
import json

CANVAS = (None, None)
CANVAS_X, CANVAS_Y = 1500, 1488
COLORS = [(255, 255, 255), (205, 205, 205), (136, 136, 136), (85, 85, 85), (34, 34, 34), (0, 0, 0), (255, 167, 209), (253, 70, 89), (229, 0, 0), (128, 0, 0), (255, 221, 202), (246, 179, 137), (229, 149, 0), (255, 91, 0), (160, 106, 66), (96, 64, 40), (255, 255, 0), (253, 253, 150), (148, 224, 68), (2, 190, 1), (0, 95, 0), (0, 211, 221), (0, 131, 199), (0, 0, 234), (3, 7, 100), (207, 110, 228), (255, 0, 255), (130, 0, 128)]

async def get_webpage(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

async def get_canvas():
    print("Fetching canvas...")
    r = await get_webpage(f"https://pxls.space/boarddata?_{time.time()}")
    frame = [x for x in bytes(r)]
    res = []
    for elmt in frame:
        if elmt==255:
            res.append((0,0,0))
        else:
            res.append(COLORS[elmt])
    img = np.array(res)
    img = img.reshape((CANVAS_X,CANVAS_Y,3), order='F')
    return np.transpose(img, (1,0,2))

def get_template_info(url):
    url_dict = parse_qs(url)
    return {'link':url_dict["https://pxls.space/#template"][0], "width":int(url_dict["tw"][0]), "x":int(url_dict["ox"][0]),"y":int(url_dict["oy"][0])}


async def get_difference(canvas, url):
    template_info = get_template_info(url)
    img_link = template_info["link"]
    r = await get_webpage(img_link)
    template_img = np.array(Image.open(BytesIO(r)).convert("RGBA"))
    template_img, num_transparent = resize(template_img, template_info["width"])
    canvas_section = canvas[template_info["y"]:template_info["y"]+template_img.shape[0], template_info["x"]:template_info["x"]+template_img.shape[1]]
    num_same = np.count_nonzero(np.apply_along_axis(np.all, 2, (canvas_section==template_img)))+num_transparent + 1 #Wtf
    size = canvas_section.shape[0]*canvas_section.shape[1]
    return num_same, size

def show(img):
    plt.imshow(img)
    plt.show()

def resize(img, new_width):
    '''Returns resized image and transparent pixel count'''
    transparent_num = 0
    height, width = img.shape[:2]
    new_height = height*new_width//width
    new_image = np.ones((new_height, new_width,3), dtype=np.uint8)
    x_ratio, y_ratio = width//new_width, height//new_height
    for i in range(new_height):
        for j in range(new_width):
            sub_image = img[i*y_ratio:(i+1)*y_ratio, j*x_ratio:(j+1)*x_ratio]
            non_zero = np.nonzero(sub_image)
            if non_zero[0].size>0:
                new_image[i, j]=sub_image[non_zero[0][0],non_zero[1][0]][:3]
            else:
                transparent_num+=1
    return new_image, transparent_num

async def get_progress(template_url):
    global CANVAS
    if CANVAS[0] is None or time.time()-CANVAS[1]>=5*60:
        CANVAS = [await get_canvas(), time.time()]
    num_same, size = await get_difference(CANVAS[0], template_url)
    return f"{round(100*num_same/size, 2)}% ({num_same}/{size}) pxls done."





