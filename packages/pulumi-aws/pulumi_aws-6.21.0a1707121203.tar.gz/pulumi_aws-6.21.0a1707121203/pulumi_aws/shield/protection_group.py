# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ProtectionGroupArgs', 'ProtectionGroup']

@pulumi.input_type
class ProtectionGroupArgs:
    def __init__(__self__, *,
                 aggregation: pulumi.Input[str],
                 pattern: pulumi.Input[str],
                 protection_group_id: pulumi.Input[str],
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 resource_type: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a ProtectionGroup resource.
        :param pulumi.Input[str] aggregation: Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        :param pulumi.Input[str] pattern: The criteria to use to choose the protected resources for inclusion in the group.
        :param pulumi.Input[str] protection_group_id: The name of the protection group.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        :param pulumi.Input[str] resource_type: The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "aggregation", aggregation)
        pulumi.set(__self__, "pattern", pattern)
        pulumi.set(__self__, "protection_group_id", protection_group_id)
        if members is not None:
            pulumi.set(__self__, "members", members)
        if resource_type is not None:
            pulumi.set(__self__, "resource_type", resource_type)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def aggregation(self) -> pulumi.Input[str]:
        """
        Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        """
        return pulumi.get(self, "aggregation")

    @aggregation.setter
    def aggregation(self, value: pulumi.Input[str]):
        pulumi.set(self, "aggregation", value)

    @property
    @pulumi.getter
    def pattern(self) -> pulumi.Input[str]:
        """
        The criteria to use to choose the protected resources for inclusion in the group.
        """
        return pulumi.get(self, "pattern")

    @pattern.setter
    def pattern(self, value: pulumi.Input[str]):
        pulumi.set(self, "pattern", value)

    @property
    @pulumi.getter(name="protectionGroupId")
    def protection_group_id(self) -> pulumi.Input[str]:
        """
        The name of the protection group.
        """
        return pulumi.get(self, "protection_group_id")

    @protection_group_id.setter
    def protection_group_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "protection_group_id", value)

    @property
    @pulumi.getter
    def members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "members", value)

    @property
    @pulumi.getter(name="resourceType")
    def resource_type(self) -> Optional[pulumi.Input[str]]:
        """
        The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        """
        return pulumi.get(self, "resource_type")

    @resource_type.setter
    def resource_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_type", value)

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
class _ProtectionGroupState:
    def __init__(__self__, *,
                 aggregation: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 pattern: Optional[pulumi.Input[str]] = None,
                 protection_group_arn: Optional[pulumi.Input[str]] = None,
                 protection_group_id: Optional[pulumi.Input[str]] = None,
                 resource_type: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering ProtectionGroup resources.
        :param pulumi.Input[str] aggregation: Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        :param pulumi.Input[str] pattern: The criteria to use to choose the protected resources for inclusion in the group.
        :param pulumi.Input[str] protection_group_arn: The ARN (Amazon Resource Name) of the protection group.
        :param pulumi.Input[str] protection_group_id: The name of the protection group.
        :param pulumi.Input[str] resource_type: The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if aggregation is not None:
            pulumi.set(__self__, "aggregation", aggregation)
        if members is not None:
            pulumi.set(__self__, "members", members)
        if pattern is not None:
            pulumi.set(__self__, "pattern", pattern)
        if protection_group_arn is not None:
            pulumi.set(__self__, "protection_group_arn", protection_group_arn)
        if protection_group_id is not None:
            pulumi.set(__self__, "protection_group_id", protection_group_id)
        if resource_type is not None:
            pulumi.set(__self__, "resource_type", resource_type)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)

    @property
    @pulumi.getter
    def aggregation(self) -> Optional[pulumi.Input[str]]:
        """
        Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        """
        return pulumi.get(self, "aggregation")

    @aggregation.setter
    def aggregation(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "aggregation", value)

    @property
    @pulumi.getter
    def members(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        """
        return pulumi.get(self, "members")

    @members.setter
    def members(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "members", value)

    @property
    @pulumi.getter
    def pattern(self) -> Optional[pulumi.Input[str]]:
        """
        The criteria to use to choose the protected resources for inclusion in the group.
        """
        return pulumi.get(self, "pattern")

    @pattern.setter
    def pattern(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "pattern", value)

    @property
    @pulumi.getter(name="protectionGroupArn")
    def protection_group_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN (Amazon Resource Name) of the protection group.
        """
        return pulumi.get(self, "protection_group_arn")

    @protection_group_arn.setter
    def protection_group_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protection_group_arn", value)

    @property
    @pulumi.getter(name="protectionGroupId")
    def protection_group_id(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the protection group.
        """
        return pulumi.get(self, "protection_group_id")

    @protection_group_id.setter
    def protection_group_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protection_group_id", value)

    @property
    @pulumi.getter(name="resourceType")
    def resource_type(self) -> Optional[pulumi.Input[str]]:
        """
        The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        """
        return pulumi.get(self, "resource_type")

    @resource_type.setter
    def resource_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_type", value)

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


class ProtectionGroup(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 aggregation: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 pattern: Optional[pulumi.Input[str]] = None,
                 protection_group_id: Optional[pulumi.Input[str]] = None,
                 resource_type: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Creates a grouping of protected resources so they can be handled as a collective.
        This resource grouping improves the accuracy of detection and reduces false positives. For more information see
        [Managing AWS Shield Advanced protection groups](https://docs.aws.amazon.com/waf/latest/developerguide/manage-protection-group.html)

        ## Example Usage
        ### Create protection group for all resources

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.shield.ProtectionGroup("example",
            aggregation="MAX",
            pattern="ALL",
            protection_group_id="example")
        ```
        ### Create protection group for arbitrary number of resources

        ```python
        import pulumi
        import pulumi_aws as aws

        current_region = aws.get_region()
        current_caller_identity = aws.get_caller_identity()
        example_eip = aws.ec2.Eip("exampleEip", domain="vpc")
        example_protection = aws.shield.Protection("exampleProtection", resource_arn=example_eip.id.apply(lambda id: f"arn:aws:ec2:{current_region.name}:{current_caller_identity.account_id}:eip-allocation/{id}"))
        example_protection_group = aws.shield.ProtectionGroup("exampleProtectionGroup",
            protection_group_id="example",
            aggregation="MEAN",
            pattern="ARBITRARY",
            members=[example_eip.id.apply(lambda id: f"arn:aws:ec2:{current_region.name}:{current_caller_identity.account_id}:eip-allocation/{id}")],
            opts=pulumi.ResourceOptions(depends_on=[example_protection]))
        ```
        ### Create protection group for a type of resource

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.shield.ProtectionGroup("example",
            aggregation="SUM",
            pattern="BY_RESOURCE_TYPE",
            protection_group_id="example",
            resource_type="ELASTIC_IP_ALLOCATION")
        ```

        ## Import

        Using `pulumi import`, import Shield protection group resources using their protection group id. For example:

        ```sh
         $ pulumi import aws:shield/protectionGroup:ProtectionGroup example example
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] aggregation: Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        :param pulumi.Input[str] pattern: The criteria to use to choose the protected resources for inclusion in the group.
        :param pulumi.Input[str] protection_group_id: The name of the protection group.
        :param pulumi.Input[str] resource_type: The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProtectionGroupArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Creates a grouping of protected resources so they can be handled as a collective.
        This resource grouping improves the accuracy of detection and reduces false positives. For more information see
        [Managing AWS Shield Advanced protection groups](https://docs.aws.amazon.com/waf/latest/developerguide/manage-protection-group.html)

        ## Example Usage
        ### Create protection group for all resources

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.shield.ProtectionGroup("example",
            aggregation="MAX",
            pattern="ALL",
            protection_group_id="example")
        ```
        ### Create protection group for arbitrary number of resources

        ```python
        import pulumi
        import pulumi_aws as aws

        current_region = aws.get_region()
        current_caller_identity = aws.get_caller_identity()
        example_eip = aws.ec2.Eip("exampleEip", domain="vpc")
        example_protection = aws.shield.Protection("exampleProtection", resource_arn=example_eip.id.apply(lambda id: f"arn:aws:ec2:{current_region.name}:{current_caller_identity.account_id}:eip-allocation/{id}"))
        example_protection_group = aws.shield.ProtectionGroup("exampleProtectionGroup",
            protection_group_id="example",
            aggregation="MEAN",
            pattern="ARBITRARY",
            members=[example_eip.id.apply(lambda id: f"arn:aws:ec2:{current_region.name}:{current_caller_identity.account_id}:eip-allocation/{id}")],
            opts=pulumi.ResourceOptions(depends_on=[example_protection]))
        ```
        ### Create protection group for a type of resource

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.shield.ProtectionGroup("example",
            aggregation="SUM",
            pattern="BY_RESOURCE_TYPE",
            protection_group_id="example",
            resource_type="ELASTIC_IP_ALLOCATION")
        ```

        ## Import

        Using `pulumi import`, import Shield protection group resources using their protection group id. For example:

        ```sh
         $ pulumi import aws:shield/protectionGroup:ProtectionGroup example example
        ```

        :param str resource_name: The name of the resource.
        :param ProtectionGroupArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProtectionGroupArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 aggregation: Optional[pulumi.Input[str]] = None,
                 members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 pattern: Optional[pulumi.Input[str]] = None,
                 protection_group_id: Optional[pulumi.Input[str]] = None,
                 resource_type: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ProtectionGroupArgs.__new__(ProtectionGroupArgs)

            if aggregation is None and not opts.urn:
                raise TypeError("Missing required property 'aggregation'")
            __props__.__dict__["aggregation"] = aggregation
            __props__.__dict__["members"] = members
            if pattern is None and not opts.urn:
                raise TypeError("Missing required property 'pattern'")
            __props__.__dict__["pattern"] = pattern
            if protection_group_id is None and not opts.urn:
                raise TypeError("Missing required property 'protection_group_id'")
            __props__.__dict__["protection_group_id"] = protection_group_id
            __props__.__dict__["resource_type"] = resource_type
            __props__.__dict__["tags"] = tags
            __props__.__dict__["protection_group_arn"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(ProtectionGroup, __self__).__init__(
            'aws:shield/protectionGroup:ProtectionGroup',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            aggregation: Optional[pulumi.Input[str]] = None,
            members: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            pattern: Optional[pulumi.Input[str]] = None,
            protection_group_arn: Optional[pulumi.Input[str]] = None,
            protection_group_id: Optional[pulumi.Input[str]] = None,
            resource_type: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'ProtectionGroup':
        """
        Get an existing ProtectionGroup resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] aggregation: Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] members: The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        :param pulumi.Input[str] pattern: The criteria to use to choose the protected resources for inclusion in the group.
        :param pulumi.Input[str] protection_group_arn: The ARN (Amazon Resource Name) of the protection group.
        :param pulumi.Input[str] protection_group_id: The name of the protection group.
        :param pulumi.Input[str] resource_type: The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ProtectionGroupState.__new__(_ProtectionGroupState)

        __props__.__dict__["aggregation"] = aggregation
        __props__.__dict__["members"] = members
        __props__.__dict__["pattern"] = pattern
        __props__.__dict__["protection_group_arn"] = protection_group_arn
        __props__.__dict__["protection_group_id"] = protection_group_id
        __props__.__dict__["resource_type"] = resource_type
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return ProtectionGroup(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def aggregation(self) -> pulumi.Output[str]:
        """
        Defines how AWS Shield combines resource data for the group in order to detect, mitigate, and report events.
        """
        return pulumi.get(self, "aggregation")

    @property
    @pulumi.getter
    def members(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        The Amazon Resource Names (ARNs) of the resources to include in the protection group. You must set this when you set `pattern` to ARBITRARY and you must not set it for any other `pattern` setting.
        """
        return pulumi.get(self, "members")

    @property
    @pulumi.getter
    def pattern(self) -> pulumi.Output[str]:
        """
        The criteria to use to choose the protected resources for inclusion in the group.
        """
        return pulumi.get(self, "pattern")

    @property
    @pulumi.getter(name="protectionGroupArn")
    def protection_group_arn(self) -> pulumi.Output[str]:
        """
        The ARN (Amazon Resource Name) of the protection group.
        """
        return pulumi.get(self, "protection_group_arn")

    @property
    @pulumi.getter(name="protectionGroupId")
    def protection_group_id(self) -> pulumi.Output[str]:
        """
        The name of the protection group.
        """
        return pulumi.get(self, "protection_group_id")

    @property
    @pulumi.getter(name="resourceType")
    def resource_type(self) -> pulumi.Output[Optional[str]]:
        """
        The resource type to include in the protection group. You must set this when you set `pattern` to BY_RESOURCE_TYPE and you must not set it for any other `pattern` setting.
        """
        return pulumi.get(self, "resource_type")

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

