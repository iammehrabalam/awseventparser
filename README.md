# Aws Event parser

[![Build Status](https://travis-ci.org/iammehrabalam/awseventparser.png?branch=master)](https://travis-ci.org/iammehrabalam/awseventparser)

## Installation

## Usages
```python
from awsevents import get_event_data
for event_data in get_event_data(aws_event):
    print(event_data)
```