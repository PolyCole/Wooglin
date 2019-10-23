import os
import logging
import urllib

from wit import Wit
from src import GreetUser, testingWit, DatabaseHandler, SMSHandler

from urllib import request, parse

# Bot authorization token from slack.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Sending our replies here.
SLACK_URL = "https://slack.com/api/chat.postMessage"




def lambda_handler(data, context):
    global SLACK_CHANNEL

    # Handles initial challenge with Slack's verification.
    if "challenge" in data:
        return data["challenge"]

    # Getting the data of the event.
    slack_event = data['event']

    # Ignore other bot events.
    if "bot_id" in slack_event:
        logging.warn("Ignore bot event")
    else:
        # Parses out garbage text if user @'s the bot'
        text = slack_event["text"].lower()
        text = text[13::] if text.find('@') != -1 else text

        # Getting ID of channel where message originated.
        SLACK_CHANNEL = slack_event["channel"]

        try:
            if text == os.environ['SECRET_PROMPT']:
                sendmessage(os.environ['SECRET_RESPONSE'])
            elif text == "help":
                sendmessage("Here's a link to my documentation: https://github.com/PolyCole/Wooglin/README.md")
            else:
                processMessage(slack_event)
        except Exception as e:
            sendmessage("I've encountered an error: " + str(e))

        return "200 OK"


def sendmessage(message):
    # Crafting our response.
    data = urllib.parse.urlencode(
        (
            ("token", BOT_TOKEN),
            ("channel", SLACK_CHANNEL),
            ("text", message)
        )
    )

    print("Sending: " + str(data))

    # Encoding
    data = data.encode("ascii")

    # Creating HTTP POST request.
    requestHTTP = urllib.request.Request(SLACK_URL, data=data, method="POST")

    # Adding header.
    requestHTTP.add_header(
        "Content-Type",
        "application/x-www-form-urlencoded"
    )

    # Request away!
    urllib.request.urlopen(requestHTTP).read()
    print("Sent message!")
    return "200 OK"


def processMessage(slack_event):
    witClient = Wit(os.environ['WIT_TOKEN'])

    resp = witClient.message(slack_event['text'].lower())

    try:
        action = resp['entities']['intent'][0]['value']
        confidence = resp['entities']['intent'][0]['confidence']
    except KeyError:
        action = "confused"
        confidence = 0

    if action == "confused" or confidence < 0.70:
        sendmessage("I'm sorry, I don't quite understand. To see my documentation, type help")
    elif action == "greeting":
        sendmessage(GreetUser.greet(slack_event['user']))
    elif action == "database":
        DatabaseHandler.dbhandler(resp)
    elif action == "sms":
        SMSHandler.smshandler(resp)
    else:
        sendmessage("Whoops! It looks like that feature hasn't been hooked up yet.")


