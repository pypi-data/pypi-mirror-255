"""
Type annotations for cost-optimization-hub service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_cost_optimization_hub.client import CostOptimizationHubClient
    from mypy_boto3_cost_optimization_hub.paginator import (
        ListEnrollmentStatusesPaginator,
        ListRecommendationSummariesPaginator,
        ListRecommendationsPaginator,
    )

    session = Session()
    client: CostOptimizationHubClient = session.client("cost-optimization-hub")

    list_enrollment_statuses_paginator: ListEnrollmentStatusesPaginator = client.get_paginator("list_enrollment_statuses")
    list_recommendation_summaries_paginator: ListRecommendationSummariesPaginator = client.get_paginator("list_recommendation_summaries")
    list_recommendations_paginator: ListRecommendationsPaginator = client.get_paginator("list_recommendations")
    ```
"""

from typing import Generic, Iterator, TypeVar

from botocore.paginate import PageIterator, Paginator

from .type_defs import (
    FilterTypeDef,
    ListEnrollmentStatusesResponseTypeDef,
    ListRecommendationsResponseTypeDef,
    ListRecommendationSummariesResponseTypeDef,
    OrderByTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = (
    "ListEnrollmentStatusesPaginator",
    "ListRecommendationSummariesPaginator",
    "ListRecommendationsPaginator",
)

_ItemTypeDef = TypeVar("_ItemTypeDef")


class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """


class ListEnrollmentStatusesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListEnrollmentStatuses)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/#listenrollmentstatusespaginator)
    """

    def paginate(
        self,
        *,
        accountId: str = ...,
        includeOrganizationInfo: bool = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListEnrollmentStatusesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListEnrollmentStatuses.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/#listenrollmentstatusespaginator)
        """


class ListRecommendationSummariesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendationSummaries)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/#listrecommendationsummariespaginator)
    """

    def paginate(
        self,
        *,
        groupBy: str,
        filter: FilterTypeDef = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListRecommendationSummariesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendationSummaries.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/#listrecommendationsummariespaginator)
        """


class ListRecommendationsPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendations)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/#listrecommendationspaginator)
    """

    def paginate(
        self,
        *,
        filter: FilterTypeDef = ...,
        includeAllRecommendations: bool = ...,
        orderBy: OrderByTypeDef = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListRecommendationsResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cost-optimization-hub.html#CostOptimizationHub.Paginator.ListRecommendations.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_cost_optimization_hub/paginators/#listrecommendationspaginator)
        """
