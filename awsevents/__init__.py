from .aws_event_parser import AwsEventFactory

def get_event_data(event):
    """Return generator of payload."""
    return AwsEventFactory.factory(event).get_event_payload(event)

def get_event_metadata(event):
    return AwsEventFactory.factory(event).get_event_metadata(event)
