from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

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

class Tick(_message.Message):
    __slots__ = ("timestamp", "value")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    value: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ...) -> None: ...

class InstrumentPricesRequest(_message.Message):
    __slots__ = ("symbol", "start_date", "end_date", "time_delta")
    SYMBOL_FIELD_NUMBER: _ClassVar[int]
    START_DATE_FIELD_NUMBER: _ClassVar[int]
    END_DATE_FIELD_NUMBER: _ClassVar[int]
    TIME_DELTA_FIELD_NUMBER: _ClassVar[int]
    symbol: str
    start_date: _timestamp_pb2.Timestamp
    end_date: _timestamp_pb2.Timestamp
    time_delta: _duration_pb2.Duration
    def __init__(self, symbol: _Optional[str] = ..., start_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_date: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., time_delta: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class InstrumentPricesResponse(_message.Message):
    __slots__ = ("ticks",)
    TICKS_FIELD_NUMBER: _ClassVar[int]
    ticks: _containers.RepeatedCompositeFieldContainer[Tick]
    def __init__(self, ticks: _Optional[_Iterable[_Union[Tick, _Mapping]]] = ...) -> None: ...
