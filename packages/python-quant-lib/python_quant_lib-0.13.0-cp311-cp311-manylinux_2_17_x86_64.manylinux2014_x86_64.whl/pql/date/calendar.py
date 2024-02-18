import datetime as dt
import python_quant_lib.date as pql_date


class HolidayCalendar(pql_date.HolidayCalendar):
    """
    Implementation of a Holiday Calendar
    Contains information about weekend and Bank holidays
    """

    def __init__(self) -> None:
        super().__init__()


class BDC(pql_date.BDC):
    """
    BusinessDayConvention Enums
    """

    def __init__(self) -> None:
        super().__init__()


class DCM(pql_date.DCM):
    """
    DayCountMethod Enums
    """

    def __init__(self) -> None:
        super().__init__()


def year_frac(dt1: dt.date, dt2: dt.date, dcm: DCM) -> float:
    return pql_date.year_frac(dt1, dt2, dcm)
