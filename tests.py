"""Test cases."""

import unittest
import tempfile
import json
import base64
import boto3
from moto import mock_s3
from aws import get_event_data

def get_file_object():
    """Generate temp file object."""
    file_object = tempfile.TemporaryFile()

    file_object.write(
        "\n".join([
            json.dumps({"repo_name": "awseventparser"}),
            "Simple test line",
            "I love python"
        ]).encode('utf-8')
    )

    file_object.seek(0)
    return file_object

class TestAwsEventParser(unittest.TestCase):
    """Aws event parser test cases."""
    def setUp(self):
        """SetUp."""
        self.s3_client = boto3.client('s3')
        self.aws_s3 = mock_s3()
        self.aws_s3.start()

        self.s3_bucket_name, self.s3_object_key_name = (
            'aws_event_parser', 'test.json'
        )

        self.s3_client.create_bucket(Bucket='aws_event_parser')
        self.s3_client.put_object(
            Bucket=self.s3_bucket_name,
            Body=get_file_object(),
            Key=self.s3_object_key_name
        )

    def test_s3(self):
        """Test for s3 event."""
        s3_event = {
            "Records": [{
                "eventVersion": "2.0",
                "eventTime": "1970-01-01T00:00:00.000Z",
                "requestParameters": {
                    "sourceIPAddress": "127.0.0.1"
                },
                "s3": {
                    "configurationId": "testConfigRule",
                    "object": {
                        "eTag": "0123456789abcdef0123456789abcdef",
                        "sequencer": "0A1B2C3D4E5F678901",
                        "key": "test.json",
                        "size": 1024
                    },
                    "bucket": {
                        "arn": "arn:aws:s3:::aws_event_parser",
                        "name": "aws_event_parser",
                        "ownerIdentity": {
                            "principalId": "EXAMPLE"
                        }
                    },
                    "s3SchemaVersion": "1.0"
                },
                "responseElements": {
                    "x-amz-id-2": ("EXAMPLE123/5678abcdefghijklambdai"
                                   "sawesome/mnopqrstuvwxyzABCDEFGH"),
                    "x-amz-request-id": "EXAMPLE123456789"
                },
                "awsRegion": "us-east-1",
                "eventName": "ObjectCreated:Put",
                "userIdentity": {
                    "principalId": "EXAMPLE"
                },
                "eventSource": "aws:s3"
            }]
        }
        data = get_event_data(s3_event)
        with get_file_object() as file:
            for line in file:
                self.assertEqual(next(data), line)

    def test_kinesis_stream(self):
        """Test case for kinesis stream."""
        kinesis_stream_event = {
            "Records": [{
                "eventID": "shardId-000000000000:495451152434909",
                "eventVersion": "1.0",
                "kinesis": {
                    "partitionKey": "partitionKey-3",
                    "data": "eyJ0ZXN0IjogInRlc3RpbmcgaGVyZSJ9",
                    "kinesisSchemaVersion": "1.0",
                    "sequenceNumber": "4954511524349098501828006771"
                },
                "invokeIdentityArn": "identityarn",
                "eventName": "aws:kinesis:record",
                "eventSourceARN": "eventsourcearn",
                "eventSource": "aws:kinesis",
                "awsRegion": "us-east-1"
            }]
        }
        data = get_event_data(kinesis_stream_event)
        for event in kinesis_stream_event['Records']:
            self.assertEqual(
                next(data),
                base64.b64decode(event['kinesis']['data'])
            )

    def tearDown(self):
        """tear down."""
        self.aws_s3.stop()

if __name__ == '__main__':
    unittest.main()
