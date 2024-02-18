"""
Type annotations for datasync service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_datasync/type_defs/)

Usage::

    ```python
    from mypy_boto3_datasync.type_defs import CredentialsTypeDef

    data: CredentialsTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    AgentStatusType,
    AtimeType,
    AzureAccessTierType,
    DiscoveryJobStatusType,
    DiscoveryResourceTypeType,
    EfsInTransitEncryptionType,
    EndpointTypeType,
    GidType,
    HdfsAuthenticationTypeType,
    HdfsDataTransferProtectionType,
    HdfsRpcProtectionType,
    LocationFilterNameType,
    LogLevelType,
    MtimeType,
    NfsVersionType,
    ObjectStorageServerProtocolType,
    ObjectTagsType,
    ObjectVersionIdsType,
    OperatorType,
    OverwriteModeType,
    PhaseStatusType,
    PosixPermissionsType,
    PreserveDeletedFilesType,
    PreserveDevicesType,
    RecommendationStatusType,
    ReportLevelType,
    ReportOutputTypeType,
    S3StorageClassType,
    SmbSecurityDescriptorCopyFlagsType,
    SmbVersionType,
    StorageSystemConnectivityStatusType,
    TaskExecutionStatusType,
    TaskFilterNameType,
    TaskQueueingType,
    TaskStatusType,
    TransferModeType,
    UidType,
    VerifyModeType,
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
    "CredentialsTypeDef",
    "DiscoveryServerConfigurationTypeDef",
    "TagListEntryTypeDef",
    "ResponseMetadataTypeDef",
    "PlatformTypeDef",
    "AzureBlobSasConfigurationTypeDef",
    "BlobTypeDef",
    "CancelTaskExecutionRequestRequestTypeDef",
    "CapacityTypeDef",
    "Ec2ConfigTypeDef",
    "HdfsNameNodeTypeDef",
    "QopConfigurationTypeDef",
    "NfsMountOptionsTypeDef",
    "OnPremConfigTypeDef",
    "S3ConfigTypeDef",
    "SmbMountOptionsTypeDef",
    "FilterRuleTypeDef",
    "OptionsTypeDef",
    "TaskScheduleTypeDef",
    "DeleteAgentRequestRequestTypeDef",
    "DeleteLocationRequestRequestTypeDef",
    "DeleteTaskRequestRequestTypeDef",
    "DescribeAgentRequestRequestTypeDef",
    "PrivateLinkConfigTypeDef",
    "DescribeDiscoveryJobRequestRequestTypeDef",
    "DescribeLocationAzureBlobRequestRequestTypeDef",
    "DescribeLocationEfsRequestRequestTypeDef",
    "DescribeLocationFsxLustreRequestRequestTypeDef",
    "DescribeLocationFsxOntapRequestRequestTypeDef",
    "DescribeLocationFsxOpenZfsRequestRequestTypeDef",
    "DescribeLocationFsxWindowsRequestRequestTypeDef",
    "DescribeLocationHdfsRequestRequestTypeDef",
    "DescribeLocationNfsRequestRequestTypeDef",
    "DescribeLocationObjectStorageRequestRequestTypeDef",
    "DescribeLocationS3RequestRequestTypeDef",
    "DescribeLocationSmbRequestRequestTypeDef",
    "DescribeStorageSystemRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "TimestampTypeDef",
    "DescribeStorageSystemResourcesRequestRequestTypeDef",
    "DescribeTaskExecutionRequestRequestTypeDef",
    "ReportResultTypeDef",
    "TaskExecutionResultDetailTypeDef",
    "DescribeTaskRequestRequestTypeDef",
    "DiscoveryJobListEntryTypeDef",
    "GenerateRecommendationsRequestRequestTypeDef",
    "IOPSTypeDef",
    "LatencyTypeDef",
    "ListAgentsRequestRequestTypeDef",
    "ListDiscoveryJobsRequestRequestTypeDef",
    "LocationFilterTypeDef",
    "LocationListEntryTypeDef",
    "ListStorageSystemsRequestRequestTypeDef",
    "StorageSystemListEntryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTaskExecutionsRequestRequestTypeDef",
    "TaskExecutionListEntryTypeDef",
    "TaskFilterTypeDef",
    "TaskListEntryTypeDef",
    "MaxP95PerformanceTypeDef",
    "RecommendationTypeDef",
    "ThroughputTypeDef",
    "RemoveStorageSystemRequestRequestTypeDef",
    "ReportDestinationS3TypeDef",
    "ReportOverrideTypeDef",
    "S3ManifestConfigTypeDef",
    "StopDiscoveryJobRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAgentRequestRequestTypeDef",
    "UpdateDiscoveryJobRequestRequestTypeDef",
    "UpdateStorageSystemRequestRequestTypeDef",
    "AddStorageSystemRequestRequestTypeDef",
    "CreateAgentRequestRequestTypeDef",
    "CreateLocationFsxLustreRequestRequestTypeDef",
    "CreateLocationFsxWindowsRequestRequestTypeDef",
    "StartDiscoveryJobRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "AddStorageSystemResponseTypeDef",
    "CreateAgentResponseTypeDef",
    "CreateLocationAzureBlobResponseTypeDef",
    "CreateLocationEfsResponseTypeDef",
    "CreateLocationFsxLustreResponseTypeDef",
    "CreateLocationFsxOntapResponseTypeDef",
    "CreateLocationFsxOpenZfsResponseTypeDef",
    "CreateLocationFsxWindowsResponseTypeDef",
    "CreateLocationHdfsResponseTypeDef",
    "CreateLocationNfsResponseTypeDef",
    "CreateLocationObjectStorageResponseTypeDef",
    "CreateLocationS3ResponseTypeDef",
    "CreateLocationSmbResponseTypeDef",
    "CreateTaskResponseTypeDef",
    "DescribeDiscoveryJobResponseTypeDef",
    "DescribeLocationAzureBlobResponseTypeDef",
    "DescribeLocationFsxLustreResponseTypeDef",
    "DescribeLocationFsxWindowsResponseTypeDef",
    "DescribeLocationObjectStorageResponseTypeDef",
    "DescribeStorageSystemResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "StartDiscoveryJobResponseTypeDef",
    "StartTaskExecutionResponseTypeDef",
    "AgentListEntryTypeDef",
    "CreateLocationAzureBlobRequestRequestTypeDef",
    "UpdateLocationAzureBlobRequestRequestTypeDef",
    "CreateLocationObjectStorageRequestRequestTypeDef",
    "UpdateLocationObjectStorageRequestRequestTypeDef",
    "CreateLocationEfsRequestRequestTypeDef",
    "DescribeLocationEfsResponseTypeDef",
    "CreateLocationHdfsRequestRequestTypeDef",
    "DescribeLocationHdfsResponseTypeDef",
    "UpdateLocationHdfsRequestRequestTypeDef",
    "FsxProtocolNfsTypeDef",
    "CreateLocationNfsRequestRequestTypeDef",
    "DescribeLocationNfsResponseTypeDef",
    "UpdateLocationNfsRequestRequestTypeDef",
    "CreateLocationS3RequestRequestTypeDef",
    "DescribeLocationS3ResponseTypeDef",
    "CreateLocationSmbRequestRequestTypeDef",
    "DescribeLocationSmbResponseTypeDef",
    "FsxProtocolSmbTypeDef",
    "UpdateLocationSmbRequestRequestTypeDef",
    "UpdateTaskExecutionRequestRequestTypeDef",
    "DescribeAgentResponseTypeDef",
    "ListAgentsRequestListAgentsPaginateTypeDef",
    "ListDiscoveryJobsRequestListDiscoveryJobsPaginateTypeDef",
    "ListStorageSystemsRequestListStorageSystemsPaginateTypeDef",
    "ListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    "ListTaskExecutionsRequestListTaskExecutionsPaginateTypeDef",
    "DescribeStorageSystemResourceMetricsRequestDescribeStorageSystemResourceMetricsPaginateTypeDef",
    "DescribeStorageSystemResourceMetricsRequestRequestTypeDef",
    "ListDiscoveryJobsResponseTypeDef",
    "ListLocationsRequestListLocationsPaginateTypeDef",
    "ListLocationsRequestRequestTypeDef",
    "ListLocationsResponseTypeDef",
    "ListStorageSystemsResponseTypeDef",
    "ListTaskExecutionsResponseTypeDef",
    "ListTasksRequestListTasksPaginateTypeDef",
    "ListTasksRequestRequestTypeDef",
    "ListTasksResponseTypeDef",
    "NetAppONTAPClusterTypeDef",
    "NetAppONTAPSVMTypeDef",
    "NetAppONTAPVolumeTypeDef",
    "P95MetricsTypeDef",
    "ReportDestinationTypeDef",
    "ReportOverridesTypeDef",
    "SourceManifestConfigTypeDef",
    "ListAgentsResponseTypeDef",
    "FsxProtocolTypeDef",
    "ResourceDetailsTypeDef",
    "ResourceMetricsTypeDef",
    "TaskReportConfigTypeDef",
    "ManifestConfigTypeDef",
    "CreateLocationFsxOntapRequestRequestTypeDef",
    "CreateLocationFsxOpenZfsRequestRequestTypeDef",
    "DescribeLocationFsxOntapResponseTypeDef",
    "DescribeLocationFsxOpenZfsResponseTypeDef",
    "DescribeStorageSystemResourcesResponseTypeDef",
    "DescribeStorageSystemResourceMetricsResponseTypeDef",
    "CreateTaskRequestRequestTypeDef",
    "DescribeTaskExecutionResponseTypeDef",
    "DescribeTaskResponseTypeDef",
    "StartTaskExecutionRequestRequestTypeDef",
    "UpdateTaskRequestRequestTypeDef",
)

CredentialsTypeDef = TypedDict(
    "CredentialsTypeDef",
    {
        "Username": str,
        "Password": str,
    },
)
DiscoveryServerConfigurationTypeDef = TypedDict(
    "DiscoveryServerConfigurationTypeDef",
    {
        "ServerHostname": str,
        "ServerPort": NotRequired[int],
    },
)
TagListEntryTypeDef = TypedDict(
    "TagListEntryTypeDef",
    {
        "Key": str,
        "Value": NotRequired[str],
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
PlatformTypeDef = TypedDict(
    "PlatformTypeDef",
    {
        "Version": NotRequired[str],
    },
)
AzureBlobSasConfigurationTypeDef = TypedDict(
    "AzureBlobSasConfigurationTypeDef",
    {
        "Token": str,
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
CancelTaskExecutionRequestRequestTypeDef = TypedDict(
    "CancelTaskExecutionRequestRequestTypeDef",
    {
        "TaskExecutionArn": str,
    },
)
CapacityTypeDef = TypedDict(
    "CapacityTypeDef",
    {
        "Used": NotRequired[int],
        "Provisioned": NotRequired[int],
        "LogicalUsed": NotRequired[int],
        "ClusterCloudStorageUsed": NotRequired[int],
    },
)
Ec2ConfigTypeDef = TypedDict(
    "Ec2ConfigTypeDef",
    {
        "SubnetArn": str,
        "SecurityGroupArns": Sequence[str],
    },
)
HdfsNameNodeTypeDef = TypedDict(
    "HdfsNameNodeTypeDef",
    {
        "Hostname": str,
        "Port": int,
    },
)
QopConfigurationTypeDef = TypedDict(
    "QopConfigurationTypeDef",
    {
        "RpcProtection": NotRequired[HdfsRpcProtectionType],
        "DataTransferProtection": NotRequired[HdfsDataTransferProtectionType],
    },
)
NfsMountOptionsTypeDef = TypedDict(
    "NfsMountOptionsTypeDef",
    {
        "Version": NotRequired[NfsVersionType],
    },
)
OnPremConfigTypeDef = TypedDict(
    "OnPremConfigTypeDef",
    {
        "AgentArns": Sequence[str],
    },
)
S3ConfigTypeDef = TypedDict(
    "S3ConfigTypeDef",
    {
        "BucketAccessRoleArn": str,
    },
)
SmbMountOptionsTypeDef = TypedDict(
    "SmbMountOptionsTypeDef",
    {
        "Version": NotRequired[SmbVersionType],
    },
)
FilterRuleTypeDef = TypedDict(
    "FilterRuleTypeDef",
    {
        "FilterType": NotRequired[Literal["SIMPLE_PATTERN"]],
        "Value": NotRequired[str],
    },
)
OptionsTypeDef = TypedDict(
    "OptionsTypeDef",
    {
        "VerifyMode": NotRequired[VerifyModeType],
        "OverwriteMode": NotRequired[OverwriteModeType],
        "Atime": NotRequired[AtimeType],
        "Mtime": NotRequired[MtimeType],
        "Uid": NotRequired[UidType],
        "Gid": NotRequired[GidType],
        "PreserveDeletedFiles": NotRequired[PreserveDeletedFilesType],
        "PreserveDevices": NotRequired[PreserveDevicesType],
        "PosixPermissions": NotRequired[PosixPermissionsType],
        "BytesPerSecond": NotRequired[int],
        "TaskQueueing": NotRequired[TaskQueueingType],
        "LogLevel": NotRequired[LogLevelType],
        "TransferMode": NotRequired[TransferModeType],
        "SecurityDescriptorCopyFlags": NotRequired[SmbSecurityDescriptorCopyFlagsType],
        "ObjectTags": NotRequired[ObjectTagsType],
    },
)
TaskScheduleTypeDef = TypedDict(
    "TaskScheduleTypeDef",
    {
        "ScheduleExpression": str,
    },
)
DeleteAgentRequestRequestTypeDef = TypedDict(
    "DeleteAgentRequestRequestTypeDef",
    {
        "AgentArn": str,
    },
)
DeleteLocationRequestRequestTypeDef = TypedDict(
    "DeleteLocationRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DeleteTaskRequestRequestTypeDef = TypedDict(
    "DeleteTaskRequestRequestTypeDef",
    {
        "TaskArn": str,
    },
)
DescribeAgentRequestRequestTypeDef = TypedDict(
    "DescribeAgentRequestRequestTypeDef",
    {
        "AgentArn": str,
    },
)
PrivateLinkConfigTypeDef = TypedDict(
    "PrivateLinkConfigTypeDef",
    {
        "VpcEndpointId": NotRequired[str],
        "PrivateLinkEndpoint": NotRequired[str],
        "SubnetArns": NotRequired[List[str]],
        "SecurityGroupArns": NotRequired[List[str]],
    },
)
DescribeDiscoveryJobRequestRequestTypeDef = TypedDict(
    "DescribeDiscoveryJobRequestRequestTypeDef",
    {
        "DiscoveryJobArn": str,
    },
)
DescribeLocationAzureBlobRequestRequestTypeDef = TypedDict(
    "DescribeLocationAzureBlobRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationEfsRequestRequestTypeDef = TypedDict(
    "DescribeLocationEfsRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationFsxLustreRequestRequestTypeDef = TypedDict(
    "DescribeLocationFsxLustreRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationFsxOntapRequestRequestTypeDef = TypedDict(
    "DescribeLocationFsxOntapRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationFsxOpenZfsRequestRequestTypeDef = TypedDict(
    "DescribeLocationFsxOpenZfsRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationFsxWindowsRequestRequestTypeDef = TypedDict(
    "DescribeLocationFsxWindowsRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationHdfsRequestRequestTypeDef = TypedDict(
    "DescribeLocationHdfsRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationNfsRequestRequestTypeDef = TypedDict(
    "DescribeLocationNfsRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationObjectStorageRequestRequestTypeDef = TypedDict(
    "DescribeLocationObjectStorageRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationS3RequestRequestTypeDef = TypedDict(
    "DescribeLocationS3RequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeLocationSmbRequestRequestTypeDef = TypedDict(
    "DescribeLocationSmbRequestRequestTypeDef",
    {
        "LocationArn": str,
    },
)
DescribeStorageSystemRequestRequestTypeDef = TypedDict(
    "DescribeStorageSystemRequestRequestTypeDef",
    {
        "StorageSystemArn": str,
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
TimestampTypeDef = Union[datetime, str]
DescribeStorageSystemResourcesRequestRequestTypeDef = TypedDict(
    "DescribeStorageSystemResourcesRequestRequestTypeDef",
    {
        "DiscoveryJobArn": str,
        "ResourceType": DiscoveryResourceTypeType,
        "ResourceIds": NotRequired[Sequence[str]],
        "Filter": NotRequired[Mapping[Literal["SVM"], Sequence[str]]],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
DescribeTaskExecutionRequestRequestTypeDef = TypedDict(
    "DescribeTaskExecutionRequestRequestTypeDef",
    {
        "TaskExecutionArn": str,
    },
)
ReportResultTypeDef = TypedDict(
    "ReportResultTypeDef",
    {
        "Status": NotRequired[PhaseStatusType],
        "ErrorCode": NotRequired[str],
        "ErrorDetail": NotRequired[str],
    },
)
TaskExecutionResultDetailTypeDef = TypedDict(
    "TaskExecutionResultDetailTypeDef",
    {
        "PrepareDuration": NotRequired[int],
        "PrepareStatus": NotRequired[PhaseStatusType],
        "TotalDuration": NotRequired[int],
        "TransferDuration": NotRequired[int],
        "TransferStatus": NotRequired[PhaseStatusType],
        "VerifyDuration": NotRequired[int],
        "VerifyStatus": NotRequired[PhaseStatusType],
        "ErrorCode": NotRequired[str],
        "ErrorDetail": NotRequired[str],
    },
)
DescribeTaskRequestRequestTypeDef = TypedDict(
    "DescribeTaskRequestRequestTypeDef",
    {
        "TaskArn": str,
    },
)
DiscoveryJobListEntryTypeDef = TypedDict(
    "DiscoveryJobListEntryTypeDef",
    {
        "DiscoveryJobArn": NotRequired[str],
        "Status": NotRequired[DiscoveryJobStatusType],
    },
)
GenerateRecommendationsRequestRequestTypeDef = TypedDict(
    "GenerateRecommendationsRequestRequestTypeDef",
    {
        "DiscoveryJobArn": str,
        "ResourceIds": Sequence[str],
        "ResourceType": DiscoveryResourceTypeType,
    },
)
IOPSTypeDef = TypedDict(
    "IOPSTypeDef",
    {
        "Read": NotRequired[float],
        "Write": NotRequired[float],
        "Other": NotRequired[float],
        "Total": NotRequired[float],
    },
)
LatencyTypeDef = TypedDict(
    "LatencyTypeDef",
    {
        "Read": NotRequired[float],
        "Write": NotRequired[float],
        "Other": NotRequired[float],
    },
)
ListAgentsRequestRequestTypeDef = TypedDict(
    "ListAgentsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListDiscoveryJobsRequestRequestTypeDef = TypedDict(
    "ListDiscoveryJobsRequestRequestTypeDef",
    {
        "StorageSystemArn": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
LocationFilterTypeDef = TypedDict(
    "LocationFilterTypeDef",
    {
        "Name": LocationFilterNameType,
        "Values": Sequence[str],
        "Operator": OperatorType,
    },
)
LocationListEntryTypeDef = TypedDict(
    "LocationListEntryTypeDef",
    {
        "LocationArn": NotRequired[str],
        "LocationUri": NotRequired[str],
    },
)
ListStorageSystemsRequestRequestTypeDef = TypedDict(
    "ListStorageSystemsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
StorageSystemListEntryTypeDef = TypedDict(
    "StorageSystemListEntryTypeDef",
    {
        "StorageSystemArn": NotRequired[str],
        "Name": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListTaskExecutionsRequestRequestTypeDef = TypedDict(
    "ListTaskExecutionsRequestRequestTypeDef",
    {
        "TaskArn": NotRequired[str],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
TaskExecutionListEntryTypeDef = TypedDict(
    "TaskExecutionListEntryTypeDef",
    {
        "TaskExecutionArn": NotRequired[str],
        "Status": NotRequired[TaskExecutionStatusType],
    },
)
TaskFilterTypeDef = TypedDict(
    "TaskFilterTypeDef",
    {
        "Name": TaskFilterNameType,
        "Values": Sequence[str],
        "Operator": OperatorType,
    },
)
TaskListEntryTypeDef = TypedDict(
    "TaskListEntryTypeDef",
    {
        "TaskArn": NotRequired[str],
        "Status": NotRequired[TaskStatusType],
        "Name": NotRequired[str],
    },
)
MaxP95PerformanceTypeDef = TypedDict(
    "MaxP95PerformanceTypeDef",
    {
        "IopsRead": NotRequired[float],
        "IopsWrite": NotRequired[float],
        "IopsOther": NotRequired[float],
        "IopsTotal": NotRequired[float],
        "ThroughputRead": NotRequired[float],
        "ThroughputWrite": NotRequired[float],
        "ThroughputOther": NotRequired[float],
        "ThroughputTotal": NotRequired[float],
        "LatencyRead": NotRequired[float],
        "LatencyWrite": NotRequired[float],
        "LatencyOther": NotRequired[float],
    },
)
RecommendationTypeDef = TypedDict(
    "RecommendationTypeDef",
    {
        "StorageType": NotRequired[str],
        "StorageConfiguration": NotRequired[Dict[str, str]],
        "EstimatedMonthlyStorageCost": NotRequired[str],
    },
)
ThroughputTypeDef = TypedDict(
    "ThroughputTypeDef",
    {
        "Read": NotRequired[float],
        "Write": NotRequired[float],
        "Other": NotRequired[float],
        "Total": NotRequired[float],
    },
)
RemoveStorageSystemRequestRequestTypeDef = TypedDict(
    "RemoveStorageSystemRequestRequestTypeDef",
    {
        "StorageSystemArn": str,
    },
)
ReportDestinationS3TypeDef = TypedDict(
    "ReportDestinationS3TypeDef",
    {
        "S3BucketArn": str,
        "BucketAccessRoleArn": str,
        "Subdirectory": NotRequired[str],
    },
)
ReportOverrideTypeDef = TypedDict(
    "ReportOverrideTypeDef",
    {
        "ReportLevel": NotRequired[ReportLevelType],
    },
)
S3ManifestConfigTypeDef = TypedDict(
    "S3ManifestConfigTypeDef",
    {
        "ManifestObjectPath": str,
        "BucketAccessRoleArn": str,
        "S3BucketArn": str,
        "ManifestObjectVersionId": NotRequired[str],
    },
)
StopDiscoveryJobRequestRequestTypeDef = TypedDict(
    "StopDiscoveryJobRequestRequestTypeDef",
    {
        "DiscoveryJobArn": str,
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Keys": Sequence[str],
    },
)
UpdateAgentRequestRequestTypeDef = TypedDict(
    "UpdateAgentRequestRequestTypeDef",
    {
        "AgentArn": str,
        "Name": NotRequired[str],
    },
)
UpdateDiscoveryJobRequestRequestTypeDef = TypedDict(
    "UpdateDiscoveryJobRequestRequestTypeDef",
    {
        "DiscoveryJobArn": str,
        "CollectionDurationMinutes": int,
    },
)
UpdateStorageSystemRequestRequestTypeDef = TypedDict(
    "UpdateStorageSystemRequestRequestTypeDef",
    {
        "StorageSystemArn": str,
        "ServerConfiguration": NotRequired[DiscoveryServerConfigurationTypeDef],
        "AgentArns": NotRequired[Sequence[str]],
        "Name": NotRequired[str],
        "CloudWatchLogGroupArn": NotRequired[str],
        "Credentials": NotRequired[CredentialsTypeDef],
    },
)
AddStorageSystemRequestRequestTypeDef = TypedDict(
    "AddStorageSystemRequestRequestTypeDef",
    {
        "ServerConfiguration": DiscoveryServerConfigurationTypeDef,
        "SystemType": Literal["NetAppONTAP"],
        "AgentArns": Sequence[str],
        "ClientToken": str,
        "Credentials": CredentialsTypeDef,
        "CloudWatchLogGroupArn": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
        "Name": NotRequired[str],
    },
)
CreateAgentRequestRequestTypeDef = TypedDict(
    "CreateAgentRequestRequestTypeDef",
    {
        "ActivationKey": str,
        "AgentName": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
        "VpcEndpointId": NotRequired[str],
        "SubnetArns": NotRequired[Sequence[str]],
        "SecurityGroupArns": NotRequired[Sequence[str]],
    },
)
CreateLocationFsxLustreRequestRequestTypeDef = TypedDict(
    "CreateLocationFsxLustreRequestRequestTypeDef",
    {
        "FsxFilesystemArn": str,
        "SecurityGroupArns": Sequence[str],
        "Subdirectory": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
CreateLocationFsxWindowsRequestRequestTypeDef = TypedDict(
    "CreateLocationFsxWindowsRequestRequestTypeDef",
    {
        "FsxFilesystemArn": str,
        "SecurityGroupArns": Sequence[str],
        "User": str,
        "Password": str,
        "Subdirectory": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
        "Domain": NotRequired[str],
    },
)
StartDiscoveryJobRequestRequestTypeDef = TypedDict(
    "StartDiscoveryJobRequestRequestTypeDef",
    {
        "StorageSystemArn": str,
        "CollectionDurationMinutes": int,
        "ClientToken": str,
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Tags": Sequence[TagListEntryTypeDef],
    },
)
AddStorageSystemResponseTypeDef = TypedDict(
    "AddStorageSystemResponseTypeDef",
    {
        "StorageSystemArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAgentResponseTypeDef = TypedDict(
    "CreateAgentResponseTypeDef",
    {
        "AgentArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationAzureBlobResponseTypeDef = TypedDict(
    "CreateLocationAzureBlobResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationEfsResponseTypeDef = TypedDict(
    "CreateLocationEfsResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationFsxLustreResponseTypeDef = TypedDict(
    "CreateLocationFsxLustreResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationFsxOntapResponseTypeDef = TypedDict(
    "CreateLocationFsxOntapResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationFsxOpenZfsResponseTypeDef = TypedDict(
    "CreateLocationFsxOpenZfsResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationFsxWindowsResponseTypeDef = TypedDict(
    "CreateLocationFsxWindowsResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationHdfsResponseTypeDef = TypedDict(
    "CreateLocationHdfsResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationNfsResponseTypeDef = TypedDict(
    "CreateLocationNfsResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationObjectStorageResponseTypeDef = TypedDict(
    "CreateLocationObjectStorageResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationS3ResponseTypeDef = TypedDict(
    "CreateLocationS3ResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationSmbResponseTypeDef = TypedDict(
    "CreateLocationSmbResponseTypeDef",
    {
        "LocationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTaskResponseTypeDef = TypedDict(
    "CreateTaskResponseTypeDef",
    {
        "TaskArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDiscoveryJobResponseTypeDef = TypedDict(
    "DescribeDiscoveryJobResponseTypeDef",
    {
        "StorageSystemArn": str,
        "DiscoveryJobArn": str,
        "CollectionDurationMinutes": int,
        "Status": DiscoveryJobStatusType,
        "JobStartTime": datetime,
        "JobEndTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLocationAzureBlobResponseTypeDef = TypedDict(
    "DescribeLocationAzureBlobResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "AuthenticationType": Literal["SAS"],
        "BlobType": Literal["BLOCK"],
        "AccessTier": AzureAccessTierType,
        "AgentArns": List[str],
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLocationFsxLustreResponseTypeDef = TypedDict(
    "DescribeLocationFsxLustreResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "SecurityGroupArns": List[str],
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLocationFsxWindowsResponseTypeDef = TypedDict(
    "DescribeLocationFsxWindowsResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "SecurityGroupArns": List[str],
        "CreationTime": datetime,
        "User": str,
        "Domain": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLocationObjectStorageResponseTypeDef = TypedDict(
    "DescribeLocationObjectStorageResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "AccessKey": str,
        "ServerPort": int,
        "ServerProtocol": ObjectStorageServerProtocolType,
        "AgentArns": List[str],
        "CreationTime": datetime,
        "ServerCertificate": bytes,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeStorageSystemResponseTypeDef = TypedDict(
    "DescribeStorageSystemResponseTypeDef",
    {
        "StorageSystemArn": str,
        "ServerConfiguration": DiscoveryServerConfigurationTypeDef,
        "SystemType": Literal["NetAppONTAP"],
        "AgentArns": List[str],
        "Name": str,
        "ErrorMessage": str,
        "ConnectivityStatus": StorageSystemConnectivityStatusType,
        "CloudWatchLogGroupArn": str,
        "CreationTime": datetime,
        "SecretsManagerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "Tags": List[TagListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDiscoveryJobResponseTypeDef = TypedDict(
    "StartDiscoveryJobResponseTypeDef",
    {
        "DiscoveryJobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTaskExecutionResponseTypeDef = TypedDict(
    "StartTaskExecutionResponseTypeDef",
    {
        "TaskExecutionArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AgentListEntryTypeDef = TypedDict(
    "AgentListEntryTypeDef",
    {
        "AgentArn": NotRequired[str],
        "Name": NotRequired[str],
        "Status": NotRequired[AgentStatusType],
        "Platform": NotRequired[PlatformTypeDef],
    },
)
CreateLocationAzureBlobRequestRequestTypeDef = TypedDict(
    "CreateLocationAzureBlobRequestRequestTypeDef",
    {
        "ContainerUrl": str,
        "AuthenticationType": Literal["SAS"],
        "AgentArns": Sequence[str],
        "SasConfiguration": NotRequired[AzureBlobSasConfigurationTypeDef],
        "BlobType": NotRequired[Literal["BLOCK"]],
        "AccessTier": NotRequired[AzureAccessTierType],
        "Subdirectory": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
UpdateLocationAzureBlobRequestRequestTypeDef = TypedDict(
    "UpdateLocationAzureBlobRequestRequestTypeDef",
    {
        "LocationArn": str,
        "Subdirectory": NotRequired[str],
        "AuthenticationType": NotRequired[Literal["SAS"]],
        "SasConfiguration": NotRequired[AzureBlobSasConfigurationTypeDef],
        "BlobType": NotRequired[Literal["BLOCK"]],
        "AccessTier": NotRequired[AzureAccessTierType],
        "AgentArns": NotRequired[Sequence[str]],
    },
)
CreateLocationObjectStorageRequestRequestTypeDef = TypedDict(
    "CreateLocationObjectStorageRequestRequestTypeDef",
    {
        "ServerHostname": str,
        "BucketName": str,
        "AgentArns": Sequence[str],
        "ServerPort": NotRequired[int],
        "ServerProtocol": NotRequired[ObjectStorageServerProtocolType],
        "Subdirectory": NotRequired[str],
        "AccessKey": NotRequired[str],
        "SecretKey": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
        "ServerCertificate": NotRequired[BlobTypeDef],
    },
)
UpdateLocationObjectStorageRequestRequestTypeDef = TypedDict(
    "UpdateLocationObjectStorageRequestRequestTypeDef",
    {
        "LocationArn": str,
        "ServerPort": NotRequired[int],
        "ServerProtocol": NotRequired[ObjectStorageServerProtocolType],
        "Subdirectory": NotRequired[str],
        "AccessKey": NotRequired[str],
        "SecretKey": NotRequired[str],
        "AgentArns": NotRequired[Sequence[str]],
        "ServerCertificate": NotRequired[BlobTypeDef],
    },
)
CreateLocationEfsRequestRequestTypeDef = TypedDict(
    "CreateLocationEfsRequestRequestTypeDef",
    {
        "EfsFilesystemArn": str,
        "Ec2Config": Ec2ConfigTypeDef,
        "Subdirectory": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
        "AccessPointArn": NotRequired[str],
        "FileSystemAccessRoleArn": NotRequired[str],
        "InTransitEncryption": NotRequired[EfsInTransitEncryptionType],
    },
)
DescribeLocationEfsResponseTypeDef = TypedDict(
    "DescribeLocationEfsResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "Ec2Config": Ec2ConfigTypeDef,
        "CreationTime": datetime,
        "AccessPointArn": str,
        "FileSystemAccessRoleArn": str,
        "InTransitEncryption": EfsInTransitEncryptionType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationHdfsRequestRequestTypeDef = TypedDict(
    "CreateLocationHdfsRequestRequestTypeDef",
    {
        "NameNodes": Sequence[HdfsNameNodeTypeDef],
        "AuthenticationType": HdfsAuthenticationTypeType,
        "AgentArns": Sequence[str],
        "Subdirectory": NotRequired[str],
        "BlockSize": NotRequired[int],
        "ReplicationFactor": NotRequired[int],
        "KmsKeyProviderUri": NotRequired[str],
        "QopConfiguration": NotRequired[QopConfigurationTypeDef],
        "SimpleUser": NotRequired[str],
        "KerberosPrincipal": NotRequired[str],
        "KerberosKeytab": NotRequired[BlobTypeDef],
        "KerberosKrb5Conf": NotRequired[BlobTypeDef],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
DescribeLocationHdfsResponseTypeDef = TypedDict(
    "DescribeLocationHdfsResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "NameNodes": List[HdfsNameNodeTypeDef],
        "BlockSize": int,
        "ReplicationFactor": int,
        "KmsKeyProviderUri": str,
        "QopConfiguration": QopConfigurationTypeDef,
        "AuthenticationType": HdfsAuthenticationTypeType,
        "SimpleUser": str,
        "KerberosPrincipal": str,
        "AgentArns": List[str],
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateLocationHdfsRequestRequestTypeDef = TypedDict(
    "UpdateLocationHdfsRequestRequestTypeDef",
    {
        "LocationArn": str,
        "Subdirectory": NotRequired[str],
        "NameNodes": NotRequired[Sequence[HdfsNameNodeTypeDef]],
        "BlockSize": NotRequired[int],
        "ReplicationFactor": NotRequired[int],
        "KmsKeyProviderUri": NotRequired[str],
        "QopConfiguration": NotRequired[QopConfigurationTypeDef],
        "AuthenticationType": NotRequired[HdfsAuthenticationTypeType],
        "SimpleUser": NotRequired[str],
        "KerberosPrincipal": NotRequired[str],
        "KerberosKeytab": NotRequired[BlobTypeDef],
        "KerberosKrb5Conf": NotRequired[BlobTypeDef],
        "AgentArns": NotRequired[Sequence[str]],
    },
)
FsxProtocolNfsTypeDef = TypedDict(
    "FsxProtocolNfsTypeDef",
    {
        "MountOptions": NotRequired[NfsMountOptionsTypeDef],
    },
)
CreateLocationNfsRequestRequestTypeDef = TypedDict(
    "CreateLocationNfsRequestRequestTypeDef",
    {
        "Subdirectory": str,
        "ServerHostname": str,
        "OnPremConfig": OnPremConfigTypeDef,
        "MountOptions": NotRequired[NfsMountOptionsTypeDef],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
DescribeLocationNfsResponseTypeDef = TypedDict(
    "DescribeLocationNfsResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "OnPremConfig": OnPremConfigTypeDef,
        "MountOptions": NfsMountOptionsTypeDef,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateLocationNfsRequestRequestTypeDef = TypedDict(
    "UpdateLocationNfsRequestRequestTypeDef",
    {
        "LocationArn": str,
        "Subdirectory": NotRequired[str],
        "OnPremConfig": NotRequired[OnPremConfigTypeDef],
        "MountOptions": NotRequired[NfsMountOptionsTypeDef],
    },
)
CreateLocationS3RequestRequestTypeDef = TypedDict(
    "CreateLocationS3RequestRequestTypeDef",
    {
        "S3BucketArn": str,
        "S3Config": S3ConfigTypeDef,
        "Subdirectory": NotRequired[str],
        "S3StorageClass": NotRequired[S3StorageClassType],
        "AgentArns": NotRequired[Sequence[str]],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
DescribeLocationS3ResponseTypeDef = TypedDict(
    "DescribeLocationS3ResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "S3StorageClass": S3StorageClassType,
        "S3Config": S3ConfigTypeDef,
        "AgentArns": List[str],
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLocationSmbRequestRequestTypeDef = TypedDict(
    "CreateLocationSmbRequestRequestTypeDef",
    {
        "Subdirectory": str,
        "ServerHostname": str,
        "User": str,
        "Password": str,
        "AgentArns": Sequence[str],
        "Domain": NotRequired[str],
        "MountOptions": NotRequired[SmbMountOptionsTypeDef],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
DescribeLocationSmbResponseTypeDef = TypedDict(
    "DescribeLocationSmbResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "AgentArns": List[str],
        "User": str,
        "Domain": str,
        "MountOptions": SmbMountOptionsTypeDef,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FsxProtocolSmbTypeDef = TypedDict(
    "FsxProtocolSmbTypeDef",
    {
        "Password": str,
        "User": str,
        "Domain": NotRequired[str],
        "MountOptions": NotRequired[SmbMountOptionsTypeDef],
    },
)
UpdateLocationSmbRequestRequestTypeDef = TypedDict(
    "UpdateLocationSmbRequestRequestTypeDef",
    {
        "LocationArn": str,
        "Subdirectory": NotRequired[str],
        "User": NotRequired[str],
        "Domain": NotRequired[str],
        "Password": NotRequired[str],
        "AgentArns": NotRequired[Sequence[str]],
        "MountOptions": NotRequired[SmbMountOptionsTypeDef],
    },
)
UpdateTaskExecutionRequestRequestTypeDef = TypedDict(
    "UpdateTaskExecutionRequestRequestTypeDef",
    {
        "TaskExecutionArn": str,
        "Options": OptionsTypeDef,
    },
)
DescribeAgentResponseTypeDef = TypedDict(
    "DescribeAgentResponseTypeDef",
    {
        "AgentArn": str,
        "Name": str,
        "Status": AgentStatusType,
        "LastConnectionTime": datetime,
        "CreationTime": datetime,
        "EndpointType": EndpointTypeType,
        "PrivateLinkConfig": PrivateLinkConfigTypeDef,
        "Platform": PlatformTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAgentsRequestListAgentsPaginateTypeDef = TypedDict(
    "ListAgentsRequestListAgentsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDiscoveryJobsRequestListDiscoveryJobsPaginateTypeDef = TypedDict(
    "ListDiscoveryJobsRequestListDiscoveryJobsPaginateTypeDef",
    {
        "StorageSystemArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListStorageSystemsRequestListStorageSystemsPaginateTypeDef = TypedDict(
    "ListStorageSystemsRequestListStorageSystemsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTagsForResourceRequestListTagsForResourcePaginateTypeDef = TypedDict(
    "ListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    {
        "ResourceArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTaskExecutionsRequestListTaskExecutionsPaginateTypeDef = TypedDict(
    "ListTaskExecutionsRequestListTaskExecutionsPaginateTypeDef",
    {
        "TaskArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeStorageSystemResourceMetricsRequestDescribeStorageSystemResourceMetricsPaginateTypeDef = TypedDict(
    "DescribeStorageSystemResourceMetricsRequestDescribeStorageSystemResourceMetricsPaginateTypeDef",
    {
        "DiscoveryJobArn": str,
        "ResourceType": DiscoveryResourceTypeType,
        "ResourceId": str,
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeStorageSystemResourceMetricsRequestRequestTypeDef = TypedDict(
    "DescribeStorageSystemResourceMetricsRequestRequestTypeDef",
    {
        "DiscoveryJobArn": str,
        "ResourceType": DiscoveryResourceTypeType,
        "ResourceId": str,
        "StartTime": NotRequired[TimestampTypeDef],
        "EndTime": NotRequired[TimestampTypeDef],
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
    },
)
ListDiscoveryJobsResponseTypeDef = TypedDict(
    "ListDiscoveryJobsResponseTypeDef",
    {
        "DiscoveryJobs": List[DiscoveryJobListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListLocationsRequestListLocationsPaginateTypeDef = TypedDict(
    "ListLocationsRequestListLocationsPaginateTypeDef",
    {
        "Filters": NotRequired[Sequence[LocationFilterTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLocationsRequestRequestTypeDef = TypedDict(
    "ListLocationsRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Filters": NotRequired[Sequence[LocationFilterTypeDef]],
    },
)
ListLocationsResponseTypeDef = TypedDict(
    "ListLocationsResponseTypeDef",
    {
        "Locations": List[LocationListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListStorageSystemsResponseTypeDef = TypedDict(
    "ListStorageSystemsResponseTypeDef",
    {
        "StorageSystems": List[StorageSystemListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTaskExecutionsResponseTypeDef = TypedDict(
    "ListTaskExecutionsResponseTypeDef",
    {
        "TaskExecutions": List[TaskExecutionListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTasksRequestListTasksPaginateTypeDef = TypedDict(
    "ListTasksRequestListTasksPaginateTypeDef",
    {
        "Filters": NotRequired[Sequence[TaskFilterTypeDef]],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTasksRequestRequestTypeDef = TypedDict(
    "ListTasksRequestRequestTypeDef",
    {
        "MaxResults": NotRequired[int],
        "NextToken": NotRequired[str],
        "Filters": NotRequired[Sequence[TaskFilterTypeDef]],
    },
)
ListTasksResponseTypeDef = TypedDict(
    "ListTasksResponseTypeDef",
    {
        "Tasks": List[TaskListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
NetAppONTAPClusterTypeDef = TypedDict(
    "NetAppONTAPClusterTypeDef",
    {
        "CifsShareCount": NotRequired[int],
        "NfsExportedVolumes": NotRequired[int],
        "ResourceId": NotRequired[str],
        "ClusterName": NotRequired[str],
        "MaxP95Performance": NotRequired[MaxP95PerformanceTypeDef],
        "ClusterBlockStorageSize": NotRequired[int],
        "ClusterBlockStorageUsed": NotRequired[int],
        "ClusterBlockStorageLogicalUsed": NotRequired[int],
        "Recommendations": NotRequired[List[RecommendationTypeDef]],
        "RecommendationStatus": NotRequired[RecommendationStatusType],
        "LunCount": NotRequired[int],
        "ClusterCloudStorageUsed": NotRequired[int],
    },
)
NetAppONTAPSVMTypeDef = TypedDict(
    "NetAppONTAPSVMTypeDef",
    {
        "ClusterUuid": NotRequired[str],
        "ResourceId": NotRequired[str],
        "SvmName": NotRequired[str],
        "CifsShareCount": NotRequired[int],
        "EnabledProtocols": NotRequired[List[str]],
        "TotalCapacityUsed": NotRequired[int],
        "TotalCapacityProvisioned": NotRequired[int],
        "TotalLogicalCapacityUsed": NotRequired[int],
        "MaxP95Performance": NotRequired[MaxP95PerformanceTypeDef],
        "Recommendations": NotRequired[List[RecommendationTypeDef]],
        "NfsExportedVolumes": NotRequired[int],
        "RecommendationStatus": NotRequired[RecommendationStatusType],
        "TotalSnapshotCapacityUsed": NotRequired[int],
        "LunCount": NotRequired[int],
    },
)
NetAppONTAPVolumeTypeDef = TypedDict(
    "NetAppONTAPVolumeTypeDef",
    {
        "VolumeName": NotRequired[str],
        "ResourceId": NotRequired[str],
        "CifsShareCount": NotRequired[int],
        "SecurityStyle": NotRequired[str],
        "SvmUuid": NotRequired[str],
        "SvmName": NotRequired[str],
        "CapacityUsed": NotRequired[int],
        "CapacityProvisioned": NotRequired[int],
        "LogicalCapacityUsed": NotRequired[int],
        "NfsExported": NotRequired[bool],
        "SnapshotCapacityUsed": NotRequired[int],
        "MaxP95Performance": NotRequired[MaxP95PerformanceTypeDef],
        "Recommendations": NotRequired[List[RecommendationTypeDef]],
        "RecommendationStatus": NotRequired[RecommendationStatusType],
        "LunCount": NotRequired[int],
    },
)
P95MetricsTypeDef = TypedDict(
    "P95MetricsTypeDef",
    {
        "IOPS": NotRequired[IOPSTypeDef],
        "Throughput": NotRequired[ThroughputTypeDef],
        "Latency": NotRequired[LatencyTypeDef],
    },
)
ReportDestinationTypeDef = TypedDict(
    "ReportDestinationTypeDef",
    {
        "S3": NotRequired[ReportDestinationS3TypeDef],
    },
)
ReportOverridesTypeDef = TypedDict(
    "ReportOverridesTypeDef",
    {
        "Transferred": NotRequired[ReportOverrideTypeDef],
        "Verified": NotRequired[ReportOverrideTypeDef],
        "Deleted": NotRequired[ReportOverrideTypeDef],
        "Skipped": NotRequired[ReportOverrideTypeDef],
    },
)
SourceManifestConfigTypeDef = TypedDict(
    "SourceManifestConfigTypeDef",
    {
        "S3": S3ManifestConfigTypeDef,
    },
)
ListAgentsResponseTypeDef = TypedDict(
    "ListAgentsResponseTypeDef",
    {
        "Agents": List[AgentListEntryTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FsxProtocolTypeDef = TypedDict(
    "FsxProtocolTypeDef",
    {
        "NFS": NotRequired[FsxProtocolNfsTypeDef],
        "SMB": NotRequired[FsxProtocolSmbTypeDef],
    },
)
ResourceDetailsTypeDef = TypedDict(
    "ResourceDetailsTypeDef",
    {
        "NetAppONTAPSVMs": NotRequired[List[NetAppONTAPSVMTypeDef]],
        "NetAppONTAPVolumes": NotRequired[List[NetAppONTAPVolumeTypeDef]],
        "NetAppONTAPClusters": NotRequired[List[NetAppONTAPClusterTypeDef]],
    },
)
ResourceMetricsTypeDef = TypedDict(
    "ResourceMetricsTypeDef",
    {
        "Timestamp": NotRequired[datetime],
        "P95Metrics": NotRequired[P95MetricsTypeDef],
        "Capacity": NotRequired[CapacityTypeDef],
        "ResourceId": NotRequired[str],
        "ResourceType": NotRequired[DiscoveryResourceTypeType],
    },
)
TaskReportConfigTypeDef = TypedDict(
    "TaskReportConfigTypeDef",
    {
        "Destination": NotRequired[ReportDestinationTypeDef],
        "OutputType": NotRequired[ReportOutputTypeType],
        "ReportLevel": NotRequired[ReportLevelType],
        "ObjectVersionIds": NotRequired[ObjectVersionIdsType],
        "Overrides": NotRequired[ReportOverridesTypeDef],
    },
)
ManifestConfigTypeDef = TypedDict(
    "ManifestConfigTypeDef",
    {
        "Action": NotRequired[Literal["TRANSFER"]],
        "Format": NotRequired[Literal["CSV"]],
        "Source": NotRequired[SourceManifestConfigTypeDef],
    },
)
CreateLocationFsxOntapRequestRequestTypeDef = TypedDict(
    "CreateLocationFsxOntapRequestRequestTypeDef",
    {
        "Protocol": FsxProtocolTypeDef,
        "SecurityGroupArns": Sequence[str],
        "StorageVirtualMachineArn": str,
        "Subdirectory": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
CreateLocationFsxOpenZfsRequestRequestTypeDef = TypedDict(
    "CreateLocationFsxOpenZfsRequestRequestTypeDef",
    {
        "FsxFilesystemArn": str,
        "Protocol": FsxProtocolTypeDef,
        "SecurityGroupArns": Sequence[str],
        "Subdirectory": NotRequired[str],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
DescribeLocationFsxOntapResponseTypeDef = TypedDict(
    "DescribeLocationFsxOntapResponseTypeDef",
    {
        "CreationTime": datetime,
        "LocationArn": str,
        "LocationUri": str,
        "Protocol": FsxProtocolTypeDef,
        "SecurityGroupArns": List[str],
        "StorageVirtualMachineArn": str,
        "FsxFilesystemArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLocationFsxOpenZfsResponseTypeDef = TypedDict(
    "DescribeLocationFsxOpenZfsResponseTypeDef",
    {
        "LocationArn": str,
        "LocationUri": str,
        "SecurityGroupArns": List[str],
        "Protocol": FsxProtocolTypeDef,
        "CreationTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeStorageSystemResourcesResponseTypeDef = TypedDict(
    "DescribeStorageSystemResourcesResponseTypeDef",
    {
        "ResourceDetails": ResourceDetailsTypeDef,
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeStorageSystemResourceMetricsResponseTypeDef = TypedDict(
    "DescribeStorageSystemResourceMetricsResponseTypeDef",
    {
        "Metrics": List[ResourceMetricsTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTaskRequestRequestTypeDef = TypedDict(
    "CreateTaskRequestRequestTypeDef",
    {
        "SourceLocationArn": str,
        "DestinationLocationArn": str,
        "CloudWatchLogGroupArn": NotRequired[str],
        "Name": NotRequired[str],
        "Options": NotRequired[OptionsTypeDef],
        "Excludes": NotRequired[Sequence[FilterRuleTypeDef]],
        "Schedule": NotRequired[TaskScheduleTypeDef],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
        "Includes": NotRequired[Sequence[FilterRuleTypeDef]],
        "ManifestConfig": NotRequired[ManifestConfigTypeDef],
        "TaskReportConfig": NotRequired[TaskReportConfigTypeDef],
    },
)
DescribeTaskExecutionResponseTypeDef = TypedDict(
    "DescribeTaskExecutionResponseTypeDef",
    {
        "TaskExecutionArn": str,
        "Status": TaskExecutionStatusType,
        "Options": OptionsTypeDef,
        "Excludes": List[FilterRuleTypeDef],
        "Includes": List[FilterRuleTypeDef],
        "ManifestConfig": ManifestConfigTypeDef,
        "StartTime": datetime,
        "EstimatedFilesToTransfer": int,
        "EstimatedBytesToTransfer": int,
        "FilesTransferred": int,
        "BytesWritten": int,
        "BytesTransferred": int,
        "BytesCompressed": int,
        "Result": TaskExecutionResultDetailTypeDef,
        "TaskReportConfig": TaskReportConfigTypeDef,
        "FilesDeleted": int,
        "FilesSkipped": int,
        "FilesVerified": int,
        "ReportResult": ReportResultTypeDef,
        "EstimatedFilesToDelete": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTaskResponseTypeDef = TypedDict(
    "DescribeTaskResponseTypeDef",
    {
        "TaskArn": str,
        "Status": TaskStatusType,
        "Name": str,
        "CurrentTaskExecutionArn": str,
        "SourceLocationArn": str,
        "DestinationLocationArn": str,
        "CloudWatchLogGroupArn": str,
        "SourceNetworkInterfaceArns": List[str],
        "DestinationNetworkInterfaceArns": List[str],
        "Options": OptionsTypeDef,
        "Excludes": List[FilterRuleTypeDef],
        "Schedule": TaskScheduleTypeDef,
        "ErrorCode": str,
        "ErrorDetail": str,
        "CreationTime": datetime,
        "Includes": List[FilterRuleTypeDef],
        "ManifestConfig": ManifestConfigTypeDef,
        "TaskReportConfig": TaskReportConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTaskExecutionRequestRequestTypeDef = TypedDict(
    "StartTaskExecutionRequestRequestTypeDef",
    {
        "TaskArn": str,
        "OverrideOptions": NotRequired[OptionsTypeDef],
        "Includes": NotRequired[Sequence[FilterRuleTypeDef]],
        "Excludes": NotRequired[Sequence[FilterRuleTypeDef]],
        "ManifestConfig": NotRequired[ManifestConfigTypeDef],
        "TaskReportConfig": NotRequired[TaskReportConfigTypeDef],
        "Tags": NotRequired[Sequence[TagListEntryTypeDef]],
    },
)
UpdateTaskRequestRequestTypeDef = TypedDict(
    "UpdateTaskRequestRequestTypeDef",
    {
        "TaskArn": str,
        "Options": NotRequired[OptionsTypeDef],
        "Excludes": NotRequired[Sequence[FilterRuleTypeDef]],
        "Schedule": NotRequired[TaskScheduleTypeDef],
        "Name": NotRequired[str],
        "CloudWatchLogGroupArn": NotRequired[str],
        "Includes": NotRequired[Sequence[FilterRuleTypeDef]],
        "ManifestConfig": NotRequired[ManifestConfigTypeDef],
        "TaskReportConfig": NotRequired[TaskReportConfigTypeDef],
    },
)
