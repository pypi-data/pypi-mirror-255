from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Optional
from typing import Union


@dataclass
class IntegrationConfig:
    amsdal_host: str
    """The host of the destination AMSDAL application or of the running AMSDAL Agent. Example: http://localhost:8054"""
    amsdal_auth: Any
    """The auth mechanism that will be used to communicate with `amsdal_host`. Can be any httpx.Auth instance."""
    client_extra: dict[str, Any] = field(default_factory=dict)
    """Extra parameters that will be passed to the httpx.Client constructor. Example: {'timeout': 10}"""


@dataclass
class DictItem:
    key: 'TypeSchema'
    """The key of the dictionary. Example: `{'type': 'string'}`"""
    value: 'TypeSchema'
    """The value of the dictionary. Example: `{'type': 'string'}`"""


@dataclass
class TypeSchema:
    type: str
    """The type of the schema. Should be valid AMSDAL type. Example: `string`"""
    items: Optional[Union[DictItem, 'TypeSchema']] = None  # noqa: UP007
    """The items of the schema in case of type is `array` or `dictionary`. Example: `{'type': 'string'}`"""


@dataclass
class OptionSchema:
    key: str
    """The key of the option. Example: `John Doe`"""
    value: str
    """The value of the option. Example: `John Doe`"""


@dataclass
class PropertySchema:
    type: str
    """The type of the property. Should be valid AMSDAL type. Example: `string`"""
    default: Any
    """The default value of the property. Example: `John Doe`"""
    title: str | None = None
    """The title of the property. Example: `Name`"""
    items: TypeSchema | DictItem | None = None
    """The items of the property in case of type is `array` or `dictionary`. Example: `{'type': 'string'}`"""
    options: list[OptionSchema] | None = None
    """The options of available values for this property."""


@dataclass
class Schema:
    title: str
    """The name of the schema/model/class. Should be valid Python class name. Example: User"""
    type: str = 'object'
    """The type of the schema. Should be `object` for now."""
    properties: dict[str, PropertySchema] = field(default_factory=dict)
    """The properties of the schema. Example: {'name': {'type': 'string', 'default': 'John Doe'}}"""
    required: list[str] = field(default_factory=list)
    """The required properties of the schema. Example: ['name']"""
    indexed: list[str] = field(default_factory=list)
    """The indexed properties of the schema. Example: ['name']"""
    unique: list[list[str]] = field(default_factory=list)
    """The unique properties of the schema. Example: [['name', 'email']]"""
    custom_code: str = ''
    """The custom code of the schema. Example: `def __str__(self): return self.name`"""
