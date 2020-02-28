import os
import datetime
import boto3
import pytz
import DatabaseHandler
import wooglin
from boto3.dynamodb.conditions import Key
from twilio.rest import Client


# The general handler for SMS operations.
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
        individual_sms_name(key, message);
        return
    except KeyError:
        print("No key specified... Could be a group message...")

    # No key given, let's see if there's a smslist specified.
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


# Handler for one person.
def individual_sms_name(key, message):
    phone_number = get_phone_number(key)
    resp = sendsms(phone_number, message)
    wooglin.sendmessage("Alright! I've sent a message saying, \n[" + str(message) + "]\n to " + str(key))
    return


# Sends an sms message to the entire chapter.
def send_sms_chapter(message):
    data = DatabaseHandler.scanTable('members')

    account_sid = os.environ["TWILIO_SID"]
    auth_token = os.environ["TWILIO_TOKEN"]
    client = Client(account_sid, auth_token)

    for person in data:
        try:
            number = person['phonenumber']

            binding_message = '{"binding_type":"sms", "address":"' + fix_phone_number_format(number) + '\"}'

            notification = client.notify.services(os.environ['TWILIO_NOTIFY_SERVICE_SID']) \
                .notifications.create(to_binding=binding_message, body=message)
        # On the off chance someone has blacklisted Wooglin.
        except Exception as e:
            print("Errored on: " + number + " which should be: " + person['name'])
            continue

    if notification:
        wooglin.sendmessage("Alrighty! I have notified the chapter: " + message)
    else:
        wooglin.sendmessage("I was unable to send that message to the chapter.")


# Sends an sms message to the active sober bros.
def send_sms_soberbros(message):
    # Correcting for our timezone. Default is UTC.
    local_tz = pytz.timezone("US/Mountain")
    now = datetime.datetime.now()
    now = now.replace(tzinfo=pytz.utc).astimezone(local_tz)
    current_date = now.isoformat()[0:10]

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table('soberbros')

    response = table.query(
        KeyConditionExpression=Key('date').eq(current_date)
    )

    if len(response['Items']) == 0:
        message = "Looks like there aren't any sober bros for " + str(DatabaseHandler.unprocessDate(current_date)) + ".\n Thus, I was unable to send them a message."
        wooglin.sendmessage(message)
        return

    response = response['Items']

    SoberBros = []
    SoberBros.append(response[0]['soberbro1'].strip())
    SoberBros.append(response[0]['soberbro2'].strip())
    SoberBros.append(response[0]['soberbro3'].strip())
    SoberBros.append(response[0]['soberbro4'].strip())
    SoberBros.append(response[0]['soberbro5'].strip())
    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    errors = []

    # Notifies sober bros.
    for person in SoberBros:
        number = get_phone_number(person)
        try:
            sendsms(number, message)
        except Exception as e:
            errors.append(person)

    # All messages went through without issue.
    if len(errors) == 0:
        date_formatted = DatabaseHandler.unprocessDate(current_date)
        confirmation = "I've successfully sent the sober bros for " + date_formatted + " the message: "
        confirmation += message
        wooglin.sendmessage(confirmation)
        return
    # Messages went through with partial success.
    else:
        message = "Okay. I've had some marginal success."
        message += "I was partially able to notify the sober bros. I was unable to notify:\n"
        for person in errors:
            message += person + ","
        wooglin.sendmessage(message)


# Sends a text message to the executive board.
# TODO need to update this once Quinn steps down.
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
        "Kyle Waggoner"
    ]

    errors = []
    message = "Message for the Executive Board: " + message

    # Sends to each exec member.
    for person in exec_members:
        print("Trying to notify: " + person)
        number = get_phone_number(person)
        resp = sendsms(number, message)
        if not resp:
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


# Gets the phone number of the given person.
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


# Creates the sober bro message to be sent to the chapter.
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
    SoberBros.append((response[0])['soberbro4'].strip())
    SoberBros.append((response[0])['soberbro5'].strip())

    print(SoberBros)
    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    message = "Here are the sober bros for " + str(DatabaseHandler.unprocessDate(date)) + ": \n"

    # Gets each of the Sober bro's phone number.
    for person in SoberBros:
        message += str(person)
        number = get_phone_number(person)
        message += " (" + str(number) + ")\n"
    message += "If you are in need of assistance, please contact one of these people."

    print("CSBM returned: " + message)
    return message


# Sends an sms message to the given number.
def sendsms(number, message):
    # TODO add in code to make this message only return true when message went through.

    # Ensures proper phone number format.
    number = fix_phone_number_format(number)
    print("Number fixed: " + str(number))

    account_sid = os.environ["TWILIO_SID"]
    auth_token = os.environ["TWILIO_TOKEN"]
    client = Client(account_sid, auth_token)

    # Sends the message!
    message = client.messages.create(
        body=message,
        from_=os.environ["TWILIO_MESSAGING_SERVICE_SID"],
        to=number
    )
    print("Message: " + str(message))

    # TODO Ensure that when message fails, user gets notice.
    return True


# Ensures we're in the proper phone number format.
def fix_phone_number_format(number):
    if number.find('+1') != -1:
        return number

    split = number.split(".")
    new_number = "+1"

    for x in range(len(split)):
        new_number += split[x]

    return new_number
