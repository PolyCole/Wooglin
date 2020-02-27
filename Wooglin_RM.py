import urllib
import boto3
import pytz
from boto3.dynamodb.conditions import Key
import SMSHandler
import datetime
import base64
import wooglin


# The general handler for risk management features.
def handler(data):
    data['body'] = data['body'].encode()

    # We have to decode the message as its sent in base 64.
    message_parsed = (base64.b64decode(data['body']))
    message_parsed = message_parsed.decode().split('&')

    message = dictify_message(message_parsed)
    current_event = get_current_event()

    # No event going on rn.
    if current_event == "none":
        SMSHandler.sendsms(message['From'], no_event_message())
        return "200 OK"
    else:
        # Trigger for help flag raising.
        if message['Body'].lower().find('help') != -1:
            start_help_handler(message)
            return "200 OK"

        dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
        table = dynamodb.Table(current_event)

        response = table.query(
            KeyConditionExpression=Key('number').eq(message['From'])
        )

        # If the number exists in our db and their flag is raised, let's forward their messages
        if response['Count'] != 0 and response['Items'][0]['help_flag']:
            notify_parties(response['Items'][0]['name'], message['Body'])
            SMSHandler.sendsms(response['Items'][0]['number'], "Successfully forwarded.")
            return "200 OK"

        # If the sender didn't have the keyword correct.
        if get_keyword() != "none":
            if not validate_keyword(message['Body']):
                SMSHandler.sendsms(message['From'], incorrect_keyword_message())
                return "200 OK"

        # Ensuring the number doesn't exist in the DB yet.
        if response['Count'] == 0:
            SMSHandler.sendsms(message['From'], welcome_number_message(message['Body']))

            table.put_item(
                Item={
                    'number': message['From'],
                    'name': get_name(message['Body']),
                    'arrived': get_arrival_time(),
                    'help_flag': False,
                    'help_flag_raised': "n/a"
                }
            )

            current_guests = increment_guests(current_event)

            # Number of people attending the event.
            if current_guests % 50 == 0:
                wooglin.sendmessage("The current event: " + current_event + " has " + str(current_guests) + " guests registered.")

        else:
            SMSHandler.sendsms(message['From'], number_exists_message())
            return "200 OK"


def increment_guests(current_event):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("events")

    response = table.query(
        KeyConditionExpression=Key('name').eq(current_event)
    )

    guests = int(response['Items'][0]['guest_count']) + 1

    table.put_item(
        Item={
            'name': current_event,
            'comments': response['Items'][0]['comments'],
            'end_time': response['Items'][0]['end_time'],
            'guest_count': str(guests),
            'start_time': response['Items'][0]['start_time']
        }
    )

    return guests


# Validates that the keyword given matches the actual keyword.
def validate_keyword(message):
    message = message.replace("+", " ")
    message = message.split(" ")
    message = [x for x in message if x != ""]

    if len(message) < 2:
        return False

    if message[0].strip().lower() != get_keyword():
        return False

    return True


# Grabs the current keyword from the db.
def get_keyword():
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table("events")
    response = table.query(KeyConditionExpression=Key('name').eq('active'))['Items'][0]['keyword']
    return response


# Grabs the current event name from the db.
def get_current_event():
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('events')
    response = table.query(KeyConditionExpression=Key('name').eq('active'))['Items'][0]['comments']
    return response


# Gets the name from the given message.
def get_name(message):
    message = message.replace("+", " ")
    message = message.split(" ")
    message = [x for x in message if x != ""]

    offset = 0 if get_keyword() == "none" else 1
    name = ""
    for x in range(offset, len(message)):
        name += message[x] + " "

    return name.strip()


# Processes the actual text from the message by removing the + signs.
def process_message(message):
    message = message.replace("+", " ")
    return message.strip()


# Gets the current time to be marked as the guest's arrival time.
def get_arrival_time():
    local_tz = pytz.timezone("US/Mountain")
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return now.ctime()


def welcome_number_message(message):
    message = "Welcome to the event, " + get_name(message) + ". You have been added to our lists."
    message += " If you are ever in need of immediate emergency assistance during the event, " \
               "please text me the phrase \"help me\"."
    message += " Additionally, if you need help but aren't in an emergency situation, " \
               "find one of our sober brothers (the guys wearing pink bandanas on their arms), "
    message += " they would be happy to help. Be safe and have a great day."
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
    message += "\nkeyword firstname lastname"
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
    message += " be forwarded to both of those groups."
    message += " Please start by responding with your location, please be as exact as possible."
    return message


def alert_message(name, number):
    message = "*****ALERT*****\n" + name + " (" + number + ") has said they require immediate assistance."
    message += " I will now forward all messages received from " + name
    message += ". If the situation is serious, DO NOT HESITATE to call 911 and Campo's Emergency line: (303)-871-3000"
    return message


# Takes the base64 decoded string and turns it into a dictionary for easier handling.
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


# Starts the ball rolling on the help process.
def start_help_handler(message):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(get_current_event())

    response = table.query(
        KeyConditionExpression=Key('number').eq(message['From'])
    )

    name = ""

    # On the off chance we have someone who isn't registered at the event but still needs help.
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
    notify_parties(name, message['From'])
    SMSHandler.sendsms(message['From'], whats_next_message())


# Notifies the sober bros and the executive board.
def notify_parties(name, number, message="nomessage"):
    if message == "nomessage":
        # SMSHandler.send_sms_exec(alert_message(name, number))
        # SMSHandler.send_sms_soberbros(alert_message(name, number))
        SMSHandler.sendsms("+19522559343", alert_message(name, number))
    else:
        # SMSHandler.send_sms_exec("Message from " + name + " (" + number + "): " + process_message(message))
        # SMSHandler.send_sms_soberbros("Message from " + name + " (" + number + "): " + process_message(message))
        SMSHandler.sendsms("+19522559343", alert_message(name,number))