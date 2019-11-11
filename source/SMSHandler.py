import os, base64, datetime, boto3
from urllib import request, parse
from source import DatabaseHandler, wooglin
from boto3.dynamodb.conditions import Key


def smshandler(resp):
    try:
        message = resp['entities']['key'][0]['value']
    except KeyError as e:
        wooglin.sendmessage("Uh-oh. Looks like I wasn't able to discern what you wanted me to send. Talk to Cole.")
        return

    try:
        key = resp['entities']['key'][0]['value']
        individual_sms(key, message);
        return
    except KeyError as e:
        print("No key specified... Could be a group message...")

    try:
        smslist = resp['entities']['smslist'][0]['value']

        if smslist == "chapter":
            send_sms_chapter(message)
            return
        elif smslist == "exec":
            return
        elif smslist == "soberbros":
            send_sms_soberbros(message)
            return
    except KeyError as e:
        wooglin.sendmessage("Oops. It looks like neither a name nor a smslist was specified. Talk to Cole.")
        return


def individual_sms(key, message):
    phone_number = get_phone_number(key)
    resp = sendsms(phone_number, message)
    wooglin.sendmessage("Alright! I've sent a message saying, " + str(message) + " to " + str(key))


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
    SoberBros.append(response[0]['soberbro4'].strip())
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
        "Luke Srsen",
        "Evan Prechodko",
        "Cole Polyak",
        "Tom Oexeman",
        "Adam Snow",
        "Deegan Coles",
        "Rex Fathauer",
        "Caleb Bruce",
        "Cade Carter",
        "Quinn Merrell"
    ]

    errors = []

    for person in exec_members:
        number = get_phone_number(person)
        resp  = sendsms(number, message)
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


def sendsms(number, message):
    # TODO add in code to make this message only rturn true when message went through.

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
        return False
    return True