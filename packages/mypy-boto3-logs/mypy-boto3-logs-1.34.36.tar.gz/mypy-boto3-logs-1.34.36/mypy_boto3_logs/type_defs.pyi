"""
Type annotations for logs service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/type_defs/)

Usage::

    ```python
    from mypy_boto3_logs.type_defs import AccountPolicyTypeDef

    data: AccountPolicyTypeDef = ...
    ```
"""

import sys
from typing import Dict, List, Mapping, Sequence

from botocore.eventstream import EventStream

from .literals import (
    AnomalyDetectorStatusType,
    DataProtectionStatusType,
    DeliveryDestinationTypeType,
    DistributionType,
    EvaluationFrequencyType,
    ExportTaskStatusCodeType,
    LogGroupClassType,
    OrderByType,
    OutputFormatType,
    PolicyTypeType,
    QueryStatusType,
    StandardUnitType,
    StateType,
    SuppressionStateType,
    SuppressionTypeType,
    SuppressionUnitType,
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
    "AccountPolicyTypeDef",
    "AnomalyDetectorTypeDef",
    "PatternTokenTypeDef",
    "AssociateKmsKeyRequestRequestTypeDef",
    "CancelExportTaskRequestRequestTypeDef",
    "CreateDeliveryRequestRequestTypeDef",
    "DeliveryTypeDef",
    "ResponseMetadataTypeDef",
    "CreateExportTaskRequestRequestTypeDef",
    "CreateLogAnomalyDetectorRequestRequestTypeDef",
    "CreateLogGroupRequestRequestTypeDef",
    "CreateLogStreamRequestRequestTypeDef",
    "DeleteAccountPolicyRequestRequestTypeDef",
    "DeleteDataProtectionPolicyRequestRequestTypeDef",
    "DeleteDeliveryDestinationPolicyRequestRequestTypeDef",
    "DeleteDeliveryDestinationRequestRequestTypeDef",
    "DeleteDeliveryRequestRequestTypeDef",
    "DeleteDeliverySourceRequestRequestTypeDef",
    "DeleteDestinationRequestRequestTypeDef",
    "DeleteLogAnomalyDetectorRequestRequestTypeDef",
    "DeleteLogGroupRequestRequestTypeDef",
    "DeleteLogStreamRequestRequestTypeDef",
    "DeleteMetricFilterRequestRequestTypeDef",
    "DeleteQueryDefinitionRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteRetentionPolicyRequestRequestTypeDef",
    "DeleteSubscriptionFilterRequestRequestTypeDef",
    "DeliveryDestinationConfigurationTypeDef",
    "DeliverySourceTypeDef",
    "DescribeAccountPoliciesRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeDeliveriesRequestRequestTypeDef",
    "DescribeDeliveryDestinationsRequestRequestTypeDef",
    "DescribeDeliverySourcesRequestRequestTypeDef",
    "DescribeDestinationsRequestRequestTypeDef",
    "DestinationTypeDef",
    "DescribeExportTasksRequestRequestTypeDef",
    "DescribeLogGroupsRequestRequestTypeDef",
    "LogGroupTypeDef",
    "DescribeLogStreamsRequestRequestTypeDef",
    "LogStreamTypeDef",
    "DescribeMetricFiltersRequestRequestTypeDef",
    "DescribeQueriesRequestRequestTypeDef",
    "QueryInfoTypeDef",
    "DescribeQueryDefinitionsRequestRequestTypeDef",
    "QueryDefinitionTypeDef",
    "DescribeResourcePoliciesRequestRequestTypeDef",
    "ResourcePolicyTypeDef",
    "DescribeSubscriptionFiltersRequestRequestTypeDef",
    "SubscriptionFilterTypeDef",
    "DisassociateKmsKeyRequestRequestTypeDef",
    "ExportTaskExecutionInfoTypeDef",
    "ExportTaskStatusTypeDef",
    "FilterLogEventsRequestRequestTypeDef",
    "FilteredLogEventTypeDef",
    "SearchedLogStreamTypeDef",
    "GetDataProtectionPolicyRequestRequestTypeDef",
    "GetDeliveryDestinationPolicyRequestRequestTypeDef",
    "PolicyTypeDef",
    "GetDeliveryDestinationRequestRequestTypeDef",
    "GetDeliveryRequestRequestTypeDef",
    "GetDeliverySourceRequestRequestTypeDef",
    "GetLogAnomalyDetectorRequestRequestTypeDef",
    "GetLogEventsRequestRequestTypeDef",
    "OutputLogEventTypeDef",
    "GetLogGroupFieldsRequestRequestTypeDef",
    "LogGroupFieldTypeDef",
    "GetLogRecordRequestRequestTypeDef",
    "GetQueryResultsRequestRequestTypeDef",
    "QueryStatisticsTypeDef",
    "ResultFieldTypeDef",
    "InputLogEventTypeDef",
    "ListAnomaliesRequestRequestTypeDef",
    "ListLogAnomalyDetectorsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTagsLogGroupRequestRequestTypeDef",
    "LiveTailSessionLogEventTypeDef",
    "LiveTailSessionMetadataTypeDef",
    "LiveTailSessionStartTypeDef",
    "MetricFilterMatchRecordTypeDef",
    "MetricTransformationTypeDef",
    "PutAccountPolicyRequestRequestTypeDef",
    "PutDataProtectionPolicyRequestRequestTypeDef",
    "PutDeliveryDestinationPolicyRequestRequestTypeDef",
    "PutDeliverySourceRequestRequestTypeDef",
    "PutDestinationPolicyRequestRequestTypeDef",
    "PutDestinationRequestRequestTypeDef",
    "RejectedLogEventsInfoTypeDef",
    "PutQueryDefinitionRequestRequestTypeDef",
    "PutResourcePolicyRequestRequestTypeDef",
    "PutRetentionPolicyRequestRequestTypeDef",
    "PutSubscriptionFilterRequestRequestTypeDef",
    "SessionStreamingExceptionTypeDef",
    "SessionTimeoutExceptionTypeDef",
    "StartLiveTailRequestRequestTypeDef",
    "StartQueryRequestRequestTypeDef",
    "StopQueryRequestRequestTypeDef",
    "SuppressionPeriodTypeDef",
    "TagLogGroupRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TestMetricFilterRequestRequestTypeDef",
    "UntagLogGroupRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateLogAnomalyDetectorRequestRequestTypeDef",
    "AnomalyTypeDef",
    "CreateDeliveryResponseTypeDef",
    "CreateExportTaskResponseTypeDef",
    "CreateLogAnomalyDetectorResponseTypeDef",
    "DeleteQueryDefinitionResponseTypeDef",
    "DescribeAccountPoliciesResponseTypeDef",
    "DescribeDeliveriesResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetDataProtectionPolicyResponseTypeDef",
    "GetDeliveryResponseTypeDef",
    "GetLogAnomalyDetectorResponseTypeDef",
    "GetLogRecordResponseTypeDef",
    "ListLogAnomalyDetectorsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "ListTagsLogGroupResponseTypeDef",
    "PutAccountPolicyResponseTypeDef",
    "PutDataProtectionPolicyResponseTypeDef",
    "PutQueryDefinitionResponseTypeDef",
    "StartQueryResponseTypeDef",
    "StopQueryResponseTypeDef",
    "DeliveryDestinationTypeDef",
    "PutDeliveryDestinationRequestRequestTypeDef",
    "DescribeDeliverySourcesResponseTypeDef",
    "GetDeliverySourceResponseTypeDef",
    "PutDeliverySourceResponseTypeDef",
    "DescribeDeliveriesRequestDescribeDeliveriesPaginateTypeDef",
    "DescribeDeliveryDestinationsRequestDescribeDeliveryDestinationsPaginateTypeDef",
    "DescribeDeliverySourcesRequestDescribeDeliverySourcesPaginateTypeDef",
    "DescribeDestinationsRequestDescribeDestinationsPaginateTypeDef",
    "DescribeExportTasksRequestDescribeExportTasksPaginateTypeDef",
    "DescribeLogGroupsRequestDescribeLogGroupsPaginateTypeDef",
    "DescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef",
    "DescribeMetricFiltersRequestDescribeMetricFiltersPaginateTypeDef",
    "DescribeQueriesRequestDescribeQueriesPaginateTypeDef",
    "DescribeResourcePoliciesRequestDescribeResourcePoliciesPaginateTypeDef",
    "DescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef",
    "FilterLogEventsRequestFilterLogEventsPaginateTypeDef",
    "ListAnomaliesRequestListAnomaliesPaginateTypeDef",
    "ListLogAnomalyDetectorsRequestListLogAnomalyDetectorsPaginateTypeDef",
    "DescribeDestinationsResponseTypeDef",
    "PutDestinationResponseTypeDef",
    "DescribeLogGroupsResponseTypeDef",
    "DescribeLogStreamsResponseTypeDef",
    "DescribeQueriesResponseTypeDef",
    "DescribeQueryDefinitionsResponseTypeDef",
    "DescribeResourcePoliciesResponseTypeDef",
    "PutResourcePolicyResponseTypeDef",
    "DescribeSubscriptionFiltersResponseTypeDef",
    "ExportTaskTypeDef",
    "FilterLogEventsResponseTypeDef",
    "GetDeliveryDestinationPolicyResponseTypeDef",
    "PutDeliveryDestinationPolicyResponseTypeDef",
    "GetLogEventsResponseTypeDef",
    "GetLogGroupFieldsResponseTypeDef",
    "GetQueryResultsResponseTypeDef",
    "PutLogEventsRequestRequestTypeDef",
    "LiveTailSessionUpdateTypeDef",
    "TestMetricFilterResponseTypeDef",
    "MetricFilterTypeDef",
    "PutMetricFilterRequestRequestTypeDef",
    "PutLogEventsResponseTypeDef",
    "UpdateAnomalyRequestRequestTypeDef",
    "ListAnomaliesResponseTypeDef",
    "DescribeDeliveryDestinationsResponseTypeDef",
    "GetDeliveryDestinationResponseTypeDef",
    "PutDeliveryDestinationResponseTypeDef",
    "DescribeExportTasksResponseTypeDef",
    "StartLiveTailResponseStreamTypeDef",
    "DescribeMetricFiltersResponseTypeDef",
    "StartLiveTailResponseTypeDef",
)

AccountPolicyTypeDef = TypedDict(
    "AccountPolicyTypeDef",
    {
        "policyName": NotRequired[str],
        "policyDocument": NotRequired[str],
        "lastUpdatedTime": NotRequired[int],
        "policyType": NotRequired[PolicyTypeType],
        "scope": NotRequired[Literal["ALL"]],
        "selectionCriteria": NotRequired[str],
        "accountId": NotRequired[str],
    },
)
AnomalyDetectorTypeDef = TypedDict(
    "AnomalyDetectorTypeDef",
    {
        "anomalyDetectorArn": NotRequired[str],
        "detectorName": NotRequired[str],
        "logGroupArnList": NotRequired[List[str]],
        "evaluationFrequency": NotRequired[EvaluationFrequencyType],
        "filterPattern": NotRequired[str],
        "anomalyDetectorStatus": NotRequired[AnomalyDetectorStatusType],
        "kmsKeyId": NotRequired[str],
        "creationTimeStamp": NotRequired[int],
        "lastModifiedTimeStamp": NotRequired[int],
        "anomalyVisibilityTime": NotRequired[int],
    },
)
PatternTokenTypeDef = TypedDict(
    "PatternTokenTypeDef",
    {
        "dynamicTokenPosition": NotRequired[int],
        "isDynamic": NotRequired[bool],
        "tokenString": NotRequired[str],
        "enumerations": NotRequired[Dict[str, int]],
    },
)
AssociateKmsKeyRequestRequestTypeDef = TypedDict(
    "AssociateKmsKeyRequestRequestTypeDef",
    {
        "kmsKeyId": str,
        "logGroupName": NotRequired[str],
        "resourceIdentifier": NotRequired[str],
    },
)
CancelExportTaskRequestRequestTypeDef = TypedDict(
    "CancelExportTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
CreateDeliveryRequestRequestTypeDef = TypedDict(
    "CreateDeliveryRequestRequestTypeDef",
    {
        "deliverySourceName": str,
        "deliveryDestinationArn": str,
        "tags": NotRequired[Mapping[str, str]],
    },
)
DeliveryTypeDef = TypedDict(
    "DeliveryTypeDef",
    {
        "id": NotRequired[str],
        "arn": NotRequired[str],
        "deliverySourceName": NotRequired[str],
        "deliveryDestinationArn": NotRequired[str],
        "deliveryDestinationType": NotRequired[DeliveryDestinationTypeType],
        "tags": NotRequired[Dict[str, str]],
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
CreateExportTaskRequestRequestTypeDef = TypedDict(
    "CreateExportTaskRequestRequestTypeDef",
    {
        "logGroupName": str,
        "fromTime": int,
        "to": int,
        "destination": str,
        "taskName": NotRequired[str],
        "logStreamNamePrefix": NotRequired[str],
        "destinationPrefix": NotRequired[str],
    },
)
CreateLogAnomalyDetectorRequestRequestTypeDef = TypedDict(
    "CreateLogAnomalyDetectorRequestRequestTypeDef",
    {
        "logGroupArnList": Sequence[str],
        "detectorName": NotRequired[str],
        "evaluationFrequency": NotRequired[EvaluationFrequencyType],
        "filterPattern": NotRequired[str],
        "kmsKeyId": NotRequired[str],
        "anomalyVisibilityTime": NotRequired[int],
        "tags": NotRequired[Mapping[str, str]],
    },
)
CreateLogGroupRequestRequestTypeDef = TypedDict(
    "CreateLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
        "kmsKeyId": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "logGroupClass": NotRequired[LogGroupClassType],
    },
)
CreateLogStreamRequestRequestTypeDef = TypedDict(
    "CreateLogStreamRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
    },
)
DeleteAccountPolicyRequestRequestTypeDef = TypedDict(
    "DeleteAccountPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "policyType": PolicyTypeType,
    },
)
DeleteDataProtectionPolicyRequestRequestTypeDef = TypedDict(
    "DeleteDataProtectionPolicyRequestRequestTypeDef",
    {
        "logGroupIdentifier": str,
    },
)
DeleteDeliveryDestinationPolicyRequestRequestTypeDef = TypedDict(
    "DeleteDeliveryDestinationPolicyRequestRequestTypeDef",
    {
        "deliveryDestinationName": str,
    },
)
DeleteDeliveryDestinationRequestRequestTypeDef = TypedDict(
    "DeleteDeliveryDestinationRequestRequestTypeDef",
    {
        "name": str,
    },
)
DeleteDeliveryRequestRequestTypeDef = TypedDict(
    "DeleteDeliveryRequestRequestTypeDef",
    {
        "id": str,
    },
)
DeleteDeliverySourceRequestRequestTypeDef = TypedDict(
    "DeleteDeliverySourceRequestRequestTypeDef",
    {
        "name": str,
    },
)
DeleteDestinationRequestRequestTypeDef = TypedDict(
    "DeleteDestinationRequestRequestTypeDef",
    {
        "destinationName": str,
    },
)
DeleteLogAnomalyDetectorRequestRequestTypeDef = TypedDict(
    "DeleteLogAnomalyDetectorRequestRequestTypeDef",
    {
        "anomalyDetectorArn": str,
    },
)
DeleteLogGroupRequestRequestTypeDef = TypedDict(
    "DeleteLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
DeleteLogStreamRequestRequestTypeDef = TypedDict(
    "DeleteLogStreamRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
    },
)
DeleteMetricFilterRequestRequestTypeDef = TypedDict(
    "DeleteMetricFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
    },
)
DeleteQueryDefinitionRequestRequestTypeDef = TypedDict(
    "DeleteQueryDefinitionRequestRequestTypeDef",
    {
        "queryDefinitionId": str,
    },
)
DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "policyName": NotRequired[str],
    },
)
DeleteRetentionPolicyRequestRequestTypeDef = TypedDict(
    "DeleteRetentionPolicyRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
DeleteSubscriptionFilterRequestRequestTypeDef = TypedDict(
    "DeleteSubscriptionFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
    },
)
DeliveryDestinationConfigurationTypeDef = TypedDict(
    "DeliveryDestinationConfigurationTypeDef",
    {
        "destinationResourceArn": str,
    },
)
DeliverySourceTypeDef = TypedDict(
    "DeliverySourceTypeDef",
    {
        "name": NotRequired[str],
        "arn": NotRequired[str],
        "resourceArns": NotRequired[List[str]],
        "service": NotRequired[str],
        "logType": NotRequired[str],
        "tags": NotRequired[Dict[str, str]],
    },
)
DescribeAccountPoliciesRequestRequestTypeDef = TypedDict(
    "DescribeAccountPoliciesRequestRequestTypeDef",
    {
        "policyType": PolicyTypeType,
        "policyName": NotRequired[str],
        "accountIdentifiers": NotRequired[Sequence[str]],
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
DescribeDeliveriesRequestRequestTypeDef = TypedDict(
    "DescribeDeliveriesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
DescribeDeliveryDestinationsRequestRequestTypeDef = TypedDict(
    "DescribeDeliveryDestinationsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
DescribeDeliverySourcesRequestRequestTypeDef = TypedDict(
    "DescribeDeliverySourcesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
DescribeDestinationsRequestRequestTypeDef = TypedDict(
    "DescribeDestinationsRequestRequestTypeDef",
    {
        "DestinationNamePrefix": NotRequired[str],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
DestinationTypeDef = TypedDict(
    "DestinationTypeDef",
    {
        "destinationName": NotRequired[str],
        "targetArn": NotRequired[str],
        "roleArn": NotRequired[str],
        "accessPolicy": NotRequired[str],
        "arn": NotRequired[str],
        "creationTime": NotRequired[int],
    },
)
DescribeExportTasksRequestRequestTypeDef = TypedDict(
    "DescribeExportTasksRequestRequestTypeDef",
    {
        "taskId": NotRequired[str],
        "statusCode": NotRequired[ExportTaskStatusCodeType],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
DescribeLogGroupsRequestRequestTypeDef = TypedDict(
    "DescribeLogGroupsRequestRequestTypeDef",
    {
        "accountIdentifiers": NotRequired[Sequence[str]],
        "logGroupNamePrefix": NotRequired[str],
        "logGroupNamePattern": NotRequired[str],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
        "includeLinkedAccounts": NotRequired[bool],
        "logGroupClass": NotRequired[LogGroupClassType],
    },
)
LogGroupTypeDef = TypedDict(
    "LogGroupTypeDef",
    {
        "logGroupName": NotRequired[str],
        "creationTime": NotRequired[int],
        "retentionInDays": NotRequired[int],
        "metricFilterCount": NotRequired[int],
        "arn": NotRequired[str],
        "storedBytes": NotRequired[int],
        "kmsKeyId": NotRequired[str],
        "dataProtectionStatus": NotRequired[DataProtectionStatusType],
        "inheritedProperties": NotRequired[List[Literal["ACCOUNT_DATA_PROTECTION"]]],
        "logGroupClass": NotRequired[LogGroupClassType],
        "logGroupArn": NotRequired[str],
    },
)
DescribeLogStreamsRequestRequestTypeDef = TypedDict(
    "DescribeLogStreamsRequestRequestTypeDef",
    {
        "logGroupName": NotRequired[str],
        "logGroupIdentifier": NotRequired[str],
        "logStreamNamePrefix": NotRequired[str],
        "orderBy": NotRequired[OrderByType],
        "descending": NotRequired[bool],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
LogStreamTypeDef = TypedDict(
    "LogStreamTypeDef",
    {
        "logStreamName": NotRequired[str],
        "creationTime": NotRequired[int],
        "firstEventTimestamp": NotRequired[int],
        "lastEventTimestamp": NotRequired[int],
        "lastIngestionTime": NotRequired[int],
        "uploadSequenceToken": NotRequired[str],
        "arn": NotRequired[str],
        "storedBytes": NotRequired[int],
    },
)
DescribeMetricFiltersRequestRequestTypeDef = TypedDict(
    "DescribeMetricFiltersRequestRequestTypeDef",
    {
        "logGroupName": NotRequired[str],
        "filterNamePrefix": NotRequired[str],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
        "metricName": NotRequired[str],
        "metricNamespace": NotRequired[str],
    },
)
DescribeQueriesRequestRequestTypeDef = TypedDict(
    "DescribeQueriesRequestRequestTypeDef",
    {
        "logGroupName": NotRequired[str],
        "status": NotRequired[QueryStatusType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
QueryInfoTypeDef = TypedDict(
    "QueryInfoTypeDef",
    {
        "queryId": NotRequired[str],
        "queryString": NotRequired[str],
        "status": NotRequired[QueryStatusType],
        "createTime": NotRequired[int],
        "logGroupName": NotRequired[str],
    },
)
DescribeQueryDefinitionsRequestRequestTypeDef = TypedDict(
    "DescribeQueryDefinitionsRequestRequestTypeDef",
    {
        "queryDefinitionNamePrefix": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
QueryDefinitionTypeDef = TypedDict(
    "QueryDefinitionTypeDef",
    {
        "queryDefinitionId": NotRequired[str],
        "name": NotRequired[str],
        "queryString": NotRequired[str],
        "lastModified": NotRequired[int],
        "logGroupNames": NotRequired[List[str]],
    },
)
DescribeResourcePoliciesRequestRequestTypeDef = TypedDict(
    "DescribeResourcePoliciesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
ResourcePolicyTypeDef = TypedDict(
    "ResourcePolicyTypeDef",
    {
        "policyName": NotRequired[str],
        "policyDocument": NotRequired[str],
        "lastUpdatedTime": NotRequired[int],
    },
)
DescribeSubscriptionFiltersRequestRequestTypeDef = TypedDict(
    "DescribeSubscriptionFiltersRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterNamePrefix": NotRequired[str],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
    },
)
SubscriptionFilterTypeDef = TypedDict(
    "SubscriptionFilterTypeDef",
    {
        "filterName": NotRequired[str],
        "logGroupName": NotRequired[str],
        "filterPattern": NotRequired[str],
        "destinationArn": NotRequired[str],
        "roleArn": NotRequired[str],
        "distribution": NotRequired[DistributionType],
        "creationTime": NotRequired[int],
    },
)
DisassociateKmsKeyRequestRequestTypeDef = TypedDict(
    "DisassociateKmsKeyRequestRequestTypeDef",
    {
        "logGroupName": NotRequired[str],
        "resourceIdentifier": NotRequired[str],
    },
)
ExportTaskExecutionInfoTypeDef = TypedDict(
    "ExportTaskExecutionInfoTypeDef",
    {
        "creationTime": NotRequired[int],
        "completionTime": NotRequired[int],
    },
)
ExportTaskStatusTypeDef = TypedDict(
    "ExportTaskStatusTypeDef",
    {
        "code": NotRequired[ExportTaskStatusCodeType],
        "message": NotRequired[str],
    },
)
FilterLogEventsRequestRequestTypeDef = TypedDict(
    "FilterLogEventsRequestRequestTypeDef",
    {
        "logGroupName": NotRequired[str],
        "logGroupIdentifier": NotRequired[str],
        "logStreamNames": NotRequired[Sequence[str]],
        "logStreamNamePrefix": NotRequired[str],
        "startTime": NotRequired[int],
        "endTime": NotRequired[int],
        "filterPattern": NotRequired[str],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
        "interleaved": NotRequired[bool],
        "unmask": NotRequired[bool],
    },
)
FilteredLogEventTypeDef = TypedDict(
    "FilteredLogEventTypeDef",
    {
        "logStreamName": NotRequired[str],
        "timestamp": NotRequired[int],
        "message": NotRequired[str],
        "ingestionTime": NotRequired[int],
        "eventId": NotRequired[str],
    },
)
SearchedLogStreamTypeDef = TypedDict(
    "SearchedLogStreamTypeDef",
    {
        "logStreamName": NotRequired[str],
        "searchedCompletely": NotRequired[bool],
    },
)
GetDataProtectionPolicyRequestRequestTypeDef = TypedDict(
    "GetDataProtectionPolicyRequestRequestTypeDef",
    {
        "logGroupIdentifier": str,
    },
)
GetDeliveryDestinationPolicyRequestRequestTypeDef = TypedDict(
    "GetDeliveryDestinationPolicyRequestRequestTypeDef",
    {
        "deliveryDestinationName": str,
    },
)
PolicyTypeDef = TypedDict(
    "PolicyTypeDef",
    {
        "deliveryDestinationPolicy": NotRequired[str],
    },
)
GetDeliveryDestinationRequestRequestTypeDef = TypedDict(
    "GetDeliveryDestinationRequestRequestTypeDef",
    {
        "name": str,
    },
)
GetDeliveryRequestRequestTypeDef = TypedDict(
    "GetDeliveryRequestRequestTypeDef",
    {
        "id": str,
    },
)
GetDeliverySourceRequestRequestTypeDef = TypedDict(
    "GetDeliverySourceRequestRequestTypeDef",
    {
        "name": str,
    },
)
GetLogAnomalyDetectorRequestRequestTypeDef = TypedDict(
    "GetLogAnomalyDetectorRequestRequestTypeDef",
    {
        "anomalyDetectorArn": str,
    },
)
GetLogEventsRequestRequestTypeDef = TypedDict(
    "GetLogEventsRequestRequestTypeDef",
    {
        "logStreamName": str,
        "logGroupName": NotRequired[str],
        "logGroupIdentifier": NotRequired[str],
        "startTime": NotRequired[int],
        "endTime": NotRequired[int],
        "nextToken": NotRequired[str],
        "limit": NotRequired[int],
        "startFromHead": NotRequired[bool],
        "unmask": NotRequired[bool],
    },
)
OutputLogEventTypeDef = TypedDict(
    "OutputLogEventTypeDef",
    {
        "timestamp": NotRequired[int],
        "message": NotRequired[str],
        "ingestionTime": NotRequired[int],
    },
)
GetLogGroupFieldsRequestRequestTypeDef = TypedDict(
    "GetLogGroupFieldsRequestRequestTypeDef",
    {
        "logGroupName": NotRequired[str],
        "time": NotRequired[int],
        "logGroupIdentifier": NotRequired[str],
    },
)
LogGroupFieldTypeDef = TypedDict(
    "LogGroupFieldTypeDef",
    {
        "name": NotRequired[str],
        "percent": NotRequired[int],
    },
)
GetLogRecordRequestRequestTypeDef = TypedDict(
    "GetLogRecordRequestRequestTypeDef",
    {
        "logRecordPointer": str,
        "unmask": NotRequired[bool],
    },
)
GetQueryResultsRequestRequestTypeDef = TypedDict(
    "GetQueryResultsRequestRequestTypeDef",
    {
        "queryId": str,
    },
)
QueryStatisticsTypeDef = TypedDict(
    "QueryStatisticsTypeDef",
    {
        "recordsMatched": NotRequired[float],
        "recordsScanned": NotRequired[float],
        "bytesScanned": NotRequired[float],
    },
)
ResultFieldTypeDef = TypedDict(
    "ResultFieldTypeDef",
    {
        "field": NotRequired[str],
        "value": NotRequired[str],
    },
)
InputLogEventTypeDef = TypedDict(
    "InputLogEventTypeDef",
    {
        "timestamp": int,
        "message": str,
    },
)
ListAnomaliesRequestRequestTypeDef = TypedDict(
    "ListAnomaliesRequestRequestTypeDef",
    {
        "anomalyDetectorArn": NotRequired[str],
        "suppressionState": NotRequired[SuppressionStateType],
        "limit": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListLogAnomalyDetectorsRequestRequestTypeDef = TypedDict(
    "ListLogAnomalyDetectorsRequestRequestTypeDef",
    {
        "filterLogGroupArn": NotRequired[str],
        "limit": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
ListTagsLogGroupRequestRequestTypeDef = TypedDict(
    "ListTagsLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
    },
)
LiveTailSessionLogEventTypeDef = TypedDict(
    "LiveTailSessionLogEventTypeDef",
    {
        "logStreamName": NotRequired[str],
        "logGroupIdentifier": NotRequired[str],
        "message": NotRequired[str],
        "timestamp": NotRequired[int],
        "ingestionTime": NotRequired[int],
    },
)
LiveTailSessionMetadataTypeDef = TypedDict(
    "LiveTailSessionMetadataTypeDef",
    {
        "sampled": NotRequired[bool],
    },
)
LiveTailSessionStartTypeDef = TypedDict(
    "LiveTailSessionStartTypeDef",
    {
        "requestId": NotRequired[str],
        "sessionId": NotRequired[str],
        "logGroupIdentifiers": NotRequired[List[str]],
        "logStreamNames": NotRequired[List[str]],
        "logStreamNamePrefixes": NotRequired[List[str]],
        "logEventFilterPattern": NotRequired[str],
    },
)
MetricFilterMatchRecordTypeDef = TypedDict(
    "MetricFilterMatchRecordTypeDef",
    {
        "eventNumber": NotRequired[int],
        "eventMessage": NotRequired[str],
        "extractedValues": NotRequired[Dict[str, str]],
    },
)
MetricTransformationTypeDef = TypedDict(
    "MetricTransformationTypeDef",
    {
        "metricName": str,
        "metricNamespace": str,
        "metricValue": str,
        "defaultValue": NotRequired[float],
        "dimensions": NotRequired[Dict[str, str]],
        "unit": NotRequired[StandardUnitType],
    },
)
PutAccountPolicyRequestRequestTypeDef = TypedDict(
    "PutAccountPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "policyDocument": str,
        "policyType": PolicyTypeType,
        "scope": NotRequired[Literal["ALL"]],
        "selectionCriteria": NotRequired[str],
    },
)
PutDataProtectionPolicyRequestRequestTypeDef = TypedDict(
    "PutDataProtectionPolicyRequestRequestTypeDef",
    {
        "logGroupIdentifier": str,
        "policyDocument": str,
    },
)
PutDeliveryDestinationPolicyRequestRequestTypeDef = TypedDict(
    "PutDeliveryDestinationPolicyRequestRequestTypeDef",
    {
        "deliveryDestinationName": str,
        "deliveryDestinationPolicy": str,
    },
)
PutDeliverySourceRequestRequestTypeDef = TypedDict(
    "PutDeliverySourceRequestRequestTypeDef",
    {
        "name": str,
        "resourceArn": str,
        "logType": str,
        "tags": NotRequired[Mapping[str, str]],
    },
)
PutDestinationPolicyRequestRequestTypeDef = TypedDict(
    "PutDestinationPolicyRequestRequestTypeDef",
    {
        "destinationName": str,
        "accessPolicy": str,
        "forceUpdate": NotRequired[bool],
    },
)
PutDestinationRequestRequestTypeDef = TypedDict(
    "PutDestinationRequestRequestTypeDef",
    {
        "destinationName": str,
        "targetArn": str,
        "roleArn": str,
        "tags": NotRequired[Mapping[str, str]],
    },
)
RejectedLogEventsInfoTypeDef = TypedDict(
    "RejectedLogEventsInfoTypeDef",
    {
        "tooNewLogEventStartIndex": NotRequired[int],
        "tooOldLogEventEndIndex": NotRequired[int],
        "expiredLogEventEndIndex": NotRequired[int],
    },
)
PutQueryDefinitionRequestRequestTypeDef = TypedDict(
    "PutQueryDefinitionRequestRequestTypeDef",
    {
        "name": str,
        "queryString": str,
        "queryDefinitionId": NotRequired[str],
        "logGroupNames": NotRequired[Sequence[str]],
        "clientToken": NotRequired[str],
    },
)
PutResourcePolicyRequestRequestTypeDef = TypedDict(
    "PutResourcePolicyRequestRequestTypeDef",
    {
        "policyName": NotRequired[str],
        "policyDocument": NotRequired[str],
    },
)
PutRetentionPolicyRequestRequestTypeDef = TypedDict(
    "PutRetentionPolicyRequestRequestTypeDef",
    {
        "logGroupName": str,
        "retentionInDays": int,
    },
)
PutSubscriptionFilterRequestRequestTypeDef = TypedDict(
    "PutSubscriptionFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
        "filterPattern": str,
        "destinationArn": str,
        "roleArn": NotRequired[str],
        "distribution": NotRequired[DistributionType],
    },
)
SessionStreamingExceptionTypeDef = TypedDict(
    "SessionStreamingExceptionTypeDef",
    {
        "message": NotRequired[str],
    },
)
SessionTimeoutExceptionTypeDef = TypedDict(
    "SessionTimeoutExceptionTypeDef",
    {
        "message": NotRequired[str],
    },
)
StartLiveTailRequestRequestTypeDef = TypedDict(
    "StartLiveTailRequestRequestTypeDef",
    {
        "logGroupIdentifiers": Sequence[str],
        "logStreamNames": NotRequired[Sequence[str]],
        "logStreamNamePrefixes": NotRequired[Sequence[str]],
        "logEventFilterPattern": NotRequired[str],
    },
)
StartQueryRequestRequestTypeDef = TypedDict(
    "StartQueryRequestRequestTypeDef",
    {
        "startTime": int,
        "endTime": int,
        "queryString": str,
        "logGroupName": NotRequired[str],
        "logGroupNames": NotRequired[Sequence[str]],
        "logGroupIdentifiers": NotRequired[Sequence[str]],
        "limit": NotRequired[int],
    },
)
StopQueryRequestRequestTypeDef = TypedDict(
    "StopQueryRequestRequestTypeDef",
    {
        "queryId": str,
    },
)
SuppressionPeriodTypeDef = TypedDict(
    "SuppressionPeriodTypeDef",
    {
        "value": NotRequired[int],
        "suppressionUnit": NotRequired[SuppressionUnitType],
    },
)
TagLogGroupRequestRequestTypeDef = TypedDict(
    "TagLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
        "tags": Mapping[str, str],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Mapping[str, str],
    },
)
TestMetricFilterRequestRequestTypeDef = TypedDict(
    "TestMetricFilterRequestRequestTypeDef",
    {
        "filterPattern": str,
        "logEventMessages": Sequence[str],
    },
)
UntagLogGroupRequestRequestTypeDef = TypedDict(
    "UntagLogGroupRequestRequestTypeDef",
    {
        "logGroupName": str,
        "tags": Sequence[str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateLogAnomalyDetectorRequestRequestTypeDef = TypedDict(
    "UpdateLogAnomalyDetectorRequestRequestTypeDef",
    {
        "anomalyDetectorArn": str,
        "enabled": bool,
        "evaluationFrequency": NotRequired[EvaluationFrequencyType],
        "filterPattern": NotRequired[str],
        "anomalyVisibilityTime": NotRequired[int],
    },
)
AnomalyTypeDef = TypedDict(
    "AnomalyTypeDef",
    {
        "anomalyId": str,
        "patternId": str,
        "anomalyDetectorArn": str,
        "patternString": str,
        "firstSeen": int,
        "lastSeen": int,
        "description": str,
        "active": bool,
        "state": StateType,
        "histogram": Dict[str, int],
        "logSamples": List[str],
        "patternTokens": List[PatternTokenTypeDef],
        "logGroupArnList": List[str],
        "patternRegex": NotRequired[str],
        "priority": NotRequired[str],
        "suppressed": NotRequired[bool],
        "suppressedDate": NotRequired[int],
        "suppressedUntil": NotRequired[int],
        "isPatternLevelSuppression": NotRequired[bool],
    },
)
CreateDeliveryResponseTypeDef = TypedDict(
    "CreateDeliveryResponseTypeDef",
    {
        "delivery": DeliveryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateExportTaskResponseTypeDef = TypedDict(
    "CreateExportTaskResponseTypeDef",
    {
        "taskId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateLogAnomalyDetectorResponseTypeDef = TypedDict(
    "CreateLogAnomalyDetectorResponseTypeDef",
    {
        "anomalyDetectorArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteQueryDefinitionResponseTypeDef = TypedDict(
    "DeleteQueryDefinitionResponseTypeDef",
    {
        "success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeAccountPoliciesResponseTypeDef = TypedDict(
    "DescribeAccountPoliciesResponseTypeDef",
    {
        "accountPolicies": List[AccountPolicyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDeliveriesResponseTypeDef = TypedDict(
    "DescribeDeliveriesResponseTypeDef",
    {
        "deliveries": List[DeliveryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDataProtectionPolicyResponseTypeDef = TypedDict(
    "GetDataProtectionPolicyResponseTypeDef",
    {
        "logGroupIdentifier": str,
        "policyDocument": str,
        "lastUpdatedTime": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDeliveryResponseTypeDef = TypedDict(
    "GetDeliveryResponseTypeDef",
    {
        "delivery": DeliveryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLogAnomalyDetectorResponseTypeDef = TypedDict(
    "GetLogAnomalyDetectorResponseTypeDef",
    {
        "detectorName": str,
        "logGroupArnList": List[str],
        "evaluationFrequency": EvaluationFrequencyType,
        "filterPattern": str,
        "anomalyDetectorStatus": AnomalyDetectorStatusType,
        "kmsKeyId": str,
        "creationTimeStamp": int,
        "lastModifiedTimeStamp": int,
        "anomalyVisibilityTime": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLogRecordResponseTypeDef = TypedDict(
    "GetLogRecordResponseTypeDef",
    {
        "logRecord": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListLogAnomalyDetectorsResponseTypeDef = TypedDict(
    "ListLogAnomalyDetectorsResponseTypeDef",
    {
        "anomalyDetectors": List[AnomalyDetectorTypeDef],
        "nextToken": str,
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
ListTagsLogGroupResponseTypeDef = TypedDict(
    "ListTagsLogGroupResponseTypeDef",
    {
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutAccountPolicyResponseTypeDef = TypedDict(
    "PutAccountPolicyResponseTypeDef",
    {
        "accountPolicy": AccountPolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutDataProtectionPolicyResponseTypeDef = TypedDict(
    "PutDataProtectionPolicyResponseTypeDef",
    {
        "logGroupIdentifier": str,
        "policyDocument": str,
        "lastUpdatedTime": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutQueryDefinitionResponseTypeDef = TypedDict(
    "PutQueryDefinitionResponseTypeDef",
    {
        "queryDefinitionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartQueryResponseTypeDef = TypedDict(
    "StartQueryResponseTypeDef",
    {
        "queryId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopQueryResponseTypeDef = TypedDict(
    "StopQueryResponseTypeDef",
    {
        "success": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeliveryDestinationTypeDef = TypedDict(
    "DeliveryDestinationTypeDef",
    {
        "name": NotRequired[str],
        "arn": NotRequired[str],
        "deliveryDestinationType": NotRequired[DeliveryDestinationTypeType],
        "outputFormat": NotRequired[OutputFormatType],
        "deliveryDestinationConfiguration": NotRequired[DeliveryDestinationConfigurationTypeDef],
        "tags": NotRequired[Dict[str, str]],
    },
)
PutDeliveryDestinationRequestRequestTypeDef = TypedDict(
    "PutDeliveryDestinationRequestRequestTypeDef",
    {
        "name": str,
        "deliveryDestinationConfiguration": DeliveryDestinationConfigurationTypeDef,
        "outputFormat": NotRequired[OutputFormatType],
        "tags": NotRequired[Mapping[str, str]],
    },
)
DescribeDeliverySourcesResponseTypeDef = TypedDict(
    "DescribeDeliverySourcesResponseTypeDef",
    {
        "deliverySources": List[DeliverySourceTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDeliverySourceResponseTypeDef = TypedDict(
    "GetDeliverySourceResponseTypeDef",
    {
        "deliverySource": DeliverySourceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutDeliverySourceResponseTypeDef = TypedDict(
    "PutDeliverySourceResponseTypeDef",
    {
        "deliverySource": DeliverySourceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDeliveriesRequestDescribeDeliveriesPaginateTypeDef = TypedDict(
    "DescribeDeliveriesRequestDescribeDeliveriesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDeliveryDestinationsRequestDescribeDeliveryDestinationsPaginateTypeDef = TypedDict(
    "DescribeDeliveryDestinationsRequestDescribeDeliveryDestinationsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDeliverySourcesRequestDescribeDeliverySourcesPaginateTypeDef = TypedDict(
    "DescribeDeliverySourcesRequestDescribeDeliverySourcesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDestinationsRequestDescribeDestinationsPaginateTypeDef = TypedDict(
    "DescribeDestinationsRequestDescribeDestinationsPaginateTypeDef",
    {
        "DestinationNamePrefix": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeExportTasksRequestDescribeExportTasksPaginateTypeDef = TypedDict(
    "DescribeExportTasksRequestDescribeExportTasksPaginateTypeDef",
    {
        "taskId": NotRequired[str],
        "statusCode": NotRequired[ExportTaskStatusCodeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeLogGroupsRequestDescribeLogGroupsPaginateTypeDef = TypedDict(
    "DescribeLogGroupsRequestDescribeLogGroupsPaginateTypeDef",
    {
        "accountIdentifiers": NotRequired[Sequence[str]],
        "logGroupNamePrefix": NotRequired[str],
        "logGroupNamePattern": NotRequired[str],
        "includeLinkedAccounts": NotRequired[bool],
        "logGroupClass": NotRequired[LogGroupClassType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef = TypedDict(
    "DescribeLogStreamsRequestDescribeLogStreamsPaginateTypeDef",
    {
        "logGroupName": NotRequired[str],
        "logGroupIdentifier": NotRequired[str],
        "logStreamNamePrefix": NotRequired[str],
        "orderBy": NotRequired[OrderByType],
        "descending": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeMetricFiltersRequestDescribeMetricFiltersPaginateTypeDef = TypedDict(
    "DescribeMetricFiltersRequestDescribeMetricFiltersPaginateTypeDef",
    {
        "logGroupName": NotRequired[str],
        "filterNamePrefix": NotRequired[str],
        "metricName": NotRequired[str],
        "metricNamespace": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeQueriesRequestDescribeQueriesPaginateTypeDef = TypedDict(
    "DescribeQueriesRequestDescribeQueriesPaginateTypeDef",
    {
        "logGroupName": NotRequired[str],
        "status": NotRequired[QueryStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeResourcePoliciesRequestDescribeResourcePoliciesPaginateTypeDef = TypedDict(
    "DescribeResourcePoliciesRequestDescribeResourcePoliciesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef = TypedDict(
    "DescribeSubscriptionFiltersRequestDescribeSubscriptionFiltersPaginateTypeDef",
    {
        "logGroupName": str,
        "filterNamePrefix": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
FilterLogEventsRequestFilterLogEventsPaginateTypeDef = TypedDict(
    "FilterLogEventsRequestFilterLogEventsPaginateTypeDef",
    {
        "logGroupName": NotRequired[str],
        "logGroupIdentifier": NotRequired[str],
        "logStreamNames": NotRequired[Sequence[str]],
        "logStreamNamePrefix": NotRequired[str],
        "startTime": NotRequired[int],
        "endTime": NotRequired[int],
        "filterPattern": NotRequired[str],
        "interleaved": NotRequired[bool],
        "unmask": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAnomaliesRequestListAnomaliesPaginateTypeDef = TypedDict(
    "ListAnomaliesRequestListAnomaliesPaginateTypeDef",
    {
        "anomalyDetectorArn": NotRequired[str],
        "suppressionState": NotRequired[SuppressionStateType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListLogAnomalyDetectorsRequestListLogAnomalyDetectorsPaginateTypeDef = TypedDict(
    "ListLogAnomalyDetectorsRequestListLogAnomalyDetectorsPaginateTypeDef",
    {
        "filterLogGroupArn": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
DescribeDestinationsResponseTypeDef = TypedDict(
    "DescribeDestinationsResponseTypeDef",
    {
        "destinations": List[DestinationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutDestinationResponseTypeDef = TypedDict(
    "PutDestinationResponseTypeDef",
    {
        "destination": DestinationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLogGroupsResponseTypeDef = TypedDict(
    "DescribeLogGroupsResponseTypeDef",
    {
        "logGroups": List[LogGroupTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeLogStreamsResponseTypeDef = TypedDict(
    "DescribeLogStreamsResponseTypeDef",
    {
        "logStreams": List[LogStreamTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeQueriesResponseTypeDef = TypedDict(
    "DescribeQueriesResponseTypeDef",
    {
        "queries": List[QueryInfoTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeQueryDefinitionsResponseTypeDef = TypedDict(
    "DescribeQueryDefinitionsResponseTypeDef",
    {
        "queryDefinitions": List[QueryDefinitionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeResourcePoliciesResponseTypeDef = TypedDict(
    "DescribeResourcePoliciesResponseTypeDef",
    {
        "resourcePolicies": List[ResourcePolicyTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutResourcePolicyResponseTypeDef = TypedDict(
    "PutResourcePolicyResponseTypeDef",
    {
        "resourcePolicy": ResourcePolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSubscriptionFiltersResponseTypeDef = TypedDict(
    "DescribeSubscriptionFiltersResponseTypeDef",
    {
        "subscriptionFilters": List[SubscriptionFilterTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExportTaskTypeDef = TypedDict(
    "ExportTaskTypeDef",
    {
        "taskId": NotRequired[str],
        "taskName": NotRequired[str],
        "logGroupName": NotRequired[str],
        "from": NotRequired[int],
        "to": NotRequired[int],
        "destination": NotRequired[str],
        "destinationPrefix": NotRequired[str],
        "status": NotRequired[ExportTaskStatusTypeDef],
        "executionInfo": NotRequired[ExportTaskExecutionInfoTypeDef],
    },
)
FilterLogEventsResponseTypeDef = TypedDict(
    "FilterLogEventsResponseTypeDef",
    {
        "events": List[FilteredLogEventTypeDef],
        "searchedLogStreams": List[SearchedLogStreamTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDeliveryDestinationPolicyResponseTypeDef = TypedDict(
    "GetDeliveryDestinationPolicyResponseTypeDef",
    {
        "policy": PolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutDeliveryDestinationPolicyResponseTypeDef = TypedDict(
    "PutDeliveryDestinationPolicyResponseTypeDef",
    {
        "policy": PolicyTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLogEventsResponseTypeDef = TypedDict(
    "GetLogEventsResponseTypeDef",
    {
        "events": List[OutputLogEventTypeDef],
        "nextForwardToken": str,
        "nextBackwardToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLogGroupFieldsResponseTypeDef = TypedDict(
    "GetLogGroupFieldsResponseTypeDef",
    {
        "logGroupFields": List[LogGroupFieldTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetQueryResultsResponseTypeDef = TypedDict(
    "GetQueryResultsResponseTypeDef",
    {
        "results": List[List[ResultFieldTypeDef]],
        "statistics": QueryStatisticsTypeDef,
        "status": QueryStatusType,
        "encryptionKey": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutLogEventsRequestRequestTypeDef = TypedDict(
    "PutLogEventsRequestRequestTypeDef",
    {
        "logGroupName": str,
        "logStreamName": str,
        "logEvents": Sequence[InputLogEventTypeDef],
        "sequenceToken": NotRequired[str],
    },
)
LiveTailSessionUpdateTypeDef = TypedDict(
    "LiveTailSessionUpdateTypeDef",
    {
        "sessionMetadata": NotRequired[LiveTailSessionMetadataTypeDef],
        "sessionResults": NotRequired[List[LiveTailSessionLogEventTypeDef]],
    },
)
TestMetricFilterResponseTypeDef = TypedDict(
    "TestMetricFilterResponseTypeDef",
    {
        "matches": List[MetricFilterMatchRecordTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MetricFilterTypeDef = TypedDict(
    "MetricFilterTypeDef",
    {
        "filterName": NotRequired[str],
        "filterPattern": NotRequired[str],
        "metricTransformations": NotRequired[List[MetricTransformationTypeDef]],
        "creationTime": NotRequired[int],
        "logGroupName": NotRequired[str],
    },
)
PutMetricFilterRequestRequestTypeDef = TypedDict(
    "PutMetricFilterRequestRequestTypeDef",
    {
        "logGroupName": str,
        "filterName": str,
        "filterPattern": str,
        "metricTransformations": Sequence[MetricTransformationTypeDef],
    },
)
PutLogEventsResponseTypeDef = TypedDict(
    "PutLogEventsResponseTypeDef",
    {
        "nextSequenceToken": str,
        "rejectedLogEventsInfo": RejectedLogEventsInfoTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateAnomalyRequestRequestTypeDef = TypedDict(
    "UpdateAnomalyRequestRequestTypeDef",
    {
        "anomalyDetectorArn": str,
        "anomalyId": NotRequired[str],
        "patternId": NotRequired[str],
        "suppressionType": NotRequired[SuppressionTypeType],
        "suppressionPeriod": NotRequired[SuppressionPeriodTypeDef],
    },
)
ListAnomaliesResponseTypeDef = TypedDict(
    "ListAnomaliesResponseTypeDef",
    {
        "anomalies": List[AnomalyTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDeliveryDestinationsResponseTypeDef = TypedDict(
    "DescribeDeliveryDestinationsResponseTypeDef",
    {
        "deliveryDestinations": List[DeliveryDestinationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDeliveryDestinationResponseTypeDef = TypedDict(
    "GetDeliveryDestinationResponseTypeDef",
    {
        "deliveryDestination": DeliveryDestinationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutDeliveryDestinationResponseTypeDef = TypedDict(
    "PutDeliveryDestinationResponseTypeDef",
    {
        "deliveryDestination": DeliveryDestinationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeExportTasksResponseTypeDef = TypedDict(
    "DescribeExportTasksResponseTypeDef",
    {
        "exportTasks": List[ExportTaskTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartLiveTailResponseStreamTypeDef = TypedDict(
    "StartLiveTailResponseStreamTypeDef",
    {
        "sessionStart": NotRequired[LiveTailSessionStartTypeDef],
        "sessionUpdate": NotRequired[LiveTailSessionUpdateTypeDef],
        "SessionTimeoutException": NotRequired[SessionTimeoutExceptionTypeDef],
        "SessionStreamingException": NotRequired[SessionStreamingExceptionTypeDef],
    },
)
DescribeMetricFiltersResponseTypeDef = TypedDict(
    "DescribeMetricFiltersResponseTypeDef",
    {
        "metricFilters": List[MetricFilterTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartLiveTailResponseTypeDef = TypedDict(
    "StartLiveTailResponseTypeDef",
    {
        "responseStream": "EventStream[StartLiveTailResponseStreamTypeDef]",
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
