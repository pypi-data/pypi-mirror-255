# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['CloudFormationStackArgs', 'CloudFormationStack']

@pulumi.input_type
class CloudFormationStackArgs:
    def __init__(__self__, *,
                 application_id: pulumi.Input[str],
                 capabilities: pulumi.Input[Sequence[pulumi.Input[str]]],
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 semantic_version: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a CloudFormationStack resource.
        :param pulumi.Input[str] application_id: The ARN of the application from the Serverless Application Repository.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] capabilities: A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        :param pulumi.Input[str] name: The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of Parameter structures that specify input parameters for the stack.
        :param pulumi.Input[str] semantic_version: The version of the application to deploy. If not supplied, deploys the latest version.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "application_id", application_id)
        pulumi.set(__self__, "capabilities", capabilities)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if parameters is not None:
            pulumi.set(__self__, "parameters", parameters)
        if semantic_version is not None:
            pulumi.set(__self__, "semantic_version", semantic_version)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="applicationId")
    def application_id(self) -> pulumi.Input[str]:
        """
        The ARN of the application from the Serverless Application Repository.
        """
        return pulumi.get(self, "application_id")

    @application_id.setter
    def application_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "application_id", value)

    @property
    @pulumi.getter
    def capabilities(self) -> pulumi.Input[Sequence[pulumi.Input[str]]]:
        """
        A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        """
        return pulumi.get(self, "capabilities")

    @capabilities.setter
    def capabilities(self, value: pulumi.Input[Sequence[pulumi.Input[str]]]):
        pulumi.set(self, "capabilities", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def parameters(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of Parameter structures that specify input parameters for the stack.
        """
        return pulumi.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameters", value)

    @property
    @pulumi.getter(name="semanticVersion")
    def semantic_version(self) -> Optional[pulumi.Input[str]]:
        """
        The version of the application to deploy. If not supplied, deploys the latest version.
        """
        return pulumi.get(self, "semantic_version")

    @semantic_version.setter
    def semantic_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "semantic_version", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _CloudFormationStackState:
    def __init__(__self__, *,
                 application_id: Optional[pulumi.Input[str]] = None,
                 capabilities: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 outputs: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 semantic_version: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering CloudFormationStack resources.
        :param pulumi.Input[str] application_id: The ARN of the application from the Serverless Application Repository.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] capabilities: A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        :param pulumi.Input[str] name: The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] outputs: A map of outputs from the stack.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of Parameter structures that specify input parameters for the stack.
        :param pulumi.Input[str] semantic_version: The version of the application to deploy. If not supplied, deploys the latest version.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if application_id is not None:
            pulumi.set(__self__, "application_id", application_id)
        if capabilities is not None:
            pulumi.set(__self__, "capabilities", capabilities)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if outputs is not None:
            pulumi.set(__self__, "outputs", outputs)
        if parameters is not None:
            pulumi.set(__self__, "parameters", parameters)
        if semantic_version is not None:
            pulumi.set(__self__, "semantic_version", semantic_version)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)

    @property
    @pulumi.getter(name="applicationId")
    def application_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the application from the Serverless Application Repository.
        """
        return pulumi.get(self, "application_id")

    @application_id.setter
    def application_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "application_id", value)

    @property
    @pulumi.getter
    def capabilities(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        """
        return pulumi.get(self, "capabilities")

    @capabilities.setter
    def capabilities(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "capabilities", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def outputs(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of outputs from the stack.
        """
        return pulumi.get(self, "outputs")

    @outputs.setter
    def outputs(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "outputs", value)

    @property
    @pulumi.getter
    def parameters(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of Parameter structures that specify input parameters for the stack.
        """
        return pulumi.get(self, "parameters")

    @parameters.setter
    def parameters(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "parameters", value)

    @property
    @pulumi.getter(name="semanticVersion")
    def semantic_version(self) -> Optional[pulumi.Input[str]]:
        """
        The version of the application to deploy. If not supplied, deploys the latest version.
        """
        return pulumi.get(self, "semantic_version")

    @semantic_version.setter
    def semantic_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "semantic_version", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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


class CloudFormationStack(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 application_id: Optional[pulumi.Input[str]] = None,
                 capabilities: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 semantic_version: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Deploys an Application CloudFormation Stack from the Serverless Application Repository.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        current_partition = aws.get_partition()
        current_region = aws.get_region()
        postgres_rotator = aws.serverlessrepository.CloudFormationStack("postgres-rotator",
            application_id="arn:aws:serverlessrepo:us-east-1:297356227824:applications/SecretsManagerRDSPostgreSQLRotationSingleUser",
            capabilities=[
                "CAPABILITY_IAM",
                "CAPABILITY_RESOURCE_POLICY",
            ],
            parameters={
                "endpoint": f"secretsmanager.{current_region.name}.{current_partition.dns_suffix}",
                "functionName": "func-postgres-rotator",
            })
        ```

        ## Import

        Using `pulumi import`, import Serverless Application Repository Stack using the CloudFormation Stack name (with or without the `serverlessrepo-` prefix) or the CloudFormation Stack ID. For example:

        ```sh
         $ pulumi import aws:serverlessrepository/cloudFormationStack:CloudFormationStack example serverlessrepo-postgres-rotator
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] application_id: The ARN of the application from the Serverless Application Repository.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] capabilities: A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        :param pulumi.Input[str] name: The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of Parameter structures that specify input parameters for the stack.
        :param pulumi.Input[str] semantic_version: The version of the application to deploy. If not supplied, deploys the latest version.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: CloudFormationStackArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Deploys an Application CloudFormation Stack from the Serverless Application Repository.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        current_partition = aws.get_partition()
        current_region = aws.get_region()
        postgres_rotator = aws.serverlessrepository.CloudFormationStack("postgres-rotator",
            application_id="arn:aws:serverlessrepo:us-east-1:297356227824:applications/SecretsManagerRDSPostgreSQLRotationSingleUser",
            capabilities=[
                "CAPABILITY_IAM",
                "CAPABILITY_RESOURCE_POLICY",
            ],
            parameters={
                "endpoint": f"secretsmanager.{current_region.name}.{current_partition.dns_suffix}",
                "functionName": "func-postgres-rotator",
            })
        ```

        ## Import

        Using `pulumi import`, import Serverless Application Repository Stack using the CloudFormation Stack name (with or without the `serverlessrepo-` prefix) or the CloudFormation Stack ID. For example:

        ```sh
         $ pulumi import aws:serverlessrepository/cloudFormationStack:CloudFormationStack example serverlessrepo-postgres-rotator
        ```

        :param str resource_name: The name of the resource.
        :param CloudFormationStackArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(CloudFormationStackArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 application_id: Optional[pulumi.Input[str]] = None,
                 capabilities: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 semantic_version: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = CloudFormationStackArgs.__new__(CloudFormationStackArgs)

            if application_id is None and not opts.urn:
                raise TypeError("Missing required property 'application_id'")
            __props__.__dict__["application_id"] = application_id
            if capabilities is None and not opts.urn:
                raise TypeError("Missing required property 'capabilities'")
            __props__.__dict__["capabilities"] = capabilities
            __props__.__dict__["name"] = name
            __props__.__dict__["parameters"] = parameters
            __props__.__dict__["semantic_version"] = semantic_version
            __props__.__dict__["tags"] = tags
            __props__.__dict__["outputs"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(CloudFormationStack, __self__).__init__(
            'aws:serverlessrepository/cloudFormationStack:CloudFormationStack',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            application_id: Optional[pulumi.Input[str]] = None,
            capabilities: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            name: Optional[pulumi.Input[str]] = None,
            outputs: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            parameters: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            semantic_version: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'CloudFormationStack':
        """
        Get an existing CloudFormationStack resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] application_id: The ARN of the application from the Serverless Application Repository.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] capabilities: A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        :param pulumi.Input[str] name: The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] outputs: A map of outputs from the stack.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] parameters: A map of Parameter structures that specify input parameters for the stack.
        :param pulumi.Input[str] semantic_version: The version of the application to deploy. If not supplied, deploys the latest version.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _CloudFormationStackState.__new__(_CloudFormationStackState)

        __props__.__dict__["application_id"] = application_id
        __props__.__dict__["capabilities"] = capabilities
        __props__.__dict__["name"] = name
        __props__.__dict__["outputs"] = outputs
        __props__.__dict__["parameters"] = parameters
        __props__.__dict__["semantic_version"] = semantic_version
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return CloudFormationStack(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="applicationId")
    def application_id(self) -> pulumi.Output[str]:
        """
        The ARN of the application from the Serverless Application Repository.
        """
        return pulumi.get(self, "application_id")

    @property
    @pulumi.getter
    def capabilities(self) -> pulumi.Output[Sequence[str]]:
        """
        A list of capabilities. Valid values are `CAPABILITY_IAM`, `CAPABILITY_NAMED_IAM`, `CAPABILITY_RESOURCE_POLICY`, or `CAPABILITY_AUTO_EXPAND`
        """
        return pulumi.get(self, "capabilities")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the stack to create. The resource deployed in AWS will be prefixed with `serverlessrepo-`
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def outputs(self) -> pulumi.Output[Mapping[str, str]]:
        """
        A map of outputs from the stack.
        """
        return pulumi.get(self, "outputs")

    @property
    @pulumi.getter
    def parameters(self) -> pulumi.Output[Mapping[str, str]]:
        """
        A map of Parameter structures that specify input parameters for the stack.
        """
        return pulumi.get(self, "parameters")

    @property
    @pulumi.getter(name="semanticVersion")
    def semantic_version(self) -> pulumi.Output[str]:
        """
        The version of the application to deploy. If not supplied, deploys the latest version.
        """
        return pulumi.get(self, "semantic_version")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A list of tags to associate with this stack. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

