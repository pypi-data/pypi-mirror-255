# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetNodeGroupsResult',
    'AwaitableGetNodeGroupsResult',
    'get_node_groups',
    'get_node_groups_output',
]

@pulumi.output_type
class GetNodeGroupsResult:
    """
    A collection of values returned by getNodeGroups.
    """
    def __init__(__self__, cluster_name=None, id=None, names=None):
        if cluster_name and not isinstance(cluster_name, str):
            raise TypeError("Expected argument 'cluster_name' to be a str")
        pulumi.set(__self__, "cluster_name", cluster_name)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if names and not isinstance(names, list):
            raise TypeError("Expected argument 'names' to be a list")
        pulumi.set(__self__, "names", names)

    @property
    @pulumi.getter(name="clusterName")
    def cluster_name(self) -> str:
        return pulumi.get(self, "cluster_name")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def names(self) -> Sequence[str]:
        """
        Set of all node group names in an EKS Cluster.
        """
        return pulumi.get(self, "names")


class AwaitableGetNodeGroupsResult(GetNodeGroupsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetNodeGroupsResult(
            cluster_name=self.cluster_name,
            id=self.id,
            names=self.names)


def get_node_groups(cluster_name: Optional[str] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetNodeGroupsResult:
    """
    Retrieve the EKS Node Groups associated with a named EKS cluster. This will allow you to pass a list of Node Group names to other resources.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example_node_groups = aws.eks.get_node_groups(cluster_name="example")
    example_node_group = [aws.eks.get_node_group(cluster_name="example",
        node_group_name=__value) for __key, __value in example_node_groups.names]
    ```


    :param str cluster_name: Name of the cluster.
    """
    __args__ = dict()
    __args__['clusterName'] = cluster_name
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:eks/getNodeGroups:getNodeGroups', __args__, opts=opts, typ=GetNodeGroupsResult).value

    return AwaitableGetNodeGroupsResult(
        cluster_name=pulumi.get(__ret__, 'cluster_name'),
        id=pulumi.get(__ret__, 'id'),
        names=pulumi.get(__ret__, 'names'))


@_utilities.lift_output_func(get_node_groups)
def get_node_groups_output(cluster_name: Optional[pulumi.Input[str]] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetNodeGroupsResult]:
    """
    Retrieve the EKS Node Groups associated with a named EKS cluster. This will allow you to pass a list of Node Group names to other resources.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example_node_groups = aws.eks.get_node_groups(cluster_name="example")
    example_node_group = [aws.eks.get_node_group(cluster_name="example",
        node_group_name=__value) for __key, __value in example_node_groups.names]
    ```


    :param str cluster_name: Name of the cluster.
    """
    ...
