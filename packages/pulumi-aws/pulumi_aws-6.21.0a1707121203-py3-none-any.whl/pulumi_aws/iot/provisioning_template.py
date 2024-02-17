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

__all__ = ['ProvisioningTemplateArgs', 'ProvisioningTemplate']

@pulumi.input_type
class ProvisioningTemplateArgs:
    def __init__(__self__, *,
                 provisioning_role_arn: pulumi.Input[str],
                 template_body: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pre_provisioning_hook: Optional[pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ProvisioningTemplate resource.
        :param pulumi.Input[str] provisioning_role_arn: The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        :param pulumi.Input[str] template_body: The JSON formatted contents of the fleet provisioning template.
        :param pulumi.Input[str] description: The description of the fleet provisioning template.
        :param pulumi.Input[bool] enabled: True to enable the fleet provisioning template, otherwise false.
        :param pulumi.Input[str] name: The name of the fleet provisioning template.
        :param pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs'] pre_provisioning_hook: Creates a pre-provisioning hook template. Details below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[str] type: The type you define in a provisioning template.
        """
        pulumi.set(__self__, "provisioning_role_arn", provisioning_role_arn)
        pulumi.set(__self__, "template_body", template_body)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if pre_provisioning_hook is not None:
            pulumi.set(__self__, "pre_provisioning_hook", pre_provisioning_hook)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="provisioningRoleArn")
    def provisioning_role_arn(self) -> pulumi.Input[str]:
        """
        The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        """
        return pulumi.get(self, "provisioning_role_arn")

    @provisioning_role_arn.setter
    def provisioning_role_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "provisioning_role_arn", value)

    @property
    @pulumi.getter(name="templateBody")
    def template_body(self) -> pulumi.Input[str]:
        """
        The JSON formatted contents of the fleet provisioning template.
        """
        return pulumi.get(self, "template_body")

    @template_body.setter
    def template_body(self, value: pulumi.Input[str]):
        pulumi.set(self, "template_body", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the fleet provisioning template.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        True to enable the fleet provisioning template, otherwise false.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the fleet provisioning template.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="preProvisioningHook")
    def pre_provisioning_hook(self) -> Optional[pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs']]:
        """
        Creates a pre-provisioning hook template. Details below.
        """
        return pulumi.get(self, "pre_provisioning_hook")

    @pre_provisioning_hook.setter
    def pre_provisioning_hook(self, value: Optional[pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs']]):
        pulumi.set(self, "pre_provisioning_hook", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        The type you define in a provisioning template.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


@pulumi.input_type
class _ProvisioningTemplateState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 default_version_id: Optional[pulumi.Input[int]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pre_provisioning_hook: Optional[pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs']] = None,
                 provisioning_role_arn: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 template_body: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ProvisioningTemplate resources.
        :param pulumi.Input[str] arn: The ARN that identifies the provisioning template.
        :param pulumi.Input[int] default_version_id: The default version of the fleet provisioning template.
        :param pulumi.Input[str] description: The description of the fleet provisioning template.
        :param pulumi.Input[bool] enabled: True to enable the fleet provisioning template, otherwise false.
        :param pulumi.Input[str] name: The name of the fleet provisioning template.
        :param pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs'] pre_provisioning_hook: Creates a pre-provisioning hook template. Details below.
        :param pulumi.Input[str] provisioning_role_arn: The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[str] template_body: The JSON formatted contents of the fleet provisioning template.
        :param pulumi.Input[str] type: The type you define in a provisioning template.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if default_version_id is not None:
            pulumi.set(__self__, "default_version_id", default_version_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if pre_provisioning_hook is not None:
            pulumi.set(__self__, "pre_provisioning_hook", pre_provisioning_hook)
        if provisioning_role_arn is not None:
            pulumi.set(__self__, "provisioning_role_arn", provisioning_role_arn)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)
        if template_body is not None:
            pulumi.set(__self__, "template_body", template_body)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN that identifies the provisioning template.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="defaultVersionId")
    def default_version_id(self) -> Optional[pulumi.Input[int]]:
        """
        The default version of the fleet provisioning template.
        """
        return pulumi.get(self, "default_version_id")

    @default_version_id.setter
    def default_version_id(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "default_version_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the fleet provisioning template.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        True to enable the fleet provisioning template, otherwise false.
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the fleet provisioning template.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="preProvisioningHook")
    def pre_provisioning_hook(self) -> Optional[pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs']]:
        """
        Creates a pre-provisioning hook template. Details below.
        """
        return pulumi.get(self, "pre_provisioning_hook")

    @pre_provisioning_hook.setter
    def pre_provisioning_hook(self, value: Optional[pulumi.Input['ProvisioningTemplatePreProvisioningHookArgs']]):
        pulumi.set(self, "pre_provisioning_hook", value)

    @property
    @pulumi.getter(name="provisioningRoleArn")
    def provisioning_role_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        """
        return pulumi.get(self, "provisioning_role_arn")

    @provisioning_role_arn.setter
    def provisioning_role_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "provisioning_role_arn", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

    @property
    @pulumi.getter(name="templateBody")
    def template_body(self) -> Optional[pulumi.Input[str]]:
        """
        The JSON formatted contents of the fleet provisioning template.
        """
        return pulumi.get(self, "template_body")

    @template_body.setter
    def template_body(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "template_body", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        The type you define in a provisioning template.
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


class ProvisioningTemplate(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pre_provisioning_hook: Optional[pulumi.Input[pulumi.InputType['ProvisioningTemplatePreProvisioningHookArgs']]] = None,
                 provisioning_role_arn: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 template_body: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages an IoT fleet provisioning template. For more info, see the AWS documentation on [fleet provisioning](https://docs.aws.amazon.com/iot/latest/developerguide/provision-wo-cert.html).

        ## Example Usage

        ```python
        import pulumi
        import json
        import pulumi_aws as aws

        iot_assume_role_policy = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="Service",
                identifiers=["iot.amazonaws.com"],
            )],
        )])
        iot_fleet_provisioning = aws.iam.Role("iotFleetProvisioning",
            path="/service-role/",
            assume_role_policy=iot_assume_role_policy.json)
        iot_fleet_provisioning_registration = aws.iam.RolePolicyAttachment("iotFleetProvisioningRegistration",
            role=iot_fleet_provisioning.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration")
        device_policy_policy_document = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            actions=["iot:Subscribe"],
            resources=["*"],
        )])
        device_policy_policy = aws.iot.Policy("devicePolicyPolicy", policy=device_policy_policy_document.json)
        fleet = aws.iot.ProvisioningTemplate("fleet",
            description="My provisioning template",
            provisioning_role_arn=iot_fleet_provisioning.arn,
            enabled=True,
            template_body=device_policy_policy.name.apply(lambda name: json.dumps({
                "Parameters": {
                    "SerialNumber": {
                        "Type": "String",
                    },
                },
                "Resources": {
                    "certificate": {
                        "Properties": {
                            "CertificateId": {
                                "Ref": "AWS::IoT::Certificate::Id",
                            },
                            "Status": "Active",
                        },
                        "Type": "AWS::IoT::Certificate",
                    },
                    "policy": {
                        "Properties": {
                            "PolicyName": name,
                        },
                        "Type": "AWS::IoT::Policy",
                    },
                },
            })))
        ```

        ## Import

        Using `pulumi import`, import IoT fleet provisioning templates using the `name`. For example:

        ```sh
         $ pulumi import aws:iot/provisioningTemplate:ProvisioningTemplate fleet FleetProvisioningTemplate
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: The description of the fleet provisioning template.
        :param pulumi.Input[bool] enabled: True to enable the fleet provisioning template, otherwise false.
        :param pulumi.Input[str] name: The name of the fleet provisioning template.
        :param pulumi.Input[pulumi.InputType['ProvisioningTemplatePreProvisioningHookArgs']] pre_provisioning_hook: Creates a pre-provisioning hook template. Details below.
        :param pulumi.Input[str] provisioning_role_arn: The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[str] template_body: The JSON formatted contents of the fleet provisioning template.
        :param pulumi.Input[str] type: The type you define in a provisioning template.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProvisioningTemplateArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an IoT fleet provisioning template. For more info, see the AWS documentation on [fleet provisioning](https://docs.aws.amazon.com/iot/latest/developerguide/provision-wo-cert.html).

        ## Example Usage

        ```python
        import pulumi
        import json
        import pulumi_aws as aws

        iot_assume_role_policy = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="Service",
                identifiers=["iot.amazonaws.com"],
            )],
        )])
        iot_fleet_provisioning = aws.iam.Role("iotFleetProvisioning",
            path="/service-role/",
            assume_role_policy=iot_assume_role_policy.json)
        iot_fleet_provisioning_registration = aws.iam.RolePolicyAttachment("iotFleetProvisioningRegistration",
            role=iot_fleet_provisioning.name,
            policy_arn="arn:aws:iam::aws:policy/service-role/AWSIoTThingsRegistration")
        device_policy_policy_document = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            actions=["iot:Subscribe"],
            resources=["*"],
        )])
        device_policy_policy = aws.iot.Policy("devicePolicyPolicy", policy=device_policy_policy_document.json)
        fleet = aws.iot.ProvisioningTemplate("fleet",
            description="My provisioning template",
            provisioning_role_arn=iot_fleet_provisioning.arn,
            enabled=True,
            template_body=device_policy_policy.name.apply(lambda name: json.dumps({
                "Parameters": {
                    "SerialNumber": {
                        "Type": "String",
                    },
                },
                "Resources": {
                    "certificate": {
                        "Properties": {
                            "CertificateId": {
                                "Ref": "AWS::IoT::Certificate::Id",
                            },
                            "Status": "Active",
                        },
                        "Type": "AWS::IoT::Certificate",
                    },
                    "policy": {
                        "Properties": {
                            "PolicyName": name,
                        },
                        "Type": "AWS::IoT::Policy",
                    },
                },
            })))
        ```

        ## Import

        Using `pulumi import`, import IoT fleet provisioning templates using the `name`. For example:

        ```sh
         $ pulumi import aws:iot/provisioningTemplate:ProvisioningTemplate fleet FleetProvisioningTemplate
        ```

        :param str resource_name: The name of the resource.
        :param ProvisioningTemplateArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProvisioningTemplateArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 pre_provisioning_hook: Optional[pulumi.Input[pulumi.InputType['ProvisioningTemplatePreProvisioningHookArgs']]] = None,
                 provisioning_role_arn: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 template_body: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ProvisioningTemplateArgs.__new__(ProvisioningTemplateArgs)

            __props__.__dict__["description"] = description
            __props__.__dict__["enabled"] = enabled
            __props__.__dict__["name"] = name
            __props__.__dict__["pre_provisioning_hook"] = pre_provisioning_hook
            if provisioning_role_arn is None and not opts.urn:
                raise TypeError("Missing required property 'provisioning_role_arn'")
            __props__.__dict__["provisioning_role_arn"] = provisioning_role_arn
            __props__.__dict__["tags"] = tags
            if template_body is None and not opts.urn:
                raise TypeError("Missing required property 'template_body'")
            __props__.__dict__["template_body"] = template_body
            __props__.__dict__["type"] = type
            __props__.__dict__["arn"] = None
            __props__.__dict__["default_version_id"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(ProvisioningTemplate, __self__).__init__(
            'aws:iot/provisioningTemplate:ProvisioningTemplate',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            default_version_id: Optional[pulumi.Input[int]] = None,
            description: Optional[pulumi.Input[str]] = None,
            enabled: Optional[pulumi.Input[bool]] = None,
            name: Optional[pulumi.Input[str]] = None,
            pre_provisioning_hook: Optional[pulumi.Input[pulumi.InputType['ProvisioningTemplatePreProvisioningHookArgs']]] = None,
            provisioning_role_arn: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            template_body: Optional[pulumi.Input[str]] = None,
            type: Optional[pulumi.Input[str]] = None) -> 'ProvisioningTemplate':
        """
        Get an existing ProvisioningTemplate resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The ARN that identifies the provisioning template.
        :param pulumi.Input[int] default_version_id: The default version of the fleet provisioning template.
        :param pulumi.Input[str] description: The description of the fleet provisioning template.
        :param pulumi.Input[bool] enabled: True to enable the fleet provisioning template, otherwise false.
        :param pulumi.Input[str] name: The name of the fleet provisioning template.
        :param pulumi.Input[pulumi.InputType['ProvisioningTemplatePreProvisioningHookArgs']] pre_provisioning_hook: Creates a pre-provisioning hook template. Details below.
        :param pulumi.Input[str] provisioning_role_arn: The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[str] template_body: The JSON formatted contents of the fleet provisioning template.
        :param pulumi.Input[str] type: The type you define in a provisioning template.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ProvisioningTemplateState.__new__(_ProvisioningTemplateState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["default_version_id"] = default_version_id
        __props__.__dict__["description"] = description
        __props__.__dict__["enabled"] = enabled
        __props__.__dict__["name"] = name
        __props__.__dict__["pre_provisioning_hook"] = pre_provisioning_hook
        __props__.__dict__["provisioning_role_arn"] = provisioning_role_arn
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        __props__.__dict__["template_body"] = template_body
        __props__.__dict__["type"] = type
        return ProvisioningTemplate(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The ARN that identifies the provisioning template.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="defaultVersionId")
    def default_version_id(self) -> pulumi.Output[int]:
        """
        The default version of the fleet provisioning template.
        """
        return pulumi.get(self, "default_version_id")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        The description of the fleet provisioning template.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        True to enable the fleet provisioning template, otherwise false.
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the fleet provisioning template.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="preProvisioningHook")
    def pre_provisioning_hook(self) -> pulumi.Output[Optional['outputs.ProvisioningTemplatePreProvisioningHook']]:
        """
        Creates a pre-provisioning hook template. Details below.
        """
        return pulumi.get(self, "pre_provisioning_hook")

    @property
    @pulumi.getter(name="provisioningRoleArn")
    def provisioning_role_arn(self) -> pulumi.Output[str]:
        """
        The role ARN for the role associated with the fleet provisioning template. This IoT role grants permission to provision a device.
        """
        return pulumi.get(self, "provisioning_role_arn")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

    @property
    @pulumi.getter(name="templateBody")
    def template_body(self) -> pulumi.Output[str]:
        """
        The JSON formatted contents of the fleet provisioning template.
        """
        return pulumi.get(self, "template_body")

    @property
    @pulumi.getter
    def type(self) -> pulumi.Output[str]:
        """
        The type you define in a provisioning template.
        """
        return pulumi.get(self, "type")

