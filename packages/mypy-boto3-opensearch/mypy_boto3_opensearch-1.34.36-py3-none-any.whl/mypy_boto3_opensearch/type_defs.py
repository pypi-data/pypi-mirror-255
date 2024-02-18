"""
Type annotations for opensearch service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_opensearch/type_defs/)

Usage::

    ```python
    from mypy_boto3_opensearch.type_defs import AWSDomainInformationTypeDef

    data: AWSDomainInformationTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionSeverityType,
    ActionStatusType,
    ActionTypeType,
    AutoTuneDesiredStateType,
    AutoTuneStateType,
    ConfigChangeStatusType,
    ConnectionModeType,
    DeploymentStatusType,
    DescribePackagesFilterNameType,
    DomainHealthType,
    DomainPackageStatusType,
    DomainProcessingStatusTypeType,
    DomainStateType,
    DryRunModeType,
    EngineTypeType,
    InboundConnectionStatusCodeType,
    InitiatedByType,
    IPAddressTypeType,
    LogTypeType,
    MaintenanceStatusType,
    MaintenanceTypeType,
    MasterNodeStatusType,
    NodeStatusType,
    NodeTypeType,
    OpenSearchPartitionInstanceTypeType,
    OpenSearchWarmPartitionInstanceTypeType,
    OptionStateType,
    OutboundConnectionStatusCodeType,
    OverallChangeStatusType,
    PackageStatusType,
    PackageTypeType,
    PrincipalTypeType,
    PropertyValueTypeType,
    ReservedInstancePaymentOptionType,
    RollbackOnDisableType,
    ScheduleAtType,
    ScheduledAutoTuneActionTypeType,
    ScheduledAutoTuneSeverityTypeType,
    ScheduledByType,
    SkipUnavailableStatusType,
    TLSSecurityPolicyType,
    UpgradeStatusType,
    UpgradeStepType,
    VolumeTypeType,
    VpcEndpointErrorCodeType,
    VpcEndpointStatusType,
    ZoneStatusType,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AWSDomainInformationTypeDef",
    "AcceptInboundConnectionRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "OptionStatusTypeDef",
    "TagTypeDef",
    "AdditionalLimitTypeDef",
    "MasterUserOptionsTypeDef",
    "AssociatePackageRequestRequestTypeDef",
    "AuthorizeVpcEndpointAccessRequestRequestTypeDef",
    "AuthorizedPrincipalTypeDef",
    "ScheduledAutoTuneDetailsTypeDef",
    "DurationTypeDef",
    "TimestampTypeDef",
    "AutoTuneOptionsOutputTypeDef",
    "AutoTuneStatusTypeDef",
    "AvailabilityZoneInfoTypeDef",
    "CancelDomainConfigChangeRequestRequestTypeDef",
    "CancelledChangePropertyTypeDef",
    "CancelServiceSoftwareUpdateRequestRequestTypeDef",
    "ServiceSoftwareOptionsTypeDef",
    "ChangeProgressDetailsTypeDef",
    "ChangeProgressStageTypeDef",
    "ColdStorageOptionsTypeDef",
    "ZoneAwarenessConfigTypeDef",
    "CognitoOptionsTypeDef",
    "CompatibleVersionsMapTypeDef",
    "CrossClusterSearchConnectionPropertiesTypeDef",
    "DomainEndpointOptionsTypeDef",
    "EBSOptionsTypeDef",
    "EncryptionAtRestOptionsTypeDef",
    "LogPublishingOptionTypeDef",
    "NodeToNodeEncryptionOptionsTypeDef",
    "SnapshotOptionsTypeDef",
    "SoftwareUpdateOptionsTypeDef",
    "VPCOptionsTypeDef",
    "OutboundConnectionStatusTypeDef",
    "PackageSourceTypeDef",
    "S3GlueDataCatalogTypeDef",
    "DeleteDataSourceRequestRequestTypeDef",
    "DeleteDomainRequestRequestTypeDef",
    "DeleteInboundConnectionRequestRequestTypeDef",
    "DeleteOutboundConnectionRequestRequestTypeDef",
    "DeletePackageRequestRequestTypeDef",
    "DeleteVpcEndpointRequestRequestTypeDef",
    "VpcEndpointSummaryTypeDef",
    "DescribeDomainAutoTunesRequestRequestTypeDef",
    "DescribeDomainChangeProgressRequestRequestTypeDef",
    "DescribeDomainConfigRequestRequestTypeDef",
    "DescribeDomainHealthRequestRequestTypeDef",
    "DescribeDomainNodesRequestRequestTypeDef",
    "DomainNodesStatusTypeDef",
    "DescribeDomainRequestRequestTypeDef",
    "DescribeDomainsRequestRequestTypeDef",
    "DescribeDryRunProgressRequestRequestTypeDef",
    "DryRunResultsTypeDef",
    "FilterTypeDef",
    "DescribeInstanceTypeLimitsRequestRequestTypeDef",
    "DescribePackagesFilterTypeDef",
    "DescribeReservedInstanceOfferingsRequestRequestTypeDef",
    "DescribeReservedInstancesRequestRequestTypeDef",
    "DescribeVpcEndpointsRequestRequestTypeDef",
    "VpcEndpointErrorTypeDef",
    "DissociatePackageRequestRequestTypeDef",
    "ModifyingPropertiesTypeDef",
    "DomainInfoTypeDef",
    "DomainMaintenanceDetailsTypeDef",
    "ErrorDetailsTypeDef",
    "VPCDerivedInfoTypeDef",
    "ValidationFailureTypeDef",
    "GetCompatibleVersionsRequestRequestTypeDef",
    "GetDataSourceRequestRequestTypeDef",
    "GetDomainMaintenanceStatusRequestRequestTypeDef",
    "GetPackageVersionHistoryRequestRequestTypeDef",
    "GetUpgradeHistoryRequestRequestTypeDef",
    "GetUpgradeStatusRequestRequestTypeDef",
    "InboundConnectionStatusTypeDef",
    "InstanceCountLimitsTypeDef",
    "InstanceTypeDetailsTypeDef",
    "ListDataSourcesRequestRequestTypeDef",
    "ListDomainMaintenancesRequestRequestTypeDef",
    "ListDomainNamesRequestRequestTypeDef",
    "ListDomainsForPackageRequestRequestTypeDef",
    "ListInstanceTypeDetailsRequestRequestTypeDef",
    "ListPackagesForDomainRequestRequestTypeDef",
    "ListScheduledActionsRequestRequestTypeDef",
    "ScheduledActionTypeDef",
    "ListTagsRequestRequestTypeDef",
    "ListVersionsRequestRequestTypeDef",
    "ListVpcEndpointAccessRequestRequestTypeDef",
    "ListVpcEndpointsForDomainRequestRequestTypeDef",
    "ListVpcEndpointsRequestRequestTypeDef",
    "WindowStartTimeTypeDef",
    "PluginPropertiesTypeDef",
    "PurchaseReservedInstanceOfferingRequestRequestTypeDef",
    "RecurringChargeTypeDef",
    "RejectInboundConnectionRequestRequestTypeDef",
    "RemoveTagsRequestRequestTypeDef",
    "RevokeVpcEndpointAccessRequestRequestTypeDef",
    "SAMLIdpTypeDef",
    "StartDomainMaintenanceRequestRequestTypeDef",
    "StartServiceSoftwareUpdateRequestRequestTypeDef",
    "StorageTypeLimitTypeDef",
    "UpdateScheduledActionRequestRequestTypeDef",
    "UpgradeDomainRequestRequestTypeDef",
    "UpgradeStepItemTypeDef",
    "DomainInformationContainerTypeDef",
    "AddDataSourceResponseTypeDef",
    "DeleteDataSourceResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetDomainMaintenanceStatusResponseTypeDef",
    "GetUpgradeStatusResponseTypeDef",
    "ListVersionsResponseTypeDef",
    "PurchaseReservedInstanceOfferingResponseTypeDef",
    "StartDomainMaintenanceResponseTypeDef",
    "UpdateDataSourceResponseTypeDef",
    "AccessPoliciesStatusTypeDef",
    "AdvancedOptionsStatusTypeDef",
    "IPAddressTypeStatusTypeDef",
    "VersionStatusTypeDef",
    "AddTagsRequestRequestTypeDef",
    "ListTagsResponseTypeDef",
    "AuthorizeVpcEndpointAccessResponseTypeDef",
    "ListVpcEndpointAccessResponseTypeDef",
    "AutoTuneDetailsTypeDef",
    "AutoTuneMaintenanceScheduleTypeDef",
    "EnvironmentInfoTypeDef",
    "CancelDomainConfigChangeResponseTypeDef",
    "CancelServiceSoftwareUpdateResponseTypeDef",
    "StartServiceSoftwareUpdateResponseTypeDef",
    "UpgradeDomainResponseTypeDef",
    "ChangeProgressStatusDetailsTypeDef",
    "ClusterConfigTypeDef",
    "CognitoOptionsStatusTypeDef",
    "GetCompatibleVersionsResponseTypeDef",
    "ConnectionPropertiesTypeDef",
    "DomainEndpointOptionsStatusTypeDef",
    "EBSOptionsStatusTypeDef",
    "EncryptionAtRestOptionsStatusTypeDef",
    "LogPublishingOptionsStatusTypeDef",
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    "SnapshotOptionsStatusTypeDef",
    "SoftwareUpdateOptionsStatusTypeDef",
    "CreateVpcEndpointRequestRequestTypeDef",
    "UpdateVpcEndpointRequestRequestTypeDef",
    "CreatePackageRequestRequestTypeDef",
    "UpdatePackageRequestRequestTypeDef",
    "DataSourceTypeTypeDef",
    "DeleteVpcEndpointResponseTypeDef",
    "ListVpcEndpointsForDomainResponseTypeDef",
    "ListVpcEndpointsResponseTypeDef",
    "DescribeDomainNodesResponseTypeDef",
    "DescribeInboundConnectionsRequestRequestTypeDef",
    "DescribeOutboundConnectionsRequestRequestTypeDef",
    "DescribePackagesRequestRequestTypeDef",
    "ListDomainNamesResponseTypeDef",
    "ListDomainMaintenancesResponseTypeDef",
    "DomainPackageDetailsTypeDef",
    "VPCDerivedInfoStatusTypeDef",
    "VpcEndpointTypeDef",
    "DryRunProgressStatusTypeDef",
    "InstanceLimitsTypeDef",
    "ListInstanceTypeDetailsResponseTypeDef",
    "ListScheduledActionsResponseTypeDef",
    "UpdateScheduledActionResponseTypeDef",
    "OffPeakWindowTypeDef",
    "PackageDetailsTypeDef",
    "PackageVersionHistoryTypeDef",
    "ReservedInstanceOfferingTypeDef",
    "ReservedInstanceTypeDef",
    "SAMLOptionsInputTypeDef",
    "SAMLOptionsOutputTypeDef",
    "StorageTypeTypeDef",
    "UpgradeHistoryTypeDef",
    "InboundConnectionTypeDef",
    "AutoTuneTypeDef",
    "AutoTuneOptionsInputTypeDef",
    "AutoTuneOptionsTypeDef",
    "DescribeDomainHealthResponseTypeDef",
    "DescribeDomainChangeProgressResponseTypeDef",
    "ClusterConfigStatusTypeDef",
    "CreateOutboundConnectionRequestRequestTypeDef",
    "CreateOutboundConnectionResponseTypeDef",
    "OutboundConnectionTypeDef",
    "AddDataSourceRequestRequestTypeDef",
    "DataSourceDetailsTypeDef",
    "GetDataSourceResponseTypeDef",
    "UpdateDataSourceRequestRequestTypeDef",
    "AssociatePackageResponseTypeDef",
    "DissociatePackageResponseTypeDef",
    "ListDomainsForPackageResponseTypeDef",
    "ListPackagesForDomainResponseTypeDef",
    "CreateVpcEndpointResponseTypeDef",
    "DescribeVpcEndpointsResponseTypeDef",
    "UpdateVpcEndpointResponseTypeDef",
    "OffPeakWindowOptionsTypeDef",
    "CreatePackageResponseTypeDef",
    "DeletePackageResponseTypeDef",
    "DescribePackagesResponseTypeDef",
    "UpdatePackageResponseTypeDef",
    "GetPackageVersionHistoryResponseTypeDef",
    "DescribeReservedInstanceOfferingsResponseTypeDef",
    "DescribeReservedInstancesResponseTypeDef",
    "AdvancedSecurityOptionsInputTypeDef",
    "AdvancedSecurityOptionsTypeDef",
    "LimitsTypeDef",
    "GetUpgradeHistoryResponseTypeDef",
    "AcceptInboundConnectionResponseTypeDef",
    "DeleteInboundConnectionResponseTypeDef",
    "DescribeInboundConnectionsResponseTypeDef",
    "RejectInboundConnectionResponseTypeDef",
    "DescribeDomainAutoTunesResponseTypeDef",
    "AutoTuneOptionsStatusTypeDef",
    "DeleteOutboundConnectionResponseTypeDef",
    "DescribeOutboundConnectionsResponseTypeDef",
    "ListDataSourcesResponseTypeDef",
    "OffPeakWindowOptionsStatusTypeDef",
    "CreateDomainRequestRequestTypeDef",
    "UpdateDomainConfigRequestRequestTypeDef",
    "AdvancedSecurityOptionsStatusTypeDef",
    "DomainStatusTypeDef",
    "DescribeInstanceTypeLimitsResponseTypeDef",
    "DomainConfigTypeDef",
    "CreateDomainResponseTypeDef",
    "DeleteDomainResponseTypeDef",
    "DescribeDomainResponseTypeDef",
    "DescribeDomainsResponseTypeDef",
    "DescribeDryRunProgressResponseTypeDef",
    "DescribeDomainConfigResponseTypeDef",
    "UpdateDomainConfigResponseTypeDef",
)

AWSDomainInformationTypeDef = TypedDict(
    "AWSDomainInformationTypeDef",
    {
        "DomainName": str,
        "OwnerId": NotRequired[str],
        "Region": NotRequired[str],
    },
)
AcceptInboundConnectionRequestRequestTypeDef = TypedDict(
    "AcceptInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)
OptionStatusTypeDef = TypedDict(
    "OptionStatusTypeDef",
    {
        "CreationDate": datetime,
        "UpdateDate": datetime,
        "State": OptionStateType,
        "UpdateVersion": NotRequired[int],
        "PendingDeletion": NotRequired[bool],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)
AdditionalLimitTypeDef = TypedDict(
    "AdditionalLimitTypeDef",
    {
        "LimitName": NotRequired[str],
        "LimitValues": NotRequired[List[str]],
    },
)
MasterUserOptionsTypeDef = TypedDict(
    "MasterUserOptionsTypeDef",
    {
        "MasterUserARN": NotRequired[str],
        "MasterUserName": NotRequired[str],
        "MasterUserPassword": NotRequired[str],
    },
)
AssociatePackageRequestRequestTypeDef = TypedDict(
    "AssociatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "DomainName": str,
    },
)
AuthorizeVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "AuthorizeVpcEndpointAccessRequestRequestTypeDef",
    {
        "DomainName": str,
        "Account": str,
    },
)
AuthorizedPrincipalTypeDef = TypedDict(
    "AuthorizedPrincipalTypeDef",
    {
        "PrincipalType": NotRequired[PrincipalTypeType],
        "Principal": NotRequired[str],
    },
)
ScheduledAutoTuneDetailsTypeDef = TypedDict(
    "ScheduledAutoTuneDetailsTypeDef",
    {
        "Date": NotRequired[datetime],
        "ActionType": NotRequired[ScheduledAutoTuneActionTypeType],
        "Action": NotRequired[str],
        "Severity": NotRequired[ScheduledAutoTuneSeverityTypeType],
    },
)
DurationTypeDef = TypedDict(
    "DurationTypeDef",
    {
        "Value": NotRequired[int],
        "Unit": NotRequired[Literal["HOURS"]],
    },
)
TimestampTypeDef = Union[datetime, str]
AutoTuneOptionsOutputTypeDef = TypedDict(
    "AutoTuneOptionsOutputTypeDef",
    {
        "State": NotRequired[AutoTuneStateType],
        "ErrorMessage": NotRequired[str],
        "UseOffPeakWindow": NotRequired[bool],
    },
)
AutoTuneStatusTypeDef = TypedDict(
    "AutoTuneStatusTypeDef",
    {
        "CreationDate": datetime,
        "UpdateDate": datetime,
        "State": AutoTuneStateType,
        "UpdateVersion": NotRequired[int],
        "ErrorMessage": NotRequired[str],
        "PendingDeletion": NotRequired[bool],
    },
)
AvailabilityZoneInfoTypeDef = TypedDict(
    "AvailabilityZoneInfoTypeDef",
    {
        "AvailabilityZoneName": NotRequired[str],
        "ZoneStatus": NotRequired[ZoneStatusType],
        "ConfiguredDataNodeCount": NotRequired[str],
        "AvailableDataNodeCount": NotRequired[str],
        "TotalShards": NotRequired[str],
        "TotalUnAssignedShards": NotRequired[str],
    },
)
CancelDomainConfigChangeRequestRequestTypeDef = TypedDict(
    "CancelDomainConfigChangeRequestRequestTypeDef",
    {
        "DomainName": str,
        "DryRun": NotRequired[bool],
    },
)
CancelledChangePropertyTypeDef = TypedDict(
    "CancelledChangePropertyTypeDef",
    {
        "PropertyName": NotRequired[str],
        "CancelledValue": NotRequired[str],
        "ActiveValue": NotRequired[str],
    },
)
CancelServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "CancelServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
ServiceSoftwareOptionsTypeDef = TypedDict(
    "ServiceSoftwareOptionsTypeDef",
    {
        "CurrentVersion": NotRequired[str],
        "NewVersion": NotRequired[str],
        "UpdateAvailable": NotRequired[bool],
        "Cancellable": NotRequired[bool],
        "UpdateStatus": NotRequired[DeploymentStatusType],
        "Description": NotRequired[str],
        "AutomatedUpdateDate": NotRequired[datetime],
        "OptionalDeployment": NotRequired[bool],
    },
)
ChangeProgressDetailsTypeDef = TypedDict(
    "ChangeProgressDetailsTypeDef",
    {
        "ChangeId": NotRequired[str],
        "Message": NotRequired[str],
        "ConfigChangeStatus": NotRequired[ConfigChangeStatusType],
        "InitiatedBy": NotRequired[InitiatedByType],
        "StartTime": NotRequired[datetime],
        "LastUpdatedTime": NotRequired[datetime],
    },
)
ChangeProgressStageTypeDef = TypedDict(
    "ChangeProgressStageTypeDef",
    {
        "Name": NotRequired[str],
        "Status": NotRequired[str],
        "Description": NotRequired[str],
        "LastUpdated": NotRequired[datetime],
    },
)
ColdStorageOptionsTypeDef = TypedDict(
    "ColdStorageOptionsTypeDef",
    {
        "Enabled": bool,
    },
)
ZoneAwarenessConfigTypeDef = TypedDict(
    "ZoneAwarenessConfigTypeDef",
    {
        "AvailabilityZoneCount": NotRequired[int],
    },
)
CognitoOptionsTypeDef = TypedDict(
    "CognitoOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "UserPoolId": NotRequired[str],
        "IdentityPoolId": NotRequired[str],
        "RoleArn": NotRequired[str],
    },
)
CompatibleVersionsMapTypeDef = TypedDict(
    "CompatibleVersionsMapTypeDef",
    {
        "SourceVersion": NotRequired[str],
        "TargetVersions": NotRequired[List[str]],
    },
)
CrossClusterSearchConnectionPropertiesTypeDef = TypedDict(
    "CrossClusterSearchConnectionPropertiesTypeDef",
    {
        "SkipUnavailable": NotRequired[SkipUnavailableStatusType],
    },
)
DomainEndpointOptionsTypeDef = TypedDict(
    "DomainEndpointOptionsTypeDef",
    {
        "EnforceHTTPS": NotRequired[bool],
        "TLSSecurityPolicy": NotRequired[TLSSecurityPolicyType],
        "CustomEndpointEnabled": NotRequired[bool],
        "CustomEndpoint": NotRequired[str],
        "CustomEndpointCertificateArn": NotRequired[str],
    },
)
EBSOptionsTypeDef = TypedDict(
    "EBSOptionsTypeDef",
    {
        "EBSEnabled": NotRequired[bool],
        "VolumeType": NotRequired[VolumeTypeType],
        "VolumeSize": NotRequired[int],
        "Iops": NotRequired[int],
        "Throughput": NotRequired[int],
    },
)
EncryptionAtRestOptionsTypeDef = TypedDict(
    "EncryptionAtRestOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "KmsKeyId": NotRequired[str],
    },
)
LogPublishingOptionTypeDef = TypedDict(
    "LogPublishingOptionTypeDef",
    {
        "CloudWatchLogsLogGroupArn": NotRequired[str],
        "Enabled": NotRequired[bool],
    },
)
NodeToNodeEncryptionOptionsTypeDef = TypedDict(
    "NodeToNodeEncryptionOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
    },
)
SnapshotOptionsTypeDef = TypedDict(
    "SnapshotOptionsTypeDef",
    {
        "AutomatedSnapshotStartHour": NotRequired[int],
    },
)
SoftwareUpdateOptionsTypeDef = TypedDict(
    "SoftwareUpdateOptionsTypeDef",
    {
        "AutoSoftwareUpdateEnabled": NotRequired[bool],
    },
)
VPCOptionsTypeDef = TypedDict(
    "VPCOptionsTypeDef",
    {
        "SubnetIds": NotRequired[Sequence[str]],
        "SecurityGroupIds": NotRequired[Sequence[str]],
    },
)
OutboundConnectionStatusTypeDef = TypedDict(
    "OutboundConnectionStatusTypeDef",
    {
        "StatusCode": NotRequired[OutboundConnectionStatusCodeType],
        "Message": NotRequired[str],
    },
)
PackageSourceTypeDef = TypedDict(
    "PackageSourceTypeDef",
    {
        "S3BucketName": NotRequired[str],
        "S3Key": NotRequired[str],
    },
)
S3GlueDataCatalogTypeDef = TypedDict(
    "S3GlueDataCatalogTypeDef",
    {
        "RoleArn": NotRequired[str],
    },
)
DeleteDataSourceRequestRequestTypeDef = TypedDict(
    "DeleteDataSourceRequestRequestTypeDef",
    {
        "DomainName": str,
        "Name": str,
    },
)
DeleteDomainRequestRequestTypeDef = TypedDict(
    "DeleteDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DeleteInboundConnectionRequestRequestTypeDef = TypedDict(
    "DeleteInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)
DeleteOutboundConnectionRequestRequestTypeDef = TypedDict(
    "DeleteOutboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)
DeletePackageRequestRequestTypeDef = TypedDict(
    "DeletePackageRequestRequestTypeDef",
    {
        "PackageID": str,
    },
)
DeleteVpcEndpointRequestRequestTypeDef = TypedDict(
    "DeleteVpcEndpointRequestRequestTypeDef",
    {
        "VpcEndpointId": str,
    },
)
VpcEndpointSummaryTypeDef = TypedDict(
    "VpcEndpointSummaryTypeDef",
    {
        "VpcEndpointId": NotRequired[str],
        "VpcEndpointOwner": NotRequired[str],
        "DomainArn": NotRequired[str],
        "Status": NotRequired[VpcEndpointStatusType],
    },
)
DescribeDomainAutoTunesRequestRequestTypeDef = TypedDict(
    "DescribeDomainAutoTunesRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeDomainChangeProgressRequestRequestTypeDef = TypedDict(
    "DescribeDomainChangeProgressRequestRequestTypeDef",
    {
        "DomainName": str,
        "ChangeId": NotRequired[str],
    },
)
DescribeDomainConfigRequestRequestTypeDef = TypedDict(
    "DescribeDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DescribeDomainHealthRequestRequestTypeDef = TypedDict(
    "DescribeDomainHealthRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DescribeDomainNodesRequestRequestTypeDef = TypedDict(
    "DescribeDomainNodesRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DomainNodesStatusTypeDef = TypedDict(
    "DomainNodesStatusTypeDef",
    {
        "NodeId": NotRequired[str],
        "NodeType": NotRequired[NodeTypeType],
        "AvailabilityZone": NotRequired[str],
        "InstanceType": NotRequired[OpenSearchPartitionInstanceTypeType],
        "NodeStatus": NotRequired[NodeStatusType],
        "StorageType": NotRequired[str],
        "StorageVolumeType": NotRequired[VolumeTypeType],
        "StorageSize": NotRequired[str],
    },
)
DescribeDomainRequestRequestTypeDef = TypedDict(
    "DescribeDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DescribeDomainsRequestRequestTypeDef = TypedDict(
    "DescribeDomainsRequestRequestTypeDef",
    {
        "DomainNames": Sequence[str],
    },
)
DescribeDryRunProgressRequestRequestTypeDef = TypedDict(
    "DescribeDryRunProgressRequestRequestTypeDef",
    {
        "DomainName": str,
        "DryRunId": NotRequired[str],
        "LoadDryRunConfig": NotRequired[bool],
    },
)
DryRunResultsTypeDef = TypedDict(
    "DryRunResultsTypeDef",
    {
        "DeploymentType": NotRequired[str],
        "Message": NotRequired[str],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": NotRequired[str],
        "Values": NotRequired[Sequence[str]],
    },
)
DescribeInstanceTypeLimitsRequestRequestTypeDef = TypedDict(
    "DescribeInstanceTypeLimitsRequestRequestTypeDef",
    {
        "InstanceType": OpenSearchPartitionInstanceTypeType,
        "EngineVersion": str,
        "DomainName": NotRequired[str],
    },
)
DescribePackagesFilterTypeDef = TypedDict(
    "DescribePackagesFilterTypeDef",
    {
        "Name": NotRequired[DescribePackagesFilterNameType],
        "Value": NotRequired[Sequence[str]],
    },
)
DescribeReservedInstanceOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstanceOfferingsRequestRequestTypeDef",
    {
        "ReservedInstanceOfferingId": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeReservedInstancesRequestRequestTypeDef = TypedDict(
    "DescribeReservedInstancesRequestRequestTypeDef",
    {
        "ReservedInstanceId": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeVpcEndpointsRequestRequestTypeDef = TypedDict(
    "DescribeVpcEndpointsRequestRequestTypeDef",
    {
        "VpcEndpointIds": Sequence[str],
    },
)
VpcEndpointErrorTypeDef = TypedDict(
    "VpcEndpointErrorTypeDef",
    {
        "VpcEndpointId": NotRequired[str],
        "ErrorCode": NotRequired[VpcEndpointErrorCodeType],
        "ErrorMessage": NotRequired[str],
    },
)
DissociatePackageRequestRequestTypeDef = TypedDict(
    "DissociatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "DomainName": str,
    },
)
ModifyingPropertiesTypeDef = TypedDict(
    "ModifyingPropertiesTypeDef",
    {
        "Name": NotRequired[str],
        "ActiveValue": NotRequired[str],
        "PendingValue": NotRequired[str],
        "ValueType": NotRequired[PropertyValueTypeType],
    },
)
DomainInfoTypeDef = TypedDict(
    "DomainInfoTypeDef",
    {
        "DomainName": NotRequired[str],
        "EngineType": NotRequired[EngineTypeType],
    },
)
DomainMaintenanceDetailsTypeDef = TypedDict(
    "DomainMaintenanceDetailsTypeDef",
    {
        "MaintenanceId": NotRequired[str],
        "DomainName": NotRequired[str],
        "Action": NotRequired[MaintenanceTypeType],
        "NodeId": NotRequired[str],
        "Status": NotRequired[MaintenanceStatusType],
        "StatusMessage": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "UpdatedAt": NotRequired[datetime],
    },
)
ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "ErrorType": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
VPCDerivedInfoTypeDef = TypedDict(
    "VPCDerivedInfoTypeDef",
    {
        "VPCId": NotRequired[str],
        "SubnetIds": NotRequired[List[str]],
        "AvailabilityZones": NotRequired[List[str]],
        "SecurityGroupIds": NotRequired[List[str]],
    },
)
ValidationFailureTypeDef = TypedDict(
    "ValidationFailureTypeDef",
    {
        "Code": NotRequired[str],
        "Message": NotRequired[str],
    },
)
GetCompatibleVersionsRequestRequestTypeDef = TypedDict(
    "GetCompatibleVersionsRequestRequestTypeDef",
    {
        "DomainName": NotRequired[str],
    },
)
GetDataSourceRequestRequestTypeDef = TypedDict(
    "GetDataSourceRequestRequestTypeDef",
    {
        "DomainName": str,
        "Name": str,
    },
)
GetDomainMaintenanceStatusRequestRequestTypeDef = TypedDict(
    "GetDomainMaintenanceStatusRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaintenanceId": str,
    },
)
GetPackageVersionHistoryRequestRequestTypeDef = TypedDict(
    "GetPackageVersionHistoryRequestRequestTypeDef",
    {
        "PackageID": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
GetUpgradeHistoryRequestRequestTypeDef = TypedDict(
    "GetUpgradeHistoryRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
GetUpgradeStatusRequestRequestTypeDef = TypedDict(
    "GetUpgradeStatusRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
InboundConnectionStatusTypeDef = TypedDict(
    "InboundConnectionStatusTypeDef",
    {
        "StatusCode": NotRequired[InboundConnectionStatusCodeType],
        "Message": NotRequired[str],
    },
)
InstanceCountLimitsTypeDef = TypedDict(
    "InstanceCountLimitsTypeDef",
    {
        "MinimumInstanceCount": NotRequired[int],
        "MaximumInstanceCount": NotRequired[int],
    },
)
InstanceTypeDetailsTypeDef = TypedDict(
    "InstanceTypeDetailsTypeDef",
    {
        "InstanceType": NotRequired[OpenSearchPartitionInstanceTypeType],
        "EncryptionEnabled": NotRequired[bool],
        "CognitoEnabled": NotRequired[bool],
        "AppLogsEnabled": NotRequired[bool],
        "AdvancedSecurityEnabled": NotRequired[bool],
        "WarmEnabled": NotRequired[bool],
        "InstanceRole": NotRequired[List[str]],
        "AvailabilityZones": NotRequired[List[str]],
    },
)
ListDataSourcesRequestRequestTypeDef = TypedDict(
    "ListDataSourcesRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
ListDomainMaintenancesRequestRequestTypeDef = TypedDict(
    "ListDomainMaintenancesRequestRequestTypeDef",
    {
        "DomainName": str,
        "Action": NotRequired[MaintenanceTypeType],
        "Status": NotRequired[MaintenanceStatusType],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListDomainNamesRequestRequestTypeDef = TypedDict(
    "ListDomainNamesRequestRequestTypeDef",
    {
        "EngineType": NotRequired[EngineTypeType],
    },
)
ListDomainsForPackageRequestRequestTypeDef = TypedDict(
    "ListDomainsForPackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListInstanceTypeDetailsRequestRequestTypeDef = TypedDict(
    "ListInstanceTypeDetailsRequestRequestTypeDef",
    {
        "EngineVersion": str,
        "DomainName": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "RetrieveAZs": NotRequired[bool],
        "InstanceType": NotRequired[str],
    },
)
ListPackagesForDomainRequestRequestTypeDef = TypedDict(
    "ListPackagesForDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListScheduledActionsRequestRequestTypeDef = TypedDict(
    "ListScheduledActionsRequestRequestTypeDef",
    {
        "DomainName": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ScheduledActionTypeDef = TypedDict(
    "ScheduledActionTypeDef",
    {
        "Id": str,
        "Type": ActionTypeType,
        "Severity": ActionSeverityType,
        "ScheduledTime": int,
        "Description": NotRequired[str],
        "ScheduledBy": NotRequired[ScheduledByType],
        "Status": NotRequired[ActionStatusType],
        "Mandatory": NotRequired[bool],
        "Cancellable": NotRequired[bool],
    },
)
ListTagsRequestRequestTypeDef = TypedDict(
    "ListTagsRequestRequestTypeDef",
    {
        "ARN": str,
    },
)
ListVersionsRequestRequestTypeDef = TypedDict(
    "ListVersionsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "ListVpcEndpointAccessRequestRequestTypeDef",
    {
        "DomainName": str,
        "NextToken": NotRequired[str],
    },
)
ListVpcEndpointsForDomainRequestRequestTypeDef = TypedDict(
    "ListVpcEndpointsForDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "NextToken": NotRequired[str],
    },
)
ListVpcEndpointsRequestRequestTypeDef = TypedDict(
    "ListVpcEndpointsRequestRequestTypeDef",
    {
        "NextToken": NotRequired[str],
    },
)
WindowStartTimeTypeDef = TypedDict(
    "WindowStartTimeTypeDef",
    {
        "Hours": int,
        "Minutes": int,
    },
)
PluginPropertiesTypeDef = TypedDict(
    "PluginPropertiesTypeDef",
    {
        "Name": NotRequired[str],
        "Description": NotRequired[str],
        "Version": NotRequired[str],
        "ClassName": NotRequired[str],
        "UncompressedSizeInBytes": NotRequired[int],
    },
)
PurchaseReservedInstanceOfferingRequestRequestTypeDef = TypedDict(
    "PurchaseReservedInstanceOfferingRequestRequestTypeDef",
    {
        "ReservedInstanceOfferingId": str,
        "ReservationName": str,
        "InstanceCount": NotRequired[int],
    },
)
RecurringChargeTypeDef = TypedDict(
    "RecurringChargeTypeDef",
    {
        "RecurringChargeAmount": NotRequired[float],
        "RecurringChargeFrequency": NotRequired[str],
    },
)
RejectInboundConnectionRequestRequestTypeDef = TypedDict(
    "RejectInboundConnectionRequestRequestTypeDef",
    {
        "ConnectionId": str,
    },
)
RemoveTagsRequestRequestTypeDef = TypedDict(
    "RemoveTagsRequestRequestTypeDef",
    {
        "ARN": str,
        "TagKeys": Sequence[str],
    },
)
RevokeVpcEndpointAccessRequestRequestTypeDef = TypedDict(
    "RevokeVpcEndpointAccessRequestRequestTypeDef",
    {
        "DomainName": str,
        "Account": str,
    },
)
SAMLIdpTypeDef = TypedDict(
    "SAMLIdpTypeDef",
    {
        "MetadataContent": str,
        "EntityId": str,
    },
)
StartDomainMaintenanceRequestRequestTypeDef = TypedDict(
    "StartDomainMaintenanceRequestRequestTypeDef",
    {
        "DomainName": str,
        "Action": MaintenanceTypeType,
        "NodeId": NotRequired[str],
    },
)
StartServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "StartServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
        "ScheduleAt": NotRequired[ScheduleAtType],
        "DesiredStartTime": NotRequired[int],
    },
)
StorageTypeLimitTypeDef = TypedDict(
    "StorageTypeLimitTypeDef",
    {
        "LimitName": NotRequired[str],
        "LimitValues": NotRequired[List[str]],
    },
)
UpdateScheduledActionRequestRequestTypeDef = TypedDict(
    "UpdateScheduledActionRequestRequestTypeDef",
    {
        "DomainName": str,
        "ActionID": str,
        "ActionType": ActionTypeType,
        "ScheduleAt": ScheduleAtType,
        "DesiredStartTime": NotRequired[int],
    },
)
UpgradeDomainRequestRequestTypeDef = TypedDict(
    "UpgradeDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "TargetVersion": str,
        "PerformCheckOnly": NotRequired[bool],
        "AdvancedOptions": NotRequired[Mapping[str, str]],
    },
)
UpgradeStepItemTypeDef = TypedDict(
    "UpgradeStepItemTypeDef",
    {
        "UpgradeStep": NotRequired[UpgradeStepType],
        "UpgradeStepStatus": NotRequired[UpgradeStatusType],
        "Issues": NotRequired[List[str]],
        "ProgressPercent": NotRequired[float],
    },
)
DomainInformationContainerTypeDef = TypedDict(
    "DomainInformationContainerTypeDef",
    {
        "AWSDomainInformation": NotRequired[AWSDomainInformationTypeDef],
    },
)
AddDataSourceResponseTypeDef = TypedDict(
    "AddDataSourceResponseTypeDef",
    {
        "Message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteDataSourceResponseTypeDef = TypedDict(
    "DeleteDataSourceResponseTypeDef",
    {
        "Message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDomainMaintenanceStatusResponseTypeDef = TypedDict(
    "GetDomainMaintenanceStatusResponseTypeDef",
    {
        "Status": MaintenanceStatusType,
        "StatusMessage": str,
        "NodeId": str,
        "Action": MaintenanceTypeType,
        "CreatedAt": datetime,
        "UpdatedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetUpgradeStatusResponseTypeDef = TypedDict(
    "GetUpgradeStatusResponseTypeDef",
    {
        "UpgradeStep": UpgradeStepType,
        "StepStatus": UpgradeStatusType,
        "UpgradeName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListVersionsResponseTypeDef = TypedDict(
    "ListVersionsResponseTypeDef",
    {
        "Versions": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PurchaseReservedInstanceOfferingResponseTypeDef = TypedDict(
    "PurchaseReservedInstanceOfferingResponseTypeDef",
    {
        "ReservedInstanceId": str,
        "ReservationName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDomainMaintenanceResponseTypeDef = TypedDict(
    "StartDomainMaintenanceResponseTypeDef",
    {
        "MaintenanceId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDataSourceResponseTypeDef = TypedDict(
    "UpdateDataSourceResponseTypeDef",
    {
        "Message": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AccessPoliciesStatusTypeDef = TypedDict(
    "AccessPoliciesStatusTypeDef",
    {
        "Options": str,
        "Status": OptionStatusTypeDef,
    },
)
AdvancedOptionsStatusTypeDef = TypedDict(
    "AdvancedOptionsStatusTypeDef",
    {
        "Options": Dict[str, str],
        "Status": OptionStatusTypeDef,
    },
)
IPAddressTypeStatusTypeDef = TypedDict(
    "IPAddressTypeStatusTypeDef",
    {
        "Options": IPAddressTypeType,
        "Status": OptionStatusTypeDef,
    },
)
VersionStatusTypeDef = TypedDict(
    "VersionStatusTypeDef",
    {
        "Options": str,
        "Status": OptionStatusTypeDef,
    },
)
AddTagsRequestRequestTypeDef = TypedDict(
    "AddTagsRequestRequestTypeDef",
    {
        "ARN": str,
        "TagList": Sequence[TagTypeDef],
    },
)
ListTagsResponseTypeDef = TypedDict(
    "ListTagsResponseTypeDef",
    {
        "TagList": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AuthorizeVpcEndpointAccessResponseTypeDef = TypedDict(
    "AuthorizeVpcEndpointAccessResponseTypeDef",
    {
        "AuthorizedPrincipal": AuthorizedPrincipalTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListVpcEndpointAccessResponseTypeDef = TypedDict(
    "ListVpcEndpointAccessResponseTypeDef",
    {
        "AuthorizedPrincipalList": List[AuthorizedPrincipalTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AutoTuneDetailsTypeDef = TypedDict(
    "AutoTuneDetailsTypeDef",
    {
        "ScheduledAutoTuneDetails": NotRequired[ScheduledAutoTuneDetailsTypeDef],
    },
)
AutoTuneMaintenanceScheduleTypeDef = TypedDict(
    "AutoTuneMaintenanceScheduleTypeDef",
    {
        "StartAt": NotRequired[TimestampTypeDef],
        "Duration": NotRequired[DurationTypeDef],
        "CronExpressionForRecurrence": NotRequired[str],
    },
)
EnvironmentInfoTypeDef = TypedDict(
    "EnvironmentInfoTypeDef",
    {
        "AvailabilityZoneInformation": NotRequired[List[AvailabilityZoneInfoTypeDef]],
    },
)
CancelDomainConfigChangeResponseTypeDef = TypedDict(
    "CancelDomainConfigChangeResponseTypeDef",
    {
        "CancelledChangeIds": List[str],
        "CancelledChangeProperties": List[CancelledChangePropertyTypeDef],
        "DryRun": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CancelServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "CancelServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "StartServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpgradeDomainResponseTypeDef = TypedDict(
    "UpgradeDomainResponseTypeDef",
    {
        "UpgradeId": str,
        "DomainName": str,
        "TargetVersion": str,
        "PerformCheckOnly": bool,
        "AdvancedOptions": Dict[str, str],
        "ChangeProgressDetails": ChangeProgressDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ChangeProgressStatusDetailsTypeDef = TypedDict(
    "ChangeProgressStatusDetailsTypeDef",
    {
        "ChangeId": NotRequired[str],
        "StartTime": NotRequired[datetime],
        "Status": NotRequired[OverallChangeStatusType],
        "PendingProperties": NotRequired[List[str]],
        "CompletedProperties": NotRequired[List[str]],
        "TotalNumberOfStages": NotRequired[int],
        "ChangeProgressStages": NotRequired[List[ChangeProgressStageTypeDef]],
        "LastUpdatedTime": NotRequired[datetime],
        "ConfigChangeStatus": NotRequired[ConfigChangeStatusType],
        "InitiatedBy": NotRequired[InitiatedByType],
    },
)
ClusterConfigTypeDef = TypedDict(
    "ClusterConfigTypeDef",
    {
        "InstanceType": NotRequired[OpenSearchPartitionInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "DedicatedMasterEnabled": NotRequired[bool],
        "ZoneAwarenessEnabled": NotRequired[bool],
        "ZoneAwarenessConfig": NotRequired[ZoneAwarenessConfigTypeDef],
        "DedicatedMasterType": NotRequired[OpenSearchPartitionInstanceTypeType],
        "DedicatedMasterCount": NotRequired[int],
        "WarmEnabled": NotRequired[bool],
        "WarmType": NotRequired[OpenSearchWarmPartitionInstanceTypeType],
        "WarmCount": NotRequired[int],
        "ColdStorageOptions": NotRequired[ColdStorageOptionsTypeDef],
        "MultiAZWithStandbyEnabled": NotRequired[bool],
    },
)
CognitoOptionsStatusTypeDef = TypedDict(
    "CognitoOptionsStatusTypeDef",
    {
        "Options": CognitoOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
GetCompatibleVersionsResponseTypeDef = TypedDict(
    "GetCompatibleVersionsResponseTypeDef",
    {
        "CompatibleVersions": List[CompatibleVersionsMapTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ConnectionPropertiesTypeDef = TypedDict(
    "ConnectionPropertiesTypeDef",
    {
        "Endpoint": NotRequired[str],
        "CrossClusterSearch": NotRequired[CrossClusterSearchConnectionPropertiesTypeDef],
    },
)
DomainEndpointOptionsStatusTypeDef = TypedDict(
    "DomainEndpointOptionsStatusTypeDef",
    {
        "Options": DomainEndpointOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
EBSOptionsStatusTypeDef = TypedDict(
    "EBSOptionsStatusTypeDef",
    {
        "Options": EBSOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
EncryptionAtRestOptionsStatusTypeDef = TypedDict(
    "EncryptionAtRestOptionsStatusTypeDef",
    {
        "Options": EncryptionAtRestOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
LogPublishingOptionsStatusTypeDef = TypedDict(
    "LogPublishingOptionsStatusTypeDef",
    {
        "Options": NotRequired[Dict[LogTypeType, LogPublishingOptionTypeDef]],
        "Status": NotRequired[OptionStatusTypeDef],
    },
)
NodeToNodeEncryptionOptionsStatusTypeDef = TypedDict(
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    {
        "Options": NodeToNodeEncryptionOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
SnapshotOptionsStatusTypeDef = TypedDict(
    "SnapshotOptionsStatusTypeDef",
    {
        "Options": SnapshotOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
SoftwareUpdateOptionsStatusTypeDef = TypedDict(
    "SoftwareUpdateOptionsStatusTypeDef",
    {
        "Options": NotRequired[SoftwareUpdateOptionsTypeDef],
        "Status": NotRequired[OptionStatusTypeDef],
    },
)
CreateVpcEndpointRequestRequestTypeDef = TypedDict(
    "CreateVpcEndpointRequestRequestTypeDef",
    {
        "DomainArn": str,
        "VpcOptions": VPCOptionsTypeDef,
        "ClientToken": NotRequired[str],
    },
)
UpdateVpcEndpointRequestRequestTypeDef = TypedDict(
    "UpdateVpcEndpointRequestRequestTypeDef",
    {
        "VpcEndpointId": str,
        "VpcOptions": VPCOptionsTypeDef,
    },
)
CreatePackageRequestRequestTypeDef = TypedDict(
    "CreatePackageRequestRequestTypeDef",
    {
        "PackageName": str,
        "PackageType": PackageTypeType,
        "PackageSource": PackageSourceTypeDef,
        "PackageDescription": NotRequired[str],
    },
)
UpdatePackageRequestRequestTypeDef = TypedDict(
    "UpdatePackageRequestRequestTypeDef",
    {
        "PackageID": str,
        "PackageSource": PackageSourceTypeDef,
        "PackageDescription": NotRequired[str],
        "CommitMessage": NotRequired[str],
    },
)
DataSourceTypeTypeDef = TypedDict(
    "DataSourceTypeTypeDef",
    {
        "S3GlueDataCatalog": NotRequired[S3GlueDataCatalogTypeDef],
    },
)
DeleteVpcEndpointResponseTypeDef = TypedDict(
    "DeleteVpcEndpointResponseTypeDef",
    {
        "VpcEndpointSummary": VpcEndpointSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListVpcEndpointsForDomainResponseTypeDef = TypedDict(
    "ListVpcEndpointsForDomainResponseTypeDef",
    {
        "VpcEndpointSummaryList": List[VpcEndpointSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListVpcEndpointsResponseTypeDef = TypedDict(
    "ListVpcEndpointsResponseTypeDef",
    {
        "VpcEndpointSummaryList": List[VpcEndpointSummaryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDomainNodesResponseTypeDef = TypedDict(
    "DescribeDomainNodesResponseTypeDef",
    {
        "DomainNodesStatusList": List[DomainNodesStatusTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeInboundConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeInboundConnectionsRequestRequestTypeDef",
    {
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeOutboundConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeOutboundConnectionsRequestRequestTypeDef",
    {
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribePackagesRequestRequestTypeDef = TypedDict(
    "DescribePackagesRequestRequestTypeDef",
    {
        "Filters": NotRequired[Sequence[DescribePackagesFilterTypeDef]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListDomainNamesResponseTypeDef = TypedDict(
    "ListDomainNamesResponseTypeDef",
    {
        "DomainNames": List[DomainInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDomainMaintenancesResponseTypeDef = TypedDict(
    "ListDomainMaintenancesResponseTypeDef",
    {
        "DomainMaintenances": List[DomainMaintenanceDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DomainPackageDetailsTypeDef = TypedDict(
    "DomainPackageDetailsTypeDef",
    {
        "PackageID": NotRequired[str],
        "PackageName": NotRequired[str],
        "PackageType": NotRequired[PackageTypeType],
        "LastUpdated": NotRequired[datetime],
        "DomainName": NotRequired[str],
        "DomainPackageStatus": NotRequired[DomainPackageStatusType],
        "PackageVersion": NotRequired[str],
        "ReferencePath": NotRequired[str],
        "ErrorDetails": NotRequired[ErrorDetailsTypeDef],
    },
)
VPCDerivedInfoStatusTypeDef = TypedDict(
    "VPCDerivedInfoStatusTypeDef",
    {
        "Options": VPCDerivedInfoTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
VpcEndpointTypeDef = TypedDict(
    "VpcEndpointTypeDef",
    {
        "VpcEndpointId": NotRequired[str],
        "VpcEndpointOwner": NotRequired[str],
        "DomainArn": NotRequired[str],
        "VpcOptions": NotRequired[VPCDerivedInfoTypeDef],
        "Status": NotRequired[VpcEndpointStatusType],
        "Endpoint": NotRequired[str],
    },
)
DryRunProgressStatusTypeDef = TypedDict(
    "DryRunProgressStatusTypeDef",
    {
        "DryRunId": str,
        "DryRunStatus": str,
        "CreationDate": str,
        "UpdateDate": str,
        "ValidationFailures": NotRequired[List[ValidationFailureTypeDef]],
    },
)
InstanceLimitsTypeDef = TypedDict(
    "InstanceLimitsTypeDef",
    {
        "InstanceCountLimits": NotRequired[InstanceCountLimitsTypeDef],
    },
)
ListInstanceTypeDetailsResponseTypeDef = TypedDict(
    "ListInstanceTypeDetailsResponseTypeDef",
    {
        "InstanceTypeDetails": List[InstanceTypeDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListScheduledActionsResponseTypeDef = TypedDict(
    "ListScheduledActionsResponseTypeDef",
    {
        "ScheduledActions": List[ScheduledActionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateScheduledActionResponseTypeDef = TypedDict(
    "UpdateScheduledActionResponseTypeDef",
    {
        "ScheduledAction": ScheduledActionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OffPeakWindowTypeDef = TypedDict(
    "OffPeakWindowTypeDef",
    {
        "WindowStartTime": NotRequired[WindowStartTimeTypeDef],
    },
)
PackageDetailsTypeDef = TypedDict(
    "PackageDetailsTypeDef",
    {
        "PackageID": NotRequired[str],
        "PackageName": NotRequired[str],
        "PackageType": NotRequired[PackageTypeType],
        "PackageDescription": NotRequired[str],
        "PackageStatus": NotRequired[PackageStatusType],
        "CreatedAt": NotRequired[datetime],
        "LastUpdatedAt": NotRequired[datetime],
        "AvailablePackageVersion": NotRequired[str],
        "ErrorDetails": NotRequired[ErrorDetailsTypeDef],
        "EngineVersion": NotRequired[str],
        "AvailablePluginProperties": NotRequired[PluginPropertiesTypeDef],
    },
)
PackageVersionHistoryTypeDef = TypedDict(
    "PackageVersionHistoryTypeDef",
    {
        "PackageVersion": NotRequired[str],
        "CommitMessage": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
        "PluginProperties": NotRequired[PluginPropertiesTypeDef],
    },
)
ReservedInstanceOfferingTypeDef = TypedDict(
    "ReservedInstanceOfferingTypeDef",
    {
        "ReservedInstanceOfferingId": NotRequired[str],
        "InstanceType": NotRequired[OpenSearchPartitionInstanceTypeType],
        "Duration": NotRequired[int],
        "FixedPrice": NotRequired[float],
        "UsagePrice": NotRequired[float],
        "CurrencyCode": NotRequired[str],
        "PaymentOption": NotRequired[ReservedInstancePaymentOptionType],
        "RecurringCharges": NotRequired[List[RecurringChargeTypeDef]],
    },
)
ReservedInstanceTypeDef = TypedDict(
    "ReservedInstanceTypeDef",
    {
        "ReservationName": NotRequired[str],
        "ReservedInstanceId": NotRequired[str],
        "BillingSubscriptionId": NotRequired[int],
        "ReservedInstanceOfferingId": NotRequired[str],
        "InstanceType": NotRequired[OpenSearchPartitionInstanceTypeType],
        "StartTime": NotRequired[datetime],
        "Duration": NotRequired[int],
        "FixedPrice": NotRequired[float],
        "UsagePrice": NotRequired[float],
        "CurrencyCode": NotRequired[str],
        "InstanceCount": NotRequired[int],
        "State": NotRequired[str],
        "PaymentOption": NotRequired[ReservedInstancePaymentOptionType],
        "RecurringCharges": NotRequired[List[RecurringChargeTypeDef]],
    },
)
SAMLOptionsInputTypeDef = TypedDict(
    "SAMLOptionsInputTypeDef",
    {
        "Enabled": NotRequired[bool],
        "Idp": NotRequired[SAMLIdpTypeDef],
        "MasterUserName": NotRequired[str],
        "MasterBackendRole": NotRequired[str],
        "SubjectKey": NotRequired[str],
        "RolesKey": NotRequired[str],
        "SessionTimeoutMinutes": NotRequired[int],
    },
)
SAMLOptionsOutputTypeDef = TypedDict(
    "SAMLOptionsOutputTypeDef",
    {
        "Enabled": NotRequired[bool],
        "Idp": NotRequired[SAMLIdpTypeDef],
        "SubjectKey": NotRequired[str],
        "RolesKey": NotRequired[str],
        "SessionTimeoutMinutes": NotRequired[int],
    },
)
StorageTypeTypeDef = TypedDict(
    "StorageTypeTypeDef",
    {
        "StorageTypeName": NotRequired[str],
        "StorageSubTypeName": NotRequired[str],
        "StorageTypeLimits": NotRequired[List[StorageTypeLimitTypeDef]],
    },
)
UpgradeHistoryTypeDef = TypedDict(
    "UpgradeHistoryTypeDef",
    {
        "UpgradeName": NotRequired[str],
        "StartTimestamp": NotRequired[datetime],
        "UpgradeStatus": NotRequired[UpgradeStatusType],
        "StepsList": NotRequired[List[UpgradeStepItemTypeDef]],
    },
)
InboundConnectionTypeDef = TypedDict(
    "InboundConnectionTypeDef",
    {
        "LocalDomainInfo": NotRequired[DomainInformationContainerTypeDef],
        "RemoteDomainInfo": NotRequired[DomainInformationContainerTypeDef],
        "ConnectionId": NotRequired[str],
        "ConnectionStatus": NotRequired[InboundConnectionStatusTypeDef],
        "ConnectionMode": NotRequired[ConnectionModeType],
    },
)
AutoTuneTypeDef = TypedDict(
    "AutoTuneTypeDef",
    {
        "AutoTuneType": NotRequired[Literal["SCHEDULED_ACTION"]],
        "AutoTuneDetails": NotRequired[AutoTuneDetailsTypeDef],
    },
)
AutoTuneOptionsInputTypeDef = TypedDict(
    "AutoTuneOptionsInputTypeDef",
    {
        "DesiredState": NotRequired[AutoTuneDesiredStateType],
        "MaintenanceSchedules": NotRequired[Sequence[AutoTuneMaintenanceScheduleTypeDef]],
        "UseOffPeakWindow": NotRequired[bool],
    },
)
AutoTuneOptionsTypeDef = TypedDict(
    "AutoTuneOptionsTypeDef",
    {
        "DesiredState": NotRequired[AutoTuneDesiredStateType],
        "RollbackOnDisable": NotRequired[RollbackOnDisableType],
        "MaintenanceSchedules": NotRequired[List[AutoTuneMaintenanceScheduleTypeDef]],
        "UseOffPeakWindow": NotRequired[bool],
    },
)
DescribeDomainHealthResponseTypeDef = TypedDict(
    "DescribeDomainHealthResponseTypeDef",
    {
        "DomainState": DomainStateType,
        "AvailabilityZoneCount": str,
        "ActiveAvailabilityZoneCount": str,
        "StandByAvailabilityZoneCount": str,
        "DataNodeCount": str,
        "DedicatedMaster": bool,
        "MasterEligibleNodeCount": str,
        "WarmNodeCount": str,
        "MasterNode": MasterNodeStatusType,
        "ClusterHealth": DomainHealthType,
        "TotalShards": str,
        "TotalUnAssignedShards": str,
        "EnvironmentInformation": List[EnvironmentInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDomainChangeProgressResponseTypeDef = TypedDict(
    "DescribeDomainChangeProgressResponseTypeDef",
    {
        "ChangeProgressStatus": ChangeProgressStatusDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ClusterConfigStatusTypeDef = TypedDict(
    "ClusterConfigStatusTypeDef",
    {
        "Options": ClusterConfigTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
CreateOutboundConnectionRequestRequestTypeDef = TypedDict(
    "CreateOutboundConnectionRequestRequestTypeDef",
    {
        "LocalDomainInfo": DomainInformationContainerTypeDef,
        "RemoteDomainInfo": DomainInformationContainerTypeDef,
        "ConnectionAlias": str,
        "ConnectionMode": NotRequired[ConnectionModeType],
        "ConnectionProperties": NotRequired[ConnectionPropertiesTypeDef],
    },
)
CreateOutboundConnectionResponseTypeDef = TypedDict(
    "CreateOutboundConnectionResponseTypeDef",
    {
        "LocalDomainInfo": DomainInformationContainerTypeDef,
        "RemoteDomainInfo": DomainInformationContainerTypeDef,
        "ConnectionAlias": str,
        "ConnectionStatus": OutboundConnectionStatusTypeDef,
        "ConnectionId": str,
        "ConnectionMode": ConnectionModeType,
        "ConnectionProperties": ConnectionPropertiesTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OutboundConnectionTypeDef = TypedDict(
    "OutboundConnectionTypeDef",
    {
        "LocalDomainInfo": NotRequired[DomainInformationContainerTypeDef],
        "RemoteDomainInfo": NotRequired[DomainInformationContainerTypeDef],
        "ConnectionId": NotRequired[str],
        "ConnectionAlias": NotRequired[str],
        "ConnectionStatus": NotRequired[OutboundConnectionStatusTypeDef],
        "ConnectionMode": NotRequired[ConnectionModeType],
        "ConnectionProperties": NotRequired[ConnectionPropertiesTypeDef],
    },
)
AddDataSourceRequestRequestTypeDef = TypedDict(
    "AddDataSourceRequestRequestTypeDef",
    {
        "DomainName": str,
        "Name": str,
        "DataSourceType": DataSourceTypeTypeDef,
        "Description": NotRequired[str],
    },
)
DataSourceDetailsTypeDef = TypedDict(
    "DataSourceDetailsTypeDef",
    {
        "DataSourceType": NotRequired[DataSourceTypeTypeDef],
        "Name": NotRequired[str],
        "Description": NotRequired[str],
    },
)
GetDataSourceResponseTypeDef = TypedDict(
    "GetDataSourceResponseTypeDef",
    {
        "DataSourceType": DataSourceTypeTypeDef,
        "Name": str,
        "Description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDataSourceRequestRequestTypeDef = TypedDict(
    "UpdateDataSourceRequestRequestTypeDef",
    {
        "DomainName": str,
        "Name": str,
        "DataSourceType": DataSourceTypeTypeDef,
        "Description": NotRequired[str],
    },
)
AssociatePackageResponseTypeDef = TypedDict(
    "AssociatePackageResponseTypeDef",
    {
        "DomainPackageDetails": DomainPackageDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DissociatePackageResponseTypeDef = TypedDict(
    "DissociatePackageResponseTypeDef",
    {
        "DomainPackageDetails": DomainPackageDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDomainsForPackageResponseTypeDef = TypedDict(
    "ListDomainsForPackageResponseTypeDef",
    {
        "DomainPackageDetailsList": List[DomainPackageDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPackagesForDomainResponseTypeDef = TypedDict(
    "ListPackagesForDomainResponseTypeDef",
    {
        "DomainPackageDetailsList": List[DomainPackageDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateVpcEndpointResponseTypeDef = TypedDict(
    "CreateVpcEndpointResponseTypeDef",
    {
        "VpcEndpoint": VpcEndpointTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeVpcEndpointsResponseTypeDef = TypedDict(
    "DescribeVpcEndpointsResponseTypeDef",
    {
        "VpcEndpoints": List[VpcEndpointTypeDef],
        "VpcEndpointErrors": List[VpcEndpointErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateVpcEndpointResponseTypeDef = TypedDict(
    "UpdateVpcEndpointResponseTypeDef",
    {
        "VpcEndpoint": VpcEndpointTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OffPeakWindowOptionsTypeDef = TypedDict(
    "OffPeakWindowOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "OffPeakWindow": NotRequired[OffPeakWindowTypeDef],
    },
)
CreatePackageResponseTypeDef = TypedDict(
    "CreatePackageResponseTypeDef",
    {
        "PackageDetails": PackageDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeletePackageResponseTypeDef = TypedDict(
    "DeletePackageResponseTypeDef",
    {
        "PackageDetails": PackageDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribePackagesResponseTypeDef = TypedDict(
    "DescribePackagesResponseTypeDef",
    {
        "PackageDetailsList": List[PackageDetailsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePackageResponseTypeDef = TypedDict(
    "UpdatePackageResponseTypeDef",
    {
        "PackageDetails": PackageDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPackageVersionHistoryResponseTypeDef = TypedDict(
    "GetPackageVersionHistoryResponseTypeDef",
    {
        "PackageID": str,
        "PackageVersionHistoryList": List[PackageVersionHistoryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeReservedInstanceOfferingsResponseTypeDef = TypedDict(
    "DescribeReservedInstanceOfferingsResponseTypeDef",
    {
        "NextToken": str,
        "ReservedInstanceOfferings": List[ReservedInstanceOfferingTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeReservedInstancesResponseTypeDef = TypedDict(
    "DescribeReservedInstancesResponseTypeDef",
    {
        "NextToken": str,
        "ReservedInstances": List[ReservedInstanceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AdvancedSecurityOptionsInputTypeDef = TypedDict(
    "AdvancedSecurityOptionsInputTypeDef",
    {
        "Enabled": NotRequired[bool],
        "InternalUserDatabaseEnabled": NotRequired[bool],
        "MasterUserOptions": NotRequired[MasterUserOptionsTypeDef],
        "SAMLOptions": NotRequired[SAMLOptionsInputTypeDef],
        "AnonymousAuthEnabled": NotRequired[bool],
    },
)
AdvancedSecurityOptionsTypeDef = TypedDict(
    "AdvancedSecurityOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "InternalUserDatabaseEnabled": NotRequired[bool],
        "SAMLOptions": NotRequired[SAMLOptionsOutputTypeDef],
        "AnonymousAuthDisableDate": NotRequired[datetime],
        "AnonymousAuthEnabled": NotRequired[bool],
    },
)
LimitsTypeDef = TypedDict(
    "LimitsTypeDef",
    {
        "StorageTypes": NotRequired[List[StorageTypeTypeDef]],
        "InstanceLimits": NotRequired[InstanceLimitsTypeDef],
        "AdditionalLimits": NotRequired[List[AdditionalLimitTypeDef]],
    },
)
GetUpgradeHistoryResponseTypeDef = TypedDict(
    "GetUpgradeHistoryResponseTypeDef",
    {
        "UpgradeHistories": List[UpgradeHistoryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AcceptInboundConnectionResponseTypeDef = TypedDict(
    "AcceptInboundConnectionResponseTypeDef",
    {
        "Connection": InboundConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteInboundConnectionResponseTypeDef = TypedDict(
    "DeleteInboundConnectionResponseTypeDef",
    {
        "Connection": InboundConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeInboundConnectionsResponseTypeDef = TypedDict(
    "DescribeInboundConnectionsResponseTypeDef",
    {
        "Connections": List[InboundConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RejectInboundConnectionResponseTypeDef = TypedDict(
    "RejectInboundConnectionResponseTypeDef",
    {
        "Connection": InboundConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDomainAutoTunesResponseTypeDef = TypedDict(
    "DescribeDomainAutoTunesResponseTypeDef",
    {
        "AutoTunes": List[AutoTuneTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AutoTuneOptionsStatusTypeDef = TypedDict(
    "AutoTuneOptionsStatusTypeDef",
    {
        "Options": NotRequired[AutoTuneOptionsTypeDef],
        "Status": NotRequired[AutoTuneStatusTypeDef],
    },
)
DeleteOutboundConnectionResponseTypeDef = TypedDict(
    "DeleteOutboundConnectionResponseTypeDef",
    {
        "Connection": OutboundConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeOutboundConnectionsResponseTypeDef = TypedDict(
    "DescribeOutboundConnectionsResponseTypeDef",
    {
        "Connections": List[OutboundConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDataSourcesResponseTypeDef = TypedDict(
    "ListDataSourcesResponseTypeDef",
    {
        "DataSources": List[DataSourceDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OffPeakWindowOptionsStatusTypeDef = TypedDict(
    "OffPeakWindowOptionsStatusTypeDef",
    {
        "Options": NotRequired[OffPeakWindowOptionsTypeDef],
        "Status": NotRequired[OptionStatusTypeDef],
    },
)
CreateDomainRequestRequestTypeDef = TypedDict(
    "CreateDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "EngineVersion": NotRequired[str],
        "ClusterConfig": NotRequired[ClusterConfigTypeDef],
        "EBSOptions": NotRequired[EBSOptionsTypeDef],
        "AccessPolicies": NotRequired[str],
        "IPAddressType": NotRequired[IPAddressTypeType],
        "SnapshotOptions": NotRequired[SnapshotOptionsTypeDef],
        "VPCOptions": NotRequired[VPCOptionsTypeDef],
        "CognitoOptions": NotRequired[CognitoOptionsTypeDef],
        "EncryptionAtRestOptions": NotRequired[EncryptionAtRestOptionsTypeDef],
        "NodeToNodeEncryptionOptions": NotRequired[NodeToNodeEncryptionOptionsTypeDef],
        "AdvancedOptions": NotRequired[Mapping[str, str]],
        "LogPublishingOptions": NotRequired[Mapping[LogTypeType, LogPublishingOptionTypeDef]],
        "DomainEndpointOptions": NotRequired[DomainEndpointOptionsTypeDef],
        "AdvancedSecurityOptions": NotRequired[AdvancedSecurityOptionsInputTypeDef],
        "TagList": NotRequired[Sequence[TagTypeDef]],
        "AutoTuneOptions": NotRequired[AutoTuneOptionsInputTypeDef],
        "OffPeakWindowOptions": NotRequired[OffPeakWindowOptionsTypeDef],
        "SoftwareUpdateOptions": NotRequired[SoftwareUpdateOptionsTypeDef],
    },
)
UpdateDomainConfigRequestRequestTypeDef = TypedDict(
    "UpdateDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
        "ClusterConfig": NotRequired[ClusterConfigTypeDef],
        "EBSOptions": NotRequired[EBSOptionsTypeDef],
        "SnapshotOptions": NotRequired[SnapshotOptionsTypeDef],
        "VPCOptions": NotRequired[VPCOptionsTypeDef],
        "CognitoOptions": NotRequired[CognitoOptionsTypeDef],
        "AdvancedOptions": NotRequired[Mapping[str, str]],
        "AccessPolicies": NotRequired[str],
        "IPAddressType": NotRequired[IPAddressTypeType],
        "LogPublishingOptions": NotRequired[Mapping[LogTypeType, LogPublishingOptionTypeDef]],
        "EncryptionAtRestOptions": NotRequired[EncryptionAtRestOptionsTypeDef],
        "DomainEndpointOptions": NotRequired[DomainEndpointOptionsTypeDef],
        "NodeToNodeEncryptionOptions": NotRequired[NodeToNodeEncryptionOptionsTypeDef],
        "AdvancedSecurityOptions": NotRequired[AdvancedSecurityOptionsInputTypeDef],
        "AutoTuneOptions": NotRequired[AutoTuneOptionsTypeDef],
        "DryRun": NotRequired[bool],
        "DryRunMode": NotRequired[DryRunModeType],
        "OffPeakWindowOptions": NotRequired[OffPeakWindowOptionsTypeDef],
        "SoftwareUpdateOptions": NotRequired[SoftwareUpdateOptionsTypeDef],
    },
)
AdvancedSecurityOptionsStatusTypeDef = TypedDict(
    "AdvancedSecurityOptionsStatusTypeDef",
    {
        "Options": AdvancedSecurityOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
DomainStatusTypeDef = TypedDict(
    "DomainStatusTypeDef",
    {
        "DomainId": str,
        "DomainName": str,
        "ARN": str,
        "ClusterConfig": ClusterConfigTypeDef,
        "Created": NotRequired[bool],
        "Deleted": NotRequired[bool],
        "Endpoint": NotRequired[str],
        "EndpointV2": NotRequired[str],
        "Endpoints": NotRequired[Dict[str, str]],
        "Processing": NotRequired[bool],
        "UpgradeProcessing": NotRequired[bool],
        "EngineVersion": NotRequired[str],
        "EBSOptions": NotRequired[EBSOptionsTypeDef],
        "AccessPolicies": NotRequired[str],
        "IPAddressType": NotRequired[IPAddressTypeType],
        "SnapshotOptions": NotRequired[SnapshotOptionsTypeDef],
        "VPCOptions": NotRequired[VPCDerivedInfoTypeDef],
        "CognitoOptions": NotRequired[CognitoOptionsTypeDef],
        "EncryptionAtRestOptions": NotRequired[EncryptionAtRestOptionsTypeDef],
        "NodeToNodeEncryptionOptions": NotRequired[NodeToNodeEncryptionOptionsTypeDef],
        "AdvancedOptions": NotRequired[Dict[str, str]],
        "LogPublishingOptions": NotRequired[Dict[LogTypeType, LogPublishingOptionTypeDef]],
        "ServiceSoftwareOptions": NotRequired[ServiceSoftwareOptionsTypeDef],
        "DomainEndpointOptions": NotRequired[DomainEndpointOptionsTypeDef],
        "AdvancedSecurityOptions": NotRequired[AdvancedSecurityOptionsTypeDef],
        "AutoTuneOptions": NotRequired[AutoTuneOptionsOutputTypeDef],
        "ChangeProgressDetails": NotRequired[ChangeProgressDetailsTypeDef],
        "OffPeakWindowOptions": NotRequired[OffPeakWindowOptionsTypeDef],
        "SoftwareUpdateOptions": NotRequired[SoftwareUpdateOptionsTypeDef],
        "DomainProcessingStatus": NotRequired[DomainProcessingStatusTypeType],
        "ModifyingProperties": NotRequired[List[ModifyingPropertiesTypeDef]],
    },
)
DescribeInstanceTypeLimitsResponseTypeDef = TypedDict(
    "DescribeInstanceTypeLimitsResponseTypeDef",
    {
        "LimitsByRole": Dict[str, LimitsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DomainConfigTypeDef = TypedDict(
    "DomainConfigTypeDef",
    {
        "EngineVersion": NotRequired[VersionStatusTypeDef],
        "ClusterConfig": NotRequired[ClusterConfigStatusTypeDef],
        "EBSOptions": NotRequired[EBSOptionsStatusTypeDef],
        "AccessPolicies": NotRequired[AccessPoliciesStatusTypeDef],
        "IPAddressType": NotRequired[IPAddressTypeStatusTypeDef],
        "SnapshotOptions": NotRequired[SnapshotOptionsStatusTypeDef],
        "VPCOptions": NotRequired[VPCDerivedInfoStatusTypeDef],
        "CognitoOptions": NotRequired[CognitoOptionsStatusTypeDef],
        "EncryptionAtRestOptions": NotRequired[EncryptionAtRestOptionsStatusTypeDef],
        "NodeToNodeEncryptionOptions": NotRequired[NodeToNodeEncryptionOptionsStatusTypeDef],
        "AdvancedOptions": NotRequired[AdvancedOptionsStatusTypeDef],
        "LogPublishingOptions": NotRequired[LogPublishingOptionsStatusTypeDef],
        "DomainEndpointOptions": NotRequired[DomainEndpointOptionsStatusTypeDef],
        "AdvancedSecurityOptions": NotRequired[AdvancedSecurityOptionsStatusTypeDef],
        "AutoTuneOptions": NotRequired[AutoTuneOptionsStatusTypeDef],
        "ChangeProgressDetails": NotRequired[ChangeProgressDetailsTypeDef],
        "OffPeakWindowOptions": NotRequired[OffPeakWindowOptionsStatusTypeDef],
        "SoftwareUpdateOptions": NotRequired[SoftwareUpdateOptionsStatusTypeDef],
        "ModifyingProperties": NotRequired[List[ModifyingPropertiesTypeDef]],
    },
)
CreateDomainResponseTypeDef = TypedDict(
    "CreateDomainResponseTypeDef",
    {
        "DomainStatus": DomainStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteDomainResponseTypeDef = TypedDict(
    "DeleteDomainResponseTypeDef",
    {
        "DomainStatus": DomainStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDomainResponseTypeDef = TypedDict(
    "DescribeDomainResponseTypeDef",
    {
        "DomainStatus": DomainStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDomainsResponseTypeDef = TypedDict(
    "DescribeDomainsResponseTypeDef",
    {
        "DomainStatusList": List[DomainStatusTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDryRunProgressResponseTypeDef = TypedDict(
    "DescribeDryRunProgressResponseTypeDef",
    {
        "DryRunProgressStatus": DryRunProgressStatusTypeDef,
        "DryRunConfig": DomainStatusTypeDef,
        "DryRunResults": DryRunResultsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDomainConfigResponseTypeDef = TypedDict(
    "DescribeDomainConfigResponseTypeDef",
    {
        "DomainConfig": DomainConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDomainConfigResponseTypeDef = TypedDict(
    "UpdateDomainConfigResponseTypeDef",
    {
        "DomainConfig": DomainConfigTypeDef,
        "DryRunResults": DryRunResultsTypeDef,
        "DryRunProgressStatus": DryRunProgressStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
