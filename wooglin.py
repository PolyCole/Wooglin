import os
import logging
import urllib
import re

from wit import Wit
import GreetUser
import DatabaseHandler
import SMSHandler
import Wooglin_RM

from urllib import request, parse

# Bot authorization token from slack.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Sending our replies here.
SLACK_URL = "https://slack.com/api/chat.postMessage"


def lambda_handler(data, context):
    print("RECEIVED:")
    print(data)

    global SLACK_CHANNEL;

    # Handles initial challenge with Slack's verification.
    if "challenge" in data:
        return data["challenge"]

    # If we're getting a text message.
    if 'body' in data:
        if data['body'] is not None:
            SLACK_CHANNEL = os.environ['DEFAULT_CHANNEL']
            Wooglin_RM.handler(data);
            return "200 OK"

    # Getting the data of the event.
    slack_event = data['event']

    event_id = data['event_id']
    event_time = data['event_time']

    # TODO add in a key/val pair in the test request to bypass this method.
    if 'ignore_event' not in data:
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

        # Checks that the user @ed us.
        if text.find(os.environ['MY_ID']) != -1:

            # Pulling the nasty @tag out of the message.
            text = re.sub('<@.........>',"Wooglin,",text).strip()
            print("Text after @ removal: " + text)
            try:
                # Some classics.
                if text == os.environ['SECRET_PROMPT']:
                    sendmessage(os.environ['SECRET_RESPONSE'])
                elif text == "Wooglin, play funkytown":
                    sendmessage("https://www.youtube.com/watch?v=s36eQwgPNSE")
                # Not a given response, let's send the message to NLP.
                else:
                    process_message(slack_event)
            except Exception as e:
                sendmessage("I've encountered an error: " + str(e))

        return "200 OK"


# Sends a message in slack.
def sendmessage(message):
    print("Sending: " + message)

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


# Handles the request to wit and the subsequent routing.
def process_message(slack_event):
    witClient = Wit(os.environ['WIT_TOKEN'])

    # Wit response.
    resp = witClient.message(slack_event['text'].lower())

    user = slack_event['user']

    # If Wooglin doesn't have a message intent, let's just tell the user we're confused.
    try:
        action = resp['entities']['intent'][0]['value']
        confidence = resp['entities']['intent'][0]['confidence']
    except KeyError:
        action = "confused"
        confidence = 0

    # Routing.
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
