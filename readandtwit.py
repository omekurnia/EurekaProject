import tweepy
import requests
from requests_oauthlib import OAuth1
import os
import os.path
from os import environ
import time
import datetime

api_key = environ["API_KEY"]
api_secret_key = environ["API_SECRET"]
bearer_key = environ["BEARER_KEY"]
access_token = environ["ACCESS_TOKEN"]
access_token_secret = environ["ACCESS_SECRET"]

auth = tweepy.OAuthHandler(api_key, api_secret_key)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

keyword = "eureka!"
media_keyword = "attachment"
filename = 'temp.jpg'

def create_log(reports):
    with open("logfile.txt", "a") as file:
        file.write(reports + "\n")

def blocked_id(sender_id):
    with open("blocked_id.txt", "a") as file:
        file.write(sender_id + "\n")

def save_last_dm(text):
    with open("last_dm.txt", "w") as file:
        file.write(text)

def check_last_dm():
    with open("last_dm.txt", "r") as file:
        last_dm = file.read()
        return last_dm

def bad_words():
    with open("badwords.txt", "r") as file:
        bwords = file.read().split()
        return bwords

def download_media(img_url):
    oauth = OAuth1(client_key = api_key, client_secret = api_secret_key, resource_owner_key = access_token, resource_owner_secret = access_token_secret)
    request = requests.get(img_url, auth=oauth)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
    else:
        print("                         Unable to download image")
        create_log("                         Unable to download image")

def check_media():
    try:
        timelog = datetime.datetime.now() + datetime.timedelta(hours= 7)
        read_dms = api.list_direct_messages(1)
        print("---------------")
        create_log("---------------")
        print(str(timelog) + " : Scanning DM")
        create_log(str(timelog) + " : Scanning DM")
        time.sleep(3)
        for message in read_dms:
            text = message.message_create["message_data"]["text"]
            sender_id = message.message_create["sender_id"]
            tweet_type = str(message)
        if "video_info" in tweet_type:
            api.send_direct_message(recipient_id = sender_id, text = "Sorry, MBC doesn't accept video or GIF for now!")
            create_log("                             error : video or GIF is not allowed")
            create_log("                             The Tweet: " + sender_id + text)
            api.send_direct_message(recipient_id = "1296865849374998528", text = "Hey, this user id: " + sender_id + ", has tried to send us video/GIF submission. Please review their id in case there were multiple attempts of violation")
            blocked_id(sender_id)
        elif media_keyword in tweet_type:
            img_url = message.message_create["message_data"]["attachment"]["media"]["url"]
            img_durl = message.message_create["message_data"]["attachment"]["media"]["media_url"]
            new_text = text.replace(img_url, " ")
            create_log("                             downloading pic")
            time.sleep(3)
            download_media(img_durl)
            check_bad_words(new_text, sender_id)
        else:
                check_bad_words(text, sender_id)
    except Exception as ex:
        print("                             Failed: " + str(ex) + " error")
        create_log("                             Failed: " + str(ex) + " error")
        time.sleep(3)


def check_bad_words(text, sender_id):
    bwords = bad_words()
    low_text = text.lower()
    print("                             Checking bad words")
    create_log("                             Checking bad words")
    time.sleep(3)
    if any(word in bwords for word in low_text.split()):
        api.send_direct_message(recipient_id = sender_id, text = "Hi! Thanks for sending us message with bad word. Please be mindful, your account can be banned from interacting with us.")
        print("                             Violation! Bad Words! User ID: " + sender_id + " has been blocked!")
        create_log("                             Violation! Bad Words! User ID: " + sender_id + " has been blocked!")
        blocked_id(sender_id)
    else:
        print("                             No bad word")
        create_log("                             No badword")
        check_keyword(low_text, sender_id)

def check_keyword(text, sender_id):
    last_dm = check_last_dm()
    print("                             Checking duplicate")
    create_log("                             Checking duplicate")
    time.sleep(3)
    if text == last_dm:
        print("                             Can not post duplicate dm")
        create_log("                             Can not post duplicate dm")
        time.sleep(3)
        pass
    else:
        if keyword in text:
            save_last_dm(text)
            check_length(text, sender_id)
        else:
            print("                             Could not found message with keyword")
            create_log("                             Could not found message with keyword")
    
def check_length(text, sender_id):
    print("                             Checking text length")
    create_log("                             Checking text length")
    time.sleep(3)
    if len(text) > 800:
        print("                             Can not post text with more than 800 characters")
        create_log("                             Can not post text with more than 800 characters")
        api.send_direct_message(recipient_id = sender_id, text = "Sorry, We can not post tweets more than 800 characters. Please make it shorter.")
    elif len(text) > 270 and len(text) < 800:
        print("                             More than 270 characters, creating Thread")
        create_log("                             More than 270 characters, creating Thread")
        time.sleep(3)
        Thread(text, sender_id)
    else:
        print("                             Less than 270 characters, processing normal tweet")
        create_log("                             Less than 270 characters, processing normal tweet")
        time.sleep(3)
        post_tweet_option(text, sender_id)
            
def post_tweet_option(text, sender_id):
    try:
        if os.path.isfile(filename):
            print("                             updating with media")
            create_log("                             updating with media")
            api.update_with_media(filename, status = text)
            id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
            api.send_direct_message(recipient_id = sender_id, text = "Hi! Thanks for sending us submission!")
            tweet_url = "https://twitter.com/hieureka/status/" + str(id_tweet)
            api.send_direct_message(recipient_id = sender_id, text = "Check your tweet " + tweet_url)
            api.send_direct_message(recipient_id = sender_id, text = "Don't forget to share to your friends!")
            print("                             Success!")
            create_log("                             Success!")
            create_log("                             The Tweet: " + sender_id + text)
            os.remove(filename)
            
        else:
            print("                             updating without media")
            create_log("                             updating without media")
            api.update_status(text)
            id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
            api.send_direct_message(recipient_id = sender_id, text = "Hi! Thanks for sending us submission!")
            tweet_url = "https://twitter.com/hieureka/status/" + str(id_tweet)
            api.send_direct_message(recipient_id = sender_id, text = "Check your tweet " + tweet_url)
            api.send_direct_message(recipient_id = sender_id, text = "Don't forget to share to your friends!")
            print("                             Success!")
            create_log("                             Success!")
            create_log("                             The Tweet: " + sender_id + " " + text)
    except Exception as ex:
        print("                             Failed: " + str(ex) + " error")
        create_log("                             Failed: " + str(ex) + " error")
        print("                             The Tweet: " + sender_id + " " + text)
        create_log("                             The Tweet: " + sender_id + " " + text)
        time.sleep(3)

def Thread(text, sender_id):
    print("                             Processing Thread")
    i = 260
    for message in text:
        if text[i] != " ":
            i -= 1
            j = i + 1
            text1 = text[0:i] + " (cont...)"
            text2 = text[j:]
    if os.path.isfile(filename) == True:
        print("                             Found image, posting first tweet with image")
        create_log("                             Found image, posting first tweet with image")    
        api.update_with_media(filename, status = text1)
        os.remove(filename)
        id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
        api.send_direct_message(recipient_id = sender_id, text = "Hi! Thanks for sending us submission!")
        tweet_url = "https://twitter.com/hieureka/status/" + str(id_tweet)
        api.send_direct_message(recipient_id = sender_id, text = "Check your tweet " + tweet_url)
        api.send_direct_message(recipient_id = sender_id, text = "Don't forget to share to your friends!")
    else:
        print("                             No image, posting normal Thread")
        api.update_status(text1)
        id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
        api.send_direct_message(recipient_id = sender_id, text = "Hi! Thanks for sending us submission!")
        tweet_url = "https://twitter.com/hieureka/status/" + str(id_tweet)
        api.send_direct_message(recipient_id = sender_id, text = "Check your tweet " + tweet_url)
        api.send_direct_message(recipient_id = sender_id, text = "Don't forget to share to your friends!")
    if len(text2) > 280:
        i = 270
        for message in text2:
            if text2[i] != " ":
                i -= 1
                j = i + 1
                text3 = text2[0:i] + " (cont...)"
                text4 = text2[j:]
        print("                             Processing tweet 2")
        create_log("                             Processing tweet 2")
        id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
        api.update_status(text3, in_reply_to_status_id = id_tweet, auto_populate_reply_metadata = True)
        time.sleep(3)
        print("                             Processing tweet 3")
        create_log("                             Processing tweet 3")
        id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
        api.update_status(text4, in_reply_to_status_id = id_tweet, auto_populate_reply_metadata = True)
        print("                             Success!")
        create_log("                             Success!")
    else:
        print("                             Processing tweet 2")
        id_tweet = api.user_timeline(screen_name = "hieureka")[0].id
        api.update_status(text2, in_reply_to_status_id = id_tweet, auto_populate_reply_metadata = True)
        print("                             Success!")
        create_log("                             Success!")

while True:
    check_media()
    time.sleep(150)