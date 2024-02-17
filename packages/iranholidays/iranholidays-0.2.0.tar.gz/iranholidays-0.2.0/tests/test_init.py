from datetime import date, datetime

from hijri_converter import Hijri
from jdatetime import date as jdate, datetime as jdatetime
from pytest import raises

from iranholidays import (
    HIJRI_HOLIDAYS,
    SOLAR_HOLIDAYS,
    holiday_occasion,
    off_occasion,
    off_occasion_lunar,
    set_default_weekend,
)

assert len(HIJRI_HOLIDAYS) == len(SOLAR_HOLIDAYS) == 13


def test_holiday_occasion_solar_calendar():
    # In reality, this was NOT a holiday in Iran (30st of Ramazan)
    assert holiday_occasion((1402, 2, 1, 'S')) == 'Eid al-Fitr'
    assert holiday_occasion((1402, 2, 2, 'S')) == 'Eid al-Fitr'
    # In reality, this WAS a holiday in Iran (2nd of Shawal)
    assert holiday_occasion((1402, 2, 3, 'S')) is None
    assert holiday_occasion((1402, 2, 4, 'S')) is None
    assert holiday_occasion((1402, 1, 13, 'S')) == 'Sizdah Be-dar'


def test_holiday_occasion_gregorian_calendar():
    assert holiday_occasion((2023, 4, 21, 'G')) == 'Eid al-Fitr'
    assert holiday_occasion((2023, 4, 22, 'G')) == 'Eid al-Fitr'
    # In reality, this WAS a holiday in Iran (2nd of Shawal)
    assert holiday_occasion((2023, 4, 23, 'G')) is None
    assert holiday_occasion((2023, 4, 24, 'G')) is None

    assert holiday_occasion((2023, 4, 2, 'G')) == 'Sizdah Be-dar'


def test_holiday_occasion_unknown_calendar():
    with raises(ValueError, match="unknown calendar='Z'"):
        # noinspection PyTypeChecker
        holiday_occasion((1402, 2, 3, 'Z'))


def test_holiday_occasion_from_jdate():
    # In reality, this was NOT a holiday in Iran (30st of Ramazan)
    assert holiday_occasion(jdate(1402, 2, 1)) == 'Eid al-Fitr'
    assert holiday_occasion(jdatetime(1402, 2, 2, 23, 59)) == 'Eid al-Fitr'
    # In reality, this WAS a holiday in Iran (2nd of Shawal)
    assert holiday_occasion(jdatetime(1402, 2, 3, 0)) is None
    assert holiday_occasion(jdate(1402, 2, 4)) is None
    assert holiday_occasion(jdatetime(1402, 1, 13)) == 'Sizdah Be-dar'


def test_holiday_occasion_gregorian():
    assert holiday_occasion(date(2023, 4, 21)) == 'Eid al-Fitr'
    assert holiday_occasion(datetime(2023, 4, 22)) == 'Eid al-Fitr'
    # In reality, this WAS a holiday in Iran (2nd of Shawal)
    assert holiday_occasion(date(2023, 4, 23)) is None
    assert holiday_occasion(datetime(2023, 4, 24, 10)) is None

    assert holiday_occasion(date(2023, 4, 2)) == 'Sizdah Be-dar'


def test_holiday_occasion_hijri():
    with raises(ValueError):
        # Hijri does not allow 30-day Ramadan in this year, but in Iran
        # Ramadan had 30 days.
        Hijri(1444, 9, 30)

    r29 = Hijri(1444, 9, 29)
    assert r29.weekday() == 3  # Thursday
    assert holiday_occasion(r29) is None
    assert holiday_occasion(Hijri(1444, 10, 1)) == 'Eid al-Fitr'
    assert holiday_occasion(Hijri(1444, 10, 2)) == 'Eid al-Fitr'
    assert holiday_occasion(Hijri(1444, 10, 3)) is None

    assert holiday_occasion(Hijri(1444, 9, 11)) == 'Sizdah Be-dar'


def test_holiday_occasion_lunar_calendar():
    assert holiday_occasion((1444, 9, 29, 'L')) is None
    assert holiday_occasion((1444, 10, 1, 'L')) == 'Eid al-Fitr'
    assert holiday_occasion((1444, 10, 2, 'L')) == 'Eid al-Fitr'
    assert holiday_occasion((1444, 10, 3, 'L')) is None

    assert holiday_occasion((1444, 9, 11, 'L')) == 'Sizdah Be-dar'


def test_set_weekend():
    date = (2024, 2, 5, 'G')  # a non-holiday Monday
    assert off_occasion(date) is None
    assert off_occasion(date, weekend=(0,)) == 'Weekend'
    set_default_weekend((0,))
    assert off_occasion(date) == 'Weekend'


def test_is_workday_lunar():
    assert (
        off_occasion_lunar(Hijri(1445, 9, 21), weekend=())
        == 'Martyrdom of Ali'
    )
