import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.status import Status

if TYPE_CHECKING:
    from ..models.contact import Contact
    from ..models.project_settings import ProjectSettings
    from ..models.tag import Tag


T = TypeVar("T", bound="ProjectDetail")


@_attrs_define
class ProjectDetail:
    """
    Attributes:
        id (str):
        name (str):
        description (str):
        billing_account_id (str):
        contacts (List['Contact']):
        status (Status):
        settings (ProjectSettings):
        status_message (str):
        tags (List['Tag']):
        created_by (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
    """

    id: str
    name: str
    description: str
    billing_account_id: str
    contacts: List["Contact"]
    status: Status
    settings: "ProjectSettings"
    status_message: str
    tags: List["Tag"]
    created_by: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id

        name = self.name

        description = self.description

        billing_account_id = self.billing_account_id

        contacts = []
        for contacts_item_data in self.contacts:
            contacts_item = contacts_item_data.to_dict()
            contacts.append(contacts_item)

        status = self.status.value

        settings = self.settings.to_dict()

        status_message = self.status_message

        tags = []
        for tags_item_data in self.tags:
            tags_item = tags_item_data.to_dict()
            tags.append(tags_item)

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "billingAccountId": billing_account_id,
                "contacts": contacts,
                "status": status,
                "settings": settings,
                "statusMessage": status_message,
                "tags": tags,
                "createdBy": created_by,
                "createdAt": created_at,
                "updatedAt": updated_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.contact import Contact
        from ..models.project_settings import ProjectSettings
        from ..models.tag import Tag

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        billing_account_id = d.pop("billingAccountId")

        contacts = []
        _contacts = d.pop("contacts")
        for contacts_item_data in _contacts:
            contacts_item = Contact.from_dict(contacts_item_data)

            contacts.append(contacts_item)

        status = Status(d.pop("status"))

        settings = ProjectSettings.from_dict(d.pop("settings"))

        status_message = d.pop("statusMessage")

        tags = []
        _tags = d.pop("tags")
        for tags_item_data in _tags:
            tags_item = Tag.from_dict(tags_item_data)

            tags.append(tags_item)

        created_by = d.pop("createdBy")

        created_at = isoparse(d.pop("createdAt"))

        updated_at = isoparse(d.pop("updatedAt"))

        project_detail = cls(
            id=id,
            name=name,
            description=description,
            billing_account_id=billing_account_id,
            contacts=contacts,
            status=status,
            settings=settings,
            status_message=status_message,
            tags=tags,
            created_by=created_by,
            created_at=created_at,
            updated_at=updated_at,
        )

        project_detail.additional_properties = d
        return project_detail

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
