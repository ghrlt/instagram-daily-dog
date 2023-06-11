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


def getDog(dogid: int):
    url = "https://random.dog/doggos?include=jpg"
    response = requests.get(url)

    if response.status_code == 200:
        url = "https://random.dog/{}".format(response.json()[dogid])
        response = requests.get(url)

        if response.status_code == 200:
            dogPath = WORKING_DIRECTORY_PATH + 'dog.jpg'

            open(dogPath, "wb").write(response.content)
            return dogPath

    raise Exception("Error getting dog: {}".format(response.status_code))

def formatImage(dogpath: str):
    base = Image.new('RGB', (1080,1920), (255,255,0))
    dog = Image.open(dogpath)
    originalDog = dog.copy()

    #~ Resize and spawn multiple image of dog in the background
    wPercent = (216/float(originalDog.size[0]))
    hSize = int((float(originalDog.size[1])*float(wPercent)))
    smallDog = originalDog.resize((216,hSize), Image.Resampling.LANCZOS)

    #~ Reduce brightness & blur, goal is to put in foreground the main dog
    smallDog = ImageEnhance.Brightness(smallDog).enhance(.75)
    smallDog = smallDog.filter(ImageFilter.GaussianBlur(4))

    for i in range( math.ceil(base.size[1]/hSize) ):
        for j in range( math.ceil(base.size[0]/smallDog.size[0]) ):
            base.paste(smallDog, (j*smallDog.size[0],i*smallDog.size[1]))


    #~ Resize the image to fit, if it's too large (>1000) or too small (<800)
    if dog.size[0] > 1000 or dog.size[0] < 800:
        wPercent = (1000/float(dog.size[0]))
        hSize = int((float(dog.size[1])*float(wPercent)))
        dog = dog.resize((1000,hSize), Image.Resampling.LANCZOS)

    wPos = int((1080-dog.size[0])/2)
    hPos = int((1920-dog.size[1])/2)

    base.paste(dog, (wPos, hPos))
    base.save(dogpath, quality=95)

def addCaption(dogpath: str, caption: str):
    dog = Image.open(dogpath)
    draw = ImageDraw.Draw(dog)
    font = ImageFont.truetype(WORKING_DIRECTORY_PATH + 'captionFont.ttf', 80)

    #~ Determine text size & position
    _,_, wText, hText = draw.textbbox((0,0), caption, font=font)
    wPos = (dog.size[0]-wText)/2

    
    #~ Draw caption background
    
    #~ Vertical placement (top/bottom) is random
    onTop = random.randint(0,1) == 0
    if onTop:
        hPos = (dog.size[1]-hText)/6
        draw.rounded_rectangle((wPos*0.90, hPos*0.95, wPos*1.10+wText, hPos*1.10+hText), fill=(0,0,0), radius=20)
    else:
        hPos = (dog.size[1]-hText)/1.1
        draw.rounded_rectangle((wPos*0.90, hPos*0.985, wPos*1.10+wText, hPos*1.025+hText), fill=(0,0,0), radius=20) # Bottom

    #~ Write caption
    draw.text((wPos, hPos), caption, font=font, fill=(255,255,255))
    dog.save(dogpath)


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

    client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, verifidogion_code=code)
    client.dump_settings(WORKING_DIRECTORY_PATH + 'ig.session')

    print("Day #{} | Logged in!".format(dayOfTheYear))

    # Obtain the dog picture
    dogPath = getDog(dayOfTheYear)
    print("Day #{} | Dog obtained!".format(dayOfTheYear))

    # Format the picture to fit
    formatImage(dogPath)
    addCaption(dogPath, 'Dog #{}'.format(dayOfTheYear))
    print("Day #{} | Story formatted!".format(dayOfTheYear))

    # Post the picture in an Instagram story
    dogStory = client.photo_upload_to_story(dogPath)
    print("Day #{} | Dog posted!".format(dayOfTheYear))

    # Check if user as an highlight named "Cs" (Feel free to change this)
    for userHighlight in client.user_highlights(client.user_id):
        if userHighlight.title == "Dogs":
            # Add the story to highlights
            client.highlight_add_stories(userHighlight.pk, [dogStory.pk])
            print("Day #{} | Added story to highlight".format(dayOfTheYear))


if __name__ == "__main__":
    main()