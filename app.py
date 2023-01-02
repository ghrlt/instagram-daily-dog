import os
import datetime
import requests

import instagrapi
# from instagrapi.types import StoryLink

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


def getDuck(duckid: int):
    url = "https://random-d.uk/api/{}.jpg".format(duckid)
    response = requests.get(url)

    if response.status_code == 200:
        duckPath = WORKING_DIRECTORY_PATH + 'duck.jpg'

        open(duckPath, "wb").write(response.content)
        return duckPath

    raise Exception("Error getting duck: {}".format(response.status_code))


def main():
    dayOfTheYear = datetime.datetime.now().timetuple().tm_yday

    print("Day #{} | Logging in...".format(dayOfTheYear))

    client = instagrapi.Client()
    try:
        client.load_settings(WORKING_DIRECTORY_PATH + 'ig.session')
    except:
        print("Day #{} | WARNING: Settings not found!".format(dayOfTheYear))

    client.login(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    client.dump_settings(WORKING_DIRECTORY_PATH + 'ig.session')

    print("Day #{} | Logged in!".format(dayOfTheYear))

    # Obtain the duck picture
    duck = getDuck(dayOfTheYear)

    print("Day #{} | Duck obtained!".format(dayOfTheYear))

    # Post the picture in an Instagram story
    client.photo_upload_to_story(
        duck,
        # links=[
        #     StoryLink(
        #         webUri="https://random-d.uk/api/{}.jpg".format(dayOfTheYear)
        #     )
        # ]
    )

    print("Day #{} | Duck posted!".format(dayOfTheYear))


if __name__ == "__main__":
    main()
