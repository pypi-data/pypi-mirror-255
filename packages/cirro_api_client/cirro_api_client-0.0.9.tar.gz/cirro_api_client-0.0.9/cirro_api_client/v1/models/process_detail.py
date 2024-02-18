from typing import TYPE_CHECKING, Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.executor import Executor
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.custom_pipeline_settings import CustomPipelineSettings
    from ..models.pipeline_code import PipelineCode


T = TypeVar("T", bound="ProcessDetail")


@_attrs_define
class ProcessDetail:
    """
    Attributes:
        id (str): Unique ID of the Process Example: process-hutch-magic_flute-1_0.
        name (str): Friendly name for the process Example: MAGeCK Flute.
        description (str):  Example: MAGeCK Flute enables accurate identification of essential genes with their related
            biological functions.
        executor (Executor):
        child_process_ids (List[str]): IDs of pipelines that can be run downstream
        parent_process_ids (List[str]): IDs of pipelines that can run this pipeline
        linked_project_ids (List[str]): Projects that can run this pipeline
        data_type (Union[None, Unset, str]): Name of the data type this pipeline produces (if it is not defined, use the
            name)
        documentation_url (Union[None, Unset, str]): Link to pipeline documentation Example:
            https://docs.cirro.bio/pipelines/catalog_targeted_sequencing/#crispr-screen-analysis.
        file_requirements_message (Union[None, Unset, str]): Description of the files to be uploaded (optional)
        pipeline_code (Union['PipelineCode', None, Unset]):
        owner (Union[None, Unset, str]): Username of the pipeline creator (blank if Cirro curated)
        custom_settings (Union['CustomPipelineSettings', None, Unset]):
        is_archived (Union[Unset, bool]): Whether the process is marked for removal
    """

    id: str
    name: str
    description: str
    executor: Executor
    child_process_ids: List[str]
    parent_process_ids: List[str]
    linked_project_ids: List[str]
    data_type: Union[None, Unset, str] = UNSET
    documentation_url: Union[None, Unset, str] = UNSET
    file_requirements_message: Union[None, Unset, str] = UNSET
    pipeline_code: Union["PipelineCode", None, Unset] = UNSET
    owner: Union[None, Unset, str] = UNSET
    custom_settings: Union["CustomPipelineSettings", None, Unset] = UNSET
    is_archived: Union[Unset, bool] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        from ..models.custom_pipeline_settings import CustomPipelineSettings
        from ..models.pipeline_code import PipelineCode

        id = self.id

        name = self.name

        description = self.description

        executor = self.executor.value

        child_process_ids = self.child_process_ids

        parent_process_ids = self.parent_process_ids

        linked_project_ids = self.linked_project_ids

        data_type: Union[None, Unset, str]
        if isinstance(self.data_type, Unset):
            data_type = UNSET
        else:
            data_type = self.data_type

        documentation_url: Union[None, Unset, str]
        if isinstance(self.documentation_url, Unset):
            documentation_url = UNSET
        else:
            documentation_url = self.documentation_url

        file_requirements_message: Union[None, Unset, str]
        if isinstance(self.file_requirements_message, Unset):
            file_requirements_message = UNSET
        else:
            file_requirements_message = self.file_requirements_message

        pipeline_code: Union[Dict[str, Any], None, Unset]
        if isinstance(self.pipeline_code, Unset):
            pipeline_code = UNSET
        elif isinstance(self.pipeline_code, PipelineCode):
            pipeline_code = self.pipeline_code.to_dict()
        else:
            pipeline_code = self.pipeline_code

        owner: Union[None, Unset, str]
        if isinstance(self.owner, Unset):
            owner = UNSET
        else:
            owner = self.owner

        custom_settings: Union[Dict[str, Any], None, Unset]
        if isinstance(self.custom_settings, Unset):
            custom_settings = UNSET
        elif isinstance(self.custom_settings, CustomPipelineSettings):
            custom_settings = self.custom_settings.to_dict()
        else:
            custom_settings = self.custom_settings

        is_archived = self.is_archived

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "executor": executor,
                "childProcessIds": child_process_ids,
                "parentProcessIds": parent_process_ids,
                "linkedProjectIds": linked_project_ids,
            }
        )
        if data_type is not UNSET:
            field_dict["dataType"] = data_type
        if documentation_url is not UNSET:
            field_dict["documentationUrl"] = documentation_url
        if file_requirements_message is not UNSET:
            field_dict["fileRequirementsMessage"] = file_requirements_message
        if pipeline_code is not UNSET:
            field_dict["pipelineCode"] = pipeline_code
        if owner is not UNSET:
            field_dict["owner"] = owner
        if custom_settings is not UNSET:
            field_dict["customSettings"] = custom_settings
        if is_archived is not UNSET:
            field_dict["isArchived"] = is_archived

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.custom_pipeline_settings import CustomPipelineSettings
        from ..models.pipeline_code import PipelineCode

        d = src_dict.copy()
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        executor = Executor(d.pop("executor"))

        child_process_ids = cast(List[str], d.pop("childProcessIds"))

        parent_process_ids = cast(List[str], d.pop("parentProcessIds"))

        linked_project_ids = cast(List[str], d.pop("linkedProjectIds"))

        def _parse_data_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        data_type = _parse_data_type(d.pop("dataType", UNSET))

        def _parse_documentation_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        documentation_url = _parse_documentation_url(d.pop("documentationUrl", UNSET))

        def _parse_file_requirements_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        file_requirements_message = _parse_file_requirements_message(d.pop("fileRequirementsMessage", UNSET))

        def _parse_pipeline_code(data: object) -> Union["PipelineCode", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                pipeline_code_type_1 = PipelineCode.from_dict(data)

                return pipeline_code_type_1
            except:  # noqa: E722
                pass
            return cast(Union["PipelineCode", None, Unset], data)

        pipeline_code = _parse_pipeline_code(d.pop("pipelineCode", UNSET))

        def _parse_owner(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        owner = _parse_owner(d.pop("owner", UNSET))

        def _parse_custom_settings(data: object) -> Union["CustomPipelineSettings", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                custom_settings_type_1 = CustomPipelineSettings.from_dict(data)

                return custom_settings_type_1
            except:  # noqa: E722
                pass
            return cast(Union["CustomPipelineSettings", None, Unset], data)

        custom_settings = _parse_custom_settings(d.pop("customSettings", UNSET))

        is_archived = d.pop("isArchived", UNSET)

        process_detail = cls(
            id=id,
            name=name,
            description=description,
            executor=executor,
            child_process_ids=child_process_ids,
            parent_process_ids=parent_process_ids,
            linked_project_ids=linked_project_ids,
            data_type=data_type,
            documentation_url=documentation_url,
            file_requirements_message=file_requirements_message,
            pipeline_code=pipeline_code,
            owner=owner,
            custom_settings=custom_settings,
            is_archived=is_archived,
        )

        process_detail.additional_properties = d
        return process_detail

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
