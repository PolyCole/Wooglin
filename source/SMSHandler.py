import os
import base64
from urllib import request, parse
from source import DatabaseHandler, wooglin

def smshandler(resp):
    key = resp['entities']['key'][0]['value']
    message = resp['entities']['key'][0]['value']

    if key == "chapter":
        data = DatabaseHandler.scanTable('members')
        for person in data:
            number = person['phonenumber']
            response = sendsms(number, message)
        if response:
            wooglin.sendmessage("Alrighty! I have notified the chapter: " + message)
        else:
            wooglin.sendmessage("I was unable to send that message to the chapter.")
    elif key == "exec":
        data = DatabaseHandler.scanTable('members')
        for x in range(10):
            number = data[x]['phonenumber']

            # TODO add in phone number format verification.
            # Perhaps this makes more sense when phone number is inputted.
            # Irrelevant if Twilio does this for us inherently.
            response = sendsms(number, message)
        if response:
            wooglin.sendmessage("I successfully notified the executive board: " + message)
        else:
            wooglin.sendmessage("I'm sorry, I was unable to tell exec that.")
    elif key == "soberbros":
        temp = 1
        print(temp)
        # TODO Implement logic for determining and notifying sober bros that evening.

        wooglin.sendmessage("I have texted the sober bros: " + message)
    else:
        print("I'm trying to send: " + message)
        # TODO RE-INSTATE ME ONCE WE HAVE TWILIO CREDS
        # response = sendsms(key, message)
        response = True

        if response:
            wooglin.sendmessage("Success! I sent " + key + " the message: " + message)
        else:
            wooglin.sendmessage("Something has gone wrong. I was unable to send that message.")


def sendsms(number, message):
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