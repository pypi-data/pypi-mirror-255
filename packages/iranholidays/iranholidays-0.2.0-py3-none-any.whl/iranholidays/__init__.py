from collections.abc import Callable as _Callable, Container as _Container
from datetime import date as _date, datetime as _datetime
from typing import Literal as _Literal

from hijri_converter import Gregorian as _Gregorian, Hijri as _Hijri
from jdatetime import date as _jdate, datetime as _jdatetime
from jdatetime.jalali import (
    GregorianToJalali as _GregorianToJalali,
    JalaliToGregorian as _JalaliToGregorian,
)

__version__ = '0.2.0'

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


OffOccasion = _Literal[False] | str
Weekend = _Container[int]


def off_occasion_gregorian(
    date: _date, /, weekend: Weekend = (4,)
) -> OffOccasion:
    if date.weekday() in weekend:
        return 'Weekend'
    year, month, day = date.year, date.month, date.day
    _, hm, hd = _Gregorian(year, month, day).to_hijri().datetuple()
    if (occ := HIJRI_HOLIDAYS[hm].get(hd)) is not None:
        return occ
    sy, sm, sd = _GregorianToJalali(year, month, day).getJalaliList()
    return SOLAR_HOLIDAYS[sm].get(sd)


def off_occasion_solar(
    date: _jdate, /, weekend: Weekend = (4,)
) -> OffOccasion:
    if date.weekday() in weekend:
        return 'Weekend'
    month, day = date.month, date.day
    if (occ := SOLAR_HOLIDAYS[month].get(day)) is not None:
        return occ
    hdate = _Gregorian(*date.togregorian().timetuple()[:3]).to_hijri()
    hy, hm, hd = hdate.datetuple()
    return HIJRI_HOLIDAYS[hm].get(hd)


def off_occasion_lunar(
    date: _Hijri, /, weekend: Weekend = (4,)
) -> OffOccasion:
    if date.weekday() in weekend:
        return 'Weekend'
    month, day = date.month, date.day
    if (occ := HIJRI_HOLIDAYS[month].get(day)) is not None:
        return occ
    sy, sm, sd = _GregorianToJalali(
        *date.to_gregorian().datetuple()
    ).getJalaliList()
    return SOLAR_HOLIDAYS[sm].get(sd)


Calendar = _Literal['S', 'L', 'G']


def off_occasion_ymd(
    year: int,
    month: int,
    day: int,
    calendar: Calendar,
    /,
    weekend: Weekend = (4,),
) -> OffOccasion:
    if calendar == 'S':
        if (occ := SOLAR_HOLIDAYS[month].get(day)) is not None:
            return occ
        gy, gm, gd = _JalaliToGregorian(year, month, day).getGregorianList()
        gdate = _Gregorian(gy, gm, gd)
        if _date(gy, gm, gd).weekday() in weekend:
            return 'Weekend'
        hdate = gdate.to_hijri()
        hy, hm, hd = hdate.datetuple()
        return HIJRI_HOLIDAYS[hm].get(hd)

    elif calendar == 'G':
        gdate = _date(year, month, day)
        return off_occasion_gregorian(gdate, weekend)

    elif calendar == 'L':
        if (occ := HIJRI_HOLIDAYS[month].get(day)) is not None:
            return occ
        hdate = _Hijri(year, month, day)
        if hdate.weekday() in weekend:
            return 'Weekend'
        sy, sm, sd = _GregorianToJalali(
            *hdate.to_gregorian().datetuple()
        ).getJalaliList()
        return SOLAR_HOLIDAYS[sm].get(sd)

    else:
        raise ValueError(f'unknown {calendar=}')


DateTuple = tuple[int, int, int, Calendar]


def _off_occasion_tuple(
    date: DateTuple, /, weekend: Weekend = (4,)
) -> OffOccasion:
    return off_occasion_ymd(*date, weekend=weekend)


AnyDate = _date | DateTuple | _jdate | _Hijri
_date_handler: dict[
    type[AnyDate], _Callable[[AnyDate, Weekend], OffOccasion]
] = {
    _Hijri: off_occasion_lunar,
    _date: off_occasion_gregorian,
    _Gregorian: off_occasion_gregorian,
    _datetime: off_occasion_gregorian,
    _jdatetime: off_occasion_solar,
    _jdate: off_occasion_solar,
    tuple: _off_occasion_tuple,
}


def off_occasion(date: AnyDate, /, weekend: Weekend = (4,)) -> OffOccasion:
    """Return occasion string if date is a non-workday (off day)."""
    return _date_handler[type(date)](date, weekend)


def holiday_occasion(date: AnyDate) -> OffOccasion:
    """Return False if date is not a holiday, otherwise the occasion string.

    If date is a holiday, instead of returning `True`, the first detected
    occasion will be returned as as string.

    This is a shortcut for `is_non_workday(date, ())`.
    """
    return off_occasion(date, ())


def set_default_weekend(weekend: Weekend):
    """Change the default weekend value for all functions."""
    defaults = (weekend,)
    for f in (
        off_occasion,
        off_occasion_ymd,
        off_occasion_lunar,
        off_occasion_solar,
        off_occasion_gregorian,
    ):
        f.__defaults__ = defaults
