from typing import Callable, Dict, List
from uuid import UUID

from .pager import Pager, PagerLogger, PagerOnId


def _make_callback(elements: List[int]) -> Callable[[int, int], List[int]]:
    def _callback(page: int, per: int) -> List[int]:
        _start = (page - 1) * per
        _end = _start + per
        return elements[_start:_end]

    return _callback


ITEMS = list(range(10))


def test_Pager__all():
    """unit test for Pager#all()"""
    pager = Pager(_make_callback(ITEMS))
    # When no argument provided
    assert pager.all() == ITEMS
    # When per page is less than the number of ITEMS
    assert pager.all(per_page=1) == ITEMS
    # When per page is more than the number of ITEMS
    assert pager.all(per_page=1000) == ITEMS


def test_Pager__iterator__pagination():
    """unit test for Pager#iterator() (pagination)"""
    pager = Pager(_make_callback(ITEMS))

    def nb_of_pages(per_page: int) -> int:
        return len([page for page in pager.iterator(per_page=per_page)])

    assert nb_of_pages(per_page=50) == 1
    assert nb_of_pages(per_page=1) == 10
    assert nb_of_pages(per_page=2) == 5
    assert nb_of_pages(per_page=4) == 3


def test_Pager__iterator__logging():
    """unit test for Pager#iterator() (pagination)"""

    class Logger(PagerLogger):
        def __init__(self):
            self.pages = []
            self.total = 0

        def on_page(self, page: int, count: int):
            self.pages.append((page, count))

        def on_success(self, page: int, total: int):
            self.total = total

    logger = Logger()
    pager = Pager(_make_callback(ITEMS), logger=logger)

    pager.all(per_page=6)

    assert logger.pages == [(1, 6), (2, 4), (3, 0)]
    assert logger.total == 10


ITEMS_WITH_IDS = [
    {"id": "00000000-0000-0000-0000-00000000000" + str(i)} for i in range(1, 10)
]


def _make_callback_with_ids(
    elements: List[Dict[str, str]],
) -> Callable[[UUID, int], List[Dict[str, str]]]:
    def _callback(max_id: UUID, per: int) -> List[Dict[str, str]]:
        """assumes the elements are sorted by id"""
        to_return: List[Dict[str, str]] = []
        for element in elements:
            if element["id"] > str(max_id):
                to_return.append(element)
            if len(to_return) >= per:
                return to_return
        return to_return

    return _callback


def test_pageronid__all():
    """unit test for PagerOnId#all()"""
    pager = PagerOnId(_make_callback_with_ids(ITEMS_WITH_IDS))
    # When no argument provided
    assert pager.all() == ITEMS_WITH_IDS
    # When per page is less than the number of ITEMS
    assert pager.all(per_page=1) == ITEMS_WITH_IDS
    # When per page is more than the number of ITEMS
    assert pager.all(per_page=1000) == ITEMS_WITH_IDS


def test_pageronid__iterator__pagination():
    """unit test for PagerOnId#iterator() (pagination)"""
    pager = PagerOnId(_make_callback_with_ids(ITEMS_WITH_IDS))

    def nb_of_pages(per_page: int) -> int:
        return len([page for page in pager.iterator(per_page=per_page)])

    assert nb_of_pages(per_page=50) == 1
    assert nb_of_pages(per_page=1) == len(ITEMS_WITH_IDS)
    assert nb_of_pages(per_page=2) == 5
    assert nb_of_pages(per_page=4) == 3
