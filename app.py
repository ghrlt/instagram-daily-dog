import os
import math
import random
import datetime
import requests

import instagrapi
from instagrapi.types import StoryLink

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

from dotenv import load_dotenv
load_dotenv()

WORKING_DIRECTORY_PATH = os.getenv('WORKING_DIRECTORY_PATH')
if WORKING_DIRECTORY_PATH: 
    if WORKING_DIRECTORY_PATH[-1] != '/':
        WORKING_DIRECTORY_PATH += '/'

INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
if not INSTAGRAM_USERNAME:
    raise Exception("INSTAGRAM_USERNAME not set!")

INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
if not INSTAGRAM_PASSWORD:
    raise Exception("INSTAGRAM_PASSWORD not set!")

INSTAGRAM_2FA_SEED = os.getenv('INSTAGRAM_2FA_SEED')


def getCat(catid: int):
    url = "https://cataas.com/api/cats?limit=1&skip={}".format(catid)
    response = requests.get(url)

    if response.status_code == 200:
        url = "https://cataas.com/cat/{}".format(response.json()[0]['_id'])
        response = requests.get(url)

        if response.status_code == 200:
            catPath = WORKING_DIRECTORY_PATH + 'cat.jpg'

            open(catPath, "wb").write(response.content)
            return catPath

    raise Exception("Error getting cat: {}".format(response.status_code))

def formatImage(catpath: str):
    base = Image.new('RGB', (1080,1920), (255,255,0))
    cat = Image.open(catpath)
    originalCat = cat.copy()

    #~ Resize and spawn multiple image of cat in the background
    wPercent = (216/float(originalCat.size[0]))
    hSize = int((float(originalCat.size[1])*float(wPercent)))
    smallCat = originalCat.resize((216,hSize), Image.Resampling.LANCZOS)

    #~ Reduce brightness & blur, goal is to put in foreground the main cat
    smallCat = ImageEnhance.Brightness(smallCat).enhance(.75)
    smallCat = smallCat.filter(ImageFilter.GaussianBlur(4))

    for i in range( math.ceil(base.size[1]/hSize) ):
        for j in range( math.ceil(base.size[0]/smallCat.size[0]) ):
            base.paste(smallCat, (j*smallCat.size[0],i*smallCat.size[1]))


    #~ Resize the image to fit, if it's too large (>1000) or too small (<800)
    if cat.size[0] > 1000 or cat.size[0] < 800:
        wPercent = (1000/float(cat.size[0]))
        hSize = int((float(cat.size[1])*float(wPercent)))
        cat = cat.resize((1000,hSize), Image.Resampling.LANCZOS)

    wPos = int((1080-cat.size[0])/2)
    hPos = int((1920-cat.size[1])/2)

    base.paste(cat, (wPos, hPos))
    base.save(catpath, quality=95)

def addCaption(catpath: str, caption: str):
    cat = Image.open(catpath)
    draw = ImageDraw.Draw(cat)
    font = ImageFont.truetype(WORKING_DIRECTORY_PATH + 'captionFont.ttf', 80)

    #~ Determine text size & position
    _,_, wText, hText = draw.textbbox((0,0), caption, font=font)
    wPos = (cat.size[0]-wText)/2

    
    #~ Draw caption background
    
    #~ Vertical placement (top/bottom) is random
    onTop = random.randint(0,1) == 0
    if onTop:
        hPos = (cat.size[1]-hText)/6
        draw.rounded_rectangle((wPos*0.90, hPos*0.95, wPos*1.10+wText, hPos*1.10+hText), fill=(0,0,0), radius=20)
    else:
        hPos = (cat.size[1]-hText)/1.1
        draw.rounded_rectangle((wPos*0.90, hPos*0.985, wPos*1.10+wText, hPos*1.025+hText), fill=(0,0,0), radius=20) # Bottom

    #~ Write caption
    draw.text((wPos, hPos), caption, font=font, fill=(255,255,255))
    cat.save(catpath)


def main():
    code = ''
    dayOfTheYear = datetime.datetime.now().timetuple().tm_yday

    print("Day #{} | Logging in...".format(dayOfTheYear))

    client = instagrapi.Client()
    try:
        client.load_settings(WORKING_DIRECTORY_PATH + 'ig.session')
    except:
        print("Day #{} | WARNING: Settings not found!".format(dayOfTheYear))

        if INSTAGRAM_2FA_SEED:
            code = client.totp_generate_code(INSTAGRAM_2FA_SEED)
            print("Day #{} | Generated 2FA code".format(dayOfTheYear))

    client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, verification_code=code)
    client.dump_settings(WORKING_DIRECTORY_PATH + 'ig.session')

    print("Day #{} | Logged in!".format(dayOfTheYear))

    # Obtain the cat picture
    catPath = getCat(dayOfTheYear)
    print("Day #{} | Cat obtained!".format(dayOfTheYear))

    # Format the picture to fit
    formatImage(catPath)
    addCaption(catPath, 'Cat #{}'.format(dayOfTheYear))
    print("Day #{} | Story formatted!".format(dayOfTheYear))

    # Post the picture in an Instagram story
    catStory = client.photo_upload_to_story(catPath)
    print("Day #{} | Cat posted!".format(dayOfTheYear))

    # Check if user as an highlight named "Cs" (Feel free to change this)
    for userHighlight in client.user_highlights(client.user_id):
        if userHighlight.title == "Cats":
            # Add the story to highlights
            client.highlight_add_stories(userHighlight.pk, [catStory.pk])
            print("Day #{} | Added story to highlight".format(dayOfTheYear))


if __name__ == "__main__":
    main()