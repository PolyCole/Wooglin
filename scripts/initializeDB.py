import boto3
import sys
import datetime
import os

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
			print("Oops. Exception of type " + sys.exc_info()[0] + " occurred")
	
	
	
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
			
			os.remove("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTaking\\ListFile.txt")
			chapterList = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTaking\\ListFile.txt", "w")
			
			#Getting rid of placeholder line
			seedFile.readline()
			
			currentLine = seedFile.readline()
			count = 0

			while currentLine != '':
				processed = currentLine.split(",")
				name = processed[0]
				rollnumber = processed[1]
				phonenumber = processed[2]
				
				chapterList.write(name + "\n")

				batch.put_item(
					Item={
						'name': name,
						'phonenumber': phonenumber,
						'rollnumber': rollnumber,
						'present':0,
						'unexcused':0,
						'excused':0,
						'excuses':[],
						'absences': 0
					}
				)
				
				print("Writing " + name + " to db...")
				currentLine = seedFile.readline()
				count = count + 1

			print("Successfully wrote " + str(count) + " entries to members")
			chapterList.close()
		except Exception as e:
			print("Oops. Exception of type " + str(sys.exc_info()[0]) + " occurred")
			print(str(e.__traceback__()))



if tablename == "members":
	initializeMembers(table, seedFile)
elif tablename == "soberbros":
	initializeSoberBros(table, seedFile)
else:
	print("I'm sorry. That table doesn't exist.")
	print("Exiting...")
	sys.exit()
	
