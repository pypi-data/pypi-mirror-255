import pandas as pd
import datetime as dt
from typing import Tuple, Optional, Union
import python_quant_lib.rates as pql_rates
from pql.date.calendar import BDC, DCM
from pql.instruments.rates.enums import QuoteType, YieldCalcType
from pql.core.context import EvaluationContext
from pql.core._utils import eval_request
from pql.date.tenor import Tenor
from pql.core._utils import get_eval_ctx
from pql.market.rates.risk_curves import RiskYieldCurveSet


def _schedule_table(
    schedule: Tuple[Tuple[dt.date, dt.date, int, float, dt.date], ...]
) -> pd.DataFrame:
    """
    Creates DataFrame for the Bond and Bill Schedules
    """
    return pd.DataFrame(
        schedule,
        columns=["Accrual Start", "Accrual End", "N Days", "Year Frac", "PayDate"],
    )


def _flows_table(flows: Tuple[Tuple[dt.date, float, float], ...]) -> pd.DataFrame:
    """
    Creates DataFrame for the Bond and Bill Flows
    """
    return pd.DataFrame(
        flows,
        columns=["PayDate", "Year Frac", "CashFlow"],
    )


class Bill(pql_rates.Bill):
    def __init__(
        self,
        issuer: str,
        ccy: str,
        issue_date: dt.date,
        maturity_date: dt.date,
        bdc: BDC,
        dcm: DCM,
        cal: str,
        quote: float,
        quote_type: QuoteType,
        settlement_lag: Tenor,
        notional: float = 1.0,
    ):
        super().__init__(
            issuer,
            ccy,
            issue_date,
            maturity_date,
            bdc,
            dcm,
            cal,
            quote,
            quote_type,
            notional,
            settlement_lag,
        )

    @eval_request
    def Schedule(self, ctx: Optional[EvaluationContext] = None) -> pd.DataFrame:
        schedule = self._schedule(ctx)
        return _schedule_table(schedule)

    @eval_request
    def Flows(self, ctx: Optional[EvaluationContext] = None) -> pd.DataFrame:
        schedule = self._flows(ctx)
        return _flows_table(schedule)

    @eval_request
    def SettlementDate(self, ctx: Optional[EvaluationContext] = None) -> dt.date:
        return self._get_settlement_date(ctx)

    @eval_request
    def Price(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._price(ctx)

    @eval_request
    def DiscountRate(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._discount_rate(ctx)
    
    @eval_request
    def Yield(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._yield(ctx)
    
    @eval_request
    def ZSpread(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        curve = curve._get_parallel_curve(0, ctx)
        return self._z_spread(ctx, curve)
    
    @eval_request
    def Duration(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._duration(curve, ctx)
    
    @eval_request
    def Convexity(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._convexity(curve, ctx)
    
    @eval_request
    def DV01(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._dv01(curve, ctx)
    
    @eval_request
    def EffectiveConvexity(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._effective_convexity(curve, ctx)

    def set_quote(self, quote: float, quote_type: QuoteType):
        self._set_quote(quote, quote_type)


class Bond(pql_rates.Bond):
    def __init__(
        self,
        issuer: str,
        ccy: str,
        issue_date: dt.date,
        dated_date: dt.date,
        maturity_date: dt.date,
        bdc: BDC,
        dcm: DCM,
        cal: str,
        quote: float,
        coupon_rate: float,
        quote_type: QuoteType,
        settlement_lag: Tenor,
        pay_freq: Tenor,
        yield_type: YieldCalcType,
        notional: float = 1.0,
    ):
        super().__init__(
            issuer,
            ccy,
            issue_date,
            dated_date,
            maturity_date,
            bdc,
            dcm,
            cal,
            quote,
            coupon_rate,
            quote_type,
            notional,
            settlement_lag,
            pay_freq,
            yield_type,
        )

    @eval_request
    def Schedule(self, ctx: Optional[EvaluationContext] = None) -> pd.DataFrame:
        schedule = self._schedule(ctx)
        return _schedule_table(schedule)

    @eval_request
    def Flows(self, ctx: Optional[EvaluationContext] = None) -> pd.DataFrame:
        schedule = self._flows(ctx)
        return _flows_table(schedule)

    @eval_request
    def SettlementDate(self, ctx: Optional[EvaluationContext] = None) -> dt.date:
        return self._get_settlement_date(ctx)

    @eval_request
    def AccruedInterests(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._accrued_interests(ctx)

    @eval_request
    def DirtyPrice(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._dirty_price(ctx)

    @eval_request
    def CleanPrice(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._clean_price(ctx)

    @eval_request
    def Yield(self, ctx: Optional[EvaluationContext] = None) -> float:
        return self._yield(ctx)
    
    @eval_request
    def ZSpread(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        curve = curve._get_parallel_curve(0, ctx)
        return self._z_spread(ctx, curve)
    
    @eval_request
    def Duration(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._duration(curve, ctx)
    
    @eval_request
    def Convexity(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._convexity(curve, ctx)
    
    @eval_request
    def DV01(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._dv01(curve, ctx)
    
    @eval_request
    def EffectiveConvexity(self, curve: RiskYieldCurveSet, ctx: Optional[EvaluationContext] = None) -> float:
        return self._effective_convexity(curve, ctx)

    def set_quote(self, quote: float, quote_type: QuoteType):
        self._set_quote(quote, quote_type)


class DebtInstrument:
    
    @classmethod
    def from_id(cls, instrument_id:str, quote: float, quote_type: QuoteType, notional: float = 1, ctx: Optional[EvaluationContext] = None) -> Union[Bill, Bond]:
        ctx = ctx or get_eval_ctx()
        if instrument_id in ctx.bonds_refdata.bills_refdata:
            refdata = ctx.bonds_refdata.bills_refdata[instrument_id]
            return Bill(
                issuer=refdata.issuer,
                ccy=refdata.ccy,
                issue_date=refdata.issue_date,
                maturity_date=refdata.maturity_date,
                bdc=refdata.bdc,
                dcm=refdata.dcm,
                cal=refdata.calendar,
                settlement_lag=refdata.settlement_lag,
                quote=quote,
                quote_type=quote_type,
                notional=notional
            )
        elif instrument_id in ctx.bonds_refdata.bonds_refdata:
            refdata = ctx.bonds_refdata.bonds_refdata[instrument_id]
            return Bond(
                issuer=refdata.issuer,
                ccy=refdata.ccy,
                issue_date=refdata.issue_date,
                dated_date=refdata.dated_date,
                maturity_date=refdata.maturity_date,
                bdc=refdata.bdc,
                dcm=refdata.dcm,
                cal=refdata.calendar,
                coupon_rate=refdata.coupon_rate,
                settlement_lag=refdata.settlement_lag,
                yield_type=refdata.yield_type,
                pay_freq=refdata.pay_freq,
                quote=quote,
                quote_type=quote_type,
                notional=notional
            )
        else:
            raise ValueError(f"Could not find RefData for ID: {instrument_id}")