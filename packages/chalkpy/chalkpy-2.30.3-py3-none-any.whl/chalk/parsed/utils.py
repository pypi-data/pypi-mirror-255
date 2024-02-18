from datetime import timedelta
from typing import Union

from google.protobuf import duration_pb2

from chalk.utils.duration import parse_chalk_duration

# These are the maximum values that can be represented by a Duration proto.
MAX_DURATION_SECONDS = 315576000000
MAX_DURATION_NANOS = 999999999


def convert_raw_duration(duration: Union[str, timedelta]) -> timedelta:
    if isinstance(duration, str):
        duration = parse_chalk_duration(duration)
    return duration


def seconds_to_proto_duration(seconds: int) -> duration_pb2.Duration:
    if seconds == timedelta.max.total_seconds():
        resolved_timedelta = timedelta.max
    else:
        resolved_timedelta = timedelta(seconds=seconds)

    return timedelta_to_proto_duration(resolved_timedelta)


def timedelta_to_proto_duration(duration: timedelta) -> duration_pb2.Duration:
    pb_duration = duration_pb2.Duration()
    if duration == timedelta.max:
        pb_duration.seconds = MAX_DURATION_SECONDS
        pb_duration.nanos = MAX_DURATION_NANOS
    else:
        try:
            pb_duration.FromTimedelta(duration)
        except Exception as e:
            raise ValueError(f"Invalid duration: {e}")

    return pb_duration
