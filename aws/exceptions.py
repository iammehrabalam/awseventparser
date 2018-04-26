"""Custom exceptions."""


class EventNotExist(Exception):
    """Event not exist Exception."""

    def __init__(self, event_type, *args, **kwargs):
        """Constructor."""
        self.message = "event_type:: {} parser not exist".format(event_type)
        super(EventNotExist, self).__init__(self.message, *args, **kwargs)
