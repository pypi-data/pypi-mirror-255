import datetime as dt
from typing import TypeVar
import python_quant_lib.rates as pql_rates
from typing import Optional
from pql.core.context import EvaluationContext
from pql.core._utils import eval_request
from pql.date.calendar import DCM

YieldCurveType = TypeVar("YieldCurveType")

class RiskYieldCurveSet(pql_rates.RiskYieldCurveSet):
    """
    A Risk Yield Curve Construct to build and store shifted curves
    given a base curve
    """
    
    def __init__(self, base_curve: YieldCurveType):
        super().__init__(base_curve)
        
    
    @eval_request
    def SpotRate(self, shock:float, date: dt.date, dcm: DCM, ctx: Optional[EvaluationContext] = None) -> float:
        curve = self._get_parallel_curve(shock, ctx)
        return curve._get_spot_rate(ctx, date, dcm)
    
    @eval_request
    def DiscountFactor(self, shock:float, date: dt.date, dcm: DCM, ctx: Optional[EvaluationContext] = None) -> float:
        curve = self._get_parallel_curve(shock, ctx)
        return curve._get_df(ctx, date, dcm)
        
    