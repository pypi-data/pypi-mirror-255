"""
Type annotations for cost-optimization-hub service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/type_defs/)

Usage::

    ```python
    from mypy_boto3_cost_optimization_hub.type_defs import AccountEnrollmentStatusTypeDef

    data: AccountEnrollmentStatusTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Sequence

from .literals import (
    ActionTypeType,
    EnrollmentStatusType,
    ImplementationEffortType,
    MemberAccountDiscountVisibilityType,
    OrderType,
    ResourceTypeType,
    SavingsEstimationModeType,
    SourceType,
)

if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AccountEnrollmentStatusTypeDef",
    "BlockStoragePerformanceConfigurationTypeDef",
    "ComputeConfigurationTypeDef",
    "ComputeSavingsPlansConfigurationTypeDef",
    "StorageConfigurationTypeDef",
    "InstanceConfigurationTypeDef",
    "Ec2InstanceSavingsPlansConfigurationTypeDef",
    "Ec2ReservedInstancesConfigurationTypeDef",
    "ElastiCacheReservedInstancesConfigurationTypeDef",
    "EstimatedDiscountsTypeDef",
    "TagTypeDef",
    "ResponseMetadataTypeDef",
    "GetRecommendationRequestRequestTypeDef",
    "PaginatorConfigTypeDef",
    "ListEnrollmentStatusesRequestRequestTypeDef",
    "RecommendationSummaryTypeDef",
    "OrderByTypeDef",
    "OpenSearchReservedInstancesConfigurationTypeDef",
    "RdsReservedInstancesConfigurationTypeDef",
    "RedshiftReservedInstancesConfigurationTypeDef",
    "ReservedInstancesPricingTypeDef",
    "UsageTypeDef",
    "SageMakerSavingsPlansConfigurationTypeDef",
    "SavingsPlansPricingTypeDef",
    "UpdateEnrollmentStatusRequestRequestTypeDef",
    "UpdatePreferencesRequestRequestTypeDef",
    "EcsServiceConfigurationTypeDef",
    "LambdaFunctionConfigurationTypeDef",
    "EbsVolumeConfigurationTypeDef",
    "Ec2AutoScalingGroupConfigurationTypeDef",
    "Ec2InstanceConfigurationTypeDef",
    "ResourcePricingTypeDef",
    "FilterTypeDef",
    "RecommendationTypeDef",
    "GetPreferencesResponseTypeDef",
    "ListEnrollmentStatusesResponseTypeDef",
    "UpdateEnrollmentStatusResponseTypeDef",
    "UpdatePreferencesResponseTypeDef",
    "ListEnrollmentStatusesRequestListEnrollmentStatusesPaginateTypeDef",
    "ListRecommendationSummariesResponseTypeDef",
    "ReservedInstancesCostCalculationTypeDef",
    "SavingsPlansCostCalculationTypeDef",
    "ResourceCostCalculationTypeDef",
    "ListRecommendationSummariesRequestListRecommendationSummariesPaginateTypeDef",
    "ListRecommendationSummariesRequestRequestTypeDef",
    "ListRecommendationsRequestListRecommendationsPaginateTypeDef",
    "ListRecommendationsRequestRequestTypeDef",
    "ListRecommendationsResponseTypeDef",
    "Ec2ReservedInstancesTypeDef",
    "ElastiCacheReservedInstancesTypeDef",
    "OpenSearchReservedInstancesTypeDef",
    "RdsReservedInstancesTypeDef",
    "RedshiftReservedInstancesTypeDef",
    "ComputeSavingsPlansTypeDef",
    "Ec2InstanceSavingsPlansTypeDef",
    "SageMakerSavingsPlansTypeDef",
    "EbsVolumeTypeDef",
    "Ec2AutoScalingGroupTypeDef",
    "Ec2InstanceTypeDef",
    "EcsServiceTypeDef",
    "LambdaFunctionTypeDef",
    "ResourceDetailsTypeDef",
    "GetRecommendationResponseTypeDef",
)

AccountEnrollmentStatusTypeDef = TypedDict(
    "AccountEnrollmentStatusTypeDef",
    {
        "accountId": NotRequired[str],
        "createdTimestamp": NotRequired[datetime],
        "lastUpdatedTimestamp": NotRequired[datetime],
        "status": NotRequired[EnrollmentStatusType],
    },
)
BlockStoragePerformanceConfigurationTypeDef = TypedDict(
    "BlockStoragePerformanceConfigurationTypeDef",
    {
        "iops": NotRequired[float],
        "throughput": NotRequired[float],
    },
)
ComputeConfigurationTypeDef = TypedDict(
    "ComputeConfigurationTypeDef",
    {
        "architecture": NotRequired[str],
        "memorySizeInMB": NotRequired[int],
        "platform": NotRequired[str],
        "vCpu": NotRequired[float],
    },
)
ComputeSavingsPlansConfigurationTypeDef = TypedDict(
    "ComputeSavingsPlansConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "hourlyCommitment": NotRequired[str],
        "paymentOption": NotRequired[str],
        "term": NotRequired[str],
    },
)
StorageConfigurationTypeDef = TypedDict(
    "StorageConfigurationTypeDef",
    {
        "sizeInGb": NotRequired[float],
        "type": NotRequired[str],
    },
)
InstanceConfigurationTypeDef = TypedDict(
    "InstanceConfigurationTypeDef",
    {
        "type": NotRequired[str],
    },
)
Ec2InstanceSavingsPlansConfigurationTypeDef = TypedDict(
    "Ec2InstanceSavingsPlansConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "hourlyCommitment": NotRequired[str],
        "instanceFamily": NotRequired[str],
        "paymentOption": NotRequired[str],
        "savingsPlansRegion": NotRequired[str],
        "term": NotRequired[str],
    },
)
Ec2ReservedInstancesConfigurationTypeDef = TypedDict(
    "Ec2ReservedInstancesConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "currentGeneration": NotRequired[str],
        "instanceFamily": NotRequired[str],
        "instanceType": NotRequired[str],
        "monthlyRecurringCost": NotRequired[str],
        "normalizedUnitsToPurchase": NotRequired[str],
        "numberOfInstancesToPurchase": NotRequired[str],
        "offeringClass": NotRequired[str],
        "paymentOption": NotRequired[str],
        "platform": NotRequired[str],
        "reservedInstancesRegion": NotRequired[str],
        "service": NotRequired[str],
        "sizeFlexEligible": NotRequired[bool],
        "tenancy": NotRequired[str],
        "term": NotRequired[str],
        "upfrontCost": NotRequired[str],
    },
)
ElastiCacheReservedInstancesConfigurationTypeDef = TypedDict(
    "ElastiCacheReservedInstancesConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "currentGeneration": NotRequired[str],
        "instanceFamily": NotRequired[str],
        "instanceType": NotRequired[str],
        "monthlyRecurringCost": NotRequired[str],
        "normalizedUnitsToPurchase": NotRequired[str],
        "numberOfInstancesToPurchase": NotRequired[str],
        "paymentOption": NotRequired[str],
        "reservedInstancesRegion": NotRequired[str],
        "service": NotRequired[str],
        "sizeFlexEligible": NotRequired[bool],
        "term": NotRequired[str],
        "upfrontCost": NotRequired[str],
    },
)
EstimatedDiscountsTypeDef = TypedDict(
    "EstimatedDiscountsTypeDef",
    {
        "otherDiscount": NotRequired[float],
        "reservedInstancesDiscount": NotRequired[float],
        "savingsPlansDiscount": NotRequired[float],
    },
)
TagTypeDef = TypedDict(
    "TagTypeDef",
    {
        "key": NotRequired[str],
        "value": NotRequired[str],
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
GetRecommendationRequestRequestTypeDef = TypedDict(
    "GetRecommendationRequestRequestTypeDef",
    {
        "recommendationId": str,
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
ListEnrollmentStatusesRequestRequestTypeDef = TypedDict(
    "ListEnrollmentStatusesRequestRequestTypeDef",
    {
        "accountId": NotRequired[str],
        "includeOrganizationInfo": NotRequired[bool],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
RecommendationSummaryTypeDef = TypedDict(
    "RecommendationSummaryTypeDef",
    {
        "estimatedMonthlySavings": NotRequired[float],
        "group": NotRequired[str],
        "recommendationCount": NotRequired[int],
    },
)
OrderByTypeDef = TypedDict(
    "OrderByTypeDef",
    {
        "dimension": NotRequired[str],
        "order": NotRequired[OrderType],
    },
)
OpenSearchReservedInstancesConfigurationTypeDef = TypedDict(
    "OpenSearchReservedInstancesConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "currentGeneration": NotRequired[str],
        "instanceType": NotRequired[str],
        "monthlyRecurringCost": NotRequired[str],
        "normalizedUnitsToPurchase": NotRequired[str],
        "numberOfInstancesToPurchase": NotRequired[str],
        "paymentOption": NotRequired[str],
        "reservedInstancesRegion": NotRequired[str],
        "service": NotRequired[str],
        "sizeFlexEligible": NotRequired[bool],
        "term": NotRequired[str],
        "upfrontCost": NotRequired[str],
    },
)
RdsReservedInstancesConfigurationTypeDef = TypedDict(
    "RdsReservedInstancesConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "currentGeneration": NotRequired[str],
        "databaseEdition": NotRequired[str],
        "databaseEngine": NotRequired[str],
        "deploymentOption": NotRequired[str],
        "instanceFamily": NotRequired[str],
        "instanceType": NotRequired[str],
        "licenseModel": NotRequired[str],
        "monthlyRecurringCost": NotRequired[str],
        "normalizedUnitsToPurchase": NotRequired[str],
        "numberOfInstancesToPurchase": NotRequired[str],
        "paymentOption": NotRequired[str],
        "reservedInstancesRegion": NotRequired[str],
        "service": NotRequired[str],
        "sizeFlexEligible": NotRequired[bool],
        "term": NotRequired[str],
        "upfrontCost": NotRequired[str],
    },
)
RedshiftReservedInstancesConfigurationTypeDef = TypedDict(
    "RedshiftReservedInstancesConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "currentGeneration": NotRequired[str],
        "instanceFamily": NotRequired[str],
        "instanceType": NotRequired[str],
        "monthlyRecurringCost": NotRequired[str],
        "normalizedUnitsToPurchase": NotRequired[str],
        "numberOfInstancesToPurchase": NotRequired[str],
        "paymentOption": NotRequired[str],
        "reservedInstancesRegion": NotRequired[str],
        "service": NotRequired[str],
        "sizeFlexEligible": NotRequired[bool],
        "term": NotRequired[str],
        "upfrontCost": NotRequired[str],
    },
)
ReservedInstancesPricingTypeDef = TypedDict(
    "ReservedInstancesPricingTypeDef",
    {
        "estimatedMonthlyAmortizedReservationCost": NotRequired[float],
        "estimatedOnDemandCost": NotRequired[float],
        "monthlyReservationEligibleCost": NotRequired[float],
        "savingsPercentage": NotRequired[float],
    },
)
UsageTypeDef = TypedDict(
    "UsageTypeDef",
    {
        "operation": NotRequired[str],
        "productCode": NotRequired[str],
        "unit": NotRequired[str],
        "usageAmount": NotRequired[float],
        "usageType": NotRequired[str],
    },
)
SageMakerSavingsPlansConfigurationTypeDef = TypedDict(
    "SageMakerSavingsPlansConfigurationTypeDef",
    {
        "accountScope": NotRequired[str],
        "hourlyCommitment": NotRequired[str],
        "paymentOption": NotRequired[str],
        "term": NotRequired[str],
    },
)
SavingsPlansPricingTypeDef = TypedDict(
    "SavingsPlansPricingTypeDef",
    {
        "estimatedMonthlyCommitment": NotRequired[float],
        "estimatedOnDemandCost": NotRequired[float],
        "monthlySavingsPlansEligibleCost": NotRequired[float],
        "savingsPercentage": NotRequired[float],
    },
)
UpdateEnrollmentStatusRequestRequestTypeDef = TypedDict(
    "UpdateEnrollmentStatusRequestRequestTypeDef",
    {
        "status": EnrollmentStatusType,
        "includeMemberAccounts": NotRequired[bool],
    },
)
UpdatePreferencesRequestRequestTypeDef = TypedDict(
    "UpdatePreferencesRequestRequestTypeDef",
    {
        "memberAccountDiscountVisibility": NotRequired[MemberAccountDiscountVisibilityType],
        "savingsEstimationMode": NotRequired[SavingsEstimationModeType],
    },
)
EcsServiceConfigurationTypeDef = TypedDict(
    "EcsServiceConfigurationTypeDef",
    {
        "compute": NotRequired[ComputeConfigurationTypeDef],
    },
)
LambdaFunctionConfigurationTypeDef = TypedDict(
    "LambdaFunctionConfigurationTypeDef",
    {
        "compute": NotRequired[ComputeConfigurationTypeDef],
    },
)
EbsVolumeConfigurationTypeDef = TypedDict(
    "EbsVolumeConfigurationTypeDef",
    {
        "attachmentState": NotRequired[str],
        "performance": NotRequired[BlockStoragePerformanceConfigurationTypeDef],
        "storage": NotRequired[StorageConfigurationTypeDef],
    },
)
Ec2AutoScalingGroupConfigurationTypeDef = TypedDict(
    "Ec2AutoScalingGroupConfigurationTypeDef",
    {
        "instance": NotRequired[InstanceConfigurationTypeDef],
    },
)
Ec2InstanceConfigurationTypeDef = TypedDict(
    "Ec2InstanceConfigurationTypeDef",
    {
        "instance": NotRequired[InstanceConfigurationTypeDef],
    },
)
ResourcePricingTypeDef = TypedDict(
    "ResourcePricingTypeDef",
    {
        "estimatedCostAfterDiscounts": NotRequired[float],
        "estimatedCostBeforeDiscounts": NotRequired[float],
        "estimatedDiscounts": NotRequired[EstimatedDiscountsTypeDef],
        "estimatedNetUnusedAmortizedCommitments": NotRequired[float],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "accountIds": NotRequired[Sequence[str]],
        "actionTypes": NotRequired[Sequence[ActionTypeType]],
        "implementationEfforts": NotRequired[Sequence[ImplementationEffortType]],
        "recommendationIds": NotRequired[Sequence[str]],
        "regions": NotRequired[Sequence[str]],
        "resourceArns": NotRequired[Sequence[str]],
        "resourceIds": NotRequired[Sequence[str]],
        "resourceTypes": NotRequired[Sequence[ResourceTypeType]],
        "restartNeeded": NotRequired[bool],
        "rollbackPossible": NotRequired[bool],
        "tags": NotRequired[Sequence[TagTypeDef]],
    },
)
RecommendationTypeDef = TypedDict(
    "RecommendationTypeDef",
    {
        "accountId": NotRequired[str],
        "actionType": NotRequired[str],
        "currencyCode": NotRequired[str],
        "currentResourceSummary": NotRequired[str],
        "currentResourceType": NotRequired[str],
        "estimatedMonthlyCost": NotRequired[float],
        "estimatedMonthlySavings": NotRequired[float],
        "estimatedSavingsPercentage": NotRequired[float],
        "implementationEffort": NotRequired[str],
        "lastRefreshTimestamp": NotRequired[datetime],
        "recommendationId": NotRequired[str],
        "recommendationLookbackPeriodInDays": NotRequired[int],
        "recommendedResourceSummary": NotRequired[str],
        "recommendedResourceType": NotRequired[str],
        "region": NotRequired[str],
        "resourceArn": NotRequired[str],
        "resourceId": NotRequired[str],
        "restartNeeded": NotRequired[bool],
        "rollbackPossible": NotRequired[bool],
        "source": NotRequired[SourceType],
        "tags": NotRequired[List[TagTypeDef]],
    },
)
GetPreferencesResponseTypeDef = TypedDict(
    "GetPreferencesResponseTypeDef",
    {
        "memberAccountDiscountVisibility": MemberAccountDiscountVisibilityType,
        "savingsEstimationMode": SavingsEstimationModeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListEnrollmentStatusesResponseTypeDef = TypedDict(
    "ListEnrollmentStatusesResponseTypeDef",
    {
        "includeMemberAccounts": bool,
        "items": List[AccountEnrollmentStatusTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdateEnrollmentStatusResponseTypeDef = TypedDict(
    "UpdateEnrollmentStatusResponseTypeDef",
    {
        "status": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
UpdatePreferencesResponseTypeDef = TypedDict(
    "UpdatePreferencesResponseTypeDef",
    {
        "memberAccountDiscountVisibility": MemberAccountDiscountVisibilityType,
        "savingsEstimationMode": SavingsEstimationModeType,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ListEnrollmentStatusesRequestListEnrollmentStatusesPaginateTypeDef = TypedDict(
    "ListEnrollmentStatusesRequestListEnrollmentStatusesPaginateTypeDef",
    {
        "accountId": NotRequired[str],
        "includeOrganizationInfo": NotRequired[bool],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRecommendationSummariesResponseTypeDef = TypedDict(
    "ListRecommendationSummariesResponseTypeDef",
    {
        "currencyCode": str,
        "estimatedTotalDedupedSavings": float,
        "groupBy": str,
        "items": List[RecommendationSummaryTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
ReservedInstancesCostCalculationTypeDef = TypedDict(
    "ReservedInstancesCostCalculationTypeDef",
    {
        "pricing": NotRequired[ReservedInstancesPricingTypeDef],
    },
)
SavingsPlansCostCalculationTypeDef = TypedDict(
    "SavingsPlansCostCalculationTypeDef",
    {
        "pricing": NotRequired[SavingsPlansPricingTypeDef],
    },
)
ResourceCostCalculationTypeDef = TypedDict(
    "ResourceCostCalculationTypeDef",
    {
        "pricing": NotRequired[ResourcePricingTypeDef],
        "usages": NotRequired[List[UsageTypeDef]],
    },
)
ListRecommendationSummariesRequestListRecommendationSummariesPaginateTypeDef = TypedDict(
    "ListRecommendationSummariesRequestListRecommendationSummariesPaginateTypeDef",
    {
        "groupBy": str,
        "filter": NotRequired[FilterTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRecommendationSummariesRequestRequestTypeDef = TypedDict(
    "ListRecommendationSummariesRequestRequestTypeDef",
    {
        "groupBy": str,
        "filter": NotRequired[FilterTypeDef],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
    },
)
ListRecommendationsRequestListRecommendationsPaginateTypeDef = TypedDict(
    "ListRecommendationsRequestListRecommendationsPaginateTypeDef",
    {
        "filter": NotRequired[FilterTypeDef],
        "includeAllRecommendations": NotRequired[bool],
        "orderBy": NotRequired[OrderByTypeDef],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListRecommendationsRequestRequestTypeDef = TypedDict(
    "ListRecommendationsRequestRequestTypeDef",
    {
        "filter": NotRequired[FilterTypeDef],
        "includeAllRecommendations": NotRequired[bool],
        "maxResults": NotRequired[int],
        "nextToken": NotRequired[str],
        "orderBy": NotRequired[OrderByTypeDef],
    },
)
ListRecommendationsResponseTypeDef = TypedDict(
    "ListRecommendationsResponseTypeDef",
    {
        "items": List[RecommendationTypeDef],
        "nextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
Ec2ReservedInstancesTypeDef = TypedDict(
    "Ec2ReservedInstancesTypeDef",
    {
        "configuration": NotRequired[Ec2ReservedInstancesConfigurationTypeDef],
        "costCalculation": NotRequired[ReservedInstancesCostCalculationTypeDef],
    },
)
ElastiCacheReservedInstancesTypeDef = TypedDict(
    "ElastiCacheReservedInstancesTypeDef",
    {
        "configuration": NotRequired[ElastiCacheReservedInstancesConfigurationTypeDef],
        "costCalculation": NotRequired[ReservedInstancesCostCalculationTypeDef],
    },
)
OpenSearchReservedInstancesTypeDef = TypedDict(
    "OpenSearchReservedInstancesTypeDef",
    {
        "configuration": NotRequired[OpenSearchReservedInstancesConfigurationTypeDef],
        "costCalculation": NotRequired[ReservedInstancesCostCalculationTypeDef],
    },
)
RdsReservedInstancesTypeDef = TypedDict(
    "RdsReservedInstancesTypeDef",
    {
        "configuration": NotRequired[RdsReservedInstancesConfigurationTypeDef],
        "costCalculation": NotRequired[ReservedInstancesCostCalculationTypeDef],
    },
)
RedshiftReservedInstancesTypeDef = TypedDict(
    "RedshiftReservedInstancesTypeDef",
    {
        "configuration": NotRequired[RedshiftReservedInstancesConfigurationTypeDef],
        "costCalculation": NotRequired[ReservedInstancesCostCalculationTypeDef],
    },
)
ComputeSavingsPlansTypeDef = TypedDict(
    "ComputeSavingsPlansTypeDef",
    {
        "configuration": NotRequired[ComputeSavingsPlansConfigurationTypeDef],
        "costCalculation": NotRequired[SavingsPlansCostCalculationTypeDef],
    },
)
Ec2InstanceSavingsPlansTypeDef = TypedDict(
    "Ec2InstanceSavingsPlansTypeDef",
    {
        "configuration": NotRequired[Ec2InstanceSavingsPlansConfigurationTypeDef],
        "costCalculation": NotRequired[SavingsPlansCostCalculationTypeDef],
    },
)
SageMakerSavingsPlansTypeDef = TypedDict(
    "SageMakerSavingsPlansTypeDef",
    {
        "configuration": NotRequired[SageMakerSavingsPlansConfigurationTypeDef],
        "costCalculation": NotRequired[SavingsPlansCostCalculationTypeDef],
    },
)
EbsVolumeTypeDef = TypedDict(
    "EbsVolumeTypeDef",
    {
        "configuration": NotRequired[EbsVolumeConfigurationTypeDef],
        "costCalculation": NotRequired[ResourceCostCalculationTypeDef],
    },
)
Ec2AutoScalingGroupTypeDef = TypedDict(
    "Ec2AutoScalingGroupTypeDef",
    {
        "configuration": NotRequired[Ec2AutoScalingGroupConfigurationTypeDef],
        "costCalculation": NotRequired[ResourceCostCalculationTypeDef],
    },
)
Ec2InstanceTypeDef = TypedDict(
    "Ec2InstanceTypeDef",
    {
        "configuration": NotRequired[Ec2InstanceConfigurationTypeDef],
        "costCalculation": NotRequired[ResourceCostCalculationTypeDef],
    },
)
EcsServiceTypeDef = TypedDict(
    "EcsServiceTypeDef",
    {
        "configuration": NotRequired[EcsServiceConfigurationTypeDef],
        "costCalculation": NotRequired[ResourceCostCalculationTypeDef],
    },
)
LambdaFunctionTypeDef = TypedDict(
    "LambdaFunctionTypeDef",
    {
        "configuration": NotRequired[LambdaFunctionConfigurationTypeDef],
        "costCalculation": NotRequired[ResourceCostCalculationTypeDef],
    },
)
ResourceDetailsTypeDef = TypedDict(
    "ResourceDetailsTypeDef",
    {
        "computeSavingsPlans": NotRequired[ComputeSavingsPlansTypeDef],
        "ebsVolume": NotRequired[EbsVolumeTypeDef],
        "ec2AutoScalingGroup": NotRequired[Ec2AutoScalingGroupTypeDef],
        "ec2Instance": NotRequired[Ec2InstanceTypeDef],
        "ec2InstanceSavingsPlans": NotRequired[Ec2InstanceSavingsPlansTypeDef],
        "ec2ReservedInstances": NotRequired[Ec2ReservedInstancesTypeDef],
        "ecsService": NotRequired[EcsServiceTypeDef],
        "elastiCacheReservedInstances": NotRequired[ElastiCacheReservedInstancesTypeDef],
        "lambdaFunction": NotRequired[LambdaFunctionTypeDef],
        "openSearchReservedInstances": NotRequired[OpenSearchReservedInstancesTypeDef],
        "rdsReservedInstances": NotRequired[RdsReservedInstancesTypeDef],
        "redshiftReservedInstances": NotRequired[RedshiftReservedInstancesTypeDef],
        "sageMakerSavingsPlans": NotRequired[SageMakerSavingsPlansTypeDef],
    },
)
GetRecommendationResponseTypeDef = TypedDict(
    "GetRecommendationResponseTypeDef",
    {
        "accountId": str,
        "actionType": ActionTypeType,
        "costCalculationLookbackPeriodInDays": int,
        "currencyCode": str,
        "currentResourceDetails": ResourceDetailsTypeDef,
        "currentResourceType": ResourceTypeType,
        "estimatedMonthlyCost": float,
        "estimatedMonthlySavings": float,
        "estimatedSavingsOverCostCalculationLookbackPeriod": float,
        "estimatedSavingsPercentage": float,
        "implementationEffort": ImplementationEffortType,
        "lastRefreshTimestamp": datetime,
        "recommendationId": str,
        "recommendationLookbackPeriodInDays": int,
        "recommendedResourceDetails": ResourceDetailsTypeDef,
        "recommendedResourceType": ResourceTypeType,
        "region": str,
        "resourceArn": str,
        "resourceId": str,
        "restartNeeded": bool,
        "rollbackPossible": bool,
        "source": SourceType,
        "tags": List[TagTypeDef],
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
