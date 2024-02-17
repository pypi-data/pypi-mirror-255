# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['EnablerArgs', 'Enabler']

@pulumi.input_type
class EnablerArgs:
    def __init__(__self__, *,
                 account_ids: pulumi.Input[Sequence[pulumi.Input[str]]],
                 resource_types: pulumi.Input[Sequence[pulumi.Input[str]]]):
        """
        The set of arguments for constructing a Enabler resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] account_ids: Set of account IDs.
               Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] resource_types: Type of resources to scan.
               Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
               At least one item is required.
        """
        pulumi.set(__self__, "account_ids", account_ids)
        pulumi.set(__self__, "resource_types", resource_types)

    @property
    @pulumi.getter(name="accountIds")
    def account_ids(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        Set of account IDs.
        Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        """
        return pulumi.get(self, "account_ids")

    @account_ids.setter
    def account_ids(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "account_ids", value)

    @property
    @pulumi.getter(name="resourceTypes")
    def resource_types(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        Type of resources to scan.
        Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
        At least one item is required.
        """
        return pulumi.get(self, "resource_types")

    @resource_types.setter
    def resource_types(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "resource_types", value)


@pulumi.input_type
class _EnablerState:
    def __init__(__self__, *,
                 account_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_types: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering Enabler resources.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] account_ids: Set of account IDs.
               Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] resource_types: Type of resources to scan.
               Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
               At least one item is required.
        """
        if account_ids is not None:
            pulumi.set(__self__, "account_ids", account_ids)
        if resource_types is not None:
            pulumi.set(__self__, "resource_types", resource_types)

    @property
    @pulumi.getter(name="accountIds")
    def account_ids(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Set of account IDs.
        Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        """
        return pulumi.get(self, "account_ids")

    @account_ids.setter
    def account_ids(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "account_ids", value)

    @property
    @pulumi.getter(name="resourceTypes")
    def resource_types(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Type of resources to scan.
        Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
        At least one item is required.
        """
        return pulumi.get(self, "resource_types")

    @resource_types.setter
    def resource_types(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "resource_types", value)


class Enabler(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 account_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_types: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Resource for enabling Amazon Inspector resource scans.

        This resource must be created in the Organization's Administrator Account.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.inspector2.Enabler("example",
            account_ids=["123456789012"],
            resource_types=["EC2"])
        ```
        ### For the Calling Account

        ```python
        import pulumi
        import pulumi_aws as aws

        current = aws.get_caller_identity()
        test = aws.inspector2.Enabler("test",
            account_ids=[current.account_id],
            resource_types=[
                "ECR",
                "EC2",
            ])
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] account_ids: Set of account IDs.
               Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] resource_types: Type of resources to scan.
               Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
               At least one item is required.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EnablerArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for enabling Amazon Inspector resource scans.

        This resource must be created in the Organization's Administrator Account.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.inspector2.Enabler("example",
            account_ids=["123456789012"],
            resource_types=["EC2"])
        ```
        ### For the Calling Account

        ```python
        import pulumi
        import pulumi_aws as aws

        current = aws.get_caller_identity()
        test = aws.inspector2.Enabler("test",
            account_ids=[current.account_id],
            resource_types=[
                "ECR",
                "EC2",
            ])
        ```

        :param str resource_name: The name of the resource.
        :param EnablerArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EnablerArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 account_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_types: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EnablerArgs.__new__(EnablerArgs)

            if account_ids is None and not opts.urn:
                raise TypeError("Missing required property 'account_ids'")
            __props__.__dict__["account_ids"] = account_ids
            if resource_types is None and not opts.urn:
                raise TypeError("Missing required property 'resource_types'")
            __props__.__dict__["resource_types"] = resource_types
        super(Enabler, __self__).__init__(
            'aws:inspector2/enabler:Enabler',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            account_ids: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            resource_types: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None) -> 'Enabler':
        """
        Get an existing Enabler resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] account_ids: Set of account IDs.
               Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] resource_types: Type of resources to scan.
               Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
               At least one item is required.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _EnablerState.__new__(_EnablerState)

        __props__.__dict__["account_ids"] = account_ids
        __props__.__dict__["resource_types"] = resource_types
        return Enabler(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="accountIds")
    def account_ids(self) -> pulumi.Output[Sequence[str]]:
        """
        Set of account IDs.
        Can contain one of: the Organization's Administrator Account, or one or more Member Accounts.
        """
        return pulumi.get(self, "account_ids")

    @property
    @pulumi.getter(name="resourceTypes")
    def resource_types(self) -> pulumi.Output[Sequence[str]]:
        """
        Type of resources to scan.
        Valid values are `EC2`, `ECR`, `LAMBDA` and `LAMBDA_CODE`.
        At least one item is required.
        """
        return pulumi.get(self, "resource_types")

