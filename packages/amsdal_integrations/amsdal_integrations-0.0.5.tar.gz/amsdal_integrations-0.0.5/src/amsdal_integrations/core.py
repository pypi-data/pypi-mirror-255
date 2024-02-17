from typing import Any

from amsdal_integrations.clients.amsdal_client import AmsdalClient
from amsdal_integrations.clients.amsdal_client import AsyncAmsdalClient
from amsdal_integrations.clients.base import AsyncBaseClient
from amsdal_integrations.clients.base import BaseClient
from amsdal_integrations.data_classes import IntegrationConfig
from amsdal_integrations.data_classes import Schema


class AmsdalIntegration:
    def __init__(
        self,
        config: IntegrationConfig,
        client_class: type[BaseClient] | None = None,
    ) -> None:
        """
        Initialize Amsdal Integration.

        :param config: Configuration for Amsdal Integration.
        :type config: IntegrationConfig
        :param client_class: The client class to use for communicating. Defaults to AmsdalClient.
        :type client_class: type[BaseClient]
        """
        client_class = client_class or AmsdalClient
        self.client = client_class(
            host=config.amsdal_host,
            auth=config.amsdal_auth,
            **config.client_extra,
        )

    def register_schema(
        self,
        schema: Schema,
        operation_id: str | None = None,
        *,
        skip_data_migrations: bool = False,
    ) -> None:
        """
        Register a new schema/model version in AMSDAL application.

        :param schema: The schema/model to register.
        :type schema: Schema
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        :param skip_data_migrations: Whether to skip data migrations if a new version of schema is registering.
                                     Defaults to False.
        :type skip_data_migrations: bool, optional
        """
        self.client.register_schema(schema, operation_id=operation_id, skip_data_migrations=skip_data_migrations)

    def unregister_schema(self, class_name: str, operation_id: str | None = None) -> None:
        """
        Unregister a schema/model from AMSDAL application.

        :param class_name: The name of the schema/model to unregister.
        :type class_name: str
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        self.client.unregister_schema(class_name, operation_id=operation_id)

    def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Create a new object/data in AMSDAL application by specific class name.

        :param class_name: The name of the schema/model to create.
        :type class_name: str
        :param data: The data to create.
        :type data: dict[str, Any]
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        self.client.create(class_name, data, operation_id=operation_id)

    def update(self, class_name: str, object_id: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Update an existing object/data in AMSDAL application by specific class name and object id.

        :param class_name: The name of the schema/model to update.
        :type class_name: str
        :param object_id: The id of the object to update.
        :type object_id: str
        :param data: The data to update.
        :type data: dict[str, Any]
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        self.client.update(class_name, object_id, data, operation_id=operation_id)

    def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        """
        Delete an existing object/data in AMSDAL application by specific class name and object id.

        :param class_name: The name of the schema/model to delete.
        :type class_name: str
        :param object_id: The id of the object to delete.
        :type object_id: str
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        self.client.delete(class_name, object_id, operation_id=operation_id)


class AsyncAmsdalSdk:
    def __init__(
        self,
        config: IntegrationConfig,
        client_class: type[AsyncBaseClient] | None = None,
    ) -> None:
        client_class = client_class or AsyncAmsdalClient
        self.client = client_class(
            host=config.amsdal_host,
            auth=config.amsdal_auth,
            **config.client_extra,
        )

    async def register_schema(self, schema: Schema, operation_id: str | None = None) -> None:
        """
        Register a new schema/model version in AMSDAL application.

        :param schema: The schema/model to register.
        :type schema: Schema
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        :param skip_data_migrations: Whether to skip data migrations if a new version of schema is registering.
                                     Defaults to False.
        :type skip_data_migrations: bool, optional
        """
        await self.client.register_schema(schema, operation_id=operation_id)

    async def unregister_schema(self, class_name: str, operation_id: str | None = None) -> None:
        """
        Unregister a schema/model from AMSDAL application.

        :param class_name: The name of the schema/model to unregister.
        :type class_name: str
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        await self.client.unregister_schema(class_name, operation_id=operation_id)

    async def create(self, class_name: str, data: dict[str, Any], operation_id: str | None = None) -> None:
        """
        Create a new object/data in AMSDAL application by specific class name.

        :param class_name: The name of the schema/model to create.
        :type class_name: str
        :param data: The data to create.
        :type data: dict[str, Any]
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        await self.client.create(class_name, data, operation_id=operation_id)

    async def update(
        self,
        class_name: str,
        object_id: str,
        data: dict[str, Any],
        operation_id: str | None = None,
    ) -> None:
        """
        Update an existing object/data in AMSDAL application by specific class name and object id.

        :param class_name: The name of the schema/model to update.
        :type class_name: str
        :param object_id: The id of the object to update.
        :type object_id: str
        :param data: The data to update.
        :type data: dict[str, Any]
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        await self.client.update(class_name, object_id=object_id, data=data, operation_id=operation_id)

    async def delete(self, class_name: str, object_id: str, operation_id: str | None = None) -> None:
        """
        Delete an existing object/data in AMSDAL application by specific class name and object id.

        :param class_name: The name of the schema/model to delete.
        :type class_name: str
        :param object_id: The id of the object to delete.
        :type object_id: str
        :param operation_id: The operation id to use for this request. This is useful to prevent duplicated requests.
                             Defaults to None.
        :type operation_id: str, optional
        """
        await self.client.delete(class_name, object_id, operation_id=operation_id)
