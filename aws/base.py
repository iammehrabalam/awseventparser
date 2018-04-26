"""Kind of interface."""


class BaseEvent(object):
    """Base class for AWS events."""

    EVENT_SOURCE = None

    def get_event_payload(self, event):
        """Return event payload."""
        raise NotImplementedError("Implement .get_event_payload()")

    def get_event_metadata(self, event):
        """Return event metadata."""
        raise NotImplementedError("Implement .get_event_metadata()")
