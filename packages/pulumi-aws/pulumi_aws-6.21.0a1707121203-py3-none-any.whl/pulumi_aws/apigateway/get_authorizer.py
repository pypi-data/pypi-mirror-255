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
    'GetAuthorizerResult',
    'AwaitableGetAuthorizerResult',
    'get_authorizer',
    'get_authorizer_output',
]

@pulumi.output_type
class GetAuthorizerResult:
    """
    A collection of values returned by getAuthorizer.
    """
    def __init__(__self__, arn=None, authorizer_credentials=None, authorizer_id=None, authorizer_result_ttl_in_seconds=None, authorizer_uri=None, id=None, identity_source=None, identity_validation_expression=None, name=None, provider_arns=None, rest_api_id=None, type=None):
        if arn and not isinstance(arn, str):
            raise TypeError("Expected argument 'arn' to be a str")
        pulumi.set(__self__, "arn", arn)
        if authorizer_credentials and not isinstance(authorizer_credentials, str):
            raise TypeError("Expected argument 'authorizer_credentials' to be a str")
        pulumi.set(__self__, "authorizer_credentials", authorizer_credentials)
        if authorizer_id and not isinstance(authorizer_id, str):
            raise TypeError("Expected argument 'authorizer_id' to be a str")
        pulumi.set(__self__, "authorizer_id", authorizer_id)
        if authorizer_result_ttl_in_seconds and not isinstance(authorizer_result_ttl_in_seconds, int):
            raise TypeError("Expected argument 'authorizer_result_ttl_in_seconds' to be a int")
        pulumi.set(__self__, "authorizer_result_ttl_in_seconds", authorizer_result_ttl_in_seconds)
        if authorizer_uri and not isinstance(authorizer_uri, str):
            raise TypeError("Expected argument 'authorizer_uri' to be a str")
        pulumi.set(__self__, "authorizer_uri", authorizer_uri)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if identity_source and not isinstance(identity_source, str):
            raise TypeError("Expected argument 'identity_source' to be a str")
        pulumi.set(__self__, "identity_source", identity_source)
        if identity_validation_expression and not isinstance(identity_validation_expression, str):
            raise TypeError("Expected argument 'identity_validation_expression' to be a str")
        pulumi.set(__self__, "identity_validation_expression", identity_validation_expression)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if provider_arns and not isinstance(provider_arns, list):
            raise TypeError("Expected argument 'provider_arns' to be a list")
        pulumi.set(__self__, "provider_arns", provider_arns)
        if rest_api_id and not isinstance(rest_api_id, str):
            raise TypeError("Expected argument 'rest_api_id' to be a str")
        pulumi.set(__self__, "rest_api_id", rest_api_id)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def arn(self) -> str:
        """
        ARN of the API Gateway Authorizer.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="authorizerCredentials")
    def authorizer_credentials(self) -> str:
        """
        Credentials required for the authorizer.
        """
        return pulumi.get(self, "authorizer_credentials")

    @property
    @pulumi.getter(name="authorizerId")
    def authorizer_id(self) -> str:
        return pulumi.get(self, "authorizer_id")

    @property
    @pulumi.getter(name="authorizerResultTtlInSeconds")
    def authorizer_result_ttl_in_seconds(self) -> int:
        """
        TTL of cached authorizer results in seconds.
        """
        return pulumi.get(self, "authorizer_result_ttl_in_seconds")

    @property
    @pulumi.getter(name="authorizerUri")
    def authorizer_uri(self) -> str:
        """
        Authorizer's Uniform Resource Identifier (URI).
        """
        return pulumi.get(self, "authorizer_uri")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="identitySource")
    def identity_source(self) -> str:
        """
        Source of the identity in an incoming request.
        """
        return pulumi.get(self, "identity_source")

    @property
    @pulumi.getter(name="identityValidationExpression")
    def identity_validation_expression(self) -> str:
        """
        Validation expression for the incoming identity.
        """
        return pulumi.get(self, "identity_validation_expression")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the authorizer.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="providerArns")
    def provider_arns(self) -> Sequence[str]:
        """
        List of the Amazon Cognito user pool ARNs.
        """
        return pulumi.get(self, "provider_arns")

    @property
    @pulumi.getter(name="restApiId")
    def rest_api_id(self) -> str:
        return pulumi.get(self, "rest_api_id")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        Type of the authorizer.
        """
        return pulumi.get(self, "type")


class AwaitableGetAuthorizerResult(GetAuthorizerResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetAuthorizerResult(
            arn=self.arn,
            authorizer_credentials=self.authorizer_credentials,
            authorizer_id=self.authorizer_id,
            authorizer_result_ttl_in_seconds=self.authorizer_result_ttl_in_seconds,
            authorizer_uri=self.authorizer_uri,
            id=self.id,
            identity_source=self.identity_source,
            identity_validation_expression=self.identity_validation_expression,
            name=self.name,
            provider_arns=self.provider_arns,
            rest_api_id=self.rest_api_id,
            type=self.type)


def get_authorizer(authorizer_id: Optional[str] = None,
                   rest_api_id: Optional[str] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetAuthorizerResult:
    """
    Provides details about a specific API Gateway Authorizer.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.apigateway.get_authorizer(rest_api_id=aws_api_gateway_rest_api["example"]["id"],
        authorizer_id=data["aws_api_gateway_authorizers"]["example"]["ids"])
    ```


    :param str authorizer_id: Authorizer identifier.
    :param str rest_api_id: ID of the associated REST API.
    """
    __args__ = dict()
    __args__['authorizerId'] = authorizer_id
    __args__['restApiId'] = rest_api_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:apigateway/getAuthorizer:getAuthorizer', __args__, opts=opts, typ=GetAuthorizerResult).value

    return AwaitableGetAuthorizerResult(
        arn=pulumi.get(__ret__, 'arn'),
        authorizer_credentials=pulumi.get(__ret__, 'authorizer_credentials'),
        authorizer_id=pulumi.get(__ret__, 'authorizer_id'),
        authorizer_result_ttl_in_seconds=pulumi.get(__ret__, 'authorizer_result_ttl_in_seconds'),
        authorizer_uri=pulumi.get(__ret__, 'authorizer_uri'),
        id=pulumi.get(__ret__, 'id'),
        identity_source=pulumi.get(__ret__, 'identity_source'),
        identity_validation_expression=pulumi.get(__ret__, 'identity_validation_expression'),
        name=pulumi.get(__ret__, 'name'),
        provider_arns=pulumi.get(__ret__, 'provider_arns'),
        rest_api_id=pulumi.get(__ret__, 'rest_api_id'),
        type=pulumi.get(__ret__, 'type'))


@_utilities.lift_output_func(get_authorizer)
def get_authorizer_output(authorizer_id: Optional[pulumi.Input[str]] = None,
                          rest_api_id: Optional[pulumi.Input[str]] = None,
                          opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetAuthorizerResult]:
    """
    Provides details about a specific API Gateway Authorizer.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.apigateway.get_authorizer(rest_api_id=aws_api_gateway_rest_api["example"]["id"],
        authorizer_id=data["aws_api_gateway_authorizers"]["example"]["ids"])
    ```


    :param str authorizer_id: Authorizer identifier.
    :param str rest_api_id: ID of the associated REST API.
    """
    ...
