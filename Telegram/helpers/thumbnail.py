import os
import re
import textwrap
 
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageChops
from youtubesearchpython.__future__ import VideosSearch
 
MUSIC_BOT_NAME = "Telethon Music"
YOUTUBE_IMG_URL = "https://telegra.ph/file/95d96663b73dbf278f28c.jpg"
files = [] 

for filename in os.listdir("./thumbnail"): 
     if filename.endswith("PNG"): 
         files.append(filename[:-4])
 
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage
 
 
def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
 
 
async def gen_thumb(videoid):
    anime = random.choice(files)
    if os.path.isfile(f"cache/{videoid}_{anime}.png"):
        return f"cache/{videoid}_{anime}.png"
    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"
 
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()
 
        
 
        youtube = Image.open(f"cache/thumb{videoid}.png")
        bg = Image.open(f"thumbnail/{anime}.PNG")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.6)
        cir = Image.open(f"thumbnail/IMG_20221129_201846_195.png") 
        image3 = changeImageSize(1280, 720, bg)
        circle = changeImageSize(1280, 720, cir)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")
 
        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), Image.ANTIALIAS)
        logo.save(f"cache/chop{videoid}.png")
        if not os.path.isfile(f"cache/cropped{videoid}.png"):
            im = Image.open(f"cache/chop{videoid}.png").convert('RGBA')
            add_corners(im)
            im.save(f"cache/cropped{videoid}.png")
 
        crop_img = Image.open(f"cache/cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((365, 365), Image.ANTIALIAS)
        width = int((1280 - 365)/ 2)
        background = Image.open(f"cache/temp{videoid}.png")
        background.paste(logo, (width + 2, 134), mask=logo)
        background.paste(circle, mask=circle)
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("thumbnail/font2.ttf", 45)
        font2 = ImageFont.truetype("thumbnail/font2.ttf", 70)
        arial = ImageFont.truetype("thumbnail/font2.ttf", 30)
        name_font = ImageFont.truetype("thumbnail/font.ttf", 30)
        para = textwrap.wrap(title, width=32)
        j = 0
        try:
            if para[0]:
                text_w, text_h = draw.textsize(f"{para[0]}", font=font)
                draw.text(((1280 - text_w)/2, 530), f"{para[0]}", fill="white", stroke_width=1, stroke_fill="white", font=font)
            if para[1]:
                text_w, text_h = draw.textsize(f"{para[1]}", font=font)
                draw.text(((1280 - text_w)/2, 580), f"{para[1]}", fill="white", stroke_width=1, stroke_fill="white", font=font)
        except:
            pass
        text_w, text_h = draw.textsize(f"Duration: {duration} Mins", font=arial)
        draw.text(((1280 - text_w)/2, 660), f"Duration: {duration} Mins", fill="white", font=arial)
 
 
 
        
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        background.save(f"cache/{videoid}_{anime}.png")
        return f"cache/{videoid}_{anime}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
