from __future__ import annotations
import enum
from typing import overload
import datetime
from time import timezone as time_timezone
from .dateutil.parser import parser, parserinfo
_EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)


class DateFormat(enum.Enum):
    YMD = '%Y-%m-%d'
    HMS = '%H:%M:%S'
    DEFAULT = f'{YMD} {HMS}'
    DEFAULT_MIL = f'{DEFAULT}.%f'
    T = f'{YMD}T{HMS}'
    T_MIL = f'{T}.%f'
    UTC = f'{T}%z'
    UTC_MIL = f'{T_MIL}%z'


timezone = datetime.timezone
timedelta = datetime.timedelta
datetime_time = datetime.time

TIME_START = 946684800  # 2000-1-1UTC0


class DateTime(datetime.datetime):
    Format = DateFormat

    @overload
    def __new__(cls, date: datetime.datetime):
        ...

    @overload
    def __new__(cls, date: datetime.date):
        ...

    @overload
    def __new__(cls, date: str):
        ...

    @overload
    def __new__(
            cls, year: int, month: int, day: int,
            hour: int = ..., minute: int = ..., second: int = ...,
            microsecond: int = ...,
            tzinfo: datetime.timezone | None = ..., *, fold: int = ...):
        ...

    def __new__(
        cls, year: int = ..., month: int = ..., day: int = ...,
        hour: int = ..., minute: int = ..., second: int = ...,
        microsecond: int = ...,
        tzinfo: datetime.timezone | None = ..., *, fold: int = 0,
    ):
        if year is None:
            return DateTime('2000-1-1')  # default set timestamp

        ii = isinstance
        if year is Ellipsis:
            return DateTime.now()
        if ii(year, float):
            year = int(year)
        if ii(year, int) and month is Ellipsis:
            return DateTime.fromtimestamp(year)
        if ii(year, str):
            x = DateTime.fromstring(year)
            return x
        if ii(year, datetime.datetime):
            x = year
            args = (
                x.year, x.month, x.day,
                x.hour, x.minute, x.second, x.microsecond,
                x.tzinfo,
            )
            return DateTime(*args, fold=x.fold)

        elif ii(year, datetime.date):
            x: datetime.date = year
            return DateTime(x.year, x.month, x.day, 0, 0, 0, 0, None, fold=0)

        if tzinfo is None:  # 无时区时，默认使用当前时区
            d = datetime.timedelta(seconds=-time_timezone)
            tzinfo = datetime.timezone(d)

        t = super().__new__(cls, year, month, day, hour, minute,
                            second, microsecond, tzinfo, fold=fold)
        return t

    @classmethod
    def fromstring(cls, date_str: str, dayfirst=False, yearfirst=False):
        r = parser(info=parserinfo(
            dayfirst=dayfirst,
            yearfirst=yearfirst,
        )).parse(date_str)

        return cls(r)

    def getDelta(self, tzinfo: datetime.timezone = None):
        if tzinfo is None:
            tzinfo = self.tzinfo
        if tzinfo is None:
            # 无时区信息则返回当前时区
            return time_timezone
        # 否则返回本DateTime的utc偏差
        x = self.replace(tzinfo=tzinfo)
        return -x.utcoffset().total_seconds()

    def getTime(self, delta: int = None) -> int:
        '''
        获取毫秒时间戳，并将时间输出为当前时区时间
        '''
        # 若未定义当前时区，则使用当前计算机时区
        if delta is None:
            delta = 0  # self.getDelta()

        # 将时间转换为UTC+X
        r = self.timestamp() - delta
        r *= 1e3  # 转换为毫秒
        return int(r)

    def tostring(
        self,
        format: str = DateFormat.DEFAULT,
        tz_info: datetime.timezone = None,
    ) -> str:
        '''
        格式化输出字符串，默认输出UTC+00:00的数值
        @param format:str:输出的格式
        @param tz_info:TzInfo:时区信息
        '''
        if format is None:
            format = DateFormat.DEFAULT
        if isinstance(format, DateFormat):
            format = format.value

        # 暂时不考虑时区
        # delta = self.getDelta(tz_info)
        # if delta != 0:
        #     x = DateTime.fromtimestamp(self.getTime(delta))
        #     return x.strftime(format)

        return self.strftime(format)

    def date(self) -> DateTime:
        return DateTime(super().date())

    @classmethod
    def now(cls):
        '''
        获取当前DateTime
        '''
        return super().now()

    @classmethod
    def today(cls):
        '''
        获取今日date
        '''
        return DateTime(super().today()).date()

    @classmethod
    def fromtimestamp(cls, t: int, tz=None):
        if t is None:
            t = TIME_START * 1e3
        if t < TIME_START:
            t = (TIME_START + t) * 1e3

        year_2300_second = 10000000000
        if t > year_2300_second:
            # 表示使用的毫秒制
            t /= 1e3

        # 将时间转换为UTC+X，不转换，则时间正确
        delta = 0 if tz is None else 0
        t += delta

        x = super().fromtimestamp(t, tz)
        return x

    def toRelativeTime(
        self,
        target: DateTime = ...,
        show_full_date_if_over: int = None,
    ) -> str:
        '''
        转换时间为相对时间
        @param target:DateTime:对比的时间，默认是现在
        @param show_full_date_if_over:int:当相差时间（天数）过多时返回绝对时间
        '''
        if target is Ellipsis:
            target = DateTime(tzinfo=self.tzinfo)
        target = DateTime(target)
        r: timedelta = target - self
        delta_time = r.days + r.seconds / 86400
        if show_full_date_if_over is not None and delta_time > show_full_date_if_over:
            return self.tostring()
        suffix = '后' if delta_time < 0 else '前'
        s_second = 1 / 86400
        v_time = abs(delta_time)
        if v_time < s_second * 60:
            return f'{int(v_time * 86400)}秒{suffix}'
        if v_time < s_second * 3600:
            return f'{int(v_time * 1440)}分钟{suffix}'
        if v_time < 1:
            return f'{int(v_time * 24)}小时{suffix}'
        if v_time < 14:
            return f'{int(v_time)}天{suffix}'
        if v_time < 30:
            return f'{int(v_time/7)}周{suffix}'

        if v_time < 365:
            v_month = target.month - self.month
            if v_month < 0:
                v_month += 12
            return f'{v_month}月{suffix}'

        v_year = abs(self.year - target.year)
        return f'{v_year}年{suffix}'

    def __add__(self, other):
        t = datetime.timedelta
        if isinstance(other, int) or isinstance(other, float):
            other = t(milliseconds=other)
        return DateTime(super().__add__(other))

    def __sub__(self, other):
        t = datetime.timedelta
        if isinstance(other, int) or isinstance(other, float):
            other = t(milliseconds=other)
        elif isinstance(other, str):
            other = DateTime.fromstring(other)

        if isinstance(other, t):
            return super().__sub__(other)
        if not isinstance(other, datetime.datetime):
            raise Exception(f'invalid type in date:{type(other)}')
        other = DateTime(other.getTime())

        result = super().__sub__(other)
        return result

    def __eq__(self, other: object) -> bool:
        other = DateTime(other)
        return self.getTime() == other.getTime()
