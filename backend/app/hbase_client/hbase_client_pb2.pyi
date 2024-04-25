from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TradeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BUY: _ClassVar[TradeType]
    SELL: _ClassVar[TradeType]

class TradeResultType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TRADE_EXECUTED_SUCCESFULLY: _ClassVar[TradeResultType]
    WRONG_TRADE_TYPE: _ClassVar[TradeResultType]
    NOT_ENOUGH: _ClassVar[TradeResultType]
    UNEXPECTED_SERVER_ERROR: _ClassVar[TradeResultType]
BUY: TradeType
SELL: TradeType
TRADE_EXECUTED_SUCCESFULLY: TradeResultType
WRONG_TRADE_TYPE: TradeResultType
NOT_ENOUGH: TradeResultType
UNEXPECTED_SERVER_ERROR: TradeResultType

class Trade(_message.Message):
    __slots__ = ("username", "type", "symbol", "quantity", "price_per_item", "time_offered", "time_executed")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_PER_ITEM_FIELD_NUMBER: _ClassVar[int]
    TIME_OFFERED_FIELD_NUMBER: _ClassVar[int]
    TIME_EXECUTED_FIELD_NUMBER: _ClassVar[int]
    username: str
    type: TradeType
    symbol: str
    quantity: int
    price_per_item: int
    time_offered: int
    time_executed: int
    def __init__(self, username: _Optional[str] = ..., type: _Optional[_Union[TradeType, str]] = ..., symbol: _Optional[str] = ..., quantity: _Optional[int] = ..., price_per_item: _Optional[int] = ..., time_offered: _Optional[int] = ..., time_executed: _Optional[int] = ...) -> None: ...

class TradeResult(_message.Message):
    __slots__ = ("result",)
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: TradeResultType
    def __init__(self, result: _Optional[_Union[TradeResultType, str]] = ...) -> None: ...
