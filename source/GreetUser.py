import urllib
import json
import os
import random


# Method greets the user using their name.
def greet(user_id):
    name = get_user_info(user_id)

    # Greetings to select from.
    greetings = ["Hi", "Hello", "Hey", "What\'s up",
               "Waddup", "How are we", "Howdy", "Yo",
               "Good day", "What's poppin", "What\'s crackalakin'",
               "Hi there", "Hello there", "Hey there", "Howdy there",
               "Hello there"]

    greeting_num = random.randint(0, len(greetings) - 1)
    return greetings[greeting_num] + " " + name + "."


# Getting the user information from the slack API.
def get_user_info(user_id):
    try:
        slack_url_special = "https://slack.com/api/users.info"

        data = urllib.parse.urlencode(
            (
                ("token", os.environ["BOT_TOKEN"]),
                ("user", user_id),
                ("include_locale", 'false')
            )
        )

        data = data.encode("ascii")
        request2 = urllib.request.Request(slack_url_special, data=data, method="POST")

        request2.add_header(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

        # Getting response from server and turning it into a dict.
        user_data = json.loads((urllib.request.urlopen(request2).read()).decode())

    except Exception as e:
        print(e)

    # Giving back the real name of the user.
    return user_data["user"]["real_name"]
