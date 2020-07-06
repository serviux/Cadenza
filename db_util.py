import boto3
dynamodb = boto3.resource("dynamodb")


def create_connect_table():
    """tries to connect to the table or create the table"""
    table = None
    try:
        table = dynamodb.Table("music_data")
        table.item_count
        return table
    # TODO: Figure out better exception to catch
    except Exception as ex:
        table = dynamodb.create_table(
            TableName='music_data',
            KeySchema=[
                {
                    'AttributeName': "title",
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': "artist",
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S',
                },
                {
                    'AttributeName': 'artist',
                    'AttributeType': 'S',
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }

        )
        table.meta.client.get_waiter('table_exists').wait(TableName='music_data')
        return table
