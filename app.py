import os
import datetime
import requests

import instagrapi
from instagrapi.types import StoryLink

from PIL import Image, ImageDraw, ImageFont

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


def getDuck(duckid: int):
    url = "https://random-d.uk/api/{}.jpg".format(duckid)
    response = requests.get(url)

    if response.status_code == 200:
        duckPath = WORKING_DIRECTORY_PATH + 'duck.jpg'

        open(duckPath, "wb").write(response.content)
        return duckPath

    raise Exception("Error getting duck: {}".format(response.status_code))

def formatImage(duckpath: str):
    base = Image.new('RGB', (1080,1920), (255,255,0))
    duck = Image.open(duckpath)

    #~ Resize the image to fit, if it's too large (>1000) or too small (<800)
    if duck.size[0] > 1000 or duck.size[0] < 800:
        wPercent = (1000/float(duck.size[0]))
        hSize = int((float(duck.size[1])*float(wPercent)))
        duck = duck.resize((1000,hSize), Image.Resampling.LANCZOS)

    wPos = int((1080-duck.size[0])/2)
    hPos = int((1920-duck.size[1])/2)
    base.paste(duck, (wPos, hPos))
    base.save(duckpath, quality=95)

def addCaption(duckpath: str, caption: str):
    duck = Image.open(duckpath)
    draw = ImageDraw.Draw(duck)
    font = ImageFont.truetype(WORKING_DIRECTORY_PATH + 'captionFont.ttf', 80)

    #~ Determine text size & position
    _,_, wText, hText = draw.textbbox((0,0), caption, font=font)
    wPos = (duck.size[0]-wText)/2
    hPos = (duck.size[1]-hText)/1.1

    #~ Draw caption background
    draw.rounded_rectangle((wPos*0.90, hPos*0.985, wPos*1.10+wText, hPos*1.025+hText), fill=(0,0,0), radius=20)

    #~ Write caption
    draw.text((wPos, hPos), caption, font=font, fill=(255,255,255))
    duck.save(duckpath)


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

    # Obtain the duck picture
    duckPath = getDuck(dayOfTheYear)
    print("Day #{} | Duck obtained!".format(dayOfTheYear))

    # Format the picture to fit
    formatImage(duckPath)
    addCaption(duckPath, 'Duck #{}'.format(dayOfTheYear))
    print("Day #{} | Story formatted!".format(dayOfTheYear))

    # Post the picture in an Instagram story
    duckStory = client.photo_upload_to_story(
        duckPath,
        # links=[
        #     StoryLink(
        #         webUri="https://random-d.uk/api/{}.jpg".format(dayOfTheYear)
        #     )
        # ]
    )
    print("Day #{} | Duck posted!".format(dayOfTheYear))

    # Check if user as an highlight named "Ducks" (Feel free to change this)
    for userHighlight in client.user_highlights(client.user_id):
        if userHighlight.title == "Ducks":
            # Add the story to highlights
            client.highlight_add_stories(userHighlight.pk, [duckStory.pk])
            print("Day #{} | Added story to highlight".format(dayOfTheYear))


if __name__ == "__main__":
    main()
