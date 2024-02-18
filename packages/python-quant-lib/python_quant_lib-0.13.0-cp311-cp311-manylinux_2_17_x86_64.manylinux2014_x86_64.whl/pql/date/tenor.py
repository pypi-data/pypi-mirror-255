import datetime as dt
import python_quant_lib.date as pql_date
from typing import Optional, Union
from pql.date.calendar import BDC, HolidayCalendar


class Tenor(pql_date.Tenor):
    """
    A Tenor Implementation.
    Tenor supported:
    - 1D
    - 1W
    - 1M
    - 1Y
    """

    def __init__(self, tenor: str) -> None:
        super().__init__(tenor)
        self.tenor = tenor

    def __repr__(self) -> str:
        return self.tenor


def add_tenor(
    date: dt.date,
    tenor: Tenor | str,
    cal: Optional[HolidayCalendar] = None,
    bdc: Optional[BDC] = None,
) -> dt.date:
    """
    Adds a tenor to a given date.
    Accounts for Holidays and BusinessDayConventions
    """
    if isinstance(tenor, str):
        tenor = Tenor(tenor)
    cal = cal or HolidayCalendar()
    bdc = bdc or BDC.NO_ADJ
    res = pql_date.add_tenor(date, tenor, cal, bdc)
    return res
