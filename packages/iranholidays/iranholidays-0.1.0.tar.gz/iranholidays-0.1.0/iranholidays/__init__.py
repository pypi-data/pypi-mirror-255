from collections.abc import Callable as _Callable, Container as _Container
from datetime import date as _date, datetime as _datetime
from typing import Literal as _Literal

from hijri_converter import Gregorian as _Gregorian, Hijri as _Hijri
from jdatetime import date as _jdate, datetime as _jdatetime
from jdatetime.jalali import (
    GregorianToJalali as _GregorianToJalali,
    JalaliToGregorian as _JalaliToGregorian,
)

__version__ = '0.1.0'

SOLAR_HOLIDAYS = [
    None,
    {  # Farvardīn
        1: 'Nowruz',
        2: 'Nowruz',
        3: 'Nowruz',
        4: 'Nowruz',
        12: 'Islamic Republic Day',
        13: 'Sizdah Be-dar',
    },
    {  # 2: Ordībehešt
    },
    {  # 3: Khordād
        14: 'death of Ruhollah Khomeini',
        15: 'the 15 Khordad uprising',
    },
    {  # 4: Tīr
    },
    {  # 5: Mordād
    },
    {  # 6: Shahrīvar
    },
    {  # 7: Mehr
    },
    {  # 8: Ābān
    },
    {  # 9: Āzar
    },
    {  # 10: Dey
    },
    {  # 11: Bahman
        22: 'Islamic Revolution',
    },
    {  # 12: Esfand
        29: 'Nationalization of the Iranian oil industry',
        30: 'Nowruz',
    },
]

HIJRI_HOLIDAYS = [
    None,
    {  # 1: al-Muḥarram
        9: "Tasu'a",
        10: 'Ashura',
    },
    {  # 2: Ṣafar
        20: "Arba'een",
        28: 'Death of Muhammad, Martyrdom of Hasan ibn Ali',
        30: 'Martyrdom of Ali ibn Musa al-Rida',
    },
    {  # 3: Rabīʿ al-ʾAwwal
        8: 'Martyrdom of Hasan al-Askari',
        17: "Mawlid an-Nabi, Birth of Ja'far al-Sadiq",
    },
    {  # 4: Rabīʿ ath-Thānī
    },
    {  # 5: Jumādā al-ʾŪlā
    },
    {  # 6: Jumādā ath-Thāniyah
        3: 'Death of Fatima',
    },
    {  # 7: Rajab
        13: "Birth of Ja'far al-Sadiq",
        27: "Muhammad's first revelation",
    },
    {  # 8: Shaʿbān
        15: "Mid-Sha'ban",
    },
    {  # 9: Ramaḍān
        21: 'Martyrdom of Ali',
    },
    {  # 10: Shawwāl
        1: 'Eid al-Fitr',
        2: 'Eid al-Fitr',
        25: "Martyrdom of Ja'far al-Sadiq",
    },
    {  # 11: Ḏū al-Qaʿdah
    },
    {  # 12: Ḏū al-Ḥijjah
        10: 'Eid al-Adha',
        18: 'Eid al-Ghadir',
    },
]


_IsWorkday = _Literal[True] | str
_Weekend = _Container[int]


def is_workday_gregorian(
    date: _date, /, weekend: _Weekend = (4,)
) -> _IsWorkday:
    if date.weekday() in weekend:
        return 'Weekend'
    year, month, day = date.year, date.month, date.day
    _, hm, hd = _Gregorian(year, month, day).to_hijri().datetuple()
    if (h := HIJRI_HOLIDAYS[hm].get(hd)) is not None:
        return h
    sy, sm, sd = _GregorianToJalali(year, month, day).getJalaliList()
    return SOLAR_HOLIDAYS[sm].get(sd) or True


def is_workday_solar(date: _jdate, /, weekend: _Weekend = (4,)) -> _IsWorkday:
    if date.weekday() in weekend:
        return 'Weekend'
    month, day = date.month, date.day
    if (h := SOLAR_HOLIDAYS[month].get(day)) is not None:
        return h
    hdate = _Gregorian(*date.togregorian().timetuple()[:3]).to_hijri()
    hy, hm, hd = hdate.datetuple()
    return HIJRI_HOLIDAYS[hm].get(hd) or True


def is_workday_lunar(date: _Hijri, /, weekend: _Weekend = (4,)) -> _IsWorkday:
    if date.weekday() in weekend:
        return 'Weekend'
    month, day = date.month, date.day
    if (h := HIJRI_HOLIDAYS[month].get(day)) is not None:
        return h
    sy, sm, sd = _GregorianToJalali(
        *date.to_gregorian().datetuple()
    ).getJalaliList()
    return SOLAR_HOLIDAYS[sm].get(sd) or True


Calendar = _Literal['S', 'L', 'G']


def is_workday_ymd(
    year: int,
    month: int,
    day: int,
    calendar: Calendar,
    /,
    weekend: _Weekend = (4,),
) -> _IsWorkday:
    if calendar == 'S':
        if (h := SOLAR_HOLIDAYS[month].get(day)) is not None:
            return h
        gy, gm, gd = _JalaliToGregorian(year, month, day).getGregorianList()
        gdate = _Gregorian(gy, gm, gd)
        if _date(gy, gm, gd).weekday() in weekend:
            return 'Weekend'
        hdate = gdate.to_hijri()
        hy, hm, hd = hdate.datetuple()
        return HIJRI_HOLIDAYS[hm].get(hd) or True

    elif calendar == 'G':
        gdate = _date(year, month, day)
        return is_workday_gregorian(gdate, weekend)

    elif calendar == 'L':
        if (h := HIJRI_HOLIDAYS[month].get(day)) is not None:
            return h
        hdate = _Hijri(year, month, day)
        if hdate.weekday() in weekend:
            return 'Weekend'
        sy, sm, sd = _GregorianToJalali(
            *hdate.to_gregorian().datetuple()
        ).getJalaliList()
        return SOLAR_HOLIDAYS[sm].get(sd) or True

    else:
        raise ValueError(f'unknown {calendar=}')


DateTuple = tuple[int, int, int, Calendar]


def _is_workday_tuple(
    date: DateTuple, /, weekend: _Weekend = (4,)
) -> _IsWorkday:
    return is_workday_ymd(*date, weekend=weekend)


AnyDate = _date | DateTuple | _jdate | _Hijri
_date_handler: dict[
    type[AnyDate], _Callable[[AnyDate, _Weekend], _IsWorkday]
] = {
    _Hijri: is_workday_lunar,
    _date: is_workday_gregorian,
    _Gregorian: is_workday_gregorian,
    _datetime: is_workday_gregorian,
    _jdatetime: is_workday_solar,
    _jdate: is_workday_solar,
    tuple: _is_workday_tuple,
}


def is_workday(date: AnyDate, /, weekend: _Weekend = (4,)) -> _IsWorkday:
    """Return True if date is a workday and is not a holiday.

    Warning: If date is not a workday, the occasion or 'Weekend' will be
    returned instead of returning False. Therefore, `if is_workday(date):` will
    *not* work as expected, use `if is_workday(date) is True:` instead.
    """
    return _date_handler[type(date)](date, weekend)


def is_holiday(date: AnyDate) -> _Literal[False] | str:
    """Return False if date is not a holiday, otherwise the occasion string.

    If date is a holiday, instead of returning `True`, the first detected
    occasion will be returned as as string.

    This is a shortcut for `is_workday(date, weekend=())`.
    """
    workday = is_workday(date, ())
    return False if workday is True else workday


def set_default_weekend(weekend: _Weekend):
    """Change the default weekend value for all functions."""
    defaults = (weekend,)
    for f in (
        is_workday,
        is_workday_ymd,
        is_workday_lunar,
        is_workday_solar,
        is_workday_gregorian,
    ):
        f.__defaults__ = defaults
