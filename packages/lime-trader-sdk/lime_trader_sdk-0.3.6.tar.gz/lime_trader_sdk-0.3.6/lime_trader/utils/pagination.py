from typing import Callable, Iterator, AsyncIterator

from lime_trader.models.page import Page, PageRequest


def iterate_pages(start_page: PageRequest, func: Callable) -> Iterator[Page]:
    """
    Creates iterator from callable and page. It assumes callable will have only one parameter, page

    Args:
        start_page: Start page
        func: Function that will be called with page parameter

    Returns:
        Iterator of pages
    """
    has_next_page = True
    current_page = PageRequest(page=start_page.page, size=start_page.size)
    while has_next_page:
        response = func(page=current_page)
        yield response
        has_next_page = response.has_next()
        if has_next_page:
            current_page.page += 1


async def iterate_pages_async(start_page: PageRequest, func: Callable) -> AsyncIterator[Page]:
    """
    Creates iterator from callable and page. It assumes callable will have only one parameter, page

    Args:
        start_page: Start page
        func: Function that will be called with page parameter

    Returns:
        Iterator of pages
    """
    has_next_page = True
    current_page = PageRequest(page=start_page.page, size=start_page.size)
    while has_next_page:
        response = await func(page=current_page)
        yield response
        has_next_page = response.has_next()
        if has_next_page:
            current_page.page += 1
