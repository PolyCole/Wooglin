import boto3
import sys
import datetime
import os
from cryptography.fernet import Fernet

seedFile = input("Please input the name of the seed file:")
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
tablename = input("Which table will we be writing to:")
table = dynamodb.Table(tablename)
filepath = input("Where is the keyfile stored:")

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
				# date = properDateFormat(processed[0])
				date = processed[0]

				soberbro1 = processed[1] if len(processed[1]) > 5 else "NO ONE"
				soberbro2 = processed[2] if len(processed[2]) > 5 else "NO ONE"
				soberbro3 = processed[3] if len(processed[3]) > 5 else "NO ONE"
				soberbro4 = processed[4] if len(processed[4]) > 5 else "NO ONE"
				soberbro5 = processed[5] if len(processed[5]) > 5 else "NO ONE"

				batch.put_item(
					Item={
						'date': date.replace("\"",""),
						'soberbro1': soberbro1.replace("\"",""),
						'soberbro2': soberbro2.replace("\"",""),
						'soberbro3': soberbro3.replace("\"",""),
						'soberbro4': soberbro4.replace("\"",""),
						'soberbro5': soberbro5.replace("\"","")
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

			# Deleting and re-creating list file
			#os.remove("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTracking\\ListFile.txt")
			#chapterList = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTracking\\ListFile.txt", "w")
			
			#Getting rid of placeholder line
			seedFile.readline()
			
			currentLine = seedFile.readline()
			count = 0

			while currentLine != '':
				processed = currentLine.split(",")

				# Because name has a middle initial, we'll have
				# to do a little bit more formatting work up front.
				name = processed[0].split(" ")

				if(len(name) > 2):
					name.pop(1)

				new_name = ""
				for x in range(len(name)):
					new_name += str(name[x]) + " "
				name = new_name.strip()
				
				rollnumber = processed[1]
				phonenumber = processed[2]
				print("Before: " + str(processed[3]))
				email = encrypt(processed[3], filepath)


				address = ""

				for x in range (4, len(processed)):
					address += str(processed[x])

				print("Before: " + str(address))
				address = encrypt(address.strip(), filepath)


				print("Address and email (Should be encrypted): ")
				print("\n" + str(address))
				print("\n" + str(email))
				sys.exit(1)

				chapterList.write(name + "\n")

				batch.put_item(
					Item={
						'name': name,
						'phonenumber': phonenumber,
						'rollnumber': rollnumber,
						'address' : address,
						'email' : email,
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

def initializeMembers2(table, seedFile):
	filepath = input("Path to encryption key:")
	# key = open(filepath, "r").readline().strip().encode()

	with table.batch_writer() as batch:
		try:
			seedFile = open(seedFile, "r")
			chapterList = open("/home/cole/Desktop/ListFile.txt", "w")

			currentLine = seedFile.readline()
			count = 0

			while currentLine != '':
				processed = currentLine.split(",")

				name = processed[0]
				rollnumber = processed[8]
				phonenumber = processed[6]
				email = processed[3]
				address = processed[2]

				"name (S)", "absences (S)", "address (S)", "email (S)", \
				"excused (N)", "excuses (L)", "phonenumber (S)", \
				"present (S)", "rollnumber (S)", "unexcused (S)"

				chapterList.write(name + "\n")

				batch.put_item(
					Item={
						'name': name,
						'phonenumber': phonenumber,
						'rollnumber': rollnumber,
						'address': address,
						'email': email,
						'present': processed[7],
						'unexcused': processed[9].strip(),
						'excused': processed[4],
						'excuses': processed[5],
						'absences': processed[1]
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



def encrypt(message, key):
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return encrypted.decode()


def decrypt(encrypted, key):
    f = Fernet(key)
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()


if tablename == "members":
	initializeMembers(table, seedFile)
elif tablename == "soberbros":
	initializeSoberBros(table, seedFile)
elif tablename == "membersspecial":
	table = dynamodb.Table("members")
	initializeMembers2(table, seedFile)
else:
	print("I'm sorry. That table doesn't exist.")
	print("Exiting...")
	sys.exit()
	
