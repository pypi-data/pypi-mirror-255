import datetime
import functools
import re


def fix_message_timestamp(func):
    @functools.wraps(func)
    def inner(message):
        # Fix `pamqp` naive timestamp
        if message.timestamp:
            message.timestamp = message.timestamp.replace(tzinfo=datetime.timezone.utc)

        return func(message)

    return inner


def clean_service_name(service_name):
    return re.sub("[^a-z0-9-]+", "-", service_name.strip().lower())
