inFile = open("testing.csv", "r")
string = inFile.readline()
split = string.split(",")

print(split[0])
print(split[1])




'''
{
    'token': '5hhu6lPPmr01l57ElWWFjzFy', 
    'team_id': 'TK8AAJF96', 
    'api_app_id': 'AK1V9SVH7', 
    'event': {
        'client_msg_id': '59a46652-caca-4af8-afdd-c85ee54c6673', 
        'type': 'message', 
        'text': 'packet', 
        'user': 'UJWT93AH0', 
        'ts': '1567731218.012400', 
        'team': 'TK8AAJF96', 
        'channel': 'DJWT3Q075', 
        'event_ts': '1567731218.012400', 
        'channel_type': 'im'}, 
    'type': 'event_callback', 
    'event_id': 'EvN4ULA1ML', 
    'event_time': 1567731218, 
    'authed_users': ['UK8ABQCAC']}
    
    
    'bot_id': 'BK1VAL1UH'
'''