"""
Type annotations for es service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_es/type_defs/)

Usage::

    ```python
    from mypy_boto3_es.type_defs import AcceptInboundCrossClusterSearchConnectionRequestRequestTypeDef

    data: AcceptInboundCrossClusterSearchConnectionRequestRequestTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    AutoTuneDesiredStateType,
    AutoTuneStateType,
    ConfigChangeStatusType,
    DeploymentStatusType,
    DescribePackagesFilterNameType,
    DomainPackageStatusType,
    DomainProcessingStatusTypeType,
    EngineTypeType,
    ESPartitionInstanceTypeType,
    ESWarmPartitionInstanceTypeType,
    InboundCrossClusterSearchConnectionStatusCodeType,
    InitiatedByType,
    LogTypeType,
    OptionStateType,
    OutboundCrossClusterSearchConnectionStatusCodeType,
    OverallChangeStatusType,
    PackageStatusType,
    PrincipalTypeType,
    PropertyValueTypeType,
    ReservedElasticsearchInstancePaymentOptionType,
    RollbackOnDisableType,
    ScheduledAutoTuneActionTypeType,
    ScheduledAutoTuneSeverityTypeType,
    TLSSecurityPolicyType,
    UpgradeStatusType,
    UpgradeStepType,
    VolumeTypeType,
    VpcEndpointErrorCodeType,
    VpcEndpointStatusType,
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
    "AcceptInboundCrossClusterSearchConnectionRequestRequestTypeDef",
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
    "CancelDomainConfigChangeRequestRequestTypeDef",
    "CancelledChangePropertyTypeDef",
    "CancelElasticsearchServiceSoftwareUpdateRequestRequestTypeDef",
    "ServiceSoftwareOptionsTypeDef",
    "ChangeProgressDetailsTypeDef",
    "ChangeProgressStageTypeDef",
    "CognitoOptionsTypeDef",
    "ColdStorageOptionsTypeDef",
    "CompatibleVersionsMapTypeDef",
    "DomainEndpointOptionsTypeDef",
    "EBSOptionsTypeDef",
    "EncryptionAtRestOptionsTypeDef",
    "LogPublishingOptionTypeDef",
    "NodeToNodeEncryptionOptionsTypeDef",
    "SnapshotOptionsTypeDef",
    "VPCOptionsTypeDef",
    "DomainInformationTypeDef",
    "OutboundCrossClusterSearchConnectionStatusTypeDef",
    "PackageSourceTypeDef",
    "DeleteElasticsearchDomainRequestRequestTypeDef",
    "DeleteInboundCrossClusterSearchConnectionRequestRequestTypeDef",
    "DeleteOutboundCrossClusterSearchConnectionRequestRequestTypeDef",
    "DeletePackageRequestRequestTypeDef",
    "DeleteVpcEndpointRequestRequestTypeDef",
    "VpcEndpointSummaryTypeDef",
    "DescribeDomainAutoTunesRequestRequestTypeDef",
    "DescribeDomainChangeProgressRequestRequestTypeDef",
    "DescribeElasticsearchDomainConfigRequestRequestTypeDef",
    "DescribeElasticsearchDomainRequestRequestTypeDef",
    "DescribeElasticsearchDomainsRequestRequestTypeDef",
    "DescribeElasticsearchInstanceTypeLimitsRequestRequestTypeDef",
    "FilterTypeDef",
    "DescribePackagesFilterTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeReservedElasticsearchInstanceOfferingsRequestRequestTypeDef",
    "DescribeReservedElasticsearchInstancesRequestRequestTypeDef",
    "DescribeVpcEndpointsRequestRequestTypeDef",
    "VpcEndpointErrorTypeDef",
    "DissociatePackageRequestRequestTypeDef",
    "DomainInfoTypeDef",
    "ErrorDetailsTypeDef",
    "DryRunResultsTypeDef",
    "ZoneAwarenessConfigTypeDef",
    "ModifyingPropertiesTypeDef",
    "VPCDerivedInfoTypeDef",
    "GetCompatibleElasticsearchVersionsRequestRequestTypeDef",
    "GetPackageVersionHistoryRequestRequestTypeDef",
    "PackageVersionHistoryTypeDef",
    "GetUpgradeHistoryRequestRequestTypeDef",
    "GetUpgradeStatusRequestRequestTypeDef",
    "InboundCrossClusterSearchConnectionStatusTypeDef",
    "InstanceCountLimitsTypeDef",
    "ListDomainNamesRequestRequestTypeDef",
    "ListDomainsForPackageRequestRequestTypeDef",
    "ListElasticsearchInstanceTypesRequestRequestTypeDef",
    "ListElasticsearchVersionsRequestRequestTypeDef",
    "ListPackagesForDomainRequestRequestTypeDef",
    "ListTagsRequestRequestTypeDef",
    "ListVpcEndpointAccessRequestRequestTypeDef",
    "ListVpcEndpointsForDomainRequestRequestTypeDef",
    "ListVpcEndpointsRequestRequestTypeDef",
    "PurchaseReservedElasticsearchInstanceOfferingRequestRequestTypeDef",
    "RecurringChargeTypeDef",
    "RejectInboundCrossClusterSearchConnectionRequestRequestTypeDef",
    "RemoveTagsRequestRequestTypeDef",
    "RevokeVpcEndpointAccessRequestRequestTypeDef",
    "SAMLIdpTypeDef",
    "StartElasticsearchServiceSoftwareUpdateRequestRequestTypeDef",
    "StorageTypeLimitTypeDef",
    "UpgradeElasticsearchDomainRequestRequestTypeDef",
    "UpgradeStepItemTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetUpgradeStatusResponseTypeDef",
    "ListElasticsearchInstanceTypesResponseTypeDef",
    "ListElasticsearchVersionsResponseTypeDef",
    "PurchaseReservedElasticsearchInstanceOfferingResponseTypeDef",
    "AccessPoliciesStatusTypeDef",
    "AdvancedOptionsStatusTypeDef",
    "ElasticsearchVersionStatusTypeDef",
    "AddTagsRequestRequestTypeDef",
    "ListTagsResponseTypeDef",
    "AuthorizeVpcEndpointAccessResponseTypeDef",
    "ListVpcEndpointAccessResponseTypeDef",
    "AutoTuneDetailsTypeDef",
    "AutoTuneMaintenanceScheduleTypeDef",
    "CancelDomainConfigChangeResponseTypeDef",
    "CancelElasticsearchServiceSoftwareUpdateResponseTypeDef",
    "StartElasticsearchServiceSoftwareUpdateResponseTypeDef",
    "UpgradeElasticsearchDomainResponseTypeDef",
    "ChangeProgressStatusDetailsTypeDef",
    "CognitoOptionsStatusTypeDef",
    "GetCompatibleElasticsearchVersionsResponseTypeDef",
    "DomainEndpointOptionsStatusTypeDef",
    "EBSOptionsStatusTypeDef",
    "EncryptionAtRestOptionsStatusTypeDef",
    "LogPublishingOptionsStatusTypeDef",
    "NodeToNodeEncryptionOptionsStatusTypeDef",
    "SnapshotOptionsStatusTypeDef",
    "CreateVpcEndpointRequestRequestTypeDef",
    "UpdateVpcEndpointRequestRequestTypeDef",
    "CreateOutboundCrossClusterSearchConnectionRequestRequestTypeDef",
    "CreateOutboundCrossClusterSearchConnectionResponseTypeDef",
    "OutboundCrossClusterSearchConnectionTypeDef",
    "CreatePackageRequestRequestTypeDef",
    "UpdatePackageRequestRequestTypeDef",
    "DeleteVpcEndpointResponseTypeDef",
    "ListVpcEndpointsForDomainResponseTypeDef",
    "ListVpcEndpointsResponseTypeDef",
    "DescribeInboundCrossClusterSearchConnectionsRequestRequestTypeDef",
    "DescribeOutboundCrossClusterSearchConnectionsRequestRequestTypeDef",
    "DescribePackagesRequestRequestTypeDef",
    "DescribeReservedElasticsearchInstanceOfferingsRequestDescribeReservedElasticsearchInstanceOfferingsPaginateTypeDef",
    "DescribeReservedElasticsearchInstancesRequestDescribeReservedElasticsearchInstancesPaginateTypeDef",
    "GetUpgradeHistoryRequestGetUpgradeHistoryPaginateTypeDef",
    "ListElasticsearchInstanceTypesRequestListElasticsearchInstanceTypesPaginateTypeDef",
    "ListElasticsearchVersionsRequestListElasticsearchVersionsPaginateTypeDef",
    "ListDomainNamesResponseTypeDef",
    "DomainPackageDetailsTypeDef",
    "PackageDetailsTypeDef",
    "ElasticsearchClusterConfigTypeDef",
    "VPCDerivedInfoStatusTypeDef",
    "VpcEndpointTypeDef",
    "GetPackageVersionHistoryResponseTypeDef",
    "InboundCrossClusterSearchConnectionTypeDef",
    "InstanceLimitsTypeDef",
    "ReservedElasticsearchInstanceOfferingTypeDef",
    "ReservedElasticsearchInstanceTypeDef",
    "SAMLOptionsInputTypeDef",
    "SAMLOptionsOutputTypeDef",
    "StorageTypeTypeDef",
    "UpgradeHistoryTypeDef",
    "AutoTuneTypeDef",
    "AutoTuneOptionsInputTypeDef",
    "AutoTuneOptionsTypeDef",
    "DescribeDomainChangeProgressResponseTypeDef",
    "DeleteOutboundCrossClusterSearchConnectionResponseTypeDef",
    "DescribeOutboundCrossClusterSearchConnectionsResponseTypeDef",
    "AssociatePackageResponseTypeDef",
    "DissociatePackageResponseTypeDef",
    "ListDomainsForPackageResponseTypeDef",
    "ListPackagesForDomainResponseTypeDef",
    "CreatePackageResponseTypeDef",
    "DeletePackageResponseTypeDef",
    "DescribePackagesResponseTypeDef",
    "UpdatePackageResponseTypeDef",
    "ElasticsearchClusterConfigStatusTypeDef",
    "CreateVpcEndpointResponseTypeDef",
    "DescribeVpcEndpointsResponseTypeDef",
    "UpdateVpcEndpointResponseTypeDef",
    "AcceptInboundCrossClusterSearchConnectionResponseTypeDef",
    "DeleteInboundCrossClusterSearchConnectionResponseTypeDef",
    "DescribeInboundCrossClusterSearchConnectionsResponseTypeDef",
    "RejectInboundCrossClusterSearchConnectionResponseTypeDef",
    "DescribeReservedElasticsearchInstanceOfferingsResponseTypeDef",
    "DescribeReservedElasticsearchInstancesResponseTypeDef",
    "AdvancedSecurityOptionsInputTypeDef",
    "AdvancedSecurityOptionsTypeDef",
    "LimitsTypeDef",
    "GetUpgradeHistoryResponseTypeDef",
    "DescribeDomainAutoTunesResponseTypeDef",
    "AutoTuneOptionsStatusTypeDef",
    "CreateElasticsearchDomainRequestRequestTypeDef",
    "UpdateElasticsearchDomainConfigRequestRequestTypeDef",
    "AdvancedSecurityOptionsStatusTypeDef",
    "ElasticsearchDomainStatusTypeDef",
    "DescribeElasticsearchInstanceTypeLimitsResponseTypeDef",
    "ElasticsearchDomainConfigTypeDef",
    "CreateElasticsearchDomainResponseTypeDef",
    "DeleteElasticsearchDomainResponseTypeDef",
    "DescribeElasticsearchDomainResponseTypeDef",
    "DescribeElasticsearchDomainsResponseTypeDef",
    "DescribeElasticsearchDomainConfigResponseTypeDef",
    "UpdateElasticsearchDomainConfigResponseTypeDef",
)

AcceptInboundCrossClusterSearchConnectionRequestRequestTypeDef = TypedDict(
    "AcceptInboundCrossClusterSearchConnectionRequestRequestTypeDef",
    {
        "CrossClusterSearchConnectionId": str,
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
CancelElasticsearchServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "CancelElasticsearchServiceSoftwareUpdateRequestRequestTypeDef",
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
        "StartTime": NotRequired[datetime],
        "LastUpdatedTime": NotRequired[datetime],
        "InitiatedBy": NotRequired[InitiatedByType],
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
CognitoOptionsTypeDef = TypedDict(
    "CognitoOptionsTypeDef",
    {
        "Enabled": NotRequired[bool],
        "UserPoolId": NotRequired[str],
        "IdentityPoolId": NotRequired[str],
        "RoleArn": NotRequired[str],
    },
)
ColdStorageOptionsTypeDef = TypedDict(
    "ColdStorageOptionsTypeDef",
    {
        "Enabled": bool,
    },
)
CompatibleVersionsMapTypeDef = TypedDict(
    "CompatibleVersionsMapTypeDef",
    {
        "SourceVersion": NotRequired[str],
        "TargetVersions": NotRequired[List[str]],
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
VPCOptionsTypeDef = TypedDict(
    "VPCOptionsTypeDef",
    {
        "SubnetIds": NotRequired[Sequence[str]],
        "SecurityGroupIds": NotRequired[Sequence[str]],
    },
)
DomainInformationTypeDef = TypedDict(
    "DomainInformationTypeDef",
    {
        "DomainName": str,
        "OwnerId": NotRequired[str],
        "Region": NotRequired[str],
    },
)
OutboundCrossClusterSearchConnectionStatusTypeDef = TypedDict(
    "OutboundCrossClusterSearchConnectionStatusTypeDef",
    {
        "StatusCode": NotRequired[OutboundCrossClusterSearchConnectionStatusCodeType],
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
DeleteElasticsearchDomainRequestRequestTypeDef = TypedDict(
    "DeleteElasticsearchDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DeleteInboundCrossClusterSearchConnectionRequestRequestTypeDef = TypedDict(
    "DeleteInboundCrossClusterSearchConnectionRequestRequestTypeDef",
    {
        "CrossClusterSearchConnectionId": str,
    },
)
DeleteOutboundCrossClusterSearchConnectionRequestRequestTypeDef = TypedDict(
    "DeleteOutboundCrossClusterSearchConnectionRequestRequestTypeDef",
    {
        "CrossClusterSearchConnectionId": str,
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
DescribeElasticsearchDomainConfigRequestRequestTypeDef = TypedDict(
    "DescribeElasticsearchDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DescribeElasticsearchDomainRequestRequestTypeDef = TypedDict(
    "DescribeElasticsearchDomainRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
DescribeElasticsearchDomainsRequestRequestTypeDef = TypedDict(
    "DescribeElasticsearchDomainsRequestRequestTypeDef",
    {
        "DomainNames": Sequence[str],
    },
)
DescribeElasticsearchInstanceTypeLimitsRequestRequestTypeDef = TypedDict(
    "DescribeElasticsearchInstanceTypeLimitsRequestRequestTypeDef",
    {
        "InstanceType": ESPartitionInstanceTypeType,
        "ElasticsearchVersion": str,
        "DomainName": NotRequired[str],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Name": NotRequired[str],
        "Values": NotRequired[Sequence[str]],
    },
)
DescribePackagesFilterTypeDef = TypedDict(
    "DescribePackagesFilterTypeDef",
    {
        "Name": NotRequired[DescribePackagesFilterNameType],
        "Value": NotRequired[Sequence[str]],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
DescribeReservedElasticsearchInstanceOfferingsRequestRequestTypeDef = TypedDict(
    "DescribeReservedElasticsearchInstanceOfferingsRequestRequestTypeDef",
    {
        "ReservedElasticsearchInstanceOfferingId": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeReservedElasticsearchInstancesRequestRequestTypeDef = TypedDict(
    "DescribeReservedElasticsearchInstancesRequestRequestTypeDef",
    {
        "ReservedElasticsearchInstanceId": NotRequired[str],
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
DomainInfoTypeDef = TypedDict(
    "DomainInfoTypeDef",
    {
        "DomainName": NotRequired[str],
        "EngineType": NotRequired[EngineTypeType],
    },
)
ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "ErrorType": NotRequired[str],
        "ErrorMessage": NotRequired[str],
    },
)
DryRunResultsTypeDef = TypedDict(
    "DryRunResultsTypeDef",
    {
        "DeploymentType": NotRequired[str],
        "Message": NotRequired[str],
    },
)
ZoneAwarenessConfigTypeDef = TypedDict(
    "ZoneAwarenessConfigTypeDef",
    {
        "AvailabilityZoneCount": NotRequired[int],
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
VPCDerivedInfoTypeDef = TypedDict(
    "VPCDerivedInfoTypeDef",
    {
        "VPCId": NotRequired[str],
        "SubnetIds": NotRequired[List[str]],
        "AvailabilityZones": NotRequired[List[str]],
        "SecurityGroupIds": NotRequired[List[str]],
    },
)
GetCompatibleElasticsearchVersionsRequestRequestTypeDef = TypedDict(
    "GetCompatibleElasticsearchVersionsRequestRequestTypeDef",
    {
        "DomainName": NotRequired[str],
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
PackageVersionHistoryTypeDef = TypedDict(
    "PackageVersionHistoryTypeDef",
    {
        "PackageVersion": NotRequired[str],
        "CommitMessage": NotRequired[str],
        "CreatedAt": NotRequired[datetime],
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
InboundCrossClusterSearchConnectionStatusTypeDef = TypedDict(
    "InboundCrossClusterSearchConnectionStatusTypeDef",
    {
        "StatusCode": NotRequired[InboundCrossClusterSearchConnectionStatusCodeType],
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
ListElasticsearchInstanceTypesRequestRequestTypeDef = TypedDict(
    "ListElasticsearchInstanceTypesRequestRequestTypeDef",
    {
        "ElasticsearchVersion": str,
        "DomainName": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListElasticsearchVersionsRequestRequestTypeDef = TypedDict(
    "ListElasticsearchVersionsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
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
ListTagsRequestRequestTypeDef = TypedDict(
    "ListTagsRequestRequestTypeDef",
    {
        "ARN": str,
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
PurchaseReservedElasticsearchInstanceOfferingRequestRequestTypeDef = TypedDict(
    "PurchaseReservedElasticsearchInstanceOfferingRequestRequestTypeDef",
    {
        "ReservedElasticsearchInstanceOfferingId": str,
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
RejectInboundCrossClusterSearchConnectionRequestRequestTypeDef = TypedDict(
    "RejectInboundCrossClusterSearchConnectionRequestRequestTypeDef",
    {
        "CrossClusterSearchConnectionId": str,
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
StartElasticsearchServiceSoftwareUpdateRequestRequestTypeDef = TypedDict(
    "StartElasticsearchServiceSoftwareUpdateRequestRequestTypeDef",
    {
        "DomainName": str,
    },
)
StorageTypeLimitTypeDef = TypedDict(
    "StorageTypeLimitTypeDef",
    {
        "LimitName": NotRequired[str],
        "LimitValues": NotRequired[List[str]],
    },
)
UpgradeElasticsearchDomainRequestRequestTypeDef = TypedDict(
    "UpgradeElasticsearchDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "TargetVersion": str,
        "PerformCheckOnly": NotRequired[bool],
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
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
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
ListElasticsearchInstanceTypesResponseTypeDef = TypedDict(
    "ListElasticsearchInstanceTypesResponseTypeDef",
    {
        "ElasticsearchInstanceTypes": List[ESPartitionInstanceTypeType],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListElasticsearchVersionsResponseTypeDef = TypedDict(
    "ListElasticsearchVersionsResponseTypeDef",
    {
        "ElasticsearchVersions": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PurchaseReservedElasticsearchInstanceOfferingResponseTypeDef = TypedDict(
    "PurchaseReservedElasticsearchInstanceOfferingResponseTypeDef",
    {
        "ReservedElasticsearchInstanceId": str,
        "ReservationName": str,
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
ElasticsearchVersionStatusTypeDef = TypedDict(
    "ElasticsearchVersionStatusTypeDef",
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
CancelDomainConfigChangeResponseTypeDef = TypedDict(
    "CancelDomainConfigChangeResponseTypeDef",
    {
        "DryRun": bool,
        "CancelledChangeIds": List[str],
        "CancelledChangeProperties": List[CancelledChangePropertyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CancelElasticsearchServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "CancelElasticsearchServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartElasticsearchServiceSoftwareUpdateResponseTypeDef = TypedDict(
    "StartElasticsearchServiceSoftwareUpdateResponseTypeDef",
    {
        "ServiceSoftwareOptions": ServiceSoftwareOptionsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpgradeElasticsearchDomainResponseTypeDef = TypedDict(
    "UpgradeElasticsearchDomainResponseTypeDef",
    {
        "DomainName": str,
        "TargetVersion": str,
        "PerformCheckOnly": bool,
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
        "ConfigChangeStatus": NotRequired[ConfigChangeStatusType],
        "LastUpdatedTime": NotRequired[datetime],
        "InitiatedBy": NotRequired[InitiatedByType],
    },
)
CognitoOptionsStatusTypeDef = TypedDict(
    "CognitoOptionsStatusTypeDef",
    {
        "Options": CognitoOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
GetCompatibleElasticsearchVersionsResponseTypeDef = TypedDict(
    "GetCompatibleElasticsearchVersionsResponseTypeDef",
    {
        "CompatibleElasticsearchVersions": List[CompatibleVersionsMapTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
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
CreateOutboundCrossClusterSearchConnectionRequestRequestTypeDef = TypedDict(
    "CreateOutboundCrossClusterSearchConnectionRequestRequestTypeDef",
    {
        "SourceDomainInfo": DomainInformationTypeDef,
        "DestinationDomainInfo": DomainInformationTypeDef,
        "ConnectionAlias": str,
    },
)
CreateOutboundCrossClusterSearchConnectionResponseTypeDef = TypedDict(
    "CreateOutboundCrossClusterSearchConnectionResponseTypeDef",
    {
        "SourceDomainInfo": DomainInformationTypeDef,
        "DestinationDomainInfo": DomainInformationTypeDef,
        "ConnectionAlias": str,
        "ConnectionStatus": OutboundCrossClusterSearchConnectionStatusTypeDef,
        "CrossClusterSearchConnectionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OutboundCrossClusterSearchConnectionTypeDef = TypedDict(
    "OutboundCrossClusterSearchConnectionTypeDef",
    {
        "SourceDomainInfo": NotRequired[DomainInformationTypeDef],
        "DestinationDomainInfo": NotRequired[DomainInformationTypeDef],
        "CrossClusterSearchConnectionId": NotRequired[str],
        "ConnectionAlias": NotRequired[str],
        "ConnectionStatus": NotRequired[OutboundCrossClusterSearchConnectionStatusTypeDef],
    },
)
CreatePackageRequestRequestTypeDef = TypedDict(
    "CreatePackageRequestRequestTypeDef",
    {
        "PackageName": str,
        "PackageType": Literal["TXT-DICTIONARY"],
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
DescribeInboundCrossClusterSearchConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeInboundCrossClusterSearchConnectionsRequestRequestTypeDef",
    {
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeOutboundCrossClusterSearchConnectionsRequestRequestTypeDef = TypedDict(
    "DescribeOutboundCrossClusterSearchConnectionsRequestRequestTypeDef",
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
DescribeReservedElasticsearchInstanceOfferingsRequestDescribeReservedElasticsearchInstanceOfferingsPaginateTypeDef = TypedDict(
    "DescribeReservedElasticsearchInstanceOfferingsRequestDescribeReservedElasticsearchInstanceOfferingsPaginateTypeDef",
    {
        "ReservedElasticsearchInstanceOfferingId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeReservedElasticsearchInstancesRequestDescribeReservedElasticsearchInstancesPaginateTypeDef = TypedDict(
    "DescribeReservedElasticsearchInstancesRequestDescribeReservedElasticsearchInstancesPaginateTypeDef",
    {
        "ReservedElasticsearchInstanceId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetUpgradeHistoryRequestGetUpgradeHistoryPaginateTypeDef = TypedDict(
    "GetUpgradeHistoryRequestGetUpgradeHistoryPaginateTypeDef",
    {
        "DomainName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListElasticsearchInstanceTypesRequestListElasticsearchInstanceTypesPaginateTypeDef = TypedDict(
    "ListElasticsearchInstanceTypesRequestListElasticsearchInstanceTypesPaginateTypeDef",
    {
        "ElasticsearchVersion": str,
        "DomainName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListElasticsearchVersionsRequestListElasticsearchVersionsPaginateTypeDef = TypedDict(
    "ListElasticsearchVersionsRequestListElasticsearchVersionsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDomainNamesResponseTypeDef = TypedDict(
    "ListDomainNamesResponseTypeDef",
    {
        "DomainNames": List[DomainInfoTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DomainPackageDetailsTypeDef = TypedDict(
    "DomainPackageDetailsTypeDef",
    {
        "PackageID": NotRequired[str],
        "PackageName": NotRequired[str],
        "PackageType": NotRequired[Literal["TXT-DICTIONARY"]],
        "LastUpdated": NotRequired[datetime],
        "DomainName": NotRequired[str],
        "DomainPackageStatus": NotRequired[DomainPackageStatusType],
        "PackageVersion": NotRequired[str],
        "ReferencePath": NotRequired[str],
        "ErrorDetails": NotRequired[ErrorDetailsTypeDef],
    },
)
PackageDetailsTypeDef = TypedDict(
    "PackageDetailsTypeDef",
    {
        "PackageID": NotRequired[str],
        "PackageName": NotRequired[str],
        "PackageType": NotRequired[Literal["TXT-DICTIONARY"]],
        "PackageDescription": NotRequired[str],
        "PackageStatus": NotRequired[PackageStatusType],
        "CreatedAt": NotRequired[datetime],
        "LastUpdatedAt": NotRequired[datetime],
        "AvailablePackageVersion": NotRequired[str],
        "ErrorDetails": NotRequired[ErrorDetailsTypeDef],
    },
)
ElasticsearchClusterConfigTypeDef = TypedDict(
    "ElasticsearchClusterConfigTypeDef",
    {
        "InstanceType": NotRequired[ESPartitionInstanceTypeType],
        "InstanceCount": NotRequired[int],
        "DedicatedMasterEnabled": NotRequired[bool],
        "ZoneAwarenessEnabled": NotRequired[bool],
        "ZoneAwarenessConfig": NotRequired[ZoneAwarenessConfigTypeDef],
        "DedicatedMasterType": NotRequired[ESPartitionInstanceTypeType],
        "DedicatedMasterCount": NotRequired[int],
        "WarmEnabled": NotRequired[bool],
        "WarmType": NotRequired[ESWarmPartitionInstanceTypeType],
        "WarmCount": NotRequired[int],
        "ColdStorageOptions": NotRequired[ColdStorageOptionsTypeDef],
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
GetPackageVersionHistoryResponseTypeDef = TypedDict(
    "GetPackageVersionHistoryResponseTypeDef",
    {
        "PackageID": str,
        "PackageVersionHistoryList": List[PackageVersionHistoryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InboundCrossClusterSearchConnectionTypeDef = TypedDict(
    "InboundCrossClusterSearchConnectionTypeDef",
    {
        "SourceDomainInfo": NotRequired[DomainInformationTypeDef],
        "DestinationDomainInfo": NotRequired[DomainInformationTypeDef],
        "CrossClusterSearchConnectionId": NotRequired[str],
        "ConnectionStatus": NotRequired[InboundCrossClusterSearchConnectionStatusTypeDef],
    },
)
InstanceLimitsTypeDef = TypedDict(
    "InstanceLimitsTypeDef",
    {
        "InstanceCountLimits": NotRequired[InstanceCountLimitsTypeDef],
    },
)
ReservedElasticsearchInstanceOfferingTypeDef = TypedDict(
    "ReservedElasticsearchInstanceOfferingTypeDef",
    {
        "ReservedElasticsearchInstanceOfferingId": NotRequired[str],
        "ElasticsearchInstanceType": NotRequired[ESPartitionInstanceTypeType],
        "Duration": NotRequired[int],
        "FixedPrice": NotRequired[float],
        "UsagePrice": NotRequired[float],
        "CurrencyCode": NotRequired[str],
        "PaymentOption": NotRequired[ReservedElasticsearchInstancePaymentOptionType],
        "RecurringCharges": NotRequired[List[RecurringChargeTypeDef]],
    },
)
ReservedElasticsearchInstanceTypeDef = TypedDict(
    "ReservedElasticsearchInstanceTypeDef",
    {
        "ReservationName": NotRequired[str],
        "ReservedElasticsearchInstanceId": NotRequired[str],
        "ReservedElasticsearchInstanceOfferingId": NotRequired[str],
        "ElasticsearchInstanceType": NotRequired[ESPartitionInstanceTypeType],
        "StartTime": NotRequired[datetime],
        "Duration": NotRequired[int],
        "FixedPrice": NotRequired[float],
        "UsagePrice": NotRequired[float],
        "CurrencyCode": NotRequired[str],
        "ElasticsearchInstanceCount": NotRequired[int],
        "State": NotRequired[str],
        "PaymentOption": NotRequired[ReservedElasticsearchInstancePaymentOptionType],
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
    },
)
AutoTuneOptionsTypeDef = TypedDict(
    "AutoTuneOptionsTypeDef",
    {
        "DesiredState": NotRequired[AutoTuneDesiredStateType],
        "RollbackOnDisable": NotRequired[RollbackOnDisableType],
        "MaintenanceSchedules": NotRequired[List[AutoTuneMaintenanceScheduleTypeDef]],
    },
)
DescribeDomainChangeProgressResponseTypeDef = TypedDict(
    "DescribeDomainChangeProgressResponseTypeDef",
    {
        "ChangeProgressStatus": ChangeProgressStatusDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteOutboundCrossClusterSearchConnectionResponseTypeDef = TypedDict(
    "DeleteOutboundCrossClusterSearchConnectionResponseTypeDef",
    {
        "CrossClusterSearchConnection": OutboundCrossClusterSearchConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeOutboundCrossClusterSearchConnectionsResponseTypeDef = TypedDict(
    "DescribeOutboundCrossClusterSearchConnectionsResponseTypeDef",
    {
        "CrossClusterSearchConnections": List[OutboundCrossClusterSearchConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
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
ElasticsearchClusterConfigStatusTypeDef = TypedDict(
    "ElasticsearchClusterConfigStatusTypeDef",
    {
        "Options": ElasticsearchClusterConfigTypeDef,
        "Status": OptionStatusTypeDef,
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
AcceptInboundCrossClusterSearchConnectionResponseTypeDef = TypedDict(
    "AcceptInboundCrossClusterSearchConnectionResponseTypeDef",
    {
        "CrossClusterSearchConnection": InboundCrossClusterSearchConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteInboundCrossClusterSearchConnectionResponseTypeDef = TypedDict(
    "DeleteInboundCrossClusterSearchConnectionResponseTypeDef",
    {
        "CrossClusterSearchConnection": InboundCrossClusterSearchConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeInboundCrossClusterSearchConnectionsResponseTypeDef = TypedDict(
    "DescribeInboundCrossClusterSearchConnectionsResponseTypeDef",
    {
        "CrossClusterSearchConnections": List[InboundCrossClusterSearchConnectionTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RejectInboundCrossClusterSearchConnectionResponseTypeDef = TypedDict(
    "RejectInboundCrossClusterSearchConnectionResponseTypeDef",
    {
        "CrossClusterSearchConnection": InboundCrossClusterSearchConnectionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeReservedElasticsearchInstanceOfferingsResponseTypeDef = TypedDict(
    "DescribeReservedElasticsearchInstanceOfferingsResponseTypeDef",
    {
        "NextToken": str,
        "ReservedElasticsearchInstanceOfferings": List[
            ReservedElasticsearchInstanceOfferingTypeDef
        ],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeReservedElasticsearchInstancesResponseTypeDef = TypedDict(
    "DescribeReservedElasticsearchInstancesResponseTypeDef",
    {
        "NextToken": str,
        "ReservedElasticsearchInstances": List[ReservedElasticsearchInstanceTypeDef],
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
CreateElasticsearchDomainRequestRequestTypeDef = TypedDict(
    "CreateElasticsearchDomainRequestRequestTypeDef",
    {
        "DomainName": str,
        "ElasticsearchVersion": NotRequired[str],
        "ElasticsearchClusterConfig": NotRequired[ElasticsearchClusterConfigTypeDef],
        "EBSOptions": NotRequired[EBSOptionsTypeDef],
        "AccessPolicies": NotRequired[str],
        "SnapshotOptions": NotRequired[SnapshotOptionsTypeDef],
        "VPCOptions": NotRequired[VPCOptionsTypeDef],
        "CognitoOptions": NotRequired[CognitoOptionsTypeDef],
        "EncryptionAtRestOptions": NotRequired[EncryptionAtRestOptionsTypeDef],
        "NodeToNodeEncryptionOptions": NotRequired[NodeToNodeEncryptionOptionsTypeDef],
        "AdvancedOptions": NotRequired[Mapping[str, str]],
        "LogPublishingOptions": NotRequired[Mapping[LogTypeType, LogPublishingOptionTypeDef]],
        "DomainEndpointOptions": NotRequired[DomainEndpointOptionsTypeDef],
        "AdvancedSecurityOptions": NotRequired[AdvancedSecurityOptionsInputTypeDef],
        "AutoTuneOptions": NotRequired[AutoTuneOptionsInputTypeDef],
        "TagList": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateElasticsearchDomainConfigRequestRequestTypeDef = TypedDict(
    "UpdateElasticsearchDomainConfigRequestRequestTypeDef",
    {
        "DomainName": str,
        "ElasticsearchClusterConfig": NotRequired[ElasticsearchClusterConfigTypeDef],
        "EBSOptions": NotRequired[EBSOptionsTypeDef],
        "SnapshotOptions": NotRequired[SnapshotOptionsTypeDef],
        "VPCOptions": NotRequired[VPCOptionsTypeDef],
        "CognitoOptions": NotRequired[CognitoOptionsTypeDef],
        "AdvancedOptions": NotRequired[Mapping[str, str]],
        "AccessPolicies": NotRequired[str],
        "LogPublishingOptions": NotRequired[Mapping[LogTypeType, LogPublishingOptionTypeDef]],
        "DomainEndpointOptions": NotRequired[DomainEndpointOptionsTypeDef],
        "AdvancedSecurityOptions": NotRequired[AdvancedSecurityOptionsInputTypeDef],
        "NodeToNodeEncryptionOptions": NotRequired[NodeToNodeEncryptionOptionsTypeDef],
        "EncryptionAtRestOptions": NotRequired[EncryptionAtRestOptionsTypeDef],
        "AutoTuneOptions": NotRequired[AutoTuneOptionsTypeDef],
        "DryRun": NotRequired[bool],
    },
)
AdvancedSecurityOptionsStatusTypeDef = TypedDict(
    "AdvancedSecurityOptionsStatusTypeDef",
    {
        "Options": AdvancedSecurityOptionsTypeDef,
        "Status": OptionStatusTypeDef,
    },
)
ElasticsearchDomainStatusTypeDef = TypedDict(
    "ElasticsearchDomainStatusTypeDef",
    {
        "DomainId": str,
        "DomainName": str,
        "ARN": str,
        "ElasticsearchClusterConfig": ElasticsearchClusterConfigTypeDef,
        "Created": NotRequired[bool],
        "Deleted": NotRequired[bool],
        "Endpoint": NotRequired[str],
        "Endpoints": NotRequired[Dict[str, str]],
        "Processing": NotRequired[bool],
        "UpgradeProcessing": NotRequired[bool],
        "ElasticsearchVersion": NotRequired[str],
        "EBSOptions": NotRequired[EBSOptionsTypeDef],
        "AccessPolicies": NotRequired[str],
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
        "DomainProcessingStatus": NotRequired[DomainProcessingStatusTypeType],
        "ModifyingProperties": NotRequired[List[ModifyingPropertiesTypeDef]],
    },
)
DescribeElasticsearchInstanceTypeLimitsResponseTypeDef = TypedDict(
    "DescribeElasticsearchInstanceTypeLimitsResponseTypeDef",
    {
        "LimitsByRole": Dict[str, LimitsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ElasticsearchDomainConfigTypeDef = TypedDict(
    "ElasticsearchDomainConfigTypeDef",
    {
        "ElasticsearchVersion": NotRequired[ElasticsearchVersionStatusTypeDef],
        "ElasticsearchClusterConfig": NotRequired[ElasticsearchClusterConfigStatusTypeDef],
        "EBSOptions": NotRequired[EBSOptionsStatusTypeDef],
        "AccessPolicies": NotRequired[AccessPoliciesStatusTypeDef],
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
        "ModifyingProperties": NotRequired[List[ModifyingPropertiesTypeDef]],
    },
)
CreateElasticsearchDomainResponseTypeDef = TypedDict(
    "CreateElasticsearchDomainResponseTypeDef",
    {
        "DomainStatus": ElasticsearchDomainStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteElasticsearchDomainResponseTypeDef = TypedDict(
    "DeleteElasticsearchDomainResponseTypeDef",
    {
        "DomainStatus": ElasticsearchDomainStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeElasticsearchDomainResponseTypeDef = TypedDict(
    "DescribeElasticsearchDomainResponseTypeDef",
    {
        "DomainStatus": ElasticsearchDomainStatusTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeElasticsearchDomainsResponseTypeDef = TypedDict(
    "DescribeElasticsearchDomainsResponseTypeDef",
    {
        "DomainStatusList": List[ElasticsearchDomainStatusTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeElasticsearchDomainConfigResponseTypeDef = TypedDict(
    "DescribeElasticsearchDomainConfigResponseTypeDef",
    {
        "DomainConfig": ElasticsearchDomainConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateElasticsearchDomainConfigResponseTypeDef = TypedDict(
    "UpdateElasticsearchDomainConfigResponseTypeDef",
    {
        "DomainConfig": ElasticsearchDomainConfigTypeDef,
        "DryRunResults": DryRunResultsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
