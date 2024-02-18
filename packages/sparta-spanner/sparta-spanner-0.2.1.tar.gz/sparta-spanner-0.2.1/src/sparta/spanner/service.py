import _queue
import logging
from typing import TypeVar, Callable

from google.api_core import exceptions
from google.cloud import spanner
from google.cloud.spanner_v1.snapshot import Snapshot
from google.cloud.spanner_v1.transaction import Transaction

from sparta.spanner.concurrency import run_as_non_blocking

_T = TypeVar("_T")


class DBService:
    def __init__(
        self,
        instance_id: str,
        database_id: str,
        pool_size: int = None,
        session_request_timeout: int = None,
        spanner_client: spanner.Client = None,
        project_id: str = None,
    ):
        """
        :param project_id: (optional) Google Cloud project ID, if provided will be validated.
        :param instance_id: Spanner instance ID
        :param database_id: Spanner database ID
        :param pool_size: (optional) size param for spanner.FixedSizePool
        :param session_request_timeout: (optional) default_timeout param for spanner.FixedSizePool
        :param spanner_client: (optional) a spanner.Client instance
        """
        if not instance_id:
            raise ValueError("Missing instance_id")
        if not database_id:
            raise ValueError("Missing database_id")

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        _pool = None
        if pool_size:
            _pool = spanner.FixedSizePool(
                size=pool_size, default_timeout=session_request_timeout
            )

        self.spanner_client = spanner_client or spanner.Client()
        if project_id and project_id != self.spanner_client.project:
            raise ValueError(
                f"Invalid project_id: received {project_id} but expected  {self.spanner_client.project}"
            )

        self.instance = self.spanner_client.instance(instance_id)
        self.database = self.instance.database(database_id, pool=_pool)

        self.logger.debug(f"Created {type(self).__name__} for {self.database.name}")

    def ping(self):
        self.execute_sql("SELECT 1")

    def execute_sql(self, *arg, **kwarg):
        with self.database.snapshot() as s:
            return s.execute_sql(*arg, **kwarg)

    async def run_in_snapshot(
        self,
        snapshot_consumer: Callable[[Snapshot], _T],
        *args,
        **kwargs,
    ) -> _T:
        def task():
            try:
                with self.database.snapshot(*args, **kwargs) as snapshot:
                    return snapshot_consumer(snapshot)
            except _queue.Empty as error:
                raise NoSessionAvailableException() from error  # exception chaining

        return await run_as_non_blocking(task)

    async def run_in_transaction(
        self,
        transaction_consumer: Callable[[Transaction], _T],
        *args,
        **kwargs,
    ) -> _T:
        def task():
            try:
                return self.database.run_in_transaction(
                    transaction_consumer, *args, **kwargs
                )
            except _queue.Empty as error:
                raise NoSessionAvailableException() from error  # exception chaining
            except exceptions.Aborted as error:
                raise TimeoutError() from error  # exception chaining

        return await run_as_non_blocking(task)


class NoSessionAvailableException(Exception):
    pass
