import urllib
import json
import os
import random

def greet(userid):
    name = getuserinfo(userid)
    greetings = ["Hi", "Hello", "Hey", "What\'s up",
               "Waddup", "How are we", "Howdy", "Yo",
               "Good day", "What's poppin", "What's crackalakin'",
               "Hi there", "Hello there", "Hey there", "Howdy there",
               ]

    greetingNum = random.randint(0, len(greetings) - 1)
    return greetings[greetingNum] + " " + name


def getuserinfo(userID):
    try:
        SLACK_URL_SPECIAL = "https://slack.com/api/users.info"
        data = urllib.parse.urlencode(
            (
                ("token", os.environ["BOT_TOKEN"]),
                ("user", userID),
                ("include_locale", 'false')
            )
        )

        data = data.encode("ascii")
        request2 = urllib.request.Request(SLACK_URL_SPECIAL, data=data, method="POST")

        request2.add_header(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

        # Getting reponse from server and turning it into a dict.
        userdata = json.loads((urllib.request.urlopen(request2).read()).decode())

    except Exception as e:
        print(e)

    return userdata["user"]["real_name"]
