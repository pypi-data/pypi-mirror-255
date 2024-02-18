"""
Type annotations for redshift service client waiters.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/)

Usage::

    ```python
    from boto3.session import Session

    from mypy_boto3_redshift.client import RedshiftClient
    from mypy_boto3_redshift.waiter import (
        ClusterAvailableWaiter,
        ClusterDeletedWaiter,
        ClusterRestoredWaiter,
        SnapshotAvailableWaiter,
    )

    session = Session()
    client: RedshiftClient = session.client("redshift")

    cluster_available_waiter: ClusterAvailableWaiter = client.get_waiter("cluster_available")
    cluster_deleted_waiter: ClusterDeletedWaiter = client.get_waiter("cluster_deleted")
    cluster_restored_waiter: ClusterRestoredWaiter = client.get_waiter("cluster_restored")
    snapshot_available_waiter: SnapshotAvailableWaiter = client.get_waiter("snapshot_available")
    ```
"""

from typing import Sequence

from botocore.waiter import Waiter

from .type_defs import SnapshotSortingEntityTypeDef, TimestampTypeDef, WaiterConfigTypeDef

__all__ = (
    "ClusterAvailableWaiter",
    "ClusterDeletedWaiter",
    "ClusterRestoredWaiter",
    "SnapshotAvailableWaiter",
)

class ClusterAvailableWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.ClusterAvailable)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#clusteravailablewaiter)
    """

    def wait(
        self,
        *,
        ClusterIdentifier: str = ...,
        MaxRecords: int = ...,
        Marker: str = ...,
        TagKeys: Sequence[str] = ...,
        TagValues: Sequence[str] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.ClusterAvailable.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#clusteravailablewaiter)
        """

class ClusterDeletedWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.ClusterDeleted)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#clusterdeletedwaiter)
    """

    def wait(
        self,
        *,
        ClusterIdentifier: str = ...,
        MaxRecords: int = ...,
        Marker: str = ...,
        TagKeys: Sequence[str] = ...,
        TagValues: Sequence[str] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.ClusterDeleted.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#clusterdeletedwaiter)
        """

class ClusterRestoredWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.ClusterRestored)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#clusterrestoredwaiter)
    """

    def wait(
        self,
        *,
        ClusterIdentifier: str = ...,
        MaxRecords: int = ...,
        Marker: str = ...,
        TagKeys: Sequence[str] = ...,
        TagValues: Sequence[str] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.ClusterRestored.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#clusterrestoredwaiter)
        """

class SnapshotAvailableWaiter(Waiter):
    """
    [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.SnapshotAvailable)
    [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#snapshotavailablewaiter)
    """

    def wait(
        self,
        *,
        ClusterIdentifier: str = ...,
        SnapshotIdentifier: str = ...,
        SnapshotArn: str = ...,
        SnapshotType: str = ...,
        StartTime: TimestampTypeDef = ...,
        EndTime: TimestampTypeDef = ...,
        MaxRecords: int = ...,
        Marker: str = ...,
        OwnerAccount: str = ...,
        TagKeys: Sequence[str] = ...,
        TagValues: Sequence[str] = ...,
        ClusterExists: bool = ...,
        SortingEntities: Sequence[SnapshotSortingEntityTypeDef] = ...,
        WaiterConfig: WaiterConfigTypeDef = ...,
    ) -> None:
        """
        [Show boto3 documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html#Redshift.Waiter.SnapshotAvailable.wait)
        [Show boto3-stubs documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_redshift/waiters/#snapshotavailablewaiter)
        """
