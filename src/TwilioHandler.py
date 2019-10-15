import os
import base64
from urllib import request, parse


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