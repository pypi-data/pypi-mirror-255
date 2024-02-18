"""
Type annotations for cost-optimization-hub service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_cost_optimization_hub.client import CostOptimizationHubClient

    session = Session()
    client: CostOptimizationHubClient = session.client("cost-optimization-hub")
    ```
"""

import sys
from typing import Any, Dict, Mapping, Type, overload

from botocore.client import BaseClient, ClientMeta

from .literals import (
    EnrollmentStatusType,
    MemberAccountDiscountVisibilityType,
    SavingsEstimationModeType,
)
from .paginator import (
    ListEnrollmentStatusesPaginator,
    ListRecommendationsPaginator,
    ListRecommendationSummariesPaginator,
)
from .type_defs import (
    FilterTypeDef,
    GetPreferencesResponseTypeDef,
    GetRecommendationResponseTypeDef,
    ListEnrollmentStatusesResponseTypeDef,
    ListRecommendationsResponseTypeDef,
    ListRecommendationSummariesResponseTypeDef,
    OrderByTypeDef,
    UpdateEnrollmentStatusResponseTypeDef,
    UpdatePreferencesResponseTypeDef,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("CostOptimizationHubClient",)

class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str

class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]

class CostOptimizationHubClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        CostOptimizationHubClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#can_paginate)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#close)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#generate_presigned_url)
        """

    def get_preferences(self) -> GetPreferencesResponseTypeDef:
        """
        Returns a set of preferences for an account in order to add account-specific
        preferences into the
        service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.get_preferences)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#get_preferences)
        """

    def get_recommendation(self, *, recommendationId: str) -> GetRecommendationResponseTypeDef:
        """
        Returns both the current and recommended resource configuration and the
        estimated cost impact for a
        recommendation.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.get_recommendation)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#get_recommendation)
        """

    def list_enrollment_statuses(
        self,
        *,
        accountId: str = ...,
        includeOrganizationInfo: bool = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListEnrollmentStatusesResponseTypeDef:
        """
        Retrieves the enrollment status for an account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.list_enrollment_statuses)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#list_enrollment_statuses)
        """

    def list_recommendation_summaries(
        self,
        *,
        groupBy: str,
        filter: FilterTypeDef = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListRecommendationSummariesResponseTypeDef:
        """
        Returns a concise representation of savings estimates for resources.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.list_recommendation_summaries)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#list_recommendation_summaries)
        """

    def list_recommendations(
        self,
        *,
        filter: FilterTypeDef = ...,
        includeAllRecommendations: bool = ...,
        maxResults: int = ...,
        nextToken: str = ...,
        orderBy: OrderByTypeDef = ...,
    ) -> ListRecommendationsResponseTypeDef:
        """
        Returns a list of recommendations.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.list_recommendations)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#list_recommendations)
        """

    def update_enrollment_status(
        self, *, status: EnrollmentStatusType, includeMemberAccounts: bool = ...
    ) -> UpdateEnrollmentStatusResponseTypeDef:
        """
        Updates the enrollment (opt in and opt out) status of an account to the Cost
        Optimization Hub
        service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.update_enrollment_status)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#update_enrollment_status)
        """

    def update_preferences(
        self,
        *,
        memberAccountDiscountVisibility: MemberAccountDiscountVisibilityType = ...,
        savingsEstimationMode: SavingsEstimationModeType = ...,
    ) -> UpdatePreferencesResponseTypeDef:
        """
        Updates a set of preferences for an account in order to add account-specific
        preferences into the
        service.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.update_preferences)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#update_preferences)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_enrollment_statuses"]
    ) -> ListEnrollmentStatusesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_recommendation_summaries"]
    ) -> ListRecommendationSummariesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#get_paginator)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_recommendations"]
    ) -> ListRecommendationsPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/client/#get_paginator)
        """
