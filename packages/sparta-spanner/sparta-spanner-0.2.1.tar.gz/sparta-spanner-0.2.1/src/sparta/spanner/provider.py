import dataclasses
import logging
import threading
import typing

from google.cloud import spanner

from sparta.spanner.service import DBService


@dataclasses.dataclass
class DBServiceConfig:
    instance_id: str
    database_id: str
    pool_size: typing.Optional[int] = None
    session_request_timeout: typing.Optional[int] = None


class DBServiceProvider:
    """
    Provides DBService instances.
    Responsible for creation and re-utilization of existing instances.
    """

    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(f"{__name__}.{type(self).__name__}")
        self._spanner_client = spanner.Client()
        self._instances = {}
        # Use lock to assure thread-safety.
        # See https://medium.com/analytics-vidhya/how-to-create-a-thread-safe-singleton-class-in-python-822e1170a7f6
        self._lock = threading.Lock()

    def get_by_config(self, config: DBServiceConfig) -> DBService:
        _key = hash(str(config))
        if _key not in self._instances:
            with self._lock:
                # Another thread could have created the instance before we acquired the lock. Double-check.
                if _key not in self._instances:
                    self._instances[_key] = DBService(
                        instance_id=config.instance_id,
                        database_id=config.database_id,
                        pool_size=config.pool_size,
                        session_request_timeout=config.session_request_timeout,
                        spanner_client=self._spanner_client,
                    )
        return self._instances[_key]

    def get(
        self,
        instance_id: str,
        database_id: str,
        pool_size: typing.Optional[int] = None,
        session_request_timeout: typing.Optional[int] = None,
    ) -> DBService:
        return self.get_by_config(
            DBServiceConfig(
                instance_id=instance_id,
                database_id=database_id,
                pool_size=pool_size,
                session_request_timeout=session_request_timeout,
            )
        )
