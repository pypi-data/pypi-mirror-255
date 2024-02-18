from typing import Any, Dict, List, Type, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CloudAccount")


@_attrs_define
class CloudAccount:
    """
    Attributes:
        account_id (Union[Unset, str]): AWS Account ID
        account_name (Union[Unset, str]): Name used to describe the account, useful when the account hosts multiple
            projects
        region_name (Union[Unset, str]): AWS Region Code Example: us-west-2.
    """

    account_id: Union[Unset, str] = UNSET
    account_name: Union[Unset, str] = UNSET
    region_name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        account_id = self.account_id

        account_name = self.account_name

        region_name = self.region_name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if account_id is not UNSET:
            field_dict["accountId"] = account_id
        if account_name is not UNSET:
            field_dict["accountName"] = account_name
        if region_name is not UNSET:
            field_dict["regionName"] = region_name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        account_id = d.pop("accountId", UNSET)

        account_name = d.pop("accountName", UNSET)

        region_name = d.pop("regionName", UNSET)

        cloud_account = cls(
            account_id=account_id,
            account_name=account_name,
            region_name=region_name,
        )

        cloud_account.additional_properties = d
        return cloud_account

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
