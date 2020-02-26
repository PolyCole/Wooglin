# Author: Cole Polyak
# File: drop_events.py
# Purpose: Drops and recreates the events table in dynamodb.
# Date: 25 February 2020

import boto3


def main():
    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table("test_table")
        response = table.delete()
        create_table()
    except Exception as e:
        create_table()


def create_table():
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    response = dynamodb.create_table(
        AttributeDefinitions=[
            {
                'AttributeName': 'event_id',
                'AttributeType': 'S',
            },
        ],
        KeySchema=[
            {
                'AttributeName': 'event_id',
                'KeyType': 'HASH',
            },
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5,
        },
        TableName="test_table",
    )
    print("Created table.")


main()
