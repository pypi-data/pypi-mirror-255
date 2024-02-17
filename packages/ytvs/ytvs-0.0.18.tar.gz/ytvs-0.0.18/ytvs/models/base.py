from dataclasses import dataclass, asdict
from typing import Type, TypeVar

from dataclasses_json import DataClassJsonMixin
from dataclasses_json.core import Json, _decode_dataclass

A = TypeVar("A", bound="DataClassJsonMixin")


@dataclass
class BaseModel(DataClassJsonMixin):
    """Base model class for instance use."""

    @classmethod
    def from_dict(cls: Type[A], kvs: Json, *, infer_missing=False) -> A:
        # save original data for lookup
        cls._json = kvs
        return _decode_dataclass(cls, kvs, infer_missing)

    def to_dict_ignore_none(self):
        return asdict(
            obj=self, dict_factory=lambda x: {k: v for (k, v) in x if v is not None}
        )
