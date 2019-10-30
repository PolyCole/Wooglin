import sys, os
from wit import Wit
import time

witClient = Wit(input("Please enter API key"))

try:
    filename = input("Please input the name of the file:")
    inputFile = open(filename, "r")
    
    currentLine = inputFile.readline()
    count = 0
    while(currentLine != ""):
        cur = currentLine.strip()
        print("Sending: " + cur + " to Wit...")
        witClient.message(cur)
        currentLine = inputFile.readline()
        count = count + 1
        time.sleep(3)

    print("Successfully sent " + str(count) + " training messages to Wit.")
    print("Deleting file...")
    os.remove(filename)
    file = open(filename, 'r')
    inputFile.close()
    
except Exception as e:
    print(e)
    print("I'm sorry, the file cannot be found. Exiting...")
    sys.exit()
