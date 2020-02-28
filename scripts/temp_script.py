import boto3

dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table("toga_party")

for x in range(0, 48):
    table.put_item(
        Item={
            'number': str(x),
            'name': "Yeeter Mcgee",
            'arrived': str(x),
            'help_flag': False,
            'help_flag_raised': "n/a"
        }
    )
