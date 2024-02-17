# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities
from . import outputs

__all__ = [
    'GetWorkspaceResult',
    'AwaitableGetWorkspaceResult',
    'get_workspace',
    'get_workspace_output',
]

@pulumi.output_type
class GetWorkspaceResult:
    """
    A collection of values returned by getWorkspace.
    """
    def __init__(__self__, bundle_id=None, computer_name=None, directory_id=None, id=None, ip_address=None, root_volume_encryption_enabled=None, state=None, tags=None, user_name=None, user_volume_encryption_enabled=None, volume_encryption_key=None, workspace_id=None, workspace_properties=None):
        if bundle_id and not isinstance(bundle_id, str):
            raise TypeError("Expected argument 'bundle_id' to be a str")
        pulumi.set(__self__, "bundle_id", bundle_id)
        if computer_name and not isinstance(computer_name, str):
            raise TypeError("Expected argument 'computer_name' to be a str")
        pulumi.set(__self__, "computer_name", computer_name)
        if directory_id and not isinstance(directory_id, str):
            raise TypeError("Expected argument 'directory_id' to be a str")
        pulumi.set(__self__, "directory_id", directory_id)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if ip_address and not isinstance(ip_address, str):
            raise TypeError("Expected argument 'ip_address' to be a str")
        pulumi.set(__self__, "ip_address", ip_address)
        if root_volume_encryption_enabled and not isinstance(root_volume_encryption_enabled, bool):
            raise TypeError("Expected argument 'root_volume_encryption_enabled' to be a bool")
        pulumi.set(__self__, "root_volume_encryption_enabled", root_volume_encryption_enabled)
        if state and not isinstance(state, str):
            raise TypeError("Expected argument 'state' to be a str")
        pulumi.set(__self__, "state", state)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if user_name and not isinstance(user_name, str):
            raise TypeError("Expected argument 'user_name' to be a str")
        pulumi.set(__self__, "user_name", user_name)
        if user_volume_encryption_enabled and not isinstance(user_volume_encryption_enabled, bool):
            raise TypeError("Expected argument 'user_volume_encryption_enabled' to be a bool")
        pulumi.set(__self__, "user_volume_encryption_enabled", user_volume_encryption_enabled)
        if volume_encryption_key and not isinstance(volume_encryption_key, str):
            raise TypeError("Expected argument 'volume_encryption_key' to be a str")
        pulumi.set(__self__, "volume_encryption_key", volume_encryption_key)
        if workspace_id and not isinstance(workspace_id, str):
            raise TypeError("Expected argument 'workspace_id' to be a str")
        pulumi.set(__self__, "workspace_id", workspace_id)
        if workspace_properties and not isinstance(workspace_properties, list):
            raise TypeError("Expected argument 'workspace_properties' to be a list")
        pulumi.set(__self__, "workspace_properties", workspace_properties)

    @property
    @pulumi.getter(name="bundleId")
    def bundle_id(self) -> str:
        return pulumi.get(self, "bundle_id")

    @property
    @pulumi.getter(name="computerName")
    def computer_name(self) -> str:
        """
        Name of the WorkSpace, as seen by the operating system.
        """
        return pulumi.get(self, "computer_name")

    @property
    @pulumi.getter(name="directoryId")
    def directory_id(self) -> str:
        return pulumi.get(self, "directory_id")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="ipAddress")
    def ip_address(self) -> str:
        """
        IP address of the WorkSpace.
        """
        return pulumi.get(self, "ip_address")

    @property
    @pulumi.getter(name="rootVolumeEncryptionEnabled")
    def root_volume_encryption_enabled(self) -> bool:
        return pulumi.get(self, "root_volume_encryption_enabled")

    @property
    @pulumi.getter
    def state(self) -> str:
        """
        Operational state of the WorkSpace.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> str:
        return pulumi.get(self, "user_name")

    @property
    @pulumi.getter(name="userVolumeEncryptionEnabled")
    def user_volume_encryption_enabled(self) -> bool:
        return pulumi.get(self, "user_volume_encryption_enabled")

    @property
    @pulumi.getter(name="volumeEncryptionKey")
    def volume_encryption_key(self) -> str:
        return pulumi.get(self, "volume_encryption_key")

    @property
    @pulumi.getter(name="workspaceId")
    def workspace_id(self) -> str:
        return pulumi.get(self, "workspace_id")

    @property
    @pulumi.getter(name="workspaceProperties")
    def workspace_properties(self) -> Sequence['outputs.GetWorkspaceWorkspacePropertyResult']:
        return pulumi.get(self, "workspace_properties")


class AwaitableGetWorkspaceResult(GetWorkspaceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetWorkspaceResult(
            bundle_id=self.bundle_id,
            computer_name=self.computer_name,
            directory_id=self.directory_id,
            id=self.id,
            ip_address=self.ip_address,
            root_volume_encryption_enabled=self.root_volume_encryption_enabled,
            state=self.state,
            tags=self.tags,
            user_name=self.user_name,
            user_volume_encryption_enabled=self.user_volume_encryption_enabled,
            volume_encryption_key=self.volume_encryption_key,
            workspace_id=self.workspace_id,
            workspace_properties=self.workspace_properties)


def get_workspace(directory_id: Optional[str] = None,
                  tags: Optional[Mapping[str, str]] = None,
                  user_name: Optional[str] = None,
                  workspace_id: Optional[str] = None,
                  opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetWorkspaceResult:
    """
    Use this data source to get information about a workspace in [AWS Workspaces](https://docs.aws.amazon.com/workspaces/latest/adminguide/amazon-workspaces.html) Service.

    ## Example Usage
    ### Filter By Workspace ID

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.workspaces.get_workspace(workspace_id="ws-cj5xcxsz5")
    ```
    ### Filter By Directory ID & User Name

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.workspaces.get_workspace(directory_id="d-9967252f57",
        user_name="Example")
    ```


    :param str directory_id: ID of the directory for the WorkSpace. You have to specify `user_name` along with `directory_id`. You cannot combine this parameter with `workspace_id`.
    :param Mapping[str, str] tags: Tags for the WorkSpace.
    :param str user_name: User name of the user for the WorkSpace. This user name must exist in the directory for the WorkSpace. You cannot combine this parameter with `workspace_id`.
    :param str workspace_id: ID of the WorkSpace. You cannot combine this parameter with `directory_id`.
    """
    __args__ = dict()
    __args__['directoryId'] = directory_id
    __args__['tags'] = tags
    __args__['userName'] = user_name
    __args__['workspaceId'] = workspace_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:workspaces/getWorkspace:getWorkspace', __args__, opts=opts, typ=GetWorkspaceResult).value

    return AwaitableGetWorkspaceResult(
        bundle_id=pulumi.get(__ret__, 'bundle_id'),
        computer_name=pulumi.get(__ret__, 'computer_name'),
        directory_id=pulumi.get(__ret__, 'directory_id'),
        id=pulumi.get(__ret__, 'id'),
        ip_address=pulumi.get(__ret__, 'ip_address'),
        root_volume_encryption_enabled=pulumi.get(__ret__, 'root_volume_encryption_enabled'),
        state=pulumi.get(__ret__, 'state'),
        tags=pulumi.get(__ret__, 'tags'),
        user_name=pulumi.get(__ret__, 'user_name'),
        user_volume_encryption_enabled=pulumi.get(__ret__, 'user_volume_encryption_enabled'),
        volume_encryption_key=pulumi.get(__ret__, 'volume_encryption_key'),
        workspace_id=pulumi.get(__ret__, 'workspace_id'),
        workspace_properties=pulumi.get(__ret__, 'workspace_properties'))


@_utilities.lift_output_func(get_workspace)
def get_workspace_output(directory_id: Optional[pulumi.Input[Optional[str]]] = None,
                         tags: Optional[pulumi.Input[Optional[Mapping[str, str]]]] = None,
                         user_name: Optional[pulumi.Input[Optional[str]]] = None,
                         workspace_id: Optional[pulumi.Input[Optional[str]]] = None,
                         opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetWorkspaceResult]:
    """
    Use this data source to get information about a workspace in [AWS Workspaces](https://docs.aws.amazon.com/workspaces/latest/adminguide/amazon-workspaces.html) Service.

    ## Example Usage
    ### Filter By Workspace ID

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.workspaces.get_workspace(workspace_id="ws-cj5xcxsz5")
    ```
    ### Filter By Directory ID & User Name

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.workspaces.get_workspace(directory_id="d-9967252f57",
        user_name="Example")
    ```


    :param str directory_id: ID of the directory for the WorkSpace. You have to specify `user_name` along with `directory_id`. You cannot combine this parameter with `workspace_id`.
    :param Mapping[str, str] tags: Tags for the WorkSpace.
    :param str user_name: User name of the user for the WorkSpace. This user name must exist in the directory for the WorkSpace. You cannot combine this parameter with `workspace_id`.
    :param str workspace_id: ID of the WorkSpace. You cannot combine this parameter with `directory_id`.
    """
    ...
