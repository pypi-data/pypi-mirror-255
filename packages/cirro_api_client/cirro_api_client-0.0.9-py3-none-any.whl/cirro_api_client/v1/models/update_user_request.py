from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.update_user_request_settings import UpdateUserRequestSettings


T = TypeVar("T", bound="UpdateUserRequest")


@_attrs_define
class UpdateUserRequest:
    """
    Attributes:
        name (str):
        email (str):
        phone (str):
        department (str):
        settings (UpdateUserRequestSettings):
    """

    name: str
    email: str
    phone: str
    department: str
    settings: "UpdateUserRequestSettings"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name

        email = self.email

        phone = self.phone

        department = self.department

        settings = self.settings.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "email": email,
                "phone": phone,
                "department": department,
                "settings": settings,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.update_user_request_settings import UpdateUserRequestSettings

        d = src_dict.copy()
        name = d.pop("name")

        email = d.pop("email")

        phone = d.pop("phone")

        department = d.pop("department")

        settings = UpdateUserRequestSettings.from_dict(d.pop("settings"))

        update_user_request = cls(
            name=name,
            email=email,
            phone=phone,
            department=department,
            settings=settings,
        )

        update_user_request.additional_properties = d
        return update_user_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
