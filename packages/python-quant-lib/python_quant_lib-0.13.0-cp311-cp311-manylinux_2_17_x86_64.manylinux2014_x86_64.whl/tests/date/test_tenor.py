import pytest
import datetime as dt
from pql.date.tenor import Tenor, add_tenor
from pql.date.calendar import HolidayCalendar, BDC

_REF_DATE = dt.datetime(2023, 6, 20)

_TENOR_TEST_CASES = [
    (_REF_DATE, Tenor("1D"), None, None, dt.date(2023, 6, 21)),
    (_REF_DATE, Tenor("1w"), None, None, dt.date(2023, 6, 27)),
    (_REF_DATE, Tenor("2M"), None, None, dt.date(2023, 8, 20)),
    (_REF_DATE, Tenor("10Y"), None, None, dt.date(2033, 6, 20)),
    (_REF_DATE, Tenor("-3M"), None, None, dt.date(2023, 3, 20)),
    (_REF_DATE, "10y", None, None, dt.date(2033, 6, 20)),
    (_REF_DATE, "-3m", None, None, dt.date(2023, 3, 20)),
]


@pytest.mark.parametrize("date,tenor,cal,bdc,expected_date", _TENOR_TEST_CASES)
def test_add_tenor(date, tenor, cal, bdc, expected_date):
    assert add_tenor(date, tenor, cal, bdc) == expected_date
