import boto3

def main():






def dynamo_connect(tablename="NONE"):
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    if tablename == "NONE":
        return dynamodb
    else:
        table = dynamodb.Table(tablename)
        return table


main()

