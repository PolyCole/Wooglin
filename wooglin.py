import os
import logging
import urllib
import re

from wit import Wit
import GreetUser
import DatabaseHandler
import SMSHandler

from urllib import request, parse

# Bot authorization token from slack.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Sending our replies here.
SLACK_URL = "https://slack.com/api/chat.postMessage"


def lambda_handler(data, context):
    print("RECEIVED:")
    print(data)

    global SLACK_CHANNEL
    #print("Conversation taking place in channel: " + str(SLACK_CHANNEL))

    # Handles initial challenge with Slack's verification.
    if "challenge" in data:
        return data["challenge"]

    # Getting the data of the event.
    slack_event = data['event']

    event_id = data['event_id']
    event_time = data['event_time']

    if DatabaseHandler.event_handled(event_id, event_time):
        return "200 OK"

    # Ignore other bot events.
    if "subtype" in slack_event:
        if slack_event['subtype'] == "bot_message":
            logging.warning("Ignore bot event")
            return "200 OK"
    else:
        # Parses out garbage text if user @'s the bot'
        text = slack_event["text"].lower()

        # Getting ID of channel where message originated.
        SLACK_CHANNEL = slack_event["channel"]

        if text.find(os.environ['MY_ID']) != -1:
            text = re.sub('<@.........>',"Wooglin,",text).strip()
            try:
                if text == os.environ['SECRET_PROMPT']:
                    sendmessage(os.environ['SECRET_RESPONSE'])
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
    return "200 OK"


def processMessage(slack_event):
    witClient = Wit(os.environ['WIT_TOKEN'])

    resp = witClient.message(slack_event['text'].lower())
    user = slack_event['user']

    try:
        action = resp['entities']['intent'][0]['value']
        confidence = resp['entities']['intent'][0]['confidence']
    except KeyError:
        action = "confused"
        confidence = 0

    if action == "confused" or confidence < 0.95:
        sendmessage("I'm sorry, I don't quite understand. To see my documentation, type help")
    elif action == "greeting":
        sendmessage(GreetUser.greet(user))
    elif action == "database":
        DatabaseHandler.dbhandler(resp, user)
    elif action == "sms":
        SMSHandler.smshandler(resp)
    elif action == "help":
        sendmessage("Here's a link to my documentation: https://github.com/PolyCole/Wooglin/#Documentation")
    else:
        sendmessage("Whoops! It looks like that feature hasn't been hooked up yet.")


