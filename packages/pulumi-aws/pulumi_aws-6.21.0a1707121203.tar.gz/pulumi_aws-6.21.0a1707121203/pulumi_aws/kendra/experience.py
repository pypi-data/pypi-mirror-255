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

__all__ = ['ExperienceArgs', 'Experience']

@pulumi.input_type
class ExperienceArgs:
    def __init__(__self__, *,
                 index_id: pulumi.Input[str],
                 role_arn: pulumi.Input[str],
                 configuration: Optional[pulumi.Input['ExperienceConfigurationArgs']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a Experience resource.
        :param pulumi.Input[str] index_id: The identifier of the index for your Amazon Kendra experience.
        :param pulumi.Input[str] role_arn: The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).
               
               The following arguments are optional:
        :param pulumi.Input['ExperienceConfigurationArgs'] configuration: Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        :param pulumi.Input[str] description: A description for your Amazon Kendra experience.
        :param pulumi.Input[str] name: A name for your Amazon Kendra experience.
        """
        pulumi.set(__self__, "index_id", index_id)
        pulumi.set(__self__, "role_arn", role_arn)
        if configuration is not None:
            pulumi.set(__self__, "configuration", configuration)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)

    @property
    @pulumi.getter(name="indexId")
    def index_id(self) -> pulumi.Input[str]:
        """
        The identifier of the index for your Amazon Kendra experience.
        """
        return pulumi.get(self, "index_id")

    @index_id.setter
    def index_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "index_id", value)

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> pulumi.Input[str]:
        """
        The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).

        The following arguments are optional:
        """
        return pulumi.get(self, "role_arn")

    @role_arn.setter
    def role_arn(self, value: pulumi.Input[str]):
        pulumi.set(self, "role_arn", value)

    @property
    @pulumi.getter
    def configuration(self) -> Optional[pulumi.Input['ExperienceConfigurationArgs']]:
        """
        Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        """
        return pulumi.get(self, "configuration")

    @configuration.setter
    def configuration(self, value: Optional[pulumi.Input['ExperienceConfigurationArgs']]):
        pulumi.set(self, "configuration", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description for your Amazon Kendra experience.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A name for your Amazon Kendra experience.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)


@pulumi.input_type
class _ExperienceState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 configuration: Optional[pulumi.Input['ExperienceConfigurationArgs']] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 endpoints: Optional[pulumi.Input[Sequence[pulumi.Input['ExperienceEndpointArgs']]]] = None,
                 experience_id: Optional[pulumi.Input[str]] = None,
                 index_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 role_arn: Optional[pulumi.Input[str]] = None,
                 status: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering Experience resources.
        :param pulumi.Input[str] arn: ARN of the Experience.
        :param pulumi.Input['ExperienceConfigurationArgs'] configuration: Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        :param pulumi.Input[str] description: A description for your Amazon Kendra experience.
        :param pulumi.Input[Sequence[pulumi.Input['ExperienceEndpointArgs']]] endpoints: Shows the endpoint URLs for your Amazon Kendra experiences. The URLs are unique and fully hosted by AWS.
        :param pulumi.Input[str] experience_id: The unique identifier of the experience.
        :param pulumi.Input[str] index_id: The identifier of the index for your Amazon Kendra experience.
        :param pulumi.Input[str] name: A name for your Amazon Kendra experience.
        :param pulumi.Input[str] role_arn: The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).
               
               The following arguments are optional:
        :param pulumi.Input[str] status: The current processing status of your Amazon Kendra experience.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if configuration is not None:
            pulumi.set(__self__, "configuration", configuration)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if endpoints is not None:
            pulumi.set(__self__, "endpoints", endpoints)
        if experience_id is not None:
            pulumi.set(__self__, "experience_id", experience_id)
        if index_id is not None:
            pulumi.set(__self__, "index_id", index_id)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if role_arn is not None:
            pulumi.set(__self__, "role_arn", role_arn)
        if status is not None:
            pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        ARN of the Experience.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter
    def configuration(self) -> Optional[pulumi.Input['ExperienceConfigurationArgs']]:
        """
        Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        """
        return pulumi.get(self, "configuration")

    @configuration.setter
    def configuration(self, value: Optional[pulumi.Input['ExperienceConfigurationArgs']]):
        pulumi.set(self, "configuration", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description for your Amazon Kendra experience.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def endpoints(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ExperienceEndpointArgs']]]]:
        """
        Shows the endpoint URLs for your Amazon Kendra experiences. The URLs are unique and fully hosted by AWS.
        """
        return pulumi.get(self, "endpoints")

    @endpoints.setter
    def endpoints(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ExperienceEndpointArgs']]]]):
        pulumi.set(self, "endpoints", value)

    @property
    @pulumi.getter(name="experienceId")
    def experience_id(self) -> Optional[pulumi.Input[str]]:
        """
        The unique identifier of the experience.
        """
        return pulumi.get(self, "experience_id")

    @experience_id.setter
    def experience_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "experience_id", value)

    @property
    @pulumi.getter(name="indexId")
    def index_id(self) -> Optional[pulumi.Input[str]]:
        """
        The identifier of the index for your Amazon Kendra experience.
        """
        return pulumi.get(self, "index_id")

    @index_id.setter
    def index_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "index_id", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A name for your Amazon Kendra experience.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).

        The following arguments are optional:
        """
        return pulumi.get(self, "role_arn")

    @role_arn.setter
    def role_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "role_arn", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        The current processing status of your Amazon Kendra experience.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)


class Experience(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 configuration: Optional[pulumi.Input[pulumi.InputType['ExperienceConfigurationArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 index_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 role_arn: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource for managing an AWS Kendra Experience.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.kendra.Experience("example",
            index_id=aws_kendra_index["example"]["id"],
            description="My Kendra Experience",
            role_arn=aws_iam_role["example"]["arn"],
            configuration=aws.kendra.ExperienceConfigurationArgs(
                content_source_configuration=aws.kendra.ExperienceConfigurationContentSourceConfigurationArgs(
                    direct_put_content=True,
                    faq_ids=[aws_kendra_faq["example"]["faq_id"]],
                ),
                user_identity_configuration=aws.kendra.ExperienceConfigurationUserIdentityConfigurationArgs(
                    identity_attribute_name="12345ec453-1546651e-79c4-4554-91fa-00b43ccfa245",
                ),
            ))
        ```

        ## Import

        Using `pulumi import`, import Kendra Experience using the unique identifiers of the experience and index separated by a slash (`/`). For example:

        ```sh
         $ pulumi import aws:kendra/experience:Experience example 1045d08d-66ef-4882-b3ed-dfb7df183e90/b34dfdf7-1f2b-4704-9581-79e00296845f
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['ExperienceConfigurationArgs']] configuration: Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        :param pulumi.Input[str] description: A description for your Amazon Kendra experience.
        :param pulumi.Input[str] index_id: The identifier of the index for your Amazon Kendra experience.
        :param pulumi.Input[str] name: A name for your Amazon Kendra experience.
        :param pulumi.Input[str] role_arn: The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).
               
               The following arguments are optional:
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ExperienceArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing an AWS Kendra Experience.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.kendra.Experience("example",
            index_id=aws_kendra_index["example"]["id"],
            description="My Kendra Experience",
            role_arn=aws_iam_role["example"]["arn"],
            configuration=aws.kendra.ExperienceConfigurationArgs(
                content_source_configuration=aws.kendra.ExperienceConfigurationContentSourceConfigurationArgs(
                    direct_put_content=True,
                    faq_ids=[aws_kendra_faq["example"]["faq_id"]],
                ),
                user_identity_configuration=aws.kendra.ExperienceConfigurationUserIdentityConfigurationArgs(
                    identity_attribute_name="12345ec453-1546651e-79c4-4554-91fa-00b43ccfa245",
                ),
            ))
        ```

        ## Import

        Using `pulumi import`, import Kendra Experience using the unique identifiers of the experience and index separated by a slash (`/`). For example:

        ```sh
         $ pulumi import aws:kendra/experience:Experience example 1045d08d-66ef-4882-b3ed-dfb7df183e90/b34dfdf7-1f2b-4704-9581-79e00296845f
        ```

        :param str resource_name: The name of the resource.
        :param ExperienceArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ExperienceArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 configuration: Optional[pulumi.Input[pulumi.InputType['ExperienceConfigurationArgs']]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 index_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 role_arn: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ExperienceArgs.__new__(ExperienceArgs)

            __props__.__dict__["configuration"] = configuration
            __props__.__dict__["description"] = description
            if index_id is None and not opts.urn:
                raise TypeError("Missing required property 'index_id'")
            __props__.__dict__["index_id"] = index_id
            __props__.__dict__["name"] = name
            if role_arn is None and not opts.urn:
                raise TypeError("Missing required property 'role_arn'")
            __props__.__dict__["role_arn"] = role_arn
            __props__.__dict__["arn"] = None
            __props__.__dict__["endpoints"] = None
            __props__.__dict__["experience_id"] = None
            __props__.__dict__["status"] = None
        super(Experience, __self__).__init__(
            'aws:kendra/experience:Experience',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            configuration: Optional[pulumi.Input[pulumi.InputType['ExperienceConfigurationArgs']]] = None,
            description: Optional[pulumi.Input[str]] = None,
            endpoints: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ExperienceEndpointArgs']]]]] = None,
            experience_id: Optional[pulumi.Input[str]] = None,
            index_id: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            role_arn: Optional[pulumi.Input[str]] = None,
            status: Optional[pulumi.Input[str]] = None) -> 'Experience':
        """
        Get an existing Experience resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: ARN of the Experience.
        :param pulumi.Input[pulumi.InputType['ExperienceConfigurationArgs']] configuration: Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        :param pulumi.Input[str] description: A description for your Amazon Kendra experience.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ExperienceEndpointArgs']]]] endpoints: Shows the endpoint URLs for your Amazon Kendra experiences. The URLs are unique and fully hosted by AWS.
        :param pulumi.Input[str] experience_id: The unique identifier of the experience.
        :param pulumi.Input[str] index_id: The identifier of the index for your Amazon Kendra experience.
        :param pulumi.Input[str] name: A name for your Amazon Kendra experience.
        :param pulumi.Input[str] role_arn: The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).
               
               The following arguments are optional:
        :param pulumi.Input[str] status: The current processing status of your Amazon Kendra experience.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ExperienceState.__new__(_ExperienceState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["configuration"] = configuration
        __props__.__dict__["description"] = description
        __props__.__dict__["endpoints"] = endpoints
        __props__.__dict__["experience_id"] = experience_id
        __props__.__dict__["index_id"] = index_id
        __props__.__dict__["name"] = name
        __props__.__dict__["role_arn"] = role_arn
        __props__.__dict__["status"] = status
        return Experience(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        ARN of the Experience.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter
    def configuration(self) -> pulumi.Output['outputs.ExperienceConfiguration']:
        """
        Configuration information for your Amazon Kendra experience. The provider will only perform drift detection of its value when present in a configuration. Detailed below.
        """
        return pulumi.get(self, "configuration")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A description for your Amazon Kendra experience.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def endpoints(self) -> pulumi.Output[Sequence['outputs.ExperienceEndpoint']]:
        """
        Shows the endpoint URLs for your Amazon Kendra experiences. The URLs are unique and fully hosted by AWS.
        """
        return pulumi.get(self, "endpoints")

    @property
    @pulumi.getter(name="experienceId")
    def experience_id(self) -> pulumi.Output[str]:
        """
        The unique identifier of the experience.
        """
        return pulumi.get(self, "experience_id")

    @property
    @pulumi.getter(name="indexId")
    def index_id(self) -> pulumi.Output[str]:
        """
        The identifier of the index for your Amazon Kendra experience.
        """
        return pulumi.get(self, "index_id")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A name for your Amazon Kendra experience.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) of a role with permission to access `Query API`, `QuerySuggestions API`, `SubmitFeedback API`, and `AWS SSO` that stores your user and group information. For more information, see [IAM roles for Amazon Kendra](https://docs.aws.amazon.com/kendra/latest/dg/iam-roles.html).

        The following arguments are optional:
        """
        return pulumi.get(self, "role_arn")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        The current processing status of your Amazon Kendra experience.
        """
        return pulumi.get(self, "status")

