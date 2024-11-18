import json
from dataclasses import fields
from fractions import Fraction
from typing import Any, Type, TypeVar

T = TypeVar("T", bound="JsonSerializable")


class JsonEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> dict:
        if isinstance(obj, JsonSerializable):
            return obj.to_dict()
        return super().default(obj)


class JsonSerializable:
    @classmethod
    def from_json(cls: Type[T], data: dict) -> T:
        # Ensure cls is a dataclass
        if not hasattr(cls, "__dataclass_fields__"):
            raise TypeError(f"{cls.__name__} is not a dataclass")

        # Get the field names and types of the dataclass
        cls_fields = {f.name: f.type for f in fields(cls)}  # type: ignore

        # Filter out any fields in the JSON that are not present in the dataclass
        filtered_data = {}
        for k, v in data.items():
            if k in cls_fields:
                if cls_fields[k] == Fraction:
                    filtered_data[k] = Fraction(v)
                else:
                    filtered_data[k] = v

        # Return an instance of the class using the filtered data
        return cls(**filtered_data)

    @classmethod
    def from_json_string(cls: Type[T], json_str: str) -> T:
        # Parse the JSON string first
        data = json.loads(json_str)

        # Call from_json method for object creation
        return cls.from_json(data)

    def to_dict(self) -> dict:
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, Fraction):
                result[key] = round(float(value), 2)
            else:
                result[key] = value
        return result

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=4)

    def to_human_readable(self) -> str:
        return str(self.__dict__)
