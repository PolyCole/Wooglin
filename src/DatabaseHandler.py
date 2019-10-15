import boto3
import sys
from boto3.dynamodb.conditions import Key, Attr


# Handles get operations to the DB.
def getOperation(resp):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    operation = resp['entities']['operation'][0]['value']
    table = resp['entities']['table'][0]['value']
    key = resp['entities']['key'][0]['value']

    table = dynamodb.Table('BTPAlphaZeta')

    response = table.query(
        KeyConditionExpression=Key('id').eq(0)
    )

    return stringify_member(response['Items'])

# Puts the data into a more readable form.
def stringify_member(data):
    toReturn = "Here is the data for " + data[0]['name'] + "\n"
    toReturn += "Phone number: " + data[0]['number'] + "\n"
    toReturn += "Roll number: " + str(data[0]['id'])

    return toReturn
