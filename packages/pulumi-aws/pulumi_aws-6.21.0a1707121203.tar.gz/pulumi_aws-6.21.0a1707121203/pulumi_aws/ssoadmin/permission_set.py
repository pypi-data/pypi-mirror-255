# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['PermissionSetArgs', 'PermissionSet']

@pulumi.input_type
class PermissionSetArgs:
    def __init__(__self__, *,
                 instance_arn: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 relay_state: Optional[pulumi.Input[str]] = None,
                 session_duration: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a PermissionSet resource.
        :param pulumi.Input[str] instance_arn: The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        :param pulumi.Input[str] description: The description of the Permission Set.
        :param pulumi.Input[str] name: The name of the Permission Set.
        :param pulumi.Input[str] relay_state: The relay state URL used to redirect users within the application during the federation authentication process.
        :param pulumi.Input[str] session_duration: The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "instance_arn", instance_arn)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if relay_state is not None:
            pulumi.set(__self__, "relay_state", relay_state)
        if session_duration is not None:
            pulumi.set(__self__, "session_duration", session_duration)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="instanceArn")
    def instance_arn(self) -> pulumi.Input[str]:
        """
        The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        """
        return pulumi.get(self, "instance_arn")

    @instance_arn.setter
    def instance_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_arn", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the Permission Set.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Permission Set.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="relayState")
    def relay_state(self) -> Optional[pulumi.Input[str]]:
        """
        The relay state URL used to redirect users within the application during the federation authentication process.
        """
        return pulumi.get(self, "relay_state")

    @relay_state.setter
    def relay_state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "relay_state", value)

    @property
    @pulumi.getter(name="sessionDuration")
    def session_duration(self) -> Optional[pulumi.Input[str]]:
        """
        The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        """
        return pulumi.get(self, "session_duration")

    @session_duration.setter
    def session_duration(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "session_duration", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _PermissionSetState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 created_date: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 instance_arn: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 relay_state: Optional[pulumi.Input[str]] = None,
                 session_duration: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering PermissionSet resources.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) of the Permission Set.
        :param pulumi.Input[str] created_date: The date the Permission Set was created in [RFC3339 format](https://tools.ietf.org/html/rfc3339#section-5.8).
        :param pulumi.Input[str] description: The description of the Permission Set.
        :param pulumi.Input[str] instance_arn: The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        :param pulumi.Input[str] name: The name of the Permission Set.
        :param pulumi.Input[str] relay_state: The relay state URL used to redirect users within the application during the federation authentication process.
        :param pulumi.Input[str] session_duration: The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if created_date is not None:
            pulumi.set(__self__, "created_date", created_date)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if instance_arn is not None:
            pulumi.set(__self__, "instance_arn", instance_arn)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if relay_state is not None:
            pulumi.set(__self__, "relay_state", relay_state)
        if session_duration is not None:
            pulumi.set(__self__, "session_duration", session_duration)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) of the Permission Set.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="createdDate")
    def created_date(self) -> Optional[pulumi.Input[str]]:
        """
        The date the Permission Set was created in [RFC3339 format](https://tools.ietf.org/html/rfc3339#section-5.8).
        """
        return pulumi.get(self, "created_date")

    @created_date.setter
    def created_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "created_date", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the Permission Set.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="instanceArn")
    def instance_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        """
        return pulumi.get(self, "instance_arn")

    @instance_arn.setter
    def instance_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "instance_arn", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the Permission Set.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="relayState")
    def relay_state(self) -> Optional[pulumi.Input[str]]:
        """
        The relay state URL used to redirect users within the application during the federation authentication process.
        """
        return pulumi.get(self, "relay_state")

    @relay_state.setter
    def relay_state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "relay_state", value)

    @property
    @pulumi.getter(name="sessionDuration")
    def session_duration(self) -> Optional[pulumi.Input[str]]:
        """
        The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        """
        return pulumi.get(self, "session_duration")

    @session_duration.setter
    def session_duration(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "session_duration", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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


class PermissionSet(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 instance_arn: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 relay_state: Optional[pulumi.Input[str]] = None,
                 session_duration: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides a Single Sign-On (SSO) Permission Set resource

        > **NOTE:** Updating this resource will automatically [Provision the Permission Set](https://docs.aws.amazon.com/singlesignon/latest/APIReference/API_ProvisionPermissionSet.html) to apply the corresponding updates to all assigned accounts.

        ## Import

        Using `pulumi import`, import SSO Permission Sets using the `arn` and `instance_arn` separated by a comma (`,`). For example:

        ```sh
         $ pulumi import aws:ssoadmin/permissionSet:PermissionSet example arn:aws:sso:::permissionSet/ssoins-2938j0x8920sbj72/ps-80383020jr9302rk,arn:aws:sso:::instance/ssoins-2938j0x8920sbj72
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: The description of the Permission Set.
        :param pulumi.Input[str] instance_arn: The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        :param pulumi.Input[str] name: The name of the Permission Set.
        :param pulumi.Input[str] relay_state: The relay state URL used to redirect users within the application during the federation authentication process.
        :param pulumi.Input[str] session_duration: The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: PermissionSetArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a Single Sign-On (SSO) Permission Set resource

        > **NOTE:** Updating this resource will automatically [Provision the Permission Set](https://docs.aws.amazon.com/singlesignon/latest/APIReference/API_ProvisionPermissionSet.html) to apply the corresponding updates to all assigned accounts.

        ## Import

        Using `pulumi import`, import SSO Permission Sets using the `arn` and `instance_arn` separated by a comma (`,`). For example:

        ```sh
         $ pulumi import aws:ssoadmin/permissionSet:PermissionSet example arn:aws:sso:::permissionSet/ssoins-2938j0x8920sbj72/ps-80383020jr9302rk,arn:aws:sso:::instance/ssoins-2938j0x8920sbj72
        ```

        :param str resource_name: The name of the resource.
        :param PermissionSetArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(PermissionSetArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 instance_arn: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 relay_state: Optional[pulumi.Input[str]] = None,
                 session_duration: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = PermissionSetArgs.__new__(PermissionSetArgs)

            __props__.__dict__["description"] = description
            if instance_arn is None and not opts.urn:
                raise TypeError("Missing required property 'instance_arn'")
            __props__.__dict__["instance_arn"] = instance_arn
            __props__.__dict__["name"] = name
            __props__.__dict__["relay_state"] = relay_state
            __props__.__dict__["session_duration"] = session_duration
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["created_date"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(PermissionSet, __self__).__init__(
            'aws:ssoadmin/permissionSet:PermissionSet',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            created_date: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            instance_arn: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            relay_state: Optional[pulumi.Input[str]] = None,
            session_duration: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'PermissionSet':
        """
        Get an existing PermissionSet resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) of the Permission Set.
        :param pulumi.Input[str] created_date: The date the Permission Set was created in [RFC3339 format](https://tools.ietf.org/html/rfc3339#section-5.8).
        :param pulumi.Input[str] description: The description of the Permission Set.
        :param pulumi.Input[str] instance_arn: The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        :param pulumi.Input[str] name: The name of the Permission Set.
        :param pulumi.Input[str] relay_state: The relay state URL used to redirect users within the application during the federation authentication process.
        :param pulumi.Input[str] session_duration: The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _PermissionSetState.__new__(_PermissionSetState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["created_date"] = created_date
        __props__.__dict__["description"] = description
        __props__.__dict__["instance_arn"] = instance_arn
        __props__.__dict__["name"] = name
        __props__.__dict__["relay_state"] = relay_state
        __props__.__dict__["session_duration"] = session_duration
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return PermissionSet(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) of the Permission Set.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="createdDate")
    def created_date(self) -> pulumi.Output[str]:
        """
        The date the Permission Set was created in [RFC3339 format](https://tools.ietf.org/html/rfc3339#section-5.8).
        """
        return pulumi.get(self, "created_date")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        The description of the Permission Set.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="instanceArn")
    def instance_arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) of the SSO Instance under which the operation will be executed.
        """
        return pulumi.get(self, "instance_arn")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the Permission Set.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="relayState")
    def relay_state(self) -> pulumi.Output[Optional[str]]:
        """
        The relay state URL used to redirect users within the application during the federation authentication process.
        """
        return pulumi.get(self, "relay_state")

    @property
    @pulumi.getter(name="sessionDuration")
    def session_duration(self) -> pulumi.Output[Optional[str]]:
        """
        The length of time that the application user sessions are valid in the ISO-8601 standard. Default: `PT1H`.
        """
        return pulumi.get(self, "session_duration")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

