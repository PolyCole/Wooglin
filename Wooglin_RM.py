import SMSHandler
import urllib
import boto3
import os
import pytz
from boto3.dynamodb.conditions import Key
import SMSHandler
import datetime
import base64


def handler(data):
    data['body'] = data['body'].encode()

    message_parsed = (base64.b64decode(data['body']))
    message_parsed = message_parsed.decode().split('&')

    message = dictify_message(message_parsed)

    if os.environ['current_party'] == "None":
        SMSHandler.sendsms(message['From'], no_event_message())
        return "200 OK"
    else:

        if not validate_keyword(message['Body']):
            SMSHandler.sendsms(message['From'], incorrect_keyword_message())
            return "200 OK"

        dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        table = dynamodb.Table(os.environ['current_party'])

        response = table.query(
            KeyConditionExpression=Key('number').eq(message['From'])
        )

        if (response['Count'] == 0):
            table.put_item(
                Item={
                    'number': message['From'],
                    'name': get_name(message['Body']),
                    'arrived': get_arrival_time(),
                    'help_flag': False,
                    'help_flag_raised': "n/a"
                }
            )
            SMSHandler.sendsms(message['From'], welcome_number_message(message['Body']))

        else:
            SMSHandler.sendsms(message['From'], number_exists_message())
            return "200 OK"


def validate_keyword(message):
    message = message.split(",")

    if len(message) != 2:
        return False

    if message[0].strip().lower() != os.environ['current_party_keyword']:
        return False

    return True


def get_name(message):
    message = message.split(",")
    name = message[1].replace("+", " ")
    return name.strip()


def get_arrival_time():
    local_tz = pytz.timezone("US/Mountain")
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return now.ctime()


def welcome_number_message(message):
    message = "Welcome to the event, " + get_name(message) + ". You have been added to our lists."
    message += " If you are ever in need of immediate help during the event, please text me the word help."
    message += " I will then notify our sober brothers (the people wearing bandanas on their arms) as well as"
    message += " a few other people to ensure you get the help you need. Be safe and have a great day."
    return message


def number_exists_message():
    message = "Oops, it looks like the phone number you sent this message from"
    message += " is already at the event. Please talk with one of the people at the event's entrance if you"
    message += " believe this to be an error."
    return message


def no_event_message():
    message = "Hi there. It doesn't look like there's an event going on right now."
    message += " If you are in need of emergency assistance or are in physical danger, please contact:"
    message += "\nDenver Police Emergency Number: 911"
    message += "\nCampus Police Emergency Number: (303)-871-3000"
    message += "\n\nAlternatively, if you are in a non-emergency situation:"
    message += "\nDenver Police Non-Emergency: (720)-913-2000"
    message += "\nCampus Safety Non-Emergency: (303)-871-3130"
    return message


def incorrect_keyword_message():
    message = "I'm sorry. Some part of your message was strange."
    message += " Please ensure your message is in the format:"
    message += "\nkeyword, firstname lastname"
    message += "\n and try agin."
    return message


def dictify_message(message):
    dictionary = {}

    for entry in message:
        try:
            current = entry.split("=")
            key = current[0]
            value = urllib.parse.unquote(current[1])
            dictionary[key] = value
        except TypeError as e:
            continue

    return dictionary
