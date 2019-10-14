from wit import Wit
from src import GreetUser

def test():

    client = Wit('4NLCSWT6WGCYWOQ4VCZDKJ6F2CMJIQ6Q')

    while(True):
        resp = client.message(input("Message:"))
        print('Response: {}'.format(resp))
        action = resp['entities']['intent'][0]['value']

        if(action == 'greeting'):
            GreetUser.greetUser();


