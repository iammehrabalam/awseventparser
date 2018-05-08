"""Aws Event Parser."""
import logging
try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote

import base64
import json
import boto3
from awsevents.exceptions import EventNotExist
from awsevents.base import BaseEvent

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')


class AwsKinesisStreamEvent(BaseEvent):
    """Aws Kinesis Stream event class."""

    EVENT_SOURCE = "aws:kinesis"

    def get_event_payload(self, event):
        """Implement get event payload for kinesis stream event.

        :rtype: generator (on next get str/unicode type)
        """
        for record in event.get('Records') or event.get('records') or []:
            try:
                yield base64.b64decode(
                    record['kinesis']['data']
                )
            except ValueError as err:
                logger.error(err, exc_info=True)


class AwsDynamodbEvent(BaseEvent):
    """Aws DynamoDb event class."""

    EVENT_SOURCE = "aws:dynamodb"

    def get_event_payload(self, event):
        """Implement get payload for dynamodb event.

        :rtype: generator (on next get dict type)
        """
        for record in event.get('Records'):
            yield record.get('dynamodb', {}).get('NewImage')


class AwsS3Event(BaseEvent):
    """Aws s3 event class."""

    EVENT_SOURCE = "aws:s3"
    def get_event_metadata(self, event):
        """Event meta data."""
        for record in event.get('Records'):
            yield {
                "s3_event_time": record['eventTime'],
                "s3_bucket": record.get('s3', {}).get('bucket', {}).get('name'),
                "s3_object": record.get('s3', {}).get('object', {}).get('key'),
                "s3_object_size": record.get('s3', {}).get('object', {}).get('size'),
            }

    def get_event_payload(self, event):
        """Overriding default implementation.

        :rtype: generator (on next get str/unicode type)
        """
        for record in event.get('Records'):
            s3_bucket_key = record.get('s3', {})
            if not (s3_bucket_key.get('bucket', {}).get('name') and
                    s3_bucket_key.get('object', {}).get('key')):
                logger.error(
                    "Invalid s3 event::data::{}".format(s3_bucket_key)
                )
                continue

            bucket_name, key_name = (
                unquote(s3_bucket_key['bucket']['name']),
                unquote(s3_bucket_key['object']['key'])
            )

            try:

                logger.info(
                    "fetching file::{}/{}".format(bucket_name, key_name)
                )
                res = s3_client.get_object(
                    Bucket=bucket_name, Key=key_name
                )

                logger.debug("Response:: {}".format(res))
            except Exception as err:
                logger.error(err, exc_info=True)

            else:
                if not res.get('Body'):
                    continue

                data_stream = res.get('Body')
                while not data_stream._raw_stream.closed:
                    yield data_stream._raw_stream.readline()


class AwsSNSEvent(BaseEvent):
    """Aws SNS event class."""

    EVENT_SOURCE = "aws:sns"

    def get_event_metadata(self, event):
        """Event meta data."""
        for record in event.get('Records'):
            meta_data = {
                "sns_topic_arn": record['Sns']['TopicArn'],
                "sns_message_id": record['Sns']['MessageId']
            }
            message = record.get('Sns', {}).get('Message')
            event_obj = self.get_next_event_obj(message)
            if event_obj:
                for data in event_obj.get_event_metadata(json.loads(message)):
                    meta_data.update(data)
                    yield meta_data
            else:
                yield meta_data

    def get_next_event_obj(self, msg):
        """Checking is given message is event."""
        try:
            return AwsEventFactory.factory(json.loads(msg))
        except (EventNotExist, ValueError):
            return None

    def get_event_payload(self, event):
        """Implement get event data for sns event."""
        for record in event.get('Records') or event.get('records') or []:
            message = record.get('Sns', {}).get('Message')

            # Checking if any known event source is present and
            # returning the required payload if found.

            event_obj = self.get_next_event_obj(message)
            if event_obj:
                for data in event_obj.get_event_payload(json.loads(message)):
                    yield data
            else:
                yield message

class AwsEventFactory(object):
    """Aws Event object generator."""

    @classmethod
    def get_event_type(cls, event):
        """Get event type."""
        records = event.get('Records') or event.get('records') or []
        if not records:
            return None

        logger.info(
            "Total event count:{}".format(len(records))
        )
        return dict(
            zip(map(lambda x: str(x).lower(), records[0].keys()), records[0].values())
        ).get('eventsource')

    @classmethod
    def factory(cls, event):
        """Object creater."""
        if not isinstance(event, dict):
            raise TypeError("event must be of type dict")

        event_type = cls.get_event_type(event)
        for sub_class in BaseEvent.__subclasses__():
            if getattr(sub_class, "EVENT_SOURCE", None) == event_type:
                return sub_class()

        raise EventNotExist(event_type)
