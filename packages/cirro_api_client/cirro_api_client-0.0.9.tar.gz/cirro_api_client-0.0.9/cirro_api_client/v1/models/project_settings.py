from typing import Any, Dict, List, Type, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.budget_period import BudgetPeriod
from ..types import UNSET, Unset

T = TypeVar("T", bound="ProjectSettings")


@_attrs_define
class ProjectSettings:
    """
    Attributes:
        budget_period (BudgetPeriod):
        service_connections (List[str]):
        budget_amount (Union[Unset, int]): Total allowed cost for the budget period
        dragen_ami (Union[None, Unset, str]): AMI ID for the DRAGEN compute environment (if enabled)
        enable_compute (Union[Unset, bool]): Enables the default compute environment Default: True.
        enable_dragen (Union[Unset, bool]): Enables the DRAGEN compute environment Default: False.
        enable_backup (Union[Unset, bool]): Enables the AWS Backup service for S3 Default: False.
        enable_sftp (Union[Unset, bool]): Enables access to files over SFTP Default: False.
        max_f1vcpu (Union[Unset, int]): Service quota limit for On Demand F1 instances Default: 0.
        max_spot_vcpu (Union[Unset, int]): Service quota limit for SPOT instances Default: 0.
        retention_policy_days (Union[Unset, int]): Days to keep deleted datasets before being permanently erased
            Default: 7.
        create_vpc (Union[Unset, bool]): Creates a default VPC for the compute environment, if false, VPC ID must be
            provided Default: False.
        vpc_id (Union[None, Unset, str]): VPC that the compute environment will use
        batch_subnets (Union[List[str], None, Unset]): List of subnets that the compute environment will use
        kms_arn (Union[None, Unset, str]): KMS Key ARN to encrypt S3 objects, one will be created if the arn is not
            provided
    """

    budget_period: BudgetPeriod
    service_connections: List[str]
    budget_amount: Union[Unset, int] = UNSET
    dragen_ami: Union[None, Unset, str] = UNSET
    enable_compute: Union[Unset, bool] = True
    enable_dragen: Union[Unset, bool] = False
    enable_backup: Union[Unset, bool] = False
    enable_sftp: Union[Unset, bool] = False
    max_f1vcpu: Union[Unset, int] = 0
    max_spot_vcpu: Union[Unset, int] = 0
    retention_policy_days: Union[Unset, int] = 7
    create_vpc: Union[Unset, bool] = False
    vpc_id: Union[None, Unset, str] = UNSET
    batch_subnets: Union[List[str], None, Unset] = UNSET
    kms_arn: Union[None, Unset, str] = UNSET
    additional_properties: Dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        budget_period = self.budget_period.value

        service_connections = self.service_connections

        budget_amount = self.budget_amount

        dragen_ami: Union[None, Unset, str]
        if isinstance(self.dragen_ami, Unset):
            dragen_ami = UNSET
        else:
            dragen_ami = self.dragen_ami

        enable_compute = self.enable_compute

        enable_dragen = self.enable_dragen

        enable_backup = self.enable_backup

        enable_sftp = self.enable_sftp

        max_f1vcpu = self.max_f1vcpu

        max_spot_vcpu = self.max_spot_vcpu

        retention_policy_days = self.retention_policy_days

        create_vpc = self.create_vpc

        vpc_id: Union[None, Unset, str]
        if isinstance(self.vpc_id, Unset):
            vpc_id = UNSET
        else:
            vpc_id = self.vpc_id

        batch_subnets: Union[List[str], None, Unset]
        if isinstance(self.batch_subnets, Unset):
            batch_subnets = UNSET
        elif isinstance(self.batch_subnets, list):
            batch_subnets = self.batch_subnets

        else:
            batch_subnets = self.batch_subnets

        kms_arn: Union[None, Unset, str]
        if isinstance(self.kms_arn, Unset):
            kms_arn = UNSET
        else:
            kms_arn = self.kms_arn

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "budgetPeriod": budget_period,
                "serviceConnections": service_connections,
            }
        )
        if budget_amount is not UNSET:
            field_dict["budgetAmount"] = budget_amount
        if dragen_ami is not UNSET:
            field_dict["dragenAmi"] = dragen_ami
        if enable_compute is not UNSET:
            field_dict["enableCompute"] = enable_compute
        if enable_dragen is not UNSET:
            field_dict["enableDragen"] = enable_dragen
        if enable_backup is not UNSET:
            field_dict["enableBackup"] = enable_backup
        if enable_sftp is not UNSET:
            field_dict["enableSftp"] = enable_sftp
        if max_f1vcpu is not UNSET:
            field_dict["maxF1VCPU"] = max_f1vcpu
        if max_spot_vcpu is not UNSET:
            field_dict["maxSpotVCPU"] = max_spot_vcpu
        if retention_policy_days is not UNSET:
            field_dict["retentionPolicyDays"] = retention_policy_days
        if create_vpc is not UNSET:
            field_dict["createVpc"] = create_vpc
        if vpc_id is not UNSET:
            field_dict["vpcId"] = vpc_id
        if batch_subnets is not UNSET:
            field_dict["batchSubnets"] = batch_subnets
        if kms_arn is not UNSET:
            field_dict["kmsArn"] = kms_arn

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        budget_period = BudgetPeriod(d.pop("budgetPeriod"))

        service_connections = cast(List[str], d.pop("serviceConnections"))

        budget_amount = d.pop("budgetAmount", UNSET)

        def _parse_dragen_ami(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        dragen_ami = _parse_dragen_ami(d.pop("dragenAmi", UNSET))

        enable_compute = d.pop("enableCompute", UNSET)

        enable_dragen = d.pop("enableDragen", UNSET)

        enable_backup = d.pop("enableBackup", UNSET)

        enable_sftp = d.pop("enableSftp", UNSET)

        max_f1vcpu = d.pop("maxF1VCPU", UNSET)

        max_spot_vcpu = d.pop("maxSpotVCPU", UNSET)

        retention_policy_days = d.pop("retentionPolicyDays", UNSET)

        create_vpc = d.pop("createVpc", UNSET)

        def _parse_vpc_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        vpc_id = _parse_vpc_id(d.pop("vpcId", UNSET))

        def _parse_batch_subnets(data: object) -> Union[List[str], None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                batch_subnets_type_0 = cast(List[str], data)

                return batch_subnets_type_0
            except:  # noqa: E722
                pass
            return cast(Union[List[str], None, Unset], data)

        batch_subnets = _parse_batch_subnets(d.pop("batchSubnets", UNSET))

        def _parse_kms_arn(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        kms_arn = _parse_kms_arn(d.pop("kmsArn", UNSET))

        project_settings = cls(
            budget_period=budget_period,
            service_connections=service_connections,
            budget_amount=budget_amount,
            dragen_ami=dragen_ami,
            enable_compute=enable_compute,
            enable_dragen=enable_dragen,
            enable_backup=enable_backup,
            enable_sftp=enable_sftp,
            max_f1vcpu=max_f1vcpu,
            max_spot_vcpu=max_spot_vcpu,
            retention_policy_days=retention_policy_days,
            create_vpc=create_vpc,
            vpc_id=vpc_id,
            batch_subnets=batch_subnets,
            kms_arn=kms_arn,
        )

        project_settings.additional_properties = d
        return project_settings

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())
