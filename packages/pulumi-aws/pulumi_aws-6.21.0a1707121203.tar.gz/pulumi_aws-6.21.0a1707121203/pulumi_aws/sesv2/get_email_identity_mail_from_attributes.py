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
    'GetEmailIdentityMailFromAttributesResult',
    'AwaitableGetEmailIdentityMailFromAttributesResult',
    'get_email_identity_mail_from_attributes',
    'get_email_identity_mail_from_attributes_output',
]

@pulumi.output_type
class GetEmailIdentityMailFromAttributesResult:
    """
    A collection of values returned by getEmailIdentityMailFromAttributes.
    """
    def __init__(__self__, behavior_on_mx_failure=None, email_identity=None, id=None, mail_from_domain=None):
        if behavior_on_mx_failure and not isinstance(behavior_on_mx_failure, str):
            raise TypeError("Expected argument 'behavior_on_mx_failure' to be a str")
        pulumi.set(__self__, "behavior_on_mx_failure", behavior_on_mx_failure)
        if email_identity and not isinstance(email_identity, str):
            raise TypeError("Expected argument 'email_identity' to be a str")
        pulumi.set(__self__, "email_identity", email_identity)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if mail_from_domain and not isinstance(mail_from_domain, str):
            raise TypeError("Expected argument 'mail_from_domain' to be a str")
        pulumi.set(__self__, "mail_from_domain", mail_from_domain)

    @property
    @pulumi.getter(name="behaviorOnMxFailure")
    def behavior_on_mx_failure(self) -> str:
        """
        The action to take if the required MX record isn't found when you send an email. Valid values: `USE_DEFAULT_VALUE`, `REJECT_MESSAGE`.
        """
        return pulumi.get(self, "behavior_on_mx_failure")

    @property
    @pulumi.getter(name="emailIdentity")
    def email_identity(self) -> str:
        return pulumi.get(self, "email_identity")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="mailFromDomain")
    def mail_from_domain(self) -> str:
        """
        The custom MAIL FROM domain that you want the verified identity to use.
        """
        return pulumi.get(self, "mail_from_domain")


class AwaitableGetEmailIdentityMailFromAttributesResult(GetEmailIdentityMailFromAttributesResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetEmailIdentityMailFromAttributesResult(
            behavior_on_mx_failure=self.behavior_on_mx_failure,
            email_identity=self.email_identity,
            id=self.id,
            mail_from_domain=self.mail_from_domain)


def get_email_identity_mail_from_attributes(email_identity: Optional[str] = None,
                                            opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetEmailIdentityMailFromAttributesResult:
    """
    Data source for managing an AWS SESv2 (Simple Email V2) Email Identity Mail From Attributes.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example_email_identity = aws.sesv2.get_email_identity(email_identity="example.com")
    example_email_identity_mail_from_attributes = aws.sesv2.get_email_identity_mail_from_attributes(email_identity=example_email_identity.email_identity)
    ```


    :param str email_identity: The name of the email identity.
    """
    __args__ = dict()
    __args__['emailIdentity'] = email_identity
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:sesv2/getEmailIdentityMailFromAttributes:getEmailIdentityMailFromAttributes', __args__, opts=opts, typ=GetEmailIdentityMailFromAttributesResult).value

    return AwaitableGetEmailIdentityMailFromAttributesResult(
        behavior_on_mx_failure=pulumi.get(__ret__, 'behavior_on_mx_failure'),
        email_identity=pulumi.get(__ret__, 'email_identity'),
        id=pulumi.get(__ret__, 'id'),
        mail_from_domain=pulumi.get(__ret__, 'mail_from_domain'))


@_utilities.lift_output_func(get_email_identity_mail_from_attributes)
def get_email_identity_mail_from_attributes_output(email_identity: Optional[pulumi.Input[str]] = None,
                                                   opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetEmailIdentityMailFromAttributesResult]:
    """
    Data source for managing an AWS SESv2 (Simple Email V2) Email Identity Mail From Attributes.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example_email_identity = aws.sesv2.get_email_identity(email_identity="example.com")
    example_email_identity_mail_from_attributes = aws.sesv2.get_email_identity_mail_from_attributes(email_identity=example_email_identity.email_identity)
    ```


    :param str email_identity: The name of the email identity.
    """
    ...
