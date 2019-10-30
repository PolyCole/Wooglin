import datetime
from msvcrt import getch
import math
import time
import boto3
import sys

def attendanceDriver():
	attendanceData = takeAttendance()
	time.sleep(10)
	writeToDB = input("Is there any reason I shouldn't write this data to file?")

	if writeToDB == "no" or writeToDB == "No":
		writeAttendanceDataToFile(attendanceData)
		print("Written. Goodbye.")
		sys.exit()
	else:
		print("Alright. Please make your changes and I'll wait till you return...")

	input("Are we good to go?")
	writeAttendanceDataToFile(attendanceData)
	print("Written. Goodbye")
	sys.exit()


def writeAttendanceDataToFile(attendanceData):
	dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
	table = dynamodb.Table('members')
	scanner = table.scan()['Items']

	with table.batch_writer() as batch:
		for i in range(len(scanner)):
			current = scanner[i]

			status = attendanceData[current['name']]

			if status == "Present":
				current['present'] = str(int(current['present']) + 1)
			elif status == "Absent":
				current['unexcused'] = str(int(current['unexcused']) + 1)
			else:
				current['excuses'].append(status)
				current['excused'] = str(int(current['excused']) + 1)

			batch.put_item(
				Item={
					'name': current['name'],
					'phonenumber': current['phonenumber'],
					'rollnumber': current['rollnumber'],
					'present':current['present'],
					'unexcused':current['unexcused'],
					'excused':current['excused'],
					'excuses':current['excuses'],
					'absences':str(int(current['unexcused']) + int(current['excused']))
				}
			)

	print("I've sucessfully updated attendance data for today.")






def takeAttendance():
	filePath = "C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTaking\\Attendances\\"

	date = datetime.datetime.now()
	today = date.today()
	today = today.strftime("%m-%d-%Y")
	
	outputFile = open(filePath + today + ".txt", "w")
	
	excuses = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTaking\\excuses.txt", "r")
	
	excuseList = {}
	
	curLine = excuses.readline()
	
	while curLine != '':
		split = curLine.split(",")
		excuseList[split[0]]= split[1].strip()
		curLine = excuses.readline()

	members = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTaking\\ListFile.txt","r")
	curLine = members.readline().strip()
	totalMembers = 0
	presentCount = 0

	attendanceData = {}
	
	while curLine != '':
		try:
			excuse = excuseList[curLine]
			outputFile.write(curLine + "\t\t\t\t" + excuse + "\n")
			totalMembers = totalMembers + 1
			attendanceData[curLine] = excuse
		except KeyError:
			print(curLine + "\n\n")
			attendanceStanding = ord(getch())
			print("-------------------")

			attendanceStanding = checkValidStanding(attendanceStanding)

			while attendanceStanding == "invalid":
				print("Please enter only (p)resent or (a)bsent: ")
				attendanceStanding = checkValidStanding(ord(getch()))

			if attendanceStanding  == 'Present':
				presentCount = presentCount + 1

			totalMembers = totalMembers + 1
			outputFile.write(curLine + "\t\t\t\t" + attendanceStanding + "\n")

			attendanceData[curLine] = attendanceStanding

		curLine = members.readline().strip()

	proportion = presentCount / totalMembers

	print("\n\n\n------------------------------")
	print("CHAPTER PROPORTION: " + str(round(proportion, 4)))
	if proportion > 0.75:
		print("We have a Quorum.")
	else:
		print("We do NOT have A Quorum.")
		print("Short by: " + str(round(0.75 - proportion, 3)* 100) + "%")
	print("------------------------------")

	outputFile.close()
	return attendanceData


def checkValidStanding(attendanceStanding):
	if attendanceStanding == 112:
		return "Present"
	elif attendanceStanding == 97:
		return "Absent"
	else:
		return "invalid"

attendanceDriver()
