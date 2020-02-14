import wooglin

while(True):
    message = input("Please input your message for the bot: ")
    data  ={
    'version': 2,
    'path': '/prod/wooglin-body',
    'httpMethod': 'POST',
    'headers': {
        'Content-Length': '409',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'mreaqd8hh6.execute-api.us-east-1.amazonaws.com',
        'I-Twilio-Idempotency-Token': '5bfe3d88-ce7c-4d0a-8f68-88da5b48dc37',
        'User-Agent': 'TwilioProxy/1.1',
        'X-Amzn-Trace-Id': 'Root=1-5e42f836-6da879586641cde482a02330',
        'X-Forwarded-For': '3.92.234.61',
        'X-Forwarded-Port': '443',
        'X-Forwarded-Proto': 'https',
        'X-Twilio-Signature': '63dYsiunev1uIRnlHn8M3R3oQFw=',
        'accept': '*/*',
        'cache-control':
        'max-age=259200'
    },
    'multiValueHeaders': {
        'Content-Length': ['409'],
        'Content-Type': ['application/x-www-form-urlencoded'],
        'Host': ['mreaqd8hh6.execute-api.us-east-1.amazonaws.com'],
        'I-Twilio-Idempotency-Token': ['5bfe3d88-ce7c-4d0a-8f68-88da5b48dc37'],
        'User-Agent': ['TwilioProxy/1.1'],
        'X-Amzn-Trace-Id': ['Root=1-5e42f836-6da879586641cde482a02330'],
        'X-Forwarded-For': ['3.92.234.61'],
        'X-Forwarded-Port': ['443'],
        'X-Forwarded-Proto': ['https'],
        'X-Twilio-Signature': ['63dYsiunev1uIRnlHn8M3R3oQFw='],
        'accept': ['*/*'],
        'cache-control': ['max-age=259200']
    },
    'queryStringParameters': None,
    'multiValueQueryStringParameters': None,
    'requestContext': {
        'accountId': '614517820915',
        'apiId': 'mreaqd8hh6',
        'authorizer': {
            'claims': None,
            'scopes': None
        },
        'domainName': 'mreaqd8hh6.execute-api.us-east-1.amazonaws.com',
        'domainPrefix': 'mreaqd8hh6',
        'extendedRequestId': 'Hvu4kjiQoAMEQFQ=',
        'httpMethod': 'POST',
        'identity': {
            'accessKey': None,
            'accountId': None,
            'caller': None,
            'cognitoAuthenticationProvider': None,
            'cognitoAuthenticationType': None,
            'cognitoIdentityId': None,
            'cognitoIdentityPoolId': None,
            'principalOrgId': None,
            'sourceIp': '3.92.234.61',
            'user': None,
            'userAgent': 'TwilioProxy/1.1',
            'userArn': None
        },
        'path': '/prod/wooglin-body',
        'protocol': 'HTTP/1.1',
        'requestId': 'Hvu4kjiQoAMEQFQ=',
        'requestTime': '11/Feb/2020:18:53:42 +0000',
        'requestTimeEpoch': 1581447222774,
        'resourceId': None,
        'resourcePath': '/wooglin-body',
        'stage': 'prod'
    },
    'pathParameters': None,
    'stageVariables': None,
    'body': 'VG9Db3VudHJ5PVVTJlRvU3RhdGU9Q1QmU21zTWVzc2FnZVNpZD1TTTM1NzMzMDIxNzUwNTRiOGUxYjY0YTA1NDE1ZWE5YmIxJk51bU1lZGlhPTAmVG9DaXR5PUhBUlRGT1JEJkZyb21aaXA9NTUzNjQmU21zU2lkPVNNMzU3MzMwMjE3NTA1NGI4ZTFiNjRhMDU0MTVlYTliYjEmRnJvbVN0YXRlPU1OJlNtc1N0YXR1cz1yZWNlaXZlZCZGcm9tQ2l0eT1NT1VORCZCb2R5PUJvb2dhbG9vJkZyb21Db3VudHJ5PVVTJlRvPSUyQjE4NjA5NTY1MzIyJlRvWmlwPTA2MTA2Jk51bVNlZ21lbnRzPTEmTWVzc2FnZVNpZD1TTTM1NzMzMDIxNzUwNTRiOGUxYjY0YTA1NDE1ZWE5YmIxJkFjY291bnRTaWQ9QUM3ZWNiOTFmOTVhODk3YmNlNGI2ODE2NDYyNDA5YjQ4ZiZGcm9tPSUyQjE5NTIyNTU5MzQzJkFwaVZlcnNpb249MjAxMC0wNC0wMQ==',
    'isBase64Encoded': True
}
    wooglin.lambda_handler(data, 123)

    # My ID in BetaThetaPi 'UGZFWNPA8'
