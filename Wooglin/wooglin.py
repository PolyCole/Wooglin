import json
import os
import logging
import urllib
import base64
import random

import boto3

from urllib import request, parse

# Bot authorization token from slack.
BOT_TOKEN = os.environ["BOT_TOKEN"]

# Sending our replies here.
SLACK_URL = "https://slack.com/api/chat.postMessage"


def sendSMS(number, message):
    # insert Twilio Account SID into the REST API URL
    populated_url = os.environ["TWILIO_SMS_URL"].format(os.environ["TWILIO_SID"])

    post_params = {"To": number, "From": os.environ["TWILIO_NUMBER"], "Body": message}

    # encode the parameters for Python's urllib
    data = parse.urlencode(post_params).encode()
    req = request.Request(populated_url)

    # add authentication header to request based on Account SID + Auth Token
    authentication = "{}:{}".format(os.environ["TWILIO_SID"], os.environ["TWILIO_TOKEN"])
    base64string = base64.b64encode(authentication.encode('utf-8'))
    req.add_header("Authorization", "Basic %s" % base64string.decode('ascii'))

    try:
        # perform HTTP POST request
        with request.urlopen(req, data) as f:
            print("Twilio returned {}".format(str(f.read().decode('utf-8'))))
    except Exception as e:
        # something went wrong!
        return e
    return "SMS sent to  successfully!"


def greet(userid):
    name = getuserinfo(userid)
    greetings = ["Hi", "Hello", "Hey", "What\'s up",
                 "Waddup", "How are we", "Howdy", "Yo",
                 "Good day", "What's poppin", "What's crackalakin'",
                 "Hi there", "Hello there", "Hey there", "Howdy there",
                 "Well hello there"]

    greetingNum = random.randint(0, len(greetings) - 1)
    return greetings[greetingNum] + " " + name


def getuserinfo(userID):
    try:
        SLACK_URL_SPECIAL = "https://slack.com/api/users.info"
        data2 = urllib.parse.urlencode(
            (
                ("token", BOT_TOKEN),
                ("user", userID),
                ("include_locale", 'false')
            )
        )

        data2 = data2.encode("ascii")
        request2 = urllib.request.Request(SLACK_URL_SPECIAL, data=data2, method="POST")

        request2.add_header(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

        # Getting reponse from server and turning it into a dict.
        userdata = json.loads((urllib.request.urlopen(request2).read()).decode())

    except Exception as e:
        return "I've encountered an error"

    return userdata["user"]["real_name"]


def testdynamo():
    try:
        client = boto3.client('dynamodb')
        return (client.get_item(TableName='test', Key={'ID': {'N': '0'}})['Item']['Name']['S'])
    except Exception as e:
        return e


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
            if (text == 'friendship'):
                returnMessage = 'fidelity'
            elif ('send' in text):
                returnMessage = sendSMS(+19522559343, text[4::])
            elif (text == 'hello' or text == 'hi'):
                returnMessage = greet(slack_event["user"])
            elif (text == "testdynamo"):
                returnMessage = testdynamo()
            elif (text == "help"):
                returnMessage = "Here's a link to my documentation: https://github.com/PolyCole/Wooglin"
            else:
                returnMessage = text
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
        request = urllib.request.Request(SLACK_URL, data=data, method="POST")

        # Adding header.
        request.add_header(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

        # Request away!
        urllib.request.urlopen(request).read()

    return "200 OK"

