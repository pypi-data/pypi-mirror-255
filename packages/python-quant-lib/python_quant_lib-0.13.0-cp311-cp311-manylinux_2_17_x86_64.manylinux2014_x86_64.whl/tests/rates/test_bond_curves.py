import pytest
import datetime as dt
import numpy as np
from typing import Sequence
from pql.core.context import EvaluationContext
from pql.instruments.rates.bonds import (
    Bill,
    Bond,
)
from pql.market.rates.risk_curves import RiskYieldCurveSet
from pql.instruments.rates.enums import QuoteType, YieldCalcType
from pql.market.rates.yield_curves import NielsonSiegelSvenssonModel, NSSBondCurve, ZeroCurve
from pql.date import BDC, DCM, Tenor, HolidayCalendar


def assert_monotonic(data: Sequence[float]):
    assert np.all(np.diff(np.array(data)) < 0)
    
@pytest.fixture
def ref_date():
    return dt.date(2023, 10, 2)


@pytest.fixture
def nss_bond_curve(ref_date):
    model = NielsonSiegelSvenssonModel(0, 0, 0, 0, 1, 1)

    bills = [
        Bill(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 10, 3),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.055,
            QuoteType.RATE,
            Tenor("0D"),
        ),
        Bill(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 10, 9),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.06,
            QuoteType.RATE,
            Tenor("0D"),
        ),
        Bill(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 10, 16),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.059,
            QuoteType.RATE,
            Tenor("0D"),
        ),
        Bill(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 10, 23),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.055,
            QuoteType.RATE,
            Tenor("0D"),
        ),
    ]

    bonds = [
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2025, 9, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.051,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2026, 9, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.047,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2029, 9, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.049,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
    ]

    curve = NSSBondCurve(
        "TEST", ref_date, instruments=bills + bonds, model=model
    )
    return curve, bills, bonds, ref_date

@pytest.fixture
def zero_curve(ref_date):
    bills = [
        Bill(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2024, 3, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.055,
            QuoteType.RATE,
            Tenor("0D"),
        ),
        Bill(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2024, 9, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.06,
            QuoteType.RATE,
            Tenor("0D"),
        ),
    ]

    bonds = [
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2025, 3, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.051,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2025, 9, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.047,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2026, 3, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.049,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2028, 3, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.045,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2030, 3, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.04,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
        Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2040, 3, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.035,
            0.04125,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        ),
    ]

    curve = ZeroCurve(
        "TEST", ref_date, instruments=bills + bonds
    )
    return curve, bills, bonds, ref_date
    

def test_nss_bond_curve(nss_bond_curve):
    curve, bills, bonds, ref_date = nss_bond_curve    
    with EvaluationContext(market_date=ref_date) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        for inst in bills + bonds:
            r = curve.SpotRate(date=inst.maturity_date, dcm=DCM.ACT_365)
            # print(f"Quote: {inst.quote} - Fitted: {r}")
        model = curve.get_model()
        assert model.beta0 == 2.784357269099789
        assert model.beta1 == -2.7277105021107495
        assert model.beta2 == -6.6159219655809824
        assert model.beta3 == 2.604820622990798
        assert model.tau1 == 8.823894280635821
        assert model.tau2 == 5.9305374219850995

        quotes = [
            (0.07, QuoteType.RATE),
            (0.075, QuoteType.RATE),
            (0.08, QuoteType.RATE),
            (0.075, QuoteType.RATE),
            (0.067, QuoteType.RATE),
            (0.054, QuoteType.RATE),
            (0.035, QuoteType.RATE),
        ]
        curve.set_quotes(quotes)

        for inst in bills + bonds:
            r = curve.SpotRate(date=inst.maturity_date, dcm=DCM.ACT_365)
            # print(f"Quote: {inst.quote} - Fitted: {r}")
        model = curve.get_model()
        assert model.beta0 == 5.631660855792108
        assert model.beta1 == -5.555332551632258
        assert model.beta2 == 4.488200226592651
        assert model.beta3 == -15.337632343191471
        assert model.tau1 == 5.624089785195212
        assert model.tau2 == 8.642453129908931
        
def test_zero_bond_curve(zero_curve):
    curve, bills, bonds, ref_date = zero_curve
    with EvaluationContext(market_date=ref_date) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        dfs = []
        for inst in bills + bonds:
            df = curve.DiscountFactor(date=inst.maturity_date, dcm=DCM.ACT_365)
            dfs.append(df)
        assert_monotonic(dfs)

        quotes = [
            (0.07, QuoteType.RATE),
            (0.075, QuoteType.RATE),
            (0.08, QuoteType.RATE),
            (0.075, QuoteType.RATE),
            (0.067, QuoteType.RATE),
            (0.060, QuoteType.RATE),
            (0.057, QuoteType.RATE),
            (0.05, QuoteType.RATE),
        ]
        curve.set_quotes(quotes)
        dfs = []
        for inst in bills + bonds:
            df = curve.DiscountFactor(date=inst.maturity_date, dcm=DCM.ACT_365)
            dfs.append(df)
        assert_monotonic(dfs)
        
        
def test_bond_zspread(zero_curve):
    curve, bills, bonds, ref_date = zero_curve
    zero_curve_set = RiskYieldCurveSet(base_curve=curve)
    with EvaluationContext(market_date=ref_date) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        z_spread = bonds[0].ZSpread(zero_curve_set)
        np.testing.assert_almost_equal(z_spread, 0, decimal=6)
        new_bond = Bond(
            "US",
            "USD",
            dt.date(2023, 9, 25),
            dt.date(2023, 9, 25),
            dt.date(2030, 9, 25),
            BDC.MODIFIED_FOLLOWING,
            DCM.ACT_360,
            "BMA",
            0.04,
            0.0625,
            QuoteType.RATE,
            Tenor("1D"),
            Tenor("6M"),
            YieldCalcType.STREET,
        )
        new_z_spread = new_bond.ZSpread(zero_curve_set)
        np.testing.assert_almost_equal(new_z_spread, -0.00177452910049649, decimal=9)
        
def test_bond_duration_convexity(zero_curve, nss_bond_curve):
    z_curve, bills, bonds, ref_date = zero_curve
    z_curve_set = RiskYieldCurveSet(z_curve)
    nss_curve, bills, bonds, ref_date = nss_bond_curve
    nss_curve_set = RiskYieldCurveSet(nss_curve)
    with EvaluationContext(market_date=ref_date) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        duration = bonds[0].Duration(z_curve_set)
        convexity = bonds[0].Convexity(z_curve_set)
        np.testing.assert_almost_equal(duration, 1.894918204220758, decimal=9)
        np.testing.assert_almost_equal(convexity, 2.2755718731299948, decimal=9)
        duration = bonds[0].Duration(nss_curve_set)
        convexity = bonds[0].Convexity(nss_curve_set)
        np.testing.assert_almost_equal(duration, 1.8793479456784141, decimal=9)
        np.testing.assert_almost_equal(convexity, 3.6535628417010475, decimal=9)
        dv01 = bonds[0].DV01(nss_curve_set)
        effective_convexity = bonds[0].EffectiveConvexity(nss_curve_set)
        np.testing.assert_almost_equal(dv01, 0.00018447493218526345, decimal=9)
        np.testing.assert_almost_equal(effective_convexity, 3.586301083879916e-08, decimal=9)

