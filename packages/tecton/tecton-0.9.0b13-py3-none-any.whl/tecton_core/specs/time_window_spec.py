import datetime
import enum
from typing import Tuple

import attrs
from google.protobuf.duration_pb2 import Duration
from typeguard import typechecked

from tecton_core.time_utils import timedelta_to_proto
from tecton_core.time_utils import to_human_readable_str
from tecton_proto.args.feature_view_pb2 import TimeWindow as TimeWindowArgs
from tecton_proto.common.time_window_pb2 import LifetimeWindow
from tecton_proto.common.time_window_pb2 import RelativeTimeWindow
from tecton_proto.common.time_window_pb2 import TimeWindow


__all__ = [
    "LifetimeWindowSpec",
    "RelativeTimeWindowSpec",
    "TimeWindowSpec",
    "create_time_window_spec_from_data_proto",
    "window_spec_to_window_data_proto",
]


class _WindowSortEnum(enum.IntEnum):
    TIME_WINDOW = 1
    LIFETIME = 2


_TimeWindowSortKey = Tuple[_WindowSortEnum, tuple]


class TimeWindowSpec:
    def offset_string(self) -> str:
        """Offset string for use in aggregation name construction."""
        raise NotImplementedError

    def window_duration_string(self) -> str:
        """Window duration for use in aggregation name construction."""
        raise NotImplementedError

    def to_string(self) -> str:
        """Full name specification for use in secondary key aggregation output column."""
        offset_name = self.offset_string()
        if offset_name:
            offset_name = f"_{self.offset_string()}"
        return f"{self.window_duration_string()}{offset_name}"

    def to_sort_tuple(self) -> _TimeWindowSortKey:
        """Tuple for sorting time windows.

        This should start with the appropriate _WindowSortEnum, and then use any attributes for the specific window type for sorting.
        This approach ensures that we have a multi-layer sort where each sub-type is collocated together.
        """
        raise NotImplementedError


@attrs.frozen
class LifetimeWindowSpec(TimeWindowSpec):
    def to_proto(self) -> LifetimeWindow:
        return LifetimeWindow()

    def to_string(self) -> str:
        return "lifetime"

    def offset_string(self) -> str:
        return ""

    def window_duration_string(self) -> str:
        return "lifetime"

    def to_sort_tuple(self) -> _TimeWindowSortKey:
        return (_WindowSortEnum.LIFETIME, ())


@attrs.frozen(order=True)
class RelativeTimeWindowSpec(TimeWindowSpec):
    # window_end represents the offset (negative or zero)
    # window_start represents the offset - window_duration (negative)
    window_start: datetime.timedelta
    window_end: datetime.timedelta

    @classmethod
    @typechecked
    def from_data_proto(cls, proto: RelativeTimeWindow) -> "RelativeTimeWindowSpec":
        return cls(
            window_start=proto.window_start.ToTimedelta(),
            window_end=proto.window_end.ToTimedelta(),
        )

    @classmethod
    @typechecked
    def from_args_proto(cls, proto: TimeWindowArgs) -> "RelativeTimeWindowSpec":
        return cls(
            window_start=Duration(
                seconds=proto.offset.seconds - proto.window_duration.seconds,
                nanos=proto.offset.nanos - proto.window_duration.nanos,
            ).ToTimedelta(),
            window_end=Duration(seconds=proto.offset.seconds, nanos=proto.offset.nanos).ToTimedelta(),
        )

    def to_data_proto(self) -> RelativeTimeWindow:
        return RelativeTimeWindow(
            window_start=timedelta_to_proto(self.window_start),
            window_end=timedelta_to_proto(self.window_end),
        )

    @property
    def window_duration(self) -> datetime.timedelta:
        return self.window_end - self.window_start

    @property
    def offset(self) -> datetime.timedelta:
        return self.window_end

    def to_args_proto(self) -> TimeWindowArgs:
        return TimeWindowArgs(
            window_duration=timedelta_to_proto(self.window_duration),
            offset=timedelta_to_proto(self.offset),
        )

    def to_sort_tuple(self) -> _TimeWindowSortKey:
        return (_WindowSortEnum.TIME_WINDOW, (self.window_start, self.window_end))

    def offset_string(self) -> str:
        return "offset_" + to_human_readable_str(-self.offset) if self.offset.total_seconds() < 0 else ""

    def window_duration_string(self) -> str:
        return to_human_readable_str(self.window_duration)


def window_spec_to_window_data_proto(window_spec: TimeWindowSpec) -> TimeWindow:
    if isinstance(window_spec, RelativeTimeWindowSpec):
        return TimeWindow(relative_time_window=window_spec.to_data_proto())
    elif isinstance(window_spec, LifetimeWindowSpec):
        return TimeWindow(lifetime_window=window_spec.to_proto())
    else:
        msg = f"Unexpected time window type: {type(window_spec)}"
        raise ValueError(msg)


def create_time_window_spec_from_data_proto(proto: TimeWindow) -> TimeWindowSpec:
    if proto.HasField("relative_time_window"):
        return RelativeTimeWindowSpec.from_data_proto(proto.relative_time_window)
    elif proto.HasField("lifetime_window"):
        return LifetimeWindowSpec()
    else:
        msg = f"Unexpected time window type: {proto}"
        raise ValueError(msg)
