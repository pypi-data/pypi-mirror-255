import logging
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from typing import Any
from urllib.parse import quote

import httpx

from amsdal_integrations.clients.base import AsyncBaseClient
from amsdal_integrations.clients.base import BaseClient
from amsdal_integrations.data_classes import Schema
from amsdal_integrations.utils import build_address_string

logger = logging.getLogger(__name__)


class AmsdalClient(BaseClient):
    def __init__(self, host: str, auth: Any = None, **kwargs: Any) -> None:
        super().__init__(host, auth, **kwargs)
        self._operation_ids: set[str] = set()
        self._client = httpx.Client(
            base_url=self._host,
            auth=self._auth,
            timeout=10.0,
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
        Sends a new schema of your model version directly to the AMSDAL Application.

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

            response = self._client.post(
                '/api/classes/',
                params={'skip_data_migrations': skip_data_migrations},
                json={'class_schema': asdict(schema)},
            )
            response.raise_for_status()

    def unregister_schema(self, class_name: str, operation_id: str | None = None) -> None:
        """
        Send a request to unregister a schema of your model version directly from AMSDAL Application.

        :param class_name: Name of the class.
        :type class_name: str
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = self._client.delete(
                f'/api/classes/{class_name}/',
            )
            response.raise_for_status()

    def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Send a request to create an object of your model directly to AMSDAL Application.

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

            response = self._client.post(
                '/api/objects/',
                json=data,
                params={
                    'class_name': class_name,
                    'load_references': False,
                },
            )
            response.raise_for_status()

    def update(self, class_name: str, object_id: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Send a request to update an object of your model directly to AMSDAL Application.

        :param class_name: Name of the class.
        :type class_name: str
        :param object_id: ID of the object.
        :type object_id: str
        :param data: Data of the object.
        :type data: dict[str, Any]
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        address = build_address_string(class_name, object_id, class_version='ALL')

        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = self._client.post(
                quote(f'/api/objects/{address}/'),
                params={'load_references': False},
                json=data,
            )
            response.raise_for_status()

    def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        """
        Send a request to delete an object of your model directly to AMSDAL Application.

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

            response = self._client.delete(
                quote(f'/api/objects/{address}/'),
            )
            response.raise_for_status()


class AsyncAmsdalClient(AsyncBaseClient):
    """
    Async version of the AMSDAL Client.
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
        Sends a new schema of your model version directly to the AMSDAL Application.

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
                '/api/classes/',
                params={'skip_data_migrations': skip_data_migrations},
                json={'class_schema': asdict(schema)},
            )
            response.raise_for_status()

    async def unregister_schema(self, class_name: str, operation_id: str | None = None) -> None:
        """
        Send a request to unregister a schema of your model version directly from AMSDAL Application.

        :param class_name: Name of the class.
        :type class_name: str
        :param operation_id: Operation ID for the request.
        :type operation_id: str
        """
        with self.unique_operation_id(operation_id) as do_request:
            if not do_request:
                return

            response = await self._client.delete(
                f'/api/classes/{class_name}/',
            )
            response.raise_for_status()

    async def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Send a request to create an object of your model directly to AMSDAL Application.

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
                '/api/objects/',
                json=data,
                params={
                    'class_name': class_name,
                    'load_references': False,
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
        Send a request to update an object of your model directly to AMSDAL Application.

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
                quote(f'/api/objects/{address}/'),
                params={'load_references': False},
                json=data,
            )
            response.raise_for_status()

    async def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        """
        Send a request to delete an object of your model directly to AMSDAL Application.

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

            response = await self._client.delete(
                quote(f'/api/objects/{address}/'),
            )
            response.raise_for_status()
