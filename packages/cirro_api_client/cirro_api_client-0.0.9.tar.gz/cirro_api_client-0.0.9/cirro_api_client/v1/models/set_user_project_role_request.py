from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.project_role import ProjectRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="SetUserProjectRoleRequest")


@_attrs_define
class SetUserProjectRoleRequest:
    """
    Attributes:
        username (str):
        role (ProjectRole):
        supress_notification (Union[Unset, bool]):  Default: False.
    """

    username: str
    role: ProjectRole
    supress_notification: Union[Unset, bool] = False
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        username = self.username

        role = self.role.value

        supress_notification = self.supress_notification

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "username": username,
                "role": role,
            }
        )
        if supress_notification is not UNSET:
            field_dict["supressNotification"] = supress_notification

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        username = d.pop("username")

        role = ProjectRole(d.pop("role"))

        supress_notification = d.pop("supressNotification", UNSET)

        set_user_project_role_request = cls(
            username=username,
            role=role,
            supress_notification=supress_notification,
        )

        set_user_project_role_request.additional_properties = d
        return set_user_project_role_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
