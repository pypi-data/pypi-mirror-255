import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Generator, List, Optional, Sequence, Union

import sqlalchemy as sa

from dql.data_storage.abstract import SELECT_BATCH_SIZE
from dql.data_storage.schema import PARTITION_COLUMN_ID

if TYPE_CHECKING:
    from dql.dataset import DatasetRow


@dataclass
class DatasetRowsBatch:
    rows: Sequence["DatasetRow"]


BatchingResult = Union["DatasetRow", DatasetRowsBatch]


class BatchingStrategy(ABC):
    """BatchingStrategy provides means of batching UDF executions."""

    @abstractmethod
    def __call__(
        self,
        execute: Callable,
        query: sa.sql.selectable.Select,
    ) -> Generator[BatchingResult, None, None]:
        """Apply the provided parameters to the UDF."""


class NoBatching(BatchingStrategy):
    """
    NoBatching implements the default batching strategy, which is not to
    batch UDF calls.
    """

    def __call__(
        self,
        execute: Callable,
        query: sa.sql.selectable.Select,
    ) -> Generator["DatasetRow", None, None]:
        return execute(query, limit=query._limit)


class Batch(BatchingStrategy):
    """
    Batch implements UDF call batching, where each execution of a UDF
    is passed a sequence of multiple parameter sets.
    """

    def __init__(self, count: int):
        self.count = count

    def __call__(
        self,
        execute: Callable,
        query: sa.sql.selectable.Select,
    ) -> Generator[DatasetRowsBatch, None, None]:
        # choose page size that is a multiple of the batch size
        page_size = math.ceil(SELECT_BATCH_SIZE / self.count) * self.count

        # select rows in batches
        results: List["DatasetRow"] = []

        for row in execute(query, page_size=page_size, limit=query._limit):
            results.append(row)
            if len(results) >= self.count:
                batch, results = results[: self.count], results[self.count :]
                yield DatasetRowsBatch(batch)

        if len(results) > 0:
            yield DatasetRowsBatch(results)


class Partition(BatchingStrategy):
    """
    Partition implements UDF call batching, where each execution of a UDF
    is run on a list of dataset rows grouped by the specified column.
    Dataset rows need to be sorted by the grouping column.
    """

    def __call__(
        self,
        execute: Callable,
        query: sa.sql.selectable.Select,
    ) -> Generator[DatasetRowsBatch, None, None]:
        current_partition: Optional[int] = None
        batch: List["DatasetRow"] = []

        for row in execute(
            query, order_by=(PARTITION_COLUMN_ID, "id"), limit=query._limit
        ):
            partition = row[PARTITION_COLUMN_ID]
            if current_partition != partition:
                current_partition = partition
                if len(batch) > 0:
                    yield DatasetRowsBatch(batch)
                    batch = []
            batch.append(row)

        if len(batch) > 0:
            yield DatasetRowsBatch(batch)
