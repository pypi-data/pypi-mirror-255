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
from ._inputs import *

__all__ = [
    'GetApplicationResult',
    'AwaitableGetApplicationResult',
    'get_application',
    'get_application_output',
]

@pulumi.output_type
class GetApplicationResult:
    """
    A collection of values returned by getApplication.
    """
    def __init__(__self__, application_account=None, application_arn=None, application_provider_arn=None, description=None, id=None, instance_arn=None, name=None, portal_options=None, status=None):
        if application_account and not isinstance(application_account, str):
            raise TypeError("Expected argument 'application_account' to be a str")
        pulumi.set(__self__, "application_account", application_account)
        if application_arn and not isinstance(application_arn, str):
            raise TypeError("Expected argument 'application_arn' to be a str")
        pulumi.set(__self__, "application_arn", application_arn)
        if application_provider_arn and not isinstance(application_provider_arn, str):
            raise TypeError("Expected argument 'application_provider_arn' to be a str")
        pulumi.set(__self__, "application_provider_arn", application_provider_arn)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if instance_arn and not isinstance(instance_arn, str):
            raise TypeError("Expected argument 'instance_arn' to be a str")
        pulumi.set(__self__, "instance_arn", instance_arn)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if portal_options and not isinstance(portal_options, list):
            raise TypeError("Expected argument 'portal_options' to be a list")
        pulumi.set(__self__, "portal_options", portal_options)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter(name="applicationAccount")
    def application_account(self) -> str:
        """
        AWS account ID.
        """
        return pulumi.get(self, "application_account")

    @property
    @pulumi.getter(name="applicationArn")
    def application_arn(self) -> str:
        return pulumi.get(self, "application_arn")

    @property
    @pulumi.getter(name="applicationProviderArn")
    def application_provider_arn(self) -> str:
        """
        ARN of the application provider.
        """
        return pulumi.get(self, "application_provider_arn")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Description of the application.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        ARN of the application.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="instanceArn")
    def instance_arn(self) -> str:
        """
        ARN of the instance of IAM Identity Center.
        """
        return pulumi.get(self, "instance_arn")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the application.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="portalOptions")
    def portal_options(self) -> Optional[Sequence['outputs.GetApplicationPortalOptionResult']]:
        """
        Options for the portal associated with an application. See the `ssoadmin.Application` resource documentation. The attributes are the same.
        """
        return pulumi.get(self, "portal_options")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status of the application.
        """
        return pulumi.get(self, "status")


class AwaitableGetApplicationResult(GetApplicationResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetApplicationResult(
            application_account=self.application_account,
            application_arn=self.application_arn,
            application_provider_arn=self.application_provider_arn,
            description=self.description,
            id=self.id,
            instance_arn=self.instance_arn,
            name=self.name,
            portal_options=self.portal_options,
            status=self.status)


def get_application(application_arn: Optional[str] = None,
                    portal_options: Optional[Sequence[pulumi.InputType['GetApplicationPortalOptionArgs']]] = None,
                    opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetApplicationResult:
    """
    Data source for managing an AWS SSO Admin Application.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.ssoadmin.get_application(application_arn="arn:aws:sso::012345678901:application/ssoins-1234/apl-5678")
    ```


    :param str application_arn: ARN of the application.
    :param Sequence[pulumi.InputType['GetApplicationPortalOptionArgs']] portal_options: Options for the portal associated with an application. See the `ssoadmin.Application` resource documentation. The attributes are the same.
    """
    __args__ = dict()
    __args__['applicationArn'] = application_arn
    __args__['portalOptions'] = portal_options
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:ssoadmin/getApplication:getApplication', __args__, opts=opts, typ=GetApplicationResult).value

    return AwaitableGetApplicationResult(
        application_account=pulumi.get(__ret__, 'application_account'),
        application_arn=pulumi.get(__ret__, 'application_arn'),
        application_provider_arn=pulumi.get(__ret__, 'application_provider_arn'),
        description=pulumi.get(__ret__, 'description'),
        id=pulumi.get(__ret__, 'id'),
        instance_arn=pulumi.get(__ret__, 'instance_arn'),
        name=pulumi.get(__ret__, 'name'),
        portal_options=pulumi.get(__ret__, 'portal_options'),
        status=pulumi.get(__ret__, 'status'))


@_utilities.lift_output_func(get_application)
def get_application_output(application_arn: Optional[pulumi.Input[str]] = None,
                           portal_options: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetApplicationPortalOptionArgs']]]]] = None,
                           opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetApplicationResult]:
    """
    Data source for managing an AWS SSO Admin Application.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.ssoadmin.get_application(application_arn="arn:aws:sso::012345678901:application/ssoins-1234/apl-5678")
    ```


    :param str application_arn: ARN of the application.
    :param Sequence[pulumi.InputType['GetApplicationPortalOptionArgs']] portal_options: Options for the portal associated with an application. See the `ssoadmin.Application` resource documentation. The attributes are the same.
    """
    ...
