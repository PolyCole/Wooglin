import os
import logging
import urllib
import re
import sys

from wit import Wit
import GreetUser
import DatabaseHandler
import SMSHandler
import Wooglin_RM

from urllib import request, parse

from twilio.twiml.messaging_response import MessagingResponse

# Bot authorization token from slack.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Sending our replies here.
SLACK_URL = "https://slack.com/api/chat.postMessage"


def lambda_handler(data, context):
    print("RECEIVED:")
    print(data)

    # Verifying that our requests are actually coming from slack.
    if "token" in data:
        if data['token'] != os.environ['SLACK_VERIFICATION_TOKEN']:
            print("VERIFICATION FOR SLACK FAILED.")
            print("Terminating....")
            sys.exit(1)

    # Verifying our requests are coming from Twilio.
    # TODO Figure out a far more accurate way to do this.
    # if "headers" in data:
    #     if data['headers']['X-Twilio-Signature'] != os.environ["TWILIO_VERIFICATION_TOKEN"]:
    #         print("VERIFICATION FOR TWILIO FAILED.")
    #         print("Terminating....")
    #         sys.exit(1)


    global SLACK_CHANNEL

    # Handles initial challenge with Slack's verification.
    if "challenge" in data:
        return data["challenge"]

    # If we're getting a text message.
    if 'body' in data:
        if data['body'] is not None:
            SLACK_CHANNEL = os.environ['DEFAULT_CHANNEL']
            Wooglin_RM.handler(data)
            resp = MessagingResponse()
            return str(resp)

    # Getting the data of the event.
    slack_event = data['event']

    event_id = data['event_id']
    event_time = data['event_time']

    # TODO add in a key/val pair in the test request to bypass this method.
    if 'ignore_event' not in data:
        if DatabaseHandler.event_handled(event_id, event_time):
            return "200 OK"

    # Ignore other bot events.
    if "bot_id" in slack_event:
        logging.warning("Ignore bot event")
        return "200 OK"
    else:
        # Parses out garbage text if user @'s the bot'
        text = slack_event["text"].lower()

        # Getting ID of channel where message originated.
        SLACK_CHANNEL = slack_event["channel"]

        if 'channel_type' in slack_event and slack_event['channel_type'] == "im":
            process_message_helper(text, slack_event)
        else:
            if mentions_me(text):
                process_message_helper(strip_text(text), slack_event)
        return "200 OK"


def mentions_me(text):
    return text.find(os.environ['MY_ID']) != -1


def strip_text(text):
    # Pulling the nasty @tag out of the message.
    text = re.sub('<@.........>', "Wooglin,", text).strip()
    print("Text after @ removal: " + text)
    return text


def process_message_helper(text, slack_event):
    try:
        # Some classics.
        if text == "Wooglin " + os.environ['SECRET_PROMPT']:
            sendmessage(os.environ['SECRET_RESPONSE'])
        elif text == "Wooglin, play funkytown":
            sendmessage("https://www.youtube.com/watch?v=s36eQwgPNSE")
        # Not a given response, let's send the message to NLP.
        else:
            process_message(slack_event)
    except Exception as e:
        sendmessage("I've encountered an error: " + str(e))


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
