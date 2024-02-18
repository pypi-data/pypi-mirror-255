from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.resources_info import ResourcesInfo


T = TypeVar("T", bound="SystemInfoResponse")


@_attrs_define
class SystemInfoResponse:
    """
    Attributes:
        sdk_app_id (str):
        resources_bucket (str):
        data_endpoint (str):
        region (str):
        system_message (str):
        commit_hash (str):
        version (str):
        resources_info (ResourcesInfo):
    """

    sdk_app_id: str
    resources_bucket: str
    data_endpoint: str
    region: str
    system_message: str
    commit_hash: str
    version: str
    resources_info: "ResourcesInfo"
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sdk_app_id = self.sdk_app_id

        resources_bucket = self.resources_bucket

        data_endpoint = self.data_endpoint

        region = self.region

        system_message = self.system_message

        commit_hash = self.commit_hash

        version = self.version

        resources_info = self.resources_info.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "sdkAppId": sdk_app_id,
                "resourcesBucket": resources_bucket,
                "dataEndpoint": data_endpoint,
                "region": region,
                "systemMessage": system_message,
                "commitHash": commit_hash,
                "version": version,
                "resourcesInfo": resources_info,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.resources_info import ResourcesInfo

        d = src_dict.copy()
        sdk_app_id = d.pop("sdkAppId")

        resources_bucket = d.pop("resourcesBucket")

        data_endpoint = d.pop("dataEndpoint")

        region = d.pop("region")

        system_message = d.pop("systemMessage")

        commit_hash = d.pop("commitHash")

        version = d.pop("version")

        resources_info = ResourcesInfo.from_dict(d.pop("resourcesInfo"))

        system_info_response = cls(
            sdk_app_id=sdk_app_id,
            resources_bucket=resources_bucket,
            data_endpoint=data_endpoint,
            region=region,
            system_message=system_message,
            commit_hash=commit_hash,
            version=version,
            resources_info=resources_info,
        )

        system_info_response.additional_properties = d
        return system_info_response

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
