``iranholidays`` is a small python library that provides functions to check if a date is a holiday in Iran or not. 

**Warning:** For Islamic holidays, like Eid al-Fitr, the calculation may be off by a day or two since those events depend on seeing the moon by naked eye and cannot be predicted by computers.

Usage
-----

.. code-block:: python

    from iranholidays import holiday_occasion

    assert holiday_occasion((2024, 4, 1, 'G')) == 'Sizdah Be-dar'  # Gregorian
    assert holiday_occasion((1403, 1, 13, 'S')) == 'Sizdah Be-dar'  # Solar
    assert holiday_occasion((1403, 1, 14, 'S')) is False
    assert holiday_occasion((1445, 9, 21, 'L')) == 'Martyrdom of Ali'  # Lunar


In case you have a date object from the following libraries, you can check it directly using one of the ``off_occasion_*`` functions:

.. code-block:: python

    import datetime

    import hijri_converter
    import jdatetime

    from iranholidays import (
        off_occasion_gregorian,
        off_occasion_lunar,
        off_occasion_solar,
    )

    date = datetime.date(2024, 4, 1)
    assert off_occasion_gregorian(date, weekend=()) == 'Sizdah Be-dar'

    date = jdatetime.date(1403, 1, 13)
    assert off_occasion_solar(date, weekend=()) == 'Sizdah Be-dar'

    date = hijri_converter.Hijri(1445, 9, 21)
    assert off_occasion_lunar(date, weekend=()) == 'Martyrdom of Ali'

``off_occasion`` function checks if a date is a weekend or holiday and returns the occasion string or ``None``. The default value for weekend parameter is ``(4,)`` which means Friday. Either pass a different value to ``weekend`` parameter to override it or use ``set_default_weekend`` function to change this default for all functions:

.. code-block:: python

    from iranholidays import off_occasion, set_default_weekend
    date = (2024, 2, 5, 'G')  # a non-holiday Monday
    assert off_occasion(date) is None
    assert off_occasion(date, weekend=(0,)) == 'Weekend'
    set_default_weekend((0,))  # set default weekends to Thursday and Friday
    assert off_occasion(date) == 'Weekend'
