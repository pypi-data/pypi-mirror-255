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

__all__ = ['AccountArgs', 'Account']

@pulumi.input_type
class AccountArgs:
    def __init__(__self__, *,
                 cloudwatch_role_arn: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Account resource.
        :param pulumi.Input[str] cloudwatch_role_arn: ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        """
        if cloudwatch_role_arn is not None:
            pulumi.set(__self__, "cloudwatch_role_arn", cloudwatch_role_arn)

    @property
    @pulumi.getter(name="cloudwatchRoleArn")
    def cloudwatch_role_arn(self) -> Optional[pulumi.Input[str]]:
        """
        ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        """
        return pulumi.get(self, "cloudwatch_role_arn")

    @cloudwatch_role_arn.setter
    def cloudwatch_role_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cloudwatch_role_arn", value)


@pulumi.input_type
class _AccountState:
    def __init__(__self__, *,
                 api_key_version: Optional[pulumi.Input[str]] = None,
                 cloudwatch_role_arn: Optional[pulumi.Input[str]] = None,
                 features: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 throttle_settings: Optional[pulumi.Input[Sequence[pulumi.Input['AccountThrottleSettingArgs']]]] = None):
        """
        Input properties used for looking up and filtering Account resources.
        :param pulumi.Input[str] api_key_version: The version of the API keys used for the account.
        :param pulumi.Input[str] cloudwatch_role_arn: ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] features: A list of features supported for the account.
        :param pulumi.Input[Sequence[pulumi.Input['AccountThrottleSettingArgs']]] throttle_settings: Account-Level throttle settings. See exported fields below.
        """
        if api_key_version is not None:
            pulumi.set(__self__, "api_key_version", api_key_version)
        if cloudwatch_role_arn is not None:
            pulumi.set(__self__, "cloudwatch_role_arn", cloudwatch_role_arn)
        if features is not None:
            pulumi.set(__self__, "features", features)
        if throttle_settings is not None:
            pulumi.set(__self__, "throttle_settings", throttle_settings)

    @property
    @pulumi.getter(name="apiKeyVersion")
    def api_key_version(self) -> Optional[pulumi.Input[str]]:
        """
        The version of the API keys used for the account.
        """
        return pulumi.get(self, "api_key_version")

    @api_key_version.setter
    def api_key_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "api_key_version", value)

    @property
    @pulumi.getter(name="cloudwatchRoleArn")
    def cloudwatch_role_arn(self) -> Optional[pulumi.Input[str]]:
        """
        ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        """
        return pulumi.get(self, "cloudwatch_role_arn")

    @cloudwatch_role_arn.setter
    def cloudwatch_role_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cloudwatch_role_arn", value)

    @property
    @pulumi.getter
    def features(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of features supported for the account.
        """
        return pulumi.get(self, "features")

    @features.setter
    def features(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "features", value)

    @property
    @pulumi.getter(name="throttleSettings")
    def throttle_settings(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['AccountThrottleSettingArgs']]]]:
        """
        Account-Level throttle settings. See exported fields below.
        """
        return pulumi.get(self, "throttle_settings")

    @throttle_settings.setter
    def throttle_settings(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['AccountThrottleSettingArgs']]]]):
        pulumi.set(self, "throttle_settings", value)


class Account(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cloudwatch_role_arn: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a settings of an API Gateway Account. Settings is applied region-wide per `provider` block.

        > **Note:** As there is no API method for deleting account settings or resetting it to defaults, destroying this resource will keep your account settings intact

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        assume_role = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="Service",
                identifiers=["apigateway.amazonaws.com"],
            )],
            actions=["sts:AssumeRole"],
        )])
        cloudwatch_role = aws.iam.Role("cloudwatchRole", assume_role_policy=assume_role.json)
        demo = aws.apigateway.Account("demo", cloudwatch_role_arn=cloudwatch_role.arn)
        cloudwatch_policy_document = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents",
            ],
            resources=["*"],
        )])
        cloudwatch_role_policy = aws.iam.RolePolicy("cloudwatchRolePolicy",
            role=cloudwatch_role.id,
            policy=cloudwatch_policy_document.json)
        ```

        ## Import

        Using `pulumi import`, import API Gateway Accounts using the word `api-gateway-account`. For example:

        ```sh
         $ pulumi import aws:apigateway/account:Account demo api-gateway-account
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cloudwatch_role_arn: ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[AccountArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a settings of an API Gateway Account. Settings is applied region-wide per `provider` block.

        > **Note:** As there is no API method for deleting account settings or resetting it to defaults, destroying this resource will keep your account settings intact

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        assume_role = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="Service",
                identifiers=["apigateway.amazonaws.com"],
            )],
            actions=["sts:AssumeRole"],
        )])
        cloudwatch_role = aws.iam.Role("cloudwatchRole", assume_role_policy=assume_role.json)
        demo = aws.apigateway.Account("demo", cloudwatch_role_arn=cloudwatch_role.arn)
        cloudwatch_policy_document = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            actions=[
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents",
                "logs:GetLogEvents",
                "logs:FilterLogEvents",
            ],
            resources=["*"],
        )])
        cloudwatch_role_policy = aws.iam.RolePolicy("cloudwatchRolePolicy",
            role=cloudwatch_role.id,
            policy=cloudwatch_policy_document.json)
        ```

        ## Import

        Using `pulumi import`, import API Gateway Accounts using the word `api-gateway-account`. For example:

        ```sh
         $ pulumi import aws:apigateway/account:Account demo api-gateway-account
        ```

        :param str resource_name: The name of the resource.
        :param AccountArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AccountArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cloudwatch_role_arn: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = AccountArgs.__new__(AccountArgs)

            __props__.__dict__["cloudwatch_role_arn"] = cloudwatch_role_arn
            __props__.__dict__["api_key_version"] = None
            __props__.__dict__["features"] = None
            __props__.__dict__["throttle_settings"] = None
        super(Account, __self__).__init__(
            'aws:apigateway/account:Account',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            api_key_version: Optional[pulumi.Input[str]] = None,
            cloudwatch_role_arn: Optional[pulumi.Input[str]] = None,
            features: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            throttle_settings: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['AccountThrottleSettingArgs']]]]] = None) -> 'Account':
        """
        Get an existing Account resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] api_key_version: The version of the API keys used for the account.
        :param pulumi.Input[str] cloudwatch_role_arn: ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] features: A list of features supported for the account.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['AccountThrottleSettingArgs']]]] throttle_settings: Account-Level throttle settings. See exported fields below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _AccountState.__new__(_AccountState)

        __props__.__dict__["api_key_version"] = api_key_version
        __props__.__dict__["cloudwatch_role_arn"] = cloudwatch_role_arn
        __props__.__dict__["features"] = features
        __props__.__dict__["throttle_settings"] = throttle_settings
        return Account(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="apiKeyVersion")
    def api_key_version(self) -> pulumi.Output[str]:
        """
        The version of the API keys used for the account.
        """
        return pulumi.get(self, "api_key_version")

    @property
    @pulumi.getter(name="cloudwatchRoleArn")
    def cloudwatch_role_arn(self) -> pulumi.Output[Optional[str]]:
        """
        ARN of an IAM role for CloudWatch (to allow logging & monitoring). See more [in AWS Docs](https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-stage-settings.html#how-to-stage-settings-console). Logging & monitoring can be enabled/disabled and otherwise tuned on the API Gateway Stage level.
        """
        return pulumi.get(self, "cloudwatch_role_arn")

    @property
    @pulumi.getter
    def features(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of features supported for the account.
        """
        return pulumi.get(self, "features")

    @property
    @pulumi.getter(name="throttleSettings")
    def throttle_settings(self) -> pulumi.Output[Sequence['outputs.AccountThrottleSetting']]:
        """
        Account-Level throttle settings. See exported fields below.
        """
        return pulumi.get(self, "throttle_settings")

