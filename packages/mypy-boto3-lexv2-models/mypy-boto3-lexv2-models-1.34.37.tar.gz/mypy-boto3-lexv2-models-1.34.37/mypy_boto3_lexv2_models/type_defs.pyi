"""
Type annotations for lexv2-models service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_lexv2_models/type_defs/)

Usage::

    ```python
    from mypy_boto3_lexv2_models.type_defs import ActiveContextTypeDef

    data: ActiveContextTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Mapping, Sequence, Union

from .literals import (
    AggregatedUtterancesFilterOperatorType,
    AggregatedUtterancesSortAttributeType,
    AnalyticsBinByNameType,
    AnalyticsCommonFilterNameType,
    AnalyticsFilterOperatorType,
    AnalyticsIntentFieldType,
    AnalyticsIntentFilterNameType,
    AnalyticsIntentMetricNameType,
    AnalyticsIntentStageFieldType,
    AnalyticsIntentStageFilterNameType,
    AnalyticsIntentStageMetricNameType,
    AnalyticsIntervalType,
    AnalyticsMetricStatisticType,
    AnalyticsModalityType,
    AnalyticsNodeTypeType,
    AnalyticsSessionFieldType,
    AnalyticsSessionFilterNameType,
    AnalyticsSessionMetricNameType,
    AnalyticsSessionSortByNameType,
    AnalyticsSortOrderType,
    AnalyticsUtteranceFieldType,
    AnalyticsUtteranceFilterNameType,
    AnalyticsUtteranceMetricNameType,
    AssociatedTranscriptFilterNameType,
    BotAliasReplicationStatusType,
    BotAliasStatusType,
    BotFilterNameType,
    BotFilterOperatorType,
    BotLocaleFilterOperatorType,
    BotLocaleStatusType,
    BotRecommendationStatusType,
    BotReplicaStatusType,
    BotStatusType,
    BotTypeType,
    BotVersionReplicationStatusType,
    ConversationEndStateType,
    ConversationLogsInputModeFilterType,
    CustomVocabularyStatusType,
    DialogActionTypeType,
    EffectType,
    ErrorCodeType,
    ExportFilterOperatorType,
    ExportStatusType,
    GenerationSortByAttributeType,
    GenerationStatusType,
    ImportExportFileFormatType,
    ImportFilterOperatorType,
    ImportResourceTypeType,
    ImportStatusType,
    IntentFilterOperatorType,
    IntentSortAttributeType,
    IntentStateType,
    MergeStrategyType,
    MessageSelectionStrategyType,
    ObfuscationSettingTypeType,
    PromptAttemptType,
    SearchOrderType,
    SlotConstraintType,
    SlotFilterOperatorType,
    SlotResolutionStrategyType,
    SlotShapeType,
    SlotSortAttributeType,
    SlotTypeCategoryType,
    SlotTypeFilterNameType,
    SlotTypeFilterOperatorType,
    SlotTypeSortAttributeType,
    SlotValueResolutionStrategyType,
    SortOrderType,
    TestExecutionApiModeType,
    TestExecutionModalityType,
    TestExecutionSortAttributeType,
    TestExecutionStatusType,
    TestResultMatchStatusType,
    TestResultTypeFilterType,
    TestSetDiscrepancyReportStatusType,
    TestSetGenerationStatusType,
    TestSetModalityType,
    TestSetSortAttributeType,
    TestSetStatusType,
    TimeDimensionType,
    UtteranceContentTypeType,
    VoiceEngineType,
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
    "ActiveContextTypeDef",
    "AdvancedRecognitionSettingTypeDef",
    "ExecutionErrorDetailsTypeDef",
    "AgentTurnSpecificationTypeDef",
    "AggregatedUtterancesFilterTypeDef",
    "AggregatedUtterancesSortByTypeDef",
    "AggregatedUtterancesSummaryTypeDef",
    "AllowedInputTypesTypeDef",
    "AnalyticsBinBySpecificationTypeDef",
    "AnalyticsBinKeyTypeDef",
    "AnalyticsIntentFilterTypeDef",
    "AnalyticsIntentGroupByKeyTypeDef",
    "AnalyticsIntentGroupBySpecificationTypeDef",
    "AnalyticsIntentMetricResultTypeDef",
    "AnalyticsIntentMetricTypeDef",
    "AnalyticsIntentNodeSummaryTypeDef",
    "AnalyticsIntentStageFilterTypeDef",
    "AnalyticsIntentStageGroupByKeyTypeDef",
    "AnalyticsIntentStageGroupBySpecificationTypeDef",
    "AnalyticsIntentStageMetricResultTypeDef",
    "AnalyticsIntentStageMetricTypeDef",
    "AnalyticsPathFilterTypeDef",
    "AnalyticsSessionFilterTypeDef",
    "AnalyticsSessionGroupByKeyTypeDef",
    "AnalyticsSessionGroupBySpecificationTypeDef",
    "AnalyticsSessionMetricResultTypeDef",
    "AnalyticsSessionMetricTypeDef",
    "AnalyticsUtteranceAttributeResultTypeDef",
    "AnalyticsUtteranceAttributeTypeDef",
    "AnalyticsUtteranceFilterTypeDef",
    "AnalyticsUtteranceGroupByKeyTypeDef",
    "AnalyticsUtteranceGroupBySpecificationTypeDef",
    "AnalyticsUtteranceMetricResultTypeDef",
    "AnalyticsUtteranceMetricTypeDef",
    "AssociatedTranscriptFilterTypeDef",
    "AssociatedTranscriptTypeDef",
    "AudioSpecificationTypeDef",
    "DTMFSpecificationTypeDef",
    "S3BucketLogDestinationTypeDef",
    "NewCustomVocabularyItemTypeDef",
    "CustomVocabularyItemTypeDef",
    "FailedCustomVocabularyItemTypeDef",
    "ResponseMetadataTypeDef",
    "CustomVocabularyEntryIdTypeDef",
    "BedrockModelSpecificationTypeDef",
    "BotAliasHistoryEventTypeDef",
    "BotAliasReplicaSummaryTypeDef",
    "BotAliasSummaryTypeDef",
    "BotAliasTestExecutionTargetTypeDef",
    "BotExportSpecificationTypeDef",
    "BotFilterTypeDef",
    "DataPrivacyTypeDef",
    "BotLocaleExportSpecificationTypeDef",
    "BotLocaleFilterTypeDef",
    "BotLocaleHistoryEventTypeDef",
    "VoiceSettingsTypeDef",
    "BotLocaleSortByTypeDef",
    "BotLocaleSummaryTypeDef",
    "BotMemberTypeDef",
    "IntentStatisticsTypeDef",
    "SlotTypeStatisticsTypeDef",
    "BotRecommendationSummaryTypeDef",
    "BotReplicaSummaryTypeDef",
    "BotSortByTypeDef",
    "BotSummaryTypeDef",
    "BotVersionLocaleDetailsTypeDef",
    "BotVersionReplicaSortByTypeDef",
    "BotVersionReplicaSummaryTypeDef",
    "BotVersionSortByTypeDef",
    "BotVersionSummaryTypeDef",
    "BuildBotLocaleRequestRequestTypeDef",
    "BuiltInIntentSortByTypeDef",
    "BuiltInIntentSummaryTypeDef",
    "BuiltInSlotTypeSortByTypeDef",
    "BuiltInSlotTypeSummaryTypeDef",
    "ButtonTypeDef",
    "CloudWatchLogGroupLogDestinationTypeDef",
    "LambdaCodeHookTypeDef",
    "SubSlotTypeCompositionTypeDef",
    "ConditionTypeDef",
    "ConversationLevelIntentClassificationResultItemTypeDef",
    "ConversationLevelResultDetailTypeDef",
    "ConversationLevelSlotResolutionResultItemTypeDef",
    "ConversationLevelTestResultsFilterByTypeDef",
    "ConversationLogsDataSourceFilterByTypeDef",
    "SentimentAnalysisSettingsTypeDef",
    "CreateBotReplicaRequestRequestTypeDef",
    "DialogCodeHookSettingsTypeDef",
    "InputContextTypeDef",
    "KendraConfigurationTypeDef",
    "OutputContextTypeDef",
    "SampleUtteranceTypeDef",
    "CreateResourcePolicyRequestRequestTypeDef",
    "PrincipalTypeDef",
    "MultipleValuesSettingTypeDef",
    "ObfuscationSettingTypeDef",
    "CustomPayloadTypeDef",
    "CustomVocabularyExportSpecificationTypeDef",
    "CustomVocabularyImportSpecificationTypeDef",
    "DateRangeFilterTypeDef",
    "DeleteBotAliasRequestRequestTypeDef",
    "DeleteBotLocaleRequestRequestTypeDef",
    "DeleteBotReplicaRequestRequestTypeDef",
    "DeleteBotRequestRequestTypeDef",
    "DeleteBotVersionRequestRequestTypeDef",
    "DeleteCustomVocabularyRequestRequestTypeDef",
    "DeleteExportRequestRequestTypeDef",
    "DeleteImportRequestRequestTypeDef",
    "DeleteIntentRequestRequestTypeDef",
    "DeleteResourcePolicyRequestRequestTypeDef",
    "DeleteResourcePolicyStatementRequestRequestTypeDef",
    "DeleteSlotRequestRequestTypeDef",
    "DeleteSlotTypeRequestRequestTypeDef",
    "DeleteTestSetRequestRequestTypeDef",
    "DeleteUtterancesRequestRequestTypeDef",
    "WaiterConfigTypeDef",
    "DescribeBotAliasRequestRequestTypeDef",
    "ParentBotNetworkTypeDef",
    "DescribeBotLocaleRequestRequestTypeDef",
    "DescribeBotRecommendationRequestRequestTypeDef",
    "EncryptionSettingTypeDef",
    "DescribeBotReplicaRequestRequestTypeDef",
    "DescribeBotRequestRequestTypeDef",
    "DescribeBotResourceGenerationRequestRequestTypeDef",
    "DescribeBotVersionRequestRequestTypeDef",
    "DescribeCustomVocabularyMetadataRequestRequestTypeDef",
    "DescribeExportRequestRequestTypeDef",
    "DescribeImportRequestRequestTypeDef",
    "DescribeIntentRequestRequestTypeDef",
    "SlotPriorityTypeDef",
    "DescribeResourcePolicyRequestRequestTypeDef",
    "DescribeSlotRequestRequestTypeDef",
    "DescribeSlotTypeRequestRequestTypeDef",
    "DescribeTestExecutionRequestRequestTypeDef",
    "DescribeTestSetDiscrepancyReportRequestRequestTypeDef",
    "DescribeTestSetGenerationRequestRequestTypeDef",
    "TestSetStorageLocationTypeDef",
    "DescribeTestSetRequestRequestTypeDef",
    "DialogActionTypeDef",
    "IntentOverrideTypeDef",
    "ElicitationCodeHookInvocationSettingTypeDef",
    "ExportFilterTypeDef",
    "TestSetExportSpecificationTypeDef",
    "ExportSortByTypeDef",
    "GenerateBotElementRequestRequestTypeDef",
    "GenerationSortByTypeDef",
    "GenerationSummaryTypeDef",
    "GetTestExecutionArtifactsUrlRequestRequestTypeDef",
    "GrammarSlotTypeSourceTypeDef",
    "ImportFilterTypeDef",
    "ImportSortByTypeDef",
    "ImportSummaryTypeDef",
    "RuntimeHintsTypeDef",
    "IntentClassificationTestResultItemCountsTypeDef",
    "IntentFilterTypeDef",
    "IntentSortByTypeDef",
    "InvokedIntentSampleTypeDef",
    "ListBotAliasReplicasRequestRequestTypeDef",
    "ListBotAliasesRequestRequestTypeDef",
    "ListBotRecommendationsRequestRequestTypeDef",
    "ListBotReplicasRequestRequestTypeDef",
    "ListCustomVocabularyItemsRequestRequestTypeDef",
    "TimestampTypeDef",
    "ListRecommendedIntentsRequestRequestTypeDef",
    "RecommendedIntentSummaryTypeDef",
    "SessionDataSortByTypeDef",
    "SlotTypeFilterTypeDef",
    "SlotTypeSortByTypeDef",
    "SlotTypeSummaryTypeDef",
    "SlotFilterTypeDef",
    "SlotSortByTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "TestExecutionSortByTypeDef",
    "ListTestSetRecordsRequestRequestTypeDef",
    "TestSetSortByTypeDef",
    "UtteranceDataSortByTypeDef",
    "PlainTextMessageTypeDef",
    "SSMLMessageTypeDef",
    "OverallTestResultItemTypeDef",
    "PathFormatTypeDef",
    "TextInputSpecificationTypeDef",
    "RelativeAggregationDurationTypeDef",
    "RuntimeHintValueTypeDef",
    "SampleValueTypeDef",
    "SlotDefaultValueTypeDef",
    "SlotResolutionSettingTypeDef",
    "SlotResolutionTestResultItemCountsTypeDef",
    "SlotValueTypeDef",
    "SlotValueRegexFilterTypeDef",
    "StartBotResourceGenerationRequestRequestTypeDef",
    "StopBotRecommendationRequestRequestTypeDef",
    "TagResourceRequestRequestTypeDef",
    "TestSetIntentDiscrepancyItemTypeDef",
    "TestSetSlotDiscrepancyItemTypeDef",
    "TestSetDiscrepancyReportBotAliasTargetTypeDef",
    "TestSetImportInputLocationTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateExportRequestRequestTypeDef",
    "UpdateResourcePolicyRequestRequestTypeDef",
    "UpdateTestSetRequestRequestTypeDef",
    "UserTurnIntentOutputTypeDef",
    "UserTurnSlotOutputTypeDef",
    "UtteranceAudioInputSpecificationTypeDef",
    "AgentTurnResultTypeDef",
    "AnalyticsIntentResultTypeDef",
    "AnalyticsIntentStageResultTypeDef",
    "AnalyticsSessionResultTypeDef",
    "AnalyticsUtteranceResultTypeDef",
    "SearchAssociatedTranscriptsRequestRequestTypeDef",
    "AudioAndDTMFInputSpecificationTypeDef",
    "AudioLogDestinationTypeDef",
    "BatchCreateCustomVocabularyItemRequestRequestTypeDef",
    "BatchUpdateCustomVocabularyItemRequestRequestTypeDef",
    "BatchCreateCustomVocabularyItemResponseTypeDef",
    "BatchDeleteCustomVocabularyItemResponseTypeDef",
    "BatchUpdateCustomVocabularyItemResponseTypeDef",
    "BuildBotLocaleResponseTypeDef",
    "CreateBotReplicaResponseTypeDef",
    "CreateResourcePolicyResponseTypeDef",
    "CreateResourcePolicyStatementResponseTypeDef",
    "CreateUploadUrlResponseTypeDef",
    "DeleteBotAliasResponseTypeDef",
    "DeleteBotLocaleResponseTypeDef",
    "DeleteBotReplicaResponseTypeDef",
    "DeleteBotResponseTypeDef",
    "DeleteBotVersionResponseTypeDef",
    "DeleteCustomVocabularyResponseTypeDef",
    "DeleteExportResponseTypeDef",
    "DeleteImportResponseTypeDef",
    "DeleteResourcePolicyResponseTypeDef",
    "DeleteResourcePolicyStatementResponseTypeDef",
    "DescribeBotReplicaResponseTypeDef",
    "DescribeBotResourceGenerationResponseTypeDef",
    "DescribeCustomVocabularyMetadataResponseTypeDef",
    "DescribeResourcePolicyResponseTypeDef",
    "EmptyResponseMetadataTypeDef",
    "GetTestExecutionArtifactsUrlResponseTypeDef",
    "ListCustomVocabularyItemsResponseTypeDef",
    "ListIntentPathsResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "SearchAssociatedTranscriptsResponseTypeDef",
    "StartBotResourceGenerationResponseTypeDef",
    "StopBotRecommendationResponseTypeDef",
    "UpdateResourcePolicyResponseTypeDef",
    "BatchDeleteCustomVocabularyItemRequestRequestTypeDef",
    "DescriptiveBotBuilderSpecificationTypeDef",
    "SampleUtteranceGenerationSpecificationTypeDef",
    "SlotResolutionImprovementSpecificationTypeDef",
    "ListBotAliasReplicasResponseTypeDef",
    "ListBotAliasesResponseTypeDef",
    "TestExecutionTargetTypeDef",
    "BotImportSpecificationTypeDef",
    "BotLocaleImportSpecificationTypeDef",
    "ListBotLocalesRequestRequestTypeDef",
    "ListBotLocalesResponseTypeDef",
    "CreateBotRequestRequestTypeDef",
    "CreateBotResponseTypeDef",
    "DescribeBotResponseTypeDef",
    "UpdateBotRequestRequestTypeDef",
    "UpdateBotResponseTypeDef",
    "BotRecommendationResultStatisticsTypeDef",
    "ListBotRecommendationsResponseTypeDef",
    "ListBotReplicasResponseTypeDef",
    "ListBotsRequestRequestTypeDef",
    "ListBotsResponseTypeDef",
    "CreateBotVersionRequestRequestTypeDef",
    "CreateBotVersionResponseTypeDef",
    "ListBotVersionReplicasRequestRequestTypeDef",
    "ListBotVersionReplicasResponseTypeDef",
    "ListBotVersionsRequestRequestTypeDef",
    "ListBotVersionsResponseTypeDef",
    "ListBuiltInIntentsRequestRequestTypeDef",
    "ListBuiltInIntentsResponseTypeDef",
    "ListBuiltInSlotTypesRequestRequestTypeDef",
    "ListBuiltInSlotTypesResponseTypeDef",
    "ImageResponseCardTypeDef",
    "TextLogDestinationTypeDef",
    "CodeHookSpecificationTypeDef",
    "CompositeSlotTypeSettingTypeDef",
    "ConversationLevelTestResultItemTypeDef",
    "TestExecutionResultFilterByTypeDef",
    "ConversationLogsDataSourceTypeDef",
    "IntentSummaryTypeDef",
    "GenerateBotElementResponseTypeDef",
    "CreateResourcePolicyStatementRequestRequestTypeDef",
    "LexTranscriptFilterTypeDef",
    "DescribeBotAliasRequestBotAliasAvailableWaitTypeDef",
    "DescribeBotLocaleRequestBotLocaleBuiltWaitTypeDef",
    "DescribeBotLocaleRequestBotLocaleCreatedWaitTypeDef",
    "DescribeBotLocaleRequestBotLocaleExpressTestingAvailableWaitTypeDef",
    "DescribeBotRequestBotAvailableWaitTypeDef",
    "DescribeBotVersionRequestBotVersionAvailableWaitTypeDef",
    "DescribeExportRequestBotExportCompletedWaitTypeDef",
    "DescribeImportRequestBotImportCompletedWaitTypeDef",
    "DescribeBotVersionResponseTypeDef",
    "UpdateBotRecommendationRequestRequestTypeDef",
    "DescribeTestSetResponseTypeDef",
    "TestSetSummaryTypeDef",
    "UpdateTestSetResponseTypeDef",
    "DialogStateTypeDef",
    "ExportResourceSpecificationTypeDef",
    "ListExportsRequestRequestTypeDef",
    "ListBotResourceGenerationsRequestRequestTypeDef",
    "ListBotResourceGenerationsResponseTypeDef",
    "GrammarSlotTypeSettingTypeDef",
    "ListImportsRequestRequestTypeDef",
    "ListImportsResponseTypeDef",
    "InputSessionStateSpecificationTypeDef",
    "IntentClassificationTestResultItemTypeDef",
    "ListIntentsRequestRequestTypeDef",
    "SessionSpecificationTypeDef",
    "ListIntentMetricsRequestRequestTypeDef",
    "ListIntentPathsRequestRequestTypeDef",
    "ListIntentStageMetricsRequestRequestTypeDef",
    "ListSessionMetricsRequestRequestTypeDef",
    "ListUtteranceMetricsRequestRequestTypeDef",
    "ListRecommendedIntentsResponseTypeDef",
    "ListSessionAnalyticsDataRequestRequestTypeDef",
    "ListSlotTypesRequestRequestTypeDef",
    "ListSlotTypesResponseTypeDef",
    "ListSlotsRequestRequestTypeDef",
    "ListTestExecutionsRequestRequestTypeDef",
    "ListTestSetsRequestRequestTypeDef",
    "ListUtteranceAnalyticsDataRequestRequestTypeDef",
    "OverallTestResultsTypeDef",
    "UtteranceAggregationDurationTypeDef",
    "RuntimeHintDetailsTypeDef",
    "SlotTypeValueTypeDef",
    "SlotDefaultValueSpecificationTypeDef",
    "SlotResolutionTestResultItemTypeDef",
    "SlotValueOverrideTypeDef",
    "SlotValueSelectionSettingTypeDef",
    "TestSetDiscrepancyErrorsTypeDef",
    "TestSetDiscrepancyReportResourceTargetTypeDef",
    "TestSetImportResourceSpecificationTypeDef",
    "UserTurnOutputSpecificationTypeDef",
    "UtteranceInputSpecificationTypeDef",
    "ListIntentMetricsResponseTypeDef",
    "ListIntentStageMetricsResponseTypeDef",
    "ListSessionMetricsResponseTypeDef",
    "ListUtteranceMetricsResponseTypeDef",
    "PromptAttemptSpecificationTypeDef",
    "AudioLogSettingTypeDef",
    "BuildtimeSettingsTypeDef",
    "RuntimeSettingsTypeDef",
    "DescribeTestExecutionResponseTypeDef",
    "StartTestExecutionRequestRequestTypeDef",
    "StartTestExecutionResponseTypeDef",
    "TestExecutionSummaryTypeDef",
    "BotRecommendationResultsTypeDef",
    "MessageTypeDef",
    "UtteranceBotResponseTypeDef",
    "TextLogSettingTypeDef",
    "BotAliasLocaleSettingsTypeDef",
    "ConversationLevelTestResultsTypeDef",
    "ListTestExecutionResultItemsRequestRequestTypeDef",
    "TestSetGenerationDataSourceTypeDef",
    "ListIntentsResponseTypeDef",
    "TranscriptFilterTypeDef",
    "ListTestSetsResponseTypeDef",
    "CreateExportRequestRequestTypeDef",
    "CreateExportResponseTypeDef",
    "DescribeExportResponseTypeDef",
    "ExportSummaryTypeDef",
    "UpdateExportResponseTypeDef",
    "ExternalSourceSettingTypeDef",
    "IntentClassificationTestResultsTypeDef",
    "ListSessionAnalyticsDataResponseTypeDef",
    "ListAggregatedUtterancesRequestRequestTypeDef",
    "ListAggregatedUtterancesResponseTypeDef",
    "IntentLevelSlotResolutionTestResultItemTypeDef",
    "CreateTestSetDiscrepancyReportRequestRequestTypeDef",
    "CreateTestSetDiscrepancyReportResponseTypeDef",
    "DescribeTestSetDiscrepancyReportResponseTypeDef",
    "ImportResourceSpecificationTypeDef",
    "UserTurnInputSpecificationTypeDef",
    "GenerativeAISettingsTypeDef",
    "ListTestExecutionsResponseTypeDef",
    "MessageGroupTypeDef",
    "UtteranceSpecificationTypeDef",
    "ConversationLogSettingsTypeDef",
    "DescribeTestSetGenerationResponseTypeDef",
    "StartTestSetGenerationRequestRequestTypeDef",
    "StartTestSetGenerationResponseTypeDef",
    "S3BucketTranscriptSourceTypeDef",
    "ListExportsResponseTypeDef",
    "CreateSlotTypeRequestRequestTypeDef",
    "CreateSlotTypeResponseTypeDef",
    "DescribeSlotTypeResponseTypeDef",
    "UpdateSlotTypeRequestRequestTypeDef",
    "UpdateSlotTypeResponseTypeDef",
    "IntentLevelSlotResolutionTestResultsTypeDef",
    "DescribeImportResponseTypeDef",
    "StartImportRequestRequestTypeDef",
    "StartImportResponseTypeDef",
    "UserTurnResultTypeDef",
    "UserTurnSpecificationTypeDef",
    "CreateBotLocaleRequestRequestTypeDef",
    "CreateBotLocaleResponseTypeDef",
    "DescribeBotLocaleResponseTypeDef",
    "UpdateBotLocaleRequestRequestTypeDef",
    "UpdateBotLocaleResponseTypeDef",
    "FulfillmentStartResponseSpecificationTypeDef",
    "FulfillmentUpdateResponseSpecificationTypeDef",
    "PromptSpecificationTypeDef",
    "ResponseSpecificationTypeDef",
    "StillWaitingResponseSpecificationTypeDef",
    "ListUtteranceAnalyticsDataResponseTypeDef",
    "CreateBotAliasRequestRequestTypeDef",
    "CreateBotAliasResponseTypeDef",
    "DescribeBotAliasResponseTypeDef",
    "UpdateBotAliasRequestRequestTypeDef",
    "UpdateBotAliasResponseTypeDef",
    "TranscriptSourceSettingTypeDef",
    "TestSetTurnResultTypeDef",
    "TurnSpecificationTypeDef",
    "FulfillmentUpdatesSpecificationTypeDef",
    "SlotSummaryTypeDef",
    "ConditionalBranchTypeDef",
    "DefaultConditionalBranchTypeDef",
    "WaitAndContinueSpecificationTypeDef",
    "DescribeBotRecommendationResponseTypeDef",
    "StartBotRecommendationRequestRequestTypeDef",
    "StartBotRecommendationResponseTypeDef",
    "UpdateBotRecommendationResponseTypeDef",
    "UtteranceLevelTestResultItemTypeDef",
    "TestSetTurnRecordTypeDef",
    "ListSlotsResponseTypeDef",
    "ConditionalSpecificationTypeDef",
    "SubSlotValueElicitationSettingTypeDef",
    "UtteranceLevelTestResultsTypeDef",
    "ListTestSetRecordsResponseTypeDef",
    "IntentClosingSettingTypeDef",
    "PostDialogCodeHookInvocationSpecificationTypeDef",
    "PostFulfillmentStatusSpecificationTypeDef",
    "SpecificationsTypeDef",
    "TestExecutionResultItemsTypeDef",
    "DialogCodeHookInvocationSettingTypeDef",
    "FulfillmentCodeHookSettingsTypeDef",
    "SubSlotSettingTypeDef",
    "ListTestExecutionResultItemsResponseTypeDef",
    "InitialResponseSettingTypeDef",
    "IntentConfirmationSettingTypeDef",
    "SlotCaptureSettingTypeDef",
    "CreateIntentRequestRequestTypeDef",
    "CreateIntentResponseTypeDef",
    "DescribeIntentResponseTypeDef",
    "UpdateIntentRequestRequestTypeDef",
    "UpdateIntentResponseTypeDef",
    "SlotValueElicitationSettingTypeDef",
    "CreateSlotRequestRequestTypeDef",
    "CreateSlotResponseTypeDef",
    "DescribeSlotResponseTypeDef",
    "UpdateSlotRequestRequestTypeDef",
    "UpdateSlotResponseTypeDef",
)

ActiveContextTypeDef = TypedDict(
    "ActiveContextTypeDef",
    {
        "name": str,
    },
)
AdvancedRecognitionSettingTypeDef = TypedDict(
    "AdvancedRecognitionSettingTypeDef",
    {
        "audioRecognitionStrategy": NotRequired[Literal["UseSlotValuesAsCustomVocabulary"]],
    },
)
ExecutionErrorDetailsTypeDef = TypedDict(
    "ExecutionErrorDetailsTypeDef",
    {
        "errorCode": str,
        "errorMessage": str,
    },
)
AgentTurnSpecificationTypeDef = TypedDict(
    "AgentTurnSpecificationTypeDef",
    {
        "agentPrompt": str,
    },
)
AggregatedUtterancesFilterTypeDef = TypedDict(
    "AggregatedUtterancesFilterTypeDef",
    {
        "name": Literal["Utterance"],
        "values": Sequence[str],
        "operator": AggregatedUtterancesFilterOperatorType,
    },
)
AggregatedUtterancesSortByTypeDef = TypedDict(
    "AggregatedUtterancesSortByTypeDef",
    {
        "attribute": AggregatedUtterancesSortAttributeType,
        "order": SortOrderType,
    },
)
AggregatedUtterancesSummaryTypeDef = TypedDict(
    "AggregatedUtterancesSummaryTypeDef",
    {
        "utterance": NotRequired[str],
        "hitCount": NotRequired[int],
        "missedCount": NotRequired[int],
        "utteranceFirstRecordedInAggregationDuration": NotRequired[datetime],
        "utteranceLastRecordedInAggregationDuration": NotRequired[datetime],
        "containsDataFromDeletedResources": NotRequired[bool],
    },
)
AllowedInputTypesTypeDef = TypedDict(
    "AllowedInputTypesTypeDef",
    {
        "allowAudioInput": bool,
        "allowDTMFInput": bool,
    },
)
AnalyticsBinBySpecificationTypeDef = TypedDict(
    "AnalyticsBinBySpecificationTypeDef",
    {
        "name": AnalyticsBinByNameType,
        "interval": AnalyticsIntervalType,
        "order": NotRequired[AnalyticsSortOrderType],
    },
)
AnalyticsBinKeyTypeDef = TypedDict(
    "AnalyticsBinKeyTypeDef",
    {
        "name": NotRequired[AnalyticsBinByNameType],
        "value": NotRequired[int],
    },
)
AnalyticsIntentFilterTypeDef = TypedDict(
    "AnalyticsIntentFilterTypeDef",
    {
        "name": AnalyticsIntentFilterNameType,
        "operator": AnalyticsFilterOperatorType,
        "values": Sequence[str],
    },
)
AnalyticsIntentGroupByKeyTypeDef = TypedDict(
    "AnalyticsIntentGroupByKeyTypeDef",
    {
        "name": NotRequired[AnalyticsIntentFieldType],
        "value": NotRequired[str],
    },
)
AnalyticsIntentGroupBySpecificationTypeDef = TypedDict(
    "AnalyticsIntentGroupBySpecificationTypeDef",
    {
        "name": AnalyticsIntentFieldType,
    },
)
AnalyticsIntentMetricResultTypeDef = TypedDict(
    "AnalyticsIntentMetricResultTypeDef",
    {
        "name": NotRequired[AnalyticsIntentMetricNameType],
        "statistic": NotRequired[AnalyticsMetricStatisticType],
        "value": NotRequired[float],
    },
)
AnalyticsIntentMetricTypeDef = TypedDict(
    "AnalyticsIntentMetricTypeDef",
    {
        "name": AnalyticsIntentMetricNameType,
        "statistic": AnalyticsMetricStatisticType,
        "order": NotRequired[AnalyticsSortOrderType],
    },
)
AnalyticsIntentNodeSummaryTypeDef = TypedDict(
    "AnalyticsIntentNodeSummaryTypeDef",
    {
        "intentName": NotRequired[str],
        "intentPath": NotRequired[str],
        "intentCount": NotRequired[int],
        "intentLevel": NotRequired[int],
        "nodeType": NotRequired[AnalyticsNodeTypeType],
    },
)
AnalyticsIntentStageFilterTypeDef = TypedDict(
    "AnalyticsIntentStageFilterTypeDef",
    {
        "name": AnalyticsIntentStageFilterNameType,
        "operator": AnalyticsFilterOperatorType,
        "values": Sequence[str],
    },
)
AnalyticsIntentStageGroupByKeyTypeDef = TypedDict(
    "AnalyticsIntentStageGroupByKeyTypeDef",
    {
        "name": NotRequired[AnalyticsIntentStageFieldType],
        "value": NotRequired[str],
    },
)
AnalyticsIntentStageGroupBySpecificationTypeDef = TypedDict(
    "AnalyticsIntentStageGroupBySpecificationTypeDef",
    {
        "name": AnalyticsIntentStageFieldType,
    },
)
AnalyticsIntentStageMetricResultTypeDef = TypedDict(
    "AnalyticsIntentStageMetricResultTypeDef",
    {
        "name": NotRequired[AnalyticsIntentStageMetricNameType],
        "statistic": NotRequired[AnalyticsMetricStatisticType],
        "value": NotRequired[float],
    },
)
AnalyticsIntentStageMetricTypeDef = TypedDict(
    "AnalyticsIntentStageMetricTypeDef",
    {
        "name": AnalyticsIntentStageMetricNameType,
        "statistic": AnalyticsMetricStatisticType,
        "order": NotRequired[AnalyticsSortOrderType],
    },
)
AnalyticsPathFilterTypeDef = TypedDict(
    "AnalyticsPathFilterTypeDef",
    {
        "name": AnalyticsCommonFilterNameType,
        "operator": AnalyticsFilterOperatorType,
        "values": Sequence[str],
    },
)
AnalyticsSessionFilterTypeDef = TypedDict(
    "AnalyticsSessionFilterTypeDef",
    {
        "name": AnalyticsSessionFilterNameType,
        "operator": AnalyticsFilterOperatorType,
        "values": Sequence[str],
    },
)
AnalyticsSessionGroupByKeyTypeDef = TypedDict(
    "AnalyticsSessionGroupByKeyTypeDef",
    {
        "name": NotRequired[AnalyticsSessionFieldType],
        "value": NotRequired[str],
    },
)
AnalyticsSessionGroupBySpecificationTypeDef = TypedDict(
    "AnalyticsSessionGroupBySpecificationTypeDef",
    {
        "name": AnalyticsSessionFieldType,
    },
)
AnalyticsSessionMetricResultTypeDef = TypedDict(
    "AnalyticsSessionMetricResultTypeDef",
    {
        "name": NotRequired[AnalyticsSessionMetricNameType],
        "statistic": NotRequired[AnalyticsMetricStatisticType],
        "value": NotRequired[float],
    },
)
AnalyticsSessionMetricTypeDef = TypedDict(
    "AnalyticsSessionMetricTypeDef",
    {
        "name": AnalyticsSessionMetricNameType,
        "statistic": AnalyticsMetricStatisticType,
        "order": NotRequired[AnalyticsSortOrderType],
    },
)
AnalyticsUtteranceAttributeResultTypeDef = TypedDict(
    "AnalyticsUtteranceAttributeResultTypeDef",
    {
        "lastUsedIntent": NotRequired[str],
    },
)
AnalyticsUtteranceAttributeTypeDef = TypedDict(
    "AnalyticsUtteranceAttributeTypeDef",
    {
        "name": Literal["LastUsedIntent"],
    },
)
AnalyticsUtteranceFilterTypeDef = TypedDict(
    "AnalyticsUtteranceFilterTypeDef",
    {
        "name": AnalyticsUtteranceFilterNameType,
        "operator": AnalyticsFilterOperatorType,
        "values": Sequence[str],
    },
)
AnalyticsUtteranceGroupByKeyTypeDef = TypedDict(
    "AnalyticsUtteranceGroupByKeyTypeDef",
    {
        "name": NotRequired[AnalyticsUtteranceFieldType],
        "value": NotRequired[str],
    },
)
AnalyticsUtteranceGroupBySpecificationTypeDef = TypedDict(
    "AnalyticsUtteranceGroupBySpecificationTypeDef",
    {
        "name": AnalyticsUtteranceFieldType,
    },
)
AnalyticsUtteranceMetricResultTypeDef = TypedDict(
    "AnalyticsUtteranceMetricResultTypeDef",
    {
        "name": NotRequired[AnalyticsUtteranceMetricNameType],
        "statistic": NotRequired[AnalyticsMetricStatisticType],
        "value": NotRequired[float],
    },
)
AnalyticsUtteranceMetricTypeDef = TypedDict(
    "AnalyticsUtteranceMetricTypeDef",
    {
        "name": AnalyticsUtteranceMetricNameType,
        "statistic": AnalyticsMetricStatisticType,
        "order": NotRequired[AnalyticsSortOrderType],
    },
)
AssociatedTranscriptFilterTypeDef = TypedDict(
    "AssociatedTranscriptFilterTypeDef",
    {
        "name": AssociatedTranscriptFilterNameType,
        "values": Sequence[str],
    },
)
AssociatedTranscriptTypeDef = TypedDict(
    "AssociatedTranscriptTypeDef",
    {
        "transcript": NotRequired[str],
    },
)
AudioSpecificationTypeDef = TypedDict(
    "AudioSpecificationTypeDef",
    {
        "maxLengthMs": int,
        "endTimeoutMs": int,
    },
)
DTMFSpecificationTypeDef = TypedDict(
    "DTMFSpecificationTypeDef",
    {
        "maxLength": int,
        "endTimeoutMs": int,
        "deletionCharacter": str,
        "endCharacter": str,
    },
)
S3BucketLogDestinationTypeDef = TypedDict(
    "S3BucketLogDestinationTypeDef",
    {
        "s3BucketArn": str,
        "logPrefix": str,
        "kmsKeyArn": NotRequired[str],
    },
)
NewCustomVocabularyItemTypeDef = TypedDict(
    "NewCustomVocabularyItemTypeDef",
    {
        "phrase": str,
        "weight": NotRequired[int],
        "displayAs": NotRequired[str],
    },
)
CustomVocabularyItemTypeDef = TypedDict(
    "CustomVocabularyItemTypeDef",
    {
        "itemId": str,
        "phrase": str,
        "weight": NotRequired[int],
        "displayAs": NotRequired[str],
    },
)
FailedCustomVocabularyItemTypeDef = TypedDict(
    "FailedCustomVocabularyItemTypeDef",
    {
        "itemId": NotRequired[str],
        "errorMessage": NotRequired[str],
        "errorCode": NotRequired[ErrorCodeType],
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
CustomVocabularyEntryIdTypeDef = TypedDict(
    "CustomVocabularyEntryIdTypeDef",
    {
        "itemId": str,
    },
)
BedrockModelSpecificationTypeDef = TypedDict(
    "BedrockModelSpecificationTypeDef",
    {
        "modelArn": str,
    },
)
BotAliasHistoryEventTypeDef = TypedDict(
    "BotAliasHistoryEventTypeDef",
    {
        "botVersion": NotRequired[str],
        "startDate": NotRequired[datetime],
        "endDate": NotRequired[datetime],
    },
)
BotAliasReplicaSummaryTypeDef = TypedDict(
    "BotAliasReplicaSummaryTypeDef",
    {
        "botAliasId": NotRequired[str],
        "botAliasReplicationStatus": NotRequired[BotAliasReplicationStatusType],
        "botVersion": NotRequired[str],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
        "failureReasons": NotRequired[List[str]],
    },
)
BotAliasSummaryTypeDef = TypedDict(
    "BotAliasSummaryTypeDef",
    {
        "botAliasId": NotRequired[str],
        "botAliasName": NotRequired[str],
        "description": NotRequired[str],
        "botVersion": NotRequired[str],
        "botAliasStatus": NotRequired[BotAliasStatusType],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
BotAliasTestExecutionTargetTypeDef = TypedDict(
    "BotAliasTestExecutionTargetTypeDef",
    {
        "botId": str,
        "botAliasId": str,
        "localeId": str,
    },
)
BotExportSpecificationTypeDef = TypedDict(
    "BotExportSpecificationTypeDef",
    {
        "botId": str,
        "botVersion": str,
    },
)
BotFilterTypeDef = TypedDict(
    "BotFilterTypeDef",
    {
        "name": BotFilterNameType,
        "values": Sequence[str],
        "operator": BotFilterOperatorType,
    },
)
DataPrivacyTypeDef = TypedDict(
    "DataPrivacyTypeDef",
    {
        "childDirected": bool,
    },
)
BotLocaleExportSpecificationTypeDef = TypedDict(
    "BotLocaleExportSpecificationTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
BotLocaleFilterTypeDef = TypedDict(
    "BotLocaleFilterTypeDef",
    {
        "name": Literal["BotLocaleName"],
        "values": Sequence[str],
        "operator": BotLocaleFilterOperatorType,
    },
)
BotLocaleHistoryEventTypeDef = TypedDict(
    "BotLocaleHistoryEventTypeDef",
    {
        "event": str,
        "eventDate": datetime,
    },
)
VoiceSettingsTypeDef = TypedDict(
    "VoiceSettingsTypeDef",
    {
        "voiceId": str,
        "engine": NotRequired[VoiceEngineType],
    },
)
BotLocaleSortByTypeDef = TypedDict(
    "BotLocaleSortByTypeDef",
    {
        "attribute": Literal["BotLocaleName"],
        "order": SortOrderType,
    },
)
BotLocaleSummaryTypeDef = TypedDict(
    "BotLocaleSummaryTypeDef",
    {
        "localeId": NotRequired[str],
        "localeName": NotRequired[str],
        "description": NotRequired[str],
        "botLocaleStatus": NotRequired[BotLocaleStatusType],
        "lastUpdatedDateTime": NotRequired[datetime],
        "lastBuildSubmittedDateTime": NotRequired[datetime],
    },
)
BotMemberTypeDef = TypedDict(
    "BotMemberTypeDef",
    {
        "botMemberId": str,
        "botMemberName": str,
        "botMemberAliasId": str,
        "botMemberAliasName": str,
        "botMemberVersion": str,
    },
)
IntentStatisticsTypeDef = TypedDict(
    "IntentStatisticsTypeDef",
    {
        "discoveredIntentCount": NotRequired[int],
    },
)
SlotTypeStatisticsTypeDef = TypedDict(
    "SlotTypeStatisticsTypeDef",
    {
        "discoveredSlotTypeCount": NotRequired[int],
    },
)
BotRecommendationSummaryTypeDef = TypedDict(
    "BotRecommendationSummaryTypeDef",
    {
        "botRecommendationStatus": BotRecommendationStatusType,
        "botRecommendationId": str,
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
BotReplicaSummaryTypeDef = TypedDict(
    "BotReplicaSummaryTypeDef",
    {
        "replicaRegion": NotRequired[str],
        "creationDateTime": NotRequired[datetime],
        "botReplicaStatus": NotRequired[BotReplicaStatusType],
        "failureReasons": NotRequired[List[str]],
    },
)
BotSortByTypeDef = TypedDict(
    "BotSortByTypeDef",
    {
        "attribute": Literal["BotName"],
        "order": SortOrderType,
    },
)
BotSummaryTypeDef = TypedDict(
    "BotSummaryTypeDef",
    {
        "botId": NotRequired[str],
        "botName": NotRequired[str],
        "description": NotRequired[str],
        "botStatus": NotRequired[BotStatusType],
        "latestBotVersion": NotRequired[str],
        "lastUpdatedDateTime": NotRequired[datetime],
        "botType": NotRequired[BotTypeType],
    },
)
BotVersionLocaleDetailsTypeDef = TypedDict(
    "BotVersionLocaleDetailsTypeDef",
    {
        "sourceBotVersion": str,
    },
)
BotVersionReplicaSortByTypeDef = TypedDict(
    "BotVersionReplicaSortByTypeDef",
    {
        "attribute": Literal["BotVersion"],
        "order": SortOrderType,
    },
)
BotVersionReplicaSummaryTypeDef = TypedDict(
    "BotVersionReplicaSummaryTypeDef",
    {
        "botVersion": NotRequired[str],
        "botVersionReplicationStatus": NotRequired[BotVersionReplicationStatusType],
        "creationDateTime": NotRequired[datetime],
        "failureReasons": NotRequired[List[str]],
    },
)
BotVersionSortByTypeDef = TypedDict(
    "BotVersionSortByTypeDef",
    {
        "attribute": Literal["BotVersion"],
        "order": SortOrderType,
    },
)
BotVersionSummaryTypeDef = TypedDict(
    "BotVersionSummaryTypeDef",
    {
        "botName": NotRequired[str],
        "botVersion": NotRequired[str],
        "description": NotRequired[str],
        "botStatus": NotRequired[BotStatusType],
        "creationDateTime": NotRequired[datetime],
    },
)
BuildBotLocaleRequestRequestTypeDef = TypedDict(
    "BuildBotLocaleRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
BuiltInIntentSortByTypeDef = TypedDict(
    "BuiltInIntentSortByTypeDef",
    {
        "attribute": Literal["IntentSignature"],
        "order": SortOrderType,
    },
)
BuiltInIntentSummaryTypeDef = TypedDict(
    "BuiltInIntentSummaryTypeDef",
    {
        "intentSignature": NotRequired[str],
        "description": NotRequired[str],
    },
)
BuiltInSlotTypeSortByTypeDef = TypedDict(
    "BuiltInSlotTypeSortByTypeDef",
    {
        "attribute": Literal["SlotTypeSignature"],
        "order": SortOrderType,
    },
)
BuiltInSlotTypeSummaryTypeDef = TypedDict(
    "BuiltInSlotTypeSummaryTypeDef",
    {
        "slotTypeSignature": NotRequired[str],
        "description": NotRequired[str],
    },
)
ButtonTypeDef = TypedDict(
    "ButtonTypeDef",
    {
        "text": str,
        "value": str,
    },
)
CloudWatchLogGroupLogDestinationTypeDef = TypedDict(
    "CloudWatchLogGroupLogDestinationTypeDef",
    {
        "cloudWatchLogGroupArn": str,
        "logPrefix": str,
    },
)
LambdaCodeHookTypeDef = TypedDict(
    "LambdaCodeHookTypeDef",
    {
        "lambdaARN": str,
        "codeHookInterfaceVersion": str,
    },
)
SubSlotTypeCompositionTypeDef = TypedDict(
    "SubSlotTypeCompositionTypeDef",
    {
        "name": str,
        "slotTypeId": str,
    },
)
ConditionTypeDef = TypedDict(
    "ConditionTypeDef",
    {
        "expressionString": str,
    },
)
ConversationLevelIntentClassificationResultItemTypeDef = TypedDict(
    "ConversationLevelIntentClassificationResultItemTypeDef",
    {
        "intentName": str,
        "matchResult": TestResultMatchStatusType,
    },
)
ConversationLevelResultDetailTypeDef = TypedDict(
    "ConversationLevelResultDetailTypeDef",
    {
        "endToEndResult": TestResultMatchStatusType,
        "speechTranscriptionResult": NotRequired[TestResultMatchStatusType],
    },
)
ConversationLevelSlotResolutionResultItemTypeDef = TypedDict(
    "ConversationLevelSlotResolutionResultItemTypeDef",
    {
        "intentName": str,
        "slotName": str,
        "matchResult": TestResultMatchStatusType,
    },
)
ConversationLevelTestResultsFilterByTypeDef = TypedDict(
    "ConversationLevelTestResultsFilterByTypeDef",
    {
        "endToEndResult": NotRequired[TestResultMatchStatusType],
    },
)
ConversationLogsDataSourceFilterByTypeDef = TypedDict(
    "ConversationLogsDataSourceFilterByTypeDef",
    {
        "startTime": datetime,
        "endTime": datetime,
        "inputMode": ConversationLogsInputModeFilterType,
    },
)
SentimentAnalysisSettingsTypeDef = TypedDict(
    "SentimentAnalysisSettingsTypeDef",
    {
        "detectSentiment": bool,
    },
)
CreateBotReplicaRequestRequestTypeDef = TypedDict(
    "CreateBotReplicaRequestRequestTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
    },
)
DialogCodeHookSettingsTypeDef = TypedDict(
    "DialogCodeHookSettingsTypeDef",
    {
        "enabled": bool,
    },
)
InputContextTypeDef = TypedDict(
    "InputContextTypeDef",
    {
        "name": str,
    },
)
KendraConfigurationTypeDef = TypedDict(
    "KendraConfigurationTypeDef",
    {
        "kendraIndex": str,
        "queryFilterStringEnabled": NotRequired[bool],
        "queryFilterString": NotRequired[str],
    },
)
OutputContextTypeDef = TypedDict(
    "OutputContextTypeDef",
    {
        "name": str,
        "timeToLiveInSeconds": int,
        "turnsToLive": int,
    },
)
SampleUtteranceTypeDef = TypedDict(
    "SampleUtteranceTypeDef",
    {
        "utterance": str,
    },
)
CreateResourcePolicyRequestRequestTypeDef = TypedDict(
    "CreateResourcePolicyRequestRequestTypeDef",
    {
        "resourceArn": str,
        "policy": str,
    },
)
PrincipalTypeDef = TypedDict(
    "PrincipalTypeDef",
    {
        "service": NotRequired[str],
        "arn": NotRequired[str],
    },
)
MultipleValuesSettingTypeDef = TypedDict(
    "MultipleValuesSettingTypeDef",
    {
        "allowMultipleValues": NotRequired[bool],
    },
)
ObfuscationSettingTypeDef = TypedDict(
    "ObfuscationSettingTypeDef",
    {
        "obfuscationSettingType": ObfuscationSettingTypeType,
    },
)
CustomPayloadTypeDef = TypedDict(
    "CustomPayloadTypeDef",
    {
        "value": str,
    },
)
CustomVocabularyExportSpecificationTypeDef = TypedDict(
    "CustomVocabularyExportSpecificationTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
CustomVocabularyImportSpecificationTypeDef = TypedDict(
    "CustomVocabularyImportSpecificationTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DateRangeFilterTypeDef = TypedDict(
    "DateRangeFilterTypeDef",
    {
        "startDateTime": datetime,
        "endDateTime": datetime,
    },
)
DeleteBotAliasRequestRequestTypeDef = TypedDict(
    "DeleteBotAliasRequestRequestTypeDef",
    {
        "botAliasId": str,
        "botId": str,
        "skipResourceInUseCheck": NotRequired[bool],
    },
)
DeleteBotLocaleRequestRequestTypeDef = TypedDict(
    "DeleteBotLocaleRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DeleteBotReplicaRequestRequestTypeDef = TypedDict(
    "DeleteBotReplicaRequestRequestTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
    },
)
DeleteBotRequestRequestTypeDef = TypedDict(
    "DeleteBotRequestRequestTypeDef",
    {
        "botId": str,
        "skipResourceInUseCheck": NotRequired[bool],
    },
)
DeleteBotVersionRequestRequestTypeDef = TypedDict(
    "DeleteBotVersionRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "skipResourceInUseCheck": NotRequired[bool],
    },
)
DeleteCustomVocabularyRequestRequestTypeDef = TypedDict(
    "DeleteCustomVocabularyRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DeleteExportRequestRequestTypeDef = TypedDict(
    "DeleteExportRequestRequestTypeDef",
    {
        "exportId": str,
    },
)
DeleteImportRequestRequestTypeDef = TypedDict(
    "DeleteImportRequestRequestTypeDef",
    {
        "importId": str,
    },
)
DeleteIntentRequestRequestTypeDef = TypedDict(
    "DeleteIntentRequestRequestTypeDef",
    {
        "intentId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DeleteResourcePolicyRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyRequestRequestTypeDef",
    {
        "resourceArn": str,
        "expectedRevisionId": NotRequired[str],
    },
)
DeleteResourcePolicyStatementRequestRequestTypeDef = TypedDict(
    "DeleteResourcePolicyStatementRequestRequestTypeDef",
    {
        "resourceArn": str,
        "statementId": str,
        "expectedRevisionId": NotRequired[str],
    },
)
DeleteSlotRequestRequestTypeDef = TypedDict(
    "DeleteSlotRequestRequestTypeDef",
    {
        "slotId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
    },
)
DeleteSlotTypeRequestRequestTypeDef = TypedDict(
    "DeleteSlotTypeRequestRequestTypeDef",
    {
        "slotTypeId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "skipResourceInUseCheck": NotRequired[bool],
    },
)
DeleteTestSetRequestRequestTypeDef = TypedDict(
    "DeleteTestSetRequestRequestTypeDef",
    {
        "testSetId": str,
    },
)
DeleteUtterancesRequestRequestTypeDef = TypedDict(
    "DeleteUtterancesRequestRequestTypeDef",
    {
        "botId": str,
        "localeId": NotRequired[str],
        "sessionId": NotRequired[str],
    },
)
WaiterConfigTypeDef = TypedDict(
    "WaiterConfigTypeDef",
    {
        "Delay": NotRequired[int],
        "MaxAttempts": NotRequired[int],
    },
)
DescribeBotAliasRequestRequestTypeDef = TypedDict(
    "DescribeBotAliasRequestRequestTypeDef",
    {
        "botAliasId": str,
        "botId": str,
    },
)
ParentBotNetworkTypeDef = TypedDict(
    "ParentBotNetworkTypeDef",
    {
        "botId": str,
        "botVersion": str,
    },
)
DescribeBotLocaleRequestRequestTypeDef = TypedDict(
    "DescribeBotLocaleRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DescribeBotRecommendationRequestRequestTypeDef = TypedDict(
    "DescribeBotRecommendationRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
    },
)
EncryptionSettingTypeDef = TypedDict(
    "EncryptionSettingTypeDef",
    {
        "kmsKeyArn": NotRequired[str],
        "botLocaleExportPassword": NotRequired[str],
        "associatedTranscriptsPassword": NotRequired[str],
    },
)
DescribeBotReplicaRequestRequestTypeDef = TypedDict(
    "DescribeBotReplicaRequestRequestTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
    },
)
DescribeBotRequestRequestTypeDef = TypedDict(
    "DescribeBotRequestRequestTypeDef",
    {
        "botId": str,
    },
)
DescribeBotResourceGenerationRequestRequestTypeDef = TypedDict(
    "DescribeBotResourceGenerationRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "generationId": str,
    },
)
DescribeBotVersionRequestRequestTypeDef = TypedDict(
    "DescribeBotVersionRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
    },
)
DescribeCustomVocabularyMetadataRequestRequestTypeDef = TypedDict(
    "DescribeCustomVocabularyMetadataRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DescribeExportRequestRequestTypeDef = TypedDict(
    "DescribeExportRequestRequestTypeDef",
    {
        "exportId": str,
    },
)
DescribeImportRequestRequestTypeDef = TypedDict(
    "DescribeImportRequestRequestTypeDef",
    {
        "importId": str,
    },
)
DescribeIntentRequestRequestTypeDef = TypedDict(
    "DescribeIntentRequestRequestTypeDef",
    {
        "intentId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
SlotPriorityTypeDef = TypedDict(
    "SlotPriorityTypeDef",
    {
        "priority": int,
        "slotId": str,
    },
)
DescribeResourcePolicyRequestRequestTypeDef = TypedDict(
    "DescribeResourcePolicyRequestRequestTypeDef",
    {
        "resourceArn": str,
    },
)
DescribeSlotRequestRequestTypeDef = TypedDict(
    "DescribeSlotRequestRequestTypeDef",
    {
        "slotId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
    },
)
DescribeSlotTypeRequestRequestTypeDef = TypedDict(
    "DescribeSlotTypeRequestRequestTypeDef",
    {
        "slotTypeId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
DescribeTestExecutionRequestRequestTypeDef = TypedDict(
    "DescribeTestExecutionRequestRequestTypeDef",
    {
        "testExecutionId": str,
    },
)
DescribeTestSetDiscrepancyReportRequestRequestTypeDef = TypedDict(
    "DescribeTestSetDiscrepancyReportRequestRequestTypeDef",
    {
        "testSetDiscrepancyReportId": str,
    },
)
DescribeTestSetGenerationRequestRequestTypeDef = TypedDict(
    "DescribeTestSetGenerationRequestRequestTypeDef",
    {
        "testSetGenerationId": str,
    },
)
TestSetStorageLocationTypeDef = TypedDict(
    "TestSetStorageLocationTypeDef",
    {
        "s3BucketName": str,
        "s3Path": str,
        "kmsKeyArn": NotRequired[str],
    },
)
DescribeTestSetRequestRequestTypeDef = TypedDict(
    "DescribeTestSetRequestRequestTypeDef",
    {
        "testSetId": str,
    },
)
DialogActionTypeDef = TypedDict(
    "DialogActionTypeDef",
    {
        "type": DialogActionTypeType,
        "slotToElicit": NotRequired[str],
        "suppressNextMessage": NotRequired[bool],
    },
)
IntentOverrideTypeDef = TypedDict(
    "IntentOverrideTypeDef",
    {
        "name": NotRequired[str],
        "slots": NotRequired[Mapping[str, "SlotValueOverrideTypeDef"]],
    },
)
ElicitationCodeHookInvocationSettingTypeDef = TypedDict(
    "ElicitationCodeHookInvocationSettingTypeDef",
    {
        "enableCodeHookInvocation": bool,
        "invocationLabel": NotRequired[str],
    },
)
ExportFilterTypeDef = TypedDict(
    "ExportFilterTypeDef",
    {
        "name": Literal["ExportResourceType"],
        "values": Sequence[str],
        "operator": ExportFilterOperatorType,
    },
)
TestSetExportSpecificationTypeDef = TypedDict(
    "TestSetExportSpecificationTypeDef",
    {
        "testSetId": str,
    },
)
ExportSortByTypeDef = TypedDict(
    "ExportSortByTypeDef",
    {
        "attribute": Literal["LastUpdatedDateTime"],
        "order": SortOrderType,
    },
)
GenerateBotElementRequestRequestTypeDef = TypedDict(
    "GenerateBotElementRequestRequestTypeDef",
    {
        "intentId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
GenerationSortByTypeDef = TypedDict(
    "GenerationSortByTypeDef",
    {
        "attribute": GenerationSortByAttributeType,
        "order": SortOrderType,
    },
)
GenerationSummaryTypeDef = TypedDict(
    "GenerationSummaryTypeDef",
    {
        "generationId": NotRequired[str],
        "generationStatus": NotRequired[GenerationStatusType],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
GetTestExecutionArtifactsUrlRequestRequestTypeDef = TypedDict(
    "GetTestExecutionArtifactsUrlRequestRequestTypeDef",
    {
        "testExecutionId": str,
    },
)
GrammarSlotTypeSourceTypeDef = TypedDict(
    "GrammarSlotTypeSourceTypeDef",
    {
        "s3BucketName": str,
        "s3ObjectKey": str,
        "kmsKeyArn": NotRequired[str],
    },
)
ImportFilterTypeDef = TypedDict(
    "ImportFilterTypeDef",
    {
        "name": Literal["ImportResourceType"],
        "values": Sequence[str],
        "operator": ImportFilterOperatorType,
    },
)
ImportSortByTypeDef = TypedDict(
    "ImportSortByTypeDef",
    {
        "attribute": Literal["LastUpdatedDateTime"],
        "order": SortOrderType,
    },
)
ImportSummaryTypeDef = TypedDict(
    "ImportSummaryTypeDef",
    {
        "importId": NotRequired[str],
        "importedResourceId": NotRequired[str],
        "importedResourceName": NotRequired[str],
        "importStatus": NotRequired[ImportStatusType],
        "mergeStrategy": NotRequired[MergeStrategyType],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
        "importedResourceType": NotRequired[ImportResourceTypeType],
    },
)
RuntimeHintsTypeDef = TypedDict(
    "RuntimeHintsTypeDef",
    {
        "slotHints": NotRequired[Dict[str, Dict[str, "RuntimeHintDetailsTypeDef"]]],
    },
)
IntentClassificationTestResultItemCountsTypeDef = TypedDict(
    "IntentClassificationTestResultItemCountsTypeDef",
    {
        "totalResultCount": int,
        "intentMatchResultCounts": Dict[TestResultMatchStatusType, int],
        "speechTranscriptionResultCounts": NotRequired[Dict[TestResultMatchStatusType, int]],
    },
)
IntentFilterTypeDef = TypedDict(
    "IntentFilterTypeDef",
    {
        "name": Literal["IntentName"],
        "values": Sequence[str],
        "operator": IntentFilterOperatorType,
    },
)
IntentSortByTypeDef = TypedDict(
    "IntentSortByTypeDef",
    {
        "attribute": IntentSortAttributeType,
        "order": SortOrderType,
    },
)
InvokedIntentSampleTypeDef = TypedDict(
    "InvokedIntentSampleTypeDef",
    {
        "intentName": NotRequired[str],
    },
)
ListBotAliasReplicasRequestRequestTypeDef = TypedDict(
    "ListBotAliasReplicasRequestRequestTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotAliasesRequestRequestTypeDef = TypedDict(
    "ListBotAliasesRequestRequestTypeDef",
    {
        "botId": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotRecommendationsRequestRequestTypeDef = TypedDict(
    "ListBotRecommendationsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotReplicasRequestRequestTypeDef = TypedDict(
    "ListBotReplicasRequestRequestTypeDef",
    {
        "botId": str,
    },
)
ListCustomVocabularyItemsRequestRequestTypeDef = TypedDict(
    "ListCustomVocabularyItemsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
TimestampTypeDef = Union[datetime, str]
ListRecommendedIntentsRequestRequestTypeDef = TypedDict(
    "ListRecommendedIntentsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
RecommendedIntentSummaryTypeDef = TypedDict(
    "RecommendedIntentSummaryTypeDef",
    {
        "intentId": NotRequired[str],
        "intentName": NotRequired[str],
        "sampleUtterancesCount": NotRequired[int],
    },
)
SessionDataSortByTypeDef = TypedDict(
    "SessionDataSortByTypeDef",
    {
        "name": AnalyticsSessionSortByNameType,
        "order": AnalyticsSortOrderType,
    },
)
SlotTypeFilterTypeDef = TypedDict(
    "SlotTypeFilterTypeDef",
    {
        "name": SlotTypeFilterNameType,
        "values": Sequence[str],
        "operator": SlotTypeFilterOperatorType,
    },
)
SlotTypeSortByTypeDef = TypedDict(
    "SlotTypeSortByTypeDef",
    {
        "attribute": SlotTypeSortAttributeType,
        "order": SortOrderType,
    },
)
SlotTypeSummaryTypeDef = TypedDict(
    "SlotTypeSummaryTypeDef",
    {
        "slotTypeId": NotRequired[str],
        "slotTypeName": NotRequired[str],
        "description": NotRequired[str],
        "parentSlotTypeSignature": NotRequired[str],
        "lastUpdatedDateTime": NotRequired[datetime],
        "slotTypeCategory": NotRequired[SlotTypeCategoryType],
    },
)
SlotFilterTypeDef = TypedDict(
    "SlotFilterTypeDef",
    {
        "name": Literal["SlotName"],
        "values": Sequence[str],
        "operator": SlotFilterOperatorType,
    },
)
SlotSortByTypeDef = TypedDict(
    "SlotSortByTypeDef",
    {
        "attribute": SlotSortAttributeType,
        "order": SortOrderType,
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
    },
)
TestExecutionSortByTypeDef = TypedDict(
    "TestExecutionSortByTypeDef",
    {
        "attribute": TestExecutionSortAttributeType,
        "order": SortOrderType,
    },
)
ListTestSetRecordsRequestRequestTypeDef = TypedDict(
    "ListTestSetRecordsRequestRequestTypeDef",
    {
        "testSetId": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
TestSetSortByTypeDef = TypedDict(
    "TestSetSortByTypeDef",
    {
        "attribute": TestSetSortAttributeType,
        "order": SortOrderType,
    },
)
UtteranceDataSortByTypeDef = TypedDict(
    "UtteranceDataSortByTypeDef",
    {
        "name": Literal["UtteranceTimestamp"],
        "order": AnalyticsSortOrderType,
    },
)
PlainTextMessageTypeDef = TypedDict(
    "PlainTextMessageTypeDef",
    {
        "value": str,
    },
)
SSMLMessageTypeDef = TypedDict(
    "SSMLMessageTypeDef",
    {
        "value": str,
    },
)
OverallTestResultItemTypeDef = TypedDict(
    "OverallTestResultItemTypeDef",
    {
        "multiTurnConversation": bool,
        "totalResultCount": int,
        "endToEndResultCounts": Dict[TestResultMatchStatusType, int],
        "speechTranscriptionResultCounts": NotRequired[Dict[TestResultMatchStatusType, int]],
    },
)
PathFormatTypeDef = TypedDict(
    "PathFormatTypeDef",
    {
        "objectPrefixes": NotRequired[List[str]],
    },
)
TextInputSpecificationTypeDef = TypedDict(
    "TextInputSpecificationTypeDef",
    {
        "startTimeoutMs": int,
    },
)
RelativeAggregationDurationTypeDef = TypedDict(
    "RelativeAggregationDurationTypeDef",
    {
        "timeDimension": TimeDimensionType,
        "timeValue": int,
    },
)
RuntimeHintValueTypeDef = TypedDict(
    "RuntimeHintValueTypeDef",
    {
        "phrase": str,
    },
)
SampleValueTypeDef = TypedDict(
    "SampleValueTypeDef",
    {
        "value": str,
    },
)
SlotDefaultValueTypeDef = TypedDict(
    "SlotDefaultValueTypeDef",
    {
        "defaultValue": str,
    },
)
SlotResolutionSettingTypeDef = TypedDict(
    "SlotResolutionSettingTypeDef",
    {
        "slotResolutionStrategy": SlotResolutionStrategyType,
    },
)
SlotResolutionTestResultItemCountsTypeDef = TypedDict(
    "SlotResolutionTestResultItemCountsTypeDef",
    {
        "totalResultCount": int,
        "slotMatchResultCounts": Dict[TestResultMatchStatusType, int],
        "speechTranscriptionResultCounts": NotRequired[Dict[TestResultMatchStatusType, int]],
    },
)
SlotValueTypeDef = TypedDict(
    "SlotValueTypeDef",
    {
        "interpretedValue": NotRequired[str],
    },
)
SlotValueRegexFilterTypeDef = TypedDict(
    "SlotValueRegexFilterTypeDef",
    {
        "pattern": str,
    },
)
StartBotResourceGenerationRequestRequestTypeDef = TypedDict(
    "StartBotResourceGenerationRequestRequestTypeDef",
    {
        "generationInputPrompt": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
    },
)
StopBotRecommendationRequestRequestTypeDef = TypedDict(
    "StopBotRecommendationRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
        "tags": Mapping[str, str],
    },
)
TestSetIntentDiscrepancyItemTypeDef = TypedDict(
    "TestSetIntentDiscrepancyItemTypeDef",
    {
        "intentName": str,
        "errorMessage": str,
    },
)
TestSetSlotDiscrepancyItemTypeDef = TypedDict(
    "TestSetSlotDiscrepancyItemTypeDef",
    {
        "intentName": str,
        "slotName": str,
        "errorMessage": str,
    },
)
TestSetDiscrepancyReportBotAliasTargetTypeDef = TypedDict(
    "TestSetDiscrepancyReportBotAliasTargetTypeDef",
    {
        "botId": str,
        "botAliasId": str,
        "localeId": str,
    },
)
TestSetImportInputLocationTypeDef = TypedDict(
    "TestSetImportInputLocationTypeDef",
    {
        "s3BucketName": str,
        "s3Path": str,
    },
)
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "resourceARN": str,
        "tagKeys": Sequence[str],
    },
)
UpdateExportRequestRequestTypeDef = TypedDict(
    "UpdateExportRequestRequestTypeDef",
    {
        "exportId": str,
        "filePassword": NotRequired[str],
    },
)
UpdateResourcePolicyRequestRequestTypeDef = TypedDict(
    "UpdateResourcePolicyRequestRequestTypeDef",
    {
        "resourceArn": str,
        "policy": str,
        "expectedRevisionId": NotRequired[str],
    },
)
UpdateTestSetRequestRequestTypeDef = TypedDict(
    "UpdateTestSetRequestRequestTypeDef",
    {
        "testSetId": str,
        "testSetName": str,
        "description": NotRequired[str],
    },
)
UserTurnIntentOutputTypeDef = TypedDict(
    "UserTurnIntentOutputTypeDef",
    {
        "name": str,
        "slots": NotRequired[Dict[str, "UserTurnSlotOutputTypeDef"]],
    },
)
UserTurnSlotOutputTypeDef = TypedDict(
    "UserTurnSlotOutputTypeDef",
    {
        "value": NotRequired[str],
        "values": NotRequired[List[Dict[str, Any]]],
        "subSlots": NotRequired[Dict[str, Dict[str, Any]]],
    },
)
UtteranceAudioInputSpecificationTypeDef = TypedDict(
    "UtteranceAudioInputSpecificationTypeDef",
    {
        "audioFileS3Location": str,
    },
)
AgentTurnResultTypeDef = TypedDict(
    "AgentTurnResultTypeDef",
    {
        "expectedAgentPrompt": str,
        "actualAgentPrompt": NotRequired[str],
        "errorDetails": NotRequired[ExecutionErrorDetailsTypeDef],
        "actualElicitedSlot": NotRequired[str],
        "actualIntent": NotRequired[str],
    },
)
AnalyticsIntentResultTypeDef = TypedDict(
    "AnalyticsIntentResultTypeDef",
    {
        "binKeys": NotRequired[List[AnalyticsBinKeyTypeDef]],
        "groupByKeys": NotRequired[List[AnalyticsIntentGroupByKeyTypeDef]],
        "metricsResults": NotRequired[List[AnalyticsIntentMetricResultTypeDef]],
    },
)
AnalyticsIntentStageResultTypeDef = TypedDict(
    "AnalyticsIntentStageResultTypeDef",
    {
        "binKeys": NotRequired[List[AnalyticsBinKeyTypeDef]],
        "groupByKeys": NotRequired[List[AnalyticsIntentStageGroupByKeyTypeDef]],
        "metricsResults": NotRequired[List[AnalyticsIntentStageMetricResultTypeDef]],
    },
)
AnalyticsSessionResultTypeDef = TypedDict(
    "AnalyticsSessionResultTypeDef",
    {
        "binKeys": NotRequired[List[AnalyticsBinKeyTypeDef]],
        "groupByKeys": NotRequired[List[AnalyticsSessionGroupByKeyTypeDef]],
        "metricsResults": NotRequired[List[AnalyticsSessionMetricResultTypeDef]],
    },
)
AnalyticsUtteranceResultTypeDef = TypedDict(
    "AnalyticsUtteranceResultTypeDef",
    {
        "binKeys": NotRequired[List[AnalyticsBinKeyTypeDef]],
        "groupByKeys": NotRequired[List[AnalyticsUtteranceGroupByKeyTypeDef]],
        "metricsResults": NotRequired[List[AnalyticsUtteranceMetricResultTypeDef]],
        "attributeResults": NotRequired[List[AnalyticsUtteranceAttributeResultTypeDef]],
    },
)
SearchAssociatedTranscriptsRequestRequestTypeDef = TypedDict(
    "SearchAssociatedTranscriptsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
        "filters": Sequence[AssociatedTranscriptFilterTypeDef],
        "searchOrder": NotRequired[SearchOrderType],
        "maxResults": NotRequired[int],
        "nextIndex": NotRequired[int],
    },
)
AudioAndDTMFInputSpecificationTypeDef = TypedDict(
    "AudioAndDTMFInputSpecificationTypeDef",
    {
        "startTimeoutMs": int,
        "audioSpecification": NotRequired[AudioSpecificationTypeDef],
        "dtmfSpecification": NotRequired[DTMFSpecificationTypeDef],
    },
)
AudioLogDestinationTypeDef = TypedDict(
    "AudioLogDestinationTypeDef",
    {
        "s3Bucket": S3BucketLogDestinationTypeDef,
    },
)
BatchCreateCustomVocabularyItemRequestRequestTypeDef = TypedDict(
    "BatchCreateCustomVocabularyItemRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "customVocabularyItemList": Sequence[NewCustomVocabularyItemTypeDef],
    },
)
BatchUpdateCustomVocabularyItemRequestRequestTypeDef = TypedDict(
    "BatchUpdateCustomVocabularyItemRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "customVocabularyItemList": Sequence[CustomVocabularyItemTypeDef],
    },
)
BatchCreateCustomVocabularyItemResponseTypeDef = TypedDict(
    "BatchCreateCustomVocabularyItemResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "errors": List[FailedCustomVocabularyItemTypeDef],
        "resources": List[CustomVocabularyItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchDeleteCustomVocabularyItemResponseTypeDef = TypedDict(
    "BatchDeleteCustomVocabularyItemResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "errors": List[FailedCustomVocabularyItemTypeDef],
        "resources": List[CustomVocabularyItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchUpdateCustomVocabularyItemResponseTypeDef = TypedDict(
    "BatchUpdateCustomVocabularyItemResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "errors": List[FailedCustomVocabularyItemTypeDef],
        "resources": List[CustomVocabularyItemTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BuildBotLocaleResponseTypeDef = TypedDict(
    "BuildBotLocaleResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botLocaleStatus": BotLocaleStatusType,
        "lastBuildSubmittedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBotReplicaResponseTypeDef = TypedDict(
    "CreateBotReplicaResponseTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
        "sourceRegion": str,
        "creationDateTime": datetime,
        "botReplicaStatus": BotReplicaStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateResourcePolicyResponseTypeDef = TypedDict(
    "CreateResourcePolicyResponseTypeDef",
    {
        "resourceArn": str,
        "revisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateResourcePolicyStatementResponseTypeDef = TypedDict(
    "CreateResourcePolicyStatementResponseTypeDef",
    {
        "resourceArn": str,
        "revisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateUploadUrlResponseTypeDef = TypedDict(
    "CreateUploadUrlResponseTypeDef",
    {
        "importId": str,
        "uploadUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteBotAliasResponseTypeDef = TypedDict(
    "DeleteBotAliasResponseTypeDef",
    {
        "botAliasId": str,
        "botId": str,
        "botAliasStatus": BotAliasStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteBotLocaleResponseTypeDef = TypedDict(
    "DeleteBotLocaleResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botLocaleStatus": BotLocaleStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteBotReplicaResponseTypeDef = TypedDict(
    "DeleteBotReplicaResponseTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
        "botReplicaStatus": BotReplicaStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteBotResponseTypeDef = TypedDict(
    "DeleteBotResponseTypeDef",
    {
        "botId": str,
        "botStatus": BotStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteBotVersionResponseTypeDef = TypedDict(
    "DeleteBotVersionResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "botStatus": BotStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteCustomVocabularyResponseTypeDef = TypedDict(
    "DeleteCustomVocabularyResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "customVocabularyStatus": CustomVocabularyStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteExportResponseTypeDef = TypedDict(
    "DeleteExportResponseTypeDef",
    {
        "exportId": str,
        "exportStatus": ExportStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteImportResponseTypeDef = TypedDict(
    "DeleteImportResponseTypeDef",
    {
        "importId": str,
        "importStatus": ImportStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteResourcePolicyResponseTypeDef = TypedDict(
    "DeleteResourcePolicyResponseTypeDef",
    {
        "resourceArn": str,
        "revisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteResourcePolicyStatementResponseTypeDef = TypedDict(
    "DeleteResourcePolicyStatementResponseTypeDef",
    {
        "resourceArn": str,
        "revisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeBotReplicaResponseTypeDef = TypedDict(
    "DescribeBotReplicaResponseTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
        "sourceRegion": str,
        "creationDateTime": datetime,
        "botReplicaStatus": BotReplicaStatusType,
        "failureReasons": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeBotResourceGenerationResponseTypeDef = TypedDict(
    "DescribeBotResourceGenerationResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "generationId": str,
        "failureReasons": List[str],
        "generationStatus": GenerationStatusType,
        "generationInputPrompt": str,
        "generatedBotLocaleUrl": str,
        "creationDateTime": datetime,
        "modelArn": str,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeCustomVocabularyMetadataResponseTypeDef = TypedDict(
    "DescribeCustomVocabularyMetadataResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "customVocabularyStatus": CustomVocabularyStatusType,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeResourcePolicyResponseTypeDef = TypedDict(
    "DescribeResourcePolicyResponseTypeDef",
    {
        "resourceArn": str,
        "policy": str,
        "revisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetTestExecutionArtifactsUrlResponseTypeDef = TypedDict(
    "GetTestExecutionArtifactsUrlResponseTypeDef",
    {
        "testExecutionId": str,
        "downloadArtifactsUrl": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListCustomVocabularyItemsResponseTypeDef = TypedDict(
    "ListCustomVocabularyItemsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "customVocabularyItems": List[CustomVocabularyItemTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListIntentPathsResponseTypeDef = TypedDict(
    "ListIntentPathsResponseTypeDef",
    {
        "nodeSummaries": List[AnalyticsIntentNodeSummaryTypeDef],
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
SearchAssociatedTranscriptsResponseTypeDef = TypedDict(
    "SearchAssociatedTranscriptsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
        "nextIndex": int,
        "associatedTranscripts": List[AssociatedTranscriptTypeDef],
        "totalResults": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartBotResourceGenerationResponseTypeDef = TypedDict(
    "StartBotResourceGenerationResponseTypeDef",
    {
        "generationInputPrompt": str,
        "generationId": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "generationStatus": GenerationStatusType,
        "creationDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopBotRecommendationResponseTypeDef = TypedDict(
    "StopBotRecommendationResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationStatus": BotRecommendationStatusType,
        "botRecommendationId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateResourcePolicyResponseTypeDef = TypedDict(
    "UpdateResourcePolicyResponseTypeDef",
    {
        "resourceArn": str,
        "revisionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BatchDeleteCustomVocabularyItemRequestRequestTypeDef = TypedDict(
    "BatchDeleteCustomVocabularyItemRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "customVocabularyItemList": Sequence[CustomVocabularyEntryIdTypeDef],
    },
)
DescriptiveBotBuilderSpecificationTypeDef = TypedDict(
    "DescriptiveBotBuilderSpecificationTypeDef",
    {
        "enabled": bool,
        "bedrockModelSpecification": NotRequired[BedrockModelSpecificationTypeDef],
    },
)
SampleUtteranceGenerationSpecificationTypeDef = TypedDict(
    "SampleUtteranceGenerationSpecificationTypeDef",
    {
        "enabled": bool,
        "bedrockModelSpecification": NotRequired[BedrockModelSpecificationTypeDef],
    },
)
SlotResolutionImprovementSpecificationTypeDef = TypedDict(
    "SlotResolutionImprovementSpecificationTypeDef",
    {
        "enabled": bool,
        "bedrockModelSpecification": NotRequired[BedrockModelSpecificationTypeDef],
    },
)
ListBotAliasReplicasResponseTypeDef = TypedDict(
    "ListBotAliasReplicasResponseTypeDef",
    {
        "botId": str,
        "sourceRegion": str,
        "replicaRegion": str,
        "botAliasReplicaSummaries": List[BotAliasReplicaSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBotAliasesResponseTypeDef = TypedDict(
    "ListBotAliasesResponseTypeDef",
    {
        "botAliasSummaries": List[BotAliasSummaryTypeDef],
        "nextToken": str,
        "botId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestExecutionTargetTypeDef = TypedDict(
    "TestExecutionTargetTypeDef",
    {
        "botAliasTarget": NotRequired[BotAliasTestExecutionTargetTypeDef],
    },
)
BotImportSpecificationTypeDef = TypedDict(
    "BotImportSpecificationTypeDef",
    {
        "botName": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": NotRequired[int],
        "botTags": NotRequired[Dict[str, str]],
        "testBotAliasTags": NotRequired[Dict[str, str]],
    },
)
BotLocaleImportSpecificationTypeDef = TypedDict(
    "BotLocaleImportSpecificationTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "nluIntentConfidenceThreshold": NotRequired[float],
        "voiceSettings": NotRequired[VoiceSettingsTypeDef],
    },
)
ListBotLocalesRequestRequestTypeDef = TypedDict(
    "ListBotLocalesRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "sortBy": NotRequired[BotLocaleSortByTypeDef],
        "filters": NotRequired[Sequence[BotLocaleFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotLocalesResponseTypeDef = TypedDict(
    "ListBotLocalesResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "nextToken": str,
        "botLocaleSummaries": List[BotLocaleSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBotRequestRequestTypeDef = TypedDict(
    "CreateBotRequestRequestTypeDef",
    {
        "botName": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": int,
        "description": NotRequired[str],
        "botTags": NotRequired[Mapping[str, str]],
        "testBotAliasTags": NotRequired[Mapping[str, str]],
        "botType": NotRequired[BotTypeType],
        "botMembers": NotRequired[Sequence[BotMemberTypeDef]],
    },
)
CreateBotResponseTypeDef = TypedDict(
    "CreateBotResponseTypeDef",
    {
        "botId": str,
        "botName": str,
        "description": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": int,
        "botStatus": BotStatusType,
        "creationDateTime": datetime,
        "botTags": Dict[str, str],
        "testBotAliasTags": Dict[str, str],
        "botType": BotTypeType,
        "botMembers": List[BotMemberTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeBotResponseTypeDef = TypedDict(
    "DescribeBotResponseTypeDef",
    {
        "botId": str,
        "botName": str,
        "description": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": int,
        "botStatus": BotStatusType,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "botType": BotTypeType,
        "botMembers": List[BotMemberTypeDef],
        "failureReasons": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBotRequestRequestTypeDef = TypedDict(
    "UpdateBotRequestRequestTypeDef",
    {
        "botId": str,
        "botName": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": int,
        "description": NotRequired[str],
        "botType": NotRequired[BotTypeType],
        "botMembers": NotRequired[Sequence[BotMemberTypeDef]],
    },
)
UpdateBotResponseTypeDef = TypedDict(
    "UpdateBotResponseTypeDef",
    {
        "botId": str,
        "botName": str,
        "description": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": int,
        "botStatus": BotStatusType,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "botType": BotTypeType,
        "botMembers": List[BotMemberTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
BotRecommendationResultStatisticsTypeDef = TypedDict(
    "BotRecommendationResultStatisticsTypeDef",
    {
        "intents": NotRequired[IntentStatisticsTypeDef],
        "slotTypes": NotRequired[SlotTypeStatisticsTypeDef],
    },
)
ListBotRecommendationsResponseTypeDef = TypedDict(
    "ListBotRecommendationsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationSummaries": List[BotRecommendationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBotReplicasResponseTypeDef = TypedDict(
    "ListBotReplicasResponseTypeDef",
    {
        "botId": str,
        "sourceRegion": str,
        "botReplicaSummaries": List[BotReplicaSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBotsRequestRequestTypeDef = TypedDict(
    "ListBotsRequestRequestTypeDef",
    {
        "sortBy": NotRequired[BotSortByTypeDef],
        "filters": NotRequired[Sequence[BotFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotsResponseTypeDef = TypedDict(
    "ListBotsResponseTypeDef",
    {
        "botSummaries": List[BotSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBotVersionRequestRequestTypeDef = TypedDict(
    "CreateBotVersionRequestRequestTypeDef",
    {
        "botId": str,
        "botVersionLocaleSpecification": Mapping[str, BotVersionLocaleDetailsTypeDef],
        "description": NotRequired[str],
    },
)
CreateBotVersionResponseTypeDef = TypedDict(
    "CreateBotVersionResponseTypeDef",
    {
        "botId": str,
        "description": str,
        "botVersion": str,
        "botVersionLocaleSpecification": Dict[str, BotVersionLocaleDetailsTypeDef],
        "botStatus": BotStatusType,
        "creationDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBotVersionReplicasRequestRequestTypeDef = TypedDict(
    "ListBotVersionReplicasRequestRequestTypeDef",
    {
        "botId": str,
        "replicaRegion": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "sortBy": NotRequired[BotVersionReplicaSortByTypeDef],
    },
)
ListBotVersionReplicasResponseTypeDef = TypedDict(
    "ListBotVersionReplicasResponseTypeDef",
    {
        "botId": str,
        "sourceRegion": str,
        "replicaRegion": str,
        "botVersionReplicaSummaries": List[BotVersionReplicaSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBotVersionsRequestRequestTypeDef = TypedDict(
    "ListBotVersionsRequestRequestTypeDef",
    {
        "botId": str,
        "sortBy": NotRequired[BotVersionSortByTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotVersionsResponseTypeDef = TypedDict(
    "ListBotVersionsResponseTypeDef",
    {
        "botId": str,
        "botVersionSummaries": List[BotVersionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBuiltInIntentsRequestRequestTypeDef = TypedDict(
    "ListBuiltInIntentsRequestRequestTypeDef",
    {
        "localeId": str,
        "sortBy": NotRequired[BuiltInIntentSortByTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBuiltInIntentsResponseTypeDef = TypedDict(
    "ListBuiltInIntentsResponseTypeDef",
    {
        "builtInIntentSummaries": List[BuiltInIntentSummaryTypeDef],
        "nextToken": str,
        "localeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListBuiltInSlotTypesRequestRequestTypeDef = TypedDict(
    "ListBuiltInSlotTypesRequestRequestTypeDef",
    {
        "localeId": str,
        "sortBy": NotRequired[BuiltInSlotTypeSortByTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBuiltInSlotTypesResponseTypeDef = TypedDict(
    "ListBuiltInSlotTypesResponseTypeDef",
    {
        "builtInSlotTypeSummaries": List[BuiltInSlotTypeSummaryTypeDef],
        "nextToken": str,
        "localeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImageResponseCardTypeDef = TypedDict(
    "ImageResponseCardTypeDef",
    {
        "title": str,
        "subtitle": NotRequired[str],
        "imageUrl": NotRequired[str],
        "buttons": NotRequired[Sequence[ButtonTypeDef]],
    },
)
TextLogDestinationTypeDef = TypedDict(
    "TextLogDestinationTypeDef",
    {
        "cloudWatch": CloudWatchLogGroupLogDestinationTypeDef,
    },
)
CodeHookSpecificationTypeDef = TypedDict(
    "CodeHookSpecificationTypeDef",
    {
        "lambdaCodeHook": LambdaCodeHookTypeDef,
    },
)
CompositeSlotTypeSettingTypeDef = TypedDict(
    "CompositeSlotTypeSettingTypeDef",
    {
        "subSlots": NotRequired[Sequence[SubSlotTypeCompositionTypeDef]],
    },
)
ConversationLevelTestResultItemTypeDef = TypedDict(
    "ConversationLevelTestResultItemTypeDef",
    {
        "conversationId": str,
        "endToEndResult": TestResultMatchStatusType,
        "intentClassificationResults": List[ConversationLevelIntentClassificationResultItemTypeDef],
        "slotResolutionResults": List[ConversationLevelSlotResolutionResultItemTypeDef],
        "speechTranscriptionResult": NotRequired[TestResultMatchStatusType],
    },
)
TestExecutionResultFilterByTypeDef = TypedDict(
    "TestExecutionResultFilterByTypeDef",
    {
        "resultTypeFilter": TestResultTypeFilterType,
        "conversationLevelTestResultsFilterBy": NotRequired[
            ConversationLevelTestResultsFilterByTypeDef
        ],
    },
)
ConversationLogsDataSourceTypeDef = TypedDict(
    "ConversationLogsDataSourceTypeDef",
    {
        "botId": str,
        "botAliasId": str,
        "localeId": str,
        "filter": ConversationLogsDataSourceFilterByTypeDef,
    },
)
IntentSummaryTypeDef = TypedDict(
    "IntentSummaryTypeDef",
    {
        "intentId": NotRequired[str],
        "intentName": NotRequired[str],
        "description": NotRequired[str],
        "parentIntentSignature": NotRequired[str],
        "inputContexts": NotRequired[List[InputContextTypeDef]],
        "outputContexts": NotRequired[List[OutputContextTypeDef]],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
GenerateBotElementResponseTypeDef = TypedDict(
    "GenerateBotElementResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "sampleUtterances": List[SampleUtteranceTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateResourcePolicyStatementRequestRequestTypeDef = TypedDict(
    "CreateResourcePolicyStatementRequestRequestTypeDef",
    {
        "resourceArn": str,
        "statementId": str,
        "effect": EffectType,
        "principal": Sequence[PrincipalTypeDef],
        "action": Sequence[str],
        "condition": NotRequired[Mapping[str, Mapping[str, str]]],
        "expectedRevisionId": NotRequired[str],
    },
)
LexTranscriptFilterTypeDef = TypedDict(
    "LexTranscriptFilterTypeDef",
    {
        "dateRangeFilter": NotRequired[DateRangeFilterTypeDef],
    },
)
DescribeBotAliasRequestBotAliasAvailableWaitTypeDef = TypedDict(
    "DescribeBotAliasRequestBotAliasAvailableWaitTypeDef",
    {
        "botAliasId": str,
        "botId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeBotLocaleRequestBotLocaleBuiltWaitTypeDef = TypedDict(
    "DescribeBotLocaleRequestBotLocaleBuiltWaitTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeBotLocaleRequestBotLocaleCreatedWaitTypeDef = TypedDict(
    "DescribeBotLocaleRequestBotLocaleCreatedWaitTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeBotLocaleRequestBotLocaleExpressTestingAvailableWaitTypeDef = TypedDict(
    "DescribeBotLocaleRequestBotLocaleExpressTestingAvailableWaitTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeBotRequestBotAvailableWaitTypeDef = TypedDict(
    "DescribeBotRequestBotAvailableWaitTypeDef",
    {
        "botId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeBotVersionRequestBotVersionAvailableWaitTypeDef = TypedDict(
    "DescribeBotVersionRequestBotVersionAvailableWaitTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeExportRequestBotExportCompletedWaitTypeDef = TypedDict(
    "DescribeExportRequestBotExportCompletedWaitTypeDef",
    {
        "exportId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeImportRequestBotImportCompletedWaitTypeDef = TypedDict(
    "DescribeImportRequestBotImportCompletedWaitTypeDef",
    {
        "importId": str,
        "WaiterConfig": NotRequired[WaiterConfigTypeDef],
    },
)
DescribeBotVersionResponseTypeDef = TypedDict(
    "DescribeBotVersionResponseTypeDef",
    {
        "botId": str,
        "botName": str,
        "botVersion": str,
        "description": str,
        "roleArn": str,
        "dataPrivacy": DataPrivacyTypeDef,
        "idleSessionTTLInSeconds": int,
        "botStatus": BotStatusType,
        "failureReasons": List[str],
        "creationDateTime": datetime,
        "parentBotNetworks": List[ParentBotNetworkTypeDef],
        "botType": BotTypeType,
        "botMembers": List[BotMemberTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBotRecommendationRequestRequestTypeDef = TypedDict(
    "UpdateBotRecommendationRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
        "encryptionSetting": EncryptionSettingTypeDef,
    },
)
DescribeTestSetResponseTypeDef = TypedDict(
    "DescribeTestSetResponseTypeDef",
    {
        "testSetId": str,
        "testSetName": str,
        "description": str,
        "modality": TestSetModalityType,
        "status": TestSetStatusType,
        "roleArn": str,
        "numTurns": int,
        "storageLocation": TestSetStorageLocationTypeDef,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestSetSummaryTypeDef = TypedDict(
    "TestSetSummaryTypeDef",
    {
        "testSetId": NotRequired[str],
        "testSetName": NotRequired[str],
        "description": NotRequired[str],
        "modality": NotRequired[TestSetModalityType],
        "status": NotRequired[TestSetStatusType],
        "roleArn": NotRequired[str],
        "numTurns": NotRequired[int],
        "storageLocation": NotRequired[TestSetStorageLocationTypeDef],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
UpdateTestSetResponseTypeDef = TypedDict(
    "UpdateTestSetResponseTypeDef",
    {
        "testSetId": str,
        "testSetName": str,
        "description": str,
        "modality": TestSetModalityType,
        "status": TestSetStatusType,
        "roleArn": str,
        "numTurns": int,
        "storageLocation": TestSetStorageLocationTypeDef,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DialogStateTypeDef = TypedDict(
    "DialogStateTypeDef",
    {
        "dialogAction": NotRequired[DialogActionTypeDef],
        "intent": NotRequired[IntentOverrideTypeDef],
        "sessionAttributes": NotRequired[Mapping[str, str]],
    },
)
ExportResourceSpecificationTypeDef = TypedDict(
    "ExportResourceSpecificationTypeDef",
    {
        "botExportSpecification": NotRequired[BotExportSpecificationTypeDef],
        "botLocaleExportSpecification": NotRequired[BotLocaleExportSpecificationTypeDef],
        "customVocabularyExportSpecification": NotRequired[
            CustomVocabularyExportSpecificationTypeDef
        ],
        "testSetExportSpecification": NotRequired[TestSetExportSpecificationTypeDef],
    },
)
ListExportsRequestRequestTypeDef = TypedDict(
    "ListExportsRequestRequestTypeDef",
    {
        "botId": NotRequired[str],
        "botVersion": NotRequired[str],
        "sortBy": NotRequired[ExportSortByTypeDef],
        "filters": NotRequired[Sequence[ExportFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "localeId": NotRequired[str],
    },
)
ListBotResourceGenerationsRequestRequestTypeDef = TypedDict(
    "ListBotResourceGenerationsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "sortBy": NotRequired[GenerationSortByTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListBotResourceGenerationsResponseTypeDef = TypedDict(
    "ListBotResourceGenerationsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "generationSummaries": List[GenerationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GrammarSlotTypeSettingTypeDef = TypedDict(
    "GrammarSlotTypeSettingTypeDef",
    {
        "source": NotRequired[GrammarSlotTypeSourceTypeDef],
    },
)
ListImportsRequestRequestTypeDef = TypedDict(
    "ListImportsRequestRequestTypeDef",
    {
        "botId": NotRequired[str],
        "botVersion": NotRequired[str],
        "sortBy": NotRequired[ImportSortByTypeDef],
        "filters": NotRequired[Sequence[ImportFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "localeId": NotRequired[str],
    },
)
ListImportsResponseTypeDef = TypedDict(
    "ListImportsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "importSummaries": List[ImportSummaryTypeDef],
        "nextToken": str,
        "localeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InputSessionStateSpecificationTypeDef = TypedDict(
    "InputSessionStateSpecificationTypeDef",
    {
        "sessionAttributes": NotRequired[Dict[str, str]],
        "activeContexts": NotRequired[List[ActiveContextTypeDef]],
        "runtimeHints": NotRequired[RuntimeHintsTypeDef],
    },
)
IntentClassificationTestResultItemTypeDef = TypedDict(
    "IntentClassificationTestResultItemTypeDef",
    {
        "intentName": str,
        "multiTurnConversation": bool,
        "resultCounts": IntentClassificationTestResultItemCountsTypeDef,
    },
)
ListIntentsRequestRequestTypeDef = TypedDict(
    "ListIntentsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "sortBy": NotRequired[IntentSortByTypeDef],
        "filters": NotRequired[Sequence[IntentFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
SessionSpecificationTypeDef = TypedDict(
    "SessionSpecificationTypeDef",
    {
        "botAliasId": NotRequired[str],
        "botVersion": NotRequired[str],
        "localeId": NotRequired[str],
        "channel": NotRequired[str],
        "sessionId": NotRequired[str],
        "conversationStartTime": NotRequired[datetime],
        "conversationEndTime": NotRequired[datetime],
        "conversationDurationSeconds": NotRequired[int],
        "conversationEndState": NotRequired[ConversationEndStateType],
        "mode": NotRequired[AnalyticsModalityType],
        "numberOfTurns": NotRequired[int],
        "invokedIntentSamples": NotRequired[List[InvokedIntentSampleTypeDef]],
        "originatingRequestId": NotRequired[str],
    },
)
ListIntentMetricsRequestRequestTypeDef = TypedDict(
    "ListIntentMetricsRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "metrics": Sequence[AnalyticsIntentMetricTypeDef],
        "binBy": NotRequired[Sequence[AnalyticsBinBySpecificationTypeDef]],
        "groupBy": NotRequired[Sequence[AnalyticsIntentGroupBySpecificationTypeDef]],
        "filters": NotRequired[Sequence[AnalyticsIntentFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListIntentPathsRequestRequestTypeDef = TypedDict(
    "ListIntentPathsRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "intentPath": str,
        "filters": NotRequired[Sequence[AnalyticsPathFilterTypeDef]],
    },
)
ListIntentStageMetricsRequestRequestTypeDef = TypedDict(
    "ListIntentStageMetricsRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "metrics": Sequence[AnalyticsIntentStageMetricTypeDef],
        "binBy": NotRequired[Sequence[AnalyticsBinBySpecificationTypeDef]],
        "groupBy": NotRequired[Sequence[AnalyticsIntentStageGroupBySpecificationTypeDef]],
        "filters": NotRequired[Sequence[AnalyticsIntentStageFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListSessionMetricsRequestRequestTypeDef = TypedDict(
    "ListSessionMetricsRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "metrics": Sequence[AnalyticsSessionMetricTypeDef],
        "binBy": NotRequired[Sequence[AnalyticsBinBySpecificationTypeDef]],
        "groupBy": NotRequired[Sequence[AnalyticsSessionGroupBySpecificationTypeDef]],
        "filters": NotRequired[Sequence[AnalyticsSessionFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListUtteranceMetricsRequestRequestTypeDef = TypedDict(
    "ListUtteranceMetricsRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "metrics": Sequence[AnalyticsUtteranceMetricTypeDef],
        "binBy": NotRequired[Sequence[AnalyticsBinBySpecificationTypeDef]],
        "groupBy": NotRequired[Sequence[AnalyticsUtteranceGroupBySpecificationTypeDef]],
        "attributes": NotRequired[Sequence[AnalyticsUtteranceAttributeTypeDef]],
        "filters": NotRequired[Sequence[AnalyticsUtteranceFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListRecommendedIntentsResponseTypeDef = TypedDict(
    "ListRecommendedIntentsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationId": str,
        "summaryList": List[RecommendedIntentSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSessionAnalyticsDataRequestRequestTypeDef = TypedDict(
    "ListSessionAnalyticsDataRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "sortBy": NotRequired[SessionDataSortByTypeDef],
        "filters": NotRequired[Sequence[AnalyticsSessionFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListSlotTypesRequestRequestTypeDef = TypedDict(
    "ListSlotTypesRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "sortBy": NotRequired[SlotTypeSortByTypeDef],
        "filters": NotRequired[Sequence[SlotTypeFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListSlotTypesResponseTypeDef = TypedDict(
    "ListSlotTypesResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "slotTypeSummaries": List[SlotTypeSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSlotsRequestRequestTypeDef = TypedDict(
    "ListSlotsRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "sortBy": NotRequired[SlotSortByTypeDef],
        "filters": NotRequired[Sequence[SlotFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListTestExecutionsRequestRequestTypeDef = TypedDict(
    "ListTestExecutionsRequestRequestTypeDef",
    {
        "sortBy": NotRequired[TestExecutionSortByTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListTestSetsRequestRequestTypeDef = TypedDict(
    "ListTestSetsRequestRequestTypeDef",
    {
        "sortBy": NotRequired[TestSetSortByTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListUtteranceAnalyticsDataRequestRequestTypeDef = TypedDict(
    "ListUtteranceAnalyticsDataRequestRequestTypeDef",
    {
        "botId": str,
        "startDateTime": TimestampTypeDef,
        "endDateTime": TimestampTypeDef,
        "sortBy": NotRequired[UtteranceDataSortByTypeDef],
        "filters": NotRequired[Sequence[AnalyticsUtteranceFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
OverallTestResultsTypeDef = TypedDict(
    "OverallTestResultsTypeDef",
    {
        "items": List[OverallTestResultItemTypeDef],
    },
)
UtteranceAggregationDurationTypeDef = TypedDict(
    "UtteranceAggregationDurationTypeDef",
    {
        "relativeAggregationDuration": RelativeAggregationDurationTypeDef,
    },
)
RuntimeHintDetailsTypeDef = TypedDict(
    "RuntimeHintDetailsTypeDef",
    {
        "runtimeHintValues": NotRequired[List[RuntimeHintValueTypeDef]],
        "subSlotHints": NotRequired[Dict[str, Dict[str, Any]]],
    },
)
SlotTypeValueTypeDef = TypedDict(
    "SlotTypeValueTypeDef",
    {
        "sampleValue": NotRequired[SampleValueTypeDef],
        "synonyms": NotRequired[Sequence[SampleValueTypeDef]],
    },
)
SlotDefaultValueSpecificationTypeDef = TypedDict(
    "SlotDefaultValueSpecificationTypeDef",
    {
        "defaultValueList": Sequence[SlotDefaultValueTypeDef],
    },
)
SlotResolutionTestResultItemTypeDef = TypedDict(
    "SlotResolutionTestResultItemTypeDef",
    {
        "slotName": str,
        "resultCounts": SlotResolutionTestResultItemCountsTypeDef,
    },
)
SlotValueOverrideTypeDef = TypedDict(
    "SlotValueOverrideTypeDef",
    {
        "shape": NotRequired[SlotShapeType],
        "value": NotRequired[SlotValueTypeDef],
        "values": NotRequired[Sequence[Dict[str, Any]]],
    },
)
SlotValueSelectionSettingTypeDef = TypedDict(
    "SlotValueSelectionSettingTypeDef",
    {
        "resolutionStrategy": SlotValueResolutionStrategyType,
        "regexFilter": NotRequired[SlotValueRegexFilterTypeDef],
        "advancedRecognitionSetting": NotRequired[AdvancedRecognitionSettingTypeDef],
    },
)
TestSetDiscrepancyErrorsTypeDef = TypedDict(
    "TestSetDiscrepancyErrorsTypeDef",
    {
        "intentDiscrepancies": List[TestSetIntentDiscrepancyItemTypeDef],
        "slotDiscrepancies": List[TestSetSlotDiscrepancyItemTypeDef],
    },
)
TestSetDiscrepancyReportResourceTargetTypeDef = TypedDict(
    "TestSetDiscrepancyReportResourceTargetTypeDef",
    {
        "botAliasTarget": NotRequired[TestSetDiscrepancyReportBotAliasTargetTypeDef],
    },
)
TestSetImportResourceSpecificationTypeDef = TypedDict(
    "TestSetImportResourceSpecificationTypeDef",
    {
        "testSetName": str,
        "roleArn": str,
        "storageLocation": TestSetStorageLocationTypeDef,
        "importInputLocation": TestSetImportInputLocationTypeDef,
        "modality": TestSetModalityType,
        "description": NotRequired[str],
        "testSetTags": NotRequired[Dict[str, str]],
    },
)
UserTurnOutputSpecificationTypeDef = TypedDict(
    "UserTurnOutputSpecificationTypeDef",
    {
        "intent": UserTurnIntentOutputTypeDef,
        "activeContexts": NotRequired[List[ActiveContextTypeDef]],
        "transcript": NotRequired[str],
    },
)
UtteranceInputSpecificationTypeDef = TypedDict(
    "UtteranceInputSpecificationTypeDef",
    {
        "textInput": NotRequired[str],
        "audioInput": NotRequired[UtteranceAudioInputSpecificationTypeDef],
    },
)
ListIntentMetricsResponseTypeDef = TypedDict(
    "ListIntentMetricsResponseTypeDef",
    {
        "botId": str,
        "results": List[AnalyticsIntentResultTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListIntentStageMetricsResponseTypeDef = TypedDict(
    "ListIntentStageMetricsResponseTypeDef",
    {
        "botId": str,
        "results": List[AnalyticsIntentStageResultTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListSessionMetricsResponseTypeDef = TypedDict(
    "ListSessionMetricsResponseTypeDef",
    {
        "botId": str,
        "results": List[AnalyticsSessionResultTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListUtteranceMetricsResponseTypeDef = TypedDict(
    "ListUtteranceMetricsResponseTypeDef",
    {
        "botId": str,
        "results": List[AnalyticsUtteranceResultTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PromptAttemptSpecificationTypeDef = TypedDict(
    "PromptAttemptSpecificationTypeDef",
    {
        "allowedInputTypes": AllowedInputTypesTypeDef,
        "allowInterrupt": NotRequired[bool],
        "audioAndDTMFInputSpecification": NotRequired[AudioAndDTMFInputSpecificationTypeDef],
        "textInputSpecification": NotRequired[TextInputSpecificationTypeDef],
    },
)
AudioLogSettingTypeDef = TypedDict(
    "AudioLogSettingTypeDef",
    {
        "enabled": bool,
        "destination": AudioLogDestinationTypeDef,
        "selectiveLoggingEnabled": NotRequired[bool],
    },
)
BuildtimeSettingsTypeDef = TypedDict(
    "BuildtimeSettingsTypeDef",
    {
        "descriptiveBotBuilder": NotRequired[DescriptiveBotBuilderSpecificationTypeDef],
        "sampleUtteranceGeneration": NotRequired[SampleUtteranceGenerationSpecificationTypeDef],
    },
)
RuntimeSettingsTypeDef = TypedDict(
    "RuntimeSettingsTypeDef",
    {
        "slotResolutionImprovement": NotRequired[SlotResolutionImprovementSpecificationTypeDef],
    },
)
DescribeTestExecutionResponseTypeDef = TypedDict(
    "DescribeTestExecutionResponseTypeDef",
    {
        "testExecutionId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "testExecutionStatus": TestExecutionStatusType,
        "testSetId": str,
        "testSetName": str,
        "target": TestExecutionTargetTypeDef,
        "apiMode": TestExecutionApiModeType,
        "testExecutionModality": TestExecutionModalityType,
        "failureReasons": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTestExecutionRequestRequestTypeDef = TypedDict(
    "StartTestExecutionRequestRequestTypeDef",
    {
        "testSetId": str,
        "target": TestExecutionTargetTypeDef,
        "apiMode": TestExecutionApiModeType,
        "testExecutionModality": NotRequired[TestExecutionModalityType],
    },
)
StartTestExecutionResponseTypeDef = TypedDict(
    "StartTestExecutionResponseTypeDef",
    {
        "testExecutionId": str,
        "creationDateTime": datetime,
        "testSetId": str,
        "target": TestExecutionTargetTypeDef,
        "apiMode": TestExecutionApiModeType,
        "testExecutionModality": TestExecutionModalityType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TestExecutionSummaryTypeDef = TypedDict(
    "TestExecutionSummaryTypeDef",
    {
        "testExecutionId": NotRequired[str],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
        "testExecutionStatus": NotRequired[TestExecutionStatusType],
        "testSetId": NotRequired[str],
        "testSetName": NotRequired[str],
        "target": NotRequired[TestExecutionTargetTypeDef],
        "apiMode": NotRequired[TestExecutionApiModeType],
        "testExecutionModality": NotRequired[TestExecutionModalityType],
    },
)
BotRecommendationResultsTypeDef = TypedDict(
    "BotRecommendationResultsTypeDef",
    {
        "botLocaleExportUrl": NotRequired[str],
        "associatedTranscriptsUrl": NotRequired[str],
        "statistics": NotRequired[BotRecommendationResultStatisticsTypeDef],
    },
)
MessageTypeDef = TypedDict(
    "MessageTypeDef",
    {
        "plainTextMessage": NotRequired[PlainTextMessageTypeDef],
        "customPayload": NotRequired[CustomPayloadTypeDef],
        "ssmlMessage": NotRequired[SSMLMessageTypeDef],
        "imageResponseCard": NotRequired[ImageResponseCardTypeDef],
    },
)
UtteranceBotResponseTypeDef = TypedDict(
    "UtteranceBotResponseTypeDef",
    {
        "content": NotRequired[str],
        "contentType": NotRequired[UtteranceContentTypeType],
        "imageResponseCard": NotRequired[ImageResponseCardTypeDef],
    },
)
TextLogSettingTypeDef = TypedDict(
    "TextLogSettingTypeDef",
    {
        "enabled": bool,
        "destination": TextLogDestinationTypeDef,
        "selectiveLoggingEnabled": NotRequired[bool],
    },
)
BotAliasLocaleSettingsTypeDef = TypedDict(
    "BotAliasLocaleSettingsTypeDef",
    {
        "enabled": bool,
        "codeHookSpecification": NotRequired[CodeHookSpecificationTypeDef],
    },
)
ConversationLevelTestResultsTypeDef = TypedDict(
    "ConversationLevelTestResultsTypeDef",
    {
        "items": List[ConversationLevelTestResultItemTypeDef],
    },
)
ListTestExecutionResultItemsRequestRequestTypeDef = TypedDict(
    "ListTestExecutionResultItemsRequestRequestTypeDef",
    {
        "testExecutionId": str,
        "resultFilterBy": TestExecutionResultFilterByTypeDef,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
TestSetGenerationDataSourceTypeDef = TypedDict(
    "TestSetGenerationDataSourceTypeDef",
    {
        "conversationLogsDataSource": NotRequired[ConversationLogsDataSourceTypeDef],
    },
)
ListIntentsResponseTypeDef = TypedDict(
    "ListIntentsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentSummaries": List[IntentSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TranscriptFilterTypeDef = TypedDict(
    "TranscriptFilterTypeDef",
    {
        "lexTranscriptFilter": NotRequired[LexTranscriptFilterTypeDef],
    },
)
ListTestSetsResponseTypeDef = TypedDict(
    "ListTestSetsResponseTypeDef",
    {
        "testSets": List[TestSetSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateExportRequestRequestTypeDef = TypedDict(
    "CreateExportRequestRequestTypeDef",
    {
        "resourceSpecification": ExportResourceSpecificationTypeDef,
        "fileFormat": ImportExportFileFormatType,
        "filePassword": NotRequired[str],
    },
)
CreateExportResponseTypeDef = TypedDict(
    "CreateExportResponseTypeDef",
    {
        "exportId": str,
        "resourceSpecification": ExportResourceSpecificationTypeDef,
        "fileFormat": ImportExportFileFormatType,
        "exportStatus": ExportStatusType,
        "creationDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeExportResponseTypeDef = TypedDict(
    "DescribeExportResponseTypeDef",
    {
        "exportId": str,
        "resourceSpecification": ExportResourceSpecificationTypeDef,
        "fileFormat": ImportExportFileFormatType,
        "exportStatus": ExportStatusType,
        "failureReasons": List[str],
        "downloadUrl": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExportSummaryTypeDef = TypedDict(
    "ExportSummaryTypeDef",
    {
        "exportId": NotRequired[str],
        "resourceSpecification": NotRequired[ExportResourceSpecificationTypeDef],
        "fileFormat": NotRequired[ImportExportFileFormatType],
        "exportStatus": NotRequired[ExportStatusType],
        "creationDateTime": NotRequired[datetime],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
UpdateExportResponseTypeDef = TypedDict(
    "UpdateExportResponseTypeDef",
    {
        "exportId": str,
        "resourceSpecification": ExportResourceSpecificationTypeDef,
        "fileFormat": ImportExportFileFormatType,
        "exportStatus": ExportStatusType,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ExternalSourceSettingTypeDef = TypedDict(
    "ExternalSourceSettingTypeDef",
    {
        "grammarSlotTypeSetting": NotRequired[GrammarSlotTypeSettingTypeDef],
    },
)
IntentClassificationTestResultsTypeDef = TypedDict(
    "IntentClassificationTestResultsTypeDef",
    {
        "items": List[IntentClassificationTestResultItemTypeDef],
    },
)
ListSessionAnalyticsDataResponseTypeDef = TypedDict(
    "ListSessionAnalyticsDataResponseTypeDef",
    {
        "botId": str,
        "nextToken": str,
        "sessions": List[SessionSpecificationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAggregatedUtterancesRequestRequestTypeDef = TypedDict(
    "ListAggregatedUtterancesRequestRequestTypeDef",
    {
        "botId": str,
        "localeId": str,
        "aggregationDuration": UtteranceAggregationDurationTypeDef,
        "botAliasId": NotRequired[str],
        "botVersion": NotRequired[str],
        "sortBy": NotRequired[AggregatedUtterancesSortByTypeDef],
        "filters": NotRequired[Sequence[AggregatedUtterancesFilterTypeDef]],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListAggregatedUtterancesResponseTypeDef = TypedDict(
    "ListAggregatedUtterancesResponseTypeDef",
    {
        "botId": str,
        "botAliasId": str,
        "botVersion": str,
        "localeId": str,
        "aggregationDuration": UtteranceAggregationDurationTypeDef,
        "aggregationWindowStartTime": datetime,
        "aggregationWindowEndTime": datetime,
        "aggregationLastRefreshedDateTime": datetime,
        "aggregatedUtterancesSummaries": List[AggregatedUtterancesSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IntentLevelSlotResolutionTestResultItemTypeDef = TypedDict(
    "IntentLevelSlotResolutionTestResultItemTypeDef",
    {
        "intentName": str,
        "multiTurnConversation": bool,
        "slotResolutionResults": List[SlotResolutionTestResultItemTypeDef],
    },
)
CreateTestSetDiscrepancyReportRequestRequestTypeDef = TypedDict(
    "CreateTestSetDiscrepancyReportRequestRequestTypeDef",
    {
        "testSetId": str,
        "target": TestSetDiscrepancyReportResourceTargetTypeDef,
    },
)
CreateTestSetDiscrepancyReportResponseTypeDef = TypedDict(
    "CreateTestSetDiscrepancyReportResponseTypeDef",
    {
        "testSetDiscrepancyReportId": str,
        "creationDateTime": datetime,
        "testSetId": str,
        "target": TestSetDiscrepancyReportResourceTargetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeTestSetDiscrepancyReportResponseTypeDef = TypedDict(
    "DescribeTestSetDiscrepancyReportResponseTypeDef",
    {
        "testSetDiscrepancyReportId": str,
        "testSetId": str,
        "creationDateTime": datetime,
        "target": TestSetDiscrepancyReportResourceTargetTypeDef,
        "testSetDiscrepancyReportStatus": TestSetDiscrepancyReportStatusType,
        "lastUpdatedDataTime": datetime,
        "testSetDiscrepancyTopErrors": TestSetDiscrepancyErrorsTypeDef,
        "testSetDiscrepancyRawOutputUrl": str,
        "failureReasons": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ImportResourceSpecificationTypeDef = TypedDict(
    "ImportResourceSpecificationTypeDef",
    {
        "botImportSpecification": NotRequired[BotImportSpecificationTypeDef],
        "botLocaleImportSpecification": NotRequired[BotLocaleImportSpecificationTypeDef],
        "customVocabularyImportSpecification": NotRequired[
            CustomVocabularyImportSpecificationTypeDef
        ],
        "testSetImportResourceSpecification": NotRequired[
            TestSetImportResourceSpecificationTypeDef
        ],
    },
)
UserTurnInputSpecificationTypeDef = TypedDict(
    "UserTurnInputSpecificationTypeDef",
    {
        "utteranceInput": UtteranceInputSpecificationTypeDef,
        "requestAttributes": NotRequired[Dict[str, str]],
        "sessionState": NotRequired[InputSessionStateSpecificationTypeDef],
    },
)
GenerativeAISettingsTypeDef = TypedDict(
    "GenerativeAISettingsTypeDef",
    {
        "runtimeSettings": NotRequired[RuntimeSettingsTypeDef],
        "buildtimeSettings": NotRequired[BuildtimeSettingsTypeDef],
    },
)
ListTestExecutionsResponseTypeDef = TypedDict(
    "ListTestExecutionsResponseTypeDef",
    {
        "testExecutions": List[TestExecutionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
MessageGroupTypeDef = TypedDict(
    "MessageGroupTypeDef",
    {
        "message": MessageTypeDef,
        "variations": NotRequired[Sequence[MessageTypeDef]],
    },
)
UtteranceSpecificationTypeDef = TypedDict(
    "UtteranceSpecificationTypeDef",
    {
        "botAliasId": NotRequired[str],
        "botVersion": NotRequired[str],
        "localeId": NotRequired[str],
        "sessionId": NotRequired[str],
        "channel": NotRequired[str],
        "mode": NotRequired[AnalyticsModalityType],
        "conversationStartTime": NotRequired[datetime],
        "conversationEndTime": NotRequired[datetime],
        "utterance": NotRequired[str],
        "utteranceTimestamp": NotRequired[datetime],
        "audioVoiceDurationMillis": NotRequired[int],
        "utteranceUnderstood": NotRequired[bool],
        "inputType": NotRequired[str],
        "outputType": NotRequired[str],
        "associatedIntentName": NotRequired[str],
        "associatedSlotName": NotRequired[str],
        "intentState": NotRequired[IntentStateType],
        "dialogActionType": NotRequired[str],
        "botResponseAudioVoiceId": NotRequired[str],
        "slotsFilledInSession": NotRequired[str],
        "utteranceRequestId": NotRequired[str],
        "botResponses": NotRequired[List[UtteranceBotResponseTypeDef]],
    },
)
ConversationLogSettingsTypeDef = TypedDict(
    "ConversationLogSettingsTypeDef",
    {
        "textLogSettings": NotRequired[Sequence[TextLogSettingTypeDef]],
        "audioLogSettings": NotRequired[Sequence[AudioLogSettingTypeDef]],
    },
)
DescribeTestSetGenerationResponseTypeDef = TypedDict(
    "DescribeTestSetGenerationResponseTypeDef",
    {
        "testSetGenerationId": str,
        "testSetGenerationStatus": TestSetGenerationStatusType,
        "failureReasons": List[str],
        "testSetId": str,
        "testSetName": str,
        "description": str,
        "storageLocation": TestSetStorageLocationTypeDef,
        "generationDataSource": TestSetGenerationDataSourceTypeDef,
        "roleArn": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartTestSetGenerationRequestRequestTypeDef = TypedDict(
    "StartTestSetGenerationRequestRequestTypeDef",
    {
        "testSetName": str,
        "storageLocation": TestSetStorageLocationTypeDef,
        "generationDataSource": TestSetGenerationDataSourceTypeDef,
        "roleArn": str,
        "description": NotRequired[str],
        "testSetTags": NotRequired[Mapping[str, str]],
    },
)
StartTestSetGenerationResponseTypeDef = TypedDict(
    "StartTestSetGenerationResponseTypeDef",
    {
        "testSetGenerationId": str,
        "creationDateTime": datetime,
        "testSetGenerationStatus": TestSetGenerationStatusType,
        "testSetName": str,
        "description": str,
        "storageLocation": TestSetStorageLocationTypeDef,
        "generationDataSource": TestSetGenerationDataSourceTypeDef,
        "roleArn": str,
        "testSetTags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
S3BucketTranscriptSourceTypeDef = TypedDict(
    "S3BucketTranscriptSourceTypeDef",
    {
        "s3BucketName": str,
        "transcriptFormat": Literal["Lex"],
        "pathFormat": NotRequired[PathFormatTypeDef],
        "transcriptFilter": NotRequired[TranscriptFilterTypeDef],
        "kmsKeyArn": NotRequired[str],
    },
)
ListExportsResponseTypeDef = TypedDict(
    "ListExportsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "exportSummaries": List[ExportSummaryTypeDef],
        "nextToken": str,
        "localeId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateSlotTypeRequestRequestTypeDef = TypedDict(
    "CreateSlotTypeRequestRequestTypeDef",
    {
        "slotTypeName": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "description": NotRequired[str],
        "slotTypeValues": NotRequired[Sequence[SlotTypeValueTypeDef]],
        "valueSelectionSetting": NotRequired[SlotValueSelectionSettingTypeDef],
        "parentSlotTypeSignature": NotRequired[str],
        "externalSourceSetting": NotRequired[ExternalSourceSettingTypeDef],
        "compositeSlotTypeSetting": NotRequired[CompositeSlotTypeSettingTypeDef],
    },
)
CreateSlotTypeResponseTypeDef = TypedDict(
    "CreateSlotTypeResponseTypeDef",
    {
        "slotTypeId": str,
        "slotTypeName": str,
        "description": str,
        "slotTypeValues": List[SlotTypeValueTypeDef],
        "valueSelectionSetting": SlotValueSelectionSettingTypeDef,
        "parentSlotTypeSignature": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "creationDateTime": datetime,
        "externalSourceSetting": ExternalSourceSettingTypeDef,
        "compositeSlotTypeSetting": CompositeSlotTypeSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSlotTypeResponseTypeDef = TypedDict(
    "DescribeSlotTypeResponseTypeDef",
    {
        "slotTypeId": str,
        "slotTypeName": str,
        "description": str,
        "slotTypeValues": List[SlotTypeValueTypeDef],
        "valueSelectionSetting": SlotValueSelectionSettingTypeDef,
        "parentSlotTypeSignature": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "externalSourceSetting": ExternalSourceSettingTypeDef,
        "compositeSlotTypeSetting": CompositeSlotTypeSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSlotTypeRequestRequestTypeDef = TypedDict(
    "UpdateSlotTypeRequestRequestTypeDef",
    {
        "slotTypeId": str,
        "slotTypeName": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "description": NotRequired[str],
        "slotTypeValues": NotRequired[Sequence[SlotTypeValueTypeDef]],
        "valueSelectionSetting": NotRequired[SlotValueSelectionSettingTypeDef],
        "parentSlotTypeSignature": NotRequired[str],
        "externalSourceSetting": NotRequired[ExternalSourceSettingTypeDef],
        "compositeSlotTypeSetting": NotRequired[CompositeSlotTypeSettingTypeDef],
    },
)
UpdateSlotTypeResponseTypeDef = TypedDict(
    "UpdateSlotTypeResponseTypeDef",
    {
        "slotTypeId": str,
        "slotTypeName": str,
        "description": str,
        "slotTypeValues": List[SlotTypeValueTypeDef],
        "valueSelectionSetting": SlotValueSelectionSettingTypeDef,
        "parentSlotTypeSignature": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "externalSourceSetting": ExternalSourceSettingTypeDef,
        "compositeSlotTypeSetting": CompositeSlotTypeSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IntentLevelSlotResolutionTestResultsTypeDef = TypedDict(
    "IntentLevelSlotResolutionTestResultsTypeDef",
    {
        "items": List[IntentLevelSlotResolutionTestResultItemTypeDef],
    },
)
DescribeImportResponseTypeDef = TypedDict(
    "DescribeImportResponseTypeDef",
    {
        "importId": str,
        "resourceSpecification": ImportResourceSpecificationTypeDef,
        "importedResourceId": str,
        "importedResourceName": str,
        "mergeStrategy": MergeStrategyType,
        "importStatus": ImportStatusType,
        "failureReasons": List[str],
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartImportRequestRequestTypeDef = TypedDict(
    "StartImportRequestRequestTypeDef",
    {
        "importId": str,
        "resourceSpecification": ImportResourceSpecificationTypeDef,
        "mergeStrategy": MergeStrategyType,
        "filePassword": NotRequired[str],
    },
)
StartImportResponseTypeDef = TypedDict(
    "StartImportResponseTypeDef",
    {
        "importId": str,
        "resourceSpecification": ImportResourceSpecificationTypeDef,
        "mergeStrategy": MergeStrategyType,
        "importStatus": ImportStatusType,
        "creationDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UserTurnResultTypeDef = TypedDict(
    "UserTurnResultTypeDef",
    {
        "input": UserTurnInputSpecificationTypeDef,
        "expectedOutput": UserTurnOutputSpecificationTypeDef,
        "actualOutput": NotRequired[UserTurnOutputSpecificationTypeDef],
        "errorDetails": NotRequired[ExecutionErrorDetailsTypeDef],
        "endToEndResult": NotRequired[TestResultMatchStatusType],
        "intentMatchResult": NotRequired[TestResultMatchStatusType],
        "slotMatchResult": NotRequired[TestResultMatchStatusType],
        "speechTranscriptionResult": NotRequired[TestResultMatchStatusType],
        "conversationLevelResult": NotRequired[ConversationLevelResultDetailTypeDef],
    },
)
UserTurnSpecificationTypeDef = TypedDict(
    "UserTurnSpecificationTypeDef",
    {
        "input": UserTurnInputSpecificationTypeDef,
        "expected": UserTurnOutputSpecificationTypeDef,
    },
)
CreateBotLocaleRequestRequestTypeDef = TypedDict(
    "CreateBotLocaleRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "nluIntentConfidenceThreshold": float,
        "description": NotRequired[str],
        "voiceSettings": NotRequired[VoiceSettingsTypeDef],
        "generativeAISettings": NotRequired[GenerativeAISettingsTypeDef],
    },
)
CreateBotLocaleResponseTypeDef = TypedDict(
    "CreateBotLocaleResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeName": str,
        "localeId": str,
        "description": str,
        "nluIntentConfidenceThreshold": float,
        "voiceSettings": VoiceSettingsTypeDef,
        "botLocaleStatus": BotLocaleStatusType,
        "creationDateTime": datetime,
        "generativeAISettings": GenerativeAISettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeBotLocaleResponseTypeDef = TypedDict(
    "DescribeBotLocaleResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "localeName": str,
        "description": str,
        "nluIntentConfidenceThreshold": float,
        "voiceSettings": VoiceSettingsTypeDef,
        "intentsCount": int,
        "slotTypesCount": int,
        "botLocaleStatus": BotLocaleStatusType,
        "failureReasons": List[str],
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "lastBuildSubmittedDateTime": datetime,
        "botLocaleHistoryEvents": List[BotLocaleHistoryEventTypeDef],
        "recommendedActions": List[str],
        "generativeAISettings": GenerativeAISettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBotLocaleRequestRequestTypeDef = TypedDict(
    "UpdateBotLocaleRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "nluIntentConfidenceThreshold": float,
        "description": NotRequired[str],
        "voiceSettings": NotRequired[VoiceSettingsTypeDef],
        "generativeAISettings": NotRequired[GenerativeAISettingsTypeDef],
    },
)
UpdateBotLocaleResponseTypeDef = TypedDict(
    "UpdateBotLocaleResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "localeName": str,
        "description": str,
        "nluIntentConfidenceThreshold": float,
        "voiceSettings": VoiceSettingsTypeDef,
        "botLocaleStatus": BotLocaleStatusType,
        "failureReasons": List[str],
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "recommendedActions": List[str],
        "generativeAISettings": GenerativeAISettingsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FulfillmentStartResponseSpecificationTypeDef = TypedDict(
    "FulfillmentStartResponseSpecificationTypeDef",
    {
        "delayInSeconds": int,
        "messageGroups": Sequence[MessageGroupTypeDef],
        "allowInterrupt": NotRequired[bool],
    },
)
FulfillmentUpdateResponseSpecificationTypeDef = TypedDict(
    "FulfillmentUpdateResponseSpecificationTypeDef",
    {
        "frequencyInSeconds": int,
        "messageGroups": Sequence[MessageGroupTypeDef],
        "allowInterrupt": NotRequired[bool],
    },
)
PromptSpecificationTypeDef = TypedDict(
    "PromptSpecificationTypeDef",
    {
        "messageGroups": Sequence[MessageGroupTypeDef],
        "maxRetries": int,
        "allowInterrupt": NotRequired[bool],
        "messageSelectionStrategy": NotRequired[MessageSelectionStrategyType],
        "promptAttemptsSpecification": NotRequired[
            Mapping[PromptAttemptType, PromptAttemptSpecificationTypeDef]
        ],
    },
)
ResponseSpecificationTypeDef = TypedDict(
    "ResponseSpecificationTypeDef",
    {
        "messageGroups": Sequence[MessageGroupTypeDef],
        "allowInterrupt": NotRequired[bool],
    },
)
StillWaitingResponseSpecificationTypeDef = TypedDict(
    "StillWaitingResponseSpecificationTypeDef",
    {
        "messageGroups": Sequence[MessageGroupTypeDef],
        "frequencyInSeconds": int,
        "timeoutInSeconds": int,
        "allowInterrupt": NotRequired[bool],
    },
)
ListUtteranceAnalyticsDataResponseTypeDef = TypedDict(
    "ListUtteranceAnalyticsDataResponseTypeDef",
    {
        "botId": str,
        "nextToken": str,
        "utterances": List[UtteranceSpecificationTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateBotAliasRequestRequestTypeDef = TypedDict(
    "CreateBotAliasRequestRequestTypeDef",
    {
        "botAliasName": str,
        "botId": str,
        "description": NotRequired[str],
        "botVersion": NotRequired[str],
        "botAliasLocaleSettings": NotRequired[Mapping[str, BotAliasLocaleSettingsTypeDef]],
        "conversationLogSettings": NotRequired[ConversationLogSettingsTypeDef],
        "sentimentAnalysisSettings": NotRequired[SentimentAnalysisSettingsTypeDef],
        "tags": NotRequired[Mapping[str, str]],
    },
)
CreateBotAliasResponseTypeDef = TypedDict(
    "CreateBotAliasResponseTypeDef",
    {
        "botAliasId": str,
        "botAliasName": str,
        "description": str,
        "botVersion": str,
        "botAliasLocaleSettings": Dict[str, BotAliasLocaleSettingsTypeDef],
        "conversationLogSettings": ConversationLogSettingsTypeDef,
        "sentimentAnalysisSettings": SentimentAnalysisSettingsTypeDef,
        "botAliasStatus": BotAliasStatusType,
        "botId": str,
        "creationDateTime": datetime,
        "tags": Dict[str, str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeBotAliasResponseTypeDef = TypedDict(
    "DescribeBotAliasResponseTypeDef",
    {
        "botAliasId": str,
        "botAliasName": str,
        "description": str,
        "botVersion": str,
        "botAliasLocaleSettings": Dict[str, BotAliasLocaleSettingsTypeDef],
        "conversationLogSettings": ConversationLogSettingsTypeDef,
        "sentimentAnalysisSettings": SentimentAnalysisSettingsTypeDef,
        "botAliasHistoryEvents": List[BotAliasHistoryEventTypeDef],
        "botAliasStatus": BotAliasStatusType,
        "botId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "parentBotNetworks": List[ParentBotNetworkTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBotAliasRequestRequestTypeDef = TypedDict(
    "UpdateBotAliasRequestRequestTypeDef",
    {
        "botAliasId": str,
        "botAliasName": str,
        "botId": str,
        "description": NotRequired[str],
        "botVersion": NotRequired[str],
        "botAliasLocaleSettings": NotRequired[Mapping[str, BotAliasLocaleSettingsTypeDef]],
        "conversationLogSettings": NotRequired[ConversationLogSettingsTypeDef],
        "sentimentAnalysisSettings": NotRequired[SentimentAnalysisSettingsTypeDef],
    },
)
UpdateBotAliasResponseTypeDef = TypedDict(
    "UpdateBotAliasResponseTypeDef",
    {
        "botAliasId": str,
        "botAliasName": str,
        "description": str,
        "botVersion": str,
        "botAliasLocaleSettings": Dict[str, BotAliasLocaleSettingsTypeDef],
        "conversationLogSettings": ConversationLogSettingsTypeDef,
        "sentimentAnalysisSettings": SentimentAnalysisSettingsTypeDef,
        "botAliasStatus": BotAliasStatusType,
        "botId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TranscriptSourceSettingTypeDef = TypedDict(
    "TranscriptSourceSettingTypeDef",
    {
        "s3BucketTranscriptSource": NotRequired[S3BucketTranscriptSourceTypeDef],
    },
)
TestSetTurnResultTypeDef = TypedDict(
    "TestSetTurnResultTypeDef",
    {
        "agent": NotRequired[AgentTurnResultTypeDef],
        "user": NotRequired[UserTurnResultTypeDef],
    },
)
TurnSpecificationTypeDef = TypedDict(
    "TurnSpecificationTypeDef",
    {
        "agentTurn": NotRequired[AgentTurnSpecificationTypeDef],
        "userTurn": NotRequired[UserTurnSpecificationTypeDef],
    },
)
FulfillmentUpdatesSpecificationTypeDef = TypedDict(
    "FulfillmentUpdatesSpecificationTypeDef",
    {
        "active": bool,
        "startResponse": NotRequired[FulfillmentStartResponseSpecificationTypeDef],
        "updateResponse": NotRequired[FulfillmentUpdateResponseSpecificationTypeDef],
        "timeoutInSeconds": NotRequired[int],
    },
)
SlotSummaryTypeDef = TypedDict(
    "SlotSummaryTypeDef",
    {
        "slotId": NotRequired[str],
        "slotName": NotRequired[str],
        "description": NotRequired[str],
        "slotConstraint": NotRequired[SlotConstraintType],
        "slotTypeId": NotRequired[str],
        "valueElicitationPromptSpecification": NotRequired[PromptSpecificationTypeDef],
        "lastUpdatedDateTime": NotRequired[datetime],
    },
)
ConditionalBranchTypeDef = TypedDict(
    "ConditionalBranchTypeDef",
    {
        "name": str,
        "condition": ConditionTypeDef,
        "nextStep": DialogStateTypeDef,
        "response": NotRequired[ResponseSpecificationTypeDef],
    },
)
DefaultConditionalBranchTypeDef = TypedDict(
    "DefaultConditionalBranchTypeDef",
    {
        "nextStep": NotRequired[DialogStateTypeDef],
        "response": NotRequired[ResponseSpecificationTypeDef],
    },
)
WaitAndContinueSpecificationTypeDef = TypedDict(
    "WaitAndContinueSpecificationTypeDef",
    {
        "waitingResponse": ResponseSpecificationTypeDef,
        "continueResponse": ResponseSpecificationTypeDef,
        "stillWaitingResponse": NotRequired[StillWaitingResponseSpecificationTypeDef],
        "active": NotRequired[bool],
    },
)
DescribeBotRecommendationResponseTypeDef = TypedDict(
    "DescribeBotRecommendationResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationStatus": BotRecommendationStatusType,
        "botRecommendationId": str,
        "failureReasons": List[str],
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "transcriptSourceSetting": TranscriptSourceSettingTypeDef,
        "encryptionSetting": EncryptionSettingTypeDef,
        "botRecommendationResults": BotRecommendationResultsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartBotRecommendationRequestRequestTypeDef = TypedDict(
    "StartBotRecommendationRequestRequestTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "transcriptSourceSetting": TranscriptSourceSettingTypeDef,
        "encryptionSetting": NotRequired[EncryptionSettingTypeDef],
    },
)
StartBotRecommendationResponseTypeDef = TypedDict(
    "StartBotRecommendationResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationStatus": BotRecommendationStatusType,
        "botRecommendationId": str,
        "creationDateTime": datetime,
        "transcriptSourceSetting": TranscriptSourceSettingTypeDef,
        "encryptionSetting": EncryptionSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateBotRecommendationResponseTypeDef = TypedDict(
    "UpdateBotRecommendationResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "botRecommendationStatus": BotRecommendationStatusType,
        "botRecommendationId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "transcriptSourceSetting": TranscriptSourceSettingTypeDef,
        "encryptionSetting": EncryptionSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UtteranceLevelTestResultItemTypeDef = TypedDict(
    "UtteranceLevelTestResultItemTypeDef",
    {
        "recordNumber": int,
        "turnResult": TestSetTurnResultTypeDef,
        "conversationId": NotRequired[str],
    },
)
TestSetTurnRecordTypeDef = TypedDict(
    "TestSetTurnRecordTypeDef",
    {
        "recordNumber": int,
        "turnSpecification": TurnSpecificationTypeDef,
        "conversationId": NotRequired[str],
        "turnNumber": NotRequired[int],
    },
)
ListSlotsResponseTypeDef = TypedDict(
    "ListSlotsResponseTypeDef",
    {
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "slotSummaries": List[SlotSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ConditionalSpecificationTypeDef = TypedDict(
    "ConditionalSpecificationTypeDef",
    {
        "active": bool,
        "conditionalBranches": Sequence[ConditionalBranchTypeDef],
        "defaultBranch": DefaultConditionalBranchTypeDef,
    },
)
SubSlotValueElicitationSettingTypeDef = TypedDict(
    "SubSlotValueElicitationSettingTypeDef",
    {
        "promptSpecification": PromptSpecificationTypeDef,
        "defaultValueSpecification": NotRequired[SlotDefaultValueSpecificationTypeDef],
        "sampleUtterances": NotRequired[Sequence[SampleUtteranceTypeDef]],
        "waitAndContinueSpecification": NotRequired[WaitAndContinueSpecificationTypeDef],
    },
)
UtteranceLevelTestResultsTypeDef = TypedDict(
    "UtteranceLevelTestResultsTypeDef",
    {
        "items": List[UtteranceLevelTestResultItemTypeDef],
    },
)
ListTestSetRecordsResponseTypeDef = TypedDict(
    "ListTestSetRecordsResponseTypeDef",
    {
        "testSetRecords": List[TestSetTurnRecordTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
IntentClosingSettingTypeDef = TypedDict(
    "IntentClosingSettingTypeDef",
    {
        "closingResponse": NotRequired[ResponseSpecificationTypeDef],
        "active": NotRequired[bool],
        "nextStep": NotRequired[DialogStateTypeDef],
        "conditional": NotRequired[ConditionalSpecificationTypeDef],
    },
)
PostDialogCodeHookInvocationSpecificationTypeDef = TypedDict(
    "PostDialogCodeHookInvocationSpecificationTypeDef",
    {
        "successResponse": NotRequired[ResponseSpecificationTypeDef],
        "successNextStep": NotRequired[DialogStateTypeDef],
        "successConditional": NotRequired[ConditionalSpecificationTypeDef],
        "failureResponse": NotRequired[ResponseSpecificationTypeDef],
        "failureNextStep": NotRequired[DialogStateTypeDef],
        "failureConditional": NotRequired[ConditionalSpecificationTypeDef],
        "timeoutResponse": NotRequired[ResponseSpecificationTypeDef],
        "timeoutNextStep": NotRequired[DialogStateTypeDef],
        "timeoutConditional": NotRequired[ConditionalSpecificationTypeDef],
    },
)
PostFulfillmentStatusSpecificationTypeDef = TypedDict(
    "PostFulfillmentStatusSpecificationTypeDef",
    {
        "successResponse": NotRequired[ResponseSpecificationTypeDef],
        "failureResponse": NotRequired[ResponseSpecificationTypeDef],
        "timeoutResponse": NotRequired[ResponseSpecificationTypeDef],
        "successNextStep": NotRequired[DialogStateTypeDef],
        "successConditional": NotRequired[ConditionalSpecificationTypeDef],
        "failureNextStep": NotRequired[DialogStateTypeDef],
        "failureConditional": NotRequired[ConditionalSpecificationTypeDef],
        "timeoutNextStep": NotRequired[DialogStateTypeDef],
        "timeoutConditional": NotRequired[ConditionalSpecificationTypeDef],
    },
)
SpecificationsTypeDef = TypedDict(
    "SpecificationsTypeDef",
    {
        "slotTypeId": str,
        "valueElicitationSetting": SubSlotValueElicitationSettingTypeDef,
    },
)
TestExecutionResultItemsTypeDef = TypedDict(
    "TestExecutionResultItemsTypeDef",
    {
        "overallTestResults": NotRequired[OverallTestResultsTypeDef],
        "conversationLevelTestResults": NotRequired[ConversationLevelTestResultsTypeDef],
        "intentClassificationTestResults": NotRequired[IntentClassificationTestResultsTypeDef],
        "intentLevelSlotResolutionTestResults": NotRequired[
            IntentLevelSlotResolutionTestResultsTypeDef
        ],
        "utteranceLevelTestResults": NotRequired[UtteranceLevelTestResultsTypeDef],
    },
)
DialogCodeHookInvocationSettingTypeDef = TypedDict(
    "DialogCodeHookInvocationSettingTypeDef",
    {
        "enableCodeHookInvocation": bool,
        "active": bool,
        "postCodeHookSpecification": PostDialogCodeHookInvocationSpecificationTypeDef,
        "invocationLabel": NotRequired[str],
    },
)
FulfillmentCodeHookSettingsTypeDef = TypedDict(
    "FulfillmentCodeHookSettingsTypeDef",
    {
        "enabled": bool,
        "postFulfillmentStatusSpecification": NotRequired[
            PostFulfillmentStatusSpecificationTypeDef
        ],
        "fulfillmentUpdatesSpecification": NotRequired[FulfillmentUpdatesSpecificationTypeDef],
        "active": NotRequired[bool],
    },
)
SubSlotSettingTypeDef = TypedDict(
    "SubSlotSettingTypeDef",
    {
        "expression": NotRequired[str],
        "slotSpecifications": NotRequired[Mapping[str, SpecificationsTypeDef]],
    },
)
ListTestExecutionResultItemsResponseTypeDef = TypedDict(
    "ListTestExecutionResultItemsResponseTypeDef",
    {
        "testExecutionResults": TestExecutionResultItemsTypeDef,
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
InitialResponseSettingTypeDef = TypedDict(
    "InitialResponseSettingTypeDef",
    {
        "initialResponse": NotRequired[ResponseSpecificationTypeDef],
        "nextStep": NotRequired[DialogStateTypeDef],
        "conditional": NotRequired[ConditionalSpecificationTypeDef],
        "codeHook": NotRequired[DialogCodeHookInvocationSettingTypeDef],
    },
)
IntentConfirmationSettingTypeDef = TypedDict(
    "IntentConfirmationSettingTypeDef",
    {
        "promptSpecification": PromptSpecificationTypeDef,
        "declinationResponse": NotRequired[ResponseSpecificationTypeDef],
        "active": NotRequired[bool],
        "confirmationResponse": NotRequired[ResponseSpecificationTypeDef],
        "confirmationNextStep": NotRequired[DialogStateTypeDef],
        "confirmationConditional": NotRequired[ConditionalSpecificationTypeDef],
        "declinationNextStep": NotRequired[DialogStateTypeDef],
        "declinationConditional": NotRequired[ConditionalSpecificationTypeDef],
        "failureResponse": NotRequired[ResponseSpecificationTypeDef],
        "failureNextStep": NotRequired[DialogStateTypeDef],
        "failureConditional": NotRequired[ConditionalSpecificationTypeDef],
        "codeHook": NotRequired[DialogCodeHookInvocationSettingTypeDef],
        "elicitationCodeHook": NotRequired[ElicitationCodeHookInvocationSettingTypeDef],
    },
)
SlotCaptureSettingTypeDef = TypedDict(
    "SlotCaptureSettingTypeDef",
    {
        "captureResponse": NotRequired[ResponseSpecificationTypeDef],
        "captureNextStep": NotRequired[DialogStateTypeDef],
        "captureConditional": NotRequired[ConditionalSpecificationTypeDef],
        "failureResponse": NotRequired[ResponseSpecificationTypeDef],
        "failureNextStep": NotRequired[DialogStateTypeDef],
        "failureConditional": NotRequired[ConditionalSpecificationTypeDef],
        "codeHook": NotRequired[DialogCodeHookInvocationSettingTypeDef],
        "elicitationCodeHook": NotRequired[ElicitationCodeHookInvocationSettingTypeDef],
    },
)
CreateIntentRequestRequestTypeDef = TypedDict(
    "CreateIntentRequestRequestTypeDef",
    {
        "intentName": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "description": NotRequired[str],
        "parentIntentSignature": NotRequired[str],
        "sampleUtterances": NotRequired[Sequence[SampleUtteranceTypeDef]],
        "dialogCodeHook": NotRequired[DialogCodeHookSettingsTypeDef],
        "fulfillmentCodeHook": NotRequired[FulfillmentCodeHookSettingsTypeDef],
        "intentConfirmationSetting": NotRequired[IntentConfirmationSettingTypeDef],
        "intentClosingSetting": NotRequired[IntentClosingSettingTypeDef],
        "inputContexts": NotRequired[Sequence[InputContextTypeDef]],
        "outputContexts": NotRequired[Sequence[OutputContextTypeDef]],
        "kendraConfiguration": NotRequired[KendraConfigurationTypeDef],
        "initialResponseSetting": NotRequired[InitialResponseSettingTypeDef],
    },
)
CreateIntentResponseTypeDef = TypedDict(
    "CreateIntentResponseTypeDef",
    {
        "intentId": str,
        "intentName": str,
        "description": str,
        "parentIntentSignature": str,
        "sampleUtterances": List[SampleUtteranceTypeDef],
        "dialogCodeHook": DialogCodeHookSettingsTypeDef,
        "fulfillmentCodeHook": FulfillmentCodeHookSettingsTypeDef,
        "intentConfirmationSetting": IntentConfirmationSettingTypeDef,
        "intentClosingSetting": IntentClosingSettingTypeDef,
        "inputContexts": List[InputContextTypeDef],
        "outputContexts": List[OutputContextTypeDef],
        "kendraConfiguration": KendraConfigurationTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "creationDateTime": datetime,
        "initialResponseSetting": InitialResponseSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeIntentResponseTypeDef = TypedDict(
    "DescribeIntentResponseTypeDef",
    {
        "intentId": str,
        "intentName": str,
        "description": str,
        "parentIntentSignature": str,
        "sampleUtterances": List[SampleUtteranceTypeDef],
        "dialogCodeHook": DialogCodeHookSettingsTypeDef,
        "fulfillmentCodeHook": FulfillmentCodeHookSettingsTypeDef,
        "slotPriorities": List[SlotPriorityTypeDef],
        "intentConfirmationSetting": IntentConfirmationSettingTypeDef,
        "intentClosingSetting": IntentClosingSettingTypeDef,
        "inputContexts": List[InputContextTypeDef],
        "outputContexts": List[OutputContextTypeDef],
        "kendraConfiguration": KendraConfigurationTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "initialResponseSetting": InitialResponseSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateIntentRequestRequestTypeDef = TypedDict(
    "UpdateIntentRequestRequestTypeDef",
    {
        "intentId": str,
        "intentName": str,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "description": NotRequired[str],
        "parentIntentSignature": NotRequired[str],
        "sampleUtterances": NotRequired[Sequence[SampleUtteranceTypeDef]],
        "dialogCodeHook": NotRequired[DialogCodeHookSettingsTypeDef],
        "fulfillmentCodeHook": NotRequired[FulfillmentCodeHookSettingsTypeDef],
        "slotPriorities": NotRequired[Sequence[SlotPriorityTypeDef]],
        "intentConfirmationSetting": NotRequired[IntentConfirmationSettingTypeDef],
        "intentClosingSetting": NotRequired[IntentClosingSettingTypeDef],
        "inputContexts": NotRequired[Sequence[InputContextTypeDef]],
        "outputContexts": NotRequired[Sequence[OutputContextTypeDef]],
        "kendraConfiguration": NotRequired[KendraConfigurationTypeDef],
        "initialResponseSetting": NotRequired[InitialResponseSettingTypeDef],
    },
)
UpdateIntentResponseTypeDef = TypedDict(
    "UpdateIntentResponseTypeDef",
    {
        "intentId": str,
        "intentName": str,
        "description": str,
        "parentIntentSignature": str,
        "sampleUtterances": List[SampleUtteranceTypeDef],
        "dialogCodeHook": DialogCodeHookSettingsTypeDef,
        "fulfillmentCodeHook": FulfillmentCodeHookSettingsTypeDef,
        "slotPriorities": List[SlotPriorityTypeDef],
        "intentConfirmationSetting": IntentConfirmationSettingTypeDef,
        "intentClosingSetting": IntentClosingSettingTypeDef,
        "inputContexts": List[InputContextTypeDef],
        "outputContexts": List[OutputContextTypeDef],
        "kendraConfiguration": KendraConfigurationTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "initialResponseSetting": InitialResponseSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
SlotValueElicitationSettingTypeDef = TypedDict(
    "SlotValueElicitationSettingTypeDef",
    {
        "slotConstraint": SlotConstraintType,
        "defaultValueSpecification": NotRequired[SlotDefaultValueSpecificationTypeDef],
        "promptSpecification": NotRequired[PromptSpecificationTypeDef],
        "sampleUtterances": NotRequired[Sequence[SampleUtteranceTypeDef]],
        "waitAndContinueSpecification": NotRequired[WaitAndContinueSpecificationTypeDef],
        "slotCaptureSetting": NotRequired[SlotCaptureSettingTypeDef],
        "slotResolutionSetting": NotRequired[SlotResolutionSettingTypeDef],
    },
)
CreateSlotRequestRequestTypeDef = TypedDict(
    "CreateSlotRequestRequestTypeDef",
    {
        "slotName": str,
        "valueElicitationSetting": SlotValueElicitationSettingTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "description": NotRequired[str],
        "slotTypeId": NotRequired[str],
        "obfuscationSetting": NotRequired[ObfuscationSettingTypeDef],
        "multipleValuesSetting": NotRequired[MultipleValuesSettingTypeDef],
        "subSlotSetting": NotRequired[SubSlotSettingTypeDef],
    },
)
CreateSlotResponseTypeDef = TypedDict(
    "CreateSlotResponseTypeDef",
    {
        "slotId": str,
        "slotName": str,
        "description": str,
        "slotTypeId": str,
        "valueElicitationSetting": SlotValueElicitationSettingTypeDef,
        "obfuscationSetting": ObfuscationSettingTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "creationDateTime": datetime,
        "multipleValuesSetting": MultipleValuesSettingTypeDef,
        "subSlotSetting": SubSlotSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeSlotResponseTypeDef = TypedDict(
    "DescribeSlotResponseTypeDef",
    {
        "slotId": str,
        "slotName": str,
        "description": str,
        "slotTypeId": str,
        "valueElicitationSetting": SlotValueElicitationSettingTypeDef,
        "obfuscationSetting": ObfuscationSettingTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "multipleValuesSetting": MultipleValuesSettingTypeDef,
        "subSlotSetting": SubSlotSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateSlotRequestRequestTypeDef = TypedDict(
    "UpdateSlotRequestRequestTypeDef",
    {
        "slotId": str,
        "slotName": str,
        "valueElicitationSetting": SlotValueElicitationSettingTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "description": NotRequired[str],
        "slotTypeId": NotRequired[str],
        "obfuscationSetting": NotRequired[ObfuscationSettingTypeDef],
        "multipleValuesSetting": NotRequired[MultipleValuesSettingTypeDef],
        "subSlotSetting": NotRequired[SubSlotSettingTypeDef],
    },
)
UpdateSlotResponseTypeDef = TypedDict(
    "UpdateSlotResponseTypeDef",
    {
        "slotId": str,
        "slotName": str,
        "description": str,
        "slotTypeId": str,
        "valueElicitationSetting": SlotValueElicitationSettingTypeDef,
        "obfuscationSetting": ObfuscationSettingTypeDef,
        "botId": str,
        "botVersion": str,
        "localeId": str,
        "intentId": str,
        "creationDateTime": datetime,
        "lastUpdatedDateTime": datetime,
        "multipleValuesSetting": MultipleValuesSettingTypeDef,
        "subSlotSetting": SubSlotSettingTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
