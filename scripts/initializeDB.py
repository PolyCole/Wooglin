import boto3
import sys

seedFile = input("Please input the name of the seed file:")
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
tablename = input("Which table will we be writing to: ")
table = dynamodb.Table(tablename)
table2 = dynamodb.Table("link")

with table.batch_writer() as batch:
    with table2.batch_writer() as batch2:
		try:
			seedFile = open(seedFile, "r")
			
			#Getting rid of placeholder line
			seedFile.readline()
			
			currentLine = seedFile.readline()
			count = 0

			while currentLine != '':
				processed = currentLine.split(",")
				name = processed[0]
				phonenumber = processed[1]

				# Removing the newline character.
				rollnumber = processed[2]
				rollnumber = rollnumber[0:rollnumber.index('\n')]

				batch.put_item(
					Item={
						'name': name,
						'phonenumber': phonenumber,
						'rollnumber': rollnumber
					}
				)
				
				batch2.put_item(
					Item={
						'id':count,
						'name':name
					}
				)
				
				print("Writing " + name + " to db...")
				currentLine = seedFile.readline()
				count = count + 1

			print("Successfully wrote " + str(count) + " entries to the db")
		except Exception as e:
			print("Oops. Exception of type " + sys.exc_info()[0] + " occurred")
