import boto3
import sys
from boto3.dynamodb.conditions import Key, Attr
from src import wooglin

def dbhandler(resp):
    operation = resp['entities']['db_operation'][0]['value']
    key = resp['entities']['key']

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
        getOperation(table,key, attribute)
    elif operation == "modify":
        modifyOperation(resp,table,key)
    elif operation == "delete":
        deleteOperation(table, key)
    elif operation == "create":
        createOperation(table, key)
    else:
        wooglin.sendmessage("I'm sorry, that database functionality is either not understood or not supported")


# Handles get operations to the DB.
def getOperation(table, key, attribute):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    tablename = table
    table = dynamodb.Table(table)

    for x in range(len(key)):
        # Getting the item!
        response = table.query(
            KeyConditionExpression=Key('name').eq(key[x]['value'])
        )

        #print("Response from GET request:")
        #print(response)
        wooglin.sendmessage(stringify_member(response['Items'], tablename, key, attribute))


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
    if(len(data) != 0):
        if(attribute == ""):
            toReturn = "Here is the data for " + data[0]['name'] + ":" + "\n"
            toReturn += "Phone number: " + str(data[0]['phonenumber']) + "\n"
            toReturn += "Roll number: " + str(data[0]['rollnumber'])
        else:
            return key + "'s " + attribute + " is: " + str(data[0][attribute])
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