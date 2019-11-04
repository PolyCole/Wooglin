import boto3, sys, datetime
from boto3.dynamodb.conditions import Key, Attr
from source import wooglin

def dbhandler(resp):
    operation = resp['entities']['db_operation'][0]['value']

    try:
        key = resp['entities']['key']
    except KeyError as e:
        key = ""

    try:
        attribute = resp['entities']['attribute'][0]['value']
    except KeyError as e:
        attribute = ""

    try:
        table = resp['entities']['table'][0]['value']
    except KeyError as e:
        table = "members"


    print("key: " + str(key))
    print("table: " + str(table))
    print("attribute: " + str(attribute))

    if operation == "get":
        if table == "soberbros":
            date = extract_date(resp)
            print("Passing with get sober bros request: " + str(date))
            getOperationSoberBros(table, date)
        else:
            getOperation(table,key, attribute)
    elif operation == "modify":
        modifyOperation(resp,table,key)
    elif operation == "delete":
        deleteOperation(table, key)
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

    if isinstance(key, list):
        print("In list option")
        for x in range(len(key)):
            # Getting the item!
            response = table.query(
                KeyConditionExpression=Key('name').eq(key[x]['value'])
            )

            #print("Response from GET request:")
            #print(response)
            print("Get operation returned: " + str(response))
            wooglin.sendmessage(stringify_member(response['Items'], tablename, key, attribute))
    elif isinstance(key, dict):
        print("In dict option")
        # Getting the item!

        print("Starting get request with key : " +key[0]['value'])

        response = table.query(
            KeyConditionExpression=Key('name').eq(key[0]['value'])
        )

        print("Got a response from query request")
        # print("Response from GET request:")
        # print(response)
        print("Get operation returned: " + str(response))
        wooglin.sendmessage(stringify_member(response['Items'], tablename, key, attribute))
    elif isinstance(key, str):
        print("In String option!")
        print(str(key))
    else:
        print("I'm not entirely sure how key was put into " + str(type(key)) + " but it was an I'm confused.")

def getOperationSoberBros(table, date):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table)

    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )

    wooglin.sendmessage(stringify_soberbros(response['Items']))


def scanTable(tablename):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(tablename)
    return table.scan()['Items']


def modifyOperation(resp, table, key):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    tablename = table
    table = dynamodb.Table(table)

    target = table.query(
        KeyConditionExpression=Key('name').eq(key[0]['value'])
    )

    # Our target doesn't exist in the table.
    if(len(target) == 0):
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


def sober_bro_assign(tablename, key, date):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(tablename)

    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )

    response = response['Items']
    print("sober_bro_assign is working with: " + str(response))

    SoberBros = []
    SoberBros.append(response[0]['soberbro1'])
    SoberBros.append(response[0]['soberbro2'])
    SoberBros.append(response[0]['soberbro3'])
    SoberBros.append(response[0]['soberbro4'])

    for x in range(4):
        if SoberBros[x] == key[0]['value']:
            wooglin.sendmessage("Whoops! It looks like " + key[0]['value'] + " is already a sober bro on " + str(unprocessDate(date)))
            return
        if SoberBros[x] == "NO ONE":
            SoberBros[x] = key[0]['value']
            numBros = x + 1
            break
        else:
            numBros = -1


    if numBros == -1:
        wooglin.sendmessage("It looks like the sober bro shift on " + str(unprocessDate(date)) + " is already full. I couldn't add " + str(key[0]['value']))
        return

    table.put_item(
        Item={
            'date': date,
            'soberbro1': SoberBros[0],
            'soberbro2': SoberBros[1],
            'soberbro3': SoberBros[2],
            'soberbro4': SoberBros[3]
        }
    )
    message = "Alrighty! I've added " + str(key[0]['value']) + " to the sober bro shift on " + str(unprocessDate(date)) + ".\nThere are now " + str(numBros) + " sober brothers on that date."

    # Gotta have the proper grammar...
    if numBros == 1:
        left = message.split("are")
        right = left[1].split("brothers")
        message = left[0] + "is" + right[0] + "brother" + right[1]

    wooglin.sendmessage(message)

def deleteOperation(table, key):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table)

    peopleIveDeleted = ""

    for x in range(len(key)):
        print("Delete is attempting to DELETE: " + str(key[x]['value']))

        response = table.delete_item(
            Key={
                'name':key[x]['value']
            }
        )

        peopleIveDeleted += str(key[x]['value']) + ", "
    wooglin.sendmessage("Well I've done it. If " + str(peopleIveDeleted[:len(peopleIveDeleted)-2]) + " existed before, they don't now")


def sober_bro_deassign(table, key, date):
    df

def createOperation(tablename, key):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(tablename)

    peopleIveCreated = ""

    for x in range(len(key)):

        table.put_item(
            Item={
                'name': key[x]['value'],
                'phonenumber': 0,
                'rollnumber': 0
            }
        )
        peopleIveCreated += str(key[x]['value']) + ", "

    toReturn = "Well, I've added " + str(peopleIveCreated[:len(peopleIveCreated) -1]) + " to " + tablename
    toReturn += ". However, their data is all null! You should probably fix that..."
    wooglin.sendmessage(toReturn)

# Puts the data into a more readable form.
def stringify_member(data, table, key, attribute):
    print("Welcome to stringify_member")
    print("S_M received: ")
    print("Data: " + str(data))
    print("Table: " + str(table))
    print("Key: " + str(key))
    print("Attribute: " + str(attribute))
    if(len(data) != 0):
        if attribute == "":
            toReturn = "Here is the data for " + str(data[0]['name']) + ":" + "\n"
            toReturn += "Phone number: " + str(data[0]['phonenumber']) + "\n"
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

def stringify_update(data, key, attribute, new_value):
    data = data['ResponseMetadata']
    responseCode = data['HTTPStatusCode']

    if responseCode == 200:
        return "Success! " + key + "'s " + attribute + " is now: " + new_value
    else:
        return "I'm sorry. Something went wrong."


def stringify_soberbros(response):
    if(len(response) == 0):
        return "Looks like there aren't any sober bros for that date yet."

    SoberBros = []
    SoberBros.append(response[0]['soberbro1'].strip())
    SoberBros.append(response[0]['soberbro2'].strip())
    SoberBros.append(response[0]['soberbro3'].strip())
    SoberBros.append(response[0]['soberbro4'].strip())

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

    dateStatement = "The Sober Bros for " + unprocessDate(response[0]['date']) + " are "

    toReturn = dateStatement + resultString + "."

    return toReturn


def unprocessDate(date):
    print("Unprocess date got:" + str(date))
    date = date.split('-')
    dt = datetime.datetime(int(date[0]), int(date[1]), int(date[2]))
    date_string = '{:%A, %B %d, %Y}'.format(dt)
    print("Unprocess date returned:" + date_string)
    return str(date_string)