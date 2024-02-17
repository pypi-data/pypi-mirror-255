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
    'GetSelectionResult',
    'AwaitableGetSelectionResult',
    'get_selection',
    'get_selection_output',
]

@pulumi.output_type
class GetSelectionResult:
    """
    A collection of values returned by getSelection.
    """
    def __init__(__self__, iam_role_arn=None, id=None, name=None, plan_id=None, resources=None, selection_id=None):
        if iam_role_arn and not isinstance(iam_role_arn, str):
            raise TypeError("Expected argument 'iam_role_arn' to be a str")
        pulumi.set(__self__, "iam_role_arn", iam_role_arn)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if plan_id and not isinstance(plan_id, str):
            raise TypeError("Expected argument 'plan_id' to be a str")
        pulumi.set(__self__, "plan_id", plan_id)
        if resources and not isinstance(resources, list):
            raise TypeError("Expected argument 'resources' to be a list")
        pulumi.set(__self__, "resources", resources)
        if selection_id and not isinstance(selection_id, str):
            raise TypeError("Expected argument 'selection_id' to be a str")
        pulumi.set(__self__, "selection_id", selection_id)

    @property
    @pulumi.getter(name="iamRoleArn")
    def iam_role_arn(self) -> str:
        """
        ARN of the IAM role that AWS Backup uses to authenticate when restoring and backing up the target resource. See the [AWS Backup Developer Guide](https://docs.aws.amazon.com/aws-backup/latest/devguide/access-control.html#managed-policies) for additional information about using AWS managed policies or creating custom policies attached to the IAM role.
        """
        return pulumi.get(self, "iam_role_arn")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Display name of a resource selection document.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="planId")
    def plan_id(self) -> str:
        return pulumi.get(self, "plan_id")

    @property
    @pulumi.getter
    def resources(self) -> Sequence[str]:
        """
        An array of strings that either contain Amazon Resource Names (ARNs) or match patterns of resources to assign to a backup plan..
        """
        return pulumi.get(self, "resources")

    @property
    @pulumi.getter(name="selectionId")
    def selection_id(self) -> str:
        return pulumi.get(self, "selection_id")


class AwaitableGetSelectionResult(GetSelectionResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetSelectionResult(
            iam_role_arn=self.iam_role_arn,
            id=self.id,
            name=self.name,
            plan_id=self.plan_id,
            resources=self.resources,
            selection_id=self.selection_id)


def get_selection(plan_id: Optional[str] = None,
                  selection_id: Optional[str] = None,
                  opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetSelectionResult:
    """
    Use this data source to get information on an existing backup selection.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.backup.get_selection(plan_id=data["aws_backup_plan"]["example"]["id"],
        selection_id="selection-id-example")
    ```


    :param str plan_id: Backup plan ID associated with the selection of resources.
    :param str selection_id: Backup selection ID.
    """
    __args__ = dict()
    __args__['planId'] = plan_id
    __args__['selectionId'] = selection_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:backup/getSelection:getSelection', __args__, opts=opts, typ=GetSelectionResult).value

    return AwaitableGetSelectionResult(
        iam_role_arn=pulumi.get(__ret__, 'iam_role_arn'),
        id=pulumi.get(__ret__, 'id'),
        name=pulumi.get(__ret__, 'name'),
        plan_id=pulumi.get(__ret__, 'plan_id'),
        resources=pulumi.get(__ret__, 'resources'),
        selection_id=pulumi.get(__ret__, 'selection_id'))


@_utilities.lift_output_func(get_selection)
def get_selection_output(plan_id: Optional[pulumi.Input[str]] = None,
                         selection_id: Optional[pulumi.Input[str]] = None,
                         opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetSelectionResult]:
    """
    Use this data source to get information on an existing backup selection.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.backup.get_selection(plan_id=data["aws_backup_plan"]["example"]["id"],
        selection_id="selection-id-example")
    ```


    :param str plan_id: Backup plan ID associated with the selection of resources.
    :param str selection_id: Backup selection ID.
    """
    ...
