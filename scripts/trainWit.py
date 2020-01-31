import sys
from wit import Wit
import time
import random

witClient = Wit(input("Please enter API key:"))


def initialize(filename):
    to_return = {}

    if filename == "ListFile":
        input_file = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTracking\\ListFile.txt", "r")
    elif filename == "witData":
        input_file = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\witData.txt", "r")
    else:
        print("ERROR, NOT VALID FILENAME")
        return None

    current = input_file.readline()
    count = 0

    while current != '':
        to_return[count] = current.strip()
        count += 1
        current = input_file.readline()

    return to_return


try:
    trainingAmount = int(input("Desired number of training messages:"))

    people = initialize("ListFile")
    templates = initialize("witData")

    for x in range(trainingAmount):
        people_index = random.randint(0, len(people)-1)
        template_index = random.randint(0, len(templates)-1)

        template = templates[template_index].split('[name]')

        if len(template) > 1:
            message = template[0] + people[people_index] + template[1]
        else:
            message = template[0]

        print("Sending: " + message + " to NLP engine")
        witClient.message(message)
        time.sleep(3)

    print("\n----------------------------------------------------------")
    print("I've sent " + str(trainingAmount) + " messages to the NLP engine.")
    print("----------------------------------------------------------\n")

except Exception as e:
    print(e)
    print("I'm sorry, the required files cannot be found. Exiting...")
    sys.exit()
