# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['PolicyTemplateArgs', 'PolicyTemplate']

@pulumi.input_type
class PolicyTemplateArgs:
    def __init__(__self__, *,
                 policy_store_id: pulumi.Input[str],
                 statement: pulumi.Input[str],
                 description: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a PolicyTemplate resource.
        :param pulumi.Input[str] policy_store_id: The ID of the Policy Store.
        :param pulumi.Input[str] statement: Defines the content of the statement, written in Cedar policy language.
               
               The following arguments are optional:
        :param pulumi.Input[str] description: Provides a description for the policy template.
        """
        pulumi.set(__self__, "policy_store_id", policy_store_id)
        pulumi.set(__self__, "statement", statement)
        if description is not None:
            pulumi.set(__self__, "description", description)

    @property
    @pulumi.getter(name="policyStoreId")
    def policy_store_id(self) -> pulumi.Input[str]:
        """
        The ID of the Policy Store.
        """
        return pulumi.get(self, "policy_store_id")

    @policy_store_id.setter
    def policy_store_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "policy_store_id", value)

    @property
    @pulumi.getter
    def statement(self) -> pulumi.Input[str]:
        """
        Defines the content of the statement, written in Cedar policy language.

        The following arguments are optional:
        """
        return pulumi.get(self, "statement")

    @statement.setter
    def statement(self, value: pulumi.Input[str]):
        pulumi.set(self, "statement", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Provides a description for the policy template.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)


@pulumi.input_type
class _PolicyTemplateState:
    def __init__(__self__, *,
                 created_date: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 policy_store_id: Optional[pulumi.Input[str]] = None,
                 policy_template_id: Optional[pulumi.Input[str]] = None,
                 statement: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering PolicyTemplate resources.
        :param pulumi.Input[str] created_date: The date the Policy Store was created.
        :param pulumi.Input[str] description: Provides a description for the policy template.
        :param pulumi.Input[str] policy_store_id: The ID of the Policy Store.
        :param pulumi.Input[str] policy_template_id: The ID of the Policy Store.
        :param pulumi.Input[str] statement: Defines the content of the statement, written in Cedar policy language.
               
               The following arguments are optional:
        """
        if created_date is not None:
            pulumi.set(__self__, "created_date", created_date)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if policy_store_id is not None:
            pulumi.set(__self__, "policy_store_id", policy_store_id)
        if policy_template_id is not None:
            pulumi.set(__self__, "policy_template_id", policy_template_id)
        if statement is not None:
            pulumi.set(__self__, "statement", statement)

    @property
    @pulumi.getter(name="createdDate")
    def created_date(self) -> Optional[pulumi.Input[str]]:
        """
        The date the Policy Store was created.
        """
        return pulumi.get(self, "created_date")

    @created_date.setter
    def created_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "created_date", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Provides a description for the policy template.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="policyStoreId")
    def policy_store_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Policy Store.
        """
        return pulumi.get(self, "policy_store_id")

    @policy_store_id.setter
    def policy_store_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_store_id", value)

    @property
    @pulumi.getter(name="policyTemplateId")
    def policy_template_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the Policy Store.
        """
        return pulumi.get(self, "policy_template_id")

    @policy_template_id.setter
    def policy_template_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_template_id", value)

    @property
    @pulumi.getter
    def statement(self) -> Optional[pulumi.Input[str]]:
        """
        Defines the content of the statement, written in Cedar policy language.

        The following arguments are optional:
        """
        return pulumi.get(self, "statement")

    @statement.setter
    def statement(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "statement", value)


class PolicyTemplate(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 policy_store_id: Optional[pulumi.Input[str]] = None,
                 statement: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource for managing an AWS Verified Permissions Policy Template.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.verifiedpermissions.PolicyTemplate("example",
            policy_store_id=aws_verifiedpermissions_policy_store["example"]["id"],
            statement="permit (principal in ?principal, action in PhotoFlash::Action::\\"FullPhotoAccess\\", resource == ?resource) unless { resource.IsPrivate };")
        ```

        ## Import

        Using `pulumi import`, import Verified Permissions Policy Store using the `policy_store_id:policy_template_id`. For example:

        ```sh
         $ pulumi import aws:verifiedpermissions/policyTemplate:PolicyTemplate example policyStoreId:policyTemplateId
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: Provides a description for the policy template.
        :param pulumi.Input[str] policy_store_id: The ID of the Policy Store.
        :param pulumi.Input[str] statement: Defines the content of the statement, written in Cedar policy language.
               
               The following arguments are optional:
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: PolicyTemplateArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing an AWS Verified Permissions Policy Template.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.verifiedpermissions.PolicyTemplate("example",
            policy_store_id=aws_verifiedpermissions_policy_store["example"]["id"],
            statement="permit (principal in ?principal, action in PhotoFlash::Action::\\"FullPhotoAccess\\", resource == ?resource) unless { resource.IsPrivate };")
        ```

        ## Import

        Using `pulumi import`, import Verified Permissions Policy Store using the `policy_store_id:policy_template_id`. For example:

        ```sh
         $ pulumi import aws:verifiedpermissions/policyTemplate:PolicyTemplate example policyStoreId:policyTemplateId
        ```

        :param str resource_name: The name of the resource.
        :param PolicyTemplateArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(PolicyTemplateArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 policy_store_id: Optional[pulumi.Input[str]] = None,
                 statement: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = PolicyTemplateArgs.__new__(PolicyTemplateArgs)

            __props__.__dict__["description"] = description
            if policy_store_id is None and not opts.urn:
                raise TypeError("Missing required property 'policy_store_id'")
            __props__.__dict__["policy_store_id"] = policy_store_id
            if statement is None and not opts.urn:
                raise TypeError("Missing required property 'statement'")
            __props__.__dict__["statement"] = statement
            __props__.__dict__["created_date"] = None
            __props__.__dict__["policy_template_id"] = None
        super(PolicyTemplate, __self__).__init__(
            'aws:verifiedpermissions/policyTemplate:PolicyTemplate',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            created_date: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            policy_store_id: Optional[pulumi.Input[str]] = None,
            policy_template_id: Optional[pulumi.Input[str]] = None,
            statement: Optional[pulumi.Input[str]] = None) -> 'PolicyTemplate':
        """
        Get an existing PolicyTemplate resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] created_date: The date the Policy Store was created.
        :param pulumi.Input[str] description: Provides a description for the policy template.
        :param pulumi.Input[str] policy_store_id: The ID of the Policy Store.
        :param pulumi.Input[str] policy_template_id: The ID of the Policy Store.
        :param pulumi.Input[str] statement: Defines the content of the statement, written in Cedar policy language.
               
               The following arguments are optional:
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _PolicyTemplateState.__new__(_PolicyTemplateState)

        __props__.__dict__["created_date"] = created_date
        __props__.__dict__["description"] = description
        __props__.__dict__["policy_store_id"] = policy_store_id
        __props__.__dict__["policy_template_id"] = policy_template_id
        __props__.__dict__["statement"] = statement
        return PolicyTemplate(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="createdDate")
    def created_date(self) -> pulumi.Output[str]:
        """
        The date the Policy Store was created.
        """
        return pulumi.get(self, "created_date")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        Provides a description for the policy template.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="policyStoreId")
    def policy_store_id(self) -> pulumi.Output[str]:
        """
        The ID of the Policy Store.
        """
        return pulumi.get(self, "policy_store_id")

    @property
    @pulumi.getter(name="policyTemplateId")
    def policy_template_id(self) -> pulumi.Output[str]:
        """
        The ID of the Policy Store.
        """
        return pulumi.get(self, "policy_template_id")

    @property
    @pulumi.getter
    def statement(self) -> pulumi.Output[str]:
        """
        Defines the content of the statement, written in Cedar policy language.

        The following arguments are optional:
        """
        return pulumi.get(self, "statement")

