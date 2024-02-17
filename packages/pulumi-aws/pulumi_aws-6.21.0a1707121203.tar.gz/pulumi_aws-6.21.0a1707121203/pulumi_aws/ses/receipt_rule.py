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

__all__ = ['ReceiptRuleArgs', 'ReceiptRule']

@pulumi.input_type
class ReceiptRuleArgs:
    def __init__(__self__, *,
                 rule_set_name: pulumi.Input[str],
                 add_header_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]]] = None,
                 after: Optional[pulumi.Input[str]] = None,
                 bounce_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 lambda_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 s3_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]]] = None,
                 scan_enabled: Optional[pulumi.Input[bool]] = None,
                 sns_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]]] = None,
                 stop_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]]] = None,
                 tls_policy: Optional[pulumi.Input[str]] = None,
                 workmail_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]]] = None):
        """
        The set of arguments for constructing a ReceiptRule resource.
        :param pulumi.Input[str] rule_set_name: The name of the rule set
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]] add_header_actions: A list of Add Header Action blocks. Documented below.
        :param pulumi.Input[str] after: The name of the rule to place this rule after
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]] bounce_actions: A list of Bounce Action blocks. Documented below.
        :param pulumi.Input[bool] enabled: If true, the rule will be enabled
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]] lambda_actions: A list of Lambda Action blocks. Documented below.
        :param pulumi.Input[str] name: The name of the rule
        :param pulumi.Input[Sequence[pulumi.Input[str]]] recipients: A list of email addresses
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]] s3_actions: A list of S3 Action blocks. Documented below.
        :param pulumi.Input[bool] scan_enabled: If true, incoming emails will be scanned for spam and viruses
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]] sns_actions: A list of SNS Action blocks. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]] stop_actions: A list of Stop Action blocks. Documented below.
        :param pulumi.Input[str] tls_policy: `Require` or `Optional`
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]] workmail_actions: A list of WorkMail Action blocks. Documented below.
        """
        pulumi.set(__self__, "rule_set_name", rule_set_name)
        if add_header_actions is not None:
            pulumi.set(__self__, "add_header_actions", add_header_actions)
        if after is not None:
            pulumi.set(__self__, "after", after)
        if bounce_actions is not None:
            pulumi.set(__self__, "bounce_actions", bounce_actions)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if lambda_actions is not None:
            pulumi.set(__self__, "lambda_actions", lambda_actions)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if recipients is not None:
            pulumi.set(__self__, "recipients", recipients)
        if s3_actions is not None:
            pulumi.set(__self__, "s3_actions", s3_actions)
        if scan_enabled is not None:
            pulumi.set(__self__, "scan_enabled", scan_enabled)
        if sns_actions is not None:
            pulumi.set(__self__, "sns_actions", sns_actions)
        if stop_actions is not None:
            pulumi.set(__self__, "stop_actions", stop_actions)
        if tls_policy is not None:
            pulumi.set(__self__, "tls_policy", tls_policy)
        if workmail_actions is not None:
            pulumi.set(__self__, "workmail_actions", workmail_actions)

    @property
    @pulumi.getter(name="ruleSetName")
    def rule_set_name(self) -> pulumi.Input[str]:
        """
        The name of the rule set
        """
        return pulumi.get(self, "rule_set_name")

    @rule_set_name.setter
    def rule_set_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "rule_set_name", value)

    @property
    @pulumi.getter(name="addHeaderActions")
    def add_header_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]]]:
        """
        A list of Add Header Action blocks. Documented below.
        """
        return pulumi.get(self, "add_header_actions")

    @add_header_actions.setter
    def add_header_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]]]):
        pulumi.set(self, "add_header_actions", value)

    @property
    @pulumi.getter
    def after(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the rule to place this rule after
        """
        return pulumi.get(self, "after")

    @after.setter
    def after(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "after", value)

    @property
    @pulumi.getter(name="bounceActions")
    def bounce_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]]]:
        """
        A list of Bounce Action blocks. Documented below.
        """
        return pulumi.get(self, "bounce_actions")

    @bounce_actions.setter
    def bounce_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]]]):
        pulumi.set(self, "bounce_actions", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, the rule will be enabled
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter(name="lambdaActions")
    def lambda_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]]]:
        """
        A list of Lambda Action blocks. Documented below.
        """
        return pulumi.get(self, "lambda_actions")

    @lambda_actions.setter
    def lambda_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]]]):
        pulumi.set(self, "lambda_actions", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the rule
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def recipients(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of email addresses
        """
        return pulumi.get(self, "recipients")

    @recipients.setter
    def recipients(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "recipients", value)

    @property
    @pulumi.getter(name="s3Actions")
    def s3_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]]]:
        """
        A list of S3 Action blocks. Documented below.
        """
        return pulumi.get(self, "s3_actions")

    @s3_actions.setter
    def s3_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]]]):
        pulumi.set(self, "s3_actions", value)

    @property
    @pulumi.getter(name="scanEnabled")
    def scan_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, incoming emails will be scanned for spam and viruses
        """
        return pulumi.get(self, "scan_enabled")

    @scan_enabled.setter
    def scan_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "scan_enabled", value)

    @property
    @pulumi.getter(name="snsActions")
    def sns_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]]]:
        """
        A list of SNS Action blocks. Documented below.
        """
        return pulumi.get(self, "sns_actions")

    @sns_actions.setter
    def sns_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]]]):
        pulumi.set(self, "sns_actions", value)

    @property
    @pulumi.getter(name="stopActions")
    def stop_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]]]:
        """
        A list of Stop Action blocks. Documented below.
        """
        return pulumi.get(self, "stop_actions")

    @stop_actions.setter
    def stop_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]]]):
        pulumi.set(self, "stop_actions", value)

    @property
    @pulumi.getter(name="tlsPolicy")
    def tls_policy(self) -> Optional[pulumi.Input[str]]:
        """
        `Require` or `Optional`
        """
        return pulumi.get(self, "tls_policy")

    @tls_policy.setter
    def tls_policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tls_policy", value)

    @property
    @pulumi.getter(name="workmailActions")
    def workmail_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]]]:
        """
        A list of WorkMail Action blocks. Documented below.
        """
        return pulumi.get(self, "workmail_actions")

    @workmail_actions.setter
    def workmail_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]]]):
        pulumi.set(self, "workmail_actions", value)


@pulumi.input_type
class _ReceiptRuleState:
    def __init__(__self__, *,
                 add_header_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]]] = None,
                 after: Optional[pulumi.Input[str]] = None,
                 arn: Optional[pulumi.Input[str]] = None,
                 bounce_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 lambda_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 rule_set_name: Optional[pulumi.Input[str]] = None,
                 s3_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]]] = None,
                 scan_enabled: Optional[pulumi.Input[bool]] = None,
                 sns_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]]] = None,
                 stop_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]]] = None,
                 tls_policy: Optional[pulumi.Input[str]] = None,
                 workmail_actions: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]]] = None):
        """
        Input properties used for looking up and filtering ReceiptRule resources.
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]] add_header_actions: A list of Add Header Action blocks. Documented below.
        :param pulumi.Input[str] after: The name of the rule to place this rule after
        :param pulumi.Input[str] arn: The SES receipt rule ARN.
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]] bounce_actions: A list of Bounce Action blocks. Documented below.
        :param pulumi.Input[bool] enabled: If true, the rule will be enabled
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]] lambda_actions: A list of Lambda Action blocks. Documented below.
        :param pulumi.Input[str] name: The name of the rule
        :param pulumi.Input[Sequence[pulumi.Input[str]]] recipients: A list of email addresses
        :param pulumi.Input[str] rule_set_name: The name of the rule set
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]] s3_actions: A list of S3 Action blocks. Documented below.
        :param pulumi.Input[bool] scan_enabled: If true, incoming emails will be scanned for spam and viruses
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]] sns_actions: A list of SNS Action blocks. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]] stop_actions: A list of Stop Action blocks. Documented below.
        :param pulumi.Input[str] tls_policy: `Require` or `Optional`
        :param pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]] workmail_actions: A list of WorkMail Action blocks. Documented below.
        """
        if add_header_actions is not None:
            pulumi.set(__self__, "add_header_actions", add_header_actions)
        if after is not None:
            pulumi.set(__self__, "after", after)
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if bounce_actions is not None:
            pulumi.set(__self__, "bounce_actions", bounce_actions)
        if enabled is not None:
            pulumi.set(__self__, "enabled", enabled)
        if lambda_actions is not None:
            pulumi.set(__self__, "lambda_actions", lambda_actions)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if recipients is not None:
            pulumi.set(__self__, "recipients", recipients)
        if rule_set_name is not None:
            pulumi.set(__self__, "rule_set_name", rule_set_name)
        if s3_actions is not None:
            pulumi.set(__self__, "s3_actions", s3_actions)
        if scan_enabled is not None:
            pulumi.set(__self__, "scan_enabled", scan_enabled)
        if sns_actions is not None:
            pulumi.set(__self__, "sns_actions", sns_actions)
        if stop_actions is not None:
            pulumi.set(__self__, "stop_actions", stop_actions)
        if tls_policy is not None:
            pulumi.set(__self__, "tls_policy", tls_policy)
        if workmail_actions is not None:
            pulumi.set(__self__, "workmail_actions", workmail_actions)

    @property
    @pulumi.getter(name="addHeaderActions")
    def add_header_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]]]:
        """
        A list of Add Header Action blocks. Documented below.
        """
        return pulumi.get(self, "add_header_actions")

    @add_header_actions.setter
    def add_header_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleAddHeaderActionArgs']]]]):
        pulumi.set(self, "add_header_actions", value)

    @property
    @pulumi.getter
    def after(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the rule to place this rule after
        """
        return pulumi.get(self, "after")

    @after.setter
    def after(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "after", value)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The SES receipt rule ARN.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="bounceActions")
    def bounce_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]]]:
        """
        A list of Bounce Action blocks. Documented below.
        """
        return pulumi.get(self, "bounce_actions")

    @bounce_actions.setter
    def bounce_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleBounceActionArgs']]]]):
        pulumi.set(self, "bounce_actions", value)

    @property
    @pulumi.getter
    def enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, the rule will be enabled
        """
        return pulumi.get(self, "enabled")

    @enabled.setter
    def enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "enabled", value)

    @property
    @pulumi.getter(name="lambdaActions")
    def lambda_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]]]:
        """
        A list of Lambda Action blocks. Documented below.
        """
        return pulumi.get(self, "lambda_actions")

    @lambda_actions.setter
    def lambda_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleLambdaActionArgs']]]]):
        pulumi.set(self, "lambda_actions", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the rule
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def recipients(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        A list of email addresses
        """
        return pulumi.get(self, "recipients")

    @recipients.setter
    def recipients(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "recipients", value)

    @property
    @pulumi.getter(name="ruleSetName")
    def rule_set_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the rule set
        """
        return pulumi.get(self, "rule_set_name")

    @rule_set_name.setter
    def rule_set_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "rule_set_name", value)

    @property
    @pulumi.getter(name="s3Actions")
    def s3_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]]]:
        """
        A list of S3 Action blocks. Documented below.
        """
        return pulumi.get(self, "s3_actions")

    @s3_actions.setter
    def s3_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleS3ActionArgs']]]]):
        pulumi.set(self, "s3_actions", value)

    @property
    @pulumi.getter(name="scanEnabled")
    def scan_enabled(self) -> Optional[pulumi.Input[bool]]:
        """
        If true, incoming emails will be scanned for spam and viruses
        """
        return pulumi.get(self, "scan_enabled")

    @scan_enabled.setter
    def scan_enabled(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "scan_enabled", value)

    @property
    @pulumi.getter(name="snsActions")
    def sns_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]]]:
        """
        A list of SNS Action blocks. Documented below.
        """
        return pulumi.get(self, "sns_actions")

    @sns_actions.setter
    def sns_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleSnsActionArgs']]]]):
        pulumi.set(self, "sns_actions", value)

    @property
    @pulumi.getter(name="stopActions")
    def stop_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]]]:
        """
        A list of Stop Action blocks. Documented below.
        """
        return pulumi.get(self, "stop_actions")

    @stop_actions.setter
    def stop_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleStopActionArgs']]]]):
        pulumi.set(self, "stop_actions", value)

    @property
    @pulumi.getter(name="tlsPolicy")
    def tls_policy(self) -> Optional[pulumi.Input[str]]:
        """
        `Require` or `Optional`
        """
        return pulumi.get(self, "tls_policy")

    @tls_policy.setter
    def tls_policy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tls_policy", value)

    @property
    @pulumi.getter(name="workmailActions")
    def workmail_actions(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]]]:
        """
        A list of WorkMail Action blocks. Documented below.
        """
        return pulumi.get(self, "workmail_actions")

    @workmail_actions.setter
    def workmail_actions(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['ReceiptRuleWorkmailActionArgs']]]]):
        pulumi.set(self, "workmail_actions", value)


class ReceiptRule(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 add_header_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleAddHeaderActionArgs']]]]] = None,
                 after: Optional[pulumi.Input[str]] = None,
                 bounce_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleBounceActionArgs']]]]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 lambda_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleLambdaActionArgs']]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 rule_set_name: Optional[pulumi.Input[str]] = None,
                 s3_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleS3ActionArgs']]]]] = None,
                 scan_enabled: Optional[pulumi.Input[bool]] = None,
                 sns_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleSnsActionArgs']]]]] = None,
                 stop_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleStopActionArgs']]]]] = None,
                 tls_policy: Optional[pulumi.Input[str]] = None,
                 workmail_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleWorkmailActionArgs']]]]] = None,
                 __props__=None):
        """
        Provides an SES receipt rule resource

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        # Add a header to the email and store it in S3
        store = aws.ses.ReceiptRule("store",
            add_header_actions=[aws.ses.ReceiptRuleAddHeaderActionArgs(
                header_name="Custom-Header",
                header_value="Added by SES",
                position=1,
            )],
            enabled=True,
            recipients=["karen@example.com"],
            rule_set_name="default-rule-set",
            s3_actions=[aws.ses.ReceiptRuleS3ActionArgs(
                bucket_name="emails",
                position=2,
            )],
            scan_enabled=True)
        ```

        ## Import

        Using `pulumi import`, import SES receipt rules using the ruleset name and rule name separated by `:`. For example:

        ```sh
         $ pulumi import aws:ses/receiptRule:ReceiptRule my_rule my_rule_set:my_rule
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleAddHeaderActionArgs']]]] add_header_actions: A list of Add Header Action blocks. Documented below.
        :param pulumi.Input[str] after: The name of the rule to place this rule after
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleBounceActionArgs']]]] bounce_actions: A list of Bounce Action blocks. Documented below.
        :param pulumi.Input[bool] enabled: If true, the rule will be enabled
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleLambdaActionArgs']]]] lambda_actions: A list of Lambda Action blocks. Documented below.
        :param pulumi.Input[str] name: The name of the rule
        :param pulumi.Input[Sequence[pulumi.Input[str]]] recipients: A list of email addresses
        :param pulumi.Input[str] rule_set_name: The name of the rule set
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleS3ActionArgs']]]] s3_actions: A list of S3 Action blocks. Documented below.
        :param pulumi.Input[bool] scan_enabled: If true, incoming emails will be scanned for spam and viruses
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleSnsActionArgs']]]] sns_actions: A list of SNS Action blocks. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleStopActionArgs']]]] stop_actions: A list of Stop Action blocks. Documented below.
        :param pulumi.Input[str] tls_policy: `Require` or `Optional`
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleWorkmailActionArgs']]]] workmail_actions: A list of WorkMail Action blocks. Documented below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ReceiptRuleArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an SES receipt rule resource

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        # Add a header to the email and store it in S3
        store = aws.ses.ReceiptRule("store",
            add_header_actions=[aws.ses.ReceiptRuleAddHeaderActionArgs(
                header_name="Custom-Header",
                header_value="Added by SES",
                position=1,
            )],
            enabled=True,
            recipients=["karen@example.com"],
            rule_set_name="default-rule-set",
            s3_actions=[aws.ses.ReceiptRuleS3ActionArgs(
                bucket_name="emails",
                position=2,
            )],
            scan_enabled=True)
        ```

        ## Import

        Using `pulumi import`, import SES receipt rules using the ruleset name and rule name separated by `:`. For example:

        ```sh
         $ pulumi import aws:ses/receiptRule:ReceiptRule my_rule my_rule_set:my_rule
        ```

        :param str resource_name: The name of the resource.
        :param ReceiptRuleArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ReceiptRuleArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 add_header_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleAddHeaderActionArgs']]]]] = None,
                 after: Optional[pulumi.Input[str]] = None,
                 bounce_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleBounceActionArgs']]]]] = None,
                 enabled: Optional[pulumi.Input[bool]] = None,
                 lambda_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleLambdaActionArgs']]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
                 rule_set_name: Optional[pulumi.Input[str]] = None,
                 s3_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleS3ActionArgs']]]]] = None,
                 scan_enabled: Optional[pulumi.Input[bool]] = None,
                 sns_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleSnsActionArgs']]]]] = None,
                 stop_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleStopActionArgs']]]]] = None,
                 tls_policy: Optional[pulumi.Input[str]] = None,
                 workmail_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleWorkmailActionArgs']]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ReceiptRuleArgs.__new__(ReceiptRuleArgs)

            __props__.__dict__["add_header_actions"] = add_header_actions
            __props__.__dict__["after"] = after
            __props__.__dict__["bounce_actions"] = bounce_actions
            __props__.__dict__["enabled"] = enabled
            __props__.__dict__["lambda_actions"] = lambda_actions
            __props__.__dict__["name"] = name
            __props__.__dict__["recipients"] = recipients
            if rule_set_name is None and not opts.urn:
                raise TypeError("Missing required property 'rule_set_name'")
            __props__.__dict__["rule_set_name"] = rule_set_name
            __props__.__dict__["s3_actions"] = s3_actions
            __props__.__dict__["scan_enabled"] = scan_enabled
            __props__.__dict__["sns_actions"] = sns_actions
            __props__.__dict__["stop_actions"] = stop_actions
            __props__.__dict__["tls_policy"] = tls_policy
            __props__.__dict__["workmail_actions"] = workmail_actions
            __props__.__dict__["arn"] = None
        super(ReceiptRule, __self__).__init__(
            'aws:ses/receiptRule:ReceiptRule',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            add_header_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleAddHeaderActionArgs']]]]] = None,
            after: Optional[pulumi.Input[str]] = None,
            arn: Optional[pulumi.Input[str]] = None,
            bounce_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleBounceActionArgs']]]]] = None,
            enabled: Optional[pulumi.Input[bool]] = None,
            lambda_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleLambdaActionArgs']]]]] = None,
            name: Optional[pulumi.Input[str]] = None,
            recipients: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None,
            rule_set_name: Optional[pulumi.Input[str]] = None,
            s3_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleS3ActionArgs']]]]] = None,
            scan_enabled: Optional[pulumi.Input[bool]] = None,
            sns_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleSnsActionArgs']]]]] = None,
            stop_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleStopActionArgs']]]]] = None,
            tls_policy: Optional[pulumi.Input[str]] = None,
            workmail_actions: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleWorkmailActionArgs']]]]] = None) -> 'ReceiptRule':
        """
        Get an existing ReceiptRule resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleAddHeaderActionArgs']]]] add_header_actions: A list of Add Header Action blocks. Documented below.
        :param pulumi.Input[str] after: The name of the rule to place this rule after
        :param pulumi.Input[str] arn: The SES receipt rule ARN.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleBounceActionArgs']]]] bounce_actions: A list of Bounce Action blocks. Documented below.
        :param pulumi.Input[bool] enabled: If true, the rule will be enabled
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleLambdaActionArgs']]]] lambda_actions: A list of Lambda Action blocks. Documented below.
        :param pulumi.Input[str] name: The name of the rule
        :param pulumi.Input[Sequence[pulumi.Input[str]]] recipients: A list of email addresses
        :param pulumi.Input[str] rule_set_name: The name of the rule set
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleS3ActionArgs']]]] s3_actions: A list of S3 Action blocks. Documented below.
        :param pulumi.Input[bool] scan_enabled: If true, incoming emails will be scanned for spam and viruses
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleSnsActionArgs']]]] sns_actions: A list of SNS Action blocks. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleStopActionArgs']]]] stop_actions: A list of Stop Action blocks. Documented below.
        :param pulumi.Input[str] tls_policy: `Require` or `Optional`
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['ReceiptRuleWorkmailActionArgs']]]] workmail_actions: A list of WorkMail Action blocks. Documented below.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ReceiptRuleState.__new__(_ReceiptRuleState)

        __props__.__dict__["add_header_actions"] = add_header_actions
        __props__.__dict__["after"] = after
        __props__.__dict__["arn"] = arn
        __props__.__dict__["bounce_actions"] = bounce_actions
        __props__.__dict__["enabled"] = enabled
        __props__.__dict__["lambda_actions"] = lambda_actions
        __props__.__dict__["name"] = name
        __props__.__dict__["recipients"] = recipients
        __props__.__dict__["rule_set_name"] = rule_set_name
        __props__.__dict__["s3_actions"] = s3_actions
        __props__.__dict__["scan_enabled"] = scan_enabled
        __props__.__dict__["sns_actions"] = sns_actions
        __props__.__dict__["stop_actions"] = stop_actions
        __props__.__dict__["tls_policy"] = tls_policy
        __props__.__dict__["workmail_actions"] = workmail_actions
        return ReceiptRule(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="addHeaderActions")
    def add_header_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleAddHeaderAction']]]:
        """
        A list of Add Header Action blocks. Documented below.
        """
        return pulumi.get(self, "add_header_actions")

    @property
    @pulumi.getter
    def after(self) -> pulumi.Output[Optional[str]]:
        """
        The name of the rule to place this rule after
        """
        return pulumi.get(self, "after")

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The SES receipt rule ARN.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="bounceActions")
    def bounce_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleBounceAction']]]:
        """
        A list of Bounce Action blocks. Documented below.
        """
        return pulumi.get(self, "bounce_actions")

    @property
    @pulumi.getter
    def enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        If true, the rule will be enabled
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter(name="lambdaActions")
    def lambda_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleLambdaAction']]]:
        """
        A list of Lambda Action blocks. Documented below.
        """
        return pulumi.get(self, "lambda_actions")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the rule
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def recipients(self) -> pulumi.Output[Optional[Sequence[str]]]:
        """
        A list of email addresses
        """
        return pulumi.get(self, "recipients")

    @property
    @pulumi.getter(name="ruleSetName")
    def rule_set_name(self) -> pulumi.Output[str]:
        """
        The name of the rule set
        """
        return pulumi.get(self, "rule_set_name")

    @property
    @pulumi.getter(name="s3Actions")
    def s3_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleS3Action']]]:
        """
        A list of S3 Action blocks. Documented below.
        """
        return pulumi.get(self, "s3_actions")

    @property
    @pulumi.getter(name="scanEnabled")
    def scan_enabled(self) -> pulumi.Output[Optional[bool]]:
        """
        If true, incoming emails will be scanned for spam and viruses
        """
        return pulumi.get(self, "scan_enabled")

    @property
    @pulumi.getter(name="snsActions")
    def sns_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleSnsAction']]]:
        """
        A list of SNS Action blocks. Documented below.
        """
        return pulumi.get(self, "sns_actions")

    @property
    @pulumi.getter(name="stopActions")
    def stop_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleStopAction']]]:
        """
        A list of Stop Action blocks. Documented below.
        """
        return pulumi.get(self, "stop_actions")

    @property
    @pulumi.getter(name="tlsPolicy")
    def tls_policy(self) -> pulumi.Output[str]:
        """
        `Require` or `Optional`
        """
        return pulumi.get(self, "tls_policy")

    @property
    @pulumi.getter(name="workmailActions")
    def workmail_actions(self) -> pulumi.Output[Optional[Sequence['outputs.ReceiptRuleWorkmailAction']]]:
        """
        A list of WorkMail Action blocks. Documented below.
        """
        return pulumi.get(self, "workmail_actions")

