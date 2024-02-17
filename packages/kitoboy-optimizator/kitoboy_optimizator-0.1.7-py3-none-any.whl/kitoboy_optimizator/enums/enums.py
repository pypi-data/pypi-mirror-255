from enum import Enum

class Exchangies(Enum):
    BINANCE_FUTURES = 'binance_futures'
    BYBIT_FUTURES = 'bybit_futures'


class Strategies(Enum):
    NUGGET_V1 = 'nugget_v1'
    NUGGET_V2 = 'nugget_v2'
    NUGGET_V3 = 'nugget_v3'
    NUGGET_V4 = 'nugget_v4'
    NUGGET_V5 = 'nugget_v5'