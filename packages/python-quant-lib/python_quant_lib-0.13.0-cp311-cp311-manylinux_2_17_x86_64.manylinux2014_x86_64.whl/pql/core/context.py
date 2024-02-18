from __future__ import annotations
import logging
import datetime as dt
from typing import Optional, List, Dict, Tuple, Union
from pql.date.calendar import HolidayCalendar
import python_quant_lib.core as pql_core
from pql.core.configs import CalibrationConfig
from pql.refdata.rates.bonds import BillRefData, BondRefData, BondRefDataConfig

LOGGER = logging.getLogger(__name__)


class _GlobalState:
    eval_ctx = None


class EvaluationContext(pql_core.EvaluationContext):
    """
    Local Evaluation Context where we cache refdata and market data
    """

    def __init__(
        self,
        market_date: Optional[dt.date] = None,
        calendars: Optional[Dict[str, HolidayCalendar]] = None,
        calib_cfg: Optional[CalibrationConfig] = None,
        bonds_refdata: Optional[BondRefDataConfig] = None,
    ):
        market_date = market_date or dt.date.today()
        calendars = calendars or {}
        calib_cfg = calib_cfg or CalibrationConfig()
        bonds_refdata = bonds_refdata or BondRefDataConfig()        
        super().__init__(market_date, calendars, calib_cfg, bonds_refdata)

    def __enter__(self):
        _GlobalState.eval_ctx = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _GlobalState.eval_ctx = None

    def set_calendars(
        self,
        cals: Dict[str, HolidayCalendar],
        override: bool = False,
    ):
        all_cals = {**self.calendars, **cals} if not override else cals
        self._set_calendars(all_cals)

    def set_bonds_refdata(self, bonds_refdata: BondRefDataConfig):
        self._set_bonds_refdata(bonds_refdata)

    def set_calibration_config(self, calibration_config: CalibrationConfig):
        self._set_calibration_config(calibration_config)

    def get_bonds_refdata(
        self, keys: Tuple[str, ...]
    ) -> Dict[str, Union[BillRefData, BondRefData]]:
        res = {}
        for key in keys:
            if key in self.bonds_refdata.bonds_refdata:
                res[key] = self.bonds_refdata.bonds_refdata
            elif key in self.bonds_refdata.bills_refdata:
                res[key] = self.bonds_refdata.bills_refdata
            else:
                LOGGER.warning(f"Could not find refdata for ID: {key}")
        return res


_DEFAULT_EVAL_CTX = EvaluationContext()


def get_eval_ctx() -> EvaluationContext:
    return _GlobalState.eval_ctx or _DEFAULT_EVAL_CTX


def refresh_default_ctx():
    _DEFAULT_EVAL_CTX = EvaluationContext()
