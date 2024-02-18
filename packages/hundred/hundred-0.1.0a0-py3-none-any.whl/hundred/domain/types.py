from abc import ABC, abstractmethod
from typing import Any, Final
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

__all__ = ("Entity", "EntityUUID", "ValueObject")


class Entity(BaseModel, ABC):
    model_config: Final[ConfigDict] = ConfigDict(validate_assignment=True)

    @property
    @abstractmethod
    def id(self) -> Any:
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, type(self)) and self.id == other.id


class EntityUUID(Entity, ABC):
    uuid: UUID = Field(alias="id", frozen=True)

    @property
    def id(self) -> UUID:
        return self.uuid


class ValueObject(BaseModel, ABC):
    model_config: Final[ConfigDict] = ConfigDict(frozen=True)
