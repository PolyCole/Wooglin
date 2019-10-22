import boto3
import sys
from boto3.dynamodb.conditions import Key, Attr

def dbhandler(resp):
    operation = resp['entities']['db_operation'][0]['value']
    key = resp['entities']['key'][0]['value']

    try:
        attribute = resp['entities']['attribute'][0]['value']
    except KeyError as e:
        attribute = ""

    try:
        table = resp['entities']['table'][0]['value']
    except KeyError as e:
        table = "members"

    print("key: " + key)
    print("table: " + table)
    print("attribute: " + attribute)

    if operation == "get":
        data = getOperation(table,key)
        return stringify_member(data, table, key, attribute)
    elif operation == "modify":
        return modifyOperation(resp,table,key)
    elif operation == "delete":
        return deleteOperation(table, key)
    elif operation == "create":
        return createOperation(table, key)
    else:
        return "I'm sorry, that database functionality is either not understood or not supported"


# Handles get operations to the DB.
def getOperation(table, key):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    table = dynamodb.Table(table)

    # Getting the item!
    response = table.query(
        KeyConditionExpression=Key('name').eq(key)
    )

    #print("Response from GET request:")
    #print(response)
    return response['Items']


def scanTable(tablename):
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    table = dynamodb.Table(tablename)
    return table.scan()['Items']


def modifyOperation(resp, table, key):
    target = getOperation(table, key)

    if(len(target) == 0):
        return stringify_member(target, table, key)

    attribute = resp['entities']['attribute'][0]['value']
    new_value = resp['entities']['new_value'][0]['value']

    print("attribute: " + attribute)
    print("new_value: " + new_value)

    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table)

    response = table.update_item(
        Key={
            'name': key
        },
        UpdateExpression='SET ' + str(attribute) + ' = :val1',
        ExpressionAttributeValues={
            ':val1': new_value
        }
    )

    return stringify_update(response, key, attribute, new_value)

def deleteOperation(table, key):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table)


    print("Delete is attempting to DELETE: " + key)

    response = table.delete_item(
        Key={
            'name':key
        }
    )

    return("Well, I've done it. If " + str(key) + " existed before they certainly don't now")


def createOperation(tablename, key):
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table(tablename)

    table.put_item(
        Item={
            'name': key,
            'phonenumber': 0,
            'rollnumber': 0
        }
    )
    toReturn = "Well, I've added " + str(key) + " to " + tablename
    toReturn += ". However, their data is all null! You should probably fix that..."

    return toReturn


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
        toReturn = "I'm sorry, I could not find " + str(key) + "\n"
        toReturn += " in " + str(table) + ". Please make sure it is spelled correctly."
    return toReturn

def stringify_update(data, key, attribute, new_value):
    data = data['ResponseMetadata']
    responseCode = data['HTTPStatusCode']

    if responseCode == 200:
        return "Success! " + key + "'s " + attribute + " is now: " + new_value
    else:
        return "I'm sorry. Something went wrong."