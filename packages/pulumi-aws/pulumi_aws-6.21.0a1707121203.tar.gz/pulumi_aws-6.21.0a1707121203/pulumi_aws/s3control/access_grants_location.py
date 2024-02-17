# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['AccessGrantsLocationArgs', 'AccessGrantsLocation']

@pulumi.input_type
class AccessGrantsLocationArgs:
    def __init__(__self__, *,
                 iam_role_arn: pulumi.Input[str],
                 location_scope: pulumi.Input[str],
                 account_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a AccessGrantsLocation resource.
        :param pulumi.Input[str] iam_role_arn: The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
               requests to the location.
        :param pulumi.Input[str] location_scope: The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "iam_role_arn", iam_role_arn)
        pulumi.set(__self__, "location_scope", location_scope)
        if account_id is not None:
            pulumi.set(__self__, "account_id", account_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="iamRoleArn")
    def iam_role_arn(self) -> pulumi.Input[str]:
        """
        The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
        requests to the location.
        """
        return pulumi.get(self, "iam_role_arn")

    @iam_role_arn.setter
    def iam_role_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "iam_role_arn", value)

    @property
    @pulumi.getter(name="locationScope")
    def location_scope(self) -> pulumi.Input[str]:
        """
        The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        """
        return pulumi.get(self, "location_scope")

    @location_scope.setter
    def location_scope(self, value: pulumi.Input[str]):
        pulumi.set(self, "location_scope", value)

    @property
    @pulumi.getter(name="accountId")
    def account_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "account_id")

    @account_id.setter
    def account_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "account_id", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _AccessGrantsLocationState:
    def __init__(__self__, *,
                 access_grants_location_arn: Optional[pulumi.Input[str]] = None,
                 access_grants_location_id: Optional[pulumi.Input[str]] = None,
                 account_id: Optional[pulumi.Input[str]] = None,
                 iam_role_arn: Optional[pulumi.Input[str]] = None,
                 location_scope: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering AccessGrantsLocation resources.
        :param pulumi.Input[str] access_grants_location_arn: Amazon Resource Name (ARN) of the S3 Access Grants location.
        :param pulumi.Input[str] access_grants_location_id: Unique ID of the S3 Access Grants location.
        :param pulumi.Input[str] iam_role_arn: The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
               requests to the location.
        :param pulumi.Input[str] location_scope: The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if access_grants_location_arn is not None:
            pulumi.set(__self__, "access_grants_location_arn", access_grants_location_arn)
        if access_grants_location_id is not None:
            pulumi.set(__self__, "access_grants_location_id", access_grants_location_id)
        if account_id is not None:
            pulumi.set(__self__, "account_id", account_id)
        if iam_role_arn is not None:
            pulumi.set(__self__, "iam_role_arn", iam_role_arn)
        if location_scope is not None:
            pulumi.set(__self__, "location_scope", location_scope)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)

    @property
    @pulumi.getter(name="accessGrantsLocationArn")
    def access_grants_location_arn(self) -> Optional[pulumi.Input[str]]:
        """
        Amazon Resource Name (ARN) of the S3 Access Grants location.
        """
        return pulumi.get(self, "access_grants_location_arn")

    @access_grants_location_arn.setter
    def access_grants_location_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_grants_location_arn", value)

    @property
    @pulumi.getter(name="accessGrantsLocationId")
    def access_grants_location_id(self) -> Optional[pulumi.Input[str]]:
        """
        Unique ID of the S3 Access Grants location.
        """
        return pulumi.get(self, "access_grants_location_id")

    @access_grants_location_id.setter
    def access_grants_location_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "access_grants_location_id", value)

    @property
    @pulumi.getter(name="accountId")
    def account_id(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "account_id")

    @account_id.setter
    def account_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "account_id", value)

    @property
    @pulumi.getter(name="iamRoleArn")
    def iam_role_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
        requests to the location.
        """
        return pulumi.get(self, "iam_role_arn")

    @iam_role_arn.setter
    def iam_role_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "iam_role_arn", value)

    @property
    @pulumi.getter(name="locationScope")
    def location_scope(self) -> Optional[pulumi.Input[str]]:
        """
        The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        """
        return pulumi.get(self, "location_scope")

    @location_scope.setter
    def location_scope(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "location_scope", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
        pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")

        return pulumi.get(self, "tags_all")

    @tags_all.setter
    def tags_all(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags_all", value)


class AccessGrantsLocation(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 account_id: Optional[pulumi.Input[str]] = None,
                 iam_role_arn: Optional[pulumi.Input[str]] = None,
                 location_scope: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides a resource to manage an S3 Access Grants location.
        A location is an S3 resource (bucket or prefix) in a permission grant that the grantee can access.
        The S3 data must be in the same Region as your S3 Access Grants instance.
        When you register a location, you must include the IAM role that has permission to manage the S3 location that you are registering.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_access_grants_instance = aws.s3control.AccessGrantsInstance("exampleAccessGrantsInstance")
        example_access_grants_location = aws.s3control.AccessGrantsLocation("exampleAccessGrantsLocation",
            iam_role_arn=aws_iam_role["example"]["arn"],
            location_scope="s3://",
            opts=pulumi.ResourceOptions(depends_on=[example_access_grants_instance]))
        # Default scope.
        ```

        ## Import

        Using `pulumi import`, import S3 Access Grants locations using the `account_id` and `access_grants_location_id`, separated by a comma (`,`). For example:

        ```sh
         $ pulumi import aws:s3control/accessGrantsLocation:AccessGrantsLocation example 123456789012,default
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] iam_role_arn: The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
               requests to the location.
        :param pulumi.Input[str] location_scope: The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: AccessGrantsLocationArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a resource to manage an S3 Access Grants location.
        A location is an S3 resource (bucket or prefix) in a permission grant that the grantee can access.
        The S3 data must be in the same Region as your S3 Access Grants instance.
        When you register a location, you must include the IAM role that has permission to manage the S3 location that you are registering.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_access_grants_instance = aws.s3control.AccessGrantsInstance("exampleAccessGrantsInstance")
        example_access_grants_location = aws.s3control.AccessGrantsLocation("exampleAccessGrantsLocation",
            iam_role_arn=aws_iam_role["example"]["arn"],
            location_scope="s3://",
            opts=pulumi.ResourceOptions(depends_on=[example_access_grants_instance]))
        # Default scope.
        ```

        ## Import

        Using `pulumi import`, import S3 Access Grants locations using the `account_id` and `access_grants_location_id`, separated by a comma (`,`). For example:

        ```sh
         $ pulumi import aws:s3control/accessGrantsLocation:AccessGrantsLocation example 123456789012,default
        ```

        :param str resource_name: The name of the resource.
        :param AccessGrantsLocationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(AccessGrantsLocationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 account_id: Optional[pulumi.Input[str]] = None,
                 iam_role_arn: Optional[pulumi.Input[str]] = None,
                 location_scope: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = AccessGrantsLocationArgs.__new__(AccessGrantsLocationArgs)

            __props__.__dict__["account_id"] = account_id
            if iam_role_arn is None and not opts.urn:
                raise TypeError("Missing required property 'iam_role_arn'")
            __props__.__dict__["iam_role_arn"] = iam_role_arn
            if location_scope is None and not opts.urn:
                raise TypeError("Missing required property 'location_scope'")
            __props__.__dict__["location_scope"] = location_scope
            __props__.__dict__["tags"] = tags
            __props__.__dict__["access_grants_location_arn"] = None
            __props__.__dict__["access_grants_location_id"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(AccessGrantsLocation, __self__).__init__(
            'aws:s3control/accessGrantsLocation:AccessGrantsLocation',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            access_grants_location_arn: Optional[pulumi.Input[str]] = None,
            access_grants_location_id: Optional[pulumi.Input[str]] = None,
            account_id: Optional[pulumi.Input[str]] = None,
            iam_role_arn: Optional[pulumi.Input[str]] = None,
            location_scope: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'AccessGrantsLocation':
        """
        Get an existing AccessGrantsLocation resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] access_grants_location_arn: Amazon Resource Name (ARN) of the S3 Access Grants location.
        :param pulumi.Input[str] access_grants_location_id: Unique ID of the S3 Access Grants location.
        :param pulumi.Input[str] iam_role_arn: The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
               requests to the location.
        :param pulumi.Input[str] location_scope: The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _AccessGrantsLocationState.__new__(_AccessGrantsLocationState)

        __props__.__dict__["access_grants_location_arn"] = access_grants_location_arn
        __props__.__dict__["access_grants_location_id"] = access_grants_location_id
        __props__.__dict__["account_id"] = account_id
        __props__.__dict__["iam_role_arn"] = iam_role_arn
        __props__.__dict__["location_scope"] = location_scope
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return AccessGrantsLocation(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="accessGrantsLocationArn")
    def access_grants_location_arn(self) -> pulumi.Output[str]:
        """
        Amazon Resource Name (ARN) of the S3 Access Grants location.
        """
        return pulumi.get(self, "access_grants_location_arn")

    @property
    @pulumi.getter(name="accessGrantsLocationId")
    def access_grants_location_id(self) -> pulumi.Output[str]:
        """
        Unique ID of the S3 Access Grants location.
        """
        return pulumi.get(self, "access_grants_location_id")

    @property
    @pulumi.getter(name="accountId")
    def account_id(self) -> pulumi.Output[str]:
        return pulumi.get(self, "account_id")

    @property
    @pulumi.getter(name="iamRoleArn")
    def iam_role_arn(self) -> pulumi.Output[str]:
        """
        The ARN of the IAM role that S3 Access Grants should use when fulfilling runtime access
        requests to the location.
        """
        return pulumi.get(self, "iam_role_arn")

    @property
    @pulumi.getter(name="locationScope")
    def location_scope(self) -> pulumi.Output[str]:
        """
        The default S3 URI `s3://` or the URI to a custom location, a specific bucket or prefix.
        """
        return pulumi.get(self, "location_scope")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> pulumi.Output[Mapping[str, str]]:
        """
        A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
        pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")

        return pulumi.get(self, "tags_all")

