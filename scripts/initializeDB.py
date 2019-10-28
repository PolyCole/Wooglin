import boto3
import sys
import datetime

seedFile = input("Please input the name of the seed file:")
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
tablename = input("Which table will we be writing to:")
table = dynamodb.Table(tablename)

def initializeSoberBros(table, seedFile):
	with table.batch_writer() as batch:
		try:
			seedFile = open(seedFile, "r")
			
			#Getting rid of placeholder line
			seedFile.readline()
			
			currentLine = seedFile.readline()
			count = 0

			while currentLine != '':
				processed = currentLine.split(",")
				date = properDateFormat(processed[0])
			
				soberbro1 = processed[1] if len(processed[1]) > 5 else "NULL"
				soberbro2 = processed[2] if len(processed[2]) > 5 else "NULL"
				soberbro3 = processed[3] if len(processed[3]) > 5 else "NULL"
				soberbro4 = processed[4] if len(processed[4]) > 5 else "NULL"

				batch.put_item(
					Item={
						'date': date,
						'soberbro1': soberbro1,
						'soberbro2': soberbro2,
						'soberbro3': soberbro3,
						'soberbro4': soberbro4
					}
				)
				
				print("Writing " + date + " to db...")
				currentLine = seedFile.readline()
				count = count + 1

			print("Successfully wrote " + str(count) + " entries to soberbros")
		except Exception as e:
			print("Oops. Exception of type " + str(sys.exc_info()[0]) + " occurred")
	
	
	
def properDateFormat(input):
	now = datetime.datetime.now()
	inputSplit = input.split('/')
	
	if int(inputSplit[0]) < 10:
		inputSplit[0] = "0" + inputSplit[0]
	
	if int(inputSplit[1]) < 10:
		inputSplit[1] = "0" + inputSplit[1]
	
	toReturn = str(now.year) + "-" + str(inputSplit[0]) + "-" + str(inputSplit[1])
	return toReturn
		



def initializeMembers(table, seedFile):
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
				
				print("Writing " + name + " to db...")
				currentLine = seedFile.readline()
				count = count + 1

			print("Successfully wrote " + str(count) + " entries to members")
		except Exception as e:
			print("Oops. Exception of type " + sys.exc_info()[0] + " occurred")



if tablename == "members":
	initializeMembers(table, seedFile)
elif tablename == "soberbros":
	initializeSoberBros(table, seedFile)
else:
	print("I'm sorry. That table doesn't exist.")
	print("Exiting...")
	sys.exit()
	
