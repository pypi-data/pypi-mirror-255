from abc import abstractmethod
from typing import Any, Type, TypeVar
from abc import ABC

T = TypeVar("T")


class AbstractConverter(ABC):
    """
    Abstract class representing converter that is used to transform data from/to dictionary to/from Python classes
    """

    @abstractmethod
    def dump_to_dict(self, t: Any, remove_none: bool = False) -> dict[str, Any]:
        """
        Dumps class to dictionary

        Args:
            t: Object to convert
            remove_none: If True, after converting object to dictionary, all keys with None values will be removed

        Returns:
            Object converted to dictionary
        """
        pass

    @abstractmethod
    def load_from_dict(self, data: dict[str, Any] | list[dict[str, Any]], t: Type[T]) -> T:
        """
        Converts dictionary to object

        Args:
            data: Dict data
            t: Type to convert to

        Returns:
            Converted object
        """
        pass
