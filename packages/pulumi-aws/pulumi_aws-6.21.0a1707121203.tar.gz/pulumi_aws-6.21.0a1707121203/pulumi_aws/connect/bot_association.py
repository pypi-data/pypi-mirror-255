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

__all__ = ['BotAssociationArgs', 'BotAssociation']

@pulumi.input_type
class BotAssociationArgs:
    def __init__(__self__, *,
                 instance_id: pulumi.Input[str],
                 lex_bot: pulumi.Input['BotAssociationLexBotArgs']):
        """
        The set of arguments for constructing a BotAssociation resource.
        :param pulumi.Input[str] instance_id: The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        :param pulumi.Input['BotAssociationLexBotArgs'] lex_bot: Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        pulumi.set(__self__, "instance_id", instance_id)
        pulumi.set(__self__, "lex_bot", lex_bot)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> pulumi.Input[str]:
        """
        The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        """
        return pulumi.get(self, "instance_id")

    @instance_id.setter
    def instance_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "instance_id", value)

    @property
    @pulumi.getter(name="lexBot")
    def lex_bot(self) -> pulumi.Input['BotAssociationLexBotArgs']:
        """
        Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        return pulumi.get(self, "lex_bot")

    @lex_bot.setter
    def lex_bot(self, value: pulumi.Input['BotAssociationLexBotArgs']):
        pulumi.set(self, "lex_bot", value)


@pulumi.input_type
class _BotAssociationState:
    def __init__(__self__, *,
                 instance_id: Optional[pulumi.Input[str]] = None,
                 lex_bot: Optional[pulumi.Input['BotAssociationLexBotArgs']] = None):
        """
        Input properties used for looking up and filtering BotAssociation resources.
        :param pulumi.Input[str] instance_id: The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        :param pulumi.Input['BotAssociationLexBotArgs'] lex_bot: Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        if instance_id is not None:
            pulumi.set(__self__, "instance_id", instance_id)
        if lex_bot is not None:
            pulumi.set(__self__, "lex_bot", lex_bot)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> Optional[pulumi.Input[str]]:
        """
        The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        """
        return pulumi.get(self, "instance_id")

    @instance_id.setter
    def instance_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "instance_id", value)

    @property
    @pulumi.getter(name="lexBot")
    def lex_bot(self) -> Optional[pulumi.Input['BotAssociationLexBotArgs']]:
        """
        Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        return pulumi.get(self, "lex_bot")

    @lex_bot.setter
    def lex_bot(self, value: Optional[pulumi.Input['BotAssociationLexBotArgs']]):
        pulumi.set(self, "lex_bot", value)


class BotAssociation(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
                 lex_bot: Optional[pulumi.Input[pulumi.InputType['BotAssociationLexBotArgs']]] = None,
                 __props__=None):
        """
        Allows the specified Amazon Connect instance to access the specified Amazon Lex (V1) bot. For more information see
        [Amazon Connect: Getting Started](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-get-started.html) and [Add an Amazon Lex bot](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-lex.html).

        > **NOTE:** This resource only currently supports Amazon Lex (V1) Associations.

        ## Example Usage
        ### Basic

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.connect.BotAssociation("example",
            instance_id=aws_connect_instance["example"]["id"],
            lex_bot=aws.connect.BotAssociationLexBotArgs(
                lex_region="us-west-2",
                name="Test",
            ))
        ```
        ### Including a sample Lex bot

        ```python
        import pulumi
        import pulumi_aws as aws

        current = aws.get_region()
        example_intent = aws.lex.Intent("exampleIntent",
            create_version=True,
            name="connect_lex_intent",
            fulfillment_activity=aws.lex.IntentFulfillmentActivityArgs(
                type="ReturnIntent",
            ),
            sample_utterances=["I would like to pick up flowers."])
        example_bot = aws.lex.Bot("exampleBot",
            abort_statement=aws.lex.BotAbortStatementArgs(
                messages=[aws.lex.BotAbortStatementMessageArgs(
                    content="Sorry, I am not able to assist at this time.",
                    content_type="PlainText",
                )],
            ),
            clarification_prompt=aws.lex.BotClarificationPromptArgs(
                max_attempts=2,
                messages=[aws.lex.BotClarificationPromptMessageArgs(
                    content="I didn't understand you, what would you like to do?",
                    content_type="PlainText",
                )],
            ),
            intents=[aws.lex.BotIntentArgs(
                intent_name=example_intent.name,
                intent_version="1",
            )],
            child_directed=False,
            name="connect_lex_bot",
            process_behavior="BUILD")
        example_bot_association = aws.connect.BotAssociation("exampleBotAssociation",
            instance_id=aws_connect_instance["example"]["id"],
            lex_bot=aws.connect.BotAssociationLexBotArgs(
                lex_region=current.name,
                name=example_bot.name,
            ))
        ```

        ## Import

        Using `pulumi import`, import `aws_connect_bot_association` using the Amazon Connect instance ID, Lex (V1) bot name, and Lex (V1) bot region separated by colons (`:`). For example:

        ```sh
         $ pulumi import aws:connect/botAssociation:BotAssociation example aaaaaaaa-bbbb-cccc-dddd-111111111111:Example:us-west-2
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] instance_id: The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        :param pulumi.Input[pulumi.InputType['BotAssociationLexBotArgs']] lex_bot: Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: BotAssociationArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Allows the specified Amazon Connect instance to access the specified Amazon Lex (V1) bot. For more information see
        [Amazon Connect: Getting Started](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-connect-get-started.html) and [Add an Amazon Lex bot](https://docs.aws.amazon.com/connect/latest/adminguide/amazon-lex.html).

        > **NOTE:** This resource only currently supports Amazon Lex (V1) Associations.

        ## Example Usage
        ### Basic

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.connect.BotAssociation("example",
            instance_id=aws_connect_instance["example"]["id"],
            lex_bot=aws.connect.BotAssociationLexBotArgs(
                lex_region="us-west-2",
                name="Test",
            ))
        ```
        ### Including a sample Lex bot

        ```python
        import pulumi
        import pulumi_aws as aws

        current = aws.get_region()
        example_intent = aws.lex.Intent("exampleIntent",
            create_version=True,
            name="connect_lex_intent",
            fulfillment_activity=aws.lex.IntentFulfillmentActivityArgs(
                type="ReturnIntent",
            ),
            sample_utterances=["I would like to pick up flowers."])
        example_bot = aws.lex.Bot("exampleBot",
            abort_statement=aws.lex.BotAbortStatementArgs(
                messages=[aws.lex.BotAbortStatementMessageArgs(
                    content="Sorry, I am not able to assist at this time.",
                    content_type="PlainText",
                )],
            ),
            clarification_prompt=aws.lex.BotClarificationPromptArgs(
                max_attempts=2,
                messages=[aws.lex.BotClarificationPromptMessageArgs(
                    content="I didn't understand you, what would you like to do?",
                    content_type="PlainText",
                )],
            ),
            intents=[aws.lex.BotIntentArgs(
                intent_name=example_intent.name,
                intent_version="1",
            )],
            child_directed=False,
            name="connect_lex_bot",
            process_behavior="BUILD")
        example_bot_association = aws.connect.BotAssociation("exampleBotAssociation",
            instance_id=aws_connect_instance["example"]["id"],
            lex_bot=aws.connect.BotAssociationLexBotArgs(
                lex_region=current.name,
                name=example_bot.name,
            ))
        ```

        ## Import

        Using `pulumi import`, import `aws_connect_bot_association` using the Amazon Connect instance ID, Lex (V1) bot name, and Lex (V1) bot region separated by colons (`:`). For example:

        ```sh
         $ pulumi import aws:connect/botAssociation:BotAssociation example aaaaaaaa-bbbb-cccc-dddd-111111111111:Example:us-west-2
        ```

        :param str resource_name: The name of the resource.
        :param BotAssociationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(BotAssociationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 instance_id: Optional[pulumi.Input[str]] = None,
                 lex_bot: Optional[pulumi.Input[pulumi.InputType['BotAssociationLexBotArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = BotAssociationArgs.__new__(BotAssociationArgs)

            if instance_id is None and not opts.urn:
                raise TypeError("Missing required property 'instance_id'")
            __props__.__dict__["instance_id"] = instance_id
            if lex_bot is None and not opts.urn:
                raise TypeError("Missing required property 'lex_bot'")
            __props__.__dict__["lex_bot"] = lex_bot
        super(BotAssociation, __self__).__init__(
            'aws:connect/botAssociation:BotAssociation',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            instance_id: Optional[pulumi.Input[str]] = None,
            lex_bot: Optional[pulumi.Input[pulumi.InputType['BotAssociationLexBotArgs']]] = None) -> 'BotAssociation':
        """
        Get an existing BotAssociation resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] instance_id: The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        :param pulumi.Input[pulumi.InputType['BotAssociationLexBotArgs']] lex_bot: Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _BotAssociationState.__new__(_BotAssociationState)

        __props__.__dict__["instance_id"] = instance_id
        __props__.__dict__["lex_bot"] = lex_bot
        return BotAssociation(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="instanceId")
    def instance_id(self) -> pulumi.Output[str]:
        """
        The identifier of the Amazon Connect instance. You can find the instanceId in the ARN of the instance.
        """
        return pulumi.get(self, "instance_id")

    @property
    @pulumi.getter(name="lexBot")
    def lex_bot(self) -> pulumi.Output['outputs.BotAssociationLexBot']:
        """
        Configuration information of an Amazon Lex (V1) bot. Detailed below.
        """
        return pulumi.get(self, "lex_bot")

