import sys

if(len(sys.argv) == 0):
    print("Whoops! Looks like you forgot to pass in the proper arguments. (name) (excuse)")
    sys.exit(1)

if(len(sys.argv) < 3):
    print("Yikes. Looks like you forgot a parameter or two. Please fix.")
    sys.exit(1)

file = open("C:\\Users\\Five\\PycharmProjects\\Wooglin\\scripts\\attendanceTracking\\excuses.txt", "a")

name = str(sys.argv[1] + " " + sys.argv[2])

excuse = ""

for x in range(3, len(sys.argv)):
    excuse += str(sys.argv[x]) + " "

entry = name + ", " + excuse + "\n"
file.write(entry)

print("I've successfully written:\n" + str(entry))
file.close()
