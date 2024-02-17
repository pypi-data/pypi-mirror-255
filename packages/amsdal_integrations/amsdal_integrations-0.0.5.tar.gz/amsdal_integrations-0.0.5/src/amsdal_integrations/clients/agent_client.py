import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from typing import Any

import httpx

from amsdal_integrations.clients.base import AsyncBaseClient
from amsdal_integrations.clients.base import BaseClient
from amsdal_integrations.data_classes import Schema
from amsdal_integrations.utils import build_address_string

logger = logging.getLogger(__name__)


class AgentClient(BaseClient):
    """
    Agent Client that communicate with the AMSDAL Agent to avoid any performance issues.
    """

    def __init__(self, host: str, auth: Any = None, **kwargs: Any) -> None:
        super().__init__(host, auth, **kwargs)
        self._operation_ids: set[str] = set()
        self._client = httpx.Client(
            base_url=self._host,
            auth=self._auth,
            **self._params,
        )

    @contextmanager
    def unique_operation_id(self, operation_id: str | None) -> Iterator[bool]:
        if operation_id is not None and operation_id in self._operation_ids:
            logger.warning('Operation ID %s already exists', operation_id)
            yield False
            return

        yield True

        if operation_id is not None:
            self._operation_ids.add(operation_id)

    def register_schema(
        self,
        schema: Schema,
        operation_id: str | None = None,
        *,
        skip_data_migrations: bool = False,
    ) -> None:
        """
        Sends a new schema of your model version to the AMSDAL Agent.

        :param schema: Schema of your model version.
        :type schema: Schema
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        :param skip_data_migrations: Skip data migrations.
        :type skip_data_migrations: bool
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            logger.info('Agent Client: Registering class %s', schema.title)
            response = self._client.post(
                '/data',
                json={
                    'action': 'register_schema',
                    'params': {
                        'skip_data_migrations': skip_data_migrations,
                    },
                    'data': {'class_schema': asdict(schema)},
                },
            )
            response.raise_for_status()

    def unregister_schema(self, class_name: str, operation_id: str | None = None) -> None:
        """
        Send a request to unregister a schema of your model version from the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            logger.info('Agent Client: Unregister class %s', class_name)
            response = self._client.request(
                'DELETE',
                '/data',
                json={
                    'action': 'unregister_schema',
                    'path_params': [class_name],
                },
            )
            response.raise_for_status()

    def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Send a request to create an object of your model to the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param data: Data of the object.
        :type data: dict[str, Any]
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            logger.info('Agent Client: Create object for class %s', class_name)
            response = self._client.post(
                '/data',
                json={
                    'action': 'object_create',
                    'data': data,
                    'params': {
                        'class_name': class_name,
                        'load_references': False,
                    },
                },
            )
            response.raise_for_status()

    def update(self, class_name: str, object_id: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Send a request to update an object of your model to the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param object_id: ID of the object.
        :type object_id: str
        :param data: Data of the object.
        :type data: dict[str, Any]
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        address = build_address_string(class_name, object_id)

        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            logger.info('Agent Client: Update object for class %s', class_name)
            response = self._client.post(
                '/data',
                json={
                    'action': 'object_update',
                    'data': data,
                    'path_params': [address],
                    'params': {'load_references': False},
                },
            )
            response.raise_for_status()

    def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        """
        Send a request to delete an object of your model to the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param object_id: ID of the object.
        :type object_id: str
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        address = build_address_string(class_name, object_id)

        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            logger.info('Agent Client: Delete object %s', address)
            response = self._client.request(
                'DELETE',
                '/data',
                json={
                    'action': 'object_delete',
                    'path_params': [address],
                },
            )
            response.raise_for_status()


class AsyncAgentClient(AsyncBaseClient):
    """
    Async Agent Client that communicate with the AMSDAL Agent to avoid any performance issues.
    """

    def __init__(self, host: str, auth: Any = None, **kwargs: Any) -> None:
        super().__init__(host, auth, **kwargs)
        self._operation_ids: set[str] = set()
        self._client = httpx.AsyncClient(
            base_url=self._host,
            auth=self._auth,
            **self._params,
        )

    @contextmanager
    def unique_operation_id(self, operation_id: str | None) -> Iterator[bool]:
        if operation_id is not None and operation_id in self._operation_ids:
            logger.warning('Operation ID %s already exists', operation_id)
            yield False
            return

        yield True

        if operation_id is not None:
            self._operation_ids.add(operation_id)

    async def register_schema(
        self,
        schema: Schema,
        operation_id: str | None = None,
        *,
        skip_data_migrations: bool = False,
    ) -> None:
        """
        Sends a new schema of your model version to the AMSDAL Agent.

        :param schema: Schema of your model version.
        :type schema: Schema
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        :param skip_data_migrations: Skip data migrations.
        :type skip_data_migrations: bool
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = await self._client.post(
                '/data',
                json={
                    'action': 'register_schema',
                    'params': {
                        'skip_data_migrations': skip_data_migrations,
                    },
                    'data': asdict(schema),
                },
            )
            response.raise_for_status()

    async def unregister_schema(self, class_name: str, operation_id: str | None = None) -> None:
        """
        Send a request to unregister a schema of your model version from the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = await self._client.request(
                'DELETE',
                '/data',
                json={
                    'action': 'unregister_schema',
                    'path_params': [class_name],
                },
            )
            response.raise_for_status()

    async def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Send a request to create an object of your model to the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param data: Data of the object.
        :type data: dict[str, Any]
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = await self._client.post(
                '/data',
                json={
                    'action': 'object_create',
                    'data': data,
                    'params': {
                        'class_name': class_name,
                        'load_references': False,
                    },
                },
            )
            response.raise_for_status()

    async def update(
        self,
        class_name: str,
        object_id: str,
        data: dict[str, Any],
        operation_id: str | None = None,
    ) -> None:
        """
        Send a request to update an object of your model to the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param object_id: ID of the object.
        :type object_id: str
        :param data: Data of the object.
        :type data: dict[str, Any]
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        address = build_address_string(class_name, object_id)

        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = await self._client.post(
                '/data',
                json={
                    'action': 'object_update',
                    'data': data,
                    'path_params': [address],
                    'params': {'load_references': False},
                },
            )
            response.raise_for_status()

    async def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        """
        Send a request to delete an object of your model to the AMSDAL Agent.

        :param class_name: Name of the class.
        :type class_name: str
        :param object_id: ID of the object.
        :type object_id: str
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        address = build_address_string(class_name, object_id)

        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = await self._client.request(
                'DELETE',
                '/data',
                json={
                    'action': 'object_delete',
                    'path_params': [address],
                },
            )
            response.raise_for_status()
