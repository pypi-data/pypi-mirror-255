import datetime as dt
from typing import Dict
import python_quant_lib.rates as pql_rates
from pql.date.calendar import BDC, DCM
from pql.date.tenor import Tenor
from pql.instruments.rates.enums import YieldCalcType


class BondRefData(pql_rates.BondRefData):
    def __init__(
        self,
        issuer: str,
        ccy: str,
        issue_date: dt.date,
        maturity_date: dt.date,
        bdc: BDC,
        dcm: DCM,
        calendar: str,
        settlement_lag: Tenor,
        id: str,
        id_type: str,
        dated_date: dt.date,
        coupon_rate: float,
        pay_freq: Tenor,
        yield_type: YieldCalcType,
    ):
        super().__init__(
            issuer,
            ccy,
            issue_date,
            maturity_date,
            bdc,
            dcm,
            calendar,
            settlement_lag,
            id,
            id_type,
            dated_date,
            coupon_rate,
            pay_freq,
            yield_type,
        )


class BillRefData(pql_rates.BillRefData):
    def __init__(
        self,
        issuer: str,
        ccy: str,
        issue_date: dt.date,
        maturity_date: dt.date,
        bdc: BDC,
        dcm: DCM,
        calendar: str,
        settlement_lag: Tenor,
        id: str,
        id_type: str,
    ):
        super().__init__(
            issuer,
            ccy,
            issue_date,
            maturity_date,
            bdc,
            dcm,
            calendar,
            settlement_lag,
            id,
            id_type,
        )


class BondRefDataConfig(pql_rates.BondRefDataConfig):
    def __init__(
        self,
        bills_refdata: Dict[str, BillRefData] = {},
        bonds_refdata: Dict[str, BondRefData] = {},
    ):
        super().__init__(bills_refdata, bonds_refdata)
