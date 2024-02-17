# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from . import _utilities

__all__ = [
    'GetDefaultTagsResult',
    'AwaitableGetDefaultTagsResult',
    'get_default_tags',
    'get_default_tags_output',
]

@pulumi.output_type
class GetDefaultTagsResult:
    """
    A collection of values returned by getDefaultTags.
    """
    def __init__(__self__, id=None, tags=None):
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def id(self) -> str:
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        Blocks of default tags set on the provider. See details below.
        """
        return pulumi.get(self, "tags")


class AwaitableGetDefaultTagsResult(GetDefaultTagsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetDefaultTagsResult(
            id=self.id,
            tags=self.tags)


def get_default_tags(id: Optional[str] = None,
                     opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetDefaultTagsResult:
    """
    Use this data source to get the default tags configured on the provider.

    With this data source, you can apply default tags to resources not _directly_ managed by a resource, such as the instances underneath an Auto Scaling group or the volumes created for an EC2 instance.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.get_default_tags()
    ```
    """
    __args__ = dict()
    __args__['id'] = id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:index/getDefaultTags:getDefaultTags', __args__, opts=opts, typ=GetDefaultTagsResult).value

    return AwaitableGetDefaultTagsResult(
        id=pulumi.get(__ret__, 'id'),
        tags=pulumi.get(__ret__, 'tags'))


@_utilities.lift_output_func(get_default_tags)
def get_default_tags_output(id: Optional[pulumi.Input[Optional[str]]] = None,
                            opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetDefaultTagsResult]:
    """
    Use this data source to get the default tags configured on the provider.

    With this data source, you can apply default tags to resources not _directly_ managed by a resource, such as the instances underneath an Auto Scaling group or the volumes created for an EC2 instance.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.get_default_tags()
    ```
    """
    ...
