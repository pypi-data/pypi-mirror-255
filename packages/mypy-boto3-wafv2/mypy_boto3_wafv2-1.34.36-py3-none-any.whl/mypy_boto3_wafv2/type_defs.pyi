"""
Type annotations for wafv2 service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_wafv2/type_defs/)

Usage::

    ```python
    from mypy_boto3_wafv2.type_defs import APIKeySummaryTypeDef

    data: APIKeySummaryTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import IO, Any, Dict, List, Mapping, Sequence, Union

from botocore.response import StreamingBody

from .literals import (
    ActionValueType,
    BodyParsingFallbackBehaviorType,
    ComparisonOperatorType,
    CountryCodeType,
    FailureReasonType,
    FallbackBehaviorType,
    FilterBehaviorType,
    FilterRequirementType,
    ForwardedIPPositionType,
    InspectionLevelType,
    IPAddressVersionType,
    JsonMatchScopeType,
    LabelMatchScopeType,
    MapMatchScopeType,
    OversizeHandlingType,
    PayloadTypeType,
    PlatformType,
    PositionalConstraintType,
    RateBasedStatementAggregateKeyTypeType,
    ResourceTypeType,
    ResponseContentTypeType,
    ScopeType,
    SensitivityLevelType,
    SizeInspectionLimitType,
    TextTransformationTypeType,
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
    "APIKeySummaryTypeDef",
    "AWSManagedRulesBotControlRuleSetTypeDef",
    "ActionConditionTypeDef",
    "AddressFieldTypeDef",
    "AndStatementTypeDef",
    "AssociateWebACLRequestRequestTypeDef",
    "RequestBodyAssociatedResourceTypeConfigTypeDef",
    "BlobTypeDef",
    "BodyTypeDef",
    "TextTransformationTypeDef",
    "ImmunityTimePropertyTypeDef",
    "CaptchaResponseTypeDef",
    "ChallengeResponseTypeDef",
    "ResponseMetadataTypeDef",
    "LabelNameConditionTypeDef",
    "CookieMatchPatternTypeDef",
    "CreateAPIKeyRequestRequestTypeDef",
    "TagTypeDef",
    "IPSetSummaryTypeDef",
    "RegexTypeDef",
    "RegexPatternSetSummaryTypeDef",
    "CustomResponseBodyTypeDef",
    "VisibilityConfigTypeDef",
    "RuleGroupSummaryTypeDef",
    "WebACLSummaryTypeDef",
    "CustomHTTPHeaderTypeDef",
    "DeleteAPIKeyRequestRequestTypeDef",
    "DeleteFirewallManagerRuleGroupsRequestRequestTypeDef",
    "DeleteIPSetRequestRequestTypeDef",
    "DeleteLoggingConfigurationRequestRequestTypeDef",
    "DeletePermissionPolicyRequestRequestTypeDef",
    "DeleteRegexPatternSetRequestRequestTypeDef",
    "DeleteRuleGroupRequestRequestTypeDef",
    "DeleteWebACLRequestRequestTypeDef",
    "DescribeAllManagedProductsRequestRequestTypeDef",
    "ManagedProductDescriptorTypeDef",
    "DescribeManagedProductsByVendorRequestRequestTypeDef",
    "DescribeManagedRuleGroupRequestRequestTypeDef",
    "LabelSummaryTypeDef",
    "DisassociateWebACLRequestRequestTypeDef",
    "EmailFieldTypeDef",
    "ExcludedRuleTypeDef",
    "HeaderOrderTypeDef",
    "JA3FingerprintTypeDef",
    "SingleHeaderTypeDef",
    "SingleQueryArgumentTypeDef",
    "ForwardedIPConfigTypeDef",
    "GenerateMobileSdkReleaseUrlRequestRequestTypeDef",
    "GetDecryptedAPIKeyRequestRequestTypeDef",
    "GetIPSetRequestRequestTypeDef",
    "IPSetTypeDef",
    "GetLoggingConfigurationRequestRequestTypeDef",
    "GetManagedRuleSetRequestRequestTypeDef",
    "GetMobileSdkReleaseRequestRequestTypeDef",
    "GetPermissionPolicyRequestRequestTypeDef",
    "GetRateBasedStatementManagedKeysRequestRequestTypeDef",
    "RateBasedStatementManagedKeysIPSetTypeDef",
    "GetRegexPatternSetRequestRequestTypeDef",
    "GetRuleGroupRequestRequestTypeDef",
    "GetWebACLForResourceRequestRequestTypeDef",
    "GetWebACLRequestRequestTypeDef",
    "HTTPHeaderTypeDef",
    "HeaderMatchPatternTypeDef",
    "IPSetForwardedIPConfigTypeDef",
    "JsonMatchPatternTypeDef",
    "LabelMatchStatementTypeDef",
    "LabelTypeDef",
    "ListAPIKeysRequestRequestTypeDef",
    "ListAvailableManagedRuleGroupVersionsRequestRequestTypeDef",
    "ManagedRuleGroupVersionTypeDef",
    "ListAvailableManagedRuleGroupsRequestRequestTypeDef",
    "ManagedRuleGroupSummaryTypeDef",
    "ListIPSetsRequestRequestTypeDef",
    "ListLoggingConfigurationsRequestRequestTypeDef",
    "ListManagedRuleSetsRequestRequestTypeDef",
    "ManagedRuleSetSummaryTypeDef",
    "ListMobileSdkReleasesRequestRequestTypeDef",
    "ReleaseSummaryTypeDef",
    "ListRegexPatternSetsRequestRequestTypeDef",
    "ListResourcesForWebACLRequestRequestTypeDef",
    "ListRuleGroupsRequestRequestTypeDef",
    "ListTagsForResourceRequestRequestTypeDef",
    "ListWebACLsRequestRequestTypeDef",
    "PasswordFieldTypeDef",
    "UsernameFieldTypeDef",
    "ManagedRuleSetVersionTypeDef",
    "NotStatementTypeDef",
    "OrStatementTypeDef",
    "PhoneNumberFieldTypeDef",
    "VersionToPublishTypeDef",
    "PutPermissionPolicyRequestRequestTypeDef",
    "RateLimitLabelNamespaceTypeDef",
    "ResponseInspectionBodyContainsTypeDef",
    "ResponseInspectionHeaderTypeDef",
    "ResponseInspectionJsonTypeDef",
    "ResponseInspectionStatusCodeTypeDef",
    "TimestampTypeDef",
    "UntagResourceRequestRequestTypeDef",
    "UpdateIPSetRequestRequestTypeDef",
    "AssociationConfigTypeDef",
    "RateLimitCookieTypeDef",
    "RateLimitHeaderTypeDef",
    "RateLimitQueryArgumentTypeDef",
    "RateLimitQueryStringTypeDef",
    "RateLimitUriPathTypeDef",
    "CaptchaConfigTypeDef",
    "ChallengeConfigTypeDef",
    "CheckCapacityResponseTypeDef",
    "CreateAPIKeyResponseTypeDef",
    "DeleteFirewallManagerRuleGroupsResponseTypeDef",
    "GenerateMobileSdkReleaseUrlResponseTypeDef",
    "GetDecryptedAPIKeyResponseTypeDef",
    "GetPermissionPolicyResponseTypeDef",
    "ListAPIKeysResponseTypeDef",
    "ListResourcesForWebACLResponseTypeDef",
    "PutManagedRuleSetVersionsResponseTypeDef",
    "UpdateIPSetResponseTypeDef",
    "UpdateManagedRuleSetVersionExpiryDateResponseTypeDef",
    "UpdateRegexPatternSetResponseTypeDef",
    "UpdateRuleGroupResponseTypeDef",
    "UpdateWebACLResponseTypeDef",
    "ConditionTypeDef",
    "CookiesTypeDef",
    "CreateIPSetRequestRequestTypeDef",
    "MobileSdkReleaseTypeDef",
    "TagInfoForResourceTypeDef",
    "TagResourceRequestRequestTypeDef",
    "CreateIPSetResponseTypeDef",
    "ListIPSetsResponseTypeDef",
    "CreateRegexPatternSetRequestRequestTypeDef",
    "RegexPatternSetTypeDef",
    "UpdateRegexPatternSetRequestRequestTypeDef",
    "CreateRegexPatternSetResponseTypeDef",
    "ListRegexPatternSetsResponseTypeDef",
    "CreateRuleGroupResponseTypeDef",
    "ListRuleGroupsResponseTypeDef",
    "CreateWebACLResponseTypeDef",
    "ListWebACLsResponseTypeDef",
    "CustomRequestHandlingTypeDef",
    "CustomResponseTypeDef",
    "DescribeAllManagedProductsResponseTypeDef",
    "DescribeManagedProductsByVendorResponseTypeDef",
    "GeoMatchStatementTypeDef",
    "GetIPSetResponseTypeDef",
    "GetRateBasedStatementManagedKeysResponseTypeDef",
    "HTTPRequestTypeDef",
    "HeadersTypeDef",
    "IPSetReferenceStatementTypeDef",
    "JsonBodyTypeDef",
    "ListAvailableManagedRuleGroupVersionsResponseTypeDef",
    "ListAvailableManagedRuleGroupsResponseTypeDef",
    "ListManagedRuleSetsResponseTypeDef",
    "ListMobileSdkReleasesResponseTypeDef",
    "RequestInspectionTypeDef",
    "ManagedRuleSetTypeDef",
    "RequestInspectionACFPTypeDef",
    "PutManagedRuleSetVersionsRequestRequestTypeDef",
    "ResponseInspectionTypeDef",
    "TimeWindowTypeDef",
    "UpdateManagedRuleSetVersionExpiryDateRequestRequestTypeDef",
    "RateBasedStatementCustomKeyTypeDef",
    "FilterTypeDef",
    "GetMobileSdkReleaseResponseTypeDef",
    "ListTagsForResourceResponseTypeDef",
    "GetRegexPatternSetResponseTypeDef",
    "AllowActionTypeDef",
    "CaptchaActionTypeDef",
    "ChallengeActionTypeDef",
    "CountActionTypeDef",
    "BlockActionTypeDef",
    "SampledHTTPRequestTypeDef",
    "FieldToMatchTypeDef",
    "GetManagedRuleSetResponseTypeDef",
    "AWSManagedRulesACFPRuleSetTypeDef",
    "AWSManagedRulesATPRuleSetTypeDef",
    "GetSampledRequestsRequestRequestTypeDef",
    "RateBasedStatementTypeDef",
    "LoggingFilterTypeDef",
    "OverrideActionTypeDef",
    "DefaultActionTypeDef",
    "RuleActionTypeDef",
    "GetSampledRequestsResponseTypeDef",
    "ByteMatchStatementTypeDef",
    "RegexMatchStatementTypeDef",
    "RegexPatternSetReferenceStatementTypeDef",
    "SizeConstraintStatementTypeDef",
    "SqliMatchStatementTypeDef",
    "XssMatchStatementTypeDef",
    "ManagedRuleGroupConfigTypeDef",
    "LoggingConfigurationTypeDef",
    "RuleActionOverrideTypeDef",
    "RuleSummaryTypeDef",
    "RuleTypeDef",
    "GetLoggingConfigurationResponseTypeDef",
    "ListLoggingConfigurationsResponseTypeDef",
    "PutLoggingConfigurationRequestRequestTypeDef",
    "PutLoggingConfigurationResponseTypeDef",
    "ManagedRuleGroupStatementTypeDef",
    "RuleGroupReferenceStatementTypeDef",
    "DescribeManagedRuleGroupResponseTypeDef",
    "CheckCapacityRequestRequestTypeDef",
    "CreateRuleGroupRequestRequestTypeDef",
    "CreateWebACLRequestRequestTypeDef",
    "RuleGroupTypeDef",
    "UpdateRuleGroupRequestRequestTypeDef",
    "UpdateWebACLRequestRequestTypeDef",
    "FirewallManagerStatementTypeDef",
    "StatementTypeDef",
    "GetRuleGroupResponseTypeDef",
    "FirewallManagerRuleGroupTypeDef",
    "WebACLTypeDef",
    "GetWebACLForResourceResponseTypeDef",
    "GetWebACLResponseTypeDef",
)

APIKeySummaryTypeDef = TypedDict(
    "APIKeySummaryTypeDef",
    {
        "TokenDomains": NotRequired[List[str]],
        "APIKey": NotRequired[str],
        "CreationTimestamp": NotRequired[datetime],
        "Version": NotRequired[int],
    },
)
AWSManagedRulesBotControlRuleSetTypeDef = TypedDict(
    "AWSManagedRulesBotControlRuleSetTypeDef",
    {
        "InspectionLevel": InspectionLevelType,
        "EnableMachineLearning": NotRequired[bool],
    },
)
ActionConditionTypeDef = TypedDict(
    "ActionConditionTypeDef",
    {
        "Action": ActionValueType,
    },
)
AddressFieldTypeDef = TypedDict(
    "AddressFieldTypeDef",
    {
        "Identifier": str,
    },
)
AndStatementTypeDef = TypedDict(
    "AndStatementTypeDef",
    {
        "Statements": Sequence["StatementTypeDef"],
    },
)
AssociateWebACLRequestRequestTypeDef = TypedDict(
    "AssociateWebACLRequestRequestTypeDef",
    {
        "WebACLArn": str,
        "ResourceArn": str,
    },
)
RequestBodyAssociatedResourceTypeConfigTypeDef = TypedDict(
    "RequestBodyAssociatedResourceTypeConfigTypeDef",
    {
        "DefaultSizeInspectionLimit": SizeInspectionLimitType,
    },
)
BlobTypeDef = Union[str, bytes, IO[Any], StreamingBody]
BodyTypeDef = TypedDict(
    "BodyTypeDef",
    {
        "OversizeHandling": NotRequired[OversizeHandlingType],
    },
)
TextTransformationTypeDef = TypedDict(
    "TextTransformationTypeDef",
    {
        "Priority": int,
        "Type": TextTransformationTypeType,
    },
)
ImmunityTimePropertyTypeDef = TypedDict(
    "ImmunityTimePropertyTypeDef",
    {
        "ImmunityTime": int,
    },
)
CaptchaResponseTypeDef = TypedDict(
    "CaptchaResponseTypeDef",
    {
        "ResponseCode": NotRequired[int],
        "SolveTimestamp": NotRequired[int],
        "FailureReason": NotRequired[FailureReasonType],
    },
)
ChallengeResponseTypeDef = TypedDict(
    "ChallengeResponseTypeDef",
    {
        "ResponseCode": NotRequired[int],
        "SolveTimestamp": NotRequired[int],
        "FailureReason": NotRequired[FailureReasonType],
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
LabelNameConditionTypeDef = TypedDict(
    "LabelNameConditionTypeDef",
    {
        "LabelName": str,
    },
)
CookieMatchPatternTypeDef = TypedDict(
    "CookieMatchPatternTypeDef",
    {
        "All": NotRequired[Mapping[str, Any]],
        "IncludedCookies": NotRequired[Sequence[str]],
        "ExcludedCookies": NotRequired[Sequence[str]],
    },
)
CreateAPIKeyRequestRequestTypeDef = TypedDict(
    "CreateAPIKeyRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "TokenDomains": Sequence[str],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "Key": str,
        "Value": str,
    },
)
IPSetSummaryTypeDef = TypedDict(
    "IPSetSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Description": NotRequired[str],
        "LockToken": NotRequired[str],
        "ARN": NotRequired[str],
    },
)
RegexTypeDef = TypedDict(
    "RegexTypeDef",
    {
        "RegexString": NotRequired[str],
    },
)
RegexPatternSetSummaryTypeDef = TypedDict(
    "RegexPatternSetSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Description": NotRequired[str],
        "LockToken": NotRequired[str],
        "ARN": NotRequired[str],
    },
)
CustomResponseBodyTypeDef = TypedDict(
    "CustomResponseBodyTypeDef",
    {
        "ContentType": ResponseContentTypeType,
        "Content": str,
    },
)
VisibilityConfigTypeDef = TypedDict(
    "VisibilityConfigTypeDef",
    {
        "SampledRequestsEnabled": bool,
        "CloudWatchMetricsEnabled": bool,
        "MetricName": str,
    },
)
RuleGroupSummaryTypeDef = TypedDict(
    "RuleGroupSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Description": NotRequired[str],
        "LockToken": NotRequired[str],
        "ARN": NotRequired[str],
    },
)
WebACLSummaryTypeDef = TypedDict(
    "WebACLSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Description": NotRequired[str],
        "LockToken": NotRequired[str],
        "ARN": NotRequired[str],
    },
)
CustomHTTPHeaderTypeDef = TypedDict(
    "CustomHTTPHeaderTypeDef",
    {
        "Name": str,
        "Value": str,
    },
)
DeleteAPIKeyRequestRequestTypeDef = TypedDict(
    "DeleteAPIKeyRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "APIKey": str,
    },
)
DeleteFirewallManagerRuleGroupsRequestRequestTypeDef = TypedDict(
    "DeleteFirewallManagerRuleGroupsRequestRequestTypeDef",
    {
        "WebACLArn": str,
        "WebACLLockToken": str,
    },
)
DeleteIPSetRequestRequestTypeDef = TypedDict(
    "DeleteIPSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "LockToken": str,
    },
)
DeleteLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "DeleteLoggingConfigurationRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
DeletePermissionPolicyRequestRequestTypeDef = TypedDict(
    "DeletePermissionPolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
DeleteRegexPatternSetRequestRequestTypeDef = TypedDict(
    "DeleteRegexPatternSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "LockToken": str,
    },
)
DeleteRuleGroupRequestRequestTypeDef = TypedDict(
    "DeleteRuleGroupRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "LockToken": str,
    },
)
DeleteWebACLRequestRequestTypeDef = TypedDict(
    "DeleteWebACLRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "LockToken": str,
    },
)
DescribeAllManagedProductsRequestRequestTypeDef = TypedDict(
    "DescribeAllManagedProductsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
    },
)
ManagedProductDescriptorTypeDef = TypedDict(
    "ManagedProductDescriptorTypeDef",
    {
        "VendorName": NotRequired[str],
        "ManagedRuleSetName": NotRequired[str],
        "ProductId": NotRequired[str],
        "ProductLink": NotRequired[str],
        "ProductTitle": NotRequired[str],
        "ProductDescription": NotRequired[str],
        "SnsTopicArn": NotRequired[str],
        "IsVersioningSupported": NotRequired[bool],
        "IsAdvancedManagedRuleSet": NotRequired[bool],
    },
)
DescribeManagedProductsByVendorRequestRequestTypeDef = TypedDict(
    "DescribeManagedProductsByVendorRequestRequestTypeDef",
    {
        "VendorName": str,
        "Scope": ScopeType,
    },
)
DescribeManagedRuleGroupRequestRequestTypeDef = TypedDict(
    "DescribeManagedRuleGroupRequestRequestTypeDef",
    {
        "VendorName": str,
        "Name": str,
        "Scope": ScopeType,
        "VersionName": NotRequired[str],
    },
)
LabelSummaryTypeDef = TypedDict(
    "LabelSummaryTypeDef",
    {
        "Name": NotRequired[str],
    },
)
DisassociateWebACLRequestRequestTypeDef = TypedDict(
    "DisassociateWebACLRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
EmailFieldTypeDef = TypedDict(
    "EmailFieldTypeDef",
    {
        "Identifier": str,
    },
)
ExcludedRuleTypeDef = TypedDict(
    "ExcludedRuleTypeDef",
    {
        "Name": str,
    },
)
HeaderOrderTypeDef = TypedDict(
    "HeaderOrderTypeDef",
    {
        "OversizeHandling": OversizeHandlingType,
    },
)
JA3FingerprintTypeDef = TypedDict(
    "JA3FingerprintTypeDef",
    {
        "FallbackBehavior": FallbackBehaviorType,
    },
)
SingleHeaderTypeDef = TypedDict(
    "SingleHeaderTypeDef",
    {
        "Name": str,
    },
)
SingleQueryArgumentTypeDef = TypedDict(
    "SingleQueryArgumentTypeDef",
    {
        "Name": str,
    },
)
ForwardedIPConfigTypeDef = TypedDict(
    "ForwardedIPConfigTypeDef",
    {
        "HeaderName": str,
        "FallbackBehavior": FallbackBehaviorType,
    },
)
GenerateMobileSdkReleaseUrlRequestRequestTypeDef = TypedDict(
    "GenerateMobileSdkReleaseUrlRequestRequestTypeDef",
    {
        "Platform": PlatformType,
        "ReleaseVersion": str,
    },
)
GetDecryptedAPIKeyRequestRequestTypeDef = TypedDict(
    "GetDecryptedAPIKeyRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "APIKey": str,
    },
)
GetIPSetRequestRequestTypeDef = TypedDict(
    "GetIPSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
    },
)
IPSetTypeDef = TypedDict(
    "IPSetTypeDef",
    {
        "Name": str,
        "Id": str,
        "ARN": str,
        "IPAddressVersion": IPAddressVersionType,
        "Addresses": List[str],
        "Description": NotRequired[str],
    },
)
GetLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "GetLoggingConfigurationRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
GetManagedRuleSetRequestRequestTypeDef = TypedDict(
    "GetManagedRuleSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
    },
)
GetMobileSdkReleaseRequestRequestTypeDef = TypedDict(
    "GetMobileSdkReleaseRequestRequestTypeDef",
    {
        "Platform": PlatformType,
        "ReleaseVersion": str,
    },
)
GetPermissionPolicyRequestRequestTypeDef = TypedDict(
    "GetPermissionPolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
GetRateBasedStatementManagedKeysRequestRequestTypeDef = TypedDict(
    "GetRateBasedStatementManagedKeysRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "WebACLName": str,
        "WebACLId": str,
        "RuleName": str,
        "RuleGroupRuleName": NotRequired[str],
    },
)
RateBasedStatementManagedKeysIPSetTypeDef = TypedDict(
    "RateBasedStatementManagedKeysIPSetTypeDef",
    {
        "IPAddressVersion": NotRequired[IPAddressVersionType],
        "Addresses": NotRequired[List[str]],
    },
)
GetRegexPatternSetRequestRequestTypeDef = TypedDict(
    "GetRegexPatternSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
    },
)
GetRuleGroupRequestRequestTypeDef = TypedDict(
    "GetRuleGroupRequestRequestTypeDef",
    {
        "Name": NotRequired[str],
        "Scope": NotRequired[ScopeType],
        "Id": NotRequired[str],
        "ARN": NotRequired[str],
    },
)
GetWebACLForResourceRequestRequestTypeDef = TypedDict(
    "GetWebACLForResourceRequestRequestTypeDef",
    {
        "ResourceArn": str,
    },
)
GetWebACLRequestRequestTypeDef = TypedDict(
    "GetWebACLRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
    },
)
HTTPHeaderTypeDef = TypedDict(
    "HTTPHeaderTypeDef",
    {
        "Name": NotRequired[str],
        "Value": NotRequired[str],
    },
)
HeaderMatchPatternTypeDef = TypedDict(
    "HeaderMatchPatternTypeDef",
    {
        "All": NotRequired[Mapping[str, Any]],
        "IncludedHeaders": NotRequired[Sequence[str]],
        "ExcludedHeaders": NotRequired[Sequence[str]],
    },
)
IPSetForwardedIPConfigTypeDef = TypedDict(
    "IPSetForwardedIPConfigTypeDef",
    {
        "HeaderName": str,
        "FallbackBehavior": FallbackBehaviorType,
        "Position": ForwardedIPPositionType,
    },
)
JsonMatchPatternTypeDef = TypedDict(
    "JsonMatchPatternTypeDef",
    {
        "All": NotRequired[Mapping[str, Any]],
        "IncludedPaths": NotRequired[Sequence[str]],
    },
)
LabelMatchStatementTypeDef = TypedDict(
    "LabelMatchStatementTypeDef",
    {
        "Scope": LabelMatchScopeType,
        "Key": str,
    },
)
LabelTypeDef = TypedDict(
    "LabelTypeDef",
    {
        "Name": str,
    },
)
ListAPIKeysRequestRequestTypeDef = TypedDict(
    "ListAPIKeysRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ListAvailableManagedRuleGroupVersionsRequestRequestTypeDef = TypedDict(
    "ListAvailableManagedRuleGroupVersionsRequestRequestTypeDef",
    {
        "VendorName": str,
        "Name": str,
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ManagedRuleGroupVersionTypeDef = TypedDict(
    "ManagedRuleGroupVersionTypeDef",
    {
        "Name": NotRequired[str],
        "LastUpdateTimestamp": NotRequired[datetime],
    },
)
ListAvailableManagedRuleGroupsRequestRequestTypeDef = TypedDict(
    "ListAvailableManagedRuleGroupsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ManagedRuleGroupSummaryTypeDef = TypedDict(
    "ManagedRuleGroupSummaryTypeDef",
    {
        "VendorName": NotRequired[str],
        "Name": NotRequired[str],
        "VersioningSupported": NotRequired[bool],
        "Description": NotRequired[str],
    },
)
ListIPSetsRequestRequestTypeDef = TypedDict(
    "ListIPSetsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ListLoggingConfigurationsRequestRequestTypeDef = TypedDict(
    "ListLoggingConfigurationsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ListManagedRuleSetsRequestRequestTypeDef = TypedDict(
    "ListManagedRuleSetsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ManagedRuleSetSummaryTypeDef = TypedDict(
    "ManagedRuleSetSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "Description": NotRequired[str],
        "LockToken": NotRequired[str],
        "ARN": NotRequired[str],
        "LabelNamespace": NotRequired[str],
    },
)
ListMobileSdkReleasesRequestRequestTypeDef = TypedDict(
    "ListMobileSdkReleasesRequestRequestTypeDef",
    {
        "Platform": PlatformType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ReleaseSummaryTypeDef = TypedDict(
    "ReleaseSummaryTypeDef",
    {
        "ReleaseVersion": NotRequired[str],
        "Timestamp": NotRequired[datetime],
    },
)
ListRegexPatternSetsRequestRequestTypeDef = TypedDict(
    "ListRegexPatternSetsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ListResourcesForWebACLRequestRequestTypeDef = TypedDict(
    "ListResourcesForWebACLRequestRequestTypeDef",
    {
        "WebACLArn": str,
        "ResourceType": NotRequired[ResourceTypeType],
    },
)
ListRuleGroupsRequestRequestTypeDef = TypedDict(
    "ListRuleGroupsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ListTagsForResourceRequestRequestTypeDef = TypedDict(
    "ListTagsForResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
ListWebACLsRequestRequestTypeDef = TypedDict(
    "ListWebACLsRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "NextMarker": NotRequired[str],
        "Limit": NotRequired[int],
    },
)
PasswordFieldTypeDef = TypedDict(
    "PasswordFieldTypeDef",
    {
        "Identifier": str,
    },
)
UsernameFieldTypeDef = TypedDict(
    "UsernameFieldTypeDef",
    {
        "Identifier": str,
    },
)
ManagedRuleSetVersionTypeDef = TypedDict(
    "ManagedRuleSetVersionTypeDef",
    {
        "AssociatedRuleGroupArn": NotRequired[str],
        "Capacity": NotRequired[int],
        "ForecastedLifetime": NotRequired[int],
        "PublishTimestamp": NotRequired[datetime],
        "LastUpdateTimestamp": NotRequired[datetime],
        "ExpiryTimestamp": NotRequired[datetime],
    },
)
NotStatementTypeDef = TypedDict(
    "NotStatementTypeDef",
    {
        "Statement": "StatementTypeDef",
    },
)
OrStatementTypeDef = TypedDict(
    "OrStatementTypeDef",
    {
        "Statements": Sequence["StatementTypeDef"],
    },
)
PhoneNumberFieldTypeDef = TypedDict(
    "PhoneNumberFieldTypeDef",
    {
        "Identifier": str,
    },
)
VersionToPublishTypeDef = TypedDict(
    "VersionToPublishTypeDef",
    {
        "AssociatedRuleGroupArn": NotRequired[str],
        "ForecastedLifetime": NotRequired[int],
    },
)
PutPermissionPolicyRequestRequestTypeDef = TypedDict(
    "PutPermissionPolicyRequestRequestTypeDef",
    {
        "ResourceArn": str,
        "Policy": str,
    },
)
RateLimitLabelNamespaceTypeDef = TypedDict(
    "RateLimitLabelNamespaceTypeDef",
    {
        "Namespace": str,
    },
)
ResponseInspectionBodyContainsTypeDef = TypedDict(
    "ResponseInspectionBodyContainsTypeDef",
    {
        "SuccessStrings": Sequence[str],
        "FailureStrings": Sequence[str],
    },
)
ResponseInspectionHeaderTypeDef = TypedDict(
    "ResponseInspectionHeaderTypeDef",
    {
        "Name": str,
        "SuccessValues": Sequence[str],
        "FailureValues": Sequence[str],
    },
)
ResponseInspectionJsonTypeDef = TypedDict(
    "ResponseInspectionJsonTypeDef",
    {
        "Identifier": str,
        "SuccessValues": Sequence[str],
        "FailureValues": Sequence[str],
    },
)
ResponseInspectionStatusCodeTypeDef = TypedDict(
    "ResponseInspectionStatusCodeTypeDef",
    {
        "SuccessCodes": Sequence[int],
        "FailureCodes": Sequence[int],
    },
)
TimestampTypeDef = Union[datetime, str]
UntagResourceRequestRequestTypeDef = TypedDict(
    "UntagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "TagKeys": Sequence[str],
    },
)
UpdateIPSetRequestRequestTypeDef = TypedDict(
    "UpdateIPSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "Addresses": Sequence[str],
        "LockToken": str,
        "Description": NotRequired[str],
    },
)
AssociationConfigTypeDef = TypedDict(
    "AssociationConfigTypeDef",
    {
        "RequestBody": NotRequired[
            Mapping[Literal["CLOUDFRONT"], RequestBodyAssociatedResourceTypeConfigTypeDef]
        ],
    },
)
RateLimitCookieTypeDef = TypedDict(
    "RateLimitCookieTypeDef",
    {
        "Name": str,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
RateLimitHeaderTypeDef = TypedDict(
    "RateLimitHeaderTypeDef",
    {
        "Name": str,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
RateLimitQueryArgumentTypeDef = TypedDict(
    "RateLimitQueryArgumentTypeDef",
    {
        "Name": str,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
RateLimitQueryStringTypeDef = TypedDict(
    "RateLimitQueryStringTypeDef",
    {
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
RateLimitUriPathTypeDef = TypedDict(
    "RateLimitUriPathTypeDef",
    {
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
CaptchaConfigTypeDef = TypedDict(
    "CaptchaConfigTypeDef",
    {
        "ImmunityTimeProperty": NotRequired[ImmunityTimePropertyTypeDef],
    },
)
ChallengeConfigTypeDef = TypedDict(
    "ChallengeConfigTypeDef",
    {
        "ImmunityTimeProperty": NotRequired[ImmunityTimePropertyTypeDef],
    },
)
CheckCapacityResponseTypeDef = TypedDict(
    "CheckCapacityResponseTypeDef",
    {
        "Capacity": int,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateAPIKeyResponseTypeDef = TypedDict(
    "CreateAPIKeyResponseTypeDef",
    {
        "APIKey": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DeleteFirewallManagerRuleGroupsResponseTypeDef = TypedDict(
    "DeleteFirewallManagerRuleGroupsResponseTypeDef",
    {
        "NextWebACLLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GenerateMobileSdkReleaseUrlResponseTypeDef = TypedDict(
    "GenerateMobileSdkReleaseUrlResponseTypeDef",
    {
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetDecryptedAPIKeyResponseTypeDef = TypedDict(
    "GetDecryptedAPIKeyResponseTypeDef",
    {
        "TokenDomains": List[str],
        "CreationTimestamp": datetime,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPermissionPolicyResponseTypeDef = TypedDict(
    "GetPermissionPolicyResponseTypeDef",
    {
        "Policy": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAPIKeysResponseTypeDef = TypedDict(
    "ListAPIKeysResponseTypeDef",
    {
        "NextMarker": str,
        "APIKeySummaries": List[APIKeySummaryTypeDef],
        "ApplicationIntegrationURL": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListResourcesForWebACLResponseTypeDef = TypedDict(
    "ListResourcesForWebACLResponseTypeDef",
    {
        "ResourceArns": List[str],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutManagedRuleSetVersionsResponseTypeDef = TypedDict(
    "PutManagedRuleSetVersionsResponseTypeDef",
    {
        "NextLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateIPSetResponseTypeDef = TypedDict(
    "UpdateIPSetResponseTypeDef",
    {
        "NextLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateManagedRuleSetVersionExpiryDateResponseTypeDef = TypedDict(
    "UpdateManagedRuleSetVersionExpiryDateResponseTypeDef",
    {
        "ExpiringVersion": str,
        "ExpiryTimestamp": datetime,
        "NextLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateRegexPatternSetResponseTypeDef = TypedDict(
    "UpdateRegexPatternSetResponseTypeDef",
    {
        "NextLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateRuleGroupResponseTypeDef = TypedDict(
    "UpdateRuleGroupResponseTypeDef",
    {
        "NextLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateWebACLResponseTypeDef = TypedDict(
    "UpdateWebACLResponseTypeDef",
    {
        "NextLockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ConditionTypeDef = TypedDict(
    "ConditionTypeDef",
    {
        "ActionCondition": NotRequired[ActionConditionTypeDef],
        "LabelNameCondition": NotRequired[LabelNameConditionTypeDef],
    },
)
CookiesTypeDef = TypedDict(
    "CookiesTypeDef",
    {
        "MatchPattern": CookieMatchPatternTypeDef,
        "MatchScope": MapMatchScopeType,
        "OversizeHandling": OversizeHandlingType,
    },
)
CreateIPSetRequestRequestTypeDef = TypedDict(
    "CreateIPSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "IPAddressVersion": IPAddressVersionType,
        "Addresses": Sequence[str],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
MobileSdkReleaseTypeDef = TypedDict(
    "MobileSdkReleaseTypeDef",
    {
        "ReleaseVersion": NotRequired[str],
        "Timestamp": NotRequired[datetime],
        "ReleaseNotes": NotRequired[str],
        "Tags": NotRequired[List[TagTypeDef]],
    },
)
TagInfoForResourceTypeDef = TypedDict(
    "TagInfoForResourceTypeDef",
    {
        "ResourceARN": NotRequired[str],
        "TagList": NotRequired[List[TagTypeDef]],
    },
)
TagResourceRequestRequestTypeDef = TypedDict(
    "TagResourceRequestRequestTypeDef",
    {
        "ResourceARN": str,
        "Tags": Sequence[TagTypeDef],
    },
)
CreateIPSetResponseTypeDef = TypedDict(
    "CreateIPSetResponseTypeDef",
    {
        "Summary": IPSetSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListIPSetsResponseTypeDef = TypedDict(
    "ListIPSetsResponseTypeDef",
    {
        "NextMarker": str,
        "IPSets": List[IPSetSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRegexPatternSetRequestRequestTypeDef = TypedDict(
    "CreateRegexPatternSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "RegularExpressionList": Sequence[RegexTypeDef],
        "Description": NotRequired[str],
        "Tags": NotRequired[Sequence[TagTypeDef]],
    },
)
RegexPatternSetTypeDef = TypedDict(
    "RegexPatternSetTypeDef",
    {
        "Name": NotRequired[str],
        "Id": NotRequired[str],
        "ARN": NotRequired[str],
        "Description": NotRequired[str],
        "RegularExpressionList": NotRequired[List[RegexTypeDef]],
    },
)
UpdateRegexPatternSetRequestRequestTypeDef = TypedDict(
    "UpdateRegexPatternSetRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "RegularExpressionList": Sequence[RegexTypeDef],
        "LockToken": str,
        "Description": NotRequired[str],
    },
)
CreateRegexPatternSetResponseTypeDef = TypedDict(
    "CreateRegexPatternSetResponseTypeDef",
    {
        "Summary": RegexPatternSetSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListRegexPatternSetsResponseTypeDef = TypedDict(
    "ListRegexPatternSetsResponseTypeDef",
    {
        "NextMarker": str,
        "RegexPatternSets": List[RegexPatternSetSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateRuleGroupResponseTypeDef = TypedDict(
    "CreateRuleGroupResponseTypeDef",
    {
        "Summary": RuleGroupSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListRuleGroupsResponseTypeDef = TypedDict(
    "ListRuleGroupsResponseTypeDef",
    {
        "NextMarker": str,
        "RuleGroups": List[RuleGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CreateWebACLResponseTypeDef = TypedDict(
    "CreateWebACLResponseTypeDef",
    {
        "Summary": WebACLSummaryTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListWebACLsResponseTypeDef = TypedDict(
    "ListWebACLsResponseTypeDef",
    {
        "NextMarker": str,
        "WebACLs": List[WebACLSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CustomRequestHandlingTypeDef = TypedDict(
    "CustomRequestHandlingTypeDef",
    {
        "InsertHeaders": Sequence[CustomHTTPHeaderTypeDef],
    },
)
CustomResponseTypeDef = TypedDict(
    "CustomResponseTypeDef",
    {
        "ResponseCode": int,
        "CustomResponseBodyKey": NotRequired[str],
        "ResponseHeaders": NotRequired[Sequence[CustomHTTPHeaderTypeDef]],
    },
)
DescribeAllManagedProductsResponseTypeDef = TypedDict(
    "DescribeAllManagedProductsResponseTypeDef",
    {
        "ManagedProducts": List[ManagedProductDescriptorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeManagedProductsByVendorResponseTypeDef = TypedDict(
    "DescribeManagedProductsByVendorResponseTypeDef",
    {
        "ManagedProducts": List[ManagedProductDescriptorTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GeoMatchStatementTypeDef = TypedDict(
    "GeoMatchStatementTypeDef",
    {
        "CountryCodes": NotRequired[Sequence[CountryCodeType]],
        "ForwardedIPConfig": NotRequired[ForwardedIPConfigTypeDef],
    },
)
GetIPSetResponseTypeDef = TypedDict(
    "GetIPSetResponseTypeDef",
    {
        "IPSet": IPSetTypeDef,
        "LockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetRateBasedStatementManagedKeysResponseTypeDef = TypedDict(
    "GetRateBasedStatementManagedKeysResponseTypeDef",
    {
        "ManagedKeysIPV4": RateBasedStatementManagedKeysIPSetTypeDef,
        "ManagedKeysIPV6": RateBasedStatementManagedKeysIPSetTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
HTTPRequestTypeDef = TypedDict(
    "HTTPRequestTypeDef",
    {
        "ClientIP": NotRequired[str],
        "Country": NotRequired[str],
        "URI": NotRequired[str],
        "Method": NotRequired[str],
        "HTTPVersion": NotRequired[str],
        "Headers": NotRequired[List[HTTPHeaderTypeDef]],
    },
)
HeadersTypeDef = TypedDict(
    "HeadersTypeDef",
    {
        "MatchPattern": HeaderMatchPatternTypeDef,
        "MatchScope": MapMatchScopeType,
        "OversizeHandling": OversizeHandlingType,
    },
)
IPSetReferenceStatementTypeDef = TypedDict(
    "IPSetReferenceStatementTypeDef",
    {
        "ARN": str,
        "IPSetForwardedIPConfig": NotRequired[IPSetForwardedIPConfigTypeDef],
    },
)
JsonBodyTypeDef = TypedDict(
    "JsonBodyTypeDef",
    {
        "MatchPattern": JsonMatchPatternTypeDef,
        "MatchScope": JsonMatchScopeType,
        "InvalidFallbackBehavior": NotRequired[BodyParsingFallbackBehaviorType],
        "OversizeHandling": NotRequired[OversizeHandlingType],
    },
)
ListAvailableManagedRuleGroupVersionsResponseTypeDef = TypedDict(
    "ListAvailableManagedRuleGroupVersionsResponseTypeDef",
    {
        "NextMarker": str,
        "Versions": List[ManagedRuleGroupVersionTypeDef],
        "CurrentDefaultVersion": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListAvailableManagedRuleGroupsResponseTypeDef = TypedDict(
    "ListAvailableManagedRuleGroupsResponseTypeDef",
    {
        "NextMarker": str,
        "ManagedRuleGroups": List[ManagedRuleGroupSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListManagedRuleSetsResponseTypeDef = TypedDict(
    "ListManagedRuleSetsResponseTypeDef",
    {
        "NextMarker": str,
        "ManagedRuleSets": List[ManagedRuleSetSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListMobileSdkReleasesResponseTypeDef = TypedDict(
    "ListMobileSdkReleasesResponseTypeDef",
    {
        "ReleaseSummaries": List[ReleaseSummaryTypeDef],
        "NextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
RequestInspectionTypeDef = TypedDict(
    "RequestInspectionTypeDef",
    {
        "PayloadType": PayloadTypeType,
        "UsernameField": UsernameFieldTypeDef,
        "PasswordField": PasswordFieldTypeDef,
    },
)
ManagedRuleSetTypeDef = TypedDict(
    "ManagedRuleSetTypeDef",
    {
        "Name": str,
        "Id": str,
        "ARN": str,
        "Description": NotRequired[str],
        "PublishedVersions": NotRequired[Dict[str, ManagedRuleSetVersionTypeDef]],
        "RecommendedVersion": NotRequired[str],
        "LabelNamespace": NotRequired[str],
    },
)
RequestInspectionACFPTypeDef = TypedDict(
    "RequestInspectionACFPTypeDef",
    {
        "PayloadType": PayloadTypeType,
        "UsernameField": NotRequired[UsernameFieldTypeDef],
        "PasswordField": NotRequired[PasswordFieldTypeDef],
        "EmailField": NotRequired[EmailFieldTypeDef],
        "PhoneNumberFields": NotRequired[Sequence[PhoneNumberFieldTypeDef]],
        "AddressFields": NotRequired[Sequence[AddressFieldTypeDef]],
    },
)
PutManagedRuleSetVersionsRequestRequestTypeDef = TypedDict(
    "PutManagedRuleSetVersionsRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "LockToken": str,
        "RecommendedVersion": NotRequired[str],
        "VersionsToPublish": NotRequired[Mapping[str, VersionToPublishTypeDef]],
    },
)
ResponseInspectionTypeDef = TypedDict(
    "ResponseInspectionTypeDef",
    {
        "StatusCode": NotRequired[ResponseInspectionStatusCodeTypeDef],
        "Header": NotRequired[ResponseInspectionHeaderTypeDef],
        "BodyContains": NotRequired[ResponseInspectionBodyContainsTypeDef],
        "Json": NotRequired[ResponseInspectionJsonTypeDef],
    },
)
TimeWindowTypeDef = TypedDict(
    "TimeWindowTypeDef",
    {
        "StartTime": TimestampTypeDef,
        "EndTime": TimestampTypeDef,
    },
)
UpdateManagedRuleSetVersionExpiryDateRequestRequestTypeDef = TypedDict(
    "UpdateManagedRuleSetVersionExpiryDateRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "LockToken": str,
        "VersionToExpire": str,
        "ExpiryTimestamp": TimestampTypeDef,
    },
)
RateBasedStatementCustomKeyTypeDef = TypedDict(
    "RateBasedStatementCustomKeyTypeDef",
    {
        "Header": NotRequired[RateLimitHeaderTypeDef],
        "Cookie": NotRequired[RateLimitCookieTypeDef],
        "QueryArgument": NotRequired[RateLimitQueryArgumentTypeDef],
        "QueryString": NotRequired[RateLimitQueryStringTypeDef],
        "HTTPMethod": NotRequired[Mapping[str, Any]],
        "ForwardedIP": NotRequired[Mapping[str, Any]],
        "IP": NotRequired[Mapping[str, Any]],
        "LabelNamespace": NotRequired[RateLimitLabelNamespaceTypeDef],
        "UriPath": NotRequired[RateLimitUriPathTypeDef],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Behavior": FilterBehaviorType,
        "Requirement": FilterRequirementType,
        "Conditions": List[ConditionTypeDef],
    },
)
GetMobileSdkReleaseResponseTypeDef = TypedDict(
    "GetMobileSdkReleaseResponseTypeDef",
    {
        "MobileSdkRelease": MobileSdkReleaseTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListTagsForResourceResponseTypeDef = TypedDict(
    "ListTagsForResourceResponseTypeDef",
    {
        "NextMarker": str,
        "TagInfoForResource": TagInfoForResourceTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetRegexPatternSetResponseTypeDef = TypedDict(
    "GetRegexPatternSetResponseTypeDef",
    {
        "RegexPatternSet": RegexPatternSetTypeDef,
        "LockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AllowActionTypeDef = TypedDict(
    "AllowActionTypeDef",
    {
        "CustomRequestHandling": NotRequired[CustomRequestHandlingTypeDef],
    },
)
CaptchaActionTypeDef = TypedDict(
    "CaptchaActionTypeDef",
    {
        "CustomRequestHandling": NotRequired[CustomRequestHandlingTypeDef],
    },
)
ChallengeActionTypeDef = TypedDict(
    "ChallengeActionTypeDef",
    {
        "CustomRequestHandling": NotRequired[CustomRequestHandlingTypeDef],
    },
)
CountActionTypeDef = TypedDict(
    "CountActionTypeDef",
    {
        "CustomRequestHandling": NotRequired[CustomRequestHandlingTypeDef],
    },
)
BlockActionTypeDef = TypedDict(
    "BlockActionTypeDef",
    {
        "CustomResponse": NotRequired[CustomResponseTypeDef],
    },
)
SampledHTTPRequestTypeDef = TypedDict(
    "SampledHTTPRequestTypeDef",
    {
        "Request": HTTPRequestTypeDef,
        "Weight": int,
        "Timestamp": NotRequired[datetime],
        "Action": NotRequired[str],
        "RuleNameWithinRuleGroup": NotRequired[str],
        "RequestHeadersInserted": NotRequired[List[HTTPHeaderTypeDef]],
        "ResponseCodeSent": NotRequired[int],
        "Labels": NotRequired[List[LabelTypeDef]],
        "CaptchaResponse": NotRequired[CaptchaResponseTypeDef],
        "ChallengeResponse": NotRequired[ChallengeResponseTypeDef],
        "OverriddenAction": NotRequired[str],
    },
)
FieldToMatchTypeDef = TypedDict(
    "FieldToMatchTypeDef",
    {
        "SingleHeader": NotRequired[SingleHeaderTypeDef],
        "SingleQueryArgument": NotRequired[SingleQueryArgumentTypeDef],
        "AllQueryArguments": NotRequired[Mapping[str, Any]],
        "UriPath": NotRequired[Mapping[str, Any]],
        "QueryString": NotRequired[Mapping[str, Any]],
        "Body": NotRequired[BodyTypeDef],
        "Method": NotRequired[Mapping[str, Any]],
        "JsonBody": NotRequired[JsonBodyTypeDef],
        "Headers": NotRequired[HeadersTypeDef],
        "Cookies": NotRequired[CookiesTypeDef],
        "HeaderOrder": NotRequired[HeaderOrderTypeDef],
        "JA3Fingerprint": NotRequired[JA3FingerprintTypeDef],
    },
)
GetManagedRuleSetResponseTypeDef = TypedDict(
    "GetManagedRuleSetResponseTypeDef",
    {
        "ManagedRuleSet": ManagedRuleSetTypeDef,
        "LockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
AWSManagedRulesACFPRuleSetTypeDef = TypedDict(
    "AWSManagedRulesACFPRuleSetTypeDef",
    {
        "CreationPath": str,
        "RegistrationPagePath": str,
        "RequestInspection": RequestInspectionACFPTypeDef,
        "ResponseInspection": NotRequired[ResponseInspectionTypeDef],
        "EnableRegexInPath": NotRequired[bool],
    },
)
AWSManagedRulesATPRuleSetTypeDef = TypedDict(
    "AWSManagedRulesATPRuleSetTypeDef",
    {
        "LoginPath": str,
        "RequestInspection": NotRequired[RequestInspectionTypeDef],
        "ResponseInspection": NotRequired[ResponseInspectionTypeDef],
        "EnableRegexInPath": NotRequired[bool],
    },
)
GetSampledRequestsRequestRequestTypeDef = TypedDict(
    "GetSampledRequestsRequestRequestTypeDef",
    {
        "WebAclArn": str,
        "RuleMetricName": str,
        "Scope": ScopeType,
        "TimeWindow": TimeWindowTypeDef,
        "MaxItems": int,
    },
)
RateBasedStatementTypeDef = TypedDict(
    "RateBasedStatementTypeDef",
    {
        "Limit": int,
        "AggregateKeyType": RateBasedStatementAggregateKeyTypeType,
        "ScopeDownStatement": NotRequired["StatementTypeDef"],
        "ForwardedIPConfig": NotRequired[ForwardedIPConfigTypeDef],
        "CustomKeys": NotRequired[Sequence[RateBasedStatementCustomKeyTypeDef]],
    },
)
LoggingFilterTypeDef = TypedDict(
    "LoggingFilterTypeDef",
    {
        "Filters": List[FilterTypeDef],
        "DefaultBehavior": FilterBehaviorType,
    },
)
OverrideActionTypeDef = TypedDict(
    "OverrideActionTypeDef",
    {
        "Count": NotRequired[CountActionTypeDef],
        "None": NotRequired[Mapping[str, Any]],
    },
)
DefaultActionTypeDef = TypedDict(
    "DefaultActionTypeDef",
    {
        "Block": NotRequired[BlockActionTypeDef],
        "Allow": NotRequired[AllowActionTypeDef],
    },
)
RuleActionTypeDef = TypedDict(
    "RuleActionTypeDef",
    {
        "Block": NotRequired[BlockActionTypeDef],
        "Allow": NotRequired[AllowActionTypeDef],
        "Count": NotRequired[CountActionTypeDef],
        "Captcha": NotRequired[CaptchaActionTypeDef],
        "Challenge": NotRequired[ChallengeActionTypeDef],
    },
)
GetSampledRequestsResponseTypeDef = TypedDict(
    "GetSampledRequestsResponseTypeDef",
    {
        "SampledRequests": List[SampledHTTPRequestTypeDef],
        "PopulationSize": int,
        "TimeWindow": TimeWindowTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ByteMatchStatementTypeDef = TypedDict(
    "ByteMatchStatementTypeDef",
    {
        "SearchString": BlobTypeDef,
        "FieldToMatch": FieldToMatchTypeDef,
        "TextTransformations": Sequence[TextTransformationTypeDef],
        "PositionalConstraint": PositionalConstraintType,
    },
)
RegexMatchStatementTypeDef = TypedDict(
    "RegexMatchStatementTypeDef",
    {
        "RegexString": str,
        "FieldToMatch": FieldToMatchTypeDef,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
RegexPatternSetReferenceStatementTypeDef = TypedDict(
    "RegexPatternSetReferenceStatementTypeDef",
    {
        "ARN": str,
        "FieldToMatch": FieldToMatchTypeDef,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
SizeConstraintStatementTypeDef = TypedDict(
    "SizeConstraintStatementTypeDef",
    {
        "FieldToMatch": FieldToMatchTypeDef,
        "ComparisonOperator": ComparisonOperatorType,
        "Size": int,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
SqliMatchStatementTypeDef = TypedDict(
    "SqliMatchStatementTypeDef",
    {
        "FieldToMatch": FieldToMatchTypeDef,
        "TextTransformations": Sequence[TextTransformationTypeDef],
        "SensitivityLevel": NotRequired[SensitivityLevelType],
    },
)
XssMatchStatementTypeDef = TypedDict(
    "XssMatchStatementTypeDef",
    {
        "FieldToMatch": FieldToMatchTypeDef,
        "TextTransformations": Sequence[TextTransformationTypeDef],
    },
)
ManagedRuleGroupConfigTypeDef = TypedDict(
    "ManagedRuleGroupConfigTypeDef",
    {
        "LoginPath": NotRequired[str],
        "PayloadType": NotRequired[PayloadTypeType],
        "UsernameField": NotRequired[UsernameFieldTypeDef],
        "PasswordField": NotRequired[PasswordFieldTypeDef],
        "AWSManagedRulesBotControlRuleSet": NotRequired[AWSManagedRulesBotControlRuleSetTypeDef],
        "AWSManagedRulesATPRuleSet": NotRequired[AWSManagedRulesATPRuleSetTypeDef],
        "AWSManagedRulesACFPRuleSet": NotRequired[AWSManagedRulesACFPRuleSetTypeDef],
    },
)
LoggingConfigurationTypeDef = TypedDict(
    "LoggingConfigurationTypeDef",
    {
        "ResourceArn": str,
        "LogDestinationConfigs": List[str],
        "RedactedFields": NotRequired[List[FieldToMatchTypeDef]],
        "ManagedByFirewallManager": NotRequired[bool],
        "LoggingFilter": NotRequired[LoggingFilterTypeDef],
    },
)
RuleActionOverrideTypeDef = TypedDict(
    "RuleActionOverrideTypeDef",
    {
        "Name": str,
        "ActionToUse": RuleActionTypeDef,
    },
)
RuleSummaryTypeDef = TypedDict(
    "RuleSummaryTypeDef",
    {
        "Name": NotRequired[str],
        "Action": NotRequired[RuleActionTypeDef],
    },
)
RuleTypeDef = TypedDict(
    "RuleTypeDef",
    {
        "Name": str,
        "Priority": int,
        "Statement": "StatementTypeDef",
        "VisibilityConfig": VisibilityConfigTypeDef,
        "Action": NotRequired[RuleActionTypeDef],
        "OverrideAction": NotRequired[OverrideActionTypeDef],
        "RuleLabels": NotRequired[Sequence[LabelTypeDef]],
        "CaptchaConfig": NotRequired[CaptchaConfigTypeDef],
        "ChallengeConfig": NotRequired[ChallengeConfigTypeDef],
    },
)
GetLoggingConfigurationResponseTypeDef = TypedDict(
    "GetLoggingConfigurationResponseTypeDef",
    {
        "LoggingConfiguration": LoggingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListLoggingConfigurationsResponseTypeDef = TypedDict(
    "ListLoggingConfigurationsResponseTypeDef",
    {
        "LoggingConfigurations": List[LoggingConfigurationTypeDef],
        "NextMarker": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
PutLoggingConfigurationRequestRequestTypeDef = TypedDict(
    "PutLoggingConfigurationRequestRequestTypeDef",
    {
        "LoggingConfiguration": LoggingConfigurationTypeDef,
    },
)
PutLoggingConfigurationResponseTypeDef = TypedDict(
    "PutLoggingConfigurationResponseTypeDef",
    {
        "LoggingConfiguration": LoggingConfigurationTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ManagedRuleGroupStatementTypeDef = TypedDict(
    "ManagedRuleGroupStatementTypeDef",
    {
        "VendorName": str,
        "Name": str,
        "Version": NotRequired[str],
        "ExcludedRules": NotRequired[Sequence[ExcludedRuleTypeDef]],
        "ScopeDownStatement": NotRequired["StatementTypeDef"],
        "ManagedRuleGroupConfigs": NotRequired[Sequence[ManagedRuleGroupConfigTypeDef]],
        "RuleActionOverrides": NotRequired[Sequence[RuleActionOverrideTypeDef]],
    },
)
RuleGroupReferenceStatementTypeDef = TypedDict(
    "RuleGroupReferenceStatementTypeDef",
    {
        "ARN": str,
        "ExcludedRules": NotRequired[Sequence[ExcludedRuleTypeDef]],
        "RuleActionOverrides": NotRequired[Sequence[RuleActionOverrideTypeDef]],
    },
)
DescribeManagedRuleGroupResponseTypeDef = TypedDict(
    "DescribeManagedRuleGroupResponseTypeDef",
    {
        "VersionName": str,
        "SnsTopicArn": str,
        "Capacity": int,
        "Rules": List[RuleSummaryTypeDef],
        "LabelNamespace": str,
        "AvailableLabels": List[LabelSummaryTypeDef],
        "ConsumedLabels": List[LabelSummaryTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
CheckCapacityRequestRequestTypeDef = TypedDict(
    "CheckCapacityRequestRequestTypeDef",
    {
        "Scope": ScopeType,
        "Rules": Sequence[RuleTypeDef],
    },
)
CreateRuleGroupRequestRequestTypeDef = TypedDict(
    "CreateRuleGroupRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Capacity": int,
        "VisibilityConfig": VisibilityConfigTypeDef,
        "Description": NotRequired[str],
        "Rules": NotRequired[Sequence[RuleTypeDef]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "CustomResponseBodies": NotRequired[Mapping[str, CustomResponseBodyTypeDef]],
    },
)
CreateWebACLRequestRequestTypeDef = TypedDict(
    "CreateWebACLRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "DefaultAction": DefaultActionTypeDef,
        "VisibilityConfig": VisibilityConfigTypeDef,
        "Description": NotRequired[str],
        "Rules": NotRequired[Sequence[RuleTypeDef]],
        "Tags": NotRequired[Sequence[TagTypeDef]],
        "CustomResponseBodies": NotRequired[Mapping[str, CustomResponseBodyTypeDef]],
        "CaptchaConfig": NotRequired[CaptchaConfigTypeDef],
        "ChallengeConfig": NotRequired[ChallengeConfigTypeDef],
        "TokenDomains": NotRequired[Sequence[str]],
        "AssociationConfig": NotRequired[AssociationConfigTypeDef],
    },
)
RuleGroupTypeDef = TypedDict(
    "RuleGroupTypeDef",
    {
        "Name": str,
        "Id": str,
        "Capacity": int,
        "ARN": str,
        "VisibilityConfig": VisibilityConfigTypeDef,
        "Description": NotRequired[str],
        "Rules": NotRequired[List[RuleTypeDef]],
        "LabelNamespace": NotRequired[str],
        "CustomResponseBodies": NotRequired[Dict[str, CustomResponseBodyTypeDef]],
        "AvailableLabels": NotRequired[List[LabelSummaryTypeDef]],
        "ConsumedLabels": NotRequired[List[LabelSummaryTypeDef]],
    },
)
UpdateRuleGroupRequestRequestTypeDef = TypedDict(
    "UpdateRuleGroupRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "VisibilityConfig": VisibilityConfigTypeDef,
        "LockToken": str,
        "Description": NotRequired[str],
        "Rules": NotRequired[Sequence[RuleTypeDef]],
        "CustomResponseBodies": NotRequired[Mapping[str, CustomResponseBodyTypeDef]],
    },
)
UpdateWebACLRequestRequestTypeDef = TypedDict(
    "UpdateWebACLRequestRequestTypeDef",
    {
        "Name": str,
        "Scope": ScopeType,
        "Id": str,
        "DefaultAction": DefaultActionTypeDef,
        "VisibilityConfig": VisibilityConfigTypeDef,
        "LockToken": str,
        "Description": NotRequired[str],
        "Rules": NotRequired[Sequence[RuleTypeDef]],
        "CustomResponseBodies": NotRequired[Mapping[str, CustomResponseBodyTypeDef]],
        "CaptchaConfig": NotRequired[CaptchaConfigTypeDef],
        "ChallengeConfig": NotRequired[ChallengeConfigTypeDef],
        "TokenDomains": NotRequired[Sequence[str]],
        "AssociationConfig": NotRequired[AssociationConfigTypeDef],
    },
)
FirewallManagerStatementTypeDef = TypedDict(
    "FirewallManagerStatementTypeDef",
    {
        "ManagedRuleGroupStatement": NotRequired[ManagedRuleGroupStatementTypeDef],
        "RuleGroupReferenceStatement": NotRequired[RuleGroupReferenceStatementTypeDef],
    },
)
StatementTypeDef = TypedDict(
    "StatementTypeDef",
    {
        "ByteMatchStatement": NotRequired[ByteMatchStatementTypeDef],
        "SqliMatchStatement": NotRequired[SqliMatchStatementTypeDef],
        "XssMatchStatement": NotRequired[XssMatchStatementTypeDef],
        "SizeConstraintStatement": NotRequired[SizeConstraintStatementTypeDef],
        "GeoMatchStatement": NotRequired[GeoMatchStatementTypeDef],
        "RuleGroupReferenceStatement": NotRequired[RuleGroupReferenceStatementTypeDef],
        "IPSetReferenceStatement": NotRequired[IPSetReferenceStatementTypeDef],
        "RegexPatternSetReferenceStatement": NotRequired[RegexPatternSetReferenceStatementTypeDef],
        "RateBasedStatement": NotRequired[Dict[str, Any]],
        "AndStatement": NotRequired[Dict[str, Any]],
        "OrStatement": NotRequired[Dict[str, Any]],
        "NotStatement": NotRequired[Dict[str, Any]],
        "ManagedRuleGroupStatement": NotRequired[Dict[str, Any]],
        "LabelMatchStatement": NotRequired[LabelMatchStatementTypeDef],
        "RegexMatchStatement": NotRequired[RegexMatchStatementTypeDef],
    },
)
GetRuleGroupResponseTypeDef = TypedDict(
    "GetRuleGroupResponseTypeDef",
    {
        "RuleGroup": RuleGroupTypeDef,
        "LockToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
FirewallManagerRuleGroupTypeDef = TypedDict(
    "FirewallManagerRuleGroupTypeDef",
    {
        "Name": str,
        "Priority": int,
        "FirewallManagerStatement": FirewallManagerStatementTypeDef,
        "OverrideAction": OverrideActionTypeDef,
        "VisibilityConfig": VisibilityConfigTypeDef,
    },
)
WebACLTypeDef = TypedDict(
    "WebACLTypeDef",
    {
        "Name": str,
        "Id": str,
        "ARN": str,
        "DefaultAction": DefaultActionTypeDef,
        "VisibilityConfig": VisibilityConfigTypeDef,
        "Description": NotRequired[str],
        "Rules": NotRequired[List[RuleTypeDef]],
        "Capacity": NotRequired[int],
        "PreProcessFirewallManagerRuleGroups": NotRequired[List[FirewallManagerRuleGroupTypeDef]],
        "PostProcessFirewallManagerRuleGroups": NotRequired[List[FirewallManagerRuleGroupTypeDef]],
        "ManagedByFirewallManager": NotRequired[bool],
        "LabelNamespace": NotRequired[str],
        "CustomResponseBodies": NotRequired[Dict[str, CustomResponseBodyTypeDef]],
        "CaptchaConfig": NotRequired[CaptchaConfigTypeDef],
        "ChallengeConfig": NotRequired[ChallengeConfigTypeDef],
        "TokenDomains": NotRequired[List[str]],
        "AssociationConfig": NotRequired[AssociationConfigTypeDef],
    },
)
GetWebACLForResourceResponseTypeDef = TypedDict(
    "GetWebACLForResourceResponseTypeDef",
    {
        "WebACL": WebACLTypeDef,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetWebACLResponseTypeDef = TypedDict(
    "GetWebACLResponseTypeDef",
    {
        "WebACL": WebACLTypeDef,
        "LockToken": str,
        "ApplicationIntegrationURL": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
