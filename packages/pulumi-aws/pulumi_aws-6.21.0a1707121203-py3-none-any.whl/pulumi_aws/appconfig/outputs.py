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

__all__ = [
    'ConfigurationProfileValidator',
    'EnvironmentMonitor',
    'EventIntegrationEventFilter',
    'ExtensionActionPoint',
    'ExtensionActionPointAction',
    'ExtensionParameter',
    'GetConfigurationProfileValidatorResult',
    'GetEnvironmentMonitorResult',
]

@pulumi.output_type
class ConfigurationProfileValidator(dict):
    def __init__(__self__, *,
                 type: str,
                 content: Optional[str] = None):
        """
        :param str type: Type of validator. Valid values: `JSON_SCHEMA` and `LAMBDA`.
        :param str content: Either the JSON Schema content or the ARN of an AWS Lambda function.
        """
        pulumi.set(__self__, "type", type)
        if content is not None:
            pulumi.set(__self__, "content", content)

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        Type of validator. Valid values: `JSON_SCHEMA` and `LAMBDA`.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter
    def content(self) -> Optional[str]:
        """
        Either the JSON Schema content or the ARN of an AWS Lambda function.
        """
        return pulumi.get(self, "content")


@pulumi.output_type
class EnvironmentMonitor(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "alarmArn":
            suggest = "alarm_arn"
        elif key == "alarmRoleArn":
            suggest = "alarm_role_arn"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in EnvironmentMonitor. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        EnvironmentMonitor.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        EnvironmentMonitor.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 alarm_arn: str,
                 alarm_role_arn: Optional[str] = None):
        """
        :param str alarm_arn: ARN of the Amazon CloudWatch alarm.
        :param str alarm_role_arn: ARN of an IAM role for AWS AppConfig to monitor `alarm_arn`.
        """
        pulumi.set(__self__, "alarm_arn", alarm_arn)
        if alarm_role_arn is not None:
            pulumi.set(__self__, "alarm_role_arn", alarm_role_arn)

    @property
    @pulumi.getter(name="alarmArn")
    def alarm_arn(self) -> str:
        """
        ARN of the Amazon CloudWatch alarm.
        """
        return pulumi.get(self, "alarm_arn")

    @property
    @pulumi.getter(name="alarmRoleArn")
    def alarm_role_arn(self) -> Optional[str]:
        """
        ARN of an IAM role for AWS AppConfig to monitor `alarm_arn`.
        """
        return pulumi.get(self, "alarm_role_arn")


@pulumi.output_type
class EventIntegrationEventFilter(dict):
    def __init__(__self__, *,
                 source: str):
        """
        :param str source: Source of the events.
        """
        pulumi.set(__self__, "source", source)

    @property
    @pulumi.getter
    def source(self) -> str:
        """
        Source of the events.
        """
        return pulumi.get(self, "source")


@pulumi.output_type
class ExtensionActionPoint(dict):
    def __init__(__self__, *,
                 actions: Sequence['outputs.ExtensionActionPointAction'],
                 point: str):
        """
        :param Sequence['ExtensionActionPointActionArgs'] actions: An action defines the tasks the extension performs during the AppConfig workflow. Detailed below.
        :param str point: The point at which to perform the defined actions. Valid points are `PRE_CREATE_HOSTED_CONFIGURATION_VERSION`, `PRE_START_DEPLOYMENT`, `ON_DEPLOYMENT_START`, `ON_DEPLOYMENT_STEP`, `ON_DEPLOYMENT_BAKING`, `ON_DEPLOYMENT_COMPLETE`, `ON_DEPLOYMENT_ROLLED_BACK`.
        """
        pulumi.set(__self__, "actions", actions)
        pulumi.set(__self__, "point", point)

    @property
    @pulumi.getter
    def actions(self) -> Sequence['outputs.ExtensionActionPointAction']:
        """
        An action defines the tasks the extension performs during the AppConfig workflow. Detailed below.
        """
        return pulumi.get(self, "actions")

    @property
    @pulumi.getter
    def point(self) -> str:
        """
        The point at which to perform the defined actions. Valid points are `PRE_CREATE_HOSTED_CONFIGURATION_VERSION`, `PRE_START_DEPLOYMENT`, `ON_DEPLOYMENT_START`, `ON_DEPLOYMENT_STEP`, `ON_DEPLOYMENT_BAKING`, `ON_DEPLOYMENT_COMPLETE`, `ON_DEPLOYMENT_ROLLED_BACK`.
        """
        return pulumi.get(self, "point")


@pulumi.output_type
class ExtensionActionPointAction(dict):
    @staticmethod
    def __key_warning(key: str):
        suggest = None
        if key == "roleArn":
            suggest = "role_arn"

        if suggest:
            pulumi.log.warn(f"Key '{key}' not found in ExtensionActionPointAction. Access the value via the '{suggest}' property getter instead.")

    def __getitem__(self, key: str) -> Any:
        ExtensionActionPointAction.__key_warning(key)
        return super().__getitem__(key)

    def get(self, key: str, default = None) -> Any:
        ExtensionActionPointAction.__key_warning(key)
        return super().get(key, default)

    def __init__(__self__, *,
                 name: str,
                 role_arn: str,
                 uri: str,
                 description: Optional[str] = None):
        """
        :param str name: The action name.
        :param str role_arn: An Amazon Resource Name (ARN) for an Identity and Access Management assume role.
        :param str uri: The extension URI associated to the action point in the extension definition. The URI can be an Amazon Resource Name (ARN) for one of the following: an Lambda function, an Amazon Simple Queue Service queue, an Amazon Simple Notification Service topic, or the Amazon EventBridge default event bus.
        :param str description: Information about the action.
        """
        pulumi.set(__self__, "name", name)
        pulumi.set(__self__, "role_arn", role_arn)
        pulumi.set(__self__, "uri", uri)
        if description is not None:
            pulumi.set(__self__, "description", description)

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The action name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="roleArn")
    def role_arn(self) -> str:
        """
        An Amazon Resource Name (ARN) for an Identity and Access Management assume role.
        """
        return pulumi.get(self, "role_arn")

    @property
    @pulumi.getter
    def uri(self) -> str:
        """
        The extension URI associated to the action point in the extension definition. The URI can be an Amazon Resource Name (ARN) for one of the following: an Lambda function, an Amazon Simple Queue Service queue, an Amazon Simple Notification Service topic, or the Amazon EventBridge default event bus.
        """
        return pulumi.get(self, "uri")

    @property
    @pulumi.getter
    def description(self) -> Optional[str]:
        """
        Information about the action.
        """
        return pulumi.get(self, "description")


@pulumi.output_type
class ExtensionParameter(dict):
    def __init__(__self__, *,
                 name: str,
                 description: Optional[str] = None,
                 required: Optional[bool] = None):
        """
        :param str name: The parameter name.
        :param str description: Information about the parameter.
        :param bool required: Determines if a parameter value must be specified in the extension association.
        """
        pulumi.set(__self__, "name", name)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if required is not None:
            pulumi.set(__self__, "required", required)

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        The parameter name.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def description(self) -> Optional[str]:
        """
        Information about the parameter.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def required(self) -> Optional[bool]:
        """
        Determines if a parameter value must be specified in the extension association.
        """
        return pulumi.get(self, "required")


@pulumi.output_type
class GetConfigurationProfileValidatorResult(dict):
    def __init__(__self__, *,
                 content: str,
                 type: str):
        """
        :param str content: Either the JSON Schema content or the ARN of an AWS Lambda function.
        :param str type: Type of validator. Valid values: JSON_SCHEMA and LAMBDA.
        """
        pulumi.set(__self__, "content", content)
        pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter
    def content(self) -> str:
        """
        Either the JSON Schema content or the ARN of an AWS Lambda function.
        """
        return pulumi.get(self, "content")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        Type of validator. Valid values: JSON_SCHEMA and LAMBDA.
        """
        return pulumi.get(self, "type")


@pulumi.output_type
class GetEnvironmentMonitorResult(dict):
    def __init__(__self__, *,
                 alarm_arn: str,
                 alarm_role_arn: str):
        """
        :param str alarm_arn: ARN of the Amazon CloudWatch alarm.
        :param str alarm_role_arn: ARN of an IAM role for AWS AppConfig to monitor.
        """
        pulumi.set(__self__, "alarm_arn", alarm_arn)
        pulumi.set(__self__, "alarm_role_arn", alarm_role_arn)

    @property
    @pulumi.getter(name="alarmArn")
    def alarm_arn(self) -> str:
        """
        ARN of the Amazon CloudWatch alarm.
        """
        return pulumi.get(self, "alarm_arn")

    @property
    @pulumi.getter(name="alarmRoleArn")
    def alarm_role_arn(self) -> str:
        """
        ARN of an IAM role for AWS AppConfig to monitor.
        """
        return pulumi.get(self, "alarm_role_arn")


