from abc import abstractmethod
from enum import Enum
from itertools import chain
from typing import (
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    TypeVar,
)
from uuid import UUID

_DEFAULT_PER_PAGE = 100
_DEFAULT_MIN_UUID = UUID("00000000-0000-0000-0000-000000000000")

T = TypeVar("T")


class PagerLogger:
    def on_page(self, page: int, count: int):
        pass

    def on_success(self, page: int, total: int):
        pass


class PagerOnIdLogger:
    def on_iteration(self, max_id: UUID, count: int):
        pass

    def on_success(self, total: int):
        pass


class PagerStopStrategy(Enum):
    """Strategy for stopping the pager"""

    EMPTY_PAGE = "EMPTY_PAGE"
    LESS_RESULTS_THAN_ASKED = "LESS_RESULTS_THAN_ASKED"


class AbstractPager(Generic[T]):
    def all(self, per_page: int = _DEFAULT_PER_PAGE) -> List[T]:
        """Returns all data provided by the callback as a list"""
        return list(chain.from_iterable(self.iterator(per_page=per_page)))

    @abstractmethod
    def iterator(self, per_page: int) -> Iterator[Sequence[T]]:
        pass


class Pager(AbstractPager):
    def __init__(
        self,
        callback: Callable[[int, int], Sequence[T]],
        *,
        logger: Optional[PagerLogger] = None,
        start_page: int = 1,
        stop_strategy: PagerStopStrategy = PagerStopStrategy.EMPTY_PAGE,
    ):
        self._callback = callback
        self._logger = logger or PagerLogger()
        self._start_page = start_page
        self._stop_strategy = stop_strategy

    def iterator(
        self,
        per_page: int = _DEFAULT_PER_PAGE,
    ) -> Iterator[Sequence[T]]:
        """Yields data provided by the callback as a list page by page"""
        page = self._start_page
        total_results = 0

        stop_on_empty_page = self._stop_strategy == PagerStopStrategy.EMPTY_PAGE

        while True:
            results = self._callback(page, per_page)
            nb_results = len(results)
            total_results += nb_results
            is_empty = nb_results == 0
            is_partial_page = nb_results < per_page
            should_stop = is_empty if stop_on_empty_page else is_partial_page

            self._logger.on_page(page, nb_results)
            if results:
                yield results

            if should_stop:
                break

            page += 1

        self._logger.on_success(page, total_results)


class PagerOnId(AbstractPager):
    def __init__(
        self,
        callback: Callable[[UUID, int], Sequence[T]],
        *,
        logger: Optional[PagerOnIdLogger] = None,
        stop_strategy: PagerStopStrategy = PagerStopStrategy.EMPTY_PAGE,
    ):
        self._callback = callback
        self._logger = logger or PagerOnIdLogger()
        self._stop_strategy = stop_strategy

    def iterator(
        self,
        per_page: int = _DEFAULT_PER_PAGE,
    ) -> Iterator[Sequence[T]]:
        """Yields data provided by the callback as a list using the greatest UUID as a reference point"""
        greater_than_id = _DEFAULT_MIN_UUID
        stop_on_empty_page = self._stop_strategy == PagerStopStrategy.EMPTY_PAGE

        total_results = 0

        while True:
            results = self._callback(greater_than_id, per_page)
            nb_results = len(results)
            total_results += nb_results
            is_empty = nb_results == 0
            is_partial_page = nb_results < per_page
            should_stop = is_empty if stop_on_empty_page else is_partial_page
            if results:
                greater_than_id = self._max_id(results)
                self._logger.on_iteration(greater_than_id, nb_results)
                yield results

            if should_stop:
                break
        self._logger.on_success(total_results)

    @staticmethod
    def _max_id(items: Sequence) -> UUID:
        return max(item["id"] for item in items)
