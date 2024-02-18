"""
Type annotations for codepipeline service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_codepipeline/type_defs/)

Usage::

    ```python
    from mypy_boto3_codepipeline.type_defs import AWSSessionCredentialsTypeDef

    data: AWSSessionCredentialsTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Mapping, Sequence, Union

from .literals import (
    ActionCategoryType,
    ActionConfigurationPropertyTypeType,
    ActionExecutionStatusType,
    ActionOwnerType,
    ApprovalStatusType,
    ExecutionModeType,
    ExecutorTypeType,
    FailureTypeType,
    GitPullRequestEventTypeType,
    JobStatusType,
    PipelineExecutionStatusType,
    PipelineTypeType,
    SourceRevisionTypeType,
    StageExecutionStatusType,
    StageRetryModeType,
    StageTransitionTypeType,
    StartTimeRangeType,
    TriggerTypeType,
    WebhookAuthenticationTypeType,
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
    "AWSSessionCredentialsTypeDef",
    "AcknowledgeJobInputRequestTypeDef",
    "ResponseMetadataTypeDef",
    "AcknowledgeThirdPartyJobInputRequestTypeDef",
    "ActionConfigurationPropertyTypeDef",
    "ActionConfigurationTypeDef",
    "ActionContextTypeDef",
    "ActionTypeIdTypeDef",
    "InputArtifactTypeDef",
    "OutputArtifactTypeDef",
    "LatestInPipelineExecutionFilterTypeDef",
    "ErrorDetailsTypeDef",
    "ActionRevisionTypeDef",
    "ActionTypeArtifactDetailsTypeDef",
    "ActionTypeIdentifierTypeDef",
    "ActionTypePermissionsTypeDef",
    "ActionTypePropertyTypeDef",
    "ActionTypeUrlsTypeDef",
    "ActionTypeSettingsTypeDef",
    "ArtifactDetailsTypeDef",
    "ApprovalResultTypeDef",
    "S3LocationTypeDef",
    "S3ArtifactLocationTypeDef",
    "ArtifactRevisionTypeDef",
    "EncryptionKeyTypeDef",
    "BlockerDeclarationTypeDef",
    "TagTypeDef",
    "TimestampTypeDef",
    "DeleteCustomActionTypeInputRequestTypeDef",
    "DeletePipelineInputRequestTypeDef",
    "DeleteWebhookInputRequestTypeDef",
    "DeregisterWebhookWithThirdPartyInputRequestTypeDef",
    "DisableStageTransitionInputRequestTypeDef",
    "EnableStageTransitionInputRequestTypeDef",
    "ExecutionDetailsTypeDef",
    "ExecutionTriggerTypeDef",
    "JobWorkerExecutorConfigurationTypeDef",
    "LambdaExecutorConfigurationTypeDef",
    "FailureDetailsTypeDef",
    "GetActionTypeInputRequestTypeDef",
    "GetJobDetailsInputRequestTypeDef",
    "GetPipelineExecutionInputRequestTypeDef",
    "GetPipelineInputRequestTypeDef",
    "PipelineMetadataTypeDef",
    "GetPipelineStateInputRequestTypeDef",
    "GetThirdPartyJobDetailsInputRequestTypeDef",
    "GitBranchFilterCriteriaTypeDef",
    "GitFilePathFilterCriteriaTypeDef",
    "GitTagFilterCriteriaTypeDef",
    "PaginatorConfigTypeDef",
    "ListActionTypesInputRequestTypeDef",
    "ListPipelineExecutionsInputRequestTypeDef",
    "ListPipelinesInputRequestTypeDef",
    "PipelineSummaryTypeDef",
    "ListTagsForResourceInputRequestTypeDef",
    "ListWebhooksInputRequestTypeDef",
    "StageContextTypeDef",
    "PipelineVariableDeclarationTypeDef",
    "SourceRevisionTypeDef",
    "StopExecutionTriggerTypeDef",
    "ResolvedPipelineVariableTypeDef",
    "PipelineVariableTypeDef",
    "ThirdPartyJobTypeDef",
    "RegisterWebhookWithThirdPartyInputRequestTypeDef",
    "RetryStageExecutionInputRequestTypeDef",
    "SourceRevisionOverrideTypeDef",
    "StageExecutionTypeDef",
    "TransitionStateTypeDef",
    "StopPipelineExecutionInputRequestTypeDef",
    "UntagResourceInputRequestTypeDef",
    "WebhookAuthConfigurationTypeDef",
    "WebhookFilterRuleTypeDef",
    "AcknowledgeJobOutputTypeDef",
    "AcknowledgeThirdPartyJobOutputTypeDef",
    "EmptyResponseMetadataTypeDef",
    "PutActionRevisionOutputTypeDef",
    "PutApprovalResultOutputTypeDef",
    "RetryStageExecutionOutputTypeDef",
    "StartPipelineExecutionOutputTypeDef",
    "StopPipelineExecutionOutputTypeDef",
    "PollForJobsInputRequestTypeDef",
    "PollForThirdPartyJobsInputRequestTypeDef",
    "ActionDeclarationTypeDef",
    "ActionExecutionFilterTypeDef",
    "ActionExecutionResultTypeDef",
    "ActionExecutionTypeDef",
    "PutActionRevisionInputRequestTypeDef",
    "ActionTypeTypeDef",
    "PutApprovalResultInputRequestTypeDef",
    "ArtifactDetailTypeDef",
    "ArtifactLocationTypeDef",
    "ArtifactStoreTypeDef",
    "CreateCustomActionTypeInputRequestTypeDef",
    "ListTagsForResourceOutputTypeDef",
    "TagResourceInputRequestTypeDef",
    "CurrentRevisionTypeDef",
    "ExecutorConfigurationTypeDef",
    "PutJobFailureResultInputRequestTypeDef",
    "PutThirdPartyJobFailureResultInputRequestTypeDef",
    "GitPullRequestFilterTypeDef",
    "GitPushFilterTypeDef",
    "ListActionTypesInputListActionTypesPaginateTypeDef",
    "ListPipelineExecutionsInputListPipelineExecutionsPaginateTypeDef",
    "ListPipelinesInputListPipelinesPaginateTypeDef",
    "ListTagsForResourceInputListTagsForResourcePaginateTypeDef",
    "ListWebhooksInputListWebhooksPaginateTypeDef",
    "ListPipelinesOutputTypeDef",
    "PipelineContextTypeDef",
    "PipelineExecutionSummaryTypeDef",
    "PipelineExecutionTypeDef",
    "PollForThirdPartyJobsOutputTypeDef",
    "StartPipelineExecutionInputRequestTypeDef",
    "WebhookDefinitionTypeDef",
    "StageDeclarationTypeDef",
    "ListActionExecutionsInputListActionExecutionsPaginateTypeDef",
    "ListActionExecutionsInputRequestTypeDef",
    "ActionStateTypeDef",
    "CreateCustomActionTypeOutputTypeDef",
    "ListActionTypesOutputTypeDef",
    "ActionExecutionInputTypeDef",
    "ActionExecutionOutputTypeDef",
    "ArtifactTypeDef",
    "PutJobSuccessResultInputRequestTypeDef",
    "PutThirdPartyJobSuccessResultInputRequestTypeDef",
    "ActionTypeExecutorTypeDef",
    "GitConfigurationTypeDef",
    "ListPipelineExecutionsOutputTypeDef",
    "GetPipelineExecutionOutputTypeDef",
    "ListWebhookItemTypeDef",
    "PutWebhookInputRequestTypeDef",
    "StageStateTypeDef",
    "ActionExecutionDetailTypeDef",
    "JobDataTypeDef",
    "ThirdPartyJobDataTypeDef",
    "ActionTypeDeclarationTypeDef",
    "PipelineTriggerDeclarationTypeDef",
    "ListWebhooksOutputTypeDef",
    "PutWebhookOutputTypeDef",
    "GetPipelineStateOutputTypeDef",
    "ListActionExecutionsOutputTypeDef",
    "JobDetailsTypeDef",
    "JobTypeDef",
    "ThirdPartyJobDetailsTypeDef",
    "GetActionTypeOutputTypeDef",
    "UpdateActionTypeInputRequestTypeDef",
    "PipelineDeclarationTypeDef",
    "GetJobDetailsOutputTypeDef",
    "PollForJobsOutputTypeDef",
    "GetThirdPartyJobDetailsOutputTypeDef",
    "CreatePipelineInputRequestTypeDef",
    "CreatePipelineOutputTypeDef",
    "GetPipelineOutputTypeDef",
    "UpdatePipelineInputRequestTypeDef",
    "UpdatePipelineOutputTypeDef",
)

AWSSessionCredentialsTypeDef = TypedDict(
    "AWSSessionCredentialsTypeDef",
    {
        "accessKeyId": str,
        "secretAccessKey": str,
        "sessionToken": str,
    },
)
AcknowledgeJobInputRequestTypeDef = TypedDict(
    "AcknowledgeJobInputRequestTypeDef",
    {
        "jobId": str,
        "nonce": str,
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
AcknowledgeThirdPartyJobInputRequestTypeDef = TypedDict(
    "AcknowledgeThirdPartyJobInputRequestTypeDef",
    {
        "jobId": str,
        "nonce": str,
        "clientToken": str,
    },
)
ActionConfigurationPropertyTypeDef = TypedDict(
    "ActionConfigurationPropertyTypeDef",
    {
        "name": str,
        "required": bool,
        "key": bool,
        "secret": bool,
        "queryable": NotRequired[bool],
        "description": NotRequired[str],
        "type": NotRequired[ActionConfigurationPropertyTypeType],
    },
)
ActionConfigurationTypeDef = TypedDict(
    "ActionConfigurationTypeDef",
    {
        "configuration": NotRequired[Dict[str, str]],
    },
)
ActionContextTypeDef = TypedDict(
    "ActionContextTypeDef",
    {
        "name": NotRequired[str],
        "actionExecutionId": NotRequired[str],
    },
)
ActionTypeIdTypeDef = TypedDict(
    "ActionTypeIdTypeDef",
    {
        "category": ActionCategoryType,
        "owner": ActionOwnerType,
        "provider": str,
        "version": str,
    },
)
InputArtifactTypeDef = TypedDict(
    "InputArtifactTypeDef",
    {
        "name": str,
    },
)
OutputArtifactTypeDef = TypedDict(
    "OutputArtifactTypeDef",
    {
        "name": str,
    },
)
LatestInPipelineExecutionFilterTypeDef = TypedDict(
    "LatestInPipelineExecutionFilterTypeDef",
    {
        "pipelineExecutionId": str,
        "startTimeRange": StartTimeRangeType,
    },
)
ErrorDetailsTypeDef = TypedDict(
    "ErrorDetailsTypeDef",
    {
        "code": NotRequired[str],
        "message": NotRequired[str],
    },
)
ActionRevisionTypeDef = TypedDict(
    "ActionRevisionTypeDef",
    {
        "revisionId": str,
        "revisionChangeId": str,
        "created": datetime,
    },
)
ActionTypeArtifactDetailsTypeDef = TypedDict(
    "ActionTypeArtifactDetailsTypeDef",
    {
        "minimumCount": int,
        "maximumCount": int,
    },
)
ActionTypeIdentifierTypeDef = TypedDict(
    "ActionTypeIdentifierTypeDef",
    {
        "category": ActionCategoryType,
        "owner": str,
        "provider": str,
        "version": str,
    },
)
ActionTypePermissionsTypeDef = TypedDict(
    "ActionTypePermissionsTypeDef",
    {
        "allowedAccounts": List[str],
    },
)
ActionTypePropertyTypeDef = TypedDict(
    "ActionTypePropertyTypeDef",
    {
        "name": str,
        "optional": bool,
        "key": bool,
        "noEcho": bool,
        "queryable": NotRequired[bool],
        "description": NotRequired[str],
    },
)
ActionTypeUrlsTypeDef = TypedDict(
    "ActionTypeUrlsTypeDef",
    {
        "configurationUrl": NotRequired[str],
        "entityUrlTemplate": NotRequired[str],
        "executionUrlTemplate": NotRequired[str],
        "revisionUrlTemplate": NotRequired[str],
    },
)
ActionTypeSettingsTypeDef = TypedDict(
    "ActionTypeSettingsTypeDef",
    {
        "thirdPartyConfigurationUrl": NotRequired[str],
        "entityUrlTemplate": NotRequired[str],
        "executionUrlTemplate": NotRequired[str],
        "revisionUrlTemplate": NotRequired[str],
    },
)
ArtifactDetailsTypeDef = TypedDict(
    "ArtifactDetailsTypeDef",
    {
        "minimumCount": int,
        "maximumCount": int,
    },
)
ApprovalResultTypeDef = TypedDict(
    "ApprovalResultTypeDef",
    {
        "summary": str,
        "status": ApprovalStatusType,
    },
)
S3LocationTypeDef = TypedDict(
    "S3LocationTypeDef",
    {
        "bucket": NotRequired[str],
        "key": NotRequired[str],
    },
)
S3ArtifactLocationTypeDef = TypedDict(
    "S3ArtifactLocationTypeDef",
    {
        "bucketName": str,
        "objectKey": str,
    },
)
ArtifactRevisionTypeDef = TypedDict(
    "ArtifactRevisionTypeDef",
    {
        "name": NotRequired[str],
        "revisionId": NotRequired[str],
        "revisionChangeIdentifier": NotRequired[str],
        "revisionSummary": NotRequired[str],
        "created": NotRequired[datetime],
        "revisionUrl": NotRequired[str],
    },
)
EncryptionKeyTypeDef = TypedDict(
    "EncryptionKeyTypeDef",
    {
        "id": str,
        "type": Literal["KMS"],
    },
)
BlockerDeclarationTypeDef = TypedDict(
    "BlockerDeclarationTypeDef",
    {
        "name": str,
        "type": Literal["Schedule"],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": str,
        "value": str,
    },
)
TimestampTypeDef = Union[datetime, str]
DeleteCustomActionTypeInputRequestTypeDef = TypedDict(
    "DeleteCustomActionTypeInputRequestTypeDef",
    {
        "category": ActionCategoryType,
        "provider": str,
        "version": str,
    },
)
DeletePipelineInputRequestTypeDef = TypedDict(
    "DeletePipelineInputRequestTypeDef",
    {
        "name": str,
    },
)
DeleteWebhookInputRequestTypeDef = TypedDict(
    "DeleteWebhookInputRequestTypeDef",
    {
        "name": str,
    },
)
DeregisterWebhookWithThirdPartyInputRequestTypeDef = TypedDict(
    "DeregisterWebhookWithThirdPartyInputRequestTypeDef",
    {
        "webhookName": NotRequired[str],
    },
)
DisableStageTransitionInputRequestTypeDef = TypedDict(
    "DisableStageTransitionInputRequestTypeDef",
    {
        "pipelineName": str,
        "stageName": str,
        "transitionType": StageTransitionTypeType,
        "reason": str,
    },
)
EnableStageTransitionInputRequestTypeDef = TypedDict(
    "EnableStageTransitionInputRequestTypeDef",
    {
        "pipelineName": str,
        "stageName": str,
        "transitionType": StageTransitionTypeType,
    },
)
ExecutionDetailsTypeDef = TypedDict(
    "ExecutionDetailsTypeDef",
    {
        "summary": NotRequired[str],
        "externalExecutionId": NotRequired[str],
        "percentComplete": NotRequired[int],
    },
)
ExecutionTriggerTypeDef = TypedDict(
    "ExecutionTriggerTypeDef",
    {
        "triggerType": NotRequired[TriggerTypeType],
        "triggerDetail": NotRequired[str],
    },
)
JobWorkerExecutorConfigurationTypeDef = TypedDict(
    "JobWorkerExecutorConfigurationTypeDef",
    {
        "pollingAccounts": NotRequired[List[str]],
        "pollingServicePrincipals": NotRequired[List[str]],
    },
)
LambdaExecutorConfigurationTypeDef = TypedDict(
    "LambdaExecutorConfigurationTypeDef",
    {
        "lambdaFunctionArn": str,
    },
)
FailureDetailsTypeDef = TypedDict(
    "FailureDetailsTypeDef",
    {
        "type": FailureTypeType,
        "message": str,
        "externalExecutionId": NotRequired[str],
    },
)
GetActionTypeInputRequestTypeDef = TypedDict(
    "GetActionTypeInputRequestTypeDef",
    {
        "category": ActionCategoryType,
        "owner": str,
        "provider": str,
        "version": str,
    },
)
GetJobDetailsInputRequestTypeDef = TypedDict(
    "GetJobDetailsInputRequestTypeDef",
    {
        "jobId": str,
    },
)
GetPipelineExecutionInputRequestTypeDef = TypedDict(
    "GetPipelineExecutionInputRequestTypeDef",
    {
        "pipelineName": str,
        "pipelineExecutionId": str,
    },
)
GetPipelineInputRequestTypeDef = TypedDict(
    "GetPipelineInputRequestTypeDef",
    {
        "name": str,
        "version": NotRequired[int],
    },
)
PipelineMetadataTypeDef = TypedDict(
    "PipelineMetadataTypeDef",
    {
        "pipelineArn": NotRequired[str],
        "created": NotRequired[datetime],
        "updated": NotRequired[datetime],
        "pollingDisabledAt": NotRequired[datetime],
    },
)
GetPipelineStateInputRequestTypeDef = TypedDict(
    "GetPipelineStateInputRequestTypeDef",
    {
        "name": str,
    },
)
GetThirdPartyJobDetailsInputRequestTypeDef = TypedDict(
    "GetThirdPartyJobDetailsInputRequestTypeDef",
    {
        "jobId": str,
        "clientToken": str,
    },
)
GitBranchFilterCriteriaTypeDef = TypedDict(
    "GitBranchFilterCriteriaTypeDef",
    {
        "includes": NotRequired[Sequence[str]],
        "excludes": NotRequired[Sequence[str]],
    },
)
GitFilePathFilterCriteriaTypeDef = TypedDict(
    "GitFilePathFilterCriteriaTypeDef",
    {
        "includes": NotRequired[Sequence[str]],
        "excludes": NotRequired[Sequence[str]],
    },
)
GitTagFilterCriteriaTypeDef = TypedDict(
    "GitTagFilterCriteriaTypeDef",
    {
        "includes": NotRequired[Sequence[str]],
        "excludes": NotRequired[Sequence[str]],
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
ListActionTypesInputRequestTypeDef = TypedDict(
    "ListActionTypesInputRequestTypeDef",
    {
        "actionOwnerFilter": NotRequired[ActionOwnerType],
        "nextToken": NotRequired[str],
        "regionFilter": NotRequired[str],
    },
)
ListPipelineExecutionsInputRequestTypeDef = TypedDict(
    "ListPipelineExecutionsInputRequestTypeDef",
    {
        "pipelineName": str,
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListPipelinesInputRequestTypeDef = TypedDict(
    "ListPipelinesInputRequestTypeDef",
    {
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
PipelineSummaryTypeDef = TypedDict(
    "PipelineSummaryTypeDef",
    {
        "name": NotRequired[str],
        "version": NotRequired[int],
        "pipelineType": NotRequired[PipelineTypeType],
        "executionMode": NotRequired[ExecutionModeType],
        "created": NotRequired[datetime],
        "updated": NotRequired[datetime],
    },
)
ListTagsForResourceInputRequestTypeDef = TypedDict(
    "ListTagsForResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "nextToken": NotRequired[str],
        "maxResults": NotRequired[int],
    },
)
ListWebhooksInputRequestTypeDef = TypedDict(
    "ListWebhooksInputRequestTypeDef",
    {
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
StageContextTypeDef = TypedDict(
    "StageContextTypeDef",
    {
        "name": NotRequired[str],
    },
)
PipelineVariableDeclarationTypeDef = TypedDict(
    "PipelineVariableDeclarationTypeDef",
    {
        "name": str,
        "defaultValue": NotRequired[str],
        "description": NotRequired[str],
    },
)
SourceRevisionTypeDef = TypedDict(
    "SourceRevisionTypeDef",
    {
        "actionName": str,
        "revisionId": NotRequired[str],
        "revisionSummary": NotRequired[str],
        "revisionUrl": NotRequired[str],
    },
)
StopExecutionTriggerTypeDef = TypedDict(
    "StopExecutionTriggerTypeDef",
    {
        "reason": NotRequired[str],
    },
)
ResolvedPipelineVariableTypeDef = TypedDict(
    "ResolvedPipelineVariableTypeDef",
    {
        "name": NotRequired[str],
        "resolvedValue": NotRequired[str],
    },
)
PipelineVariableTypeDef = TypedDict(
    "PipelineVariableTypeDef",
    {
        "name": str,
        "value": str,
    },
)
ThirdPartyJobTypeDef = TypedDict(
    "ThirdPartyJobTypeDef",
    {
        "clientId": NotRequired[str],
        "jobId": NotRequired[str],
    },
)
RegisterWebhookWithThirdPartyInputRequestTypeDef = TypedDict(
    "RegisterWebhookWithThirdPartyInputRequestTypeDef",
    {
        "webhookName": NotRequired[str],
    },
)
RetryStageExecutionInputRequestTypeDef = TypedDict(
    "RetryStageExecutionInputRequestTypeDef",
    {
        "pipelineName": str,
        "stageName": str,
        "pipelineExecutionId": str,
        "retryMode": StageRetryModeType,
    },
)
SourceRevisionOverrideTypeDef = TypedDict(
    "SourceRevisionOverrideTypeDef",
    {
        "actionName": str,
        "revisionType": SourceRevisionTypeType,
        "revisionValue": str,
    },
)
StageExecutionTypeDef = TypedDict(
    "StageExecutionTypeDef",
    {
        "pipelineExecutionId": str,
        "status": StageExecutionStatusType,
    },
)
TransitionStateTypeDef = TypedDict(
    "TransitionStateTypeDef",
    {
        "enabled": NotRequired[bool],
        "lastChangedBy": NotRequired[str],
        "lastChangedAt": NotRequired[datetime],
        "disabledReason": NotRequired[str],
    },
)
StopPipelineExecutionInputRequestTypeDef = TypedDict(
    "StopPipelineExecutionInputRequestTypeDef",
    {
        "pipelineName": str,
        "pipelineExecutionId": str,
        "abandon": NotRequired[bool],
        "reason": NotRequired[str],
    },
)
UntagResourceInputRequestTypeDef = TypedDict(
    "UntagResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "tagKeys": Sequence[str],
    },
)
WebhookAuthConfigurationTypeDef = TypedDict(
    "WebhookAuthConfigurationTypeDef",
    {
        "AllowedIPRange": NotRequired[str],
        "SecretToken": NotRequired[str],
    },
)
WebhookFilterRuleTypeDef = TypedDict(
    "WebhookFilterRuleTypeDef",
    {
        "jsonPath": str,
        "matchEquals": NotRequired[str],
    },
)
AcknowledgeJobOutputTypeDef = TypedDict(
    "AcknowledgeJobOutputTypeDef",
    {
        "status": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AcknowledgeThirdPartyJobOutputTypeDef = TypedDict(
    "AcknowledgeThirdPartyJobOutputTypeDef",
    {
        "status": JobStatusType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
EmptyResponseMetadataTypeDef = TypedDict(
    "EmptyResponseMetadataTypeDef",
    {
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutActionRevisionOutputTypeDef = TypedDict(
    "PutActionRevisionOutputTypeDef",
    {
        "newRevision": bool,
        "pipelineExecutionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutApprovalResultOutputTypeDef = TypedDict(
    "PutApprovalResultOutputTypeDef",
    {
        "approvedAt": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RetryStageExecutionOutputTypeDef = TypedDict(
    "RetryStageExecutionOutputTypeDef",
    {
        "pipelineExecutionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartPipelineExecutionOutputTypeDef = TypedDict(
    "StartPipelineExecutionOutputTypeDef",
    {
        "pipelineExecutionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StopPipelineExecutionOutputTypeDef = TypedDict(
    "StopPipelineExecutionOutputTypeDef",
    {
        "pipelineExecutionId": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PollForJobsInputRequestTypeDef = TypedDict(
    "PollForJobsInputRequestTypeDef",
    {
        "actionTypeId": ActionTypeIdTypeDef,
        "maxBatchSize": NotRequired[int],
        "queryParam": NotRequired[Mapping[str, str]],
    },
)
PollForThirdPartyJobsInputRequestTypeDef = TypedDict(
    "PollForThirdPartyJobsInputRequestTypeDef",
    {
        "actionTypeId": ActionTypeIdTypeDef,
        "maxBatchSize": NotRequired[int],
    },
)
ActionDeclarationTypeDef = TypedDict(
    "ActionDeclarationTypeDef",
    {
        "name": str,
        "actionTypeId": ActionTypeIdTypeDef,
        "runOrder": NotRequired[int],
        "configuration": NotRequired[Mapping[str, str]],
        "outputArtifacts": NotRequired[Sequence[OutputArtifactTypeDef]],
        "inputArtifacts": NotRequired[Sequence[InputArtifactTypeDef]],
        "roleArn": NotRequired[str],
        "region": NotRequired[str],
        "namespace": NotRequired[str],
    },
)
ActionExecutionFilterTypeDef = TypedDict(
    "ActionExecutionFilterTypeDef",
    {
        "pipelineExecutionId": NotRequired[str],
        "latestInPipelineExecution": NotRequired[LatestInPipelineExecutionFilterTypeDef],
    },
)
ActionExecutionResultTypeDef = TypedDict(
    "ActionExecutionResultTypeDef",
    {
        "externalExecutionId": NotRequired[str],
        "externalExecutionSummary": NotRequired[str],
        "externalExecutionUrl": NotRequired[str],
        "errorDetails": NotRequired[ErrorDetailsTypeDef],
    },
)
ActionExecutionTypeDef = TypedDict(
    "ActionExecutionTypeDef",
    {
        "actionExecutionId": NotRequired[str],
        "status": NotRequired[ActionExecutionStatusType],
        "summary": NotRequired[str],
        "lastStatusChange": NotRequired[datetime],
        "token": NotRequired[str],
        "lastUpdatedBy": NotRequired[str],
        "externalExecutionId": NotRequired[str],
        "externalExecutionUrl": NotRequired[str],
        "percentComplete": NotRequired[int],
        "errorDetails": NotRequired[ErrorDetailsTypeDef],
    },
)
PutActionRevisionInputRequestTypeDef = TypedDict(
    "PutActionRevisionInputRequestTypeDef",
    {
        "pipelineName": str,
        "stageName": str,
        "actionName": str,
        "actionRevision": ActionRevisionTypeDef,
    },
)
ActionTypeTypeDef = TypedDict(
    "ActionTypeTypeDef",
    {
        "id": ActionTypeIdTypeDef,
        "inputArtifactDetails": ArtifactDetailsTypeDef,
        "outputArtifactDetails": ArtifactDetailsTypeDef,
        "settings": NotRequired[ActionTypeSettingsTypeDef],
        "actionConfigurationProperties": NotRequired[List[ActionConfigurationPropertyTypeDef]],
    },
)
PutApprovalResultInputRequestTypeDef = TypedDict(
    "PutApprovalResultInputRequestTypeDef",
    {
        "pipelineName": str,
        "stageName": str,
        "actionName": str,
        "result": ApprovalResultTypeDef,
        "token": str,
    },
)
ArtifactDetailTypeDef = TypedDict(
    "ArtifactDetailTypeDef",
    {
        "name": NotRequired[str],
        "s3location": NotRequired[S3LocationTypeDef],
    },
)
ArtifactLocationTypeDef = TypedDict(
    "ArtifactLocationTypeDef",
    {
        "type": NotRequired[Literal["S3"]],
        "s3Location": NotRequired[S3ArtifactLocationTypeDef],
    },
)
ArtifactStoreTypeDef = TypedDict(
    "ArtifactStoreTypeDef",
    {
        "type": Literal["S3"],
        "location": str,
        "encryptionKey": NotRequired[EncryptionKeyTypeDef],
    },
)
CreateCustomActionTypeInputRequestTypeDef = TypedDict(
    "CreateCustomActionTypeInputRequestTypeDef",
    {
        "category": ActionCategoryType,
        "provider": str,
        "version": str,
        "inputArtifactDetails": ArtifactDetailsTypeDef,
        "outputArtifactDetails": ArtifactDetailsTypeDef,
        "settings": NotRequired[ActionTypeSettingsTypeDef],
        "configurationProperties": NotRequired[Sequence[ActionConfigurationPropertyTypeDef]],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
ListTagsForResourceOutputTypeDef = TypedDict(
    "ListTagsForResourceOutputTypeDef",
    {
        "tags": List[TagTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
TagResourceInputRequestTypeDef = TypedDict(
    "TagResourceInputRequestTypeDef",
    {
        "resourceArn": str,
        "tags": Sequence[TagTypeDef],
    },
)
CurrentRevisionTypeDef = TypedDict(
    "CurrentRevisionTypeDef",
    {
        "revision": str,
        "changeIdentifier": str,
        "created": NotRequired[TimestampTypeDef],
        "revisionSummary": NotRequired[str],
    },
)
ExecutorConfigurationTypeDef = TypedDict(
    "ExecutorConfigurationTypeDef",
    {
        "lambdaExecutorConfiguration": NotRequired[LambdaExecutorConfigurationTypeDef],
        "jobWorkerExecutorConfiguration": NotRequired[JobWorkerExecutorConfigurationTypeDef],
    },
)
PutJobFailureResultInputRequestTypeDef = TypedDict(
    "PutJobFailureResultInputRequestTypeDef",
    {
        "jobId": str,
        "failureDetails": FailureDetailsTypeDef,
    },
)
PutThirdPartyJobFailureResultInputRequestTypeDef = TypedDict(
    "PutThirdPartyJobFailureResultInputRequestTypeDef",
    {
        "jobId": str,
        "clientToken": str,
        "failureDetails": FailureDetailsTypeDef,
    },
)
GitPullRequestFilterTypeDef = TypedDict(
    "GitPullRequestFilterTypeDef",
    {
        "events": NotRequired[Sequence[GitPullRequestEventTypeType]],
        "branches": NotRequired[GitBranchFilterCriteriaTypeDef],
        "filePaths": NotRequired[GitFilePathFilterCriteriaTypeDef],
    },
)
GitPushFilterTypeDef = TypedDict(
    "GitPushFilterTypeDef",
    {
        "tags": NotRequired[GitTagFilterCriteriaTypeDef],
        "branches": NotRequired[GitBranchFilterCriteriaTypeDef],
        "filePaths": NotRequired[GitFilePathFilterCriteriaTypeDef],
    },
)
ListActionTypesInputListActionTypesPaginateTypeDef = TypedDict(
    "ListActionTypesInputListActionTypesPaginateTypeDef",
    {
        "actionOwnerFilter": NotRequired[ActionOwnerType],
        "regionFilter": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelineExecutionsInputListPipelineExecutionsPaginateTypeDef = TypedDict(
    "ListPipelineExecutionsInputListPipelineExecutionsPaginateTypeDef",
    {
        "pipelineName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelinesInputListPipelinesPaginateTypeDef = TypedDict(
    "ListPipelinesInputListPipelinesPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListTagsForResourceInputListTagsForResourcePaginateTypeDef = TypedDict(
    "ListTagsForResourceInputListTagsForResourcePaginateTypeDef",
    {
        "resourceArn": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListWebhooksInputListWebhooksPaginateTypeDef = TypedDict(
    "ListWebhooksInputListWebhooksPaginateTypeDef",
    {
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPipelinesOutputTypeDef = TypedDict(
    "ListPipelinesOutputTypeDef",
    {
        "pipelines": List[PipelineSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PipelineContextTypeDef = TypedDict(
    "PipelineContextTypeDef",
    {
        "pipelineName": NotRequired[str],
        "stage": NotRequired[StageContextTypeDef],
        "action": NotRequired[ActionContextTypeDef],
        "pipelineArn": NotRequired[str],
        "pipelineExecutionId": NotRequired[str],
    },
)
PipelineExecutionSummaryTypeDef = TypedDict(
    "PipelineExecutionSummaryTypeDef",
    {
        "pipelineExecutionId": NotRequired[str],
        "status": NotRequired[PipelineExecutionStatusType],
        "startTime": NotRequired[datetime],
        "lastUpdateTime": NotRequired[datetime],
        "sourceRevisions": NotRequired[List[SourceRevisionTypeDef]],
        "trigger": NotRequired[ExecutionTriggerTypeDef],
        "stopTrigger": NotRequired[StopExecutionTriggerTypeDef],
        "executionMode": NotRequired[ExecutionModeType],
    },
)
PipelineExecutionTypeDef = TypedDict(
    "PipelineExecutionTypeDef",
    {
        "pipelineName": NotRequired[str],
        "pipelineVersion": NotRequired[int],
        "pipelineExecutionId": NotRequired[str],
        "status": NotRequired[PipelineExecutionStatusType],
        "statusSummary": NotRequired[str],
        "artifactRevisions": NotRequired[List[ArtifactRevisionTypeDef]],
        "variables": NotRequired[List[ResolvedPipelineVariableTypeDef]],
        "trigger": NotRequired[ExecutionTriggerTypeDef],
        "executionMode": NotRequired[ExecutionModeType],
    },
)
PollForThirdPartyJobsOutputTypeDef = TypedDict(
    "PollForThirdPartyJobsOutputTypeDef",
    {
        "jobs": List[ThirdPartyJobTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
StartPipelineExecutionInputRequestTypeDef = TypedDict(
    "StartPipelineExecutionInputRequestTypeDef",
    {
        "name": str,
        "variables": NotRequired[Sequence[PipelineVariableTypeDef]],
        "clientRequestToken": NotRequired[str],
        "sourceRevisions": NotRequired[Sequence[SourceRevisionOverrideTypeDef]],
    },
)
WebhookDefinitionTypeDef = TypedDict(
    "WebhookDefinitionTypeDef",
    {
        "name": str,
        "targetPipeline": str,
        "targetAction": str,
        "filters": List[WebhookFilterRuleTypeDef],
        "authentication": WebhookAuthenticationTypeType,
        "authenticationConfiguration": WebhookAuthConfigurationTypeDef,
    },
)
StageDeclarationTypeDef = TypedDict(
    "StageDeclarationTypeDef",
    {
        "name": str,
        "actions": Sequence[ActionDeclarationTypeDef],
        "blockers": NotRequired[Sequence[BlockerDeclarationTypeDef]],
    },
)
ListActionExecutionsInputListActionExecutionsPaginateTypeDef = TypedDict(
    "ListActionExecutionsInputListActionExecutionsPaginateTypeDef",
    {
        "pipelineName": str,
        "filter": NotRequired[ActionExecutionFilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListActionExecutionsInputRequestTypeDef = TypedDict(
    "ListActionExecutionsInputRequestTypeDef",
    {
        "pipelineName": str,
        "filter": NotRequired[ActionExecutionFilterTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ActionStateTypeDef = TypedDict(
    "ActionStateTypeDef",
    {
        "actionName": NotRequired[str],
        "currentRevision": NotRequired[ActionRevisionTypeDef],
        "latestExecution": NotRequired[ActionExecutionTypeDef],
        "entityUrl": NotRequired[str],
        "revisionUrl": NotRequired[str],
    },
)
CreateCustomActionTypeOutputTypeDef = TypedDict(
    "CreateCustomActionTypeOutputTypeDef",
    {
        "actionType": ActionTypeTypeDef,
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListActionTypesOutputTypeDef = TypedDict(
    "ListActionTypesOutputTypeDef",
    {
        "actionTypes": List[ActionTypeTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ActionExecutionInputTypeDef = TypedDict(
    "ActionExecutionInputTypeDef",
    {
        "actionTypeId": NotRequired[ActionTypeIdTypeDef],
        "configuration": NotRequired[Dict[str, str]],
        "resolvedConfiguration": NotRequired[Dict[str, str]],
        "roleArn": NotRequired[str],
        "region": NotRequired[str],
        "inputArtifacts": NotRequired[List[ArtifactDetailTypeDef]],
        "namespace": NotRequired[str],
    },
)
ActionExecutionOutputTypeDef = TypedDict(
    "ActionExecutionOutputTypeDef",
    {
        "outputArtifacts": NotRequired[List[ArtifactDetailTypeDef]],
        "executionResult": NotRequired[ActionExecutionResultTypeDef],
        "outputVariables": NotRequired[Dict[str, str]],
    },
)
ArtifactTypeDef = TypedDict(
    "ArtifactTypeDef",
    {
        "name": NotRequired[str],
        "revision": NotRequired[str],
        "location": NotRequired[ArtifactLocationTypeDef],
    },
)
PutJobSuccessResultInputRequestTypeDef = TypedDict(
    "PutJobSuccessResultInputRequestTypeDef",
    {
        "jobId": str,
        "currentRevision": NotRequired[CurrentRevisionTypeDef],
        "continuationToken": NotRequired[str],
        "executionDetails": NotRequired[ExecutionDetailsTypeDef],
        "outputVariables": NotRequired[Mapping[str, str]],
    },
)
PutThirdPartyJobSuccessResultInputRequestTypeDef = TypedDict(
    "PutThirdPartyJobSuccessResultInputRequestTypeDef",
    {
        "jobId": str,
        "clientToken": str,
        "currentRevision": NotRequired[CurrentRevisionTypeDef],
        "continuationToken": NotRequired[str],
        "executionDetails": NotRequired[ExecutionDetailsTypeDef],
    },
)
ActionTypeExecutorTypeDef = TypedDict(
    "ActionTypeExecutorTypeDef",
    {
        "configuration": ExecutorConfigurationTypeDef,
        "type": ExecutorTypeType,
        "policyStatementsTemplate": NotRequired[str],
        "jobTimeout": NotRequired[int],
    },
)
GitConfigurationTypeDef = TypedDict(
    "GitConfigurationTypeDef",
    {
        "sourceActionName": str,
        "push": NotRequired[Sequence[GitPushFilterTypeDef]],
        "pullRequest": NotRequired[Sequence[GitPullRequestFilterTypeDef]],
    },
)
ListPipelineExecutionsOutputTypeDef = TypedDict(
    "ListPipelineExecutionsOutputTypeDef",
    {
        "pipelineExecutionSummaries": List[PipelineExecutionSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPipelineExecutionOutputTypeDef = TypedDict(
    "GetPipelineExecutionOutputTypeDef",
    {
        "pipelineExecution": PipelineExecutionTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListWebhookItemTypeDef = TypedDict(
    "ListWebhookItemTypeDef",
    {
        "definition": WebhookDefinitionTypeDef,
        "url": str,
        "errorMessage": NotRequired[str],
        "errorCode": NotRequired[str],
        "lastTriggered": NotRequired[datetime],
        "arn": NotRequired[str],
        "tags": NotRequired[List[TagTypeDef]],
    },
)
PutWebhookInputRequestTypeDef = TypedDict(
    "PutWebhookInputRequestTypeDef",
    {
        "webhook": WebhookDefinitionTypeDef,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
StageStateTypeDef = TypedDict(
    "StageStateTypeDef",
    {
        "stageName": NotRequired[str],
        "inboundExecution": NotRequired[StageExecutionTypeDef],
        "inboundExecutions": NotRequired[List[StageExecutionTypeDef]],
        "inboundTransitionState": NotRequired[TransitionStateTypeDef],
        "actionStates": NotRequired[List[ActionStateTypeDef]],
        "latestExecution": NotRequired[StageExecutionTypeDef],
    },
)
ActionExecutionDetailTypeDef = TypedDict(
    "ActionExecutionDetailTypeDef",
    {
        "pipelineExecutionId": NotRequired[str],
        "actionExecutionId": NotRequired[str],
        "pipelineVersion": NotRequired[int],
        "stageName": NotRequired[str],
        "actionName": NotRequired[str],
        "startTime": NotRequired[datetime],
        "lastUpdateTime": NotRequired[datetime],
        "updatedBy": NotRequired[str],
        "status": NotRequired[ActionExecutionStatusType],
        "input": NotRequired[ActionExecutionInputTypeDef],
        "output": NotRequired[ActionExecutionOutputTypeDef],
    },
)
JobDataTypeDef = TypedDict(
    "JobDataTypeDef",
    {
        "actionTypeId": NotRequired[ActionTypeIdTypeDef],
        "actionConfiguration": NotRequired[ActionConfigurationTypeDef],
        "pipelineContext": NotRequired[PipelineContextTypeDef],
        "inputArtifacts": NotRequired[List[ArtifactTypeDef]],
        "outputArtifacts": NotRequired[List[ArtifactTypeDef]],
        "artifactCredentials": NotRequired[AWSSessionCredentialsTypeDef],
        "continuationToken": NotRequired[str],
        "encryptionKey": NotRequired[EncryptionKeyTypeDef],
    },
)
ThirdPartyJobDataTypeDef = TypedDict(
    "ThirdPartyJobDataTypeDef",
    {
        "actionTypeId": NotRequired[ActionTypeIdTypeDef],
        "actionConfiguration": NotRequired[ActionConfigurationTypeDef],
        "pipelineContext": NotRequired[PipelineContextTypeDef],
        "inputArtifacts": NotRequired[List[ArtifactTypeDef]],
        "outputArtifacts": NotRequired[List[ArtifactTypeDef]],
        "artifactCredentials": NotRequired[AWSSessionCredentialsTypeDef],
        "continuationToken": NotRequired[str],
        "encryptionKey": NotRequired[EncryptionKeyTypeDef],
    },
)
ActionTypeDeclarationTypeDef = TypedDict(
    "ActionTypeDeclarationTypeDef",
    {
        "executor": ActionTypeExecutorTypeDef,
        "id": ActionTypeIdentifierTypeDef,
        "inputArtifactDetails": ActionTypeArtifactDetailsTypeDef,
        "outputArtifactDetails": ActionTypeArtifactDetailsTypeDef,
        "description": NotRequired[str],
        "permissions": NotRequired[ActionTypePermissionsTypeDef],
        "properties": NotRequired[List[ActionTypePropertyTypeDef]],
        "urls": NotRequired[ActionTypeUrlsTypeDef],
    },
)
PipelineTriggerDeclarationTypeDef = TypedDict(
    "PipelineTriggerDeclarationTypeDef",
    {
        "providerType": Literal["CodeStarSourceConnection"],
        "gitConfiguration": GitConfigurationTypeDef,
    },
)
ListWebhooksOutputTypeDef = TypedDict(
    "ListWebhooksOutputTypeDef",
    {
        "webhooks": List[ListWebhookItemTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutWebhookOutputTypeDef = TypedDict(
    "PutWebhookOutputTypeDef",
    {
        "webhook": ListWebhookItemTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPipelineStateOutputTypeDef = TypedDict(
    "GetPipelineStateOutputTypeDef",
    {
        "pipelineName": str,
        "pipelineVersion": int,
        "stageStates": List[StageStateTypeDef],
        "created": datetime,
        "updated": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListActionExecutionsOutputTypeDef = TypedDict(
    "ListActionExecutionsOutputTypeDef",
    {
        "actionExecutionDetails": List[ActionExecutionDetailTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
JobDetailsTypeDef = TypedDict(
    "JobDetailsTypeDef",
    {
        "id": NotRequired[str],
        "data": NotRequired[JobDataTypeDef],
        "accountId": NotRequired[str],
    },
)
JobTypeDef = TypedDict(
    "JobTypeDef",
    {
        "id": NotRequired[str],
        "data": NotRequired[JobDataTypeDef],
        "nonce": NotRequired[str],
        "accountId": NotRequired[str],
    },
)
ThirdPartyJobDetailsTypeDef = TypedDict(
    "ThirdPartyJobDetailsTypeDef",
    {
        "id": NotRequired[str],
        "data": NotRequired[ThirdPartyJobDataTypeDef],
        "nonce": NotRequired[str],
    },
)
GetActionTypeOutputTypeDef = TypedDict(
    "GetActionTypeOutputTypeDef",
    {
        "actionType": ActionTypeDeclarationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateActionTypeInputRequestTypeDef = TypedDict(
    "UpdateActionTypeInputRequestTypeDef",
    {
        "actionType": ActionTypeDeclarationTypeDef,
    },
)
PipelineDeclarationTypeDef = TypedDict(
    "PipelineDeclarationTypeDef",
    {
        "name": str,
        "roleArn": str,
        "stages": Sequence[StageDeclarationTypeDef],
        "artifactStore": NotRequired[ArtifactStoreTypeDef],
        "artifactStores": NotRequired[Mapping[str, ArtifactStoreTypeDef]],
        "version": NotRequired[int],
        "executionMode": NotRequired[ExecutionModeType],
        "pipelineType": NotRequired[PipelineTypeType],
        "variables": NotRequired[Sequence[PipelineVariableDeclarationTypeDef]],
        "triggers": NotRequired[Sequence[PipelineTriggerDeclarationTypeDef]],
    },
)
GetJobDetailsOutputTypeDef = TypedDict(
    "GetJobDetailsOutputTypeDef",
    {
        "jobDetails": JobDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PollForJobsOutputTypeDef = TypedDict(
    "PollForJobsOutputTypeDef",
    {
        "jobs": List[JobTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetThirdPartyJobDetailsOutputTypeDef = TypedDict(
    "GetThirdPartyJobDetailsOutputTypeDef",
    {
        "jobDetails": ThirdPartyJobDetailsTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreatePipelineInputRequestTypeDef = TypedDict(
    "CreatePipelineInputRequestTypeDef",
    {
        "pipeline": PipelineDeclarationTypeDef,
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
CreatePipelineOutputTypeDef = TypedDict(
    "CreatePipelineOutputTypeDef",
    {
        "pipeline": PipelineDeclarationTypeDef,
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPipelineOutputTypeDef = TypedDict(
    "GetPipelineOutputTypeDef",
    {
        "pipeline": PipelineDeclarationTypeDef,
        "metadata": PipelineMetadataTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePipelineInputRequestTypeDef = TypedDict(
    "UpdatePipelineInputRequestTypeDef",
    {
        "pipeline": PipelineDeclarationTypeDef,
    },
)
UpdatePipelineOutputTypeDef = TypedDict(
    "UpdatePipelineOutputTypeDef",
    {
        "pipeline": PipelineDeclarationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
