import datetime as dt
from pql.core.context import EvaluationContext
from pql.date.calendar import HolidayCalendar, BDC, DCM
from pql.instruments.rates.bonds import Bill, Bond, DebtInstrument
from pql.instruments.rates.enums import QuoteType, YieldCalcType
from pql.date.tenor import Tenor
from pql.refdata.rates.bonds import BillRefData, BondRefData, BondRefDataConfig

#https://www.treasurydirect.gov/instit/annceresult/press/preanre/2004/ofcalc6decbill.pdf


def test_bill():
    bill = Bill(
        "US",
        "USD",
        dt.date(2004, 1, 22),
        dt.date(2004, 2, 19),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "BMA",
        0.008,
        QuoteType.RATE,
        Tenor("0D"),
    )

    with EvaluationContext(market_date=dt.date(2004, 1, 22)) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        assert bill.SettlementDate() == dt.date(2004, 1, 22)
        assert list(bill.Schedule().iloc[0, :]) == [
            dt.date(2004, 1, 22),
            dt.date(2004, 2, 19),
            28,
            0.07777777777777778,
            dt.date(2004, 2, 19),
        ]
        assert bill.Price() == 0.9993777777777778
        assert bill.DiscountRate() == 0.008
        assert bill.Yield() == 0.00813839722493955
        assert list(bill.Flows().iloc[0, :]) == [
            dt.date(2004, 2, 19),
            0.07777777777777778,
            1.0,
        ]
        bill.set_quote(0.98001, QuoteType.PRICE)
        assert bill.DiscountRate() == 0.2570142857142851
        bill.set_quote(0.9993777777777778, QuoteType.PRICE)
        assert bill.DiscountRate() == 0.007999999999999594
        
def test_bill_yield():
    bill = Bill(
        "US",
        "USD",
        dt.date(1990, 6, 7),
        dt.date(1991, 6, 6),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "BMA",
        0.92265000,
        QuoteType.PRICE,
        Tenor("0D"),
    )
    with EvaluationContext(market_date=dt.date(1990, 6, 7)) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        assert bill.Yield() == 0.0823732441248205


def test_bond():
    bond = Bond(
        "US",
        "USD",
        dt.date(2023, 8, 15),
        dt.date(2023, 8, 15),
        dt.date(2053, 8, 15),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "BMA",
        0.9890121339706388,
        0.04125,
        QuoteType.CLEAN_PRICE,
        Tenor("1D"),
        Tenor("6M"),
        YieldCalcType.STREET,
    )

    with EvaluationContext(market_date=dt.date(2023, 8, 15)) as ctx:
        ctx.set_calendars({"BMA": HolidayCalendar()})
        assert bond.SettlementDate() == dt.date(2023, 8, 16)
        assert len(bond.Schedule()) == 60
        assert bond.AccruedInterests() == 0.00011458333333333334
        assert bond.DirtyPrice() == 0.9891267173039722
        assert bond.CleanPrice() == 0.9890121339706388
        assert bond.Yield() == 0.0418900000000002
        assert len(bond.Flows()) == 60
        bond.set_quote(0.05, QuoteType.RATE)
        assert bond.DirtyPrice() == 0.8647746278778761
        bond.set_quote(0.041890000000000, QuoteType.RATE)
        assert bond.DirtyPrice() == 0.9891267173039722
        
def test_bill_from_refdata():
    bill_refdata = BillRefData(
        "US",
        "USD",
        dt.date(2004, 1, 22),
        dt.date(2004, 2, 19),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "BMA",
        Tenor("0D"),
        "TEST",
        "ISIN"
    ) 
    refdata = BondRefDataConfig(
        bills_refdata={
            "TEST": bill_refdata
        }
    )   
    with EvaluationContext(market_date=dt.date(2023, 8, 15)) as ctx:
        ctx.set_bonds_refdata(refdata)
        inst = DebtInstrument.from_id("TEST", 0.008, QuoteType.RATE)
        assert isinstance(inst, Bill)

def test_bond_from_refdata():
    bond_refdata = BondRefData(
        "US",
        "USD",
        dt.date(2023, 8, 15),
        dt.date(2023, 8, 15),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "BMA",
        Tenor("1D"),
        "TEST",
        "ISIN",
        dt.date(2053, 8, 15),
        0.04125,
        Tenor("6M"),
        YieldCalcType.STREET,
    ) 
    refdata = BondRefDataConfig(
        bonds_refdata={
            "TEST": bond_refdata
        }
    )   
    with EvaluationContext(market_date=dt.date(2023, 8, 15)) as ctx:
        ctx.set_bonds_refdata(refdata)
        inst = DebtInstrument.from_id("TEST", 0.008, QuoteType.RATE)
        assert isinstance(inst, Bond)
