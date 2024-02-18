"""
Type annotations for braket service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_braket/type_defs/)

Usage::

    ```python
    from mypy_boto3_braket.type_defs import ContainerImageTypeDef

    data: ContainerImageTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence

from .literals import (
    CancellationStatusType,
    CompressionTypeType,
    DeviceStatusType,
    DeviceTypeType,
    InstanceTypeType,
    JobEventTypeType,
    JobPrimaryStatusType,
    QuantumTaskStatusType,
    QueueNameType,
    QueuePriorityType,
    SearchJobsFilterOperatorType,
    SearchQuantumTasksFilterOperatorType,
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
    "ContainerImageTypeDef",
    "ScriptModeConfigTypeDef",
    "AssociationTypeDef",
    "CancelJobRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "CancelQuantumTaskRequestRequestTypeDef",
    "DeviceConfigTypeDef",
    "InstanceConfigTypeDef",
    "JobCheckpointConfigTypeDef",
    "JobOutputDataConfigTypeDef",
    "JobStoppingConditionTypeDef",
    "S3DataSourceTypeDef",
    "DeviceQueueInfoTypeDef",
    "DeviceSummaryTypeDef",
    "GetDeviceRequestRequestTypeDef",
    "GetJobRequestRequestTypeDef",
    "HybridJobQueueInfoTypeDef",
    "JobEventDetailsTypeDef",
    "GetQuantumTaskRequestRequestTypeDef",
    "QuantumTaskQueueInfoTypeDef",
    "JobSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "QuantumTaskSummaryTypeDef",
    "SearchDevicesFilterTypeDef",
    "SearchJobsFilterTypeDef",
    "SearchQuantumTasksFilterTypeDef",
    "TagResourceRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "AlgorithmSpecificationTypeDef",
    "CreateQuantumTaskRequestRequestTypeDef",
    "CancelJobResponseTypeDef",
    "CancelQuantumTaskResponseTypeDef",
    "CreateJobResponseTypeDef",
    "CreateQuantumTaskResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "DataSourceTypeDef",
    "GetDeviceResponseTypeDef",
    "SearchDevicesResponseTypeDef",
    "GetQuantumTaskResponseTypeDef",
    "SearchJobsResponseTypeDef",
    "SearchQuantumTasksResponseTypeDef",
    "SearchDevicesRequestRequestTypeDef",
    "SearchDevicesRequestSearchDevicesPaginateTypeDef",
    "SearchJobsRequestRequestTypeDef",
    "SearchJobsRequestSearchJobsPaginateTypeDef",
    "SearchQuantumTasksRequestRequestTypeDef",
    "SearchQuantumTasksRequestSearchQuantumTasksPaginateTypeDef",
    "InputFileConfigTypeDef",
    "CreateJobRequestRequestTypeDef",
    "GetJobResponseTypeDef",
)

ContainerImageTypeDef = TypedDict(
    "ContainerImageTypeDef",
    {
        "uri": str,
    },
)
ScriptModeConfigTypeDef = TypedDict(
    "ScriptModeConfigTypeDef",
    {
        "entryPoint": str,
        "s3Uri": str,
        "compressionType": NotRequired[CompressionTypeType],
    },
)
AssociationTypeDef = TypedDict(
    "AssociationTypeDef",
    {
        "arn": str,
        "type": Literal["RESERVATION_TIME_WINDOW_ARN"],
    },
)
CancelJobRequestRequestTypeDef = TypedDict(
    "CancelJobRequestRequestTypeDef",
    {
        "jobArn": str,
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
CancelQuantumTaskRequestRequestTypeDef = TypedDict(
    "CancelQuantumTaskRequestRequestTypeDef",
    {
        "clientToken": str,
        "quantumTaskArn": str,
    },
)
DeviceConfigTypeDef = TypedDict(
    "DeviceConfigTypeDef",
    {
        "device": str,
    },
)
InstanceConfigTypeDef = TypedDict(
    "InstanceConfigTypeDef",
    {
        "instanceType": InstanceTypeType,
        "volumeSizeInGb": int,
        "instanceCount": NotRequired[int],
    },
)
JobCheckpointConfigTypeDef = TypedDict(
    "JobCheckpointConfigTypeDef",
    {
        "s3Uri": str,
        "localPath": NotRequired[str],
    },
)
JobOutputDataConfigTypeDef = TypedDict(
    "JobOutputDataConfigTypeDef",
    {
        "s3Path": str,
        "kmsKeyId": NotRequired[str],
    },
)
JobStoppingConditionTypeDef = TypedDict(
    "JobStoppingConditionTypeDef",
    {
        "maxRuntimeInSeconds": NotRequired[int],
    },
)
S3DataSourceTypeDef = TypedDict(
    "S3DataSourceTypeDef",
    {
        "s3Uri": str,
    },
)
DeviceQueueInfoTypeDef = TypedDict(
    "DeviceQueueInfoTypeDef",
    {
        "queue": QueueNameType,
        "queueSize": str,
        "queuePriority": NotRequired[QueuePriorityType],
    },
)
DeviceSummaryTypeDef = TypedDict(
    "DeviceSummaryTypeDef",
    {
        "deviceArn": str,
        "deviceName": str,
        "deviceStatus": DeviceStatusType,
        "deviceType": DeviceTypeType,
        "providerName": str,
    },
)
GetDeviceRequestRequestTypeDef = TypedDict(
    "GetDeviceRequestRequestTypeDef",
    {
        "deviceArn": str,
    },
)
GetJobRequestRequestTypeDef = TypedDict(
    "GetJobRequestRequestTypeDef",
    {
        "jobArn": str,
        "additionalAttributeNames": NotRequired[Sequence[Literal["QueueInfo"]]],
    },
)
HybridJobQueueInfoTypeDef = TypedDict(
    "HybridJobQueueInfoTypeDef",
    {
        "position": str,
        "queue": QueueNameType,
        "message": NotRequired[str],
    },
)
JobEventDetailsTypeDef = TypedDict(
    "JobEventDetailsTypeDef",
    {
        "eventType": NotRequired[JobEventTypeType],
        "message": NotRequired[str],
        "timeOfEvent": NotRequired[datetime],
    },
)
GetQuantumTaskRequestRequestTypeDef = TypedDict(
    "GetQuantumTaskRequestRequestTypeDef",
    {
        "quantumTaskArn": str,
        "additionalAttributeNames": NotRequired[Sequence[Literal["QueueInfo"]]],
    },
)
QuantumTaskQueueInfoTypeDef = TypedDict(
    "QuantumTaskQueueInfoTypeDef",
    {
        "position": str,
        "queue": QueueNameType,
        "message": NotRequired[str],
        "queuePriority": NotRequired[QueuePriorityType],
    },
)
JobSummaryTypeDef = TypedDict(
    "JobSummaryTypeDef",
    {
        "createdAt": datetime,
        "device": str,
        "jobArn": str,
        "jobName": str,
        "status": JobPrimaryStatusType,
        "endedAt": NotRequired[datetime],
        "startedAt": NotRequired[datetime],
        "tags": NotRequired[Dict[str, str]],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
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
QuantumTaskSummaryTypeDef = TypedDict(
    "QuantumTaskSummaryTypeDef",
    {
        "createdAt": datetime,
        "deviceArn": str,
        "outputS3Bucket": str,
        "outputS3Directory": str,
        "quantumTaskArn": str,
        "shots": int,
        "status": QuantumTaskStatusType,
        "endedAt": NotRequired[datetime],
        "tags": NotRequired[Dict[str, str]],
    },
)
SearchDevicesFilterTypeDef = TypedDict(
    "SearchDevicesFilterTypeDef",
    {
        "name": str,
        "values": Sequence[str],
    },
)
SearchJobsFilterTypeDef = TypedDict(
    "SearchJobsFilterTypeDef",
    {
        "name": str,
        "operator": SearchJobsFilterOperatorType,
        "values": Sequence[str],
    },
)
SearchQuantumTasksFilterTypeDef = TypedDict(
    "SearchQuantumTasksFilterTypeDef",
    {
        "name": str,
        "operator": SearchQuantumTasksFilterOperatorType,
        "values": Sequence[str],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
AlgorithmSpecificationTypeDef = TypedDict(
    "AlgorithmSpecificationTypeDef",
    {
        "containerImage": NotRequired[ContainerImageTypeDef],
        "scriptModeConfig": NotRequired[ScriptModeConfigTypeDef],
    },
)
CreateQuantumTaskRequestRequestTypeDef = TypedDict(
    "CreateQuantumTaskRequestRequestTypeDef",
    {
        "action": str,
        "clientToken": str,
        "deviceArn": str,
        "outputS3Bucket": str,
        "outputS3KeyPrefix": str,
        "shots": int,
        "associations": NotRequired[Sequence[AssociationTypeDef]],
        "deviceParameters": NotRequired[str],
        "jobToken": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
    },
)
CancelJobResponseTypeDef = TypedDict(
    "CancelJobResponseTypeDef",
    {
        "cancellationStatus": CancellationStatusType,
        "jobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CancelQuantumTaskResponseTypeDef = TypedDict(
    "CancelQuantumTaskResponseTypeDef",
    {
        "cancellationStatus": CancellationStatusType,
        "quantumTaskArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateJobResponseTypeDef = TypedDict(
    "CreateJobResponseTypeDef",
    {
        "jobArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateQuantumTaskResponseTypeDef = TypedDict(
    "CreateQuantumTaskResponseTypeDef",
    {
        "quantumTaskArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DataSourceTypeDef = TypedDict(
    "DataSourceTypeDef",
    {
        "s3DataSource": S3DataSourceTypeDef,
    },
)
GetDeviceResponseTypeDef = TypedDict(
    "GetDeviceResponseTypeDef",
    {
        "deviceArn": str,
        "deviceCapabilities": str,
        "deviceName": str,
        "deviceQueueInfo": List[DeviceQueueInfoTypeDef],
        "deviceStatus": DeviceStatusType,
        "deviceType": DeviceTypeType,
        "providerName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchDevicesResponseTypeDef = TypedDict(
    "SearchDevicesResponseTypeDef",
    {
        "devices": List[DeviceSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetQuantumTaskResponseTypeDef = TypedDict(
    "GetQuantumTaskResponseTypeDef",
    {
        "associations": List[AssociationTypeDef],
        "createdAt": datetime,
        "deviceArn": str,
        "deviceParameters": str,
        "endedAt": datetime,
        "failureReason": str,
        "jobArn": str,
        "outputS3Bucket": str,
        "outputS3Directory": str,
        "quantumTaskArn": str,
        "queueInfo": QuantumTaskQueueInfoTypeDef,
        "shots": int,
        "status": QuantumTaskStatusType,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchJobsResponseTypeDef = TypedDict(
    "SearchJobsResponseTypeDef",
    {
        "jobs": List[JobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchQuantumTasksResponseTypeDef = TypedDict(
    "SearchQuantumTasksResponseTypeDef",
    {
        "nextToken": str,
        "quantumTasks": List[QuantumTaskSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SearchDevicesRequestRequestTypeDef = TypedDict(
    "SearchDevicesRequestRequestTypeDef",
    {
        "filters": Sequence[SearchDevicesFilterTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SearchDevicesRequestSearchDevicesPaginateTypeDef = TypedDict(
    "SearchDevicesRequestSearchDevicesPaginateTypeDef",
    {
        "filters": Sequence[SearchDevicesFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchJobsRequestRequestTypeDef = TypedDict(
    "SearchJobsRequestRequestTypeDef",
    {
        "filters": Sequence[SearchJobsFilterTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SearchJobsRequestSearchJobsPaginateTypeDef = TypedDict(
    "SearchJobsRequestSearchJobsPaginateTypeDef",
    {
        "filters": Sequence[SearchJobsFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
SearchQuantumTasksRequestRequestTypeDef = TypedDict(
    "SearchQuantumTasksRequestRequestTypeDef",
    {
        "filters": Sequence[SearchQuantumTasksFilterTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SearchQuantumTasksRequestSearchQuantumTasksPaginateTypeDef = TypedDict(
    "SearchQuantumTasksRequestSearchQuantumTasksPaginateTypeDef",
    {
        "filters": Sequence[SearchQuantumTasksFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
InputFileConfigTypeDef = TypedDict(
    "InputFileConfigTypeDef",
    {
        "channelName": str,
        "dataSource": DataSourceTypeDef,
        "contentType": NotRequired[str],
    },
)
CreateJobRequestRequestTypeDef = TypedDict(
    "CreateJobRequestRequestTypeDef",
    {
        "algorithmSpecification": AlgorithmSpecificationTypeDef,
        "clientToken": str,
        "deviceConfig": DeviceConfigTypeDef,
        "instanceConfig": InstanceConfigTypeDef,
        "jobName": str,
        "outputDataConfig": JobOutputDataConfigTypeDef,
        "roleArn": str,
        "associations": NotRequired[Sequence[AssociationTypeDef]],
        "checkpointConfig": NotRequired[JobCheckpointConfigTypeDef],
        "hyperParameters": NotRequired[Mapping[str, str]],
        "inputDataConfig": NotRequired[Sequence[InputFileConfigTypeDef]],
        "stoppingCondition": NotRequired[JobStoppingConditionTypeDef],
        "tags": NotRequired[Mapping[str, str]],
    },
)
GetJobResponseTypeDef = TypedDict(
    "GetJobResponseTypeDef",
    {
        "algorithmSpecification": AlgorithmSpecificationTypeDef,
        "associations": List[AssociationTypeDef],
        "billableDuration": int,
        "checkpointConfig": JobCheckpointConfigTypeDef,
        "createdAt": datetime,
        "deviceConfig": DeviceConfigTypeDef,
        "endedAt": datetime,
        "events": List[JobEventDetailsTypeDef],
        "failureReason": str,
        "hyperParameters": Dict[str, str],
        "inputDataConfig": List[InputFileConfigTypeDef],
        "instanceConfig": InstanceConfigTypeDef,
        "jobArn": str,
        "jobName": str,
        "outputDataConfig": JobOutputDataConfigTypeDef,
        "queueInfo": HybridJobQueueInfoTypeDef,
        "roleArn": str,
        "startedAt": datetime,
        "status": JobPrimaryStatusType,
        "stoppingCondition": JobStoppingConditionTypeDef,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
