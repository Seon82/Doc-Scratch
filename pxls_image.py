import aiohttp
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO
import time
from urllib.parse import parse_qs
import json
import cv2

CANVAS = (None, None)
CANVAS_X, CANVAS_Y = 4000, 600
COLORS = [(255, 255, 255, 255), (205, 205, 205, 255), (136, 136, 136, 255), (85, 85, 85, 255), (34, 34, 34, 255), (0, 0, 0, 255), (255, 167, 209, 255), (253, 70, 89, 255), (229, 0, 0, 255), (128, 0, 0, 255), (255, 221, 202, 255), (246, 179, 137, 255), (229, 149, 0, 255), (255, 91, 0, 255), (160, 106, 66, 255), (96, 64, 40, 255), (255, 255, 0, 255), (253, 253, 150, 255), (148, 224, 68, 255), (2, 190, 1, 255), (0, 95, 0, 255), (0, 211, 221, 255), (0, 131, 199, 255), (0, 0, 234, 255), (3, 7, 100, 255), (207, 110, 228, 255), (255, 0, 255, 255), (130, 0, 128, 255)]

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
            res.append((1,1,1,0))
        else:
            res.append(COLORS[elmt])
    img = np.array(res)
    img = img.reshape((CANVAS_X,CANVAS_Y,4), order='F')
    return np.transpose(img, (1,0,2))


def get_template_info(url):
    url_dict = parse_qs(url)
    if "template" in url_dict.keys():
        return {'link':url_dict["template"][0], "width":int(url_dict["tw"][0]), "x":int(url_dict["ox"][0]),"y":int(url_dict["oy"][0])}
    return {'link':url_dict["https://pxls.space/#template"][0], "width":int(url_dict["tw"][0]), "x":int(url_dict["ox"][0]),"y":int(url_dict["oy"][0])}

def clip(img, canvas_shape, x, y, width):
    ratio = img.shape[1]//width


async def get_difference(canvas, url):
    template_info = get_template_info(url)
    img_link = template_info["link"]
    r = await get_webpage(img_link)
    template_img = np.array(Image.open(BytesIO(r)).convert("RGBA"))
    template_img, num_opaque = resize(template_img, template_info["width"])
    canvas_section = canvas[template_info["y"]:template_info["y"]+template_img.shape[0], template_info["x"]:template_info["x"]+template_img.shape[1]]
    num_same = np.count_nonzero(np.apply_along_axis(np.all, 2, (canvas_section==template_img)))
    size = num_opaque
    return num_same, size

def show(img):
    plt.imshow(img)
    plt.show()

def resize(img, new_width):
    '''Returns resized image and non-transparent pixel count'''
    h,w, _=img.shape
    ratio = w//new_width
    bgra=[0,0,0,0]
    bgra[0], bgra[1],bgra[2], bgra[3] =cv2.split(img)
    for k in range(4):
        bgra[k].shape=(h*w//ratio, ratio)
        bgra[k]=np.max(bgra[k], axis=1)
        bgra[k].shape=(h//ratio, ratio, w//ratio)
        bgra[k]=np.max(bgra[k], axis=1)
        bgra[k].shape=(h//ratio,w//ratio)
        bgra[k]=np.uint8(bgra[k])
    out=cv2.merge((bgra[0], bgra[1], bgra[2], bgra[3]))
    return out, np.count_nonzero(bgra[3])

async def get_progress(template_url):
    global CANVAS
    if CANVAS[0] is None or time.time()-CANVAS[1]>=5*60:
        CANVAS = [await get_canvas(), time.time()]
    num_same, size = await get_difference(CANVAS[0], template_url)
    return f"{round(100*num_same/size, 2)}% ({num_same}/{size}) pxls done."





