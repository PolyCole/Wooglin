import boto3
import datetime
from boto3.dynamodb.conditions import Key, Attr
import wooglin
import Wooglin_RM


# Checks if the current slack event has already been handled.
def event_handled(event_id, event_time):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table("event_ids")

    response = table.query(
        KeyConditionExpression=Key('event_id').eq(event_id)
    )

    # Hasn't been handled, let's add it to DB.
    if response['Count'] == 0:
        table.put_item(
            Item={
                'event_id': event_id,
                'event_time': event_time
            }
        )
    else:
        # Event has been taken care of.
        previous_event_time = response['Items'][0]['event_time']
        if previous_event_time == event_time:
            print("Event already being handled, terminating")
            return True
    return False


# The generic handler for all Database Operations.
def dbhandler(resp, user):
    # First, what are we doing?
    operation = resp['entities']['db_operation'][0]['value']

    # Event creation.
    if "eventname" in resp['entities'] or "new_keyword" in resp['entities']:
        event_operation_handler(operation, resp)
        return "200 OK"

    # We probably have a key.
    try:
        key = resp['entities']['key']
    except KeyError as e:
        key = ""

    # User specified an attribute.
    try:
        attribute = resp['entities']['attribute'][0]['value']
    except KeyError as e:
        attribute = ""

    # User didn't specify a table, probably members.
    try:
        table = resp['entities']['table'][0]['value']
    except KeyError as e:
        table = "members"


    print("key: " + str(key))
    print("table: " + str(table))
    print("attribute: " + str(attribute))

    # TODO clean up this garbage routing table.
    if operation == "get":
        if table == "soberbros":
            date = extract_date(resp)
            print("Passing with get sober bros request: " + str(date))
            getOperationSoberBros(table, date)
        else:
            getOperation(table,key, attribute)
    elif operation == "modify":
        modifyOperation(resp,table,key)
    elif operation == "close_event":
        event_operation_handler(operation, resp)
    elif operation == "delete":
        if table == "soberbros":
            date = extract_date(resp)
            sober_bro_deassign("soberbros", key, date)
        else:
            deleteOperation(table, key, user)
    elif operation == "create":
        createOperation(table, key)
    elif operation == "assign":
        date = extract_date(resp)
        sober_bro_assign("soberbros", key, date)
    elif operation == "deassign":
        date = extract_date(resp)
        sober_bro_deassign("soberbros", key, date)
    else:
        wooglin.sendmessage("I'm sorry, that database functionality is either not understood or not supported")


# Handles the event logic.
def event_operation_handler(operation, resp):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    # Creating an event.
    if operation == "create":
        response = dynamodb.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'number',
                    'AttributeType': 'S',
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'number',
                    'KeyType': 'HASH',
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5,
            },
            TableName=resp['entities']['eventname'][0]['value'],
        )

        # Adding event to events db.
        table = dynamodb.Table('events')
        table.put_item(
            Item={
                'name':resp['entities']['eventname'][0]['value'],
                'start_time': Wooglin_RM.get_arrival_time(),
                'end_time': "currently active",
                'guest_count': 0,
                'comments': "none"
            }
        )

        keyword = "none"

        # Did the user specify a keyword at inception?
        if 'new_keyword' in resp['entities']:
            keyword = resp['entities']['new_keyword'][0]['value']

        # Updating live entry.
        table.put_item(
            Item={
                'name': "active",
                'comments': resp['entities']['eventname'][0]['value'],
                'keyword': keyword
            }
        )

        # Yup. We got a keyword.
        if 'new_keyword' in resp['entities']:
            wooglin.sendmessage("I have successfully created an event called : " +
                                resp['entities']['eventname'][0]['value'] + ", with keyword " +
                                resp['entities']['new_keyword'][0]['value'])
        # No keyword.
        else:
            wooglin.sendmessage("I have successfully created an event called: " +
                                resp['entities']['eventname'][0]['value'] + ". There is currently no keyword.")

    # Closing the current active event.
    elif operation == "close_event":
        table = dynamodb.Table('events');

        response = table.query(KeyConditionExpression=Key('name').eq('active'))['Items'][0]

        if response['comments'] == "none":
            wooglin.sendmessage("Yikes. Doesn't look like there's an event going on right now.")

        print("Terminating event: " + response['comments'])

        # Erasing the current party's active listing.
        table.put_item(
            Item={
                'name': "active",
                'comments': "none",
                'keyword': "none"
            }
        )

        # Grabbing the party's data from the events db.
        initial_data = table.query(KeyConditionExpression=Key('name').eq(response['comments']))

        # Putting the new information about the party into the db.
        table.put_item(
            Item={
                'name': initial_data['Items'][0]['name'],
                'start_time': initial_data['Items'][0]['start_time'],
                'end_time': Wooglin_RM.get_arrival_time(),
                'guest_count': initial_data['Items'][0]['guest_count'],
                'comments': "Terminated by Wooglin."
            }
        )

        wooglin.sendmessage("I have closed the current event. Somebody cue unwritten followed by closing time.")
    # We're modifying the keyword.
    elif operation == "modify":
        table = dynamodb.Table('events')

        response = table.query(KeyConditionExpression=Key('name').eq('active'))['Items'][0]

        # No event happening.
        if response['comments'] == "none":
            wooglin.sendmessage("Doesn't look like there's an event going on right now. I wasn't able to update the keyword.")
            return "200 OK"

        # Let's update that keyword.
        table.put_item(
            Item={
                'name': 'active',
                'comments': response['comments'],
                'keyword': resp['entities']['new_keyword'][0]['value']
            }
        )
        wooglin.sendmessage("I have updated the new event keyword to be: " + resp['entities']['new_keyword'][0]['value'])


# Takes the date from Wit and turns it into something DynamoDB can understand.
def extract_date(resp):
    try:
        date = resp['entities']['datetime'][0]['value']
    except KeyError as e:
        date = resp['entities']['datetime'][0]['from']['value']
    return date[0:10]


# Handles get operations to the DB.
def getOperation(table, key, attribute):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    tablename = table
    table = dynamodb.Table(table)

    # Handling for getting a list of users.
    if isinstance(key, list):
        print("In list option")
        for x in range(len(key)):
            # Getting the item!
            response = table.query(
                KeyConditionExpression=Key('name').eq(key[x]['value'])
            )

            print("Get operation returned: " + str(response))
            wooglin.sendmessage(stringify_member(response['Items'], tablename, key, attribute))
    elif isinstance(key, dict):
        # Getting one key.
        print("In dict option")
        # Getting the item!

        print("Starting get request with key : " + key[0]['value'])

        response = table.query(
            KeyConditionExpression=Key('name').eq(key[0]['value'])
        )

        print("Get operation returned: " + str(response))
        wooglin.sendmessage(stringify_member(response['Items'], tablename, key, attribute))
    elif isinstance(key, str):
        print("In String option!")
        print(str(key))
    else:
        print("I'm not entirely sure how key was put into " + str(type(key)) + " but it was an I'm confused.")


# Handles get operations on the sober bro table.
def getOperationSoberBros(table, date):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table)

    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )

    if len(response['Items']) == 0:
        message = "Looks like there aren't any sober bro shifts for " + str(unprocessDate(date)) + " yet."
        wooglin.sendmessage(message)
        return

    wooglin.sendmessage(stringify_soberbros(response['Items']))


# Returns all values in the given table.
def scanTable(tablename):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(tablename)
    return table.scan()['Items']


# Handles modify operations on members table.
def modifyOperation(resp, table, key):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    tablename = table
    table = dynamodb.Table(table)

    target = table.query(
        KeyConditionExpression=Key('name').eq(key[0]['value'])
    )

    # Our target doesn't exist in the table.
    if len(target) == 0:
        wooglin.sendmessage(stringify_member(target, tablename, key, ""))
        return

    attribute = resp['entities']['attribute'][0]['value']
    new_value = resp['entities']['new_value'][0]['value']

    print("attribute: " + str(attribute))
    print("new_value: " + str(new_value))

    response = table.update_item(
        Key={
            'name': key[0]['value']
        },
        UpdateExpression='SET ' + str(attribute) + ' = :val1',
        ExpressionAttributeValues={
            ':val1': new_value
        }
    )

    wooglin.sendmessage(stringify_update(response, key[0]['value'], attribute, new_value))


# Assigns a sober bro on a given date.
def sober_bro_assign(tablename, key, date):
    SoberBros = list_sober_bros(tablename, date)
    key = key[0]['value']

    # We only want actual sober bros in the list.
    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    if len(SoberBros) == 5:
        wooglin.sendmessage("It looks like the sober bro shift on " + str(
            unprocessDate(date)) + " is already full. I couldn't add " + str(key))
        return

    if SoberBros.count(key) == 1:
        wooglin.sendmessage(
            "Whoops! It looks like " + str(key) + " is already a sober bro on " + str(unprocessDate(date)))
        return

    SoberBros.append(key)

    message = "Alrighty! I've added " + str(key) + " to the sober bro shift on " + str(unprocessDate(date)) + ".\nThere are now " + str(len(SoberBros)) + " sober brothers on that date."

    # Gotta have the proper grammar...
    if len(SoberBros) == 1:
        left = message.split("are")
        right = left[1].split("brothers")
        message = left[0] + "is" + right[0] + "brother" + right[1]

    while len(SoberBros) != 5:
        SoberBros.append("NO ONE")

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(tablename)
    table.put_item(
        Item={
            'date': date,
            'soberbro1': SoberBros[0],
            'soberbro2': SoberBros[1],
            'soberbro3': SoberBros[2],
            'soberbro4': SoberBros[3],
            'soberbro5': SoberBros[4]
        }
    )

    wooglin.sendmessage(message)


# Handles delete operations in the members table.
def deleteOperation(table, key, user):
    # TODO Change this into a method in a handler. Perhaps a boto3 handler?
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table)
    backup_table = dynamodb.Table('members_backup')

    peopleIveDeleted = ""

    for x in range(len(key)):
        print("Delete is attempting to DELETE: " + str(key[x]['value']))

        entry = table.query(
            KeyConditionExpression=Key('name').eq(key[x]['value'])
        )

        # Backing up the entry in the case of accidental deletion.
        backup_entry(entry, backup_table)

        response = table.delete_item(
            Key={
                'name': key[x]['value']
            }
        )

        peopleIveDeleted += str(key[x]['value']) + ", "
    wooglin.sendmessage("Well I've done it. If " + str(peopleIveDeleted[:len(peopleIveDeleted)-2]) + " existed before, they don't now. If you accidentally deleted someone, contact Cole.")


# Let's back up the entry in another DB just in case.
def backup_entry(entry, backup_table):
    entry = entry['Items'][0]
    backup_table.put_item(
        Item={
            'name': entry['name'],
            'phonenumber': entry['phonenumber'],
            'rollnumber': entry['rollnumber'],
            'address': entry['address'],
            'email': entry['email'],
            'present': entry['present'],
            'unexcused': entry['unexcused'],
            'excused': entry['excused'],
            'excuses': entry['excuses'],
            'absences': entry['absences']
        }
    )

    print("Alrighty. I completed the operation, but I just added the entry to the backup table just to be sure.")


# Deassigns the specified sober bro.
def sober_bro_deassign(tablename, key, date):
    SoberBros = list_sober_bros(tablename, date)
    key = key[0]['value']

    # Only want active sober bro listings.
    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    try:
        SoberBros.remove(key)
    except ValueError:
        wooglin.sendmessage(
            "Oops. It looks like " + str(key) + " is not currently a sober bro on " + str(unprocessDate(date)))
        return

    message = "Alrighty! I've removed " + str(key) + " from the sober bro shift on " + str(
        unprocessDate(date)) + ".\nThere are now " + str(len(SoberBros)) + " sober brothers on that date."

    # Gotta have the proper grammar...
    if len(SoberBros) == 1:
        left = message.split("are")
        right = left[1].split("brothers")
        message = left[0] + "is" + right[0] + "brother" + right[1]

    wooglin.sendmessage(message)

    # Ensuring the table is fixed.
    while len(SoberBros) != 4:
        SoberBros.append("NO ONE")

    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table("soberbros")

    table.put_item(
        Item={
            'date': date,
            'soberbro1': SoberBros[0],
            'soberbro2': SoberBros[1],
            'soberbro3': SoberBros[2],
            'soberbro4': SoberBros[3],
            'soberbro5': SoberBros[4]
        }
    )


# Creates an entry in the members table.
def createOperation(tablename, key):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(tablename)

    peopleIveCreated = ""

    for x in range(len(key)):

        table.put_item(
            Item={
                'name': key[x]['value'],
                'phonenumber': 0,
                'rollnumber': 0,
                'address': "No Address",
                'email': "no email",
                'present': 0,
                'unexcused': 0,
                'excused': 0,
                'excuses': [],
                'absences': 0
            }
        )
        peopleIveCreated += str(key[x]['value']) + ", "

    toReturn = "Well, I've added " + str(peopleIveCreated[:len(peopleIveCreated) -1]) + " to " + tablename
    toReturn += ". However, their data is all null! You should probably fix that..."
    wooglin.sendmessage(toReturn)


# Lists the sober bros for a given date.
def list_sober_bros(tablename, date):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(tablename)

    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )

    response = response['Items']

    # Sober bro shift doesn't exist yet, let's create it.
    if len(response) == 0:
        return []

    SoberBros = []
    SoberBros.append(response[0]['soberbro1'])
    SoberBros.append(response[0]['soberbro2'])
    SoberBros.append(response[0]['soberbro3'])
    SoberBros.append(response[0]['soberbro4'])
    SoberBros.append(response[0]['soberbro5'])

    return SoberBros


# Puts the data into a more readable form.
# TODO make this method less.... gross.
def stringify_member(data, table, key, attribute):
    print("Welcome to stringify_member")
    print("S_M received: ")
    print("Data: " + str(data))
    print("Table: " + str(table))
    print("Key: " + str(key))
    print("Attribute: " + str(attribute))
    if len(data) != 0:
        if attribute == "":
            toReturn = "Here is the data for " + str(data[0]['name']) + ":" + "\n"
            toReturn += "Phone number: " + str(data[0]['phonenumber']) + "\n"
            toReturn += "Email: " + str(data[0]['email']) + "\n"
            toReturn += "Address: " + str(data[0]['address']) + "\n"
            toReturn += "Roll number: " + str(data[0]['rollnumber']) + "\n"
            toReturn += "Excused Absences: " + str(data[0]['excused']) + "\n"
            toReturn += "Excuses: " + str(data[0]['excuses']) + "\n"
            toReturn += "Unexcused Absences: " + str(data[0]['unexcused']) + "\n"
            toReturn += "Absences in total: " + str(data[0]['absences']) + "\n"
            toReturn += "Times Present at Chapter: " + str(data[0]['present']) + "\n"
        elif attribute == "excuses":
            toReturn = key[0]['value'] +"'s " + "excuses for missing chapter have been: "
            for i in range(len(data[0]['excuses'])):
                toReturn += str(data[0]['excuses'][i]) + ", "
        else:
            if attribute == "absences" or attribute == "unexcused" or attribute == "excused":
                if attribute == "absences":
                    return key[0]['value'] + " has been absent from chapter " + str(data[0][attribute]) + " times."
                else:
                    return key[0]['value'] + " has been " + attribute + " at chapter " + str(data[0][attribute]) + " times."
            return key[0]['value'] + "'s " + attribute + " is: " + str(data[0][attribute])
    else:
        toReturn = "I'm sorry, I could not find " + str(key[0]['value']) + "\n"
        toReturn += " in " + str(table) + ". Please make sure it is spelled correctly."
    return toReturn


# Stringifies the modify operation.
def stringify_update(data, key, attribute, new_value):
    data = data['ResponseMetadata']
    responseCode = data['HTTPStatusCode']

    if responseCode == 200:
        return "Success! " + key + "'s " + attribute + " is now: " + new_value
    else:
        return "I'm sorry. Something went wrong."


# Stringifies the sober bros for a given night.
def stringify_soberbros(response):
    SoberBros = []
    SoberBros.append(response[0]['soberbro1'].strip())
    SoberBros.append(response[0]['soberbro2'].strip())
    SoberBros.append(response[0]['soberbro3'].strip())
    SoberBros.append(response[0]['soberbro4'].strip())
    SoberBros.append(response[0]['soberbro5'].strip())

    SoberBros = [x for x in SoberBros if x != "NO ONE"]

    num = len(SoberBros)
    resultString = ""

    # TODO: Fix this because it's garbage can code.
    if num == 0:
        return "Yikes. It looks like there are NO sober bros for " + unprocessDate(response[0]['date'])
    elif num == 1:
        dateStatement = "The Sober Bro for " + unprocessDate(response[0]['date']) + " is just "
        resultString = SoberBros[0]
        return dateStatement + resultString + "."
    elif num == 2:
        resultString = SoberBros[0] + " and " + SoberBros[1]
    elif num == 3:
        resultString = SoberBros[0] + ", " + SoberBros[1] + ", and " + SoberBros[2]
    elif num == 4:
        resultString = SoberBros[0] + ", " + SoberBros[1] + ", " + SoberBros[2] + ", and " + SoberBros[3]
    elif num == 5:
        resultString = SoberBros[0] + ", " + SoberBros[1] + ", " + SoberBros[2] + ", " + SoberBros[3] + ", and " + SoberBros[4]
    dateStatement = "The Sober Bros for " + unprocessDate(response[0]['date']) + " are "

    toReturn = dateStatement + resultString + "."

    return toReturn


# Takes the date in YYYY-MM-DD format and translates it into Human-readable format.
def unprocessDate(date):
    print("Unprocess date got:" + str(date))
    date = date.split('-')
    day = (date[2])[0:2]
    dt = datetime.datetime(int(date[0]), int(date[1]), int(day))
    date_string = '{:%A, %B %d, %Y}'.format(dt)
    print("Unprocess date returned:" + date_string)
    return str(date_string)