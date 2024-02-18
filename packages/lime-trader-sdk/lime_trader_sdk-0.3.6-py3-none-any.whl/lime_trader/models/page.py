from dataclasses import dataclass
import math
from typing import TypeVar, Generic

# Generic page type
T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    """
    Represents one page of items

    Attributes:
        data: Items in a page.
        number: Page number
        size: Page size
        total_elements: Number of existing elements. It does not represent number of elements in a page but
                        number of elements in total
    """

    data: list[T]
    number: int
    size: int

    total_elements: int

    def get_total_pages(self) -> int:
        """
        Get number of total pages based on total elements and page size

        Returns:
            Number of existing pages
        """
        if self.size == 0:
            return 1
        return int(math.ceil(self.total_elements / self.size))

    def has_next(self) -> bool:
        """
        Checks if there is a page after current one

        Returns:
            True if next page exists, False otherwise
        """
        return self.number < self.get_total_pages()

    def has_previous(self) -> bool:
        """
        Checks if there is a page before current one. Will be False just for the first page

        Returns:
            True if previous page exists, False otherwise
        """
        return 1 < self.number <= self.get_total_pages()

    def next_page_number(self) -> int:
        """
        Gets next page number

        Returns:
            Next page number
        """
        return self.number + 1

    def previous_page_number(self) -> int:
        """
        Gets previous page number

        Returns:
            Previous page number
        """
        return self.number - 1

    def is_last(self) -> bool:
        """
        Checks if current page is the last one

        Returns:
            True if current page is the last one, False otherwise
        """
        return not self.has_next()


@dataclass
class PageRequest:
    """Page specification

    Attributes:
        page: Page number
        size: Page size
    """

    page: int = 1
    size: int = 20

    def get_offset(self) -> int:
        """
        Gets items offset for current page

        Returns:
            Integer representing offset
        """
        return self.size * (self.page - 1)
