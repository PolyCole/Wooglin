import os
import time
import base64
import datetime
import boto3
from urllib import request, parse
import DatabaseHandler
import wooglin
from boto3.dynamodb.conditions import Key
from twilio.rest import Client

def smshandler(resp):
    try:
        message = resp['entities']['message'][0]['value']
    except KeyError:
        wooglin.sendmessage("Uh-oh. Looks like I wasn't able to discern what you wanted me to send. Talk to Cole.")
        return

    print("Trying to send message : " + str(message))

    # Ensuring we get the proper date regardless of syntax used.
    if message == "ListSoberBros":
        try:
            date = resp['entities']['datetime'][0]['value']
        except KeyError:
            try:
                date = resp['entities']['datetime'][0]['from']['value']
            except KeyError:
                now = datetime.datetime.now()
                date = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
        message = create_sober_bro_message(date)

    try:
        key = resp['entities']['key'][0]['value']
        individual_sms(key, message);
        return
    except KeyError:
        print("No key specified... Could be a group message...")

    try:
        smslist = resp['entities']['smslist'][0]['value']

        if smslist == "chapter":
            send_sms_chapter(message)
            return
        elif smslist == "exec":
            send_sms_exec(message)
            return
        elif smslist == "soberbros":
            send_sms_soberbros(message)
            return
    except KeyError:
        wooglin.sendmessage("Oops. It looks like neither a name nor a smslist was specified. Talk to Cole.")
        return


def individual_sms(key, message):
    phone_number = get_phone_number(key)
    resp = sendsms(phone_number, message)
    wooglin.sendmessage("Alright! I've sent a message saying, \n[" + str(message) + "]\n to " + str(key))
    return


# TODO NEED TO ENSURE THIS WORKS WITH TWILIO
def send_sms_chapter(message):
    data = DatabaseHandler.scanTable('members')
    for person in data:
        number = person['phonenumber']
        response = sendsms(number, message)

    if response:
        wooglin.sendmessage("Alrighty! I have notified the chapter: " + message)
    else:
        wooglin.sendmessage("I was unable to send that message to the chapter.")


def send_sms_soberbros(message):
    now = datetime.datetime.now()
    date = str(now.year) + "-" + str(now.month) + "-" + str(now.day)

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('soberbros')

    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )

    if len(response['Items']) == 0:
        message = "Looks like there aren't any sober bros for " + str(DatabaseHandler.unprocessDate(date)) + ".\n Thus, I was unable to send them a message."
        wooglin.sendmessage(message)
        return

    SoberBros = []
    SoberBros.append(response[0]['soberbro1'].strip())
    SoberBros.append(response[0]['soberbro2'].strip())
    SoberBros.append(response[0]['soberbro3'].strip())
    # SoberBros.append(response[0]['soberbro4'].strip())
    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    errors = []

    for person in SoberBros:
        number = get_phone_number(person)
        try:
            sendsms(number, message)
        except Exception as e:
            errors.append(person)

    if len(errors) == 0:
        date_formatted = DatabaseHandler.unprocessDate(date)
        confirmation = "I've successfully sent the sober bros for " + date_formatted + " the message: "
        confirmation += message
        wooglin.sendmessage(confirmation)
        return

    else:
        message = "Okay. I've had some marginal success."
        message += "I was partially able to notify the sober bros. I was unable to notify:\n"
        for person in errors:
            message += person + ","
        wooglin.sendmessage(message)


def send_sms_exec(message):
    exec_members = [
        "Cole Polyak",
        "Luke Srsen",
        "Evan Prechodko",
        "Thomas Oexeman",
        "Adam Snow",
        "Deegan Coles",
        "Rex Fathauer",
        "Caleb Bruce",
        "Cade Carter",
        "Quinn Merrell"
    ]

    errors = []
    message = "Message for the Executive Board: " + message

    for person in exec_members:
        print("Trying to notify: " + person)
        number = get_phone_number(person)
        resp = sendsms(number, message)
        if (not resp):
            errors.append(person)

    if len(errors) == 0:
        wooglin.sendmessage("I successfully sent the executive board: " + message)
    else:
        message = "Okay. I've had some marginal success."
        message += "I was partially able to notify the executive board. I was unable to notify:\n"
        for person in errors:
            message += person + ","
        wooglin.sendmessage(message)
    return


def get_phone_number(key):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('members')

    resp = table.query(
        KeyConditionExpression=Key('name').eq(key)
    )

    try:
        number = resp['Items'][0]['phonenumber']
    except KeyError as e:
        wooglin.sendmessage("Uh-oh. Looks like " + str(key) + " doesn't have a listed phonenumber.")

    return number


def create_sober_bro_message(date):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('soberbros')

    date = date[0:10]

    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )

    response = response['Items']

    if len(response) == 0:
        message = "Looks like there aren't any sober bros for " + str(DatabaseHandler.unprocessDate(date))
        return message

    SoberBros = []
    SoberBros.append((response[0])['soberbro1'].strip())
    SoberBros.append((response[0])['soberbro2'].strip())
    SoberBros.append((response[0])['soberbro3'].strip())

    print(SoberBros)
    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    message = "Here are the sober bros for " + str(DatabaseHandler.unprocessDate(date)) + ": \n"

    for person in SoberBros:
        message += str(person)
        number = get_phone_number(person)
        message += " (" + str(number) + ")\n"
    message += "If you are in need of assistance, please contact one of these people."
    print("CSBM returned: " + message)
    return message

def sendsms(number, message):
    # TODO add in code to make this message only return true when message went through.

    # insert Twilio Account SID into the REST API URL
    # populated_url = os.environ["TWILIO_SMS_URL"].format(os.environ["TWILIO_SID"])

    number = fix_phone_number_format(number)
    print("Number fixed: " + str(number))

    account_sid = os.environ["TWILIO_SID"]
    auth_token = os.environ["TWILIO_TOKEN"]
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
        body=message,
        from_=os.environ["TWILIO_NUMBER"],
        to=number
    )

    print("Message: " + str(message))
    time.sleep(4)

    # TODO Ensure that when message fails, user gets notice.
    return True


def fix_phone_number_format(number):
    split = number.split(".")
    new_number = "+1"

    for x in range(len(split)):
        new_number += split[x]

    return new_number