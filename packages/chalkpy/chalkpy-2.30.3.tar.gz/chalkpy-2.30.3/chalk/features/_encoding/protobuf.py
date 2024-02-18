from chalk._gen.chalk.arrow.v1 import arrow_pb2 as pb

PROTOBUF_TO_UNIT = {
    pb.TimeUnit.TIME_UNIT_SECOND: "s",
    pb.TimeUnit.TIME_UNIT_MILLISECOND: "ms",
    pb.TimeUnit.TIME_UNIT_MICROSECOND: "us",
    pb.TimeUnit.TIME_UNIT_NANOSECOND: "ns",
}


UNIT_TO_PROTOBUF = {
    "s": pb.TimeUnit.TIME_UNIT_SECOND,
    "ms": pb.TimeUnit.TIME_UNIT_MILLISECOND,
    "us": pb.TimeUnit.TIME_UNIT_MICROSECOND,
    "ns": pb.TimeUnit.TIME_UNIT_NANOSECOND,
}
