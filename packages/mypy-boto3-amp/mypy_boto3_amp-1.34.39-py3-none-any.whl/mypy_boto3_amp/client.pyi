"""
Type annotations for amp service client.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/)

Usage::

    ```python
    from boto3.session import Session
    from mypy_boto3_amp.client import PrometheusServiceClient

    session = Session()
    client: PrometheusServiceClient = session.client("amp")
    ```
"""

import sys
from typing import Any, Dict, Mapping, Sequence, Type, overload

from botocore.client import BaseClient, ClientMeta

from .paginator import (
    ListRuleGroupsNamespacesPaginator,
    ListScrapersPaginator,
    ListWorkspacesPaginator,
)
from .type_defs import (
    BlobTypeDef,
    CreateAlertManagerDefinitionResponseTypeDef,
    CreateLoggingConfigurationResponseTypeDef,
    CreateRuleGroupsNamespaceResponseTypeDef,
    CreateScraperResponseTypeDef,
    CreateWorkspaceResponseTypeDef,
    DeleteScraperResponseTypeDef,
    DescribeAlertManagerDefinitionResponseTypeDef,
    DescribeLoggingConfigurationResponseTypeDef,
    DescribeRuleGroupsNamespaceResponseTypeDef,
    DescribeScraperResponseTypeDef,
    DescribeWorkspaceResponseTypeDef,
    DestinationTypeDef,
    EmptyResponseMetadataTypeDef,
    GetDefaultScraperConfigurationResponseTypeDef,
    ListRuleGroupsNamespacesResponseTypeDef,
    ListScrapersResponseTypeDef,
    ListTagsForResourceResponseTypeDef,
    ListWorkspacesResponseTypeDef,
    PutAlertManagerDefinitionResponseTypeDef,
    PutRuleGroupsNamespaceResponseTypeDef,
    ScrapeConfigurationTypeDef,
    SourceTypeDef,
    UpdateLoggingConfigurationResponseTypeDef,
)
from .waiter import (
    ScraperActiveWaiter,
    ScraperDeletedWaiter,
    WorkspaceActiveWaiter,
    WorkspaceDeletedWaiter,
)

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal

__all__ = ("PrometheusServiceClient",)

class BotocoreClientError(Exception):
    MSG_TEMPLATE: str

    def __init__(self, error_response: Mapping[str, Any], operation_name: str) -> None:
        self.response: Dict[str, Any]
        self.operation_name: str

class Exceptions:
    AccessDeniedException: Type[BotocoreClientError]
    ClientError: Type[BotocoreClientError]
    ConflictException: Type[BotocoreClientError]
    InternalServerException: Type[BotocoreClientError]
    ResourceNotFoundException: Type[BotocoreClientError]
    ServiceQuotaExceededException: Type[BotocoreClientError]
    ThrottlingException: Type[BotocoreClientError]
    ValidationException: Type[BotocoreClientError]

class PrometheusServiceClient(BaseClient):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/)
    """

    meta: ClientMeta

    @property
    def exceptions(self) -> Exceptions:
        """
        PrometheusServiceClient exceptions.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.exceptions)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#exceptions)
        """

    def can_paginate(self, operation_name: str) -> bool:
        """
        Check if an operation can be paginated.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.can_paginate)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#can_paginate)
        """

    def close(self) -> None:
        """
        Closes underlying endpoint connections.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.close)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#close)
        """

    def create_alert_manager_definition(
        self, *, data: BlobTypeDef, workspaceId: str, clientToken: str = ...
    ) -> CreateAlertManagerDefinitionResponseTypeDef:
        """
        The `CreateAlertManagerDefinition` operation creates the alert manager
        definition in a
        workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.create_alert_manager_definition)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#create_alert_manager_definition)
        """

    def create_logging_configuration(
        self, *, logGroupArn: str, workspaceId: str, clientToken: str = ...
    ) -> CreateLoggingConfigurationResponseTypeDef:
        """
        The `CreateLoggingConfiguration` operation creates a logging configuration for
        the
        workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.create_logging_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#create_logging_configuration)
        """

    def create_rule_groups_namespace(
        self,
        *,
        data: BlobTypeDef,
        name: str,
        workspaceId: str,
        clientToken: str = ...,
        tags: Mapping[str, str] = ...,
    ) -> CreateRuleGroupsNamespaceResponseTypeDef:
        """
        The `CreateRuleGroupsNamespace` operation creates a rule groups namespace
        within a
        workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.create_rule_groups_namespace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#create_rule_groups_namespace)
        """

    def create_scraper(
        self,
        *,
        destination: DestinationTypeDef,
        scrapeConfiguration: ScrapeConfigurationTypeDef,
        source: SourceTypeDef,
        alias: str = ...,
        clientToken: str = ...,
        tags: Mapping[str, str] = ...,
    ) -> CreateScraperResponseTypeDef:
        """
        The `CreateScraper` operation creates a scraper to collect metrics.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.create_scraper)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#create_scraper)
        """

    def create_workspace(
        self,
        *,
        alias: str = ...,
        clientToken: str = ...,
        kmsKeyArn: str = ...,
        tags: Mapping[str, str] = ...,
    ) -> CreateWorkspaceResponseTypeDef:
        """
        Creates a Prometheus workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.create_workspace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#create_workspace)
        """

    def delete_alert_manager_definition(
        self, *, workspaceId: str, clientToken: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the alert manager definition from a workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.delete_alert_manager_definition)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#delete_alert_manager_definition)
        """

    def delete_logging_configuration(
        self, *, workspaceId: str, clientToken: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes the logging configuration for a workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.delete_logging_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#delete_logging_configuration)
        """

    def delete_rule_groups_namespace(
        self, *, name: str, workspaceId: str, clientToken: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes one rule groups namespace and its associated rule groups definition.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.delete_rule_groups_namespace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#delete_rule_groups_namespace)
        """

    def delete_scraper(
        self, *, scraperId: str, clientToken: str = ...
    ) -> DeleteScraperResponseTypeDef:
        """
        The `DeleteScraper` operation deletes one scraper, and stops any metrics
        collection that the scraper
        performs.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.delete_scraper)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#delete_scraper)
        """

    def delete_workspace(
        self, *, workspaceId: str, clientToken: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Deletes an existing workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.delete_workspace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#delete_workspace)
        """

    def describe_alert_manager_definition(
        self, *, workspaceId: str
    ) -> DescribeAlertManagerDefinitionResponseTypeDef:
        """
        Retrieves the full information about the alert manager definition for a
        workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.describe_alert_manager_definition)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#describe_alert_manager_definition)
        """

    def describe_logging_configuration(
        self, *, workspaceId: str
    ) -> DescribeLoggingConfigurationResponseTypeDef:
        """
        Returns complete information about the current logging configuration of the
        workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.describe_logging_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#describe_logging_configuration)
        """

    def describe_rule_groups_namespace(
        self, *, name: str, workspaceId: str
    ) -> DescribeRuleGroupsNamespaceResponseTypeDef:
        """
        Returns complete information about one rule groups namespace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.describe_rule_groups_namespace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#describe_rule_groups_namespace)
        """

    def describe_scraper(self, *, scraperId: str) -> DescribeScraperResponseTypeDef:
        """
        The `DescribeScraper` operation displays information about an existing scraper.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.describe_scraper)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#describe_scraper)
        """

    def describe_workspace(self, *, workspaceId: str) -> DescribeWorkspaceResponseTypeDef:
        """
        Returns information about an existing workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.describe_workspace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#describe_workspace)
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

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.generate_presigned_url)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#generate_presigned_url)
        """

    def get_default_scraper_configuration(self) -> GetDefaultScraperConfigurationResponseTypeDef:
        """
        The `GetDefaultScraperConfiguration` operation returns the default scraper
        configuration used when Amazon EKS creates a scraper for
        you.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_default_scraper_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_default_scraper_configuration)
        """

    def list_rule_groups_namespaces(
        self, *, workspaceId: str, maxResults: int = ..., name: str = ..., nextToken: str = ...
    ) -> ListRuleGroupsNamespacesResponseTypeDef:
        """
        Returns a list of rule groups namespaces in a workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.list_rule_groups_namespaces)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#list_rule_groups_namespaces)
        """

    def list_scrapers(
        self,
        *,
        filters: Mapping[str, Sequence[str]] = ...,
        maxResults: int = ...,
        nextToken: str = ...,
    ) -> ListScrapersResponseTypeDef:
        """
        The `ListScrapers` operation lists all of the scrapers in your account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.list_scrapers)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#list_scrapers)
        """

    def list_tags_for_resource(self, *, resourceArn: str) -> ListTagsForResourceResponseTypeDef:
        """
        The `ListTagsForResource` operation returns the tags that are associated with
        an Amazon Managed Service for Prometheus
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.list_tags_for_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#list_tags_for_resource)
        """

    def list_workspaces(
        self, *, alias: str = ..., maxResults: int = ..., nextToken: str = ...
    ) -> ListWorkspacesResponseTypeDef:
        """
        Lists all of the Amazon Managed Service for Prometheus workspaces in your
        account.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.list_workspaces)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#list_workspaces)
        """

    def put_alert_manager_definition(
        self, *, data: BlobTypeDef, workspaceId: str, clientToken: str = ...
    ) -> PutAlertManagerDefinitionResponseTypeDef:
        """
        Updates an existing alert manager definition in a workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.put_alert_manager_definition)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#put_alert_manager_definition)
        """

    def put_rule_groups_namespace(
        self, *, data: BlobTypeDef, name: str, workspaceId: str, clientToken: str = ...
    ) -> PutRuleGroupsNamespaceResponseTypeDef:
        """
        Updates an existing rule groups namespace within a workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.put_rule_groups_namespace)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#put_rule_groups_namespace)
        """

    def tag_resource(self, *, resourceArn: str, tags: Mapping[str, str]) -> Dict[str, Any]:
        """
        The `TagResource` operation associates tags with an Amazon Managed Service for
        Prometheus
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.tag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#tag_resource)
        """

    def untag_resource(self, *, resourceArn: str, tagKeys: Sequence[str]) -> Dict[str, Any]:
        """
        Removes the specified tags from an Amazon Managed Service for Prometheus
        resource.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.untag_resource)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#untag_resource)
        """

    def update_logging_configuration(
        self, *, logGroupArn: str, workspaceId: str, clientToken: str = ...
    ) -> UpdateLoggingConfigurationResponseTypeDef:
        """
        Updates the log group ARN or the workspace ID of the current logging
        configuration.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.update_logging_configuration)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#update_logging_configuration)
        """

    def update_workspace_alias(
        self, *, workspaceId: str, alias: str = ..., clientToken: str = ...
    ) -> EmptyResponseMetadataTypeDef:
        """
        Updates the alias of an existing workspace.

        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.update_workspace_alias)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#update_workspace_alias)
        """

    @overload
    def get_paginator(
        self, operation_name: Literal["list_rule_groups_namespaces"]
    ) -> ListRuleGroupsNamespacesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_scrapers"]) -> ListScrapersPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_paginator)
        """

    @overload
    def get_paginator(self, operation_name: Literal["list_workspaces"]) -> ListWorkspacesPaginator:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_paginator)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_paginator)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["scraper_active"]) -> ScraperActiveWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_waiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["scraper_deleted"]) -> ScraperDeletedWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_waiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["workspace_active"]) -> WorkspaceActiveWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_waiter)
        """

    @overload
    def get_waiter(self, waiter_name: Literal["workspace_deleted"]) -> WorkspaceDeletedWaiter:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Client.get_waiter)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/client/#get_waiter)
        """
