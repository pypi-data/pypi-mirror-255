"""
Type annotations for amp service client waiters.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_amp.client import PrometheusServiceClient
    from mypy_boto3_amp.waiter import (
        ScraperActiveWaiter,
        ScraperDeletedWaiter,
        WorkspaceActiveWaiter,
        WorkspaceDeletedWaiter,
    )

    session = Session()
    client: PrometheusServiceClient = session.client("amp")

    scraper_active_waiter: ScraperActiveWaiter = client.get_waiter("scraper_active")
    scraper_deleted_waiter: ScraperDeletedWaiter = client.get_waiter("scraper_deleted")
    workspace_active_waiter: WorkspaceActiveWaiter = client.get_waiter("workspace_active")
    workspace_deleted_waiter: WorkspaceDeletedWaiter = client.get_waiter("workspace_deleted")
    ```
"""

from botocore.waiter import Waiter

from .type_defs import WaiterConfigTypeDef

__all__ = (
    "ScraperActiveWaiter",
    "ScraperDeletedWaiter",
    "WorkspaceActiveWaiter",
    "WorkspaceDeletedWaiter",
)

class ScraperActiveWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.ScraperActive)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#scraperactivewaiter)
    """

    def wait(self, *, scraperId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.ScraperActive.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#scraperactivewaiter)
        """

class ScraperDeletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.ScraperDeleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#scraperdeletedwaiter)
    """

    def wait(self, *, scraperId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.ScraperDeleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#scraperdeletedwaiter)
        """

class WorkspaceActiveWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.WorkspaceActive)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#workspaceactivewaiter)
    """

    def wait(self, *, workspaceId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.WorkspaceActive.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#workspaceactivewaiter)
        """

class WorkspaceDeletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.WorkspaceDeleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#workspacedeletedwaiter)
    """

    def wait(self, *, workspaceId: str, WaiterConfig: WaiterConfigTypeDef = ...) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/amp.html#PrometheusService.Waiter.WorkspaceDeleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_amp/waiters/#workspacedeletedwaiter)
        """
