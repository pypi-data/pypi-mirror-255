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

__all__ = ['WorkflowArgs', 'Workflow']

@pulumi.input_type
class WorkflowArgs:
    def __init__(__self__, *,
                 steps: pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]],
                 description: Optional[pulumi.Input[str]] = None,
                 on_exception_steps: Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a Workflow resource.
        :param pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]] steps: Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        :param pulumi.Input[str] description: A textual description for the workflow.
        :param pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]] on_exception_steps: Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "steps", steps)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if on_exception_steps is not None:
            pulumi.set(__self__, "on_exception_steps", on_exception_steps)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def steps(self) -> pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]]:
        """
        Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        """
        return pulumi.get(self, "steps")

    @steps.setter
    def steps(self, value: pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]]):
        pulumi.set(self, "steps", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A textual description for the workflow.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="onExceptionSteps")
    def on_exception_steps(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]]]:
        """
        Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        """
        return pulumi.get(self, "on_exception_steps")

    @on_exception_steps.setter
    def on_exception_steps(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]]]):
        pulumi.set(self, "on_exception_steps", value)

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
class _WorkflowState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 on_exception_steps: Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]]] = None,
                 steps: Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering Workflow resources.
        :param pulumi.Input[str] arn: The Workflow ARN.
        :param pulumi.Input[str] description: A textual description for the workflow.
        :param pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]] on_exception_steps: Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        :param pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]] steps: Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if on_exception_steps is not None:
            pulumi.set(__self__, "on_exception_steps", on_exception_steps)
        if steps is not None:
            pulumi.set(__self__, "steps", steps)
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
        The Workflow ARN.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A textual description for the workflow.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="onExceptionSteps")
    def on_exception_steps(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]]]:
        """
        Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        """
        return pulumi.get(self, "on_exception_steps")

    @on_exception_steps.setter
    def on_exception_steps(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowOnExceptionStepArgs']]]]):
        pulumi.set(self, "on_exception_steps", value)

    @property
    @pulumi.getter
    def steps(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]]]:
        """
        Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        """
        return pulumi.get(self, "steps")

    @steps.setter
    def steps(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['WorkflowStepArgs']]]]):
        pulumi.set(self, "steps", value)

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


class Workflow(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 on_exception_steps: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowOnExceptionStepArgs']]]]] = None,
                 steps: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowStepArgs']]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides a AWS Transfer Workflow resource.

        ## Example Usage
        ### Basic single step example

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.transfer.Workflow("example", steps=[aws.transfer.WorkflowStepArgs(
            delete_step_details=aws.transfer.WorkflowStepDeleteStepDetailsArgs(
                name="example",
                source_file_location="${original.file}",
            ),
            type="DELETE",
        )])
        ```
        ### Multistep example

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.transfer.Workflow("example", steps=[
            aws.transfer.WorkflowStepArgs(
                custom_step_details=aws.transfer.WorkflowStepCustomStepDetailsArgs(
                    name="example",
                    source_file_location="${original.file}",
                    target=aws_lambda_function["example"]["arn"],
                    timeout_seconds=60,
                ),
                type="CUSTOM",
            ),
            aws.transfer.WorkflowStepArgs(
                tag_step_details=aws.transfer.WorkflowStepTagStepDetailsArgs(
                    name="example",
                    source_file_location="${original.file}",
                    tags=[aws.transfer.WorkflowStepTagStepDetailsTagArgs(
                        key="Name",
                        value="Hello World",
                    )],
                ),
                type="TAG",
            ),
        ])
        ```

        ## Import

        Using `pulumi import`, import Transfer Workflows using the `worflow_id`. For example:

        ```sh
         $ pulumi import aws:transfer/workflow:Workflow example example
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] description: A textual description for the workflow.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowOnExceptionStepArgs']]]] on_exception_steps: Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowStepArgs']]]] steps: Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: WorkflowArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a AWS Transfer Workflow resource.

        ## Example Usage
        ### Basic single step example

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.transfer.Workflow("example", steps=[aws.transfer.WorkflowStepArgs(
            delete_step_details=aws.transfer.WorkflowStepDeleteStepDetailsArgs(
                name="example",
                source_file_location="${original.file}",
            ),
            type="DELETE",
        )])
        ```
        ### Multistep example

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.transfer.Workflow("example", steps=[
            aws.transfer.WorkflowStepArgs(
                custom_step_details=aws.transfer.WorkflowStepCustomStepDetailsArgs(
                    name="example",
                    source_file_location="${original.file}",
                    target=aws_lambda_function["example"]["arn"],
                    timeout_seconds=60,
                ),
                type="CUSTOM",
            ),
            aws.transfer.WorkflowStepArgs(
                tag_step_details=aws.transfer.WorkflowStepTagStepDetailsArgs(
                    name="example",
                    source_file_location="${original.file}",
                    tags=[aws.transfer.WorkflowStepTagStepDetailsTagArgs(
                        key="Name",
                        value="Hello World",
                    )],
                ),
                type="TAG",
            ),
        ])
        ```

        ## Import

        Using `pulumi import`, import Transfer Workflows using the `worflow_id`. For example:

        ```sh
         $ pulumi import aws:transfer/workflow:Workflow example example
        ```

        :param str resource_name: The name of the resource.
        :param WorkflowArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(WorkflowArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 on_exception_steps: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowOnExceptionStepArgs']]]]] = None,
                 steps: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowStepArgs']]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = WorkflowArgs.__new__(WorkflowArgs)

            __props__.__dict__["description"] = description
            __props__.__dict__["on_exception_steps"] = on_exception_steps
            if steps is None and not opts.urn:
                raise TypeError("Missing required property 'steps'")
            __props__.__dict__["steps"] = steps
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(Workflow, __self__).__init__(
            'aws:transfer/workflow:Workflow',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            on_exception_steps: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowOnExceptionStepArgs']]]]] = None,
            steps: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowStepArgs']]]]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'Workflow':
        """
        Get an existing Workflow resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Workflow ARN.
        :param pulumi.Input[str] description: A textual description for the workflow.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowOnExceptionStepArgs']]]] on_exception_steps: Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['WorkflowStepArgs']]]] steps: Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _WorkflowState.__new__(_WorkflowState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["description"] = description
        __props__.__dict__["on_exception_steps"] = on_exception_steps
        __props__.__dict__["steps"] = steps
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return Workflow(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Workflow ARN.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A textual description for the workflow.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="onExceptionSteps")
    def on_exception_steps(self) -> pulumi.Output[Optional[Sequence['outputs.WorkflowOnExceptionStep']]]:
        """
        Specifies the steps (actions) to take if errors are encountered during execution of the workflow. See Workflow Steps below.
        """
        return pulumi.get(self, "on_exception_steps")

    @property
    @pulumi.getter
    def steps(self) -> pulumi.Output[Sequence['outputs.WorkflowStep']]:
        """
        Specifies the details for the steps that are in the specified workflow. See Workflow Steps below.
        """
        return pulumi.get(self, "steps")

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

