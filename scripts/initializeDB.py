import boto3
import sys

seedFile = input("Please input the name of the seed file:")
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table('BTPAlphaZeta')

with table.batch_writer() as batch:
    try:
        seedFile = open(seedFile, "r")
        
        #Getting rid of placeholder line
        seedFile.readline()
        
        currentLine = seedFile.readline()
        count = 0

        while currentLine != '':
            processed = currentLine.split(",")
            name = processed[0]
            
            number = processed[1]
            number = number[0:number.index('\n')]

            batch.put_item(
                Item={
                    'id': count,
                    'name': name,
                    'number': number
                }
            )
            print("Writing " + name + " to db...")
            currentLine = seedFile.readline()
            count = count + 1

        print("Successfully wrote " + str(count) + " entries to the db")
    except Exception as e:
        print("Oops. Exception of type " + sys.exc_info()[0] + " occurred")
