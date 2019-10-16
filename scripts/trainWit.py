import sys
from wit import Wit

witClient = Wit(input("Please enter API key"))

try:
    filename = input("Please input the name of the file:")
    inputFile = open(filename, "r")
    
    currentLine = inputFile.readline()
    count = 0
    while(currentLine != ""):
        cur = currentLine.split(",")[1]
        chop =  cur.index('\n')
        cur = cur[0:chop]
        print("Sending: " + cur + " to Wit...")
        witClient.message(cur)
        currentLine = inputFile.readline()
        count = count + 1

    print("Successfully sent " + str(count) + " training messages to Wit.")
    inputFile.close()
    
except Exception as e:
    print(e)
    print("I'm sorry, the file cannot be found. Exiting...")
    sys.exit()
