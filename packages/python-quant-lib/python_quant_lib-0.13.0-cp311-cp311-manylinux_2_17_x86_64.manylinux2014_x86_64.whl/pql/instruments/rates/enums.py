import python_quant_lib.rates as pql_rates


class QuoteType(pql_rates.QuoteType):
    """Rates Instruments Quote Types"""

    def __init__(self) -> None:
        super().__init__()


class YieldCalcType(pql_rates.YieldCalcType):
    """Yield Computation Conventions"""

    def __init__(self) -> None:
        super().__init__()


class DiscountingType(pql_rates.DiscountingType):
    """Discounting Types"""

    def __init__(self) -> None:
        super().__init__()
