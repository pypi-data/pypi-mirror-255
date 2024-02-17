from abc import ABC
from abc import abstractmethod
from typing import Any

from amsdal_integrations.data_classes import Schema


class BaseClient(ABC):
    def __init__(self, host: str, auth: Any, **kwargs: Any) -> None:
        self._host = host
        self._auth = auth
        self._params = kwargs

    @abstractmethod
    def register_schema(
        self,
        schema: Schema,
        operation_id: str | None = None,
        *,
        skip_data_migrations: bool = False,
    ) -> None:
        ...

    @abstractmethod
    def unregister_schema(
        self,
        class_name: str,
        operation_id: str | None = None,
    ) -> None:
        ...

    @abstractmethod
    def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        ...

    @abstractmethod
    def update(self, class_name: str, object_id: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        ...

    @abstractmethod
    def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        ...


class AsyncBaseClient(ABC):
    def __init__(self, host: str, auth: Any, **kwargs: Any) -> None:
        self._host = host
        self._auth = auth
        self._params = kwargs

    @abstractmethod
    async def register_schema(
        self,
        schema: Schema,
        operation_id: str | None = None,
        *,
        skip_data_migrations: bool = False,
    ) -> None:
        ...

    @abstractmethod
    async def unregister_schema(
        self,
        class_name: str,
        operation_id: str | None = None,
    ) -> None:
        ...

    @abstractmethod
    async def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        ...

    @abstractmethod
    async def update(
        self,
        class_name: str,
        object_id: str,
        data: dict[str, Any],
        operation_id: str | None = None,
    ) -> None:
        ...

    @abstractmethod
    async def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        ...
