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

__all__ = ['V2modelsBotLocaleArgs', 'V2modelsBotLocale']

@pulumi.input_type
class V2modelsBotLocaleArgs:
    def __init__(__self__, *,
                 bot_id: pulumi.Input[str],
                 bot_version: pulumi.Input[str],
                 locale_id: pulumi.Input[str],
                 n_lu_intent_confidence_threshold: pulumi.Input[float],
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 timeouts: Optional[pulumi.Input['V2modelsBotLocaleTimeoutsArgs']] = None,
                 voice_settings: Optional[pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs']] = None):
        """
        The set of arguments for constructing a V2modelsBotLocale resource.
        :param pulumi.Input[str] bot_id: Identifier of the bot to create the locale for.
        :param pulumi.Input[str] bot_version: Version of the bot to create the locale for. This can only be the draft version of the bot.
        :param pulumi.Input[str] locale_id: Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        :param pulumi.Input[float] n_lu_intent_confidence_threshold: Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.
               
               The following arguments are optional:
        :param pulumi.Input[str] description: Description of the bot locale. Use this to help identify the bot locale in lists.
        :param pulumi.Input[str] name: Specified locale name.
        :param pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs'] voice_settings: Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        pulumi.set(__self__, "bot_id", bot_id)
        pulumi.set(__self__, "bot_version", bot_version)
        pulumi.set(__self__, "locale_id", locale_id)
        pulumi.set(__self__, "n_lu_intent_confidence_threshold", n_lu_intent_confidence_threshold)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if timeouts is not None:
            pulumi.set(__self__, "timeouts", timeouts)
        if voice_settings is not None:
            pulumi.set(__self__, "voice_settings", voice_settings)

    @property
    @pulumi.getter(name="botId")
    def bot_id(self) -> pulumi.Input[str]:
        """
        Identifier of the bot to create the locale for.
        """
        return pulumi.get(self, "bot_id")

    @bot_id.setter
    def bot_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "bot_id", value)

    @property
    @pulumi.getter(name="botVersion")
    def bot_version(self) -> pulumi.Input[str]:
        """
        Version of the bot to create the locale for. This can only be the draft version of the bot.
        """
        return pulumi.get(self, "bot_version")

    @bot_version.setter
    def bot_version(self, value: pulumi.Input[str]):
        pulumi.set(self, "bot_version", value)

    @property
    @pulumi.getter(name="localeId")
    def locale_id(self) -> pulumi.Input[str]:
        """
        Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        """
        return pulumi.get(self, "locale_id")

    @locale_id.setter
    def locale_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "locale_id", value)

    @property
    @pulumi.getter(name="nLuIntentConfidenceThreshold")
    def n_lu_intent_confidence_threshold(self) -> pulumi.Input[float]:
        """
        Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.

        The following arguments are optional:
        """
        return pulumi.get(self, "n_lu_intent_confidence_threshold")

    @n_lu_intent_confidence_threshold.setter
    def n_lu_intent_confidence_threshold(self, value: pulumi.Input[float]):
        pulumi.set(self, "n_lu_intent_confidence_threshold", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of the bot locale. Use this to help identify the bot locale in lists.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specified locale name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def timeouts(self) -> Optional[pulumi.Input['V2modelsBotLocaleTimeoutsArgs']]:
        return pulumi.get(self, "timeouts")

    @timeouts.setter
    def timeouts(self, value: Optional[pulumi.Input['V2modelsBotLocaleTimeoutsArgs']]):
        pulumi.set(self, "timeouts", value)

    @property
    @pulumi.getter(name="voiceSettings")
    def voice_settings(self) -> Optional[pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs']]:
        """
        Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        return pulumi.get(self, "voice_settings")

    @voice_settings.setter
    def voice_settings(self, value: Optional[pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs']]):
        pulumi.set(self, "voice_settings", value)


@pulumi.input_type
class _V2modelsBotLocaleState:
    def __init__(__self__, *,
                 bot_id: Optional[pulumi.Input[str]] = None,
                 bot_version: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 locale_id: Optional[pulumi.Input[str]] = None,
                 n_lu_intent_confidence_threshold: Optional[pulumi.Input[float]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 timeouts: Optional[pulumi.Input['V2modelsBotLocaleTimeoutsArgs']] = None,
                 voice_settings: Optional[pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs']] = None):
        """
        Input properties used for looking up and filtering V2modelsBotLocale resources.
        :param pulumi.Input[str] bot_id: Identifier of the bot to create the locale for.
        :param pulumi.Input[str] bot_version: Version of the bot to create the locale for. This can only be the draft version of the bot.
        :param pulumi.Input[str] description: Description of the bot locale. Use this to help identify the bot locale in lists.
        :param pulumi.Input[str] locale_id: Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        :param pulumi.Input[float] n_lu_intent_confidence_threshold: Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.
               
               The following arguments are optional:
        :param pulumi.Input[str] name: Specified locale name.
        :param pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs'] voice_settings: Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        if bot_id is not None:
            pulumi.set(__self__, "bot_id", bot_id)
        if bot_version is not None:
            pulumi.set(__self__, "bot_version", bot_version)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if locale_id is not None:
            pulumi.set(__self__, "locale_id", locale_id)
        if n_lu_intent_confidence_threshold is not None:
            pulumi.set(__self__, "n_lu_intent_confidence_threshold", n_lu_intent_confidence_threshold)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if timeouts is not None:
            pulumi.set(__self__, "timeouts", timeouts)
        if voice_settings is not None:
            pulumi.set(__self__, "voice_settings", voice_settings)

    @property
    @pulumi.getter(name="botId")
    def bot_id(self) -> Optional[pulumi.Input[str]]:
        """
        Identifier of the bot to create the locale for.
        """
        return pulumi.get(self, "bot_id")

    @bot_id.setter
    def bot_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "bot_id", value)

    @property
    @pulumi.getter(name="botVersion")
    def bot_version(self) -> Optional[pulumi.Input[str]]:
        """
        Version of the bot to create the locale for. This can only be the draft version of the bot.
        """
        return pulumi.get(self, "bot_version")

    @bot_version.setter
    def bot_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "bot_version", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        Description of the bot locale. Use this to help identify the bot locale in lists.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="localeId")
    def locale_id(self) -> Optional[pulumi.Input[str]]:
        """
        Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        """
        return pulumi.get(self, "locale_id")

    @locale_id.setter
    def locale_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "locale_id", value)

    @property
    @pulumi.getter(name="nLuIntentConfidenceThreshold")
    def n_lu_intent_confidence_threshold(self) -> Optional[pulumi.Input[float]]:
        """
        Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.

        The following arguments are optional:
        """
        return pulumi.get(self, "n_lu_intent_confidence_threshold")

    @n_lu_intent_confidence_threshold.setter
    def n_lu_intent_confidence_threshold(self, value: Optional[pulumi.Input[float]]):
        pulumi.set(self, "n_lu_intent_confidence_threshold", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Specified locale name.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def timeouts(self) -> Optional[pulumi.Input['V2modelsBotLocaleTimeoutsArgs']]:
        return pulumi.get(self, "timeouts")

    @timeouts.setter
    def timeouts(self, value: Optional[pulumi.Input['V2modelsBotLocaleTimeoutsArgs']]):
        pulumi.set(self, "timeouts", value)

    @property
    @pulumi.getter(name="voiceSettings")
    def voice_settings(self) -> Optional[pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs']]:
        """
        Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        return pulumi.get(self, "voice_settings")

    @voice_settings.setter
    def voice_settings(self, value: Optional[pulumi.Input['V2modelsBotLocaleVoiceSettingsArgs']]):
        pulumi.set(self, "voice_settings", value)


class V2modelsBotLocale(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bot_id: Optional[pulumi.Input[str]] = None,
                 bot_version: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 locale_id: Optional[pulumi.Input[str]] = None,
                 n_lu_intent_confidence_threshold: Optional[pulumi.Input[float]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 timeouts: Optional[pulumi.Input[pulumi.InputType['V2modelsBotLocaleTimeoutsArgs']]] = None,
                 voice_settings: Optional[pulumi.Input[pulumi.InputType['V2modelsBotLocaleVoiceSettingsArgs']]] = None,
                 __props__=None):
        """
        Resource for managing an AWS Lex V2 Models Bot Locale.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.lex.V2modelsBotLocale("example",
            bot_id=aws_lexv2models_bot["example"]["id"],
            bot_version="DRAFT",
            locale_id="en_US",
            n_lu_intent_confidence_threshold=0.7)
        ```
        ### Voice Settings

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.lex.V2modelsBotLocale("example",
            bot_id=aws_lexv2models_bot["example"]["id"],
            bot_version="DRAFT",
            locale_id="en_US",
            n_lu_intent_confidence_threshold=0.7,
            voice_settings=aws.lex.V2modelsBotLocaleVoiceSettingsArgs(
                voice_id="Kendra",
                engine="standard",
            ))
        ```

        ## Import

        Using `pulumi import`, import Lex V2 Models Bot Locale using the `id`. For example:

        ```sh
         $ pulumi import aws:lex/v2modelsBotLocale:V2modelsBotLocale example en_US,abcd-12345678,1
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bot_id: Identifier of the bot to create the locale for.
        :param pulumi.Input[str] bot_version: Version of the bot to create the locale for. This can only be the draft version of the bot.
        :param pulumi.Input[str] description: Description of the bot locale. Use this to help identify the bot locale in lists.
        :param pulumi.Input[str] locale_id: Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        :param pulumi.Input[float] n_lu_intent_confidence_threshold: Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.
               
               The following arguments are optional:
        :param pulumi.Input[str] name: Specified locale name.
        :param pulumi.Input[pulumi.InputType['V2modelsBotLocaleVoiceSettingsArgs']] voice_settings: Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: V2modelsBotLocaleArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing an AWS Lex V2 Models Bot Locale.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.lex.V2modelsBotLocale("example",
            bot_id=aws_lexv2models_bot["example"]["id"],
            bot_version="DRAFT",
            locale_id="en_US",
            n_lu_intent_confidence_threshold=0.7)
        ```
        ### Voice Settings

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.lex.V2modelsBotLocale("example",
            bot_id=aws_lexv2models_bot["example"]["id"],
            bot_version="DRAFT",
            locale_id="en_US",
            n_lu_intent_confidence_threshold=0.7,
            voice_settings=aws.lex.V2modelsBotLocaleVoiceSettingsArgs(
                voice_id="Kendra",
                engine="standard",
            ))
        ```

        ## Import

        Using `pulumi import`, import Lex V2 Models Bot Locale using the `id`. For example:

        ```sh
         $ pulumi import aws:lex/v2modelsBotLocale:V2modelsBotLocale example en_US,abcd-12345678,1
        ```

        :param str resource_name: The name of the resource.
        :param V2modelsBotLocaleArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(V2modelsBotLocaleArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 bot_id: Optional[pulumi.Input[str]] = None,
                 bot_version: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 locale_id: Optional[pulumi.Input[str]] = None,
                 n_lu_intent_confidence_threshold: Optional[pulumi.Input[float]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 timeouts: Optional[pulumi.Input[pulumi.InputType['V2modelsBotLocaleTimeoutsArgs']]] = None,
                 voice_settings: Optional[pulumi.Input[pulumi.InputType['V2modelsBotLocaleVoiceSettingsArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = V2modelsBotLocaleArgs.__new__(V2modelsBotLocaleArgs)

            if bot_id is None and not opts.urn:
                raise TypeError("Missing required property 'bot_id'")
            __props__.__dict__["bot_id"] = bot_id
            if bot_version is None and not opts.urn:
                raise TypeError("Missing required property 'bot_version'")
            __props__.__dict__["bot_version"] = bot_version
            __props__.__dict__["description"] = description
            if locale_id is None and not opts.urn:
                raise TypeError("Missing required property 'locale_id'")
            __props__.__dict__["locale_id"] = locale_id
            if n_lu_intent_confidence_threshold is None and not opts.urn:
                raise TypeError("Missing required property 'n_lu_intent_confidence_threshold'")
            __props__.__dict__["n_lu_intent_confidence_threshold"] = n_lu_intent_confidence_threshold
            __props__.__dict__["name"] = name
            __props__.__dict__["timeouts"] = timeouts
            __props__.__dict__["voice_settings"] = voice_settings
        super(V2modelsBotLocale, __self__).__init__(
            'aws:lex/v2modelsBotLocale:V2modelsBotLocale',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            bot_id: Optional[pulumi.Input[str]] = None,
            bot_version: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            locale_id: Optional[pulumi.Input[str]] = None,
            n_lu_intent_confidence_threshold: Optional[pulumi.Input[float]] = None,
            name: Optional[pulumi.Input[str]] = None,
            timeouts: Optional[pulumi.Input[pulumi.InputType['V2modelsBotLocaleTimeoutsArgs']]] = None,
            voice_settings: Optional[pulumi.Input[pulumi.InputType['V2modelsBotLocaleVoiceSettingsArgs']]] = None) -> 'V2modelsBotLocale':
        """
        Get an existing V2modelsBotLocale resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] bot_id: Identifier of the bot to create the locale for.
        :param pulumi.Input[str] bot_version: Version of the bot to create the locale for. This can only be the draft version of the bot.
        :param pulumi.Input[str] description: Description of the bot locale. Use this to help identify the bot locale in lists.
        :param pulumi.Input[str] locale_id: Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        :param pulumi.Input[float] n_lu_intent_confidence_threshold: Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.
               
               The following arguments are optional:
        :param pulumi.Input[str] name: Specified locale name.
        :param pulumi.Input[pulumi.InputType['V2modelsBotLocaleVoiceSettingsArgs']] voice_settings: Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _V2modelsBotLocaleState.__new__(_V2modelsBotLocaleState)

        __props__.__dict__["bot_id"] = bot_id
        __props__.__dict__["bot_version"] = bot_version
        __props__.__dict__["description"] = description
        __props__.__dict__["locale_id"] = locale_id
        __props__.__dict__["n_lu_intent_confidence_threshold"] = n_lu_intent_confidence_threshold
        __props__.__dict__["name"] = name
        __props__.__dict__["timeouts"] = timeouts
        __props__.__dict__["voice_settings"] = voice_settings
        return V2modelsBotLocale(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="botId")
    def bot_id(self) -> pulumi.Output[str]:
        """
        Identifier of the bot to create the locale for.
        """
        return pulumi.get(self, "bot_id")

    @property
    @pulumi.getter(name="botVersion")
    def bot_version(self) -> pulumi.Output[str]:
        """
        Version of the bot to create the locale for. This can only be the draft version of the bot.
        """
        return pulumi.get(self, "bot_version")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        Description of the bot locale. Use this to help identify the bot locale in lists.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="localeId")
    def locale_id(self) -> pulumi.Output[str]:
        """
        Identifier of the language and locale that the bot will be used in. The string must match one of the supported locales. All of the intents, slot types, and slots used in the bot must have the same locale. For more information, see Supported languages (https://docs.aws.amazon.com/lexv2/latest/dg/how-languages.html)
        """
        return pulumi.get(self, "locale_id")

    @property
    @pulumi.getter(name="nLuIntentConfidenceThreshold")
    def n_lu_intent_confidence_threshold(self) -> pulumi.Output[float]:
        """
        Determines the threshold where Amazon Lex will insert the AMAZON.FallbackIntent, AMAZON.KendraSearchIntent, or both when returning alternative intents.

        The following arguments are optional:
        """
        return pulumi.get(self, "n_lu_intent_confidence_threshold")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Specified locale name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def timeouts(self) -> pulumi.Output[Optional['outputs.V2modelsBotLocaleTimeouts']]:
        return pulumi.get(self, "timeouts")

    @property
    @pulumi.getter(name="voiceSettings")
    def voice_settings(self) -> pulumi.Output[Optional['outputs.V2modelsBotLocaleVoiceSettings']]:
        """
        Amazon Polly voice ID that Amazon Lex uses for voice interaction with the user. See `voice_settings`.
        """
        return pulumi.get(self, "voice_settings")

