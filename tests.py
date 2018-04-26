"""Test cases."""

import unittest
import tempfile
import json
import base64
import boto3
from six import string_types
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

        with open('aws_event_sample.json') as f_obj:
            self.aws_events = json.load(f_obj)

        self.s3_bucket_name, self.s3_object_key_name = (
            'aws_event_parser', 'test.json'
        )

        self.s3_client.create_bucket(Bucket='aws_event_parser')
        self.s3_client.put_object(
            Bucket=self.s3_bucket_name,
            Body=get_file_object(),
            Key=self.s3_object_key_name
        )

    def _s3(self, event, bucket, key):
        if isinstance(event, string_types):
            event = json.loads(event)

        raw_data = self.s3_client.get_object(
            Bucket=bucket,
            Key=key
        ).get('Body')

        data = get_event_data(event)

        while not raw_data._raw_stream.closed:
            yield raw_data._raw_stream.readline(), next(data)

    def test_s3(self):
        """Test for s3 event."""
        s3_event = self.aws_events['s3']
        for object_line, event_line in self._s3(
                s3_event, self.s3_bucket_name, self.s3_object_key_name):
            self.assertEqual(object_line, event_line)

    def test_kinesis_stream(self):
        """Test case for kinesis stream."""
        kinesis_stream_event = self.aws_events['kinesis_stream']
        data = get_event_data(kinesis_stream_event)
        for event in kinesis_stream_event['Records']:
            self.assertEqual(
                next(data),
                base64.b64decode(event['kinesis']['data'])
            )

    def test_dynamodb_stream(self):
        """Test case for dynamodb event."""
        dynamodb_stream_event = self.aws_events['dynamodb_stream']
        data = get_event_data(dynamodb_stream_event)
        for event in dynamodb_stream_event['Records']:
            self.assertEqual(
                next(data),
                event['dynamodb']['NewImage']
            )

    def test_sns_event(self):
        """Test case for sns event."""
        sns_event = self.aws_events['sns']
        data = get_event_data(sns_event)
        for event in sns_event['Records']:
            self.assertEqual(
                next(data),
                event['Sns']['Message']
            )

    def test_s3_sns_event(self):
        """Test case for s3->sns event."""
        s3_sns_event = self.aws_events['s3_sns']
        for event in s3_sns_event['Records']:
            for object_line, event_line in self._s3(
                    event['Sns']['Message'], self.s3_bucket_name,
                    self.s3_object_key_name):
                self.assertEqual(object_line, event_line)

    def tearDown(self):
        """Tear down."""
        self.aws_s3.stop()

if __name__ == '__main__':
    unittest.main()
