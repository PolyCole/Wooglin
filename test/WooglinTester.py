import src.wooglin

while(True):
    text = input("Please enter input for the bot: \n" )
    packaged = {"event":{"text":text, "channel":"DJWT3Q075", "user":'UJWT93AH0'}}
    print(src.wooglin.lambda_handler(packaged, 123))



'''
When a message is posted.
{
    'token': '5hhu6lPPmr01l57ElWWFjzFy', 
    'team_id': 'TK8AAJF96', 
    'api_app_id': 'AK1V9SVH7', 
    'event': {
        'client_msg_id': '5712d875-10d8-425f-afbc-ac1f59e05a81', 
        'type': 'message', 
        'text': 'waddup', 
        'user': 'UJWT93AH0', 
        'ts': '1571065444.001400', 
        'team': 'TK8AAJF96', 
        'channel': 'DJWT3Q075', 
        'event_ts': '1571065444.001400', 
        'channel_type': 'im'
    }, 
    'type': 'event_callback', 
    'event_id': 'EvPEDQHNGP', 
    'event_time': 1571065444, 
    'authed_users': ['UK8ABQCAC']
}
'''