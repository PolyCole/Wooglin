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
        if message['Body'].lower().find('help') != -1:
            start_help_handler(message)
            return "200 OK"

        dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        table = dynamodb.Table(os.environ['current_party'])

        response = table.query(
            KeyConditionExpression=Key('number').eq(message['From'])
        )

        if response['Count'] != 0 and response['Items'][0]['help_flag']:
            notify_parties(response['Items'][0]['name'], message['Body'])
            SMSHandler.sendsms(response['Items'][0]['number'], "Successfully forwarded.")
            return "200 OK"

        if not validate_keyword(message['Body']):
            SMSHandler.sendsms(message['From'], incorrect_keyword_message())
            return "200 OK"

        if response['Count'] == 0:
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


def process_message(message):
    message = message.replace("+", " ")
    return message.strip()


def get_arrival_time():
    local_tz = pytz.timezone("US/Mountain")
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return now.ctime()


def welcome_number_message(message):
    message = "Welcome to the event, " + get_name(message) + ". You have been added to our lists."
    message += " If you are ever in need of immediate help during the event, please text me the phrase \"help me\"."
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
    message += "\nEmergency: 911"
    message += "\nCamPo Emergency: (303)-871-3000"
    message += "\n\nAlternatively, if you are in a non-emergency situation:"
    message += "\nDenver PD Non-Emergency: (720)-913-2000"
    message += "\nCamPo Non-Emergency: (303)-871-3130"
    return message


def incorrect_keyword_message():
    message = "I'm sorry. Some part of your message was strange."
    message += " Please ensure your message is in the format:"
    message += "\nkeyword, firstname lastname"
    message += "\n and try agin."
    return message


def immediate_help_message():
    message = "First and foremost, if you are in immediate danger or a life threatening situation contact "
    message += "one of the following: "
    message += "\nEmergency: 911"
    message += "\nCamPo Emergency: (303)-871-3000"
    message += "\n\nOr, if you're not in immediate danger:"
    message += "\nDenver PD Non-Emergency: (720)-913-2000"
    message += "\nCamPo Non-Emergency: (303)-871-3130"
    return message


def whats_next_message():
    message = "I have notified the sober brothers and the executive board that you are in need of immediate assistance."
    message += " From this point onward, any message that you send to me will"
    message += " be forwarded to both the sober brothers and the executive board."
    message += " Please start by responding with your location, please be as exact as possible."
    return message


def alert_message(name):
    message = "*****ALERT*****\n" + name + " has said they require immediate assistance."
    message += " I will now forward all messages received by " + name
    message += ". If the situation is serious, DO NOT HESITATE to call 911 and Campo's Emergency line: (303)-871-3000"
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


def start_help_handler(message):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(os.environ['current_party'])

    response = table.query(
        KeyConditionExpression=Key('number').eq(message['From'])
    )

    name = ""

    if response['Count'] == 0:
        table.put_item(
            Item={
                'number': message['From'],
                'name': name,
                'arrived': get_arrival_time(),
                'help_flag': True,
                'help_flag_raised': get_arrival_time()
            }
        )
    else:
        name = response['Items'][0]['name']
        table.put_item(
            Item={
                'number': response['Items'][0]['number'],
                'name': response['Items'][0]['name'],
                'arrived': response['Items'][0]['arrived'],
                'help_flag': True,
                'help_flag_raised': get_arrival_time()
            }
        )

    SMSHandler.sendsms(message['From'], immediate_help_message())
    notify_parties(name)
    SMSHandler.sendsms(message['From'], whats_next_message())


def notify_parties(name, message="nomessage"):
    if message == "nomessage":
        SMSHandler.send_sms_exec(alert_message(name))
        # SMSHandler.send_sms_soberbros(alert_message(name))
        # SMSHandler.sendsms("+19522559343", alert_message(name))
    else:
        SMSHandler.send_sms_exec("Message from " + name + ": " + process_message(message))
        # SMSHandler.send_sms_soberbros("Message from " + name + ": " + process_message(message))
        # SMSHandler.sendsms("+19522559343", "Message from " + name + ": " + process_message(message))
