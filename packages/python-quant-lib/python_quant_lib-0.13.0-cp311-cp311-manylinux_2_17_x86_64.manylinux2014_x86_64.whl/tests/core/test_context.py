import datetime as dt
from pql.core.context import EvaluationContext, get_eval_ctx
from pql.date import Tenor, BDC, DCM
from pql.refdata.rates.bonds import BillRefData, BondRefData, BondRefDataConfig
from pql.instruments.rates.enums import YieldCalcType
import python_quant_lib.rates as pql_rates


def test_default_context():
    today = dt.date.today()
    ctx = get_eval_ctx()
    assert ctx.market_date == today


def test_custom_ctx():
    ctx_1 = EvaluationContext(market_date=dt.date(2023, 1, 1))
    ctx_2 = EvaluationContext(market_date=dt.date(2022, 1, 1))
    with ctx_1:
        ctx = get_eval_ctx()
        assert ctx.market_date == dt.date(2023, 1, 1)
    with ctx_2:
        ctx = get_eval_ctx()
        assert ctx.market_date == dt.date(2022, 1, 1)


def test_ctx_bonds_refdata():
    bond_refdata = BondRefData(
        "US",
        "USD",
        dt.date(2023, 1, 1),
        dt.date(2053, 1, 1),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "NYC",
        Tenor("1D"),
        "US000000001",
        "ISIN",
        dt.date(2023, 1, 1),
        0.045,
        Tenor("6M"),
        YieldCalcType.STREET,
    )

    bill_refdata = BillRefData(
        "US",
        "USD",
        dt.date(2023, 1, 1),
        dt.date(2053, 1, 1),
        BDC.MODIFIED_FOLLOWING,
        DCM.ACT_360,
        "NYC",
        Tenor("1D"),
        "US000000002",
        "ISIN",
    )

    refdata = BondRefDataConfig(
        {bill_refdata.id: bill_refdata}, {bond_refdata.id: bond_refdata}
    )
    ctx = get_eval_ctx()
    ctx.set_bonds_refdata(refdata)
    assert len(ctx.get_bonds_refdata(["US000000001", "US000000002"])) == 2
