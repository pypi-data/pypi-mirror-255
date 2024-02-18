"""
Type annotations for amp service client paginators.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_amp.client import PrometheusServiceClient
    from mypy_boto3_amp.paginator import (
        ListRuleGroupsNamespacesPaginator,
        ListScrapersPaginator,
        ListWorkspacesPaginator,
    )

    session = Session()
    client: PrometheusServiceClient = session.client("amp")

    list_rule_groups_namespaces_paginator: ListRuleGroupsNamespacesPaginator = client.get_paginator("list_rule_groups_namespaces")
    list_scrapers_paginator: ListScrapersPaginator = client.get_paginator("list_scrapers")
    list_workspaces_paginator: ListWorkspacesPaginator = client.get_paginator("list_workspaces")
    ```
"""

from typing import Generic, Iterator, Mapping, Sequence, TypeVar

from botocore.paginate import PageIterator, Paginator

from .type_defs import (
    ListRuleGroupsNamespacesResponseTypeDef,
    ListScrapersResponsePaginatorTypeDef,
    ListWorkspacesResponseTypeDef,
    PaginatorConfigTypeDef,
)

__all__ = ("ListRuleGroupsNamespacesPaginator", "ListScrapersPaginator", "ListWorkspacesPaginator")

_ItemTypeDef = TypeVar("_ItemTypeDef")

class _PageIterator(Generic[_ItemTypeDef], PageIterator):
    def __iter__(self) -> Iterator[_ItemTypeDef]:
        """
        Proxy method to specify iterator item type.
        """

class ListRuleGroupsNamespacesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Paginator.ListRuleGroupsNamespaces)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/#listrulegroupsnamespacespaginator)
    """

    def paginate(
        self, *, workspaceId: str, name: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListRuleGroupsNamespacesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Paginator.ListRuleGroupsNamespaces.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/#listrulegroupsnamespacespaginator)
        """

class ListScrapersPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Paginator.ListScrapers)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/#listscraperspaginator)
    """

    def paginate(
        self,
        *,
        filters: Mapping[str, Sequence[str]] = ...,
        PaginationConfig: PaginatorConfigTypeDef = ...,
    ) -> _PageIterator[ListScrapersResponsePaginatorTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Paginator.ListScrapers.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/#listscraperspaginator)
        """

class ListWorkspacesPaginator(Paginator):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Paginator.ListWorkspaces)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/#listworkspacespaginator)
    """

    def paginate(
        self, *, alias: str = ..., PaginationConfig: PaginatorConfigTypeDef = ...
    ) -> _PageIterator[ListWorkspacesResponseTypeDef]:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Paginator.ListWorkspaces.paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/paginators/#listworkspacespaginator)
        """
