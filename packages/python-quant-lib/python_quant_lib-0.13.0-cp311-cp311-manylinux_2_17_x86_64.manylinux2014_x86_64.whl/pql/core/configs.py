import python_quant_lib.core as pql_core


class CalibrationConfig(pql_core.CalibrationConfig):
    """Config for the various calibration parameters"""

    def __init__(self, max_iter: int = 1e6, x_tol: float = 1e-6):
        super().__init__(int(max_iter), x_tol)
