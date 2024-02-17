from ._enum_base import EnumBase as EnumBase

class StatSigTest(EnumBase):
    FISHERS_OR_CHI_SQUARED: str
    FISHERS_EXACT: str
    CHI_SQUARED_TEST: str
    TWO_SAMPLE_T_TEST: str
    STACKED_REGRESSION: str
    BOOTSTRAPPING: str
