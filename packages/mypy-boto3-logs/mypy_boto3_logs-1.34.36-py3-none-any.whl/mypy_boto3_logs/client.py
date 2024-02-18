"""
Type annotations for logs service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_logs.client import CloudWatchLogsClient

    session = Session()
    client: CloudWatchLogsClient = session.client("logs")
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    DistributionType,
    EvaluationFrequencyType,
    ExportTaskStatusCodeType,
    LogGroupClassType,
    OrderByType,
    OutputFormatType,
    PolicyTypeType,
    QueryStatusType,
    SuppressionStateType,
    SuppressionTypeType,
)
from .paginator import (
    DescribeDeliveriesPaginator,
    DescribeDeliveryDestinationsPaginator,
    DescribeDeliverySourcesPaginator,
    DescribeDestinationsPaginator,
    DescribeExportTasksPaginator,
    DescribeLogGroupsPaginator,
    DescribeLogStreamsPaginator,
    DescribeMetricFiltersPaginator,
    DescribeQueriesPaginator,
    DescribeResourcePoliciesPaginator,
    DescribeSubscriptionFiltersPaginator,
    FilterLogEventsPaginator,
    ListAnomaliesPaginator,
    ListLogAnomalyDetectorsPaginator,
)
from .type_defs import (
    CreateDeliveryResponseTypeDef,
    CreateExportTaskResponseTypeDef,
    CreateLogAnomalyDetectorResponseTypeDef,
    DeleteQueryDefinitionResponseTypeDef,
    DeliveryDestinationConfigurationTypeDef,
    DescribeAccountPoliciesResponseTypeDef,
    DescribeDeliveriesResponseTypeDef,
    DescribeDeliveryDestinationsResponseTypeDef,
    DescribeDeliverySourcesResponseTypeDef,
    DescribeDestinationsResponseTypeDef,
    DescribeExportTasksResponseTypeDef,
    DescribeLogGroupsResponseTypeDef,
    DescribeLogStreamsResponseTypeDef,
    DescribeMetricFiltersResponseTypeDef,
    DescribeQueriesResponseTypeDef,
    DescribeQueryDefinitionsResponseTypeDef,
    DescribeResourcePoliciesResponseTypeDef,
    DescribeSubscriptionFiltersResponseTypeDef,
    EmptyResponseMetadataTypeDef,
    FilterLogEventsResponseTypeDef,
    GetDataProtectionPolicyResponseTypeDef,
    GetDeliveryDestinationPolicyResponseTypeDef,
    GetDeliveryDestinationResponseTypeDef,
    GetDeliveryResponseTypeDef,
    GetDeliverySourceResponseTypeDef,
    GetLogAnomalyDetectorResponseTypeDef,
    GetLogEventsResponseTypeDef,
    GetLogGroupFieldsResponseTypeDef,
    GetLogRecordResponseTypeDef,
    GetQueryResultsResponseTypeDef,
    InputLogEventTypeDef,
    ListAnomaliesResponseTypeDef,
    ListLogAnomalyDetectorsResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListTagsLogGroupResponseTypeDef,
    MetricTransformationTypeDef,
    PutAccountPolicyResponseTypeDef,
    PutDataProtectionPolicyResponseTypeDef,
    PutDeliveryDestinationPolicyResponseTypeDef,
    PutDeliveryDestinationResponseTypeDef,
    PutDeliverySourceResponseTypeDef,
    PutDestinationResponseTypeDef,
    PutLogEventsResponseTypeDef,
    PutQueryDefinitionResponseTypeDef,
    PutResourcePolicyResponseTypeDef,
    StartLiveTailResponseTypeDef,
    StartQueryResponseTypeDef,
    StopQueryResponseTypeDef,
    SuppressionPeriodTypeDef,
    TestMetricFilterResponseTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("CloudWatchLogsClient",)


class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str


class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    DataAlreadyAcceptedException: Type[BotocoreClientError]
    InvalidOperationException: Type[BotocoreClientError]
    InvalidParameterException: Type[BotocoreClientError]
    InvalidSequenceTokenException: Type[BotocoreClientError]
    LimitExceededException: Type[BotocoreClientError]
    MalformedQueryException: Type[BotocoreClientError]
    OperationAbortedException: Type[BotocoreClientError]
    ResourceAlreadyExistsException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ServiceUnavailableException: Type[BotocoreClientError]
    SessionStreamingException: Type[BotocoreClientError]
    SessionTimeoutException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    TooManyTagsException: Type[BotocoreClientError]
    UnrecognizedClientException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]


class CloudWatchLogsClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        CloudWatchLogsClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#exceptions)
        """

    def associate_kms_key(
        self, *, kmsKeyId: str, logGroupName: str = ..., resourceIdentifier: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Associates the specified KMS key with either one log group in the account, or
        with all stored CloudWatch Logs query insights results in the
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.associate_kms_key)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#associate_kms_key)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#can_paginate)
        """

    def cancel_export_task(self, *, taskId: str) -> EmptyResponseMetadataTypeDef:
        """
        Cancels the specified export task.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.cancel_export_task)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#cancel_export_task)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#close)
        """

    def create_delivery(
        self, *, deliverySourceName: str, deliveryDestinationArn: str, tags: Mapping[str, str] = ...
    ) -> CreateDeliveryResponseTypeDef:
        """
        Creates a *delivery*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.create_delivery)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#create_delivery)
        """

    def create_export_task(
        self,
        *,
        logGroupName: str,
        fromTime: int,
        to: int,
        destination: str,
        taskName: str = ...,
        logStreamNamePrefix: str = ...,
        destinationPrefix: str = ...,
    ) -> CreateExportTaskResponseTypeDef:
        """
        Creates an export task so that you can efficiently export data from a log group
        to an Amazon S3
        bucket.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.create_export_task)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#create_export_task)
        """

    def create_log_anomaly_detector(
        self,
        *,
        logGroupArnList: Sequence[str],
        detectorName: str = ...,
        evaluationFrequency: EvaluationFrequencyType = ...,
        filterPattern: str = ...,
        kmsKeyId: str = ...,
        anomalyVisibilityTime: int = ...,
        tags: Mapping[str, str] = ...,
    ) -> CreateLogAnomalyDetectorResponseTypeDef:
        """
        Creates an *anomaly detector* that regularly scans one or more log groups and
        look for patterns and anomalies in the
        logs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.create_log_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#create_log_anomaly_detector)
        """

    def create_log_group(
        self,
        *,
        logGroupName: str,
        kmsKeyId: str = ...,
        tags: Mapping[str, str] = ...,
        logGroupClass: LogGroupClassType = ...,
    ) -> EmptyResponseMetadataTypeDef:
        """
        Creates a log group with the specified name.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.create_log_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#create_log_group)
        """

    def create_log_stream(
        self, *, logGroupName: str, logStreamName: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Creates a log stream for the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.create_log_stream)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#create_log_stream)
        """

    def delete_account_policy(
        self, *, policyName: str, policyType: PolicyTypeType
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a CloudWatch Logs account policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_account_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_account_policy)
        """

    def delete_data_protection_policy(
        self, *, logGroupIdentifier: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the data protection policy from the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_data_protection_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_data_protection_policy)
        """

    def delete_delivery(self, *, id: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes s *delivery*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_delivery)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_delivery)
        """

    def delete_delivery_destination(self, *, name: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a *delivery destination*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_delivery_destination)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_delivery_destination)
        """

    def delete_delivery_destination_policy(
        self, *, deliveryDestinationName: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a delivery destination policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_delivery_destination_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_delivery_destination_policy)
        """

    def delete_delivery_source(self, *, name: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a *delivery source*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_delivery_source)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_delivery_source)
        """

    def delete_destination(self, *, destinationName: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified destination, and eventually disables all the subscription
        filters that publish to
        it.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_destination)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_destination)
        """

    def delete_log_anomaly_detector(
        self, *, anomalyDetectorArn: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified CloudWatch Logs anomaly detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_log_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_log_anomaly_detector)
        """

    def delete_log_group(self, *, logGroupName: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified log group and permanently deletes all the archived log
        events associated with the log
        group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_log_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_log_group)
        """

    def delete_log_stream(
        self, *, logGroupName: str, logStreamName: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified log stream and permanently deletes all the archived log
        events associated with the log
        stream.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_log_stream)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_log_stream)
        """

    def delete_metric_filter(
        self, *, logGroupName: str, filterName: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified metric filter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_metric_filter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_metric_filter)
        """

    def delete_query_definition(
        self, *, queryDefinitionId: str
    ) -> DeleteQueryDefinitionResponseTypeDef:
        """
        Deletes a saved CloudWatch Logs Insights query definition.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_query_definition)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_query_definition)
        """

    def delete_resource_policy(self, *, policyName: str = ...) -> EmptyResponseMetadataTypeDef:
        """
        Deletes a resource policy from this account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_resource_policy)
        """

    def delete_retention_policy(self, *, logGroupName: str) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified retention policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_retention_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_retention_policy)
        """

    def delete_subscription_filter(
        self, *, logGroupName: str, filterName: str
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the specified subscription filter.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_subscription_filter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#delete_subscription_filter)
        """

    def describe_account_policies(
        self,
        *,
        policyType: PolicyTypeType,
        policyName: str = ...,
        accountIdentifiers: Sequence[str] = ...,
    ) -> DescribeAccountPoliciesResponseTypeDef:
        """
        Returns a list of all CloudWatch Logs account policies in the account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_account_policies)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_account_policies)
        """

    def describe_deliveries(
        self, *, nextToken: str = ..., limit: int = ...
    ) -> DescribeDeliveriesResponseTypeDef:
        """
        Retrieves a list of the deliveries that have been created in the account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_deliveries)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_deliveries)
        """

    def describe_delivery_destinations(
        self, *, nextToken: str = ..., limit: int = ...
    ) -> DescribeDeliveryDestinationsResponseTypeDef:
        """
        Retrieves a list of the delivery destinations that have been created in the
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_delivery_destinations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_delivery_destinations)
        """

    def describe_delivery_sources(
        self, *, nextToken: str = ..., limit: int = ...
    ) -> DescribeDeliverySourcesResponseTypeDef:
        """
        Retrieves a list of the delivery sources that have been created in the account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_delivery_sources)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_delivery_sources)
        """

    def describe_destinations(
        self, *, DestinationNamePrefix: str = ..., nextToken: str = ..., limit: int = ...
    ) -> DescribeDestinationsResponseTypeDef:
        """
        Lists all your destinations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_destinations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_destinations)
        """

    def describe_export_tasks(
        self,
        *,
        taskId: str = ...,
        statusCode: ExportTaskStatusCodeType = ...,
        nextToken: str = ...,
        limit: int = ...,
    ) -> DescribeExportTasksResponseTypeDef:
        """
        Lists the specified export tasks.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_export_tasks)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_export_tasks)
        """

    def describe_log_groups(
        self,
        *,
        accountIdentifiers: Sequence[str] = ...,
        logGroupNamePrefix: str = ...,
        logGroupNamePattern: str = ...,
        nextToken: str = ...,
        limit: int = ...,
        includeLinkedAccounts: bool = ...,
        logGroupClass: LogGroupClassType = ...,
    ) -> DescribeLogGroupsResponseTypeDef:
        """
        Lists the specified log groups.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_log_groups)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_log_groups)
        """

    def describe_log_streams(
        self,
        *,
        logGroupName: str = ...,
        logGroupIdentifier: str = ...,
        logStreamNamePrefix: str = ...,
        orderBy: OrderByType = ...,
        descending: bool = ...,
        nextToken: str = ...,
        limit: int = ...,
    ) -> DescribeLogStreamsResponseTypeDef:
        """
        Lists the log streams for the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_log_streams)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_log_streams)
        """

    def describe_metric_filters(
        self,
        *,
        logGroupName: str = ...,
        filterNamePrefix: str = ...,
        nextToken: str = ...,
        limit: int = ...,
        metricName: str = ...,
        metricNamespace: str = ...,
    ) -> DescribeMetricFiltersResponseTypeDef:
        """
        Lists the specified metric filters.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_metric_filters)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_metric_filters)
        """

    def describe_queries(
        self,
        *,
        logGroupName: str = ...,
        status: QueryStatusType = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> DescribeQueriesResponseTypeDef:
        """
        Returns a list of CloudWatch Logs Insights queries that are scheduled, running,
        or have been run recently in this
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_queries)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_queries)
        """

    def describe_query_definitions(
        self, *, queryDefinitionNamePrefix: str = ..., maxResults: int = ..., nextToken: str = ...
    ) -> DescribeQueryDefinitionsResponseTypeDef:
        """
        This operation returns a paginated list of your saved CloudWatch Logs Insights
        query
        definitions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_query_definitions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_query_definitions)
        """

    def describe_resource_policies(
        self, *, nextToken: str = ..., limit: int = ...
    ) -> DescribeResourcePoliciesResponseTypeDef:
        """
        Lists the resource policies in this account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_resource_policies)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_resource_policies)
        """

    def describe_subscription_filters(
        self,
        *,
        logGroupName: str,
        filterNamePrefix: str = ...,
        nextToken: str = ...,
        limit: int = ...,
    ) -> DescribeSubscriptionFiltersResponseTypeDef:
        """
        Lists the subscription filters for the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.describe_subscription_filters)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#describe_subscription_filters)
        """

    def disassociate_kms_key(
        self, *, logGroupName: str = ..., resourceIdentifier: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Disassociates the specified KMS key from the specified log group or from all
        CloudWatch Logs Insights query results in the
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.disassociate_kms_key)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#disassociate_kms_key)
        """

    def filter_log_events(
        self,
        *,
        logGroupName: str = ...,
        logGroupIdentifier: str = ...,
        logStreamNames: Sequence[str] = ...,
        logStreamNamePrefix: str = ...,
        startTime: int = ...,
        endTime: int = ...,
        filterPattern: str = ...,
        nextToken: str = ...,
        limit: int = ...,
        interleaved: bool = ...,
        unmask: bool = ...,
    ) -> FilterLogEventsResponseTypeDef:
        """
        Lists log events from the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.filter_log_events)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#filter_log_events)
        """

    def generate_presigned_url(
        self,
        ClientMethod: str,
        Params: Mapping[str, Any] = ...,
        ExpiresIn: int = 3600,
        HttpMethod: str = ...,
    ) -> str:
        """
        Generate a presigned url given a client, its method, and arguments.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#generate_presigned_url)
        """

    def get_data_protection_policy(
        self, *, logGroupIdentifier: str
    ) -> GetDataProtectionPolicyResponseTypeDef:
        """
        Returns information about a log group data protection policy.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_data_protection_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_data_protection_policy)
        """

    def get_delivery(self, *, id: str) -> GetDeliveryResponseTypeDef:
        """
        Returns complete information about one logical *delivery*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_delivery)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_delivery)
        """

    def get_delivery_destination(self, *, name: str) -> GetDeliveryDestinationResponseTypeDef:
        """
        Retrieves complete information about one delivery destination.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_delivery_destination)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_delivery_destination)
        """

    def get_delivery_destination_policy(
        self, *, deliveryDestinationName: str
    ) -> GetDeliveryDestinationPolicyResponseTypeDef:
        """
        Retrieves the delivery destination policy assigned to the delivery destination
        that you
        specify.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_delivery_destination_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_delivery_destination_policy)
        """

    def get_delivery_source(self, *, name: str) -> GetDeliverySourceResponseTypeDef:
        """
        Retrieves complete information about one delivery source.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_delivery_source)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_delivery_source)
        """

    def get_log_anomaly_detector(
        self, *, anomalyDetectorArn: str
    ) -> GetLogAnomalyDetectorResponseTypeDef:
        """
        Retrieves information about the log anomaly detector that you specify.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_log_anomaly_detector)
        """

    def get_log_events(
        self,
        *,
        logStreamName: str,
        logGroupName: str = ...,
        logGroupIdentifier: str = ...,
        startTime: int = ...,
        endTime: int = ...,
        nextToken: str = ...,
        limit: int = ...,
        startFromHead: bool = ...,
        unmask: bool = ...,
    ) -> GetLogEventsResponseTypeDef:
        """
        Lists log events from the specified log stream.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_events)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_log_events)
        """

    def get_log_group_fields(
        self, *, logGroupName: str = ..., time: int = ..., logGroupIdentifier: str = ...
    ) -> GetLogGroupFieldsResponseTypeDef:
        """
        Returns a list of the fields that are included in log events in the specified
        log
        group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_group_fields)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_log_group_fields)
        """

    def get_log_record(
        self, *, logRecordPointer: str, unmask: bool = ...
    ) -> GetLogRecordResponseTypeDef:
        """
        Retrieves all of the fields and values of a single log event.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_log_record)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_log_record)
        """

    def get_query_results(self, *, queryId: str) -> GetQueryResultsResponseTypeDef:
        """
        Returns the results from the specified query.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_query_results)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_query_results)
        """

    def list_anomalies(
        self,
        *,
        anomalyDetectorArn: str = ...,
        suppressionState: SuppressionStateType = ...,
        limit: int = ...,
        nextToken: str = ...,
    ) -> ListAnomaliesResponseTypeDef:
        """
        Returns a list of anomalies that log anomaly detectors have found.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.list_anomalies)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#list_anomalies)
        """

    def list_log_anomaly_detectors(
        self, *, filterLogGroupArn: str = ..., limit: int = ..., nextToken: str = ...
    ) -> ListLogAnomalyDetectorsResponseTypeDef:
        """
        Retrieves a list of the log anomaly detectors in the account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.list_log_anomaly_detectors)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#list_log_anomaly_detectors)
        """

    def list_tags_for_resource(self, *, resourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        Displays the tags associated with a CloudWatch Logs resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#list_tags_for_resource)
        """

    def list_tags_log_group(self, *, logGroupName: str) -> ListTagsLogGroupResponseTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.list_tags_log_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#list_tags_log_group)
        """

    def put_account_policy(
        self,
        *,
        policyName: str,
        policyDocument: str,
        policyType: PolicyTypeType,
        scope: Literal["ALL"] = ...,
        selectionCriteria: str = ...,
    ) -> PutAccountPolicyResponseTypeDef:
        """
        Creates an account-level data protection policy or subscription filter policy
        that applies to all log groups or a subset of log groups in the
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_account_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_account_policy)
        """

    def put_data_protection_policy(
        self, *, logGroupIdentifier: str, policyDocument: str
    ) -> PutDataProtectionPolicyResponseTypeDef:
        """
        Creates a data protection policy for the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_data_protection_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_data_protection_policy)
        """

    def put_delivery_destination(
        self,
        *,
        name: str,
        deliveryDestinationConfiguration: DeliveryDestinationConfigurationTypeDef,
        outputFormat: OutputFormatType = ...,
        tags: Mapping[str, str] = ...,
    ) -> PutDeliveryDestinationResponseTypeDef:
        """
        Creates or updates a logical *delivery destination*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_delivery_destination)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_delivery_destination)
        """

    def put_delivery_destination_policy(
        self, *, deliveryDestinationName: str, deliveryDestinationPolicy: str
    ) -> PutDeliveryDestinationPolicyResponseTypeDef:
        """
        Creates and assigns an IAM policy that grants permissions to CloudWatch Logs to
        deliver logs cross-account to a specified destination in this
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_delivery_destination_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_delivery_destination_policy)
        """

    def put_delivery_source(
        self, *, name: str, resourceArn: str, logType: str, tags: Mapping[str, str] = ...
    ) -> PutDeliverySourceResponseTypeDef:
        """
        Creates or updates a logical *delivery source*.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_delivery_source)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_delivery_source)
        """

    def put_destination(
        self, *, destinationName: str, targetArn: str, roleArn: str, tags: Mapping[str, str] = ...
    ) -> PutDestinationResponseTypeDef:
        """
        Creates or updates a destination.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_destination)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_destination)
        """

    def put_destination_policy(
        self, *, destinationName: str, accessPolicy: str, forceUpdate: bool = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Creates or updates an access policy associated with an existing destination.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_destination_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_destination_policy)
        """

    def put_log_events(
        self,
        *,
        logGroupName: str,
        logStreamName: str,
        logEvents: Sequence[InputLogEventTypeDef],
        sequenceToken: str = ...,
    ) -> PutLogEventsResponseTypeDef:
        """
        Uploads a batch of log events to the specified log stream.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_log_events)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_log_events)
        """

    def put_metric_filter(
        self,
        *,
        logGroupName: str,
        filterName: str,
        filterPattern: str,
        metricTransformations: Sequence[MetricTransformationTypeDef],
    ) -> EmptyResponseMetadataTypeDef:
        """
        Creates or updates a metric filter and associates it with the specified log
        group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_metric_filter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_metric_filter)
        """

    def put_query_definition(
        self,
        *,
        name: str,
        queryString: str,
        queryDefinitionId: str = ...,
        logGroupNames: Sequence[str] = ...,
        clientToken: str = ...,
    ) -> PutQueryDefinitionResponseTypeDef:
        """
        Creates or updates a query definition for CloudWatch Logs Insights.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_query_definition)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_query_definition)
        """

    def put_resource_policy(
        self, *, policyName: str = ..., policyDocument: str = ...
    ) -> PutResourcePolicyResponseTypeDef:
        """
        Creates or updates a resource policy allowing other Amazon Web Services
        services to put log events to this account, such as Amazon Route
        53.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_resource_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_resource_policy)
        """

    def put_retention_policy(
        self, *, logGroupName: str, retentionInDays: int
    ) -> EmptyResponseMetadataTypeDef:
        """
        Sets the retention of the specified log group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_retention_policy)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_retention_policy)
        """

    def put_subscription_filter(
        self,
        *,
        logGroupName: str,
        filterName: str,
        filterPattern: str,
        destinationArn: str,
        roleArn: str = ...,
        distribution: DistributionType = ...,
    ) -> EmptyResponseMetadataTypeDef:
        """
        Creates or updates a subscription filter and associates it with the specified
        log
        group.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.put_subscription_filter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#put_subscription_filter)
        """

    def start_live_tail(
        self,
        *,
        logGroupIdentifiers: Sequence[str],
        logStreamNames: Sequence[str] = ...,
        logStreamNamePrefixes: Sequence[str] = ...,
        logEventFilterPattern: str = ...,
    ) -> StartLiveTailResponseTypeDef:
        """
        Starts a Live Tail streaming session for one or more log groups.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.start_live_tail)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#start_live_tail)
        """

    def start_query(
        self,
        *,
        startTime: int,
        endTime: int,
        queryString: str,
        logGroupName: str = ...,
        logGroupNames: Sequence[str] = ...,
        logGroupIdentifiers: Sequence[str] = ...,
        limit: int = ...,
    ) -> StartQueryResponseTypeDef:
        """
        Schedules a query of a log group using CloudWatch Logs Insights.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.start_query)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#start_query)
        """

    def stop_query(self, *, queryId: str) -> StopQueryResponseTypeDef:
        """
        Stops a CloudWatch Logs Insights query that is in progress.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.stop_query)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#stop_query)
        """

    def tag_log_group(
        self, *, logGroupName: str, tags: Mapping[str, str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.tag_log_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#tag_log_group)
        """

    def tag_resource(
        self, *, resourceArn: str, tags: Mapping[str, str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Assigns one or more tags (key-value pairs) to the specified CloudWatch Logs
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#tag_resource)
        """

    def test_metric_filter(
        self, *, filterPattern: str, logEventMessages: Sequence[str]
    ) -> TestMetricFilterResponseTypeDef:
        """
        Tests the filter pattern of a metric filter against a sample of log event
        messages.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.test_metric_filter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#test_metric_filter)
        """

    def untag_log_group(
        self, *, logGroupName: str, tags: Sequence[str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        .

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.untag_log_group)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#untag_log_group)
        """

    def untag_resource(
        self, *, resourceArn: str, tagKeys: Sequence[str]
    ) -> EmptyResponseMetadataTypeDef:
        """
        Removes one or more tags from the specified resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#untag_resource)
        """

    def update_anomaly(
        self,
        *,
        anomalyDetectorArn: str,
        anomalyId: str = ...,
        patternId: str = ...,
        suppressionType: SuppressionTypeType = ...,
        suppressionPeriod: SuppressionPeriodTypeDef = ...,
    ) -> EmptyResponseMetadataTypeDef:
        """
        Use this operation to *suppress* anomaly detection for a specified anomaly or
        pattern.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.update_anomaly)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#update_anomaly)
        """

    def update_log_anomaly_detector(
        self,
        *,
        anomalyDetectorArn: str,
        enabled: bool,
        evaluationFrequency: EvaluationFrequencyType = ...,
        filterPattern: str = ...,
        anomalyVisibilityTime: int = ...,
    ) -> EmptyResponseMetadataTypeDef:
        """
        Updates an existing log anomaly detector.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.update_log_anomaly_detector)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#update_log_anomaly_detector)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_deliveries"]
    ) -> DescribeDeliveriesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_delivery_destinations"]
    ) -> DescribeDeliveryDestinationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_delivery_sources"]
    ) -> DescribeDeliverySourcesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_destinations"]
    ) -> DescribeDestinationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_export_tasks"]
    ) -> DescribeExportTasksPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_log_groups"]
    ) -> DescribeLogGroupsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_log_streams"]
    ) -> DescribeLogStreamsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_metric_filters"]
    ) -> DescribeMetricFiltersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_queries"]
    ) -> DescribeQueriesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_resource_policies"]
    ) -> DescribeResourcePoliciesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["describe_subscription_filters"]
    ) -> DescribeSubscriptionFiltersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["filter_log_events"]
    ) -> FilterLogEventsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_anomalies"]) -> ListAnomaliesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_log_anomaly_detectors"]
    ) -> ListLogAnomalyDetectorsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/logs.html#CloudWatchLogs.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_logs/client/#get_paginator)
        """
