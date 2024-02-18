import datetime as dt
import numpy as np
from pql.date.calendar import year_frac, DCM


def test_year_frac():
    dt1, dt2 = dt.date(2023, 1, 1), dt.date(2023, 6, 1)
    yf1 = year_frac(dt1, dt2, DCM.ACT_360)
    np.testing.assert_almost_equal(yf1, 0.4194444, decimal=5)
    yf2 = year_frac(dt1, dt2, DCM.ACT_365)
    np.testing.assert_almost_equal(yf2, 0.413698, 5)
