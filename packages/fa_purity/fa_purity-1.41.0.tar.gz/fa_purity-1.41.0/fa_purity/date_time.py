from __future__ import (
    annotations,
)

from dataclasses import (
    dataclass,
    field,
)
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from fa_purity.cmd.core import (
    Cmd,
)
from fa_purity.result import (
    Result,
    ResultE,
)
from fa_purity.utils import (
    cast_exception,
)


@dataclass(frozen=True)
class _Private:
    pass


@dataclass(frozen=True)
class DatetimeTZ:
    _private: _Private = field(repr=False, hash=False, compare=False)
    date_time: datetime

    @staticmethod
    def assert_tz(time: datetime) -> ResultE[DatetimeTZ]:
        if time.tzinfo is not None:
            return Result.success(DatetimeTZ(_Private(), time))
        err = ValueError("datetime must have a timezone")
        return Result.failure(err, DatetimeTZ).alt(cast_exception)

    def __add__(self, delta: timedelta) -> DatetimeTZ:
        return self.assert_tz(self.date_time + delta).unwrap()

    def __sub__(self, delta: timedelta) -> DatetimeTZ:
        return self.assert_tz(self.date_time - delta).unwrap()


@dataclass(frozen=True)
class DatetimeUTC:
    _private: _Private = field(repr=False, hash=False, compare=False)
    date_time: datetime

    @staticmethod
    def assert_utc(time: datetime | DatetimeTZ) -> ResultE[DatetimeUTC]:
        _time = time if isinstance(time, datetime) else time.date_time
        if _time.tzinfo == timezone.utc:
            return Result.success(DatetimeUTC(_Private(), _time))
        err = ValueError(
            f"datetime must have UTC timezone but got {_time.tzinfo}"
        )
        return Result.failure(err, DatetimeUTC).alt(cast_exception)

    def __add__(self, delta: timedelta) -> DatetimeUTC:
        return self.assert_utc(self.date_time + delta).unwrap()

    def __sub__(self, delta: timedelta) -> DatetimeUTC:
        return self.assert_utc(self.date_time - delta).unwrap()


@dataclass(frozen=True)
class DatetimeFactory:
    EPOCH_START: DatetimeUTC = DatetimeUTC.assert_utc(
        datetime.fromtimestamp(0, timezone.utc)
    ).unwrap()

    @staticmethod
    def new_utc(
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        microsecond: int,
    ) -> DatetimeUTC:
        return DatetimeUTC.assert_utc(
            datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                microsecond,
                tzinfo=timezone.utc,
            )
        ).unwrap()

    @staticmethod
    def new_tz(
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        microsecond: int,
        zone: timezone,
    ) -> DatetimeTZ:
        return DatetimeTZ.assert_tz(
            datetime(
                year,
                month,
                day,
                hour,
                minute,
                second,
                microsecond,
                tzinfo=zone,
            )
        ).unwrap()

    @staticmethod
    def to_tz(
        date_time: datetime | DatetimeUTC, time_zone: timezone
    ) -> DatetimeTZ:
        item = (
            date_time
            if isinstance(date_time, datetime)
            else date_time.date_time
        )
        return DatetimeTZ.assert_tz(item.astimezone(time_zone)).unwrap()

    @classmethod
    def to_utc(cls, date_time: DatetimeTZ) -> DatetimeUTC:
        return DatetimeUTC.assert_utc(
            cls.to_tz(date_time.date_time, timezone.utc)
        ).unwrap()

    @staticmethod
    def date_now() -> Cmd[DatetimeUTC]:
        return Cmd.from_cmd(
            lambda: DatetimeUTC.assert_utc(datetime.now(timezone.utc)).unwrap()
        )
