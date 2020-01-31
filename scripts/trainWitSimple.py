import sys
from wit import Wit

witClient = Wit(input("Please enter API key"))

cur = "yeet"
count = 0
while(cur != "exit"):
    cur = input("Please input message:")
    if cur != "exit":
        print(witClient.message(cur))
        count += 1

print("Thanks for providing " + str(count) + " training sentences for the bot!")
print("Goodbye...")

sys.exit()
    
