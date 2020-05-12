import sys
from cryptography.fernet import Fernet


def main():
    filepath = input("Path to keyfile:")
    key = open(filepath, "r").readline().strip().encode()

    filepath = input("Path to inputfile:")
    file = open(filepath, "r")

    out = open("/home/cole/Desktop/out.csv", "w")

    current_line = file.readline()
    while current_line != "":
        processed = current_line.split(",")
        processed[2] = encrypt(processed[2].replace("\"", ""), key)
        processed[3] = encrypt(processed[3].replace("\"", ""), key)

        string = ""
        for x in range(0, len(processed)):
            string += str(processed[x].replace("\"", ""))
            if x != len(processed) - 1:
                string += ","

        out.write(string)
        current_line = file.readline()

    out.close()
    file.close()
    print("Success.")


def encrypt(message, key):
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return encrypted.decode()


def decrypt(encrypted, key):
    f = Fernet(key)
    decrypted = f.decrypt(encrypted.encode())
    return decrypted.decode()


main()
