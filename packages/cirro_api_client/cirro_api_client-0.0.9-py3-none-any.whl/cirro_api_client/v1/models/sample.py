import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.sample_metadata import SampleMetadata


T = TypeVar("T", bound="Sample")


@_attrs_define
class Sample:
    """
    Attributes:
        id (str):
        name (str):
        metadata (SampleMetadata):
        dataset_ids (List[str]):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    metadata: "SampleMetadata"
    dataset_ids: List[str]
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        metadata = self.metadata.to_dict()

        dataset_ids = self.dataset_ids

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "metadata": metadata,
                "datasetIds": dataset_ids,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.sample_metadata import SampleMetadata

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        metadata = SampleMetadata.from_dict(d.pop("metadata"))

        dataset_ids = cast(List[str], d.pop("datasetIds"))

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        sample = cls(
            id=id,
            name=name,
            metadata=metadata,
            dataset_ids=dataset_ids,
            created_at=created_at,
            updated_at=updated_at,
        )

        sample.additional_properties = d
        return sample

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
