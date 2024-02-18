import datetime
from decimal import Decimal
from typing import Optional, List, Any, Type, TypeVar
import cattr

from lime_trader.converters.abstract_converter import AbstractConverter
from lime_trader.utils.date_utils import timestamp_to_datetime, datetime_to_timestamp, str_to_date, date_to_str

T = TypeVar("T")


class CAttrConverter(AbstractConverter):
    """
    Converter that utilizes cattr library to convert dataclasses from/to python objects
    """

    converter = cattr.Converter()
    dump_hidden_fields: Optional[List[str]] = None
    dump_specify_fields: Optional[List[str]] = None

    def __init__(self):
        # structure hook for load
        # unstructure hook for dump

        self.converter.register_structure_hook(Decimal, lambda val, _: Decimal(str(val)) if val is not None else None)
        self.converter.register_unstructure_hook(Decimal, lambda val: float(val) if val is not None else None)

        self.converter.register_structure_hook(datetime.datetime, lambda val, _: timestamp_to_datetime(
            int(val)) if val is not None else None)
        self.converter.register_unstructure_hook(datetime.datetime,
                                                 lambda val: datetime_to_timestamp(val) if val is not None else None)

        self.converter.register_structure_hook(datetime.date,
                                               lambda val, _: str_to_date(str(val)) if val is not None else None)
        self.converter.register_unstructure_hook(datetime.date,
                                                 lambda val: date_to_str(val) if val is not None else None)

    def dump_to_dict(self, t: Any, remove_none: bool = False) -> dict[str, Any]:
        if type(t) in (int, bool, str, float):
            return t
        d = self.converter.unstructure(t)
        if remove_none:
            return {k: v for k, v in d.items() if v is not None}
        return d

    def load_from_dict(self, data: dict[str, Any] | list[dict[str, Any]], t: Type[T]) -> T:
        return self.converter.structure(data, t)


converter = CAttrConverter()
