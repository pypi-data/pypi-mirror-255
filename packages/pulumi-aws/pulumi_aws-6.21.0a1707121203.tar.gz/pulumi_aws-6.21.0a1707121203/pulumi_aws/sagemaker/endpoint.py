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

__all__ = ['EndpointArgs', 'Endpoint']

@pulumi.input_type
class EndpointArgs:
    def __init__(__self__, *,
                 endpoint_config_name: pulumi.Input[str],
                 deployment_config: Optional[pulumi.Input['EndpointDeploymentConfigArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a Endpoint resource.
        :param pulumi.Input[str] endpoint_config_name: The name of the endpoint configuration to use.
        :param pulumi.Input['EndpointDeploymentConfigArgs'] deployment_config: The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        :param pulumi.Input[str] name: The name of the endpoint. If omitted, the provider will assign a random, unique name.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "endpoint_config_name", endpoint_config_name)
        if deployment_config is not None:
            pulumi.set(__self__, "deployment_config", deployment_config)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="endpointConfigName")
    def endpoint_config_name(self) -> pulumi.Input[str]:
        """
        The name of the endpoint configuration to use.
        """
        return pulumi.get(self, "endpoint_config_name")

    @endpoint_config_name.setter
    def endpoint_config_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "endpoint_config_name", value)

    @property
    @pulumi.getter(name="deploymentConfig")
    def deployment_config(self) -> Optional[pulumi.Input['EndpointDeploymentConfigArgs']]:
        """
        The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        """
        return pulumi.get(self, "deployment_config")

    @deployment_config.setter
    def deployment_config(self, value: Optional[pulumi.Input['EndpointDeploymentConfigArgs']]):
        pulumi.set(self, "deployment_config", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the endpoint. If omitted, the provider will assign a random, unique name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

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


@pulumi.input_type
class _EndpointState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 deployment_config: Optional[pulumi.Input['EndpointDeploymentConfigArgs']] = None,
                 endpoint_config_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering Endpoint resources.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) assigned by AWS to this endpoint.
        :param pulumi.Input['EndpointDeploymentConfigArgs'] deployment_config: The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        :param pulumi.Input[str] endpoint_config_name: The name of the endpoint configuration to use.
        :param pulumi.Input[str] name: The name of the endpoint. If omitted, the provider will assign a random, unique name.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if deployment_config is not None:
            pulumi.set(__self__, "deployment_config", deployment_config)
        if endpoint_config_name is not None:
            pulumi.set(__self__, "endpoint_config_name", endpoint_config_name)
        if name is not None:
            pulumi.set(__self__, "name", name)
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
        The Amazon Resource Name (ARN) assigned by AWS to this endpoint.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="deploymentConfig")
    def deployment_config(self) -> Optional[pulumi.Input['EndpointDeploymentConfigArgs']]:
        """
        The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        """
        return pulumi.get(self, "deployment_config")

    @deployment_config.setter
    def deployment_config(self, value: Optional[pulumi.Input['EndpointDeploymentConfigArgs']]):
        pulumi.set(self, "deployment_config", value)

    @property
    @pulumi.getter(name="endpointConfigName")
    def endpoint_config_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the endpoint configuration to use.
        """
        return pulumi.get(self, "endpoint_config_name")

    @endpoint_config_name.setter
    def endpoint_config_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "endpoint_config_name", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the endpoint. If omitted, the provider will assign a random, unique name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

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


class Endpoint(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 deployment_config: Optional[pulumi.Input[pulumi.InputType['EndpointDeploymentConfigArgs']]] = None,
                 endpoint_config_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides a SageMaker Endpoint resource.

        ## Example Usage

        Basic usage:

        ```python
        import pulumi
        import pulumi_aws as aws

        endpoint = aws.sagemaker.Endpoint("endpoint",
            endpoint_config_name=aws_sagemaker_endpoint_configuration["ec"]["name"],
            tags={
                "Name": "foo",
            })
        ```

        ## Import

        Using `pulumi import`, import endpoints using the `name`. For example:

        ```sh
         $ pulumi import aws:sagemaker/endpoint:Endpoint test_endpoint my-endpoint
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['EndpointDeploymentConfigArgs']] deployment_config: The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        :param pulumi.Input[str] endpoint_config_name: The name of the endpoint configuration to use.
        :param pulumi.Input[str] name: The name of the endpoint. If omitted, the provider will assign a random, unique name.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: EndpointArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a SageMaker Endpoint resource.

        ## Example Usage

        Basic usage:

        ```python
        import pulumi
        import pulumi_aws as aws

        endpoint = aws.sagemaker.Endpoint("endpoint",
            endpoint_config_name=aws_sagemaker_endpoint_configuration["ec"]["name"],
            tags={
                "Name": "foo",
            })
        ```

        ## Import

        Using `pulumi import`, import endpoints using the `name`. For example:

        ```sh
         $ pulumi import aws:sagemaker/endpoint:Endpoint test_endpoint my-endpoint
        ```

        :param str resource_name: The name of the resource.
        :param EndpointArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(EndpointArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 deployment_config: Optional[pulumi.Input[pulumi.InputType['EndpointDeploymentConfigArgs']]] = None,
                 endpoint_config_name: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = EndpointArgs.__new__(EndpointArgs)

            __props__.__dict__["deployment_config"] = deployment_config
            if endpoint_config_name is None and not opts.urn:
                raise TypeError("Missing required property 'endpoint_config_name'")
            __props__.__dict__["endpoint_config_name"] = endpoint_config_name
            __props__.__dict__["name"] = name
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(Endpoint, __self__).__init__(
            'aws:sagemaker/endpoint:Endpoint',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            deployment_config: Optional[pulumi.Input[pulumi.InputType['EndpointDeploymentConfigArgs']]] = None,
            endpoint_config_name: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'Endpoint':
        """
        Get an existing Endpoint resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) assigned by AWS to this endpoint.
        :param pulumi.Input[pulumi.InputType['EndpointDeploymentConfigArgs']] deployment_config: The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        :param pulumi.Input[str] endpoint_config_name: The name of the endpoint configuration to use.
        :param pulumi.Input[str] name: The name of the endpoint. If omitted, the provider will assign a random, unique name.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _EndpointState.__new__(_EndpointState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["deployment_config"] = deployment_config
        __props__.__dict__["endpoint_config_name"] = endpoint_config_name
        __props__.__dict__["name"] = name
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return Endpoint(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) assigned by AWS to this endpoint.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="deploymentConfig")
    def deployment_config(self) -> pulumi.Output[Optional['outputs.EndpointDeploymentConfig']]:
        """
        The deployment configuration for an endpoint, which contains the desired deployment strategy and rollback configurations. See Deployment Config.
        """
        return pulumi.get(self, "deployment_config")

    @property
    @pulumi.getter(name="endpointConfigName")
    def endpoint_config_name(self) -> pulumi.Output[str]:
        """
        The name of the endpoint configuration to use.
        """
        return pulumi.get(self, "endpoint_config_name")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the endpoint. If omitted, the provider will assign a random, unique name.
        """
        return pulumi.get(self, "name")

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

