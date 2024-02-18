from __future__ import annotations
import datetime as dt
from typing import TypeVar
from typing import Tuple, Optional
import python_quant_lib.rates as pql_rates
from pql.date.calendar import DCM
from pql.core.context import EvaluationContext
from pql.core._utils import eval_request
from pql.instruments.rates.enums import DiscountingType, QuoteType
from pql.market.rates.enums import InterpolationType

CurveInstrument = TypeVar("CurveInstrument")

class NielsonSiegelSvenssonModel(pql_rates.NielsonSiegelSvenssonModel):
    """NSS Model for fitting YieldCurves"""

    def __init__(
        self,
        beta0: float = 0,
        beta1: float = 0,
        beta2: float = 0,
        beta3: float = 0,
        tau1: float = 1.0,
        tau2: float = 1.0,
    ):
        super().__init__(beta0, beta1, beta2, beta3, tau1, tau2)

    def spot_date(self, t: float) -> float:
        return self._spot_rate(t)


class NSSBondCurve(pql_rates.NSSBondCurve):
    """
    NSS Bond Curve Implementation
    """

    def __init__(
        self,
        curve_name: str,
        curve_date: dt.date,
        instruments: Tuple[CurveInstrument, ...],
        weights: Tuple[float] = None,
        discounting_type: Optional[DiscountingType] = None,
        model: Optional[NielsonSiegelSvenssonModel] = None,
    ):
        if not weights:
            weights = [1.0] * len(instruments)
        else:
            assert len(weights) == len(instruments), "All instruments must have a weight"
        model = model or NielsonSiegelSvenssonModel()
        discounting_type = discounting_type or DiscountingType.CONTINUOUS
        super().__init__(
            curve_name, curve_date, model, instruments, weights, discounting_type
        )

    def set_quotes(self, quotes: Tuple[Tuple[float, QuoteType]]):
        self._set_quotes(quotes)

    def get_model(self) -> NielsonSiegelSvenssonModel:
        return self._get_model()

    @eval_request
    def SpotRate(self, date: dt.date, dcm: DCM, ctx: Optional[EvaluationContext] = None) -> float:
        return self._get_spot_rate(ctx, date, dcm)
    
    @eval_request
    def DiscountFactor(self, date: dt.date, dcm: DCM, ctx: Optional[EvaluationContext] = None) -> float:
        return self._get_df(ctx, date, dcm)


class ZeroCurve(pql_rates.ZeroCurve):
    """
    Simple Zero Curve Bootstrapping 
    """
    
    def __init__(
        self,
        curve_name: str,
        curve_date: dt.date,
        instruments: Tuple[CurveInstrument, ...],
        discounting_type: Optional[DiscountingType] = None,
        interpolation_type: Optional[InterpolationType] = None,
        extrapolation_type: Optional[InterpolationType] = None
    ):
        discounting_type = discounting_type or DiscountingType.CONTINUOUS
        interpolation_type = interpolation_type or InterpolationType.LOGLINEAR
        extrapolation_type = extrapolation_type or InterpolationType.LOGLINEAR
        super().__init__(
            curve_name, curve_date, instruments, discounting_type, interpolation_type, extrapolation_type
        )

    def set_quotes(self, quotes: Tuple[Tuple[float, QuoteType]]):
        self._set_quotes(quotes)

    @eval_request
    def SpotRate(self, date: dt.date, dcm: DCM, ctx: Optional[EvaluationContext] = None) -> float:
        return self._get_spot_rate(ctx, date, dcm)
    
    @eval_request
    def DiscountFactor(self, date: dt.date, dcm: DCM, ctx: Optional[EvaluationContext] = None) -> float:
        return self._get_df(ctx, date, dcm)
    