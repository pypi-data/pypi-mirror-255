# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['RestApiPolicyArgs', 'RestApiPolicy']

@pulumi.input_type
class RestApiPolicyArgs:
    def __init__(__self__, *,
                 policy: pulumi.Input[str],
                 rest_api_id: pulumi.Input[str]):
        """
        The set of arguments for constructing a RestApiPolicy resource.
        :param pulumi.Input[str] policy: JSON formatted policy document that controls access to the API Gateway.
        :param pulumi.Input[str] rest_api_id: ID of the REST API.
        """
        pulumi.set(__self__, "policy", policy)
        pulumi.set(__self__, "rest_api_id", rest_api_id)

    @property
    @pulumi.getter
    def policy(self) -> pulumi.Input[str]:
        """
        JSON formatted policy document that controls access to the API Gateway.
        """
        return pulumi.get(self, "policy")

    @policy.setter
    def policy(self, value: pulumi.Input[str]):
        pulumi.set(self, "policy", value)

    @property
    @pulumi.getter(name="restApiId")
    def rest_api_id(self) -> pulumi.Input[str]:
        """
        ID of the REST API.
        """
        return pulumi.get(self, "rest_api_id")

    @rest_api_id.setter
    def rest_api_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "rest_api_id", value)


@pulumi.input_type
class _RestApiPolicyState:
    def __init__(__self__, *,
                 policy: Optional[pulumi.Input[str]] = None,
                 rest_api_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering RestApiPolicy resources.
        :param pulumi.Input[str] policy: JSON formatted policy document that controls access to the API Gateway.
        :param pulumi.Input[str] rest_api_id: ID of the REST API.
        """
        if policy is not None:
            pulumi.set(__self__, "policy", policy)
        if rest_api_id is not None:
            pulumi.set(__self__, "rest_api_id", rest_api_id)

    @property
    @pulumi.getter
    def policy(self) -> Optional[pulumi.Input[str]]:
        """
        JSON formatted policy document that controls access to the API Gateway.
        """
        return pulumi.get(self, "policy")

    @policy.setter
    def policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy", value)

    @property
    @pulumi.getter(name="restApiId")
    def rest_api_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the REST API.
        """
        return pulumi.get(self, "rest_api_id")

    @rest_api_id.setter
    def rest_api_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "rest_api_id", value)


class RestApiPolicy(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 policy: Optional[pulumi.Input[str]] = None,
                 rest_api_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides an API Gateway REST API Policy.

        > **Note:** Amazon API Gateway Version 1 resources are used for creating and deploying REST APIs. To create and deploy WebSocket and HTTP APIs, use Amazon API Gateway Version 2 resources.

        ## Example Usage
        ### Basic

        ```python
        import pulumi
        import pulumi_aws as aws

        test_rest_api = aws.apigateway.RestApi("testRestApi")
        test_policy_document = aws.iam.get_policy_document_output(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="AWS",
                identifiers=["*"],
            )],
            actions=["execute-api:Invoke"],
            resources=[test_rest_api.execution_arn],
            conditions=[aws.iam.GetPolicyDocumentStatementConditionArgs(
                test="IpAddress",
                variable="aws:SourceIp",
                values=["123.123.123.123/32"],
            )],
        )])
        test_rest_api_policy = aws.apigateway.RestApiPolicy("testRestApiPolicy",
            rest_api_id=test_rest_api.id,
            policy=test_policy_document.json)
        ```

        ## Import

        Using `pulumi import`, import `aws_api_gateway_rest_api_policy` using the REST API ID. For example:

        ```sh
         $ pulumi import aws:apigateway/restApiPolicy:RestApiPolicy example 12345abcde
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] policy: JSON formatted policy document that controls access to the API Gateway.
        :param pulumi.Input[str] rest_api_id: ID of the REST API.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RestApiPolicyArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an API Gateway REST API Policy.

        > **Note:** Amazon API Gateway Version 1 resources are used for creating and deploying REST APIs. To create and deploy WebSocket and HTTP APIs, use Amazon API Gateway Version 2 resources.

        ## Example Usage
        ### Basic

        ```python
        import pulumi
        import pulumi_aws as aws

        test_rest_api = aws.apigateway.RestApi("testRestApi")
        test_policy_document = aws.iam.get_policy_document_output(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="AWS",
                identifiers=["*"],
            )],
            actions=["execute-api:Invoke"],
            resources=[test_rest_api.execution_arn],
            conditions=[aws.iam.GetPolicyDocumentStatementConditionArgs(
                test="IpAddress",
                variable="aws:SourceIp",
                values=["123.123.123.123/32"],
            )],
        )])
        test_rest_api_policy = aws.apigateway.RestApiPolicy("testRestApiPolicy",
            rest_api_id=test_rest_api.id,
            policy=test_policy_document.json)
        ```

        ## Import

        Using `pulumi import`, import `aws_api_gateway_rest_api_policy` using the REST API ID. For example:

        ```sh
         $ pulumi import aws:apigateway/restApiPolicy:RestApiPolicy example 12345abcde
        ```

        :param str resource_name: The name of the resource.
        :param RestApiPolicyArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RestApiPolicyArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 policy: Optional[pulumi.Input[str]] = None,
                 rest_api_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RestApiPolicyArgs.__new__(RestApiPolicyArgs)

            if policy is None and not opts.urn:
                raise TypeError("Missing required property 'policy'")
            __props__.__dict__["policy"] = policy
            if rest_api_id is None and not opts.urn:
                raise TypeError("Missing required property 'rest_api_id'")
            __props__.__dict__["rest_api_id"] = rest_api_id
        super(RestApiPolicy, __self__).__init__(
            'aws:apigateway/restApiPolicy:RestApiPolicy',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            policy: Optional[pulumi.Input[str]] = None,
            rest_api_id: Optional[pulumi.Input[str]] = None) -> 'RestApiPolicy':
        """
        Get an existing RestApiPolicy resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] policy: JSON formatted policy document that controls access to the API Gateway.
        :param pulumi.Input[str] rest_api_id: ID of the REST API.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _RestApiPolicyState.__new__(_RestApiPolicyState)

        __props__.__dict__["policy"] = policy
        __props__.__dict__["rest_api_id"] = rest_api_id
        return RestApiPolicy(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def policy(self) -> pulumi.Output[str]:
        """
        JSON formatted policy document that controls access to the API Gateway.
        """
        return pulumi.get(self, "policy")

    @property
    @pulumi.getter(name="restApiId")
    def rest_api_id(self) -> pulumi.Output[str]:
        """
        ID of the REST API.
        """
        return pulumi.get(self, "rest_api_id")

