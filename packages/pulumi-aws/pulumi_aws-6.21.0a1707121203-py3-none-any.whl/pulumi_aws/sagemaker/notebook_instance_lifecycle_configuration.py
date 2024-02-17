# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['NotebookInstanceLifecycleConfigurationArgs', 'NotebookInstanceLifecycleConfiguration']

@pulumi.input_type
class NotebookInstanceLifecycleConfigurationArgs:
    def __init__(__self__, *,
                 name: Optional[pulumi.Input[str]] = None,
                 on_create: Optional[pulumi.Input[str]] = None,
                 on_start: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a NotebookInstanceLifecycleConfiguration resource.
        :param pulumi.Input[str] name: The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        :param pulumi.Input[str] on_create: A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        :param pulumi.Input[str] on_start: A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        if name is not None:
            pulumi.set(__self__, "name", name)
        if on_create is not None:
            pulumi.set(__self__, "on_create", on_create)
        if on_start is not None:
            pulumi.set(__self__, "on_start", on_start)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="onCreate")
    def on_create(self) -> Optional[pulumi.Input[str]]:
        """
        A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        """
        return pulumi.get(self, "on_create")

    @on_create.setter
    def on_create(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "on_create", value)

    @property
    @pulumi.getter(name="onStart")
    def on_start(self) -> Optional[pulumi.Input[str]]:
        """
        A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        return pulumi.get(self, "on_start")

    @on_start.setter
    def on_start(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "on_start", value)


@pulumi.input_type
class _NotebookInstanceLifecycleConfigurationState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 on_create: Optional[pulumi.Input[str]] = None,
                 on_start: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering NotebookInstanceLifecycleConfiguration resources.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) assigned by AWS to this lifecycle configuration.
        :param pulumi.Input[str] name: The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        :param pulumi.Input[str] on_create: A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        :param pulumi.Input[str] on_start: A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if on_create is not None:
            pulumi.set(__self__, "on_create", on_create)
        if on_start is not None:
            pulumi.set(__self__, "on_start", on_start)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) assigned by AWS to this lifecycle configuration.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="onCreate")
    def on_create(self) -> Optional[pulumi.Input[str]]:
        """
        A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        """
        return pulumi.get(self, "on_create")

    @on_create.setter
    def on_create(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "on_create", value)

    @property
    @pulumi.getter(name="onStart")
    def on_start(self) -> Optional[pulumi.Input[str]]:
        """
        A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        return pulumi.get(self, "on_start")

    @on_start.setter
    def on_start(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "on_start", value)


class NotebookInstanceLifecycleConfiguration(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 on_create: Optional[pulumi.Input[str]] = None,
                 on_start: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a lifecycle configuration for SageMaker Notebook Instances.

        ## Import

        Using `pulumi import`, import models using the `name`. For example:

        ```sh
         $ pulumi import aws:sagemaker/notebookInstanceLifecycleConfiguration:NotebookInstanceLifecycleConfiguration lc foo
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] name: The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        :param pulumi.Input[str] on_create: A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        :param pulumi.Input[str] on_start: A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[NotebookInstanceLifecycleConfigurationArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a lifecycle configuration for SageMaker Notebook Instances.

        ## Import

        Using `pulumi import`, import models using the `name`. For example:

        ```sh
         $ pulumi import aws:sagemaker/notebookInstanceLifecycleConfiguration:NotebookInstanceLifecycleConfiguration lc foo
        ```

        :param str resource_name: The name of the resource.
        :param NotebookInstanceLifecycleConfigurationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(NotebookInstanceLifecycleConfigurationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 on_create: Optional[pulumi.Input[str]] = None,
                 on_start: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = NotebookInstanceLifecycleConfigurationArgs.__new__(NotebookInstanceLifecycleConfigurationArgs)

            __props__.__dict__["name"] = name
            __props__.__dict__["on_create"] = on_create
            __props__.__dict__["on_start"] = on_start
            __props__.__dict__["arn"] = None
        super(NotebookInstanceLifecycleConfiguration, __self__).__init__(
            'aws:sagemaker/notebookInstanceLifecycleConfiguration:NotebookInstanceLifecycleConfiguration',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            on_create: Optional[pulumi.Input[str]] = None,
            on_start: Optional[pulumi.Input[str]] = None) -> 'NotebookInstanceLifecycleConfiguration':
        """
        Get an existing NotebookInstanceLifecycleConfiguration resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) assigned by AWS to this lifecycle configuration.
        :param pulumi.Input[str] name: The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        :param pulumi.Input[str] on_create: A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        :param pulumi.Input[str] on_start: A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _NotebookInstanceLifecycleConfigurationState.__new__(_NotebookInstanceLifecycleConfigurationState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["name"] = name
        __props__.__dict__["on_create"] = on_create
        __props__.__dict__["on_start"] = on_start
        return NotebookInstanceLifecycleConfiguration(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) assigned by AWS to this lifecycle configuration.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the lifecycle configuration (must be unique). If omitted, this provider will assign a random, unique name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="onCreate")
    def on_create(self) -> pulumi.Output[Optional[str]]:
        """
        A shell script (base64-encoded) that runs only once when the SageMaker Notebook Instance is created.
        """
        return pulumi.get(self, "on_create")

    @property
    @pulumi.getter(name="onStart")
    def on_start(self) -> pulumi.Output[Optional[str]]:
        """
        A shell script (base64-encoded) that runs every time the SageMaker Notebook Instance is started including the time it's created.
        """
        return pulumi.get(self, "on_start")

