from typing import Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="FileNamePattern")


@_attrs_define
class FileNamePattern:
    """
    Attributes:
        example_name (str):
        description (str):
    """

    example_name: str
    description: str
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        example_name = self.example_name

        description = self.description

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "exampleName": example_name,
                "description": description,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        example_name = d.pop("exampleName")

        description = d.pop("description")

        file_name_pattern = cls(
            example_name=example_name,
            description=description,
        )

        file_name_pattern.additional_properties = d
        return file_name_pattern

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
