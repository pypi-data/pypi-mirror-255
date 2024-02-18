"""
Type annotations for iot service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_iot/type_defs/)

Usage::

    ```python
    from mypy_boto3_iot.type_defs import AbortCriteriaTypeDef

    data: AbortCriteriaTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    ActionTypeType,
    AggregationTypeNameType,
    AuditCheckRunStatusType,
    AuditFindingSeverityType,
    AuditFrequencyType,
    AuditMitigationActionsExecutionStatusType,
    AuditMitigationActionsTaskStatusType,
    AuditTaskStatusType,
    AuditTaskTypeType,
    AuthDecisionType,
    AuthorizerStatusType,
    AutoRegistrationStatusType,
    AwsJobAbortCriteriaFailureTypeType,
    BehaviorCriteriaTypeType,
    CACertificateStatusType,
    CannedAccessControlListType,
    CertificateModeType,
    CertificateStatusType,
    ComparisonOperatorType,
    ConfidenceLevelType,
    CustomMetricTypeType,
    DayOfWeekType,
    DetectMitigationActionExecutionStatusType,
    DetectMitigationActionsTaskStatusType,
    DeviceDefenderIndexingModeType,
    DimensionValueOperatorType,
    DomainConfigurationStatusType,
    DomainTypeType,
    DynamicGroupStatusType,
    DynamoKeyTypeType,
    EventTypeType,
    FieldTypeType,
    FleetMetricUnitType,
    IndexStatusType,
    JobEndBehaviorType,
    JobExecutionFailureTypeType,
    JobExecutionStatusType,
    JobStatusType,
    LogLevelType,
    LogTargetTypeType,
    MessageFormatType,
    MitigationActionTypeType,
    ModelStatusType,
    NamedShadowIndexingModeType,
    OTAUpdateStatusType,
    PackageVersionActionType,
    PackageVersionStatusType,
    ProtocolType,
    ReportTypeType,
    ResourceTypeType,
    RetryableFailureTypeType,
    ServerCertificateStatusType,
    ServiceTypeType,
    StatusType,
    TargetFieldOrderType,
    TargetSelectionType,
    TemplateTypeType,
    ThingConnectivityIndexingModeType,
    ThingGroupIndexingModeType,
    ThingIndexingModeType,
    TopicRuleDestinationStatusType,
    VerificationStateType,
    ViolationEventTypeType,
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
    "AbortCriteriaTypeDef",
    "AcceptCertificateTransferRequestRequestTypeDef",
    "CloudwatchAlarmActionTypeDef",
    "CloudwatchLogsActionTypeDef",
    "CloudwatchMetricActionTypeDef",
    "DynamoDBActionTypeDef",
    "ElasticsearchActionTypeDef",
    "FirehoseActionTypeDef",
    "IotAnalyticsActionTypeDef",
    "IotEventsActionTypeDef",
    "KinesisActionTypeDef",
    "LambdaActionTypeDef",
    "OpenSearchActionTypeDef",
    "S3ActionTypeDef",
    "SalesforceActionTypeDef",
    "SnsActionTypeDef",
    "SqsActionTypeDef",
    "StepFunctionsActionTypeDef",
    "MetricValuePaginatorTypeDef",
    "ViolationEventAdditionalInfoTypeDef",
    "MetricValueTypeDef",
    "AddThingToBillingGroupRequestRequestTypeDef",
    "AddThingToThingGroupRequestRequestTypeDef",
    "AddThingsToThingGroupParamsPaginatorTypeDef",
    "AddThingsToThingGroupParamsTypeDef",
    "AggregationTypeTypeDef",
    "AlertTargetTypeDef",
    "PolicyTypeDef",
    "AssetPropertyTimestampTypeDef",
    "AssetPropertyVariantTypeDef",
    "AssociateTargetsWithJobRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AttachPolicyRequestRequestTypeDef",
    "AttachPrincipalPolicyRequestRequestTypeDef",
    "AttachSecurityProfileRequestRequestTypeDef",
    "AttachThingPrincipalRequestRequestTypeDef",
    "AttributePayloadTypeDef",
    "AuditCheckConfigurationTypeDef",
    "AuditCheckDetailsTypeDef",
    "AuditMitigationActionExecutionMetadataTypeDef",
    "AuditMitigationActionsTaskMetadataTypeDef",
    "AuditMitigationActionsTaskTargetTypeDef",
    "AuditNotificationTargetTypeDef",
    "AuditTaskMetadataTypeDef",
    "AuthInfoTypeDef",
    "AuthorizerConfigTypeDef",
    "AuthorizerDescriptionTypeDef",
    "AuthorizerSummaryTypeDef",
    "AwsJobAbortCriteriaTypeDef",
    "AwsJobRateIncreaseCriteriaTypeDef",
    "AwsJobPresignedUrlConfigTypeDef",
    "AwsJobTimeoutConfigTypeDef",
    "MachineLearningDetectionConfigTypeDef",
    "StatisticalThresholdTypeDef",
    "BehaviorModelTrainingSummaryTypeDef",
    "MetricDimensionTypeDef",
    "BillingGroupMetadataTypeDef",
    "BillingGroupPropertiesTypeDef",
    "BlobTypeDef",
    "BucketTypeDef",
    "TermsAggregationTypeDef",
    "CertificateValidityTypeDef",
    "CACertificateTypeDef",
    "CancelAuditMitigationActionsTaskRequestRequestTypeDef",
    "CancelAuditTaskRequestRequestTypeDef",
    "CancelCertificateTransferRequestRequestTypeDef",
    "CancelDetectMitigationActionsTaskRequestRequestTypeDef",
    "CancelJobExecutionRequestRequestTypeDef",
    "CancelJobRequestRequestTypeDef",
    "TransferDataTypeDef",
    "CertificateProviderSummaryTypeDef",
    "CertificateTypeDef",
    "CodeSigningCertificateChainTypeDef",
    "ConfigurationTypeDef",
    "ConfirmTopicRuleDestinationRequestRequestTypeDef",
    "TimestampTypeDef",
    "TagTypeDef",
    "CreateCertificateFromCsrRequestRequestTypeDef",
    "ServerCertificateConfigTypeDef",
    "TlsConfigTypeDef",
    "PresignedUrlConfigTypeDef",
    "TimeoutConfigTypeDef",
    "MaintenanceWindowTypeDef",
    "CreateKeysAndCertificateRequestRequestTypeDef",
    "KeyPairTypeDef",
    "CreatePackageRequestRequestTypeDef",
    "CreatePackageVersionRequestRequestTypeDef",
    "CreatePolicyVersionRequestRequestTypeDef",
    "CreateProvisioningClaimRequestRequestTypeDef",
    "ProvisioningHookTypeDef",
    "CreateProvisioningTemplateVersionRequestRequestTypeDef",
    "MetricsExportConfigTypeDef",
    "ThingTypePropertiesTypeDef",
    "DeleteAccountAuditConfigurationRequestRequestTypeDef",
    "DeleteAuthorizerRequestRequestTypeDef",
    "DeleteBillingGroupRequestRequestTypeDef",
    "DeleteCACertificateRequestRequestTypeDef",
    "DeleteCertificateProviderRequestRequestTypeDef",
    "DeleteCertificateRequestRequestTypeDef",
    "DeleteCustomMetricRequestRequestTypeDef",
    "DeleteDimensionRequestRequestTypeDef",
    "DeleteDomainConfigurationRequestRequestTypeDef",
    "DeleteDynamicThingGroupRequestRequestTypeDef",
    "DeleteFleetMetricRequestRequestTypeDef",
    "DeleteJobExecutionRequestRequestTypeDef",
    "DeleteJobRequestRequestTypeDef",
    "DeleteJobTemplateRequestRequestTypeDef",
    "DeleteMitigationActionRequestRequestTypeDef",
    "DeleteOTAUpdateRequestRequestTypeDef",
    "DeletePackageRequestRequestTypeDef",
    "DeletePackageVersionRequestRequestTypeDef",
    "DeletePolicyRequestRequestTypeDef",
    "DeletePolicyVersionRequestRequestTypeDef",
    "DeleteProvisioningTemplateRequestRequestTypeDef",
    "DeleteProvisioningTemplateVersionRequestRequestTypeDef",
    "DeleteRoleAliasRequestRequestTypeDef",
    "DeleteScheduledAuditRequestRequestTypeDef",
    "DeleteSecurityProfileRequestRequestTypeDef",
    "DeleteStreamRequestRequestTypeDef",
    "DeleteThingGroupRequestRequestTypeDef",
    "DeleteThingRequestRequestTypeDef",
    "DeleteThingTypeRequestRequestTypeDef",
    "DeleteTopicRuleDestinationRequestRequestTypeDef",
    "DeleteTopicRuleRequestRequestTypeDef",
    "DeleteV2LoggingLevelRequestRequestTypeDef",
    "DeprecateThingTypeRequestRequestTypeDef",
    "DescribeAuditFindingRequestRequestTypeDef",
    "DescribeAuditMitigationActionsTaskRequestRequestTypeDef",
    "TaskStatisticsForAuditCheckTypeDef",
    "DescribeAuditTaskRequestRequestTypeDef",
    "TaskStatisticsTypeDef",
    "DescribeAuthorizerRequestRequestTypeDef",
    "DescribeBillingGroupRequestRequestTypeDef",
    "DescribeCACertificateRequestRequestTypeDef",
    "RegistrationConfigTypeDef",
    "DescribeCertificateProviderRequestRequestTypeDef",
    "DescribeCertificateRequestRequestTypeDef",
    "DescribeCustomMetricRequestRequestTypeDef",
    "DescribeDetectMitigationActionsTaskRequestRequestTypeDef",
    "DescribeDimensionRequestRequestTypeDef",
    "DescribeDomainConfigurationRequestRequestTypeDef",
    "ServerCertificateSummaryTypeDef",
    "DescribeEndpointRequestRequestTypeDef",
    "DescribeFleetMetricRequestRequestTypeDef",
    "DescribeIndexRequestRequestTypeDef",
    "DescribeJobExecutionRequestRequestTypeDef",
    "DescribeJobRequestRequestTypeDef",
    "DescribeJobTemplateRequestRequestTypeDef",
    "DescribeManagedJobTemplateRequestRequestTypeDef",
    "DocumentParameterTypeDef",
    "DescribeMitigationActionRequestRequestTypeDef",
    "DescribeProvisioningTemplateRequestRequestTypeDef",
    "DescribeProvisioningTemplateVersionRequestRequestTypeDef",
    "DescribeRoleAliasRequestRequestTypeDef",
    "RoleAliasDescriptionTypeDef",
    "DescribeScheduledAuditRequestRequestTypeDef",
    "DescribeSecurityProfileRequestRequestTypeDef",
    "DescribeStreamRequestRequestTypeDef",
    "DescribeThingGroupRequestRequestTypeDef",
    "DescribeThingRegistrationTaskRequestRequestTypeDef",
    "DescribeThingRequestRequestTypeDef",
    "DescribeThingTypeRequestRequestTypeDef",
    "ThingTypeMetadataTypeDef",
    "S3DestinationTypeDef",
    "DetachPolicyRequestRequestTypeDef",
    "DetachPrincipalPolicyRequestRequestTypeDef",
    "DetachSecurityProfileRequestRequestTypeDef",
    "DetachThingPrincipalRequestRequestTypeDef",
    "DetectMitigationActionExecutionTypeDef",
    "DetectMitigationActionsTaskStatisticsTypeDef",
    "DetectMitigationActionsTaskTargetTypeDef",
    "ViolationEventOccurrenceRangeTypeDef",
    "DisableTopicRuleRequestRequestTypeDef",
    "DomainConfigurationSummaryTypeDef",
    "PutItemInputTypeDef",
    "EffectivePolicyTypeDef",
    "EnableIoTLoggingParamsTypeDef",
    "EnableTopicRuleRequestRequestTypeDef",
    "ErrorInfoTypeDef",
    "RateIncreaseCriteriaTypeDef",
    "FieldTypeDef",
    "S3LocationTypeDef",
    "StreamTypeDef",
    "FleetMetricNameAndArnTypeDef",
    "GeoLocationTargetTypeDef",
    "PaginatorConfigTypeDef",
    "GetBehaviorModelTrainingSummariesRequestRequestTypeDef",
    "GetCardinalityRequestRequestTypeDef",
    "GetEffectivePoliciesRequestRequestTypeDef",
    "GetJobDocumentRequestRequestTypeDef",
    "GetOTAUpdateRequestRequestTypeDef",
    "VersionUpdateByJobsConfigTypeDef",
    "GetPackageRequestRequestTypeDef",
    "GetPackageVersionRequestRequestTypeDef",
    "GetPercentilesRequestRequestTypeDef",
    "PercentPairTypeDef",
    "GetPolicyRequestRequestTypeDef",
    "GetPolicyVersionRequestRequestTypeDef",
    "GetStatisticsRequestRequestTypeDef",
    "StatisticsTypeDef",
    "GetTopicRuleDestinationRequestRequestTypeDef",
    "GetTopicRuleRequestRequestTypeDef",
    "GroupNameAndArnTypeDef",
    "HttpActionHeaderTypeDef",
    "SigV4AuthorizationTypeDef",
    "HttpContextTypeDef",
    "HttpUrlDestinationConfigurationTypeDef",
    "HttpUrlDestinationPropertiesTypeDef",
    "HttpUrlDestinationSummaryTypeDef",
    "IssuerCertificateIdentifierTypeDef",
    "JobExecutionStatusDetailsTypeDef",
    "JobExecutionSummaryTypeDef",
    "RetryCriteriaTypeDef",
    "JobProcessDetailsTypeDef",
    "JobSummaryTypeDef",
    "JobTemplateSummaryTypeDef",
    "ScheduledJobRolloutTypeDef",
    "KafkaActionHeaderTypeDef",
    "ListActiveViolationsRequestRequestTypeDef",
    "ListAttachedPoliciesRequestRequestTypeDef",
    "ListAuditMitigationActionsExecutionsRequestRequestTypeDef",
    "ListAuthorizersRequestRequestTypeDef",
    "ListBillingGroupsRequestRequestTypeDef",
    "ListCACertificatesRequestRequestTypeDef",
    "ListCertificateProvidersRequestRequestTypeDef",
    "ListCertificatesByCARequestRequestTypeDef",
    "ListCertificatesRequestRequestTypeDef",
    "ListCustomMetricsRequestRequestTypeDef",
    "ListDimensionsRequestRequestTypeDef",
    "ListDomainConfigurationsRequestRequestTypeDef",
    "ListFleetMetricsRequestRequestTypeDef",
    "ListIndicesRequestRequestTypeDef",
    "ListJobExecutionsForJobRequestRequestTypeDef",
    "ListJobExecutionsForThingRequestRequestTypeDef",
    "ListJobTemplatesRequestRequestTypeDef",
    "ListJobsRequestRequestTypeDef",
    "ListManagedJobTemplatesRequestRequestTypeDef",
    "ManagedJobTemplateSummaryTypeDef",
    "ListMitigationActionsRequestRequestTypeDef",
    "MitigationActionIdentifierTypeDef",
    "ListOTAUpdatesRequestRequestTypeDef",
    "OTAUpdateSummaryTypeDef",
    "ListOutgoingCertificatesRequestRequestTypeDef",
    "OutgoingCertificateTypeDef",
    "ListPackageVersionsRequestRequestTypeDef",
    "PackageVersionSummaryTypeDef",
    "ListPackagesRequestRequestTypeDef",
    "PackageSummaryTypeDef",
    "ListPoliciesRequestRequestTypeDef",
    "ListPolicyPrincipalsRequestRequestTypeDef",
    "ListPolicyVersionsRequestRequestTypeDef",
    "PolicyVersionTypeDef",
    "ListPrincipalPoliciesRequestRequestTypeDef",
    "ListPrincipalThingsRequestRequestTypeDef",
    "ListProvisioningTemplateVersionsRequestRequestTypeDef",
    "ProvisioningTemplateVersionSummaryTypeDef",
    "ListProvisioningTemplatesRequestRequestTypeDef",
    "ProvisioningTemplateSummaryTypeDef",
    "ListRelatedResourcesForAuditFindingRequestRequestTypeDef",
    "ListRoleAliasesRequestRequestTypeDef",
    "ListScheduledAuditsRequestRequestTypeDef",
    "ScheduledAuditMetadataTypeDef",
    "ListSecurityProfilesForTargetRequestRequestTypeDef",
    "ListSecurityProfilesRequestRequestTypeDef",
    "SecurityProfileIdentifierTypeDef",
    "ListStreamsRequestRequestTypeDef",
    "StreamSummaryTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListTargetsForPolicyRequestRequestTypeDef",
    "ListTargetsForSecurityProfileRequestRequestTypeDef",
    "SecurityProfileTargetTypeDef",
    "ListThingGroupsForThingRequestRequestTypeDef",
    "ListThingGroupsRequestRequestTypeDef",
    "ListThingPrincipalsRequestRequestTypeDef",
    "ListThingRegistrationTaskReportsRequestRequestTypeDef",
    "ListThingRegistrationTasksRequestRequestTypeDef",
    "ListThingTypesRequestRequestTypeDef",
    "ListThingsInBillingGroupRequestRequestTypeDef",
    "ListThingsInThingGroupRequestRequestTypeDef",
    "ListThingsRequestRequestTypeDef",
    "ThingAttributeTypeDef",
    "ListTopicRuleDestinationsRequestRequestTypeDef",
    "ListTopicRulesRequestRequestTypeDef",
    "TopicRuleListItemTypeDef",
    "ListV2LoggingLevelsRequestRequestTypeDef",
    "LocationTimestampTypeDef",
    "LogTargetTypeDef",
    "LoggingOptionsPayloadTypeDef",
    "PublishFindingToSnsParamsTypeDef",
    "ReplaceDefaultPolicyVersionParamsTypeDef",
    "UpdateCACertificateParamsTypeDef",
    "UpdateDeviceCertificateParamsTypeDef",
    "UserPropertyTypeDef",
    "PolicyVersionIdentifierTypeDef",
    "PutVerificationStateOnViolationRequestRequestTypeDef",
    "RegisterCertificateRequestRequestTypeDef",
    "RegisterCertificateWithoutCARequestRequestTypeDef",
    "RegisterThingRequestRequestTypeDef",
    "RejectCertificateTransferRequestRequestTypeDef",
    "RemoveThingFromBillingGroupRequestRequestTypeDef",
    "RemoveThingFromThingGroupRequestRequestTypeDef",
    "SearchIndexRequestRequestTypeDef",
    "ThingGroupDocumentTypeDef",
    "SetDefaultAuthorizerRequestRequestTypeDef",
    "SetDefaultPolicyVersionRequestRequestTypeDef",
    "SetV2LoggingOptionsRequestRequestTypeDef",
    "SigningProfileParameterTypeDef",
    "StartOnDemandAuditTaskRequestRequestTypeDef",
    "StartThingRegistrationTaskRequestRequestTypeDef",
    "StopThingRegistrationTaskRequestRequestTypeDef",
    "TlsContextTypeDef",
    "ThingConnectivityTypeDef",
    "ThingTypePropertiesPaginatorTypeDef",
    "TimestreamDimensionTypeDef",
    "TimestreamTimestampTypeDef",
    "VpcDestinationConfigurationTypeDef",
    "VpcDestinationSummaryTypeDef",
    "VpcDestinationPropertiesTypeDef",
    "TransferCertificateRequestRequestTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateAuthorizerRequestRequestTypeDef",
    "UpdateCertificateProviderRequestRequestTypeDef",
    "UpdateCertificateRequestRequestTypeDef",
    "UpdateCustomMetricRequestRequestTypeDef",
    "UpdateDimensionRequestRequestTypeDef",
    "UpdatePackageRequestRequestTypeDef",
    "UpdatePackageVersionRequestRequestTypeDef",
    "UpdateRoleAliasRequestRequestTypeDef",
    "UpdateScheduledAuditRequestRequestTypeDef",
    "UpdateThingGroupsForThingRequestRequestTypeDef",
    "UpdateTopicRuleDestinationRequestRequestTypeDef",
    "ValidationErrorTypeDef",
    "AbortConfigTypeDef",
    "MetricDatumPaginatorTypeDef",
    "MetricDatumTypeDef",
    "UpdateFleetMetricRequestRequestTypeDef",
    "AllowedTypeDef",
    "ExplicitDenyTypeDef",
    "ImplicitDenyTypeDef",
    "AssetPropertyValueTypeDef",
    "AssociateTargetsWithJobResponseTypeDef",
    "CancelJobResponseTypeDef",
    "CreateAuthorizerResponseTypeDef",
    "CreateBillingGroupResponseTypeDef",
    "CreateCertificateFromCsrResponseTypeDef",
    "CreateCertificateProviderResponseTypeDef",
    "CreateCustomMetricResponseTypeDef",
    "CreateDimensionResponseTypeDef",
    "CreateDomainConfigurationResponseTypeDef",
    "CreateDynamicThingGroupResponseTypeDef",
    "CreateFleetMetricResponseTypeDef",
    "CreateJobResponseTypeDef",
    "CreateJobTemplateResponseTypeDef",
    "CreateMitigationActionResponseTypeDef",
    "CreateOTAUpdateResponseTypeDef",
    "CreatePackageResponseTypeDef",
    "CreatePackageVersionResponseTypeDef",
    "CreatePolicyResponseTypeDef",
    "CreatePolicyVersionResponseTypeDef",
    "CreateProvisioningTemplateResponseTypeDef",
    "CreateProvisioningTemplateVersionResponseTypeDef",
    "CreateRoleAliasResponseTypeDef",
    "CreateScheduledAuditResponseTypeDef",
    "CreateSecurityProfileResponseTypeDef",
    "CreateStreamResponseTypeDef",
    "CreateThingGroupResponseTypeDef",
    "CreateThingResponseTypeDef",
    "CreateThingTypeResponseTypeDef",
    "DescribeCertificateProviderResponseTypeDef",
    "DescribeCustomMetricResponseTypeDef",
    "DescribeDimensionResponseTypeDef",
    "DescribeEndpointResponseTypeDef",
    "DescribeFleetMetricResponseTypeDef",
    "DescribeIndexResponseTypeDef",
    "DescribeProvisioningTemplateVersionResponseTypeDef",
    "DescribeScheduledAuditResponseTypeDef",
    "DescribeThingRegistrationTaskResponseTypeDef",
    "DescribeThingResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetCardinalityResponseTypeDef",
    "GetJobDocumentResponseTypeDef",
    "GetLoggingOptionsResponseTypeDef",
    "GetPackageResponseTypeDef",
    "GetPackageVersionResponseTypeDef",
    "GetPolicyResponseTypeDef",
    "GetPolicyVersionResponseTypeDef",
    "GetRegistrationCodeResponseTypeDef",
    "GetV2LoggingOptionsResponseTypeDef",
    "ListAttachedPoliciesResponseTypeDef",
    "ListCustomMetricsResponseTypeDef",
    "ListDimensionsResponseTypeDef",
    "ListIndicesResponseTypeDef",
    "ListPoliciesResponseTypeDef",
    "ListPolicyPrincipalsResponseTypeDef",
    "ListPrincipalPoliciesResponseTypeDef",
    "ListPrincipalThingsResponseTypeDef",
    "ListRoleAliasesResponseTypeDef",
    "ListTargetsForPolicyResponseTypeDef",
    "ListThingPrincipalsResponseTypeDef",
    "ListThingRegistrationTaskReportsResponseTypeDef",
    "ListThingRegistrationTasksResponseTypeDef",
    "ListThingsInBillingGroupResponseTypeDef",
    "ListThingsInThingGroupResponseTypeDef",
    "RegisterCACertificateResponseTypeDef",
    "RegisterCertificateResponseTypeDef",
    "RegisterCertificateWithoutCAResponseTypeDef",
    "RegisterThingResponseTypeDef",
    "SetDefaultAuthorizerResponseTypeDef",
    "StartAuditMitigationActionsTaskResponseTypeDef",
    "StartDetectMitigationActionsTaskResponseTypeDef",
    "StartOnDemandAuditTaskResponseTypeDef",
    "StartThingRegistrationTaskResponseTypeDef",
    "TestInvokeAuthorizerResponseTypeDef",
    "TransferCertificateResponseTypeDef",
    "UpdateAuthorizerResponseTypeDef",
    "UpdateBillingGroupResponseTypeDef",
    "UpdateCertificateProviderResponseTypeDef",
    "UpdateCustomMetricResponseTypeDef",
    "UpdateDimensionResponseTypeDef",
    "UpdateDomainConfigurationResponseTypeDef",
    "UpdateDynamicThingGroupResponseTypeDef",
    "UpdateMitigationActionResponseTypeDef",
    "UpdateRoleAliasResponseTypeDef",
    "UpdateScheduledAuditResponseTypeDef",
    "UpdateStreamResponseTypeDef",
    "UpdateThingGroupResponseTypeDef",
    "CreateThingRequestRequestTypeDef",
    "ThingGroupPropertiesTypeDef",
    "UpdateThingRequestRequestTypeDef",
    "ListAuditMitigationActionsExecutionsResponseTypeDef",
    "ListAuditMitigationActionsTasksResponseTypeDef",
    "StartAuditMitigationActionsTaskRequestRequestTypeDef",
    "DescribeAccountAuditConfigurationResponseTypeDef",
    "UpdateAccountAuditConfigurationRequestRequestTypeDef",
    "ListAuditTasksResponseTypeDef",
    "TestAuthorizationRequestRequestTypeDef",
    "DescribeAuthorizerResponseTypeDef",
    "DescribeDefaultAuthorizerResponseTypeDef",
    "ListAuthorizersResponseTypeDef",
    "AwsJobAbortConfigTypeDef",
    "AwsJobExponentialRolloutRateTypeDef",
    "BehaviorCriteriaPaginatorTypeDef",
    "BehaviorCriteriaTypeDef",
    "GetBehaviorModelTrainingSummariesResponseTypeDef",
    "MetricToRetainTypeDef",
    "DescribeBillingGroupResponseTypeDef",
    "UpdateBillingGroupRequestRequestTypeDef",
    "CodeSigningSignatureTypeDef",
    "MqttContextTypeDef",
    "GetBucketsAggregationResponseTypeDef",
    "BucketsAggregationTypeTypeDef",
    "CACertificateDescriptionTypeDef",
    "ListCACertificatesResponseTypeDef",
    "CertificateDescriptionTypeDef",
    "ListCertificateProvidersResponseTypeDef",
    "ListCertificatesByCAResponseTypeDef",
    "ListCertificatesResponseTypeDef",
    "DescribeEventConfigurationsResponseTypeDef",
    "UpdateEventConfigurationsRequestRequestTypeDef",
    "ListAuditMitigationActionsTasksRequestRequestTypeDef",
    "ListAuditTasksRequestRequestTypeDef",
    "ListDetectMitigationActionsExecutionsRequestRequestTypeDef",
    "ListDetectMitigationActionsTasksRequestRequestTypeDef",
    "ListMetricValuesRequestRequestTypeDef",
    "ListViolationEventsRequestRequestTypeDef",
    "CreateAuthorizerRequestRequestTypeDef",
    "CreateBillingGroupRequestRequestTypeDef",
    "CreateCertificateProviderRequestRequestTypeDef",
    "CreateCustomMetricRequestRequestTypeDef",
    "CreateDimensionRequestRequestTypeDef",
    "CreateFleetMetricRequestRequestTypeDef",
    "CreatePolicyRequestRequestTypeDef",
    "CreateRoleAliasRequestRequestTypeDef",
    "CreateScheduledAuditRequestRequestTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateDomainConfigurationRequestRequestTypeDef",
    "UpdateDomainConfigurationRequestRequestTypeDef",
    "SchedulingConfigTypeDef",
    "CreateKeysAndCertificateResponseTypeDef",
    "CreateProvisioningClaimResponseTypeDef",
    "CreateProvisioningTemplateRequestRequestTypeDef",
    "DescribeProvisioningTemplateResponseTypeDef",
    "UpdateProvisioningTemplateRequestRequestTypeDef",
    "CreateThingTypeRequestRequestTypeDef",
    "DescribeAuditTaskResponseTypeDef",
    "RegisterCACertificateRequestRequestTypeDef",
    "UpdateCACertificateRequestRequestTypeDef",
    "DescribeDomainConfigurationResponseTypeDef",
    "DescribeManagedJobTemplateResponseTypeDef",
    "DescribeRoleAliasResponseTypeDef",
    "DescribeThingTypeResponseTypeDef",
    "ThingTypeDefinitionTypeDef",
    "DestinationTypeDef",
    "ListDetectMitigationActionsExecutionsResponseTypeDef",
    "StartDetectMitigationActionsTaskRequestRequestTypeDef",
    "ListDomainConfigurationsResponseTypeDef",
    "DynamoDBv2ActionTypeDef",
    "GetEffectivePoliciesResponseTypeDef",
    "ExponentialRolloutRateTypeDef",
    "ThingGroupIndexingConfigurationTypeDef",
    "StreamFileTypeDef",
    "FileLocationTypeDef",
    "ListFleetMetricsResponseTypeDef",
    "IndexingFilterTypeDef",
    "GetBehaviorModelTrainingSummariesRequestGetBehaviorModelTrainingSummariesPaginateTypeDef",
    "ListActiveViolationsRequestListActiveViolationsPaginateTypeDef",
    "ListAttachedPoliciesRequestListAttachedPoliciesPaginateTypeDef",
    "ListAuditMitigationActionsExecutionsRequestListAuditMitigationActionsExecutionsPaginateTypeDef",
    "ListAuditMitigationActionsTasksRequestListAuditMitigationActionsTasksPaginateTypeDef",
    "ListAuditTasksRequestListAuditTasksPaginateTypeDef",
    "ListAuthorizersRequestListAuthorizersPaginateTypeDef",
    "ListBillingGroupsRequestListBillingGroupsPaginateTypeDef",
    "ListCACertificatesRequestListCACertificatesPaginateTypeDef",
    "ListCertificatesByCARequestListCertificatesByCAPaginateTypeDef",
    "ListCertificatesRequestListCertificatesPaginateTypeDef",
    "ListCustomMetricsRequestListCustomMetricsPaginateTypeDef",
    "ListDetectMitigationActionsExecutionsRequestListDetectMitigationActionsExecutionsPaginateTypeDef",
    "ListDetectMitigationActionsTasksRequestListDetectMitigationActionsTasksPaginateTypeDef",
    "ListDimensionsRequestListDimensionsPaginateTypeDef",
    "ListDomainConfigurationsRequestListDomainConfigurationsPaginateTypeDef",
    "ListFleetMetricsRequestListFleetMetricsPaginateTypeDef",
    "ListIndicesRequestListIndicesPaginateTypeDef",
    "ListJobExecutionsForJobRequestListJobExecutionsForJobPaginateTypeDef",
    "ListJobExecutionsForThingRequestListJobExecutionsForThingPaginateTypeDef",
    "ListJobTemplatesRequestListJobTemplatesPaginateTypeDef",
    "ListJobsRequestListJobsPaginateTypeDef",
    "ListManagedJobTemplatesRequestListManagedJobTemplatesPaginateTypeDef",
    "ListMetricValuesRequestListMetricValuesPaginateTypeDef",
    "ListMitigationActionsRequestListMitigationActionsPaginateTypeDef",
    "ListOTAUpdatesRequestListOTAUpdatesPaginateTypeDef",
    "ListOutgoingCertificatesRequestListOutgoingCertificatesPaginateTypeDef",
    "ListPackageVersionsRequestListPackageVersionsPaginateTypeDef",
    "ListPackagesRequestListPackagesPaginateTypeDef",
    "ListPoliciesRequestListPoliciesPaginateTypeDef",
    "ListPolicyPrincipalsRequestListPolicyPrincipalsPaginateTypeDef",
    "ListPrincipalPoliciesRequestListPrincipalPoliciesPaginateTypeDef",
    "ListPrincipalThingsRequestListPrincipalThingsPaginateTypeDef",
    "ListProvisioningTemplateVersionsRequestListProvisioningTemplateVersionsPaginateTypeDef",
    "ListProvisioningTemplatesRequestListProvisioningTemplatesPaginateTypeDef",
    "ListRelatedResourcesForAuditFindingRequestListRelatedResourcesForAuditFindingPaginateTypeDef",
    "ListRoleAliasesRequestListRoleAliasesPaginateTypeDef",
    "ListScheduledAuditsRequestListScheduledAuditsPaginateTypeDef",
    "ListSecurityProfilesForTargetRequestListSecurityProfilesForTargetPaginateTypeDef",
    "ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef",
    "ListStreamsRequestListStreamsPaginateTypeDef",
    "ListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    "ListTargetsForPolicyRequestListTargetsForPolicyPaginateTypeDef",
    "ListTargetsForSecurityProfileRequestListTargetsForSecurityProfilePaginateTypeDef",
    "ListThingGroupsForThingRequestListThingGroupsForThingPaginateTypeDef",
    "ListThingGroupsRequestListThingGroupsPaginateTypeDef",
    "ListThingPrincipalsRequestListThingPrincipalsPaginateTypeDef",
    "ListThingRegistrationTaskReportsRequestListThingRegistrationTaskReportsPaginateTypeDef",
    "ListThingRegistrationTasksRequestListThingRegistrationTasksPaginateTypeDef",
    "ListThingTypesRequestListThingTypesPaginateTypeDef",
    "ListThingsInBillingGroupRequestListThingsInBillingGroupPaginateTypeDef",
    "ListThingsInThingGroupRequestListThingsInThingGroupPaginateTypeDef",
    "ListThingsRequestListThingsPaginateTypeDef",
    "ListTopicRuleDestinationsRequestListTopicRuleDestinationsPaginateTypeDef",
    "ListTopicRulesRequestListTopicRulesPaginateTypeDef",
    "ListV2LoggingLevelsRequestListV2LoggingLevelsPaginateTypeDef",
    "ListViolationEventsRequestListViolationEventsPaginateTypeDef",
    "GetPackageConfigurationResponseTypeDef",
    "UpdatePackageConfigurationRequestRequestTypeDef",
    "GetPercentilesResponseTypeDef",
    "GetStatisticsResponseTypeDef",
    "ListBillingGroupsResponseTypeDef",
    "ListThingGroupsForThingResponseTypeDef",
    "ListThingGroupsResponseTypeDef",
    "ThingGroupMetadataTypeDef",
    "HttpAuthorizationTypeDef",
    "JobExecutionTypeDef",
    "JobExecutionSummaryForJobTypeDef",
    "JobExecutionSummaryForThingTypeDef",
    "JobExecutionsRetryConfigTypeDef",
    "ListJobsResponseTypeDef",
    "ListJobTemplatesResponseTypeDef",
    "KafkaActionTypeDef",
    "ListManagedJobTemplatesResponseTypeDef",
    "ListMitigationActionsResponseTypeDef",
    "ListOTAUpdatesResponseTypeDef",
    "ListOutgoingCertificatesResponseTypeDef",
    "ListPackageVersionsResponseTypeDef",
    "ListPackagesResponseTypeDef",
    "ListPolicyVersionsResponseTypeDef",
    "ListProvisioningTemplateVersionsResponseTypeDef",
    "ListProvisioningTemplatesResponseTypeDef",
    "ListScheduledAuditsResponseTypeDef",
    "ListSecurityProfilesResponseTypeDef",
    "ListStreamsResponseTypeDef",
    "ListTargetsForSecurityProfileResponseTypeDef",
    "SecurityProfileTargetMappingTypeDef",
    "ListThingsResponseTypeDef",
    "ListTopicRulesResponseTypeDef",
    "LocationActionTypeDef",
    "LogTargetConfigurationTypeDef",
    "SetV2LoggingLevelRequestRequestTypeDef",
    "SetLoggingOptionsRequestRequestTypeDef",
    "MitigationActionParamsPaginatorTypeDef",
    "MitigationActionParamsTypeDef",
    "MqttHeadersTypeDef",
    "ResourceIdentifierTypeDef",
    "ThingDocumentTypeDef",
    "ThingTypeDefinitionPaginatorTypeDef",
    "TimestreamActionTypeDef",
    "TopicRuleDestinationConfigurationTypeDef",
    "TopicRuleDestinationSummaryTypeDef",
    "TopicRuleDestinationTypeDef",
    "ValidateSecurityProfileBehaviorsResponseTypeDef",
    "ListMetricValuesResponsePaginatorTypeDef",
    "ListMetricValuesResponseTypeDef",
    "DeniedTypeDef",
    "PutAssetPropertyValueEntryTypeDef",
    "CreateDynamicThingGroupRequestRequestTypeDef",
    "CreateThingGroupRequestRequestTypeDef",
    "UpdateDynamicThingGroupRequestRequestTypeDef",
    "UpdateThingGroupRequestRequestTypeDef",
    "AwsJobExecutionsRolloutConfigTypeDef",
    "BehaviorPaginatorTypeDef",
    "BehaviorTypeDef",
    "CustomCodeSigningTypeDef",
    "TestInvokeAuthorizerRequestRequestTypeDef",
    "GetBucketsAggregationRequestRequestTypeDef",
    "DescribeCACertificateResponseTypeDef",
    "DescribeCertificateResponseTypeDef",
    "ListThingTypesResponseTypeDef",
    "StartSigningJobParameterTypeDef",
    "JobExecutionsRolloutConfigTypeDef",
    "CreateStreamRequestRequestTypeDef",
    "StreamInfoTypeDef",
    "UpdateStreamRequestRequestTypeDef",
    "ThingIndexingConfigurationTypeDef",
    "DescribeThingGroupResponseTypeDef",
    "HttpActionTypeDef",
    "DescribeJobExecutionResponseTypeDef",
    "ListJobExecutionsForJobResponseTypeDef",
    "ListJobExecutionsForThingResponseTypeDef",
    "ListSecurityProfilesForTargetResponseTypeDef",
    "ListV2LoggingLevelsResponseTypeDef",
    "MitigationActionPaginatorTypeDef",
    "CreateMitigationActionRequestRequestTypeDef",
    "DescribeMitigationActionResponseTypeDef",
    "MitigationActionTypeDef",
    "UpdateMitigationActionRequestRequestTypeDef",
    "RepublishActionTypeDef",
    "AuditSuppressionTypeDef",
    "CreateAuditSuppressionRequestRequestTypeDef",
    "DeleteAuditSuppressionRequestRequestTypeDef",
    "DescribeAuditSuppressionRequestRequestTypeDef",
    "DescribeAuditSuppressionResponseTypeDef",
    "ListAuditFindingsRequestListAuditFindingsPaginateTypeDef",
    "ListAuditFindingsRequestRequestTypeDef",
    "ListAuditSuppressionsRequestListAuditSuppressionsPaginateTypeDef",
    "ListAuditSuppressionsRequestRequestTypeDef",
    "NonCompliantResourceTypeDef",
    "RelatedResourceTypeDef",
    "UpdateAuditSuppressionRequestRequestTypeDef",
    "SearchIndexResponseTypeDef",
    "ListThingTypesResponsePaginatorTypeDef",
    "CreateTopicRuleDestinationRequestRequestTypeDef",
    "ListTopicRuleDestinationsResponseTypeDef",
    "CreateTopicRuleDestinationResponseTypeDef",
    "GetTopicRuleDestinationResponseTypeDef",
    "AuthResultTypeDef",
    "IotSiteWiseActionTypeDef",
    "ActiveViolationPaginatorTypeDef",
    "ViolationEventPaginatorTypeDef",
    "ActiveViolationTypeDef",
    "CreateSecurityProfileRequestRequestTypeDef",
    "DescribeSecurityProfileResponseTypeDef",
    "UpdateSecurityProfileRequestRequestTypeDef",
    "UpdateSecurityProfileResponseTypeDef",
    "ValidateSecurityProfileBehaviorsRequestRequestTypeDef",
    "ViolationEventTypeDef",
    "CodeSigningTypeDef",
    "CreateJobRequestRequestTypeDef",
    "CreateJobTemplateRequestRequestTypeDef",
    "DescribeJobTemplateResponseTypeDef",
    "JobTypeDef",
    "UpdateJobRequestRequestTypeDef",
    "DescribeStreamResponseTypeDef",
    "GetIndexingConfigurationResponseTypeDef",
    "UpdateIndexingConfigurationRequestRequestTypeDef",
    "DetectMitigationActionsTaskSummaryPaginatorTypeDef",
    "DescribeAuditMitigationActionsTaskResponseTypeDef",
    "DetectMitigationActionsTaskSummaryTypeDef",
    "ListAuditSuppressionsResponseTypeDef",
    "AuditFindingTypeDef",
    "ListRelatedResourcesForAuditFindingResponseTypeDef",
    "TestAuthorizationResponseTypeDef",
    "ActionTypeDef",
    "ListActiveViolationsResponsePaginatorTypeDef",
    "ListViolationEventsResponsePaginatorTypeDef",
    "ListActiveViolationsResponseTypeDef",
    "ListViolationEventsResponseTypeDef",
    "OTAUpdateFileTypeDef",
    "DescribeJobResponseTypeDef",
    "ListDetectMitigationActionsTasksResponsePaginatorTypeDef",
    "DescribeDetectMitigationActionsTaskResponseTypeDef",
    "ListDetectMitigationActionsTasksResponseTypeDef",
    "DescribeAuditFindingResponseTypeDef",
    "ListAuditFindingsResponseTypeDef",
    "TopicRulePayloadTypeDef",
    "TopicRuleTypeDef",
    "CreateOTAUpdateRequestRequestTypeDef",
    "OTAUpdateInfoTypeDef",
    "CreateTopicRuleRequestRequestTypeDef",
    "ReplaceTopicRuleRequestRequestTypeDef",
    "GetTopicRuleResponseTypeDef",
    "GetOTAUpdateResponseTypeDef",
)

AbortCriteriaTypeDef = TypedDict(
    "AbortCriteriaTypeDef",
    {
        "failureType": JobExecutionFailureTypeType,
        "action": Literal["CANCEL"],
        "thresholdPercentage": float,
        "minNumberOfExecutedThings": int,
    },
)
AcceptCertificateTransferRequestRequestTypeDef = TypedDict(
    "AcceptCertificateTransferRequestRequestTypeDef",
    {
        "certificateId": str,
        "setAsActive": NotRequired[bool],
    },
)
CloudwatchAlarmActionTypeDef = TypedDict(
    "CloudwatchAlarmActionTypeDef",
    {
        "roleArn": str,
        "alarmName": str,
        "stateReason": str,
        "stateValue": str,
    },
)
CloudwatchLogsActionTypeDef = TypedDict(
    "CloudwatchLogsActionTypeDef",
    {
        "roleArn": str,
        "logGroupName": str,
        "batchMode": NotRequired[bool],
    },
)
CloudwatchMetricActionTypeDef = TypedDict(
    "CloudwatchMetricActionTypeDef",
    {
        "roleArn": str,
        "metricNamespace": str,
        "metricName": str,
        "metricValue": str,
        "metricUnit": str,
        "metricTimestamp": NotRequired[str],
    },
)
DynamoDBActionTypeDef = TypedDict(
    "DynamoDBActionTypeDef",
    {
        "tableName": str,
        "roleArn": str,
        "hashKeyField": str,
        "hashKeyValue": str,
        "operation": NotRequired[str],
        "hashKeyType": NotRequired[DynamoKeyTypeType],
        "rangeKeyField": NotRequired[str],
        "rangeKeyValue": NotRequired[str],
        "rangeKeyType": NotRequired[DynamoKeyTypeType],
        "payloadField": NotRequired[str],
    },
)
ElasticsearchActionTypeDef = TypedDict(
    "ElasticsearchActionTypeDef",
    {
        "roleArn": str,
        "endpoint": str,
        "index": str,
        "type": str,
        "id": str,
    },
)
FirehoseActionTypeDef = TypedDict(
    "FirehoseActionTypeDef",
    {
        "roleArn": str,
        "deliveryStreamName": str,
        "separator": NotRequired[str],
        "batchMode": NotRequired[bool],
    },
)
IotAnalyticsActionTypeDef = TypedDict(
    "IotAnalyticsActionTypeDef",
    {
        "channelArn": NotRequired[str],
        "channelName": NotRequired[str],
        "batchMode": NotRequired[bool],
        "roleArn": NotRequired[str],
    },
)
IotEventsActionTypeDef = TypedDict(
    "IotEventsActionTypeDef",
    {
        "inputName": str,
        "roleArn": str,
        "messageId": NotRequired[str],
        "batchMode": NotRequired[bool],
    },
)
KinesisActionTypeDef = TypedDict(
    "KinesisActionTypeDef",
    {
        "roleArn": str,
        "streamName": str,
        "partitionKey": NotRequired[str],
    },
)
LambdaActionTypeDef = TypedDict(
    "LambdaActionTypeDef",
    {
        "functionArn": str,
    },
)
OpenSearchActionTypeDef = TypedDict(
    "OpenSearchActionTypeDef",
    {
        "roleArn": str,
        "endpoint": str,
        "index": str,
        "type": str,
        "id": str,
    },
)
S3ActionTypeDef = TypedDict(
    "S3ActionTypeDef",
    {
        "roleArn": str,
        "bucketName": str,
        "key": str,
        "cannedAcl": NotRequired[CannedAccessControlListType],
    },
)
SalesforceActionTypeDef = TypedDict(
    "SalesforceActionTypeDef",
    {
        "token": str,
        "url": str,
    },
)
SnsActionTypeDef = TypedDict(
    "SnsActionTypeDef",
    {
        "targetArn": str,
        "roleArn": str,
        "messageFormat": NotRequired[MessageFormatType],
    },
)
SqsActionTypeDef = TypedDict(
    "SqsActionTypeDef",
    {
        "roleArn": str,
        "queueUrl": str,
        "useBase64": NotRequired[bool],
    },
)
StepFunctionsActionTypeDef = TypedDict(
    "StepFunctionsActionTypeDef",
    {
        "stateMachineName": str,
        "roleArn": str,
        "executionNamePrefix": NotRequired[str],
    },
)
MetricValuePaginatorTypeDef = TypedDict(
    "MetricValuePaginatorTypeDef",
    {
        "count": NotRequired[int],
        "cidrs": NotRequired[List[str]],
        "ports": NotRequired[List[int]],
        "number": NotRequired[float],
        "numbers": NotRequired[List[float]],
        "strings": NotRequired[List[str]],
    },
)
ViolationEventAdditionalInfoTypeDef = TypedDict(
    "ViolationEventAdditionalInfoTypeDef",
    {
        "confidenceLevel": NotRequired[ConfidenceLevelType],
    },
)
MetricValueTypeDef = TypedDict(
    "MetricValueTypeDef",
    {
        "count": NotRequired[int],
        "cidrs": NotRequired[Sequence[str]],
        "ports": NotRequired[Sequence[int]],
        "number": NotRequired[float],
        "numbers": NotRequired[Sequence[float]],
        "strings": NotRequired[Sequence[str]],
    },
)
AddThingToBillingGroupRequestRequestTypeDef = TypedDict(
    "AddThingToBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": NotRequired[str],
        "billingGroupArn": NotRequired[str],
        "thingName": NotRequired[str],
        "thingArn": NotRequired[str],
    },
)
AddThingToThingGroupRequestRequestTypeDef = TypedDict(
    "AddThingToThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": NotRequired[str],
        "thingGroupArn": NotRequired[str],
        "thingName": NotRequired[str],
        "thingArn": NotRequired[str],
        "overrideDynamicGroups": NotRequired[bool],
    },
)
AddThingsToThingGroupParamsPaginatorTypeDef = TypedDict(
    "AddThingsToThingGroupParamsPaginatorTypeDef",
    {
        "thingGroupNames": List[str],
        "overrideDynamicGroups": NotRequired[bool],
    },
)
AddThingsToThingGroupParamsTypeDef = TypedDict(
    "AddThingsToThingGroupParamsTypeDef",
    {
        "thingGroupNames": Sequence[str],
        "overrideDynamicGroups": NotRequired[bool],
    },
)
AggregationTypeTypeDef = TypedDict(
    "AggregationTypeTypeDef",
    {
        "name": AggregationTypeNameType,
        "values": NotRequired[Sequence[str]],
    },
)
AlertTargetTypeDef = TypedDict(
    "AlertTargetTypeDef",
    {
        "alertTargetArn": str,
        "roleArn": str,
    },
)
PolicyTypeDef = TypedDict(
    "PolicyTypeDef",
    {
        "policyName": NotRequired[str],
        "policyArn": NotRequired[str],
    },
)
AssetPropertyTimestampTypeDef = TypedDict(
    "AssetPropertyTimestampTypeDef",
    {
        "timeInSeconds": str,
        "offsetInNanos": NotRequired[str],
    },
)
AssetPropertyVariantTypeDef = TypedDict(
    "AssetPropertyVariantTypeDef",
    {
        "stringValue": NotRequired[str],
        "integerValue": NotRequired[str],
        "doubleValue": NotRequired[str],
        "booleanValue": NotRequired[str],
    },
)
AssociateTargetsWithJobRequestRequestTypeDef = TypedDict(
    "AssociateTargetsWithJobRequestRequestTypeDef",
    {
        "targets": Sequence[str],
        "jobId": str,
        "comment": NotRequired[str],
        "namespaceId": NotRequired[str],
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
AttachPolicyRequestRequestTypeDef = TypedDict(
    "AttachPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "target": str,
    },
)
AttachPrincipalPolicyRequestRequestTypeDef = TypedDict(
    "AttachPrincipalPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "principal": str,
    },
)
AttachSecurityProfileRequestRequestTypeDef = TypedDict(
    "AttachSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
        "securityProfileTargetArn": str,
    },
)
AttachThingPrincipalRequestRequestTypeDef = TypedDict(
    "AttachThingPrincipalRequestRequestTypeDef",
    {
        "thingName": str,
        "principal": str,
    },
)
AttributePayloadTypeDef = TypedDict(
    "AttributePayloadTypeDef",
    {
        "attributes": NotRequired[Mapping[str, str]],
        "merge": NotRequired[bool],
    },
)
AuditCheckConfigurationTypeDef = TypedDict(
    "AuditCheckConfigurationTypeDef",
    {
        "enabled": NotRequired[bool],
    },
)
AuditCheckDetailsTypeDef = TypedDict(
    "AuditCheckDetailsTypeDef",
    {
        "checkRunStatus": NotRequired[AuditCheckRunStatusType],
        "checkCompliant": NotRequired[bool],
        "totalResourcesCount": NotRequired[int],
        "nonCompliantResourcesCount": NotRequired[int],
        "suppressedNonCompliantResourcesCount": NotRequired[int],
        "errorCode": NotRequired[str],
        "message": NotRequired[str],
    },
)
AuditMitigationActionExecutionMetadataTypeDef = TypedDict(
    "AuditMitigationActionExecutionMetadataTypeDef",
    {
        "taskId": NotRequired[str],
        "findingId": NotRequired[str],
        "actionName": NotRequired[str],
        "actionId": NotRequired[str],
        "status": NotRequired[AuditMitigationActionsExecutionStatusType],
        "startTime": NotRequired[datetime],
        "endTime": NotRequired[datetime],
        "errorCode": NotRequired[str],
        "message": NotRequired[str],
    },
)
AuditMitigationActionsTaskMetadataTypeDef = TypedDict(
    "AuditMitigationActionsTaskMetadataTypeDef",
    {
        "taskId": NotRequired[str],
        "startTime": NotRequired[datetime],
        "taskStatus": NotRequired[AuditMitigationActionsTaskStatusType],
    },
)
AuditMitigationActionsTaskTargetTypeDef = TypedDict(
    "AuditMitigationActionsTaskTargetTypeDef",
    {
        "auditTaskId": NotRequired[str],
        "findingIds": NotRequired[List[str]],
        "auditCheckToReasonCodeFilter": NotRequired[Dict[str, List[str]]],
    },
)
AuditNotificationTargetTypeDef = TypedDict(
    "AuditNotificationTargetTypeDef",
    {
        "targetArn": NotRequired[str],
        "roleArn": NotRequired[str],
        "enabled": NotRequired[bool],
    },
)
AuditTaskMetadataTypeDef = TypedDict(
    "AuditTaskMetadataTypeDef",
    {
        "taskId": NotRequired[str],
        "taskStatus": NotRequired[AuditTaskStatusType],
        "taskType": NotRequired[AuditTaskTypeType],
    },
)
AuthInfoTypeDef = TypedDict(
    "AuthInfoTypeDef",
    {
        "resources": Sequence[str],
        "actionType": NotRequired[ActionTypeType],
    },
)
AuthorizerConfigTypeDef = TypedDict(
    "AuthorizerConfigTypeDef",
    {
        "defaultAuthorizerName": NotRequired[str],
        "allowAuthorizerOverride": NotRequired[bool],
    },
)
AuthorizerDescriptionTypeDef = TypedDict(
    "AuthorizerDescriptionTypeDef",
    {
        "authorizerName": NotRequired[str],
        "authorizerArn": NotRequired[str],
        "authorizerFunctionArn": NotRequired[str],
        "tokenKeyName": NotRequired[str],
        "tokenSigningPublicKeys": NotRequired[Dict[str, str]],
        "status": NotRequired[AuthorizerStatusType],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
        "signingDisabled": NotRequired[bool],
        "enableCachingForHttp": NotRequired[bool],
    },
)
AuthorizerSummaryTypeDef = TypedDict(
    "AuthorizerSummaryTypeDef",
    {
        "authorizerName": NotRequired[str],
        "authorizerArn": NotRequired[str],
    },
)
AwsJobAbortCriteriaTypeDef = TypedDict(
    "AwsJobAbortCriteriaTypeDef",
    {
        "failureType": AwsJobAbortCriteriaFailureTypeType,
        "action": Literal["CANCEL"],
        "thresholdPercentage": float,
        "minNumberOfExecutedThings": int,
    },
)
AwsJobRateIncreaseCriteriaTypeDef = TypedDict(
    "AwsJobRateIncreaseCriteriaTypeDef",
    {
        "numberOfNotifiedThings": NotRequired[int],
        "numberOfSucceededThings": NotRequired[int],
    },
)
AwsJobPresignedUrlConfigTypeDef = TypedDict(
    "AwsJobPresignedUrlConfigTypeDef",
    {
        "expiresInSec": NotRequired[int],
    },
)
AwsJobTimeoutConfigTypeDef = TypedDict(
    "AwsJobTimeoutConfigTypeDef",
    {
        "inProgressTimeoutInMinutes": NotRequired[int],
    },
)
MachineLearningDetectionConfigTypeDef = TypedDict(
    "MachineLearningDetectionConfigTypeDef",
    {
        "confidenceLevel": ConfidenceLevelType,
    },
)
StatisticalThresholdTypeDef = TypedDict(
    "StatisticalThresholdTypeDef",
    {
        "statistic": NotRequired[str],
    },
)
BehaviorModelTrainingSummaryTypeDef = TypedDict(
    "BehaviorModelTrainingSummaryTypeDef",
    {
        "securityProfileName": NotRequired[str],
        "behaviorName": NotRequired[str],
        "trainingDataCollectionStartDate": NotRequired[datetime],
        "modelStatus": NotRequired[ModelStatusType],
        "datapointsCollectionPercentage": NotRequired[float],
        "lastModelRefreshDate": NotRequired[datetime],
    },
)
MetricDimensionTypeDef = TypedDict(
    "MetricDimensionTypeDef",
    {
        "dimensionName": str,
        "operator": NotRequired[DimensionValueOperatorType],
    },
)
BillingGroupMetadataTypeDef = TypedDict(
    "BillingGroupMetadataTypeDef",
    {
        "creationDate": NotRequired[datetime],
    },
)
BillingGroupPropertiesTypeDef = TypedDict(
    "BillingGroupPropertiesTypeDef",
    {
        "billingGroupDescription": NotRequired[str],
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
BucketTypeDef = TypedDict(
    "BucketTypeDef",
    {
        "keyValue": NotRequired[str],
        "count": NotRequired[int],
    },
)
TermsAggregationTypeDef = TypedDict(
    "TermsAggregationTypeDef",
    {
        "maxBuckets": NotRequired[int],
    },
)
CertificateValidityTypeDef = TypedDict(
    "CertificateValidityTypeDef",
    {
        "notBefore": NotRequired[datetime],
        "notAfter": NotRequired[datetime],
    },
)
CACertificateTypeDef = TypedDict(
    "CACertificateTypeDef",
    {
        "certificateArn": NotRequired[str],
        "certificateId": NotRequired[str],
        "status": NotRequired[CACertificateStatusType],
        "creationDate": NotRequired[datetime],
    },
)
CancelAuditMitigationActionsTaskRequestRequestTypeDef = TypedDict(
    "CancelAuditMitigationActionsTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
CancelAuditTaskRequestRequestTypeDef = TypedDict(
    "CancelAuditTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
CancelCertificateTransferRequestRequestTypeDef = TypedDict(
    "CancelCertificateTransferRequestRequestTypeDef",
    {
        "certificateId": str,
    },
)
CancelDetectMitigationActionsTaskRequestRequestTypeDef = TypedDict(
    "CancelDetectMitigationActionsTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
CancelJobExecutionRequestRequestTypeDef = TypedDict(
    "CancelJobExecutionRequestRequestTypeDef",
    {
        "jobId": str,
        "thingName": str,
        "force": NotRequired[bool],
        "expectedVersion": NotRequired[int],
        "statusDetails": NotRequired[Mapping[str, str]],
    },
)
CancelJobRequestRequestTypeDef = TypedDict(
    "CancelJobRequestRequestTypeDef",
    {
        "jobId": str,
        "reasonCode": NotRequired[str],
        "comment": NotRequired[str],
        "force": NotRequired[bool],
    },
)
TransferDataTypeDef = TypedDict(
    "TransferDataTypeDef",
    {
        "transferMessage": NotRequired[str],
        "rejectReason": NotRequired[str],
        "transferDate": NotRequired[datetime],
        "acceptDate": NotRequired[datetime],
        "rejectDate": NotRequired[datetime],
    },
)
CertificateProviderSummaryTypeDef = TypedDict(
    "CertificateProviderSummaryTypeDef",
    {
        "certificateProviderName": NotRequired[str],
        "certificateProviderArn": NotRequired[str],
    },
)
CertificateTypeDef = TypedDict(
    "CertificateTypeDef",
    {
        "certificateArn": NotRequired[str],
        "certificateId": NotRequired[str],
        "status": NotRequired[CertificateStatusType],
        "certificateMode": NotRequired[CertificateModeType],
        "creationDate": NotRequired[datetime],
    },
)
CodeSigningCertificateChainTypeDef = TypedDict(
    "CodeSigningCertificateChainTypeDef",
    {
        "certificateName": NotRequired[str],
        "inlineDocument": NotRequired[str],
    },
)
ConfigurationTypeDef = TypedDict(
    "ConfigurationTypeDef",
    {
        "Enabled": NotRequired[bool],
    },
)
ConfirmTopicRuleDestinationRequestRequestTypeDef = TypedDict(
    "ConfirmTopicRuleDestinationRequestRequestTypeDef",
    {
        "confirmationToken": str,
    },
)
TimestampTypeDef = Union[datetime, str]
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": NotRequired[str],
    },
)
CreateCertificateFromCsrRequestRequestTypeDef = TypedDict(
    "CreateCertificateFromCsrRequestRequestTypeDef",
    {
        "certificateSigningRequest": str,
        "setAsActive": NotRequired[bool],
    },
)
ServerCertificateConfigTypeDef = TypedDict(
    "ServerCertificateConfigTypeDef",
    {
        "enableOCSPCheck": NotRequired[bool],
    },
)
TlsConfigTypeDef = TypedDict(
    "TlsConfigTypeDef",
    {
        "securityPolicy": NotRequired[str],
    },
)
PresignedUrlConfigTypeDef = TypedDict(
    "PresignedUrlConfigTypeDef",
    {
        "roleArn": NotRequired[str],
        "expiresInSec": NotRequired[int],
    },
)
TimeoutConfigTypeDef = TypedDict(
    "TimeoutConfigTypeDef",
    {
        "inProgressTimeoutInMinutes": NotRequired[int],
    },
)
MaintenanceWindowTypeDef = TypedDict(
    "MaintenanceWindowTypeDef",
    {
        "startTime": str,
        "durationInMinutes": int,
    },
)
CreateKeysAndCertificateRequestRequestTypeDef = TypedDict(
    "CreateKeysAndCertificateRequestRequestTypeDef",
    {
        "setAsActive": NotRequired[bool],
    },
)
KeyPairTypeDef = TypedDict(
    "KeyPairTypeDef",
    {
        "PublicKey": NotRequired[str],
        "PrivateKey": NotRequired[str],
    },
)
CreatePackageRequestRequestTypeDef = TypedDict(
    "CreatePackageRequestRequestTypeDef",
    {
        "packageName": str,
        "description": NotRequired[str],
        "tags": NotRequired[Mapping[str, str]],
        "clientToken": NotRequired[str],
    },
)
CreatePackageVersionRequestRequestTypeDef = TypedDict(
    "CreatePackageVersionRequestRequestTypeDef",
    {
        "packageName": str,
        "versionName": str,
        "description": NotRequired[str],
        "attributes": NotRequired[Mapping[str, str]],
        "tags": NotRequired[Mapping[str, str]],
        "clientToken": NotRequired[str],
    },
)
CreatePolicyVersionRequestRequestTypeDef = TypedDict(
    "CreatePolicyVersionRequestRequestTypeDef",
    {
        "policyName": str,
        "policyDocument": str,
        "setAsDefault": NotRequired[bool],
    },
)
CreateProvisioningClaimRequestRequestTypeDef = TypedDict(
    "CreateProvisioningClaimRequestRequestTypeDef",
    {
        "templateName": str,
    },
)
ProvisioningHookTypeDef = TypedDict(
    "ProvisioningHookTypeDef",
    {
        "targetArn": str,
        "payloadVersion": NotRequired[str],
    },
)
CreateProvisioningTemplateVersionRequestRequestTypeDef = TypedDict(
    "CreateProvisioningTemplateVersionRequestRequestTypeDef",
    {
        "templateName": str,
        "templateBody": str,
        "setAsDefault": NotRequired[bool],
    },
)
MetricsExportConfigTypeDef = TypedDict(
    "MetricsExportConfigTypeDef",
    {
        "mqttTopic": str,
        "roleArn": str,
    },
)
ThingTypePropertiesTypeDef = TypedDict(
    "ThingTypePropertiesTypeDef",
    {
        "thingTypeDescription": NotRequired[str],
        "searchableAttributes": NotRequired[Sequence[str]],
    },
)
DeleteAccountAuditConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteAccountAuditConfigurationRequestRequestTypeDef",
    {
        "deleteScheduledAudits": NotRequired[bool],
    },
)
DeleteAuthorizerRequestRequestTypeDef = TypedDict(
    "DeleteAuthorizerRequestRequestTypeDef",
    {
        "authorizerName": str,
    },
)
DeleteBillingGroupRequestRequestTypeDef = TypedDict(
    "DeleteBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": str,
        "expectedVersion": NotRequired[int],
    },
)
DeleteCACertificateRequestRequestTypeDef = TypedDict(
    "DeleteCACertificateRequestRequestTypeDef",
    {
        "certificateId": str,
    },
)
DeleteCertificateProviderRequestRequestTypeDef = TypedDict(
    "DeleteCertificateProviderRequestRequestTypeDef",
    {
        "certificateProviderName": str,
    },
)
DeleteCertificateRequestRequestTypeDef = TypedDict(
    "DeleteCertificateRequestRequestTypeDef",
    {
        "certificateId": str,
        "forceDelete": NotRequired[bool],
    },
)
DeleteCustomMetricRequestRequestTypeDef = TypedDict(
    "DeleteCustomMetricRequestRequestTypeDef",
    {
        "metricName": str,
    },
)
DeleteDimensionRequestRequestTypeDef = TypedDict(
    "DeleteDimensionRequestRequestTypeDef",
    {
        "name": str,
    },
)
DeleteDomainConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteDomainConfigurationRequestRequestTypeDef",
    {
        "domainConfigurationName": str,
    },
)
DeleteDynamicThingGroupRequestRequestTypeDef = TypedDict(
    "DeleteDynamicThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "expectedVersion": NotRequired[int],
    },
)
DeleteFleetMetricRequestRequestTypeDef = TypedDict(
    "DeleteFleetMetricRequestRequestTypeDef",
    {
        "metricName": str,
        "expectedVersion": NotRequired[int],
    },
)
DeleteJobExecutionRequestRequestTypeDef = TypedDict(
    "DeleteJobExecutionRequestRequestTypeDef",
    {
        "jobId": str,
        "thingName": str,
        "executionNumber": int,
        "force": NotRequired[bool],
        "namespaceId": NotRequired[str],
    },
)
DeleteJobRequestRequestTypeDef = TypedDict(
    "DeleteJobRequestRequestTypeDef",
    {
        "jobId": str,
        "force": NotRequired[bool],
        "namespaceId": NotRequired[str],
    },
)
DeleteJobTemplateRequestRequestTypeDef = TypedDict(
    "DeleteJobTemplateRequestRequestTypeDef",
    {
        "jobTemplateId": str,
    },
)
DeleteMitigationActionRequestRequestTypeDef = TypedDict(
    "DeleteMitigationActionRequestRequestTypeDef",
    {
        "actionName": str,
    },
)
DeleteOTAUpdateRequestRequestTypeDef = TypedDict(
    "DeleteOTAUpdateRequestRequestTypeDef",
    {
        "otaUpdateId": str,
        "deleteStream": NotRequired[bool],
        "forceDeleteAWSJob": NotRequired[bool],
    },
)
DeletePackageRequestRequestTypeDef = TypedDict(
    "DeletePackageRequestRequestTypeDef",
    {
        "packageName": str,
        "clientToken": NotRequired[str],
    },
)
DeletePackageVersionRequestRequestTypeDef = TypedDict(
    "DeletePackageVersionRequestRequestTypeDef",
    {
        "packageName": str,
        "versionName": str,
        "clientToken": NotRequired[str],
    },
)
DeletePolicyRequestRequestTypeDef = TypedDict(
    "DeletePolicyRequestRequestTypeDef",
    {
        "policyName": str,
    },
)
DeletePolicyVersionRequestRequestTypeDef = TypedDict(
    "DeletePolicyVersionRequestRequestTypeDef",
    {
        "policyName": str,
        "policyVersionId": str,
    },
)
DeleteProvisioningTemplateRequestRequestTypeDef = TypedDict(
    "DeleteProvisioningTemplateRequestRequestTypeDef",
    {
        "templateName": str,
    },
)
DeleteProvisioningTemplateVersionRequestRequestTypeDef = TypedDict(
    "DeleteProvisioningTemplateVersionRequestRequestTypeDef",
    {
        "templateName": str,
        "versionId": int,
    },
)
DeleteRoleAliasRequestRequestTypeDef = TypedDict(
    "DeleteRoleAliasRequestRequestTypeDef",
    {
        "roleAlias": str,
    },
)
DeleteScheduledAuditRequestRequestTypeDef = TypedDict(
    "DeleteScheduledAuditRequestRequestTypeDef",
    {
        "scheduledAuditName": str,
    },
)
DeleteSecurityProfileRequestRequestTypeDef = TypedDict(
    "DeleteSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
        "expectedVersion": NotRequired[int],
    },
)
DeleteStreamRequestRequestTypeDef = TypedDict(
    "DeleteStreamRequestRequestTypeDef",
    {
        "streamId": str,
    },
)
DeleteThingGroupRequestRequestTypeDef = TypedDict(
    "DeleteThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "expectedVersion": NotRequired[int],
    },
)
DeleteThingRequestRequestTypeDef = TypedDict(
    "DeleteThingRequestRequestTypeDef",
    {
        "thingName": str,
        "expectedVersion": NotRequired[int],
    },
)
DeleteThingTypeRequestRequestTypeDef = TypedDict(
    "DeleteThingTypeRequestRequestTypeDef",
    {
        "thingTypeName": str,
    },
)
DeleteTopicRuleDestinationRequestRequestTypeDef = TypedDict(
    "DeleteTopicRuleDestinationRequestRequestTypeDef",
    {
        "arn": str,
    },
)
DeleteTopicRuleRequestRequestTypeDef = TypedDict(
    "DeleteTopicRuleRequestRequestTypeDef",
    {
        "ruleName": str,
    },
)
DeleteV2LoggingLevelRequestRequestTypeDef = TypedDict(
    "DeleteV2LoggingLevelRequestRequestTypeDef",
    {
        "targetType": LogTargetTypeType,
        "targetName": str,
    },
)
DeprecateThingTypeRequestRequestTypeDef = TypedDict(
    "DeprecateThingTypeRequestRequestTypeDef",
    {
        "thingTypeName": str,
        "undoDeprecate": NotRequired[bool],
    },
)
DescribeAuditFindingRequestRequestTypeDef = TypedDict(
    "DescribeAuditFindingRequestRequestTypeDef",
    {
        "findingId": str,
    },
)
DescribeAuditMitigationActionsTaskRequestRequestTypeDef = TypedDict(
    "DescribeAuditMitigationActionsTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
TaskStatisticsForAuditCheckTypeDef = TypedDict(
    "TaskStatisticsForAuditCheckTypeDef",
    {
        "totalFindingsCount": NotRequired[int],
        "failedFindingsCount": NotRequired[int],
        "succeededFindingsCount": NotRequired[int],
        "skippedFindingsCount": NotRequired[int],
        "canceledFindingsCount": NotRequired[int],
    },
)
DescribeAuditTaskRequestRequestTypeDef = TypedDict(
    "DescribeAuditTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
TaskStatisticsTypeDef = TypedDict(
    "TaskStatisticsTypeDef",
    {
        "totalChecks": NotRequired[int],
        "inProgressChecks": NotRequired[int],
        "waitingForDataCollectionChecks": NotRequired[int],
        "compliantChecks": NotRequired[int],
        "nonCompliantChecks": NotRequired[int],
        "failedChecks": NotRequired[int],
        "canceledChecks": NotRequired[int],
    },
)
DescribeAuthorizerRequestRequestTypeDef = TypedDict(
    "DescribeAuthorizerRequestRequestTypeDef",
    {
        "authorizerName": str,
    },
)
DescribeBillingGroupRequestRequestTypeDef = TypedDict(
    "DescribeBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": str,
    },
)
DescribeCACertificateRequestRequestTypeDef = TypedDict(
    "DescribeCACertificateRequestRequestTypeDef",
    {
        "certificateId": str,
    },
)
RegistrationConfigTypeDef = TypedDict(
    "RegistrationConfigTypeDef",
    {
        "templateBody": NotRequired[str],
        "roleArn": NotRequired[str],
        "templateName": NotRequired[str],
    },
)
DescribeCertificateProviderRequestRequestTypeDef = TypedDict(
    "DescribeCertificateProviderRequestRequestTypeDef",
    {
        "certificateProviderName": str,
    },
)
DescribeCertificateRequestRequestTypeDef = TypedDict(
    "DescribeCertificateRequestRequestTypeDef",
    {
        "certificateId": str,
    },
)
DescribeCustomMetricRequestRequestTypeDef = TypedDict(
    "DescribeCustomMetricRequestRequestTypeDef",
    {
        "metricName": str,
    },
)
DescribeDetectMitigationActionsTaskRequestRequestTypeDef = TypedDict(
    "DescribeDetectMitigationActionsTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
DescribeDimensionRequestRequestTypeDef = TypedDict(
    "DescribeDimensionRequestRequestTypeDef",
    {
        "name": str,
    },
)
DescribeDomainConfigurationRequestRequestTypeDef = TypedDict(
    "DescribeDomainConfigurationRequestRequestTypeDef",
    {
        "domainConfigurationName": str,
    },
)
ServerCertificateSummaryTypeDef = TypedDict(
    "ServerCertificateSummaryTypeDef",
    {
        "serverCertificateArn": NotRequired[str],
        "serverCertificateStatus": NotRequired[ServerCertificateStatusType],
        "serverCertificateStatusDetail": NotRequired[str],
    },
)
DescribeEndpointRequestRequestTypeDef = TypedDict(
    "DescribeEndpointRequestRequestTypeDef",
    {
        "endpointType": NotRequired[str],
    },
)
DescribeFleetMetricRequestRequestTypeDef = TypedDict(
    "DescribeFleetMetricRequestRequestTypeDef",
    {
        "metricName": str,
    },
)
DescribeIndexRequestRequestTypeDef = TypedDict(
    "DescribeIndexRequestRequestTypeDef",
    {
        "indexName": str,
    },
)
DescribeJobExecutionRequestRequestTypeDef = TypedDict(
    "DescribeJobExecutionRequestRequestTypeDef",
    {
        "jobId": str,
        "thingName": str,
        "executionNumber": NotRequired[int],
    },
)
DescribeJobRequestRequestTypeDef = TypedDict(
    "DescribeJobRequestRequestTypeDef",
    {
        "jobId": str,
    },
)
DescribeJobTemplateRequestRequestTypeDef = TypedDict(
    "DescribeJobTemplateRequestRequestTypeDef",
    {
        "jobTemplateId": str,
    },
)
DescribeManagedJobTemplateRequestRequestTypeDef = TypedDict(
    "DescribeManagedJobTemplateRequestRequestTypeDef",
    {
        "templateName": str,
        "templateVersion": NotRequired[str],
    },
)
DocumentParameterTypeDef = TypedDict(
    "DocumentParameterTypeDef",
    {
        "key": NotRequired[str],
        "description": NotRequired[str],
        "regex": NotRequired[str],
        "example": NotRequired[str],
        "optional": NotRequired[bool],
    },
)
DescribeMitigationActionRequestRequestTypeDef = TypedDict(
    "DescribeMitigationActionRequestRequestTypeDef",
    {
        "actionName": str,
    },
)
DescribeProvisioningTemplateRequestRequestTypeDef = TypedDict(
    "DescribeProvisioningTemplateRequestRequestTypeDef",
    {
        "templateName": str,
    },
)
DescribeProvisioningTemplateVersionRequestRequestTypeDef = TypedDict(
    "DescribeProvisioningTemplateVersionRequestRequestTypeDef",
    {
        "templateName": str,
        "versionId": int,
    },
)
DescribeRoleAliasRequestRequestTypeDef = TypedDict(
    "DescribeRoleAliasRequestRequestTypeDef",
    {
        "roleAlias": str,
    },
)
RoleAliasDescriptionTypeDef = TypedDict(
    "RoleAliasDescriptionTypeDef",
    {
        "roleAlias": NotRequired[str],
        "roleAliasArn": NotRequired[str],
        "roleArn": NotRequired[str],
        "owner": NotRequired[str],
        "credentialDurationSeconds": NotRequired[int],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
    },
)
DescribeScheduledAuditRequestRequestTypeDef = TypedDict(
    "DescribeScheduledAuditRequestRequestTypeDef",
    {
        "scheduledAuditName": str,
    },
)
DescribeSecurityProfileRequestRequestTypeDef = TypedDict(
    "DescribeSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
    },
)
DescribeStreamRequestRequestTypeDef = TypedDict(
    "DescribeStreamRequestRequestTypeDef",
    {
        "streamId": str,
    },
)
DescribeThingGroupRequestRequestTypeDef = TypedDict(
    "DescribeThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
    },
)
DescribeThingRegistrationTaskRequestRequestTypeDef = TypedDict(
    "DescribeThingRegistrationTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
DescribeThingRequestRequestTypeDef = TypedDict(
    "DescribeThingRequestRequestTypeDef",
    {
        "thingName": str,
    },
)
DescribeThingTypeRequestRequestTypeDef = TypedDict(
    "DescribeThingTypeRequestRequestTypeDef",
    {
        "thingTypeName": str,
    },
)
ThingTypeMetadataTypeDef = TypedDict(
    "ThingTypeMetadataTypeDef",
    {
        "deprecated": NotRequired[bool],
        "deprecationDate": NotRequired[datetime],
        "creationDate": NotRequired[datetime],
    },
)
S3DestinationTypeDef = TypedDict(
    "S3DestinationTypeDef",
    {
        "bucket": NotRequired[str],
        "prefix": NotRequired[str],
    },
)
DetachPolicyRequestRequestTypeDef = TypedDict(
    "DetachPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "target": str,
    },
)
DetachPrincipalPolicyRequestRequestTypeDef = TypedDict(
    "DetachPrincipalPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "principal": str,
    },
)
DetachSecurityProfileRequestRequestTypeDef = TypedDict(
    "DetachSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
        "securityProfileTargetArn": str,
    },
)
DetachThingPrincipalRequestRequestTypeDef = TypedDict(
    "DetachThingPrincipalRequestRequestTypeDef",
    {
        "thingName": str,
        "principal": str,
    },
)
DetectMitigationActionExecutionTypeDef = TypedDict(
    "DetectMitigationActionExecutionTypeDef",
    {
        "taskId": NotRequired[str],
        "violationId": NotRequired[str],
        "actionName": NotRequired[str],
        "thingName": NotRequired[str],
        "executionStartDate": NotRequired[datetime],
        "executionEndDate": NotRequired[datetime],
        "status": NotRequired[DetectMitigationActionExecutionStatusType],
        "errorCode": NotRequired[str],
        "message": NotRequired[str],
    },
)
DetectMitigationActionsTaskStatisticsTypeDef = TypedDict(
    "DetectMitigationActionsTaskStatisticsTypeDef",
    {
        "actionsExecuted": NotRequired[int],
        "actionsSkipped": NotRequired[int],
        "actionsFailed": NotRequired[int],
    },
)
DetectMitigationActionsTaskTargetTypeDef = TypedDict(
    "DetectMitigationActionsTaskTargetTypeDef",
    {
        "violationIds": NotRequired[List[str]],
        "securityProfileName": NotRequired[str],
        "behaviorName": NotRequired[str],
    },
)
ViolationEventOccurrenceRangeTypeDef = TypedDict(
    "ViolationEventOccurrenceRangeTypeDef",
    {
        "startTime": datetime,
        "endTime": datetime,
    },
)
DisableTopicRuleRequestRequestTypeDef = TypedDict(
    "DisableTopicRuleRequestRequestTypeDef",
    {
        "ruleName": str,
    },
)
DomainConfigurationSummaryTypeDef = TypedDict(
    "DomainConfigurationSummaryTypeDef",
    {
        "domainConfigurationName": NotRequired[str],
        "domainConfigurationArn": NotRequired[str],
        "serviceType": NotRequired[ServiceTypeType],
    },
)
PutItemInputTypeDef = TypedDict(
    "PutItemInputTypeDef",
    {
        "tableName": str,
    },
)
EffectivePolicyTypeDef = TypedDict(
    "EffectivePolicyTypeDef",
    {
        "policyName": NotRequired[str],
        "policyArn": NotRequired[str],
        "policyDocument": NotRequired[str],
    },
)
EnableIoTLoggingParamsTypeDef = TypedDict(
    "EnableIoTLoggingParamsTypeDef",
    {
        "roleArnForLogging": str,
        "logLevel": LogLevelType,
    },
)
EnableTopicRuleRequestRequestTypeDef = TypedDict(
    "EnableTopicRuleRequestRequestTypeDef",
    {
        "ruleName": str,
    },
)
ErrorInfoTypeDef = TypedDict(
    "ErrorInfoTypeDef",
    {
        "code": NotRequired[str],
        "message": NotRequired[str],
    },
)
RateIncreaseCriteriaTypeDef = TypedDict(
    "RateIncreaseCriteriaTypeDef",
    {
        "numberOfNotifiedThings": NotRequired[int],
        "numberOfSucceededThings": NotRequired[int],
    },
)
FieldTypeDef = TypedDict(
    "FieldTypeDef",
    {
        "name": NotRequired[str],
        "type": NotRequired[FieldTypeType],
    },
)
S3LocationTypeDef = TypedDict(
    "S3LocationTypeDef",
    {
        "bucket": NotRequired[str],
        "key": NotRequired[str],
        "version": NotRequired[str],
    },
)
StreamTypeDef = TypedDict(
    "StreamTypeDef",
    {
        "streamId": NotRequired[str],
        "fileId": NotRequired[int],
    },
)
FleetMetricNameAndArnTypeDef = TypedDict(
    "FleetMetricNameAndArnTypeDef",
    {
        "metricName": NotRequired[str],
        "metricArn": NotRequired[str],
    },
)
GeoLocationTargetTypeDef = TypedDict(
    "GeoLocationTargetTypeDef",
    {
        "name": NotRequired[str],
        "order": NotRequired[TargetFieldOrderType],
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
GetBehaviorModelTrainingSummariesRequestRequestTypeDef = TypedDict(
    "GetBehaviorModelTrainingSummariesRequestRequestTypeDef",
    {
        "securityProfileName": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
GetCardinalityRequestRequestTypeDef = TypedDict(
    "GetCardinalityRequestRequestTypeDef",
    {
        "queryString": str,
        "indexName": NotRequired[str],
        "aggregationField": NotRequired[str],
        "queryVersion": NotRequired[str],
    },
)
GetEffectivePoliciesRequestRequestTypeDef = TypedDict(
    "GetEffectivePoliciesRequestRequestTypeDef",
    {
        "principal": NotRequired[str],
        "cognitoIdentityPoolId": NotRequired[str],
        "thingName": NotRequired[str],
    },
)
GetJobDocumentRequestRequestTypeDef = TypedDict(
    "GetJobDocumentRequestRequestTypeDef",
    {
        "jobId": str,
    },
)
GetOTAUpdateRequestRequestTypeDef = TypedDict(
    "GetOTAUpdateRequestRequestTypeDef",
    {
        "otaUpdateId": str,
    },
)
VersionUpdateByJobsConfigTypeDef = TypedDict(
    "VersionUpdateByJobsConfigTypeDef",
    {
        "enabled": NotRequired[bool],
        "roleArn": NotRequired[str],
    },
)
GetPackageRequestRequestTypeDef = TypedDict(
    "GetPackageRequestRequestTypeDef",
    {
        "packageName": str,
    },
)
GetPackageVersionRequestRequestTypeDef = TypedDict(
    "GetPackageVersionRequestRequestTypeDef",
    {
        "packageName": str,
        "versionName": str,
    },
)
GetPercentilesRequestRequestTypeDef = TypedDict(
    "GetPercentilesRequestRequestTypeDef",
    {
        "queryString": str,
        "indexName": NotRequired[str],
        "aggregationField": NotRequired[str],
        "queryVersion": NotRequired[str],
        "percents": NotRequired[Sequence[float]],
    },
)
PercentPairTypeDef = TypedDict(
    "PercentPairTypeDef",
    {
        "percent": NotRequired[float],
        "value": NotRequired[float],
    },
)
GetPolicyRequestRequestTypeDef = TypedDict(
    "GetPolicyRequestRequestTypeDef",
    {
        "policyName": str,
    },
)
GetPolicyVersionRequestRequestTypeDef = TypedDict(
    "GetPolicyVersionRequestRequestTypeDef",
    {
        "policyName": str,
        "policyVersionId": str,
    },
)
GetStatisticsRequestRequestTypeDef = TypedDict(
    "GetStatisticsRequestRequestTypeDef",
    {
        "queryString": str,
        "indexName": NotRequired[str],
        "aggregationField": NotRequired[str],
        "queryVersion": NotRequired[str],
    },
)
StatisticsTypeDef = TypedDict(
    "StatisticsTypeDef",
    {
        "count": NotRequired[int],
        "average": NotRequired[float],
        "sum": NotRequired[float],
        "minimum": NotRequired[float],
        "maximum": NotRequired[float],
        "sumOfSquares": NotRequired[float],
        "variance": NotRequired[float],
        "stdDeviation": NotRequired[float],
    },
)
GetTopicRuleDestinationRequestRequestTypeDef = TypedDict(
    "GetTopicRuleDestinationRequestRequestTypeDef",
    {
        "arn": str,
    },
)
GetTopicRuleRequestRequestTypeDef = TypedDict(
    "GetTopicRuleRequestRequestTypeDef",
    {
        "ruleName": str,
    },
)
GroupNameAndArnTypeDef = TypedDict(
    "GroupNameAndArnTypeDef",
    {
        "groupName": NotRequired[str],
        "groupArn": NotRequired[str],
    },
)
HttpActionHeaderTypeDef = TypedDict(
    "HttpActionHeaderTypeDef",
    {
        "key": str,
        "value": str,
    },
)
SigV4AuthorizationTypeDef = TypedDict(
    "SigV4AuthorizationTypeDef",
    {
        "signingRegion": str,
        "serviceName": str,
        "roleArn": str,
    },
)
HttpContextTypeDef = TypedDict(
    "HttpContextTypeDef",
    {
        "headers": NotRequired[Mapping[str, str]],
        "queryString": NotRequired[str],
    },
)
HttpUrlDestinationConfigurationTypeDef = TypedDict(
    "HttpUrlDestinationConfigurationTypeDef",
    {
        "confirmationUrl": str,
    },
)
HttpUrlDestinationPropertiesTypeDef = TypedDict(
    "HttpUrlDestinationPropertiesTypeDef",
    {
        "confirmationUrl": NotRequired[str],
    },
)
HttpUrlDestinationSummaryTypeDef = TypedDict(
    "HttpUrlDestinationSummaryTypeDef",
    {
        "confirmationUrl": NotRequired[str],
    },
)
IssuerCertificateIdentifierTypeDef = TypedDict(
    "IssuerCertificateIdentifierTypeDef",
    {
        "issuerCertificateSubject": NotRequired[str],
        "issuerId": NotRequired[str],
        "issuerCertificateSerialNumber": NotRequired[str],
    },
)
JobExecutionStatusDetailsTypeDef = TypedDict(
    "JobExecutionStatusDetailsTypeDef",
    {
        "detailsMap": NotRequired[Dict[str, str]],
    },
)
JobExecutionSummaryTypeDef = TypedDict(
    "JobExecutionSummaryTypeDef",
    {
        "status": NotRequired[JobExecutionStatusType],
        "queuedAt": NotRequired[datetime],
        "startedAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "executionNumber": NotRequired[int],
        "retryAttempt": NotRequired[int],
    },
)
RetryCriteriaTypeDef = TypedDict(
    "RetryCriteriaTypeDef",
    {
        "failureType": RetryableFailureTypeType,
        "numberOfRetries": int,
    },
)
JobProcessDetailsTypeDef = TypedDict(
    "JobProcessDetailsTypeDef",
    {
        "processingTargets": NotRequired[List[str]],
        "numberOfCanceledThings": NotRequired[int],
        "numberOfSucceededThings": NotRequired[int],
        "numberOfFailedThings": NotRequired[int],
        "numberOfRejectedThings": NotRequired[int],
        "numberOfQueuedThings": NotRequired[int],
        "numberOfInProgressThings": NotRequired[int],
        "numberOfRemovedThings": NotRequired[int],
        "numberOfTimedOutThings": NotRequired[int],
    },
)
JobSummaryTypeDef = TypedDict(
    "JobSummaryTypeDef",
    {
        "jobArn": NotRequired[str],
        "jobId": NotRequired[str],
        "thingGroupId": NotRequired[str],
        "targetSelection": NotRequired[TargetSelectionType],
        "status": NotRequired[JobStatusType],
        "createdAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "completedAt": NotRequired[datetime],
        "isConcurrent": NotRequired[bool],
    },
)
JobTemplateSummaryTypeDef = TypedDict(
    "JobTemplateSummaryTypeDef",
    {
        "jobTemplateArn": NotRequired[str],
        "jobTemplateId": NotRequired[str],
        "description": NotRequired[str],
        "createdAt": NotRequired[datetime],
    },
)
ScheduledJobRolloutTypeDef = TypedDict(
    "ScheduledJobRolloutTypeDef",
    {
        "startTime": NotRequired[str],
    },
)
KafkaActionHeaderTypeDef = TypedDict(
    "KafkaActionHeaderTypeDef",
    {
        "key": str,
        "value": str,
    },
)
ListActiveViolationsRequestRequestTypeDef = TypedDict(
    "ListActiveViolationsRequestRequestTypeDef",
    {
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behaviorCriteriaType": NotRequired[BehaviorCriteriaTypeType],
        "listSuppressedAlerts": NotRequired[bool],
        "verificationState": NotRequired[VerificationStateType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListAttachedPoliciesRequestRequestTypeDef = TypedDict(
    "ListAttachedPoliciesRequestRequestTypeDef",
    {
        "target": str,
        "recursive": NotRequired[bool],
        "marker": NotRequired[str],
        "pageSize": NotRequired[int],
    },
)
ListAuditMitigationActionsExecutionsRequestRequestTypeDef = TypedDict(
    "ListAuditMitigationActionsExecutionsRequestRequestTypeDef",
    {
        "taskId": str,
        "findingId": str,
        "actionStatus": NotRequired[AuditMitigationActionsExecutionStatusType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListAuthorizersRequestRequestTypeDef = TypedDict(
    "ListAuthorizersRequestRequestTypeDef",
    {
        "pageSize": NotRequired[int],
        "marker": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
        "status": NotRequired[AuthorizerStatusType],
    },
)
ListBillingGroupsRequestRequestTypeDef = TypedDict(
    "ListBillingGroupsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "namePrefixFilter": NotRequired[str],
    },
)
ListCACertificatesRequestRequestTypeDef = TypedDict(
    "ListCACertificatesRequestRequestTypeDef",
    {
        "pageSize": NotRequired[int],
        "marker": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
        "templateName": NotRequired[str],
    },
)
ListCertificateProvidersRequestRequestTypeDef = TypedDict(
    "ListCertificateProvidersRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
    },
)
ListCertificatesByCARequestRequestTypeDef = TypedDict(
    "ListCertificatesByCARequestRequestTypeDef",
    {
        "caCertificateId": str,
        "pageSize": NotRequired[int],
        "marker": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
    },
)
ListCertificatesRequestRequestTypeDef = TypedDict(
    "ListCertificatesRequestRequestTypeDef",
    {
        "pageSize": NotRequired[int],
        "marker": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
    },
)
ListCustomMetricsRequestRequestTypeDef = TypedDict(
    "ListCustomMetricsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListDimensionsRequestRequestTypeDef = TypedDict(
    "ListDimensionsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListDomainConfigurationsRequestRequestTypeDef = TypedDict(
    "ListDomainConfigurationsRequestRequestTypeDef",
    {
        "marker": NotRequired[str],
        "pageSize": NotRequired[int],
        "serviceType": NotRequired[ServiceTypeType],
    },
)
ListFleetMetricsRequestRequestTypeDef = TypedDict(
    "ListFleetMetricsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListIndicesRequestRequestTypeDef = TypedDict(
    "ListIndicesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListJobExecutionsForJobRequestRequestTypeDef = TypedDict(
    "ListJobExecutionsForJobRequestRequestTypeDef",
    {
        "jobId": str,
        "status": NotRequired[JobExecutionStatusType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListJobExecutionsForThingRequestRequestTypeDef = TypedDict(
    "ListJobExecutionsForThingRequestRequestTypeDef",
    {
        "thingName": str,
        "status": NotRequired[JobExecutionStatusType],
        "namespaceId": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "jobId": NotRequired[str],
    },
)
ListJobTemplatesRequestRequestTypeDef = TypedDict(
    "ListJobTemplatesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListJobsRequestRequestTypeDef = TypedDict(
    "ListJobsRequestRequestTypeDef",
    {
        "status": NotRequired[JobStatusType],
        "targetSelection": NotRequired[TargetSelectionType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "thingGroupName": NotRequired[str],
        "thingGroupId": NotRequired[str],
        "namespaceId": NotRequired[str],
    },
)
ListManagedJobTemplatesRequestRequestTypeDef = TypedDict(
    "ListManagedJobTemplatesRequestRequestTypeDef",
    {
        "templateName": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ManagedJobTemplateSummaryTypeDef = TypedDict(
    "ManagedJobTemplateSummaryTypeDef",
    {
        "templateArn": NotRequired[str],
        "templateName": NotRequired[str],
        "description": NotRequired[str],
        "environments": NotRequired[List[str]],
        "templateVersion": NotRequired[str],
    },
)
ListMitigationActionsRequestRequestTypeDef = TypedDict(
    "ListMitigationActionsRequestRequestTypeDef",
    {
        "actionType": NotRequired[MitigationActionTypeType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
MitigationActionIdentifierTypeDef = TypedDict(
    "MitigationActionIdentifierTypeDef",
    {
        "actionName": NotRequired[str],
        "actionArn": NotRequired[str],
        "creationDate": NotRequired[datetime],
    },
)
ListOTAUpdatesRequestRequestTypeDef = TypedDict(
    "ListOTAUpdatesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "otaUpdateStatus": NotRequired[OTAUpdateStatusType],
    },
)
OTAUpdateSummaryTypeDef = TypedDict(
    "OTAUpdateSummaryTypeDef",
    {
        "otaUpdateId": NotRequired[str],
        "otaUpdateArn": NotRequired[str],
        "creationDate": NotRequired[datetime],
    },
)
ListOutgoingCertificatesRequestRequestTypeDef = TypedDict(
    "ListOutgoingCertificatesRequestRequestTypeDef",
    {
        "pageSize": NotRequired[int],
        "marker": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
    },
)
OutgoingCertificateTypeDef = TypedDict(
    "OutgoingCertificateTypeDef",
    {
        "certificateArn": NotRequired[str],
        "certificateId": NotRequired[str],
        "transferredTo": NotRequired[str],
        "transferDate": NotRequired[datetime],
        "transferMessage": NotRequired[str],
        "creationDate": NotRequired[datetime],
    },
)
ListPackageVersionsRequestRequestTypeDef = TypedDict(
    "ListPackageVersionsRequestRequestTypeDef",
    {
        "packageName": str,
        "status": NotRequired[PackageVersionStatusType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
PackageVersionSummaryTypeDef = TypedDict(
    "PackageVersionSummaryTypeDef",
    {
        "packageName": NotRequired[str],
        "versionName": NotRequired[str],
        "status": NotRequired[PackageVersionStatusType],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
    },
)
ListPackagesRequestRequestTypeDef = TypedDict(
    "ListPackagesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
PackageSummaryTypeDef = TypedDict(
    "PackageSummaryTypeDef",
    {
        "packageName": NotRequired[str],
        "defaultVersionName": NotRequired[str],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
    },
)
ListPoliciesRequestRequestTypeDef = TypedDict(
    "ListPoliciesRequestRequestTypeDef",
    {
        "marker": NotRequired[str],
        "pageSize": NotRequired[int],
        "ascendingOrder": NotRequired[bool],
    },
)
ListPolicyPrincipalsRequestRequestTypeDef = TypedDict(
    "ListPolicyPrincipalsRequestRequestTypeDef",
    {
        "policyName": str,
        "marker": NotRequired[str],
        "pageSize": NotRequired[int],
        "ascendingOrder": NotRequired[bool],
    },
)
ListPolicyVersionsRequestRequestTypeDef = TypedDict(
    "ListPolicyVersionsRequestRequestTypeDef",
    {
        "policyName": str,
    },
)
PolicyVersionTypeDef = TypedDict(
    "PolicyVersionTypeDef",
    {
        "versionId": NotRequired[str],
        "isDefaultVersion": NotRequired[bool],
        "createDate": NotRequired[datetime],
    },
)
ListPrincipalPoliciesRequestRequestTypeDef = TypedDict(
    "ListPrincipalPoliciesRequestRequestTypeDef",
    {
        "principal": str,
        "marker": NotRequired[str],
        "pageSize": NotRequired[int],
        "ascendingOrder": NotRequired[bool],
    },
)
ListPrincipalThingsRequestRequestTypeDef = TypedDict(
    "ListPrincipalThingsRequestRequestTypeDef",
    {
        "principal": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListProvisioningTemplateVersionsRequestRequestTypeDef = TypedDict(
    "ListProvisioningTemplateVersionsRequestRequestTypeDef",
    {
        "templateName": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ProvisioningTemplateVersionSummaryTypeDef = TypedDict(
    "ProvisioningTemplateVersionSummaryTypeDef",
    {
        "versionId": NotRequired[int],
        "creationDate": NotRequired[datetime],
        "isDefaultVersion": NotRequired[bool],
    },
)
ListProvisioningTemplatesRequestRequestTypeDef = TypedDict(
    "ListProvisioningTemplatesRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ProvisioningTemplateSummaryTypeDef = TypedDict(
    "ProvisioningTemplateSummaryTypeDef",
    {
        "templateArn": NotRequired[str],
        "templateName": NotRequired[str],
        "description": NotRequired[str],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
        "enabled": NotRequired[bool],
        "type": NotRequired[TemplateTypeType],
    },
)
ListRelatedResourcesForAuditFindingRequestRequestTypeDef = TypedDict(
    "ListRelatedResourcesForAuditFindingRequestRequestTypeDef",
    {
        "findingId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListRoleAliasesRequestRequestTypeDef = TypedDict(
    "ListRoleAliasesRequestRequestTypeDef",
    {
        "pageSize": NotRequired[int],
        "marker": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
    },
)
ListScheduledAuditsRequestRequestTypeDef = TypedDict(
    "ListScheduledAuditsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ScheduledAuditMetadataTypeDef = TypedDict(
    "ScheduledAuditMetadataTypeDef",
    {
        "scheduledAuditName": NotRequired[str],
        "scheduledAuditArn": NotRequired[str],
        "frequency": NotRequired[AuditFrequencyType],
        "dayOfMonth": NotRequired[str],
        "dayOfWeek": NotRequired[DayOfWeekType],
    },
)
ListSecurityProfilesForTargetRequestRequestTypeDef = TypedDict(
    "ListSecurityProfilesForTargetRequestRequestTypeDef",
    {
        "securityProfileTargetArn": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "recursive": NotRequired[bool],
    },
)
ListSecurityProfilesRequestRequestTypeDef = TypedDict(
    "ListSecurityProfilesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "dimensionName": NotRequired[str],
        "metricName": NotRequired[str],
    },
)
SecurityProfileIdentifierTypeDef = TypedDict(
    "SecurityProfileIdentifierTypeDef",
    {
        "name": str,
        "arn": str,
    },
)
ListStreamsRequestRequestTypeDef = TypedDict(
    "ListStreamsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "ascendingOrder": NotRequired[bool],
    },
)
StreamSummaryTypeDef = TypedDict(
    "StreamSummaryTypeDef",
    {
        "streamId": NotRequired[str],
        "streamArn": NotRequired[str],
        "streamVersion": NotRequired[int],
        "description": NotRequired[str],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "nextToken": NotRequired[str],
    },
)
ListTargetsForPolicyRequestRequestTypeDef = TypedDict(
    "ListTargetsForPolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "marker": NotRequired[str],
        "pageSize": NotRequired[int],
    },
)
ListTargetsForSecurityProfileRequestRequestTypeDef = TypedDict(
    "ListTargetsForSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
SecurityProfileTargetTypeDef = TypedDict(
    "SecurityProfileTargetTypeDef",
    {
        "arn": str,
    },
)
ListThingGroupsForThingRequestRequestTypeDef = TypedDict(
    "ListThingGroupsForThingRequestRequestTypeDef",
    {
        "thingName": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListThingGroupsRequestRequestTypeDef = TypedDict(
    "ListThingGroupsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "parentGroup": NotRequired[str],
        "namePrefixFilter": NotRequired[str],
        "recursive": NotRequired[bool],
    },
)
ListThingPrincipalsRequestRequestTypeDef = TypedDict(
    "ListThingPrincipalsRequestRequestTypeDef",
    {
        "thingName": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListThingRegistrationTaskReportsRequestRequestTypeDef = TypedDict(
    "ListThingRegistrationTaskReportsRequestRequestTypeDef",
    {
        "taskId": str,
        "reportType": ReportTypeType,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListThingRegistrationTasksRequestRequestTypeDef = TypedDict(
    "ListThingRegistrationTasksRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "status": NotRequired[StatusType],
    },
)
ListThingTypesRequestRequestTypeDef = TypedDict(
    "ListThingTypesRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "thingTypeName": NotRequired[str],
    },
)
ListThingsInBillingGroupRequestRequestTypeDef = TypedDict(
    "ListThingsInBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListThingsInThingGroupRequestRequestTypeDef = TypedDict(
    "ListThingsInThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "recursive": NotRequired[bool],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListThingsRequestRequestTypeDef = TypedDict(
    "ListThingsRequestRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "attributeName": NotRequired[str],
        "attributeValue": NotRequired[str],
        "thingTypeName": NotRequired[str],
        "usePrefixAttributeValue": NotRequired[bool],
    },
)
ThingAttributeTypeDef = TypedDict(
    "ThingAttributeTypeDef",
    {
        "thingName": NotRequired[str],
        "thingTypeName": NotRequired[str],
        "thingArn": NotRequired[str],
        "attributes": NotRequired[Dict[str, str]],
        "version": NotRequired[int],
    },
)
ListTopicRuleDestinationsRequestRequestTypeDef = TypedDict(
    "ListTopicRuleDestinationsRequestRequestTypeDef",
    {
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListTopicRulesRequestRequestTypeDef = TypedDict(
    "ListTopicRulesRequestRequestTypeDef",
    {
        "topic": NotRequired[str],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "ruleDisabled": NotRequired[bool],
    },
)
TopicRuleListItemTypeDef = TypedDict(
    "TopicRuleListItemTypeDef",
    {
        "ruleArn": NotRequired[str],
        "ruleName": NotRequired[str],
        "topicPattern": NotRequired[str],
        "createdAt": NotRequired[datetime],
        "ruleDisabled": NotRequired[bool],
    },
)
ListV2LoggingLevelsRequestRequestTypeDef = TypedDict(
    "ListV2LoggingLevelsRequestRequestTypeDef",
    {
        "targetType": NotRequired[LogTargetTypeType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
LocationTimestampTypeDef = TypedDict(
    "LocationTimestampTypeDef",
    {
        "value": str,
        "unit": NotRequired[str],
    },
)
LogTargetTypeDef = TypedDict(
    "LogTargetTypeDef",
    {
        "targetType": LogTargetTypeType,
        "targetName": NotRequired[str],
    },
)
LoggingOptionsPayloadTypeDef = TypedDict(
    "LoggingOptionsPayloadTypeDef",
    {
        "roleArn": str,
        "logLevel": NotRequired[LogLevelType],
    },
)
PublishFindingToSnsParamsTypeDef = TypedDict(
    "PublishFindingToSnsParamsTypeDef",
    {
        "topicArn": str,
    },
)
ReplaceDefaultPolicyVersionParamsTypeDef = TypedDict(
    "ReplaceDefaultPolicyVersionParamsTypeDef",
    {
        "templateName": Literal["BLANK_POLICY"],
    },
)
UpdateCACertificateParamsTypeDef = TypedDict(
    "UpdateCACertificateParamsTypeDef",
    {
        "action": Literal["DEACTIVATE"],
    },
)
UpdateDeviceCertificateParamsTypeDef = TypedDict(
    "UpdateDeviceCertificateParamsTypeDef",
    {
        "action": Literal["DEACTIVATE"],
    },
)
UserPropertyTypeDef = TypedDict(
    "UserPropertyTypeDef",
    {
        "key": str,
        "value": str,
    },
)
PolicyVersionIdentifierTypeDef = TypedDict(
    "PolicyVersionIdentifierTypeDef",
    {
        "policyName": NotRequired[str],
        "policyVersionId": NotRequired[str],
    },
)
PutVerificationStateOnViolationRequestRequestTypeDef = TypedDict(
    "PutVerificationStateOnViolationRequestRequestTypeDef",
    {
        "violationId": str,
        "verificationState": VerificationStateType,
        "verificationStateDescription": NotRequired[str],
    },
)
RegisterCertificateRequestRequestTypeDef = TypedDict(
    "RegisterCertificateRequestRequestTypeDef",
    {
        "certificatePem": str,
        "caCertificatePem": NotRequired[str],
        "setAsActive": NotRequired[bool],
        "status": NotRequired[CertificateStatusType],
    },
)
RegisterCertificateWithoutCARequestRequestTypeDef = TypedDict(
    "RegisterCertificateWithoutCARequestRequestTypeDef",
    {
        "certificatePem": str,
        "status": NotRequired[CertificateStatusType],
    },
)
RegisterThingRequestRequestTypeDef = TypedDict(
    "RegisterThingRequestRequestTypeDef",
    {
        "templateBody": str,
        "parameters": NotRequired[Mapping[str, str]],
    },
)
RejectCertificateTransferRequestRequestTypeDef = TypedDict(
    "RejectCertificateTransferRequestRequestTypeDef",
    {
        "certificateId": str,
        "rejectReason": NotRequired[str],
    },
)
RemoveThingFromBillingGroupRequestRequestTypeDef = TypedDict(
    "RemoveThingFromBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": NotRequired[str],
        "billingGroupArn": NotRequired[str],
        "thingName": NotRequired[str],
        "thingArn": NotRequired[str],
    },
)
RemoveThingFromThingGroupRequestRequestTypeDef = TypedDict(
    "RemoveThingFromThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": NotRequired[str],
        "thingGroupArn": NotRequired[str],
        "thingName": NotRequired[str],
        "thingArn": NotRequired[str],
    },
)
SearchIndexRequestRequestTypeDef = TypedDict(
    "SearchIndexRequestRequestTypeDef",
    {
        "queryString": str,
        "indexName": NotRequired[str],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
        "queryVersion": NotRequired[str],
    },
)
ThingGroupDocumentTypeDef = TypedDict(
    "ThingGroupDocumentTypeDef",
    {
        "thingGroupName": NotRequired[str],
        "thingGroupId": NotRequired[str],
        "thingGroupDescription": NotRequired[str],
        "attributes": NotRequired[Dict[str, str]],
        "parentGroupNames": NotRequired[List[str]],
    },
)
SetDefaultAuthorizerRequestRequestTypeDef = TypedDict(
    "SetDefaultAuthorizerRequestRequestTypeDef",
    {
        "authorizerName": str,
    },
)
SetDefaultPolicyVersionRequestRequestTypeDef = TypedDict(
    "SetDefaultPolicyVersionRequestRequestTypeDef",
    {
        "policyName": str,
        "policyVersionId": str,
    },
)
SetV2LoggingOptionsRequestRequestTypeDef = TypedDict(
    "SetV2LoggingOptionsRequestRequestTypeDef",
    {
        "roleArn": NotRequired[str],
        "defaultLogLevel": NotRequired[LogLevelType],
        "disableAllLogs": NotRequired[bool],
    },
)
SigningProfileParameterTypeDef = TypedDict(
    "SigningProfileParameterTypeDef",
    {
        "certificateArn": NotRequired[str],
        "platform": NotRequired[str],
        "certificatePathOnDevice": NotRequired[str],
    },
)
StartOnDemandAuditTaskRequestRequestTypeDef = TypedDict(
    "StartOnDemandAuditTaskRequestRequestTypeDef",
    {
        "targetCheckNames": Sequence[str],
    },
)
StartThingRegistrationTaskRequestRequestTypeDef = TypedDict(
    "StartThingRegistrationTaskRequestRequestTypeDef",
    {
        "templateBody": str,
        "inputFileBucket": str,
        "inputFileKey": str,
        "roleArn": str,
    },
)
StopThingRegistrationTaskRequestRequestTypeDef = TypedDict(
    "StopThingRegistrationTaskRequestRequestTypeDef",
    {
        "taskId": str,
    },
)
TlsContextTypeDef = TypedDict(
    "TlsContextTypeDef",
    {
        "serverName": NotRequired[str],
    },
)
ThingConnectivityTypeDef = TypedDict(
    "ThingConnectivityTypeDef",
    {
        "connected": NotRequired[bool],
        "timestamp": NotRequired[int],
        "disconnectReason": NotRequired[str],
    },
)
ThingTypePropertiesPaginatorTypeDef = TypedDict(
    "ThingTypePropertiesPaginatorTypeDef",
    {
        "thingTypeDescription": NotRequired[str],
        "searchableAttributes": NotRequired[List[str]],
    },
)
TimestreamDimensionTypeDef = TypedDict(
    "TimestreamDimensionTypeDef",
    {
        "name": str,
        "value": str,
    },
)
TimestreamTimestampTypeDef = TypedDict(
    "TimestreamTimestampTypeDef",
    {
        "value": str,
        "unit": str,
    },
)
VpcDestinationConfigurationTypeDef = TypedDict(
    "VpcDestinationConfigurationTypeDef",
    {
        "subnetIds": Sequence[str],
        "vpcId": str,
        "roleArn": str,
        "securityGroups": NotRequired[Sequence[str]],
    },
)
VpcDestinationSummaryTypeDef = TypedDict(
    "VpcDestinationSummaryTypeDef",
    {
        "subnetIds": NotRequired[List[str]],
        "securityGroups": NotRequired[List[str]],
        "vpcId": NotRequired[str],
        "roleArn": NotRequired[str],
    },
)
VpcDestinationPropertiesTypeDef = TypedDict(
    "VpcDestinationPropertiesTypeDef",
    {
        "subnetIds": NotRequired[List[str]],
        "securityGroups": NotRequired[List[str]],
        "vpcId": NotRequired[str],
        "roleArn": NotRequired[str],
    },
)
TransferCertificateRequestRequestTypeDef = TypedDict(
    "TransferCertificateRequestRequestTypeDef",
    {
        "certificateId": str,
        "targetAwsAccount": str,
        "transferMessage": NotRequired[str],
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
UpdateAuthorizerRequestRequestTypeDef = TypedDict(
    "UpdateAuthorizerRequestRequestTypeDef",
    {
        "authorizerName": str,
        "authorizerFunctionArn": NotRequired[str],
        "tokenKeyName": NotRequired[str],
        "tokenSigningPublicKeys": NotRequired[Mapping[str, str]],
        "status": NotRequired[AuthorizerStatusType],
        "enableCachingForHttp": NotRequired[bool],
    },
)
UpdateCertificateProviderRequestRequestTypeDef = TypedDict(
    "UpdateCertificateProviderRequestRequestTypeDef",
    {
        "certificateProviderName": str,
        "lambdaFunctionArn": NotRequired[str],
        "accountDefaultForOperations": NotRequired[Sequence[Literal["CreateCertificateFromCsr"]]],
    },
)
UpdateCertificateRequestRequestTypeDef = TypedDict(
    "UpdateCertificateRequestRequestTypeDef",
    {
        "certificateId": str,
        "newStatus": CertificateStatusType,
    },
)
UpdateCustomMetricRequestRequestTypeDef = TypedDict(
    "UpdateCustomMetricRequestRequestTypeDef",
    {
        "metricName": str,
        "displayName": str,
    },
)
UpdateDimensionRequestRequestTypeDef = TypedDict(
    "UpdateDimensionRequestRequestTypeDef",
    {
        "name": str,
        "stringValues": Sequence[str],
    },
)
UpdatePackageRequestRequestTypeDef = TypedDict(
    "UpdatePackageRequestRequestTypeDef",
    {
        "packageName": str,
        "description": NotRequired[str],
        "defaultVersionName": NotRequired[str],
        "unsetDefaultVersion": NotRequired[bool],
        "clientToken": NotRequired[str],
    },
)
UpdatePackageVersionRequestRequestTypeDef = TypedDict(
    "UpdatePackageVersionRequestRequestTypeDef",
    {
        "packageName": str,
        "versionName": str,
        "description": NotRequired[str],
        "attributes": NotRequired[Mapping[str, str]],
        "action": NotRequired[PackageVersionActionType],
        "clientToken": NotRequired[str],
    },
)
UpdateRoleAliasRequestRequestTypeDef = TypedDict(
    "UpdateRoleAliasRequestRequestTypeDef",
    {
        "roleAlias": str,
        "roleArn": NotRequired[str],
        "credentialDurationSeconds": NotRequired[int],
    },
)
UpdateScheduledAuditRequestRequestTypeDef = TypedDict(
    "UpdateScheduledAuditRequestRequestTypeDef",
    {
        "scheduledAuditName": str,
        "frequency": NotRequired[AuditFrequencyType],
        "dayOfMonth": NotRequired[str],
        "dayOfWeek": NotRequired[DayOfWeekType],
        "targetCheckNames": NotRequired[Sequence[str]],
    },
)
UpdateThingGroupsForThingRequestRequestTypeDef = TypedDict(
    "UpdateThingGroupsForThingRequestRequestTypeDef",
    {
        "thingName": NotRequired[str],
        "thingGroupsToAdd": NotRequired[Sequence[str]],
        "thingGroupsToRemove": NotRequired[Sequence[str]],
        "overrideDynamicGroups": NotRequired[bool],
    },
)
UpdateTopicRuleDestinationRequestRequestTypeDef = TypedDict(
    "UpdateTopicRuleDestinationRequestRequestTypeDef",
    {
        "arn": str,
        "status": TopicRuleDestinationStatusType,
    },
)
ValidationErrorTypeDef = TypedDict(
    "ValidationErrorTypeDef",
    {
        "errorMessage": NotRequired[str],
    },
)
AbortConfigTypeDef = TypedDict(
    "AbortConfigTypeDef",
    {
        "criteriaList": Sequence[AbortCriteriaTypeDef],
    },
)
MetricDatumPaginatorTypeDef = TypedDict(
    "MetricDatumPaginatorTypeDef",
    {
        "timestamp": NotRequired[datetime],
        "value": NotRequired[MetricValuePaginatorTypeDef],
    },
)
MetricDatumTypeDef = TypedDict(
    "MetricDatumTypeDef",
    {
        "timestamp": NotRequired[datetime],
        "value": NotRequired[MetricValueTypeDef],
    },
)
UpdateFleetMetricRequestRequestTypeDef = TypedDict(
    "UpdateFleetMetricRequestRequestTypeDef",
    {
        "metricName": str,
        "indexName": str,
        "queryString": NotRequired[str],
        "aggregationType": NotRequired[AggregationTypeTypeDef],
        "period": NotRequired[int],
        "aggregationField": NotRequired[str],
        "description": NotRequired[str],
        "queryVersion": NotRequired[str],
        "unit": NotRequired[FleetMetricUnitType],
        "expectedVersion": NotRequired[int],
    },
)
AllowedTypeDef = TypedDict(
    "AllowedTypeDef",
    {
        "policies": NotRequired[List[PolicyTypeDef]],
    },
)
ExplicitDenyTypeDef = TypedDict(
    "ExplicitDenyTypeDef",
    {
        "policies": NotRequired[List[PolicyTypeDef]],
    },
)
ImplicitDenyTypeDef = TypedDict(
    "ImplicitDenyTypeDef",
    {
        "policies": NotRequired[List[PolicyTypeDef]],
    },
)
AssetPropertyValueTypeDef = TypedDict(
    "AssetPropertyValueTypeDef",
    {
        "value": AssetPropertyVariantTypeDef,
        "timestamp": AssetPropertyTimestampTypeDef,
        "quality": NotRequired[str],
    },
)
AssociateTargetsWithJobResponseTypeDef = TypedDict(
    "AssociateTargetsWithJobResponseTypeDef",
    {
        "jobArn": str,
        "jobId": str,
        "description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CancelJobResponseTypeDef = TypedDict(
    "CancelJobResponseTypeDef",
    {
        "jobArn": str,
        "jobId": str,
        "description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAuthorizerResponseTypeDef = TypedDict(
    "CreateAuthorizerResponseTypeDef",
    {
        "authorizerName": str,
        "authorizerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBillingGroupResponseTypeDef = TypedDict(
    "CreateBillingGroupResponseTypeDef",
    {
        "billingGroupName": str,
        "billingGroupArn": str,
        "billingGroupId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCertificateFromCsrResponseTypeDef = TypedDict(
    "CreateCertificateFromCsrResponseTypeDef",
    {
        "certificateArn": str,
        "certificateId": str,
        "certificatePem": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCertificateProviderResponseTypeDef = TypedDict(
    "CreateCertificateProviderResponseTypeDef",
    {
        "certificateProviderName": str,
        "certificateProviderArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateCustomMetricResponseTypeDef = TypedDict(
    "CreateCustomMetricResponseTypeDef",
    {
        "metricName": str,
        "metricArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDimensionResponseTypeDef = TypedDict(
    "CreateDimensionResponseTypeDef",
    {
        "name": str,
        "arn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDomainConfigurationResponseTypeDef = TypedDict(
    "CreateDomainConfigurationResponseTypeDef",
    {
        "domainConfigurationName": str,
        "domainConfigurationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateDynamicThingGroupResponseTypeDef = TypedDict(
    "CreateDynamicThingGroupResponseTypeDef",
    {
        "thingGroupName": str,
        "thingGroupArn": str,
        "thingGroupId": str,
        "indexName": str,
        "queryString": str,
        "queryVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateFleetMetricResponseTypeDef = TypedDict(
    "CreateFleetMetricResponseTypeDef",
    {
        "metricName": str,
        "metricArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateJobResponseTypeDef = TypedDict(
    "CreateJobResponseTypeDef",
    {
        "jobArn": str,
        "jobId": str,
        "description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateJobTemplateResponseTypeDef = TypedDict(
    "CreateJobTemplateResponseTypeDef",
    {
        "jobTemplateArn": str,
        "jobTemplateId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateMitigationActionResponseTypeDef = TypedDict(
    "CreateMitigationActionResponseTypeDef",
    {
        "actionArn": str,
        "actionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateOTAUpdateResponseTypeDef = TypedDict(
    "CreateOTAUpdateResponseTypeDef",
    {
        "otaUpdateId": str,
        "awsIotJobId": str,
        "otaUpdateArn": str,
        "awsIotJobArn": str,
        "otaUpdateStatus": OTAUpdateStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePackageResponseTypeDef = TypedDict(
    "CreatePackageResponseTypeDef",
    {
        "packageName": str,
        "packageArn": str,
        "description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePackageVersionResponseTypeDef = TypedDict(
    "CreatePackageVersionResponseTypeDef",
    {
        "packageVersionArn": str,
        "packageName": str,
        "versionName": str,
        "description": str,
        "attributes": Dict[str, str],
        "status": PackageVersionStatusType,
        "errorReason": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePolicyResponseTypeDef = TypedDict(
    "CreatePolicyResponseTypeDef",
    {
        "policyName": str,
        "policyArn": str,
        "policyDocument": str,
        "policyVersionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePolicyVersionResponseTypeDef = TypedDict(
    "CreatePolicyVersionResponseTypeDef",
    {
        "policyArn": str,
        "policyDocument": str,
        "policyVersionId": str,
        "isDefaultVersion": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProvisioningTemplateResponseTypeDef = TypedDict(
    "CreateProvisioningTemplateResponseTypeDef",
    {
        "templateArn": str,
        "templateName": str,
        "defaultVersionId": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProvisioningTemplateVersionResponseTypeDef = TypedDict(
    "CreateProvisioningTemplateVersionResponseTypeDef",
    {
        "templateArn": str,
        "templateName": str,
        "versionId": int,
        "isDefaultVersion": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRoleAliasResponseTypeDef = TypedDict(
    "CreateRoleAliasResponseTypeDef",
    {
        "roleAlias": str,
        "roleAliasArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateScheduledAuditResponseTypeDef = TypedDict(
    "CreateScheduledAuditResponseTypeDef",
    {
        "scheduledAuditArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateSecurityProfileResponseTypeDef = TypedDict(
    "CreateSecurityProfileResponseTypeDef",
    {
        "securityProfileName": str,
        "securityProfileArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateStreamResponseTypeDef = TypedDict(
    "CreateStreamResponseTypeDef",
    {
        "streamId": str,
        "streamArn": str,
        "description": str,
        "streamVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateThingGroupResponseTypeDef = TypedDict(
    "CreateThingGroupResponseTypeDef",
    {
        "thingGroupName": str,
        "thingGroupArn": str,
        "thingGroupId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateThingResponseTypeDef = TypedDict(
    "CreateThingResponseTypeDef",
    {
        "thingName": str,
        "thingArn": str,
        "thingId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateThingTypeResponseTypeDef = TypedDict(
    "CreateThingTypeResponseTypeDef",
    {
        "thingTypeName": str,
        "thingTypeArn": str,
        "thingTypeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeCertificateProviderResponseTypeDef = TypedDict(
    "DescribeCertificateProviderResponseTypeDef",
    {
        "certificateProviderName": str,
        "certificateProviderArn": str,
        "lambdaFunctionArn": str,
        "accountDefaultForOperations": List[Literal["CreateCertificateFromCsr"]],
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeCustomMetricResponseTypeDef = TypedDict(
    "DescribeCustomMetricResponseTypeDef",
    {
        "metricName": str,
        "metricArn": str,
        "metricType": CustomMetricTypeType,
        "displayName": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDimensionResponseTypeDef = TypedDict(
    "DescribeDimensionResponseTypeDef",
    {
        "name": str,
        "arn": str,
        "type": Literal["TOPIC_FILTER"],
        "stringValues": List[str],
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeEndpointResponseTypeDef = TypedDict(
    "DescribeEndpointResponseTypeDef",
    {
        "endpointAddress": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeFleetMetricResponseTypeDef = TypedDict(
    "DescribeFleetMetricResponseTypeDef",
    {
        "metricName": str,
        "queryString": str,
        "aggregationType": AggregationTypeTypeDef,
        "period": int,
        "aggregationField": str,
        "description": str,
        "queryVersion": str,
        "indexName": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "unit": FleetMetricUnitType,
        "version": int,
        "metricArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeIndexResponseTypeDef = TypedDict(
    "DescribeIndexResponseTypeDef",
    {
        "indexName": str,
        "indexStatus": IndexStatusType,
        "schema": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeProvisioningTemplateVersionResponseTypeDef = TypedDict(
    "DescribeProvisioningTemplateVersionResponseTypeDef",
    {
        "versionId": int,
        "creationDate": datetime,
        "templateBody": str,
        "isDefaultVersion": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeScheduledAuditResponseTypeDef = TypedDict(
    "DescribeScheduledAuditResponseTypeDef",
    {
        "frequency": AuditFrequencyType,
        "dayOfMonth": str,
        "dayOfWeek": DayOfWeekType,
        "targetCheckNames": List[str],
        "scheduledAuditName": str,
        "scheduledAuditArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeThingRegistrationTaskResponseTypeDef = TypedDict(
    "DescribeThingRegistrationTaskResponseTypeDef",
    {
        "taskId": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "templateBody": str,
        "inputFileBucket": str,
        "inputFileKey": str,
        "roleArn": str,
        "status": StatusType,
        "message": str,
        "successCount": int,
        "failureCount": int,
        "percentageProgress": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeThingResponseTypeDef = TypedDict(
    "DescribeThingResponseTypeDef",
    {
        "defaultClientId": str,
        "thingName": str,
        "thingId": str,
        "thingArn": str,
        "thingTypeName": str,
        "attributes": Dict[str, str],
        "version": int,
        "billingGroupName": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetCardinalityResponseTypeDef = TypedDict(
    "GetCardinalityResponseTypeDef",
    {
        "cardinality": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetJobDocumentResponseTypeDef = TypedDict(
    "GetJobDocumentResponseTypeDef",
    {
        "document": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetLoggingOptionsResponseTypeDef = TypedDict(
    "GetLoggingOptionsResponseTypeDef",
    {
        "roleArn": str,
        "logLevel": LogLevelType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPackageResponseTypeDef = TypedDict(
    "GetPackageResponseTypeDef",
    {
        "packageName": str,
        "packageArn": str,
        "description": str,
        "defaultVersionName": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPackageVersionResponseTypeDef = TypedDict(
    "GetPackageVersionResponseTypeDef",
    {
        "packageVersionArn": str,
        "packageName": str,
        "versionName": str,
        "description": str,
        "attributes": Dict[str, str],
        "status": PackageVersionStatusType,
        "errorReason": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPolicyResponseTypeDef = TypedDict(
    "GetPolicyResponseTypeDef",
    {
        "policyName": str,
        "policyArn": str,
        "policyDocument": str,
        "defaultVersionId": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "generationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPolicyVersionResponseTypeDef = TypedDict(
    "GetPolicyVersionResponseTypeDef",
    {
        "policyArn": str,
        "policyName": str,
        "policyDocument": str,
        "policyVersionId": str,
        "isDefaultVersion": bool,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "generationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetRegistrationCodeResponseTypeDef = TypedDict(
    "GetRegistrationCodeResponseTypeDef",
    {
        "registrationCode": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetV2LoggingOptionsResponseTypeDef = TypedDict(
    "GetV2LoggingOptionsResponseTypeDef",
    {
        "roleArn": str,
        "defaultLogLevel": LogLevelType,
        "disableAllLogs": bool,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAttachedPoliciesResponseTypeDef = TypedDict(
    "ListAttachedPoliciesResponseTypeDef",
    {
        "policies": List[PolicyTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCustomMetricsResponseTypeDef = TypedDict(
    "ListCustomMetricsResponseTypeDef",
    {
        "metricNames": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDimensionsResponseTypeDef = TypedDict(
    "ListDimensionsResponseTypeDef",
    {
        "dimensionNames": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListIndicesResponseTypeDef = TypedDict(
    "ListIndicesResponseTypeDef",
    {
        "indexNames": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPoliciesResponseTypeDef = TypedDict(
    "ListPoliciesResponseTypeDef",
    {
        "policies": List[PolicyTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPolicyPrincipalsResponseTypeDef = TypedDict(
    "ListPolicyPrincipalsResponseTypeDef",
    {
        "principals": List[str],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPrincipalPoliciesResponseTypeDef = TypedDict(
    "ListPrincipalPoliciesResponseTypeDef",
    {
        "policies": List[PolicyTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPrincipalThingsResponseTypeDef = TypedDict(
    "ListPrincipalThingsResponseTypeDef",
    {
        "things": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListRoleAliasesResponseTypeDef = TypedDict(
    "ListRoleAliasesResponseTypeDef",
    {
        "roleAliases": List[str],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTargetsForPolicyResponseTypeDef = TypedDict(
    "ListTargetsForPolicyResponseTypeDef",
    {
        "targets": List[str],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingPrincipalsResponseTypeDef = TypedDict(
    "ListThingPrincipalsResponseTypeDef",
    {
        "principals": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingRegistrationTaskReportsResponseTypeDef = TypedDict(
    "ListThingRegistrationTaskReportsResponseTypeDef",
    {
        "resourceLinks": List[str],
        "reportType": ReportTypeType,
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingRegistrationTasksResponseTypeDef = TypedDict(
    "ListThingRegistrationTasksResponseTypeDef",
    {
        "taskIds": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingsInBillingGroupResponseTypeDef = TypedDict(
    "ListThingsInBillingGroupResponseTypeDef",
    {
        "things": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingsInThingGroupResponseTypeDef = TypedDict(
    "ListThingsInThingGroupResponseTypeDef",
    {
        "things": List[str],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterCACertificateResponseTypeDef = TypedDict(
    "RegisterCACertificateResponseTypeDef",
    {
        "certificateArn": str,
        "certificateId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterCertificateResponseTypeDef = TypedDict(
    "RegisterCertificateResponseTypeDef",
    {
        "certificateArn": str,
        "certificateId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterCertificateWithoutCAResponseTypeDef = TypedDict(
    "RegisterCertificateWithoutCAResponseTypeDef",
    {
        "certificateArn": str,
        "certificateId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterThingResponseTypeDef = TypedDict(
    "RegisterThingResponseTypeDef",
    {
        "certificatePem": str,
        "resourceArns": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SetDefaultAuthorizerResponseTypeDef = TypedDict(
    "SetDefaultAuthorizerResponseTypeDef",
    {
        "authorizerName": str,
        "authorizerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartAuditMitigationActionsTaskResponseTypeDef = TypedDict(
    "StartAuditMitigationActionsTaskResponseTypeDef",
    {
        "taskId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDetectMitigationActionsTaskResponseTypeDef = TypedDict(
    "StartDetectMitigationActionsTaskResponseTypeDef",
    {
        "taskId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartOnDemandAuditTaskResponseTypeDef = TypedDict(
    "StartOnDemandAuditTaskResponseTypeDef",
    {
        "taskId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartThingRegistrationTaskResponseTypeDef = TypedDict(
    "StartThingRegistrationTaskResponseTypeDef",
    {
        "taskId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestInvokeAuthorizerResponseTypeDef = TypedDict(
    "TestInvokeAuthorizerResponseTypeDef",
    {
        "isAuthenticated": bool,
        "principalId": str,
        "policyDocuments": List[str],
        "refreshAfterInSeconds": int,
        "disconnectAfterInSeconds": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TransferCertificateResponseTypeDef = TypedDict(
    "TransferCertificateResponseTypeDef",
    {
        "transferredCertificateArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateAuthorizerResponseTypeDef = TypedDict(
    "UpdateAuthorizerResponseTypeDef",
    {
        "authorizerName": str,
        "authorizerArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBillingGroupResponseTypeDef = TypedDict(
    "UpdateBillingGroupResponseTypeDef",
    {
        "version": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCertificateProviderResponseTypeDef = TypedDict(
    "UpdateCertificateProviderResponseTypeDef",
    {
        "certificateProviderName": str,
        "certificateProviderArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateCustomMetricResponseTypeDef = TypedDict(
    "UpdateCustomMetricResponseTypeDef",
    {
        "metricName": str,
        "metricArn": str,
        "metricType": CustomMetricTypeType,
        "displayName": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDimensionResponseTypeDef = TypedDict(
    "UpdateDimensionResponseTypeDef",
    {
        "name": str,
        "arn": str,
        "type": Literal["TOPIC_FILTER"],
        "stringValues": List[str],
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDomainConfigurationResponseTypeDef = TypedDict(
    "UpdateDomainConfigurationResponseTypeDef",
    {
        "domainConfigurationName": str,
        "domainConfigurationArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateDynamicThingGroupResponseTypeDef = TypedDict(
    "UpdateDynamicThingGroupResponseTypeDef",
    {
        "version": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateMitigationActionResponseTypeDef = TypedDict(
    "UpdateMitigationActionResponseTypeDef",
    {
        "actionArn": str,
        "actionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateRoleAliasResponseTypeDef = TypedDict(
    "UpdateRoleAliasResponseTypeDef",
    {
        "roleAlias": str,
        "roleAliasArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateScheduledAuditResponseTypeDef = TypedDict(
    "UpdateScheduledAuditResponseTypeDef",
    {
        "scheduledAuditArn": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateStreamResponseTypeDef = TypedDict(
    "UpdateStreamResponseTypeDef",
    {
        "streamId": str,
        "streamArn": str,
        "description": str,
        "streamVersion": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateThingGroupResponseTypeDef = TypedDict(
    "UpdateThingGroupResponseTypeDef",
    {
        "version": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateThingRequestRequestTypeDef = TypedDict(
    "CreateThingRequestRequestTypeDef",
    {
        "thingName": str,
        "thingTypeName": NotRequired[str],
        "attributePayload": NotRequired[AttributePayloadTypeDef],
        "billingGroupName": NotRequired[str],
    },
)
ThingGroupPropertiesTypeDef = TypedDict(
    "ThingGroupPropertiesTypeDef",
    {
        "thingGroupDescription": NotRequired[str],
        "attributePayload": NotRequired[AttributePayloadTypeDef],
    },
)
UpdateThingRequestRequestTypeDef = TypedDict(
    "UpdateThingRequestRequestTypeDef",
    {
        "thingName": str,
        "thingTypeName": NotRequired[str],
        "attributePayload": NotRequired[AttributePayloadTypeDef],
        "expectedVersion": NotRequired[int],
        "removeThingType": NotRequired[bool],
    },
)
ListAuditMitigationActionsExecutionsResponseTypeDef = TypedDict(
    "ListAuditMitigationActionsExecutionsResponseTypeDef",
    {
        "actionsExecutions": List[AuditMitigationActionExecutionMetadataTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAuditMitigationActionsTasksResponseTypeDef = TypedDict(
    "ListAuditMitigationActionsTasksResponseTypeDef",
    {
        "tasks": List[AuditMitigationActionsTaskMetadataTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartAuditMitigationActionsTaskRequestRequestTypeDef = TypedDict(
    "StartAuditMitigationActionsTaskRequestRequestTypeDef",
    {
        "taskId": str,
        "target": AuditMitigationActionsTaskTargetTypeDef,
        "auditCheckToActionsMapping": Mapping[str, Sequence[str]],
        "clientRequestToken": str,
    },
)
DescribeAccountAuditConfigurationResponseTypeDef = TypedDict(
    "DescribeAccountAuditConfigurationResponseTypeDef",
    {
        "roleArn": str,
        "auditNotificationTargetConfigurations": Dict[
            Literal["SNS"], AuditNotificationTargetTypeDef
        ],
        "auditCheckConfigurations": Dict[str, AuditCheckConfigurationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateAccountAuditConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateAccountAuditConfigurationRequestRequestTypeDef",
    {
        "roleArn": NotRequired[str],
        "auditNotificationTargetConfigurations": NotRequired[
            Mapping[Literal["SNS"], AuditNotificationTargetTypeDef]
        ],
        "auditCheckConfigurations": NotRequired[Mapping[str, AuditCheckConfigurationTypeDef]],
    },
)
ListAuditTasksResponseTypeDef = TypedDict(
    "ListAuditTasksResponseTypeDef",
    {
        "tasks": List[AuditTaskMetadataTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestAuthorizationRequestRequestTypeDef = TypedDict(
    "TestAuthorizationRequestRequestTypeDef",
    {
        "authInfos": Sequence[AuthInfoTypeDef],
        "principal": NotRequired[str],
        "cognitoIdentityPoolId": NotRequired[str],
        "clientId": NotRequired[str],
        "policyNamesToAdd": NotRequired[Sequence[str]],
        "policyNamesToSkip": NotRequired[Sequence[str]],
    },
)
DescribeAuthorizerResponseTypeDef = TypedDict(
    "DescribeAuthorizerResponseTypeDef",
    {
        "authorizerDescription": AuthorizerDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDefaultAuthorizerResponseTypeDef = TypedDict(
    "DescribeDefaultAuthorizerResponseTypeDef",
    {
        "authorizerDescription": AuthorizerDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAuthorizersResponseTypeDef = TypedDict(
    "ListAuthorizersResponseTypeDef",
    {
        "authorizers": List[AuthorizerSummaryTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AwsJobAbortConfigTypeDef = TypedDict(
    "AwsJobAbortConfigTypeDef",
    {
        "abortCriteriaList": Sequence[AwsJobAbortCriteriaTypeDef],
    },
)
AwsJobExponentialRolloutRateTypeDef = TypedDict(
    "AwsJobExponentialRolloutRateTypeDef",
    {
        "baseRatePerMinute": int,
        "incrementFactor": float,
        "rateIncreaseCriteria": AwsJobRateIncreaseCriteriaTypeDef,
    },
)
BehaviorCriteriaPaginatorTypeDef = TypedDict(
    "BehaviorCriteriaPaginatorTypeDef",
    {
        "comparisonOperator": NotRequired[ComparisonOperatorType],
        "value": NotRequired[MetricValuePaginatorTypeDef],
        "durationSeconds": NotRequired[int],
        "consecutiveDatapointsToAlarm": NotRequired[int],
        "consecutiveDatapointsToClear": NotRequired[int],
        "statisticalThreshold": NotRequired[StatisticalThresholdTypeDef],
        "mlDetectionConfig": NotRequired[MachineLearningDetectionConfigTypeDef],
    },
)
BehaviorCriteriaTypeDef = TypedDict(
    "BehaviorCriteriaTypeDef",
    {
        "comparisonOperator": NotRequired[ComparisonOperatorType],
        "value": NotRequired[MetricValueTypeDef],
        "durationSeconds": NotRequired[int],
        "consecutiveDatapointsToAlarm": NotRequired[int],
        "consecutiveDatapointsToClear": NotRequired[int],
        "statisticalThreshold": NotRequired[StatisticalThresholdTypeDef],
        "mlDetectionConfig": NotRequired[MachineLearningDetectionConfigTypeDef],
    },
)
GetBehaviorModelTrainingSummariesResponseTypeDef = TypedDict(
    "GetBehaviorModelTrainingSummariesResponseTypeDef",
    {
        "summaries": List[BehaviorModelTrainingSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MetricToRetainTypeDef = TypedDict(
    "MetricToRetainTypeDef",
    {
        "metric": str,
        "metricDimension": NotRequired[MetricDimensionTypeDef],
        "exportMetric": NotRequired[bool],
    },
)
DescribeBillingGroupResponseTypeDef = TypedDict(
    "DescribeBillingGroupResponseTypeDef",
    {
        "billingGroupName": str,
        "billingGroupId": str,
        "billingGroupArn": str,
        "version": int,
        "billingGroupProperties": BillingGroupPropertiesTypeDef,
        "billingGroupMetadata": BillingGroupMetadataTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBillingGroupRequestRequestTypeDef = TypedDict(
    "UpdateBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": str,
        "billingGroupProperties": BillingGroupPropertiesTypeDef,
        "expectedVersion": NotRequired[int],
    },
)
CodeSigningSignatureTypeDef = TypedDict(
    "CodeSigningSignatureTypeDef",
    {
        "inlineDocument": NotRequired[BlobTypeDef],
    },
)
MqttContextTypeDef = TypedDict(
    "MqttContextTypeDef",
    {
        "username": NotRequired[str],
        "password": NotRequired[BlobTypeDef],
        "clientId": NotRequired[str],
    },
)
GetBucketsAggregationResponseTypeDef = TypedDict(
    "GetBucketsAggregationResponseTypeDef",
    {
        "totalCount": int,
        "buckets": List[BucketTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BucketsAggregationTypeTypeDef = TypedDict(
    "BucketsAggregationTypeTypeDef",
    {
        "termsAggregation": NotRequired[TermsAggregationTypeDef],
    },
)
CACertificateDescriptionTypeDef = TypedDict(
    "CACertificateDescriptionTypeDef",
    {
        "certificateArn": NotRequired[str],
        "certificateId": NotRequired[str],
        "status": NotRequired[CACertificateStatusType],
        "certificatePem": NotRequired[str],
        "ownedBy": NotRequired[str],
        "creationDate": NotRequired[datetime],
        "autoRegistrationStatus": NotRequired[AutoRegistrationStatusType],
        "lastModifiedDate": NotRequired[datetime],
        "customerVersion": NotRequired[int],
        "generationId": NotRequired[str],
        "validity": NotRequired[CertificateValidityTypeDef],
        "certificateMode": NotRequired[CertificateModeType],
    },
)
ListCACertificatesResponseTypeDef = TypedDict(
    "ListCACertificatesResponseTypeDef",
    {
        "certificates": List[CACertificateTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CertificateDescriptionTypeDef = TypedDict(
    "CertificateDescriptionTypeDef",
    {
        "certificateArn": NotRequired[str],
        "certificateId": NotRequired[str],
        "caCertificateId": NotRequired[str],
        "status": NotRequired[CertificateStatusType],
        "certificatePem": NotRequired[str],
        "ownedBy": NotRequired[str],
        "previousOwnedBy": NotRequired[str],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
        "customerVersion": NotRequired[int],
        "transferData": NotRequired[TransferDataTypeDef],
        "generationId": NotRequired[str],
        "validity": NotRequired[CertificateValidityTypeDef],
        "certificateMode": NotRequired[CertificateModeType],
    },
)
ListCertificateProvidersResponseTypeDef = TypedDict(
    "ListCertificateProvidersResponseTypeDef",
    {
        "certificateProviders": List[CertificateProviderSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCertificatesByCAResponseTypeDef = TypedDict(
    "ListCertificatesByCAResponseTypeDef",
    {
        "certificates": List[CertificateTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCertificatesResponseTypeDef = TypedDict(
    "ListCertificatesResponseTypeDef",
    {
        "certificates": List[CertificateTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeEventConfigurationsResponseTypeDef = TypedDict(
    "DescribeEventConfigurationsResponseTypeDef",
    {
        "eventConfigurations": Dict[EventTypeType, ConfigurationTypeDef],
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEventConfigurationsRequestRequestTypeDef = TypedDict(
    "UpdateEventConfigurationsRequestRequestTypeDef",
    {
        "eventConfigurations": NotRequired[Mapping[EventTypeType, ConfigurationTypeDef]],
    },
)
ListAuditMitigationActionsTasksRequestRequestTypeDef = TypedDict(
    "ListAuditMitigationActionsTasksRequestRequestTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "auditTaskId": NotRequired[str],
        "findingId": NotRequired[str],
        "taskStatus": NotRequired[AuditMitigationActionsTaskStatusType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListAuditTasksRequestRequestTypeDef = TypedDict(
    "ListAuditTasksRequestRequestTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "taskType": NotRequired[AuditTaskTypeType],
        "taskStatus": NotRequired[AuditTaskStatusType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListDetectMitigationActionsExecutionsRequestRequestTypeDef = TypedDict(
    "ListDetectMitigationActionsExecutionsRequestRequestTypeDef",
    {
        "taskId": NotRequired[str],
        "violationId": NotRequired[str],
        "thingName": NotRequired[str],
        "startTime": NotRequired[TimestampTypeDef],
        "endTime": NotRequired[TimestampTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListDetectMitigationActionsTasksRequestRequestTypeDef = TypedDict(
    "ListDetectMitigationActionsTasksRequestRequestTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListMetricValuesRequestRequestTypeDef = TypedDict(
    "ListMetricValuesRequestRequestTypeDef",
    {
        "thingName": str,
        "metricName": str,
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "dimensionName": NotRequired[str],
        "dimensionValueOperator": NotRequired[DimensionValueOperatorType],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListViolationEventsRequestRequestTypeDef = TypedDict(
    "ListViolationEventsRequestRequestTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behaviorCriteriaType": NotRequired[BehaviorCriteriaTypeType],
        "listSuppressedAlerts": NotRequired[bool],
        "verificationState": NotRequired[VerificationStateType],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
CreateAuthorizerRequestRequestTypeDef = TypedDict(
    "CreateAuthorizerRequestRequestTypeDef",
    {
        "authorizerName": str,
        "authorizerFunctionArn": str,
        "tokenKeyName": NotRequired[str],
        "tokenSigningPublicKeys": NotRequired[Mapping[str, str]],
        "status": NotRequired[AuthorizerStatusType],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "signingDisabled": NotRequired[bool],
        "enableCachingForHttp": NotRequired[bool],
    },
)
CreateBillingGroupRequestRequestTypeDef = TypedDict(
    "CreateBillingGroupRequestRequestTypeDef",
    {
        "billingGroupName": str,
        "billingGroupProperties": NotRequired[BillingGroupPropertiesTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateCertificateProviderRequestRequestTypeDef = TypedDict(
    "CreateCertificateProviderRequestRequestTypeDef",
    {
        "certificateProviderName": str,
        "lambdaFunctionArn": str,
        "accountDefaultForOperations": Sequence[Literal["CreateCertificateFromCsr"]],
        "clientToken": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateCustomMetricRequestRequestTypeDef = TypedDict(
    "CreateCustomMetricRequestRequestTypeDef",
    {
        "metricName": str,
        "metricType": CustomMetricTypeType,
        "clientRequestToken": str,
        "displayName": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateDimensionRequestRequestTypeDef = TypedDict(
    "CreateDimensionRequestRequestTypeDef",
    {
        "name": str,
        "type": Literal["TOPIC_FILTER"],
        "stringValues": Sequence[str],
        "clientRequestToken": str,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateFleetMetricRequestRequestTypeDef = TypedDict(
    "CreateFleetMetricRequestRequestTypeDef",
    {
        "metricName": str,
        "queryString": str,
        "aggregationType": AggregationTypeTypeDef,
        "period": int,
        "aggregationField": str,
        "description": NotRequired[str],
        "queryVersion": NotRequired[str],
        "indexName": NotRequired[str],
        "unit": NotRequired[FleetMetricUnitType],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreatePolicyRequestRequestTypeDef = TypedDict(
    "CreatePolicyRequestRequestTypeDef",
    {
        "policyName": str,
        "policyDocument": str,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateRoleAliasRequestRequestTypeDef = TypedDict(
    "CreateRoleAliasRequestRequestTypeDef",
    {
        "roleAlias": str,
        "roleArn": str,
        "credentialDurationSeconds": NotRequired[int],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateScheduledAuditRequestRequestTypeDef = TypedDict(
    "CreateScheduledAuditRequestRequestTypeDef",
    {
        "frequency": AuditFrequencyType,
        "targetCheckNames": Sequence[str],
        "scheduledAuditName": str,
        "dayOfMonth": NotRequired[str],
        "dayOfWeek": NotRequired[DayOfWeekType],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "tags": List[TagTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Sequence[TagTypeDef],
    },
)
CreateDomainConfigurationRequestRequestTypeDef = TypedDict(
    "CreateDomainConfigurationRequestRequestTypeDef",
    {
        "domainConfigurationName": str,
        "domainName": NotRequired[str],
        "serverCertificateArns": NotRequired[Sequence[str]],
        "validationCertificateArn": NotRequired[str],
        "authorizerConfig": NotRequired[AuthorizerConfigTypeDef],
        "serviceType": NotRequired[ServiceTypeType],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "tlsConfig": NotRequired[TlsConfigTypeDef],
        "serverCertificateConfig": NotRequired[ServerCertificateConfigTypeDef],
    },
)
UpdateDomainConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateDomainConfigurationRequestRequestTypeDef",
    {
        "domainConfigurationName": str,
        "authorizerConfig": NotRequired[AuthorizerConfigTypeDef],
        "domainConfigurationStatus": NotRequired[DomainConfigurationStatusType],
        "removeAuthorizerConfig": NotRequired[bool],
        "tlsConfig": NotRequired[TlsConfigTypeDef],
        "serverCertificateConfig": NotRequired[ServerCertificateConfigTypeDef],
    },
)
SchedulingConfigTypeDef = TypedDict(
    "SchedulingConfigTypeDef",
    {
        "startTime": NotRequired[str],
        "endTime": NotRequired[str],
        "endBehavior": NotRequired[JobEndBehaviorType],
        "maintenanceWindows": NotRequired[Sequence[MaintenanceWindowTypeDef]],
    },
)
CreateKeysAndCertificateResponseTypeDef = TypedDict(
    "CreateKeysAndCertificateResponseTypeDef",
    {
        "certificateArn": str,
        "certificateId": str,
        "certificatePem": str,
        "keyPair": KeyPairTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProvisioningClaimResponseTypeDef = TypedDict(
    "CreateProvisioningClaimResponseTypeDef",
    {
        "certificateId": str,
        "certificatePem": str,
        "keyPair": KeyPairTypeDef,
        "expiration": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateProvisioningTemplateRequestRequestTypeDef = TypedDict(
    "CreateProvisioningTemplateRequestRequestTypeDef",
    {
        "templateName": str,
        "templateBody": str,
        "provisioningRoleArn": str,
        "description": NotRequired[str],
        "enabled": NotRequired[bool],
        "preProvisioningHook": NotRequired[ProvisioningHookTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "type": NotRequired[TemplateTypeType],
    },
)
DescribeProvisioningTemplateResponseTypeDef = TypedDict(
    "DescribeProvisioningTemplateResponseTypeDef",
    {
        "templateArn": str,
        "templateName": str,
        "description": str,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "defaultVersionId": int,
        "templateBody": str,
        "enabled": bool,
        "provisioningRoleArn": str,
        "preProvisioningHook": ProvisioningHookTypeDef,
        "type": TemplateTypeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateProvisioningTemplateRequestRequestTypeDef = TypedDict(
    "UpdateProvisioningTemplateRequestRequestTypeDef",
    {
        "templateName": str,
        "description": NotRequired[str],
        "enabled": NotRequired[bool],
        "defaultVersionId": NotRequired[int],
        "provisioningRoleArn": NotRequired[str],
        "preProvisioningHook": NotRequired[ProvisioningHookTypeDef],
        "removePreProvisioningHook": NotRequired[bool],
    },
)
CreateThingTypeRequestRequestTypeDef = TypedDict(
    "CreateThingTypeRequestRequestTypeDef",
    {
        "thingTypeName": str,
        "thingTypeProperties": NotRequired[ThingTypePropertiesTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeAuditTaskResponseTypeDef = TypedDict(
    "DescribeAuditTaskResponseTypeDef",
    {
        "taskStatus": AuditTaskStatusType,
        "taskType": AuditTaskTypeType,
        "taskStartTime": datetime,
        "taskStatistics": TaskStatisticsTypeDef,
        "scheduledAuditName": str,
        "auditDetails": Dict[str, AuditCheckDetailsTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RegisterCACertificateRequestRequestTypeDef = TypedDict(
    "RegisterCACertificateRequestRequestTypeDef",
    {
        "caCertificate": str,
        "verificationCertificate": NotRequired[str],
        "setAsActive": NotRequired[bool],
        "allowAutoRegistration": NotRequired[bool],
        "registrationConfig": NotRequired[RegistrationConfigTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "certificateMode": NotRequired[CertificateModeType],
    },
)
UpdateCACertificateRequestRequestTypeDef = TypedDict(
    "UpdateCACertificateRequestRequestTypeDef",
    {
        "certificateId": str,
        "newStatus": NotRequired[CACertificateStatusType],
        "newAutoRegistrationStatus": NotRequired[AutoRegistrationStatusType],
        "registrationConfig": NotRequired[RegistrationConfigTypeDef],
        "removeAutoRegistration": NotRequired[bool],
    },
)
DescribeDomainConfigurationResponseTypeDef = TypedDict(
    "DescribeDomainConfigurationResponseTypeDef",
    {
        "domainConfigurationName": str,
        "domainConfigurationArn": str,
        "domainName": str,
        "serverCertificates": List[ServerCertificateSummaryTypeDef],
        "authorizerConfig": AuthorizerConfigTypeDef,
        "domainConfigurationStatus": DomainConfigurationStatusType,
        "serviceType": ServiceTypeType,
        "domainType": DomainTypeType,
        "lastStatusChangeDate": datetime,
        "tlsConfig": TlsConfigTypeDef,
        "serverCertificateConfig": ServerCertificateConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeManagedJobTemplateResponseTypeDef = TypedDict(
    "DescribeManagedJobTemplateResponseTypeDef",
    {
        "templateName": str,
        "templateArn": str,
        "description": str,
        "templateVersion": str,
        "environments": List[str],
        "documentParameters": List[DocumentParameterTypeDef],
        "document": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeRoleAliasResponseTypeDef = TypedDict(
    "DescribeRoleAliasResponseTypeDef",
    {
        "roleAliasDescription": RoleAliasDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeThingTypeResponseTypeDef = TypedDict(
    "DescribeThingTypeResponseTypeDef",
    {
        "thingTypeName": str,
        "thingTypeId": str,
        "thingTypeArn": str,
        "thingTypeProperties": ThingTypePropertiesTypeDef,
        "thingTypeMetadata": ThingTypeMetadataTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ThingTypeDefinitionTypeDef = TypedDict(
    "ThingTypeDefinitionTypeDef",
    {
        "thingTypeName": NotRequired[str],
        "thingTypeArn": NotRequired[str],
        "thingTypeProperties": NotRequired[ThingTypePropertiesTypeDef],
        "thingTypeMetadata": NotRequired[ThingTypeMetadataTypeDef],
    },
)
DestinationTypeDef = TypedDict(
    "DestinationTypeDef",
    {
        "s3Destination": NotRequired[S3DestinationTypeDef],
    },
)
ListDetectMitigationActionsExecutionsResponseTypeDef = TypedDict(
    "ListDetectMitigationActionsExecutionsResponseTypeDef",
    {
        "actionsExecutions": List[DetectMitigationActionExecutionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartDetectMitigationActionsTaskRequestRequestTypeDef = TypedDict(
    "StartDetectMitigationActionsTaskRequestRequestTypeDef",
    {
        "taskId": str,
        "target": DetectMitigationActionsTaskTargetTypeDef,
        "actions": Sequence[str],
        "clientRequestToken": str,
        "violationEventOccurrenceRange": NotRequired[ViolationEventOccurrenceRangeTypeDef],
        "includeOnlyActiveViolations": NotRequired[bool],
        "includeSuppressedAlerts": NotRequired[bool],
    },
)
ListDomainConfigurationsResponseTypeDef = TypedDict(
    "ListDomainConfigurationsResponseTypeDef",
    {
        "domainConfigurations": List[DomainConfigurationSummaryTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DynamoDBv2ActionTypeDef = TypedDict(
    "DynamoDBv2ActionTypeDef",
    {
        "roleArn": str,
        "putItem": PutItemInputTypeDef,
    },
)
GetEffectivePoliciesResponseTypeDef = TypedDict(
    "GetEffectivePoliciesResponseTypeDef",
    {
        "effectivePolicies": List[EffectivePolicyTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExponentialRolloutRateTypeDef = TypedDict(
    "ExponentialRolloutRateTypeDef",
    {
        "baseRatePerMinute": int,
        "incrementFactor": float,
        "rateIncreaseCriteria": RateIncreaseCriteriaTypeDef,
    },
)
ThingGroupIndexingConfigurationTypeDef = TypedDict(
    "ThingGroupIndexingConfigurationTypeDef",
    {
        "thingGroupIndexingMode": ThingGroupIndexingModeType,
        "managedFields": NotRequired[List[FieldTypeDef]],
        "customFields": NotRequired[List[FieldTypeDef]],
    },
)
StreamFileTypeDef = TypedDict(
    "StreamFileTypeDef",
    {
        "fileId": NotRequired[int],
        "s3Location": NotRequired[S3LocationTypeDef],
    },
)
FileLocationTypeDef = TypedDict(
    "FileLocationTypeDef",
    {
        "stream": NotRequired[StreamTypeDef],
        "s3Location": NotRequired[S3LocationTypeDef],
    },
)
ListFleetMetricsResponseTypeDef = TypedDict(
    "ListFleetMetricsResponseTypeDef",
    {
        "fleetMetrics": List[FleetMetricNameAndArnTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IndexingFilterTypeDef = TypedDict(
    "IndexingFilterTypeDef",
    {
        "namedShadowNames": NotRequired[List[str]],
        "geoLocations": NotRequired[List[GeoLocationTargetTypeDef]],
    },
)
GetBehaviorModelTrainingSummariesRequestGetBehaviorModelTrainingSummariesPaginateTypeDef = (
    TypedDict(
        "GetBehaviorModelTrainingSummariesRequestGetBehaviorModelTrainingSummariesPaginateTypeDef",
        {
            "securityProfileName": NotRequired[str],
            "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
        },
    )
)
ListActiveViolationsRequestListActiveViolationsPaginateTypeDef = TypedDict(
    "ListActiveViolationsRequestListActiveViolationsPaginateTypeDef",
    {
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behaviorCriteriaType": NotRequired[BehaviorCriteriaTypeType],
        "listSuppressedAlerts": NotRequired[bool],
        "verificationState": NotRequired[VerificationStateType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAttachedPoliciesRequestListAttachedPoliciesPaginateTypeDef = TypedDict(
    "ListAttachedPoliciesRequestListAttachedPoliciesPaginateTypeDef",
    {
        "target": str,
        "recursive": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuditMitigationActionsExecutionsRequestListAuditMitigationActionsExecutionsPaginateTypeDef = TypedDict(
    "ListAuditMitigationActionsExecutionsRequestListAuditMitigationActionsExecutionsPaginateTypeDef",
    {
        "taskId": str,
        "findingId": str,
        "actionStatus": NotRequired[AuditMitigationActionsExecutionStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuditMitigationActionsTasksRequestListAuditMitigationActionsTasksPaginateTypeDef = TypedDict(
    "ListAuditMitigationActionsTasksRequestListAuditMitigationActionsTasksPaginateTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "auditTaskId": NotRequired[str],
        "findingId": NotRequired[str],
        "taskStatus": NotRequired[AuditMitigationActionsTaskStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuditTasksRequestListAuditTasksPaginateTypeDef = TypedDict(
    "ListAuditTasksRequestListAuditTasksPaginateTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "taskType": NotRequired[AuditTaskTypeType],
        "taskStatus": NotRequired[AuditTaskStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuthorizersRequestListAuthorizersPaginateTypeDef = TypedDict(
    "ListAuthorizersRequestListAuthorizersPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "status": NotRequired[AuthorizerStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListBillingGroupsRequestListBillingGroupsPaginateTypeDef = TypedDict(
    "ListBillingGroupsRequestListBillingGroupsPaginateTypeDef",
    {
        "namePrefixFilter": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCACertificatesRequestListCACertificatesPaginateTypeDef = TypedDict(
    "ListCACertificatesRequestListCACertificatesPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "templateName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCertificatesByCARequestListCertificatesByCAPaginateTypeDef = TypedDict(
    "ListCertificatesByCARequestListCertificatesByCAPaginateTypeDef",
    {
        "caCertificateId": str,
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCertificatesRequestListCertificatesPaginateTypeDef = TypedDict(
    "ListCertificatesRequestListCertificatesPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListCustomMetricsRequestListCustomMetricsPaginateTypeDef = TypedDict(
    "ListCustomMetricsRequestListCustomMetricsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDetectMitigationActionsExecutionsRequestListDetectMitigationActionsExecutionsPaginateTypeDef = TypedDict(
    "ListDetectMitigationActionsExecutionsRequestListDetectMitigationActionsExecutionsPaginateTypeDef",
    {
        "taskId": NotRequired[str],
        "violationId": NotRequired[str],
        "thingName": NotRequired[str],
        "startTime": NotRequired[TimestampTypeDef],
        "endTime": NotRequired[TimestampTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDetectMitigationActionsTasksRequestListDetectMitigationActionsTasksPaginateTypeDef = TypedDict(
    "ListDetectMitigationActionsTasksRequestListDetectMitigationActionsTasksPaginateTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDimensionsRequestListDimensionsPaginateTypeDef = TypedDict(
    "ListDimensionsRequestListDimensionsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListDomainConfigurationsRequestListDomainConfigurationsPaginateTypeDef = TypedDict(
    "ListDomainConfigurationsRequestListDomainConfigurationsPaginateTypeDef",
    {
        "serviceType": NotRequired[ServiceTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListFleetMetricsRequestListFleetMetricsPaginateTypeDef = TypedDict(
    "ListFleetMetricsRequestListFleetMetricsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListIndicesRequestListIndicesPaginateTypeDef = TypedDict(
    "ListIndicesRequestListIndicesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobExecutionsForJobRequestListJobExecutionsForJobPaginateTypeDef = TypedDict(
    "ListJobExecutionsForJobRequestListJobExecutionsForJobPaginateTypeDef",
    {
        "jobId": str,
        "status": NotRequired[JobExecutionStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobExecutionsForThingRequestListJobExecutionsForThingPaginateTypeDef = TypedDict(
    "ListJobExecutionsForThingRequestListJobExecutionsForThingPaginateTypeDef",
    {
        "thingName": str,
        "status": NotRequired[JobExecutionStatusType],
        "namespaceId": NotRequired[str],
        "jobId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobTemplatesRequestListJobTemplatesPaginateTypeDef = TypedDict(
    "ListJobTemplatesRequestListJobTemplatesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListJobsRequestListJobsPaginateTypeDef = TypedDict(
    "ListJobsRequestListJobsPaginateTypeDef",
    {
        "status": NotRequired[JobStatusType],
        "targetSelection": NotRequired[TargetSelectionType],
        "thingGroupName": NotRequired[str],
        "thingGroupId": NotRequired[str],
        "namespaceId": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListManagedJobTemplatesRequestListManagedJobTemplatesPaginateTypeDef = TypedDict(
    "ListManagedJobTemplatesRequestListManagedJobTemplatesPaginateTypeDef",
    {
        "templateName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMetricValuesRequestListMetricValuesPaginateTypeDef = TypedDict(
    "ListMetricValuesRequestListMetricValuesPaginateTypeDef",
    {
        "thingName": str,
        "metricName": str,
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "dimensionName": NotRequired[str],
        "dimensionValueOperator": NotRequired[DimensionValueOperatorType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListMitigationActionsRequestListMitigationActionsPaginateTypeDef = TypedDict(
    "ListMitigationActionsRequestListMitigationActionsPaginateTypeDef",
    {
        "actionType": NotRequired[MitigationActionTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListOTAUpdatesRequestListOTAUpdatesPaginateTypeDef = TypedDict(
    "ListOTAUpdatesRequestListOTAUpdatesPaginateTypeDef",
    {
        "otaUpdateStatus": NotRequired[OTAUpdateStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListOutgoingCertificatesRequestListOutgoingCertificatesPaginateTypeDef = TypedDict(
    "ListOutgoingCertificatesRequestListOutgoingCertificatesPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPackageVersionsRequestListPackageVersionsPaginateTypeDef = TypedDict(
    "ListPackageVersionsRequestListPackageVersionsPaginateTypeDef",
    {
        "packageName": str,
        "status": NotRequired[PackageVersionStatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPackagesRequestListPackagesPaginateTypeDef = TypedDict(
    "ListPackagesRequestListPackagesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPoliciesRequestListPoliciesPaginateTypeDef = TypedDict(
    "ListPoliciesRequestListPoliciesPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPolicyPrincipalsRequestListPolicyPrincipalsPaginateTypeDef = TypedDict(
    "ListPolicyPrincipalsRequestListPolicyPrincipalsPaginateTypeDef",
    {
        "policyName": str,
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPrincipalPoliciesRequestListPrincipalPoliciesPaginateTypeDef = TypedDict(
    "ListPrincipalPoliciesRequestListPrincipalPoliciesPaginateTypeDef",
    {
        "principal": str,
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPrincipalThingsRequestListPrincipalThingsPaginateTypeDef = TypedDict(
    "ListPrincipalThingsRequestListPrincipalThingsPaginateTypeDef",
    {
        "principal": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListProvisioningTemplateVersionsRequestListProvisioningTemplateVersionsPaginateTypeDef = TypedDict(
    "ListProvisioningTemplateVersionsRequestListProvisioningTemplateVersionsPaginateTypeDef",
    {
        "templateName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListProvisioningTemplatesRequestListProvisioningTemplatesPaginateTypeDef = TypedDict(
    "ListProvisioningTemplatesRequestListProvisioningTemplatesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRelatedResourcesForAuditFindingRequestListRelatedResourcesForAuditFindingPaginateTypeDef = TypedDict(
    "ListRelatedResourcesForAuditFindingRequestListRelatedResourcesForAuditFindingPaginateTypeDef",
    {
        "findingId": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRoleAliasesRequestListRoleAliasesPaginateTypeDef = TypedDict(
    "ListRoleAliasesRequestListRoleAliasesPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListScheduledAuditsRequestListScheduledAuditsPaginateTypeDef = TypedDict(
    "ListScheduledAuditsRequestListScheduledAuditsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSecurityProfilesForTargetRequestListSecurityProfilesForTargetPaginateTypeDef = TypedDict(
    "ListSecurityProfilesForTargetRequestListSecurityProfilesForTargetPaginateTypeDef",
    {
        "securityProfileTargetArn": str,
        "recursive": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef = TypedDict(
    "ListSecurityProfilesRequestListSecurityProfilesPaginateTypeDef",
    {
        "dimensionName": NotRequired[str],
        "metricName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListStreamsRequestListStreamsPaginateTypeDef = TypedDict(
    "ListStreamsRequestListStreamsPaginateTypeDef",
    {
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTagsForResourceRequestListTagsForResourcePaginateTypeDef = TypedDict(
    "ListTagsForResourceRequestListTagsForResourcePaginateTypeDef",
    {
        "resourceArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTargetsForPolicyRequestListTargetsForPolicyPaginateTypeDef = TypedDict(
    "ListTargetsForPolicyRequestListTargetsForPolicyPaginateTypeDef",
    {
        "policyName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTargetsForSecurityProfileRequestListTargetsForSecurityProfilePaginateTypeDef = TypedDict(
    "ListTargetsForSecurityProfileRequestListTargetsForSecurityProfilePaginateTypeDef",
    {
        "securityProfileName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingGroupsForThingRequestListThingGroupsForThingPaginateTypeDef = TypedDict(
    "ListThingGroupsForThingRequestListThingGroupsForThingPaginateTypeDef",
    {
        "thingName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingGroupsRequestListThingGroupsPaginateTypeDef = TypedDict(
    "ListThingGroupsRequestListThingGroupsPaginateTypeDef",
    {
        "parentGroup": NotRequired[str],
        "namePrefixFilter": NotRequired[str],
        "recursive": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingPrincipalsRequestListThingPrincipalsPaginateTypeDef = TypedDict(
    "ListThingPrincipalsRequestListThingPrincipalsPaginateTypeDef",
    {
        "thingName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingRegistrationTaskReportsRequestListThingRegistrationTaskReportsPaginateTypeDef = TypedDict(
    "ListThingRegistrationTaskReportsRequestListThingRegistrationTaskReportsPaginateTypeDef",
    {
        "taskId": str,
        "reportType": ReportTypeType,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingRegistrationTasksRequestListThingRegistrationTasksPaginateTypeDef = TypedDict(
    "ListThingRegistrationTasksRequestListThingRegistrationTasksPaginateTypeDef",
    {
        "status": NotRequired[StatusType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingTypesRequestListThingTypesPaginateTypeDef = TypedDict(
    "ListThingTypesRequestListThingTypesPaginateTypeDef",
    {
        "thingTypeName": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingsInBillingGroupRequestListThingsInBillingGroupPaginateTypeDef = TypedDict(
    "ListThingsInBillingGroupRequestListThingsInBillingGroupPaginateTypeDef",
    {
        "billingGroupName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingsInThingGroupRequestListThingsInThingGroupPaginateTypeDef = TypedDict(
    "ListThingsInThingGroupRequestListThingsInThingGroupPaginateTypeDef",
    {
        "thingGroupName": str,
        "recursive": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListThingsRequestListThingsPaginateTypeDef = TypedDict(
    "ListThingsRequestListThingsPaginateTypeDef",
    {
        "attributeName": NotRequired[str],
        "attributeValue": NotRequired[str],
        "thingTypeName": NotRequired[str],
        "usePrefixAttributeValue": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTopicRuleDestinationsRequestListTopicRuleDestinationsPaginateTypeDef = TypedDict(
    "ListTopicRuleDestinationsRequestListTopicRuleDestinationsPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTopicRulesRequestListTopicRulesPaginateTypeDef = TypedDict(
    "ListTopicRulesRequestListTopicRulesPaginateTypeDef",
    {
        "topic": NotRequired[str],
        "ruleDisabled": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListV2LoggingLevelsRequestListV2LoggingLevelsPaginateTypeDef = TypedDict(
    "ListV2LoggingLevelsRequestListV2LoggingLevelsPaginateTypeDef",
    {
        "targetType": NotRequired[LogTargetTypeType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListViolationEventsRequestListViolationEventsPaginateTypeDef = TypedDict(
    "ListViolationEventsRequestListViolationEventsPaginateTypeDef",
    {
        "startTime": TimestampTypeDef,
        "endTime": TimestampTypeDef,
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behaviorCriteriaType": NotRequired[BehaviorCriteriaTypeType],
        "listSuppressedAlerts": NotRequired[bool],
        "verificationState": NotRequired[VerificationStateType],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetPackageConfigurationResponseTypeDef = TypedDict(
    "GetPackageConfigurationResponseTypeDef",
    {
        "versionUpdateByJobsConfig": VersionUpdateByJobsConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePackageConfigurationRequestRequestTypeDef = TypedDict(
    "UpdatePackageConfigurationRequestRequestTypeDef",
    {
        "versionUpdateByJobsConfig": NotRequired[VersionUpdateByJobsConfigTypeDef],
        "clientToken": NotRequired[str],
    },
)
GetPercentilesResponseTypeDef = TypedDict(
    "GetPercentilesResponseTypeDef",
    {
        "percentiles": List[PercentPairTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetStatisticsResponseTypeDef = TypedDict(
    "GetStatisticsResponseTypeDef",
    {
        "statistics": StatisticsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBillingGroupsResponseTypeDef = TypedDict(
    "ListBillingGroupsResponseTypeDef",
    {
        "billingGroups": List[GroupNameAndArnTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingGroupsForThingResponseTypeDef = TypedDict(
    "ListThingGroupsForThingResponseTypeDef",
    {
        "thingGroups": List[GroupNameAndArnTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingGroupsResponseTypeDef = TypedDict(
    "ListThingGroupsResponseTypeDef",
    {
        "thingGroups": List[GroupNameAndArnTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ThingGroupMetadataTypeDef = TypedDict(
    "ThingGroupMetadataTypeDef",
    {
        "parentGroupName": NotRequired[str],
        "rootToParentThingGroups": NotRequired[List[GroupNameAndArnTypeDef]],
        "creationDate": NotRequired[datetime],
    },
)
HttpAuthorizationTypeDef = TypedDict(
    "HttpAuthorizationTypeDef",
    {
        "sigv4": NotRequired[SigV4AuthorizationTypeDef],
    },
)
JobExecutionTypeDef = TypedDict(
    "JobExecutionTypeDef",
    {
        "jobId": NotRequired[str],
        "status": NotRequired[JobExecutionStatusType],
        "forceCanceled": NotRequired[bool],
        "statusDetails": NotRequired[JobExecutionStatusDetailsTypeDef],
        "thingArn": NotRequired[str],
        "queuedAt": NotRequired[datetime],
        "startedAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "executionNumber": NotRequired[int],
        "versionNumber": NotRequired[int],
        "approximateSecondsBeforeTimedOut": NotRequired[int],
    },
)
JobExecutionSummaryForJobTypeDef = TypedDict(
    "JobExecutionSummaryForJobTypeDef",
    {
        "thingArn": NotRequired[str],
        "jobExecutionSummary": NotRequired[JobExecutionSummaryTypeDef],
    },
)
JobExecutionSummaryForThingTypeDef = TypedDict(
    "JobExecutionSummaryForThingTypeDef",
    {
        "jobId": NotRequired[str],
        "jobExecutionSummary": NotRequired[JobExecutionSummaryTypeDef],
    },
)
JobExecutionsRetryConfigTypeDef = TypedDict(
    "JobExecutionsRetryConfigTypeDef",
    {
        "criteriaList": Sequence[RetryCriteriaTypeDef],
    },
)
ListJobsResponseTypeDef = TypedDict(
    "ListJobsResponseTypeDef",
    {
        "jobs": List[JobSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListJobTemplatesResponseTypeDef = TypedDict(
    "ListJobTemplatesResponseTypeDef",
    {
        "jobTemplates": List[JobTemplateSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
KafkaActionTypeDef = TypedDict(
    "KafkaActionTypeDef",
    {
        "destinationArn": str,
        "topic": str,
        "clientProperties": Mapping[str, str],
        "key": NotRequired[str],
        "partition": NotRequired[str],
        "headers": NotRequired[Sequence[KafkaActionHeaderTypeDef]],
    },
)
ListManagedJobTemplatesResponseTypeDef = TypedDict(
    "ListManagedJobTemplatesResponseTypeDef",
    {
        "managedJobTemplates": List[ManagedJobTemplateSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMitigationActionsResponseTypeDef = TypedDict(
    "ListMitigationActionsResponseTypeDef",
    {
        "actionIdentifiers": List[MitigationActionIdentifierTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListOTAUpdatesResponseTypeDef = TypedDict(
    "ListOTAUpdatesResponseTypeDef",
    {
        "otaUpdates": List[OTAUpdateSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListOutgoingCertificatesResponseTypeDef = TypedDict(
    "ListOutgoingCertificatesResponseTypeDef",
    {
        "outgoingCertificates": List[OutgoingCertificateTypeDef],
        "nextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPackageVersionsResponseTypeDef = TypedDict(
    "ListPackageVersionsResponseTypeDef",
    {
        "packageVersionSummaries": List[PackageVersionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPackagesResponseTypeDef = TypedDict(
    "ListPackagesResponseTypeDef",
    {
        "packageSummaries": List[PackageSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListPolicyVersionsResponseTypeDef = TypedDict(
    "ListPolicyVersionsResponseTypeDef",
    {
        "policyVersions": List[PolicyVersionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListProvisioningTemplateVersionsResponseTypeDef = TypedDict(
    "ListProvisioningTemplateVersionsResponseTypeDef",
    {
        "versions": List[ProvisioningTemplateVersionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListProvisioningTemplatesResponseTypeDef = TypedDict(
    "ListProvisioningTemplatesResponseTypeDef",
    {
        "templates": List[ProvisioningTemplateSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListScheduledAuditsResponseTypeDef = TypedDict(
    "ListScheduledAuditsResponseTypeDef",
    {
        "scheduledAudits": List[ScheduledAuditMetadataTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSecurityProfilesResponseTypeDef = TypedDict(
    "ListSecurityProfilesResponseTypeDef",
    {
        "securityProfileIdentifiers": List[SecurityProfileIdentifierTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListStreamsResponseTypeDef = TypedDict(
    "ListStreamsResponseTypeDef",
    {
        "streams": List[StreamSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTargetsForSecurityProfileResponseTypeDef = TypedDict(
    "ListTargetsForSecurityProfileResponseTypeDef",
    {
        "securityProfileTargets": List[SecurityProfileTargetTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SecurityProfileTargetMappingTypeDef = TypedDict(
    "SecurityProfileTargetMappingTypeDef",
    {
        "securityProfileIdentifier": NotRequired[SecurityProfileIdentifierTypeDef],
        "target": NotRequired[SecurityProfileTargetTypeDef],
    },
)
ListThingsResponseTypeDef = TypedDict(
    "ListThingsResponseTypeDef",
    {
        "things": List[ThingAttributeTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTopicRulesResponseTypeDef = TypedDict(
    "ListTopicRulesResponseTypeDef",
    {
        "rules": List[TopicRuleListItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
LocationActionTypeDef = TypedDict(
    "LocationActionTypeDef",
    {
        "roleArn": str,
        "trackerName": str,
        "deviceId": str,
        "latitude": str,
        "longitude": str,
        "timestamp": NotRequired[LocationTimestampTypeDef],
    },
)
LogTargetConfigurationTypeDef = TypedDict(
    "LogTargetConfigurationTypeDef",
    {
        "logTarget": NotRequired[LogTargetTypeDef],
        "logLevel": NotRequired[LogLevelType],
    },
)
SetV2LoggingLevelRequestRequestTypeDef = TypedDict(
    "SetV2LoggingLevelRequestRequestTypeDef",
    {
        "logTarget": LogTargetTypeDef,
        "logLevel": LogLevelType,
    },
)
SetLoggingOptionsRequestRequestTypeDef = TypedDict(
    "SetLoggingOptionsRequestRequestTypeDef",
    {
        "loggingOptionsPayload": LoggingOptionsPayloadTypeDef,
    },
)
MitigationActionParamsPaginatorTypeDef = TypedDict(
    "MitigationActionParamsPaginatorTypeDef",
    {
        "updateDeviceCertificateParams": NotRequired[UpdateDeviceCertificateParamsTypeDef],
        "updateCACertificateParams": NotRequired[UpdateCACertificateParamsTypeDef],
        "addThingsToThingGroupParams": NotRequired[AddThingsToThingGroupParamsPaginatorTypeDef],
        "replaceDefaultPolicyVersionParams": NotRequired[ReplaceDefaultPolicyVersionParamsTypeDef],
        "enableIoTLoggingParams": NotRequired[EnableIoTLoggingParamsTypeDef],
        "publishFindingToSnsParams": NotRequired[PublishFindingToSnsParamsTypeDef],
    },
)
MitigationActionParamsTypeDef = TypedDict(
    "MitigationActionParamsTypeDef",
    {
        "updateDeviceCertificateParams": NotRequired[UpdateDeviceCertificateParamsTypeDef],
        "updateCACertificateParams": NotRequired[UpdateCACertificateParamsTypeDef],
        "addThingsToThingGroupParams": NotRequired[AddThingsToThingGroupParamsTypeDef],
        "replaceDefaultPolicyVersionParams": NotRequired[ReplaceDefaultPolicyVersionParamsTypeDef],
        "enableIoTLoggingParams": NotRequired[EnableIoTLoggingParamsTypeDef],
        "publishFindingToSnsParams": NotRequired[PublishFindingToSnsParamsTypeDef],
    },
)
MqttHeadersTypeDef = TypedDict(
    "MqttHeadersTypeDef",
    {
        "payloadFormatIndicator": NotRequired[str],
        "contentType": NotRequired[str],
        "responseTopic": NotRequired[str],
        "correlationData": NotRequired[str],
        "messageExpiry": NotRequired[str],
        "userProperties": NotRequired[Sequence[UserPropertyTypeDef]],
    },
)
ResourceIdentifierTypeDef = TypedDict(
    "ResourceIdentifierTypeDef",
    {
        "deviceCertificateId": NotRequired[str],
        "caCertificateId": NotRequired[str],
        "cognitoIdentityPoolId": NotRequired[str],
        "clientId": NotRequired[str],
        "policyVersionIdentifier": NotRequired[PolicyVersionIdentifierTypeDef],
        "account": NotRequired[str],
        "iamRoleArn": NotRequired[str],
        "roleAliasArn": NotRequired[str],
        "issuerCertificateIdentifier": NotRequired[IssuerCertificateIdentifierTypeDef],
        "deviceCertificateArn": NotRequired[str],
    },
)
ThingDocumentTypeDef = TypedDict(
    "ThingDocumentTypeDef",
    {
        "thingName": NotRequired[str],
        "thingId": NotRequired[str],
        "thingTypeName": NotRequired[str],
        "thingGroupNames": NotRequired[List[str]],
        "attributes": NotRequired[Dict[str, str]],
        "shadow": NotRequired[str],
        "deviceDefender": NotRequired[str],
        "connectivity": NotRequired[ThingConnectivityTypeDef],
    },
)
ThingTypeDefinitionPaginatorTypeDef = TypedDict(
    "ThingTypeDefinitionPaginatorTypeDef",
    {
        "thingTypeName": NotRequired[str],
        "thingTypeArn": NotRequired[str],
        "thingTypeProperties": NotRequired[ThingTypePropertiesPaginatorTypeDef],
        "thingTypeMetadata": NotRequired[ThingTypeMetadataTypeDef],
    },
)
TimestreamActionTypeDef = TypedDict(
    "TimestreamActionTypeDef",
    {
        "roleArn": str,
        "databaseName": str,
        "tableName": str,
        "dimensions": Sequence[TimestreamDimensionTypeDef],
        "timestamp": NotRequired[TimestreamTimestampTypeDef],
    },
)
TopicRuleDestinationConfigurationTypeDef = TypedDict(
    "TopicRuleDestinationConfigurationTypeDef",
    {
        "httpUrlConfiguration": NotRequired[HttpUrlDestinationConfigurationTypeDef],
        "vpcConfiguration": NotRequired[VpcDestinationConfigurationTypeDef],
    },
)
TopicRuleDestinationSummaryTypeDef = TypedDict(
    "TopicRuleDestinationSummaryTypeDef",
    {
        "arn": NotRequired[str],
        "status": NotRequired[TopicRuleDestinationStatusType],
        "createdAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "statusReason": NotRequired[str],
        "httpUrlSummary": NotRequired[HttpUrlDestinationSummaryTypeDef],
        "vpcDestinationSummary": NotRequired[VpcDestinationSummaryTypeDef],
    },
)
TopicRuleDestinationTypeDef = TypedDict(
    "TopicRuleDestinationTypeDef",
    {
        "arn": NotRequired[str],
        "status": NotRequired[TopicRuleDestinationStatusType],
        "createdAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "statusReason": NotRequired[str],
        "httpUrlProperties": NotRequired[HttpUrlDestinationPropertiesTypeDef],
        "vpcProperties": NotRequired[VpcDestinationPropertiesTypeDef],
    },
)
ValidateSecurityProfileBehaviorsResponseTypeDef = TypedDict(
    "ValidateSecurityProfileBehaviorsResponseTypeDef",
    {
        "valid": bool,
        "validationErrors": List[ValidationErrorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMetricValuesResponsePaginatorTypeDef = TypedDict(
    "ListMetricValuesResponsePaginatorTypeDef",
    {
        "metricDatumList": List[MetricDatumPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMetricValuesResponseTypeDef = TypedDict(
    "ListMetricValuesResponseTypeDef",
    {
        "metricDatumList": List[MetricDatumTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeniedTypeDef = TypedDict(
    "DeniedTypeDef",
    {
        "implicitDeny": NotRequired[ImplicitDenyTypeDef],
        "explicitDeny": NotRequired[ExplicitDenyTypeDef],
    },
)
PutAssetPropertyValueEntryTypeDef = TypedDict(
    "PutAssetPropertyValueEntryTypeDef",
    {
        "propertyValues": Sequence[AssetPropertyValueTypeDef],
        "entryId": NotRequired[str],
        "assetId": NotRequired[str],
        "propertyId": NotRequired[str],
        "propertyAlias": NotRequired[str],
    },
)
CreateDynamicThingGroupRequestRequestTypeDef = TypedDict(
    "CreateDynamicThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "queryString": str,
        "thingGroupProperties": NotRequired[ThingGroupPropertiesTypeDef],
        "indexName": NotRequired[str],
        "queryVersion": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreateThingGroupRequestRequestTypeDef = TypedDict(
    "CreateThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "parentGroupName": NotRequired[str],
        "thingGroupProperties": NotRequired[ThingGroupPropertiesTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
UpdateDynamicThingGroupRequestRequestTypeDef = TypedDict(
    "UpdateDynamicThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "thingGroupProperties": ThingGroupPropertiesTypeDef,
        "expectedVersion": NotRequired[int],
        "indexName": NotRequired[str],
        "queryString": NotRequired[str],
        "queryVersion": NotRequired[str],
    },
)
UpdateThingGroupRequestRequestTypeDef = TypedDict(
    "UpdateThingGroupRequestRequestTypeDef",
    {
        "thingGroupName": str,
        "thingGroupProperties": ThingGroupPropertiesTypeDef,
        "expectedVersion": NotRequired[int],
    },
)
AwsJobExecutionsRolloutConfigTypeDef = TypedDict(
    "AwsJobExecutionsRolloutConfigTypeDef",
    {
        "maximumPerMinute": NotRequired[int],
        "exponentialRate": NotRequired[AwsJobExponentialRolloutRateTypeDef],
    },
)
BehaviorPaginatorTypeDef = TypedDict(
    "BehaviorPaginatorTypeDef",
    {
        "name": str,
        "metric": NotRequired[str],
        "metricDimension": NotRequired[MetricDimensionTypeDef],
        "criteria": NotRequired[BehaviorCriteriaPaginatorTypeDef],
        "suppressAlerts": NotRequired[bool],
        "exportMetric": NotRequired[bool],
    },
)
BehaviorTypeDef = TypedDict(
    "BehaviorTypeDef",
    {
        "name": str,
        "metric": NotRequired[str],
        "metricDimension": NotRequired[MetricDimensionTypeDef],
        "criteria": NotRequired[BehaviorCriteriaTypeDef],
        "suppressAlerts": NotRequired[bool],
        "exportMetric": NotRequired[bool],
    },
)
CustomCodeSigningTypeDef = TypedDict(
    "CustomCodeSigningTypeDef",
    {
        "signature": NotRequired[CodeSigningSignatureTypeDef],
        "certificateChain": NotRequired[CodeSigningCertificateChainTypeDef],
        "hashAlgorithm": NotRequired[str],
        "signatureAlgorithm": NotRequired[str],
    },
)
TestInvokeAuthorizerRequestRequestTypeDef = TypedDict(
    "TestInvokeAuthorizerRequestRequestTypeDef",
    {
        "authorizerName": str,
        "token": NotRequired[str],
        "tokenSignature": NotRequired[str],
        "httpContext": NotRequired[HttpContextTypeDef],
        "mqttContext": NotRequired[MqttContextTypeDef],
        "tlsContext": NotRequired[TlsContextTypeDef],
    },
)
GetBucketsAggregationRequestRequestTypeDef = TypedDict(
    "GetBucketsAggregationRequestRequestTypeDef",
    {
        "queryString": str,
        "aggregationField": str,
        "bucketsAggregationType": BucketsAggregationTypeTypeDef,
        "indexName": NotRequired[str],
        "queryVersion": NotRequired[str],
    },
)
DescribeCACertificateResponseTypeDef = TypedDict(
    "DescribeCACertificateResponseTypeDef",
    {
        "certificateDescription": CACertificateDescriptionTypeDef,
        "registrationConfig": RegistrationConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeCertificateResponseTypeDef = TypedDict(
    "DescribeCertificateResponseTypeDef",
    {
        "certificateDescription": CertificateDescriptionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingTypesResponseTypeDef = TypedDict(
    "ListThingTypesResponseTypeDef",
    {
        "thingTypes": List[ThingTypeDefinitionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartSigningJobParameterTypeDef = TypedDict(
    "StartSigningJobParameterTypeDef",
    {
        "signingProfileParameter": NotRequired[SigningProfileParameterTypeDef],
        "signingProfileName": NotRequired[str],
        "destination": NotRequired[DestinationTypeDef],
    },
)
JobExecutionsRolloutConfigTypeDef = TypedDict(
    "JobExecutionsRolloutConfigTypeDef",
    {
        "maximumPerMinute": NotRequired[int],
        "exponentialRate": NotRequired[ExponentialRolloutRateTypeDef],
    },
)
CreateStreamRequestRequestTypeDef = TypedDict(
    "CreateStreamRequestRequestTypeDef",
    {
        "streamId": str,
        "files": Sequence[StreamFileTypeDef],
        "roleArn": str,
        "description": NotRequired[str],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
StreamInfoTypeDef = TypedDict(
    "StreamInfoTypeDef",
    {
        "streamId": NotRequired[str],
        "streamArn": NotRequired[str],
        "streamVersion": NotRequired[int],
        "description": NotRequired[str],
        "files": NotRequired[List[StreamFileTypeDef]],
        "createdAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "roleArn": NotRequired[str],
    },
)
UpdateStreamRequestRequestTypeDef = TypedDict(
    "UpdateStreamRequestRequestTypeDef",
    {
        "streamId": str,
        "description": NotRequired[str],
        "files": NotRequired[Sequence[StreamFileTypeDef]],
        "roleArn": NotRequired[str],
    },
)
ThingIndexingConfigurationTypeDef = TypedDict(
    "ThingIndexingConfigurationTypeDef",
    {
        "thingIndexingMode": ThingIndexingModeType,
        "thingConnectivityIndexingMode": NotRequired[ThingConnectivityIndexingModeType],
        "deviceDefenderIndexingMode": NotRequired[DeviceDefenderIndexingModeType],
        "namedShadowIndexingMode": NotRequired[NamedShadowIndexingModeType],
        "managedFields": NotRequired[List[FieldTypeDef]],
        "customFields": NotRequired[List[FieldTypeDef]],
        "filter": NotRequired[IndexingFilterTypeDef],
    },
)
DescribeThingGroupResponseTypeDef = TypedDict(
    "DescribeThingGroupResponseTypeDef",
    {
        "thingGroupName": str,
        "thingGroupId": str,
        "thingGroupArn": str,
        "version": int,
        "thingGroupProperties": ThingGroupPropertiesTypeDef,
        "thingGroupMetadata": ThingGroupMetadataTypeDef,
        "indexName": str,
        "queryString": str,
        "queryVersion": str,
        "status": DynamicGroupStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HttpActionTypeDef = TypedDict(
    "HttpActionTypeDef",
    {
        "url": str,
        "confirmationUrl": NotRequired[str],
        "headers": NotRequired[Sequence[HttpActionHeaderTypeDef]],
        "auth": NotRequired[HttpAuthorizationTypeDef],
    },
)
DescribeJobExecutionResponseTypeDef = TypedDict(
    "DescribeJobExecutionResponseTypeDef",
    {
        "execution": JobExecutionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListJobExecutionsForJobResponseTypeDef = TypedDict(
    "ListJobExecutionsForJobResponseTypeDef",
    {
        "executionSummaries": List[JobExecutionSummaryForJobTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListJobExecutionsForThingResponseTypeDef = TypedDict(
    "ListJobExecutionsForThingResponseTypeDef",
    {
        "executionSummaries": List[JobExecutionSummaryForThingTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSecurityProfilesForTargetResponseTypeDef = TypedDict(
    "ListSecurityProfilesForTargetResponseTypeDef",
    {
        "securityProfileTargetMappings": List[SecurityProfileTargetMappingTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListV2LoggingLevelsResponseTypeDef = TypedDict(
    "ListV2LoggingLevelsResponseTypeDef",
    {
        "logTargetConfigurations": List[LogTargetConfigurationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MitigationActionPaginatorTypeDef = TypedDict(
    "MitigationActionPaginatorTypeDef",
    {
        "name": NotRequired[str],
        "id": NotRequired[str],
        "roleArn": NotRequired[str],
        "actionParams": NotRequired[MitigationActionParamsPaginatorTypeDef],
    },
)
CreateMitigationActionRequestRequestTypeDef = TypedDict(
    "CreateMitigationActionRequestRequestTypeDef",
    {
        "actionName": str,
        "roleArn": str,
        "actionParams": MitigationActionParamsTypeDef,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
DescribeMitigationActionResponseTypeDef = TypedDict(
    "DescribeMitigationActionResponseTypeDef",
    {
        "actionName": str,
        "actionType": MitigationActionTypeType,
        "actionArn": str,
        "actionId": str,
        "roleArn": str,
        "actionParams": MitigationActionParamsTypeDef,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MitigationActionTypeDef = TypedDict(
    "MitigationActionTypeDef",
    {
        "name": NotRequired[str],
        "id": NotRequired[str],
        "roleArn": NotRequired[str],
        "actionParams": NotRequired[MitigationActionParamsTypeDef],
    },
)
UpdateMitigationActionRequestRequestTypeDef = TypedDict(
    "UpdateMitigationActionRequestRequestTypeDef",
    {
        "actionName": str,
        "roleArn": NotRequired[str],
        "actionParams": NotRequired[MitigationActionParamsTypeDef],
    },
)
RepublishActionTypeDef = TypedDict(
    "RepublishActionTypeDef",
    {
        "roleArn": str,
        "topic": str,
        "qos": NotRequired[int],
        "headers": NotRequired[MqttHeadersTypeDef],
    },
)
AuditSuppressionTypeDef = TypedDict(
    "AuditSuppressionTypeDef",
    {
        "checkName": str,
        "resourceIdentifier": ResourceIdentifierTypeDef,
        "expirationDate": NotRequired[datetime],
        "suppressIndefinitely": NotRequired[bool],
        "description": NotRequired[str],
    },
)
CreateAuditSuppressionRequestRequestTypeDef = TypedDict(
    "CreateAuditSuppressionRequestRequestTypeDef",
    {
        "checkName": str,
        "resourceIdentifier": ResourceIdentifierTypeDef,
        "clientRequestToken": str,
        "expirationDate": NotRequired[TimestampTypeDef],
        "suppressIndefinitely": NotRequired[bool],
        "description": NotRequired[str],
    },
)
DeleteAuditSuppressionRequestRequestTypeDef = TypedDict(
    "DeleteAuditSuppressionRequestRequestTypeDef",
    {
        "checkName": str,
        "resourceIdentifier": ResourceIdentifierTypeDef,
    },
)
DescribeAuditSuppressionRequestRequestTypeDef = TypedDict(
    "DescribeAuditSuppressionRequestRequestTypeDef",
    {
        "checkName": str,
        "resourceIdentifier": ResourceIdentifierTypeDef,
    },
)
DescribeAuditSuppressionResponseTypeDef = TypedDict(
    "DescribeAuditSuppressionResponseTypeDef",
    {
        "checkName": str,
        "resourceIdentifier": ResourceIdentifierTypeDef,
        "expirationDate": datetime,
        "suppressIndefinitely": bool,
        "description": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAuditFindingsRequestListAuditFindingsPaginateTypeDef = TypedDict(
    "ListAuditFindingsRequestListAuditFindingsPaginateTypeDef",
    {
        "taskId": NotRequired[str],
        "checkName": NotRequired[str],
        "resourceIdentifier": NotRequired[ResourceIdentifierTypeDef],
        "startTime": NotRequired[TimestampTypeDef],
        "endTime": NotRequired[TimestampTypeDef],
        "listSuppressedFindings": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuditFindingsRequestRequestTypeDef = TypedDict(
    "ListAuditFindingsRequestRequestTypeDef",
    {
        "taskId": NotRequired[str],
        "checkName": NotRequired[str],
        "resourceIdentifier": NotRequired[ResourceIdentifierTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "startTime": NotRequired[TimestampTypeDef],
        "endTime": NotRequired[TimestampTypeDef],
        "listSuppressedFindings": NotRequired[bool],
    },
)
ListAuditSuppressionsRequestListAuditSuppressionsPaginateTypeDef = TypedDict(
    "ListAuditSuppressionsRequestListAuditSuppressionsPaginateTypeDef",
    {
        "checkName": NotRequired[str],
        "resourceIdentifier": NotRequired[ResourceIdentifierTypeDef],
        "ascendingOrder": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListAuditSuppressionsRequestRequestTypeDef = TypedDict(
    "ListAuditSuppressionsRequestRequestTypeDef",
    {
        "checkName": NotRequired[str],
        "resourceIdentifier": NotRequired[ResourceIdentifierTypeDef],
        "ascendingOrder": NotRequired[bool],
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
NonCompliantResourceTypeDef = TypedDict(
    "NonCompliantResourceTypeDef",
    {
        "resourceType": NotRequired[ResourceTypeType],
        "resourceIdentifier": NotRequired[ResourceIdentifierTypeDef],
        "additionalInfo": NotRequired[Dict[str, str]],
    },
)
RelatedResourceTypeDef = TypedDict(
    "RelatedResourceTypeDef",
    {
        "resourceType": NotRequired[ResourceTypeType],
        "resourceIdentifier": NotRequired[ResourceIdentifierTypeDef],
        "additionalInfo": NotRequired[Dict[str, str]],
    },
)
UpdateAuditSuppressionRequestRequestTypeDef = TypedDict(
    "UpdateAuditSuppressionRequestRequestTypeDef",
    {
        "checkName": str,
        "resourceIdentifier": ResourceIdentifierTypeDef,
        "expirationDate": NotRequired[TimestampTypeDef],
        "suppressIndefinitely": NotRequired[bool],
        "description": NotRequired[str],
    },
)
SearchIndexResponseTypeDef = TypedDict(
    "SearchIndexResponseTypeDef",
    {
        "nextToken": str,
        "things": List[ThingDocumentTypeDef],
        "thingGroups": List[ThingGroupDocumentTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListThingTypesResponsePaginatorTypeDef = TypedDict(
    "ListThingTypesResponsePaginatorTypeDef",
    {
        "thingTypes": List[ThingTypeDefinitionPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTopicRuleDestinationRequestRequestTypeDef = TypedDict(
    "CreateTopicRuleDestinationRequestRequestTypeDef",
    {
        "destinationConfiguration": TopicRuleDestinationConfigurationTypeDef,
    },
)
ListTopicRuleDestinationsResponseTypeDef = TypedDict(
    "ListTopicRuleDestinationsResponseTypeDef",
    {
        "destinationSummaries": List[TopicRuleDestinationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateTopicRuleDestinationResponseTypeDef = TypedDict(
    "CreateTopicRuleDestinationResponseTypeDef",
    {
        "topicRuleDestination": TopicRuleDestinationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetTopicRuleDestinationResponseTypeDef = TypedDict(
    "GetTopicRuleDestinationResponseTypeDef",
    {
        "topicRuleDestination": TopicRuleDestinationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AuthResultTypeDef = TypedDict(
    "AuthResultTypeDef",
    {
        "authInfo": NotRequired[AuthInfoTypeDef],
        "allowed": NotRequired[AllowedTypeDef],
        "denied": NotRequired[DeniedTypeDef],
        "authDecision": NotRequired[AuthDecisionType],
        "missingContextValues": NotRequired[List[str]],
    },
)
IotSiteWiseActionTypeDef = TypedDict(
    "IotSiteWiseActionTypeDef",
    {
        "putAssetPropertyValueEntries": Sequence[PutAssetPropertyValueEntryTypeDef],
        "roleArn": str,
    },
)
ActiveViolationPaginatorTypeDef = TypedDict(
    "ActiveViolationPaginatorTypeDef",
    {
        "violationId": NotRequired[str],
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behavior": NotRequired[BehaviorPaginatorTypeDef],
        "lastViolationValue": NotRequired[MetricValuePaginatorTypeDef],
        "violationEventAdditionalInfo": NotRequired[ViolationEventAdditionalInfoTypeDef],
        "verificationState": NotRequired[VerificationStateType],
        "verificationStateDescription": NotRequired[str],
        "lastViolationTime": NotRequired[datetime],
        "violationStartTime": NotRequired[datetime],
    },
)
ViolationEventPaginatorTypeDef = TypedDict(
    "ViolationEventPaginatorTypeDef",
    {
        "violationId": NotRequired[str],
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behavior": NotRequired[BehaviorPaginatorTypeDef],
        "metricValue": NotRequired[MetricValuePaginatorTypeDef],
        "violationEventAdditionalInfo": NotRequired[ViolationEventAdditionalInfoTypeDef],
        "violationEventType": NotRequired[ViolationEventTypeType],
        "verificationState": NotRequired[VerificationStateType],
        "verificationStateDescription": NotRequired[str],
        "violationEventTime": NotRequired[datetime],
    },
)
ActiveViolationTypeDef = TypedDict(
    "ActiveViolationTypeDef",
    {
        "violationId": NotRequired[str],
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behavior": NotRequired[BehaviorTypeDef],
        "lastViolationValue": NotRequired[MetricValueTypeDef],
        "violationEventAdditionalInfo": NotRequired[ViolationEventAdditionalInfoTypeDef],
        "verificationState": NotRequired[VerificationStateType],
        "verificationStateDescription": NotRequired[str],
        "lastViolationTime": NotRequired[datetime],
        "violationStartTime": NotRequired[datetime],
    },
)
CreateSecurityProfileRequestRequestTypeDef = TypedDict(
    "CreateSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
        "securityProfileDescription": NotRequired[str],
        "behaviors": NotRequired[Sequence[BehaviorTypeDef]],
        "alertTargets": NotRequired[Mapping[Literal["SNS"], AlertTargetTypeDef]],
        "additionalMetricsToRetain": NotRequired[Sequence[str]],
        "additionalMetricsToRetainV2": NotRequired[Sequence[MetricToRetainTypeDef]],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "metricsExportConfig": NotRequired[MetricsExportConfigTypeDef],
    },
)
DescribeSecurityProfileResponseTypeDef = TypedDict(
    "DescribeSecurityProfileResponseTypeDef",
    {
        "securityProfileName": str,
        "securityProfileArn": str,
        "securityProfileDescription": str,
        "behaviors": List[BehaviorTypeDef],
        "alertTargets": Dict[Literal["SNS"], AlertTargetTypeDef],
        "additionalMetricsToRetain": List[str],
        "additionalMetricsToRetainV2": List[MetricToRetainTypeDef],
        "version": int,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "metricsExportConfig": MetricsExportConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSecurityProfileRequestRequestTypeDef = TypedDict(
    "UpdateSecurityProfileRequestRequestTypeDef",
    {
        "securityProfileName": str,
        "securityProfileDescription": NotRequired[str],
        "behaviors": NotRequired[Sequence[BehaviorTypeDef]],
        "alertTargets": NotRequired[Mapping[Literal["SNS"], AlertTargetTypeDef]],
        "additionalMetricsToRetain": NotRequired[Sequence[str]],
        "additionalMetricsToRetainV2": NotRequired[Sequence[MetricToRetainTypeDef]],
        "deleteBehaviors": NotRequired[bool],
        "deleteAlertTargets": NotRequired[bool],
        "deleteAdditionalMetricsToRetain": NotRequired[bool],
        "expectedVersion": NotRequired[int],
        "metricsExportConfig": NotRequired[MetricsExportConfigTypeDef],
        "deleteMetricsExportConfig": NotRequired[bool],
    },
)
UpdateSecurityProfileResponseTypeDef = TypedDict(
    "UpdateSecurityProfileResponseTypeDef",
    {
        "securityProfileName": str,
        "securityProfileArn": str,
        "securityProfileDescription": str,
        "behaviors": List[BehaviorTypeDef],
        "alertTargets": Dict[Literal["SNS"], AlertTargetTypeDef],
        "additionalMetricsToRetain": List[str],
        "additionalMetricsToRetainV2": List[MetricToRetainTypeDef],
        "version": int,
        "creationDate": datetime,
        "lastModifiedDate": datetime,
        "metricsExportConfig": MetricsExportConfigTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ValidateSecurityProfileBehaviorsRequestRequestTypeDef = TypedDict(
    "ValidateSecurityProfileBehaviorsRequestRequestTypeDef",
    {
        "behaviors": Sequence[BehaviorTypeDef],
    },
)
ViolationEventTypeDef = TypedDict(
    "ViolationEventTypeDef",
    {
        "violationId": NotRequired[str],
        "thingName": NotRequired[str],
        "securityProfileName": NotRequired[str],
        "behavior": NotRequired[BehaviorTypeDef],
        "metricValue": NotRequired[MetricValueTypeDef],
        "violationEventAdditionalInfo": NotRequired[ViolationEventAdditionalInfoTypeDef],
        "violationEventType": NotRequired[ViolationEventTypeType],
        "verificationState": NotRequired[VerificationStateType],
        "verificationStateDescription": NotRequired[str],
        "violationEventTime": NotRequired[datetime],
    },
)
CodeSigningTypeDef = TypedDict(
    "CodeSigningTypeDef",
    {
        "awsSignerJobId": NotRequired[str],
        "startSigningJobParameter": NotRequired[StartSigningJobParameterTypeDef],
        "customCodeSigning": NotRequired[CustomCodeSigningTypeDef],
    },
)
CreateJobRequestRequestTypeDef = TypedDict(
    "CreateJobRequestRequestTypeDef",
    {
        "jobId": str,
        "targets": Sequence[str],
        "documentSource": NotRequired[str],
        "document": NotRequired[str],
        "description": NotRequired[str],
        "presignedUrlConfig": NotRequired[PresignedUrlConfigTypeDef],
        "targetSelection": NotRequired[TargetSelectionType],
        "jobExecutionsRolloutConfig": NotRequired[JobExecutionsRolloutConfigTypeDef],
        "abortConfig": NotRequired[AbortConfigTypeDef],
        "timeoutConfig": NotRequired[TimeoutConfigTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "namespaceId": NotRequired[str],
        "jobTemplateArn": NotRequired[str],
        "jobExecutionsRetryConfig": NotRequired[JobExecutionsRetryConfigTypeDef],
        "documentParameters": NotRequired[Mapping[str, str]],
        "schedulingConfig": NotRequired[SchedulingConfigTypeDef],
        "destinationPackageVersions": NotRequired[Sequence[str]],
    },
)
CreateJobTemplateRequestRequestTypeDef = TypedDict(
    "CreateJobTemplateRequestRequestTypeDef",
    {
        "jobTemplateId": str,
        "description": str,
        "jobArn": NotRequired[str],
        "documentSource": NotRequired[str],
        "document": NotRequired[str],
        "presignedUrlConfig": NotRequired[PresignedUrlConfigTypeDef],
        "jobExecutionsRolloutConfig": NotRequired[JobExecutionsRolloutConfigTypeDef],
        "abortConfig": NotRequired[AbortConfigTypeDef],
        "timeoutConfig": NotRequired[TimeoutConfigTypeDef],
        "tags": NotRequired[Sequence[TagTypeDef]],
        "jobExecutionsRetryConfig": NotRequired[JobExecutionsRetryConfigTypeDef],
        "maintenanceWindows": NotRequired[Sequence[MaintenanceWindowTypeDef]],
        "destinationPackageVersions": NotRequired[Sequence[str]],
    },
)
DescribeJobTemplateResponseTypeDef = TypedDict(
    "DescribeJobTemplateResponseTypeDef",
    {
        "jobTemplateArn": str,
        "jobTemplateId": str,
        "description": str,
        "documentSource": str,
        "document": str,
        "createdAt": datetime,
        "presignedUrlConfig": PresignedUrlConfigTypeDef,
        "jobExecutionsRolloutConfig": JobExecutionsRolloutConfigTypeDef,
        "abortConfig": AbortConfigTypeDef,
        "timeoutConfig": TimeoutConfigTypeDef,
        "jobExecutionsRetryConfig": JobExecutionsRetryConfigTypeDef,
        "maintenanceWindows": List[MaintenanceWindowTypeDef],
        "destinationPackageVersions": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JobTypeDef = TypedDict(
    "JobTypeDef",
    {
        "jobArn": NotRequired[str],
        "jobId": NotRequired[str],
        "targetSelection": NotRequired[TargetSelectionType],
        "status": NotRequired[JobStatusType],
        "forceCanceled": NotRequired[bool],
        "reasonCode": NotRequired[str],
        "comment": NotRequired[str],
        "targets": NotRequired[List[str]],
        "description": NotRequired[str],
        "presignedUrlConfig": NotRequired[PresignedUrlConfigTypeDef],
        "jobExecutionsRolloutConfig": NotRequired[JobExecutionsRolloutConfigTypeDef],
        "abortConfig": NotRequired[AbortConfigTypeDef],
        "createdAt": NotRequired[datetime],
        "lastUpdatedAt": NotRequired[datetime],
        "completedAt": NotRequired[datetime],
        "jobProcessDetails": NotRequired[JobProcessDetailsTypeDef],
        "timeoutConfig": NotRequired[TimeoutConfigTypeDef],
        "namespaceId": NotRequired[str],
        "jobTemplateArn": NotRequired[str],
        "jobExecutionsRetryConfig": NotRequired[JobExecutionsRetryConfigTypeDef],
        "documentParameters": NotRequired[Dict[str, str]],
        "isConcurrent": NotRequired[bool],
        "schedulingConfig": NotRequired[SchedulingConfigTypeDef],
        "scheduledJobRollouts": NotRequired[List[ScheduledJobRolloutTypeDef]],
        "destinationPackageVersions": NotRequired[List[str]],
    },
)
UpdateJobRequestRequestTypeDef = TypedDict(
    "UpdateJobRequestRequestTypeDef",
    {
        "jobId": str,
        "description": NotRequired[str],
        "presignedUrlConfig": NotRequired[PresignedUrlConfigTypeDef],
        "jobExecutionsRolloutConfig": NotRequired[JobExecutionsRolloutConfigTypeDef],
        "abortConfig": NotRequired[AbortConfigTypeDef],
        "timeoutConfig": NotRequired[TimeoutConfigTypeDef],
        "namespaceId": NotRequired[str],
        "jobExecutionsRetryConfig": NotRequired[JobExecutionsRetryConfigTypeDef],
    },
)
DescribeStreamResponseTypeDef = TypedDict(
    "DescribeStreamResponseTypeDef",
    {
        "streamInfo": StreamInfoTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetIndexingConfigurationResponseTypeDef = TypedDict(
    "GetIndexingConfigurationResponseTypeDef",
    {
        "thingIndexingConfiguration": ThingIndexingConfigurationTypeDef,
        "thingGroupIndexingConfiguration": ThingGroupIndexingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateIndexingConfigurationRequestRequestTypeDef = TypedDict(
    "UpdateIndexingConfigurationRequestRequestTypeDef",
    {
        "thingIndexingConfiguration": NotRequired[ThingIndexingConfigurationTypeDef],
        "thingGroupIndexingConfiguration": NotRequired[ThingGroupIndexingConfigurationTypeDef],
    },
)
DetectMitigationActionsTaskSummaryPaginatorTypeDef = TypedDict(
    "DetectMitigationActionsTaskSummaryPaginatorTypeDef",
    {
        "taskId": NotRequired[str],
        "taskStatus": NotRequired[DetectMitigationActionsTaskStatusType],
        "taskStartTime": NotRequired[datetime],
        "taskEndTime": NotRequired[datetime],
        "target": NotRequired[DetectMitigationActionsTaskTargetTypeDef],
        "violationEventOccurrenceRange": NotRequired[ViolationEventOccurrenceRangeTypeDef],
        "onlyActiveViolationsIncluded": NotRequired[bool],
        "suppressedAlertsIncluded": NotRequired[bool],
        "actionsDefinition": NotRequired[List[MitigationActionPaginatorTypeDef]],
        "taskStatistics": NotRequired[DetectMitigationActionsTaskStatisticsTypeDef],
    },
)
DescribeAuditMitigationActionsTaskResponseTypeDef = TypedDict(
    "DescribeAuditMitigationActionsTaskResponseTypeDef",
    {
        "taskStatus": AuditMitigationActionsTaskStatusType,
        "startTime": datetime,
        "endTime": datetime,
        "taskStatistics": Dict[str, TaskStatisticsForAuditCheckTypeDef],
        "target": AuditMitigationActionsTaskTargetTypeDef,
        "auditCheckToActionsMapping": Dict[str, List[str]],
        "actionsDefinition": List[MitigationActionTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DetectMitigationActionsTaskSummaryTypeDef = TypedDict(
    "DetectMitigationActionsTaskSummaryTypeDef",
    {
        "taskId": NotRequired[str],
        "taskStatus": NotRequired[DetectMitigationActionsTaskStatusType],
        "taskStartTime": NotRequired[datetime],
        "taskEndTime": NotRequired[datetime],
        "target": NotRequired[DetectMitigationActionsTaskTargetTypeDef],
        "violationEventOccurrenceRange": NotRequired[ViolationEventOccurrenceRangeTypeDef],
        "onlyActiveViolationsIncluded": NotRequired[bool],
        "suppressedAlertsIncluded": NotRequired[bool],
        "actionsDefinition": NotRequired[List[MitigationActionTypeDef]],
        "taskStatistics": NotRequired[DetectMitigationActionsTaskStatisticsTypeDef],
    },
)
ListAuditSuppressionsResponseTypeDef = TypedDict(
    "ListAuditSuppressionsResponseTypeDef",
    {
        "suppressions": List[AuditSuppressionTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AuditFindingTypeDef = TypedDict(
    "AuditFindingTypeDef",
    {
        "findingId": NotRequired[str],
        "taskId": NotRequired[str],
        "checkName": NotRequired[str],
        "taskStartTime": NotRequired[datetime],
        "findingTime": NotRequired[datetime],
        "severity": NotRequired[AuditFindingSeverityType],
        "nonCompliantResource": NotRequired[NonCompliantResourceTypeDef],
        "relatedResources": NotRequired[List[RelatedResourceTypeDef]],
        "reasonForNonCompliance": NotRequired[str],
        "reasonForNonComplianceCode": NotRequired[str],
        "isSuppressed": NotRequired[bool],
    },
)
ListRelatedResourcesForAuditFindingResponseTypeDef = TypedDict(
    "ListRelatedResourcesForAuditFindingResponseTypeDef",
    {
        "relatedResources": List[RelatedResourceTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestAuthorizationResponseTypeDef = TypedDict(
    "TestAuthorizationResponseTypeDef",
    {
        "authResults": List[AuthResultTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ActionTypeDef = TypedDict(
    "ActionTypeDef",
    {
        "dynamoDB": NotRequired[DynamoDBActionTypeDef],
        "dynamoDBv2": NotRequired[DynamoDBv2ActionTypeDef],
        "lambda": NotRequired[LambdaActionTypeDef],
        "sns": NotRequired[SnsActionTypeDef],
        "sqs": NotRequired[SqsActionTypeDef],
        "kinesis": NotRequired[KinesisActionTypeDef],
        "republish": NotRequired[RepublishActionTypeDef],
        "s3": NotRequired[S3ActionTypeDef],
        "firehose": NotRequired[FirehoseActionTypeDef],
        "cloudwatchMetric": NotRequired[CloudwatchMetricActionTypeDef],
        "cloudwatchAlarm": NotRequired[CloudwatchAlarmActionTypeDef],
        "cloudwatchLogs": NotRequired[CloudwatchLogsActionTypeDef],
        "elasticsearch": NotRequired[ElasticsearchActionTypeDef],
        "salesforce": NotRequired[SalesforceActionTypeDef],
        "iotAnalytics": NotRequired[IotAnalyticsActionTypeDef],
        "iotEvents": NotRequired[IotEventsActionTypeDef],
        "iotSiteWise": NotRequired[IotSiteWiseActionTypeDef],
        "stepFunctions": NotRequired[StepFunctionsActionTypeDef],
        "timestream": NotRequired[TimestreamActionTypeDef],
        "http": NotRequired[HttpActionTypeDef],
        "kafka": NotRequired[KafkaActionTypeDef],
        "openSearch": NotRequired[OpenSearchActionTypeDef],
        "location": NotRequired[LocationActionTypeDef],
    },
)
ListActiveViolationsResponsePaginatorTypeDef = TypedDict(
    "ListActiveViolationsResponsePaginatorTypeDef",
    {
        "activeViolations": List[ActiveViolationPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListViolationEventsResponsePaginatorTypeDef = TypedDict(
    "ListViolationEventsResponsePaginatorTypeDef",
    {
        "violationEvents": List[ViolationEventPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListActiveViolationsResponseTypeDef = TypedDict(
    "ListActiveViolationsResponseTypeDef",
    {
        "activeViolations": List[ActiveViolationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListViolationEventsResponseTypeDef = TypedDict(
    "ListViolationEventsResponseTypeDef",
    {
        "violationEvents": List[ViolationEventTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
OTAUpdateFileTypeDef = TypedDict(
    "OTAUpdateFileTypeDef",
    {
        "fileName": NotRequired[str],
        "fileType": NotRequired[int],
        "fileVersion": NotRequired[str],
        "fileLocation": NotRequired[FileLocationTypeDef],
        "codeSigning": NotRequired[CodeSigningTypeDef],
        "attributes": NotRequired[Mapping[str, str]],
    },
)
DescribeJobResponseTypeDef = TypedDict(
    "DescribeJobResponseTypeDef",
    {
        "documentSource": str,
        "job": JobTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDetectMitigationActionsTasksResponsePaginatorTypeDef = TypedDict(
    "ListDetectMitigationActionsTasksResponsePaginatorTypeDef",
    {
        "tasks": List[DetectMitigationActionsTaskSummaryPaginatorTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeDetectMitigationActionsTaskResponseTypeDef = TypedDict(
    "DescribeDetectMitigationActionsTaskResponseTypeDef",
    {
        "taskSummary": DetectMitigationActionsTaskSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListDetectMitigationActionsTasksResponseTypeDef = TypedDict(
    "ListDetectMitigationActionsTasksResponseTypeDef",
    {
        "tasks": List[DetectMitigationActionsTaskSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeAuditFindingResponseTypeDef = TypedDict(
    "DescribeAuditFindingResponseTypeDef",
    {
        "finding": AuditFindingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAuditFindingsResponseTypeDef = TypedDict(
    "ListAuditFindingsResponseTypeDef",
    {
        "findings": List[AuditFindingTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TopicRulePayloadTypeDef = TypedDict(
    "TopicRulePayloadTypeDef",
    {
        "sql": str,
        "actions": Sequence[ActionTypeDef],
        "description": NotRequired[str],
        "ruleDisabled": NotRequired[bool],
        "awsIotSqlVersion": NotRequired[str],
        "errorAction": NotRequired[ActionTypeDef],
    },
)
TopicRuleTypeDef = TypedDict(
    "TopicRuleTypeDef",
    {
        "ruleName": NotRequired[str],
        "sql": NotRequired[str],
        "description": NotRequired[str],
        "createdAt": NotRequired[datetime],
        "actions": NotRequired[List[ActionTypeDef]],
        "ruleDisabled": NotRequired[bool],
        "awsIotSqlVersion": NotRequired[str],
        "errorAction": NotRequired[ActionTypeDef],
    },
)
CreateOTAUpdateRequestRequestTypeDef = TypedDict(
    "CreateOTAUpdateRequestRequestTypeDef",
    {
        "otaUpdateId": str,
        "targets": Sequence[str],
        "files": Sequence[OTAUpdateFileTypeDef],
        "roleArn": str,
        "description": NotRequired[str],
        "protocols": NotRequired[Sequence[ProtocolType]],
        "targetSelection": NotRequired[TargetSelectionType],
        "awsJobExecutionsRolloutConfig": NotRequired[AwsJobExecutionsRolloutConfigTypeDef],
        "awsJobPresignedUrlConfig": NotRequired[AwsJobPresignedUrlConfigTypeDef],
        "awsJobAbortConfig": NotRequired[AwsJobAbortConfigTypeDef],
        "awsJobTimeoutConfig": NotRequired[AwsJobTimeoutConfigTypeDef],
        "additionalParameters": NotRequired[Mapping[str, str]],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
OTAUpdateInfoTypeDef = TypedDict(
    "OTAUpdateInfoTypeDef",
    {
        "otaUpdateId": NotRequired[str],
        "otaUpdateArn": NotRequired[str],
        "creationDate": NotRequired[datetime],
        "lastModifiedDate": NotRequired[datetime],
        "description": NotRequired[str],
        "targets": NotRequired[List[str]],
        "protocols": NotRequired[List[ProtocolType]],
        "awsJobExecutionsRolloutConfig": NotRequired[AwsJobExecutionsRolloutConfigTypeDef],
        "awsJobPresignedUrlConfig": NotRequired[AwsJobPresignedUrlConfigTypeDef],
        "targetSelection": NotRequired[TargetSelectionType],
        "otaUpdateFiles": NotRequired[List[OTAUpdateFileTypeDef]],
        "otaUpdateStatus": NotRequired[OTAUpdateStatusType],
        "awsIotJobId": NotRequired[str],
        "awsIotJobArn": NotRequired[str],
        "errorInfo": NotRequired[ErrorInfoTypeDef],
        "additionalParameters": NotRequired[Dict[str, str]],
    },
)
CreateTopicRuleRequestRequestTypeDef = TypedDict(
    "CreateTopicRuleRequestRequestTypeDef",
    {
        "ruleName": str,
        "topicRulePayload": TopicRulePayloadTypeDef,
        "tags": NotRequired[str],
    },
)
ReplaceTopicRuleRequestRequestTypeDef = TypedDict(
    "ReplaceTopicRuleRequestRequestTypeDef",
    {
        "ruleName": str,
        "topicRulePayload": TopicRulePayloadTypeDef,
    },
)
GetTopicRuleResponseTypeDef = TypedDict(
    "GetTopicRuleResponseTypeDef",
    {
        "ruleArn": str,
        "rule": TopicRuleTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetOTAUpdateResponseTypeDef = TypedDict(
    "GetOTAUpdateResponseTypeDef",
    {
        "otaUpdateInfo": OTAUpdateInfoTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
