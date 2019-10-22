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

        try:
            if text == os.environ['SECRET_PROMPT']:
                returnMessage = os.environ['SECRET_RESPONSE']
            elif text == "help":
                returnMessage = "Here's a link to my documentation: https://github.com/PolyCole/Wooglin/README.md"
            elif text == "test":
                returnMessage = testingWit.test()
            else:
                returnMessage = processMessage(slack_event)
        except Exception as e:
            returnMessage = e

        # Getting ID of channel where message originated.
        channel_id = slack_event["channel"]

        # Crafting our response.
        data = urllib.parse.urlencode(
            (
                ("token", BOT_TOKEN),
                ("channel", channel_id),
                ("text", returnMessage)
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
    action = resp['entities']['intent'][0]['value']

    if action == "greeting":
        return GreetUser.greet(slack_event['user'])
    elif action == "database":
        return DatabaseHandler.dbhandler(resp)
    elif action == "sms":
        return SMSHandler.smshandler(resp)
    else:
        return "I'm sorry, I don't quite understand. To see my documentation, type help"

    return action


