# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['MailFromArgs', 'MailFrom']

@pulumi.input_type
class MailFromArgs:
    def __init__(__self__, *,
                 domain: pulumi.Input[str],
                 mail_from_domain: pulumi.Input[str],
                 behavior_on_mx_failure: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a MailFrom resource.
        :param pulumi.Input[str] domain: Verified domain name or email identity to generate DKIM tokens for.
        :param pulumi.Input[str] mail_from_domain: Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)
               
               The following arguments are optional:
        :param pulumi.Input[str] behavior_on_mx_failure: The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        """
        pulumi.set(__self__, "domain", domain)
        pulumi.set(__self__, "mail_from_domain", mail_from_domain)
        if behavior_on_mx_failure is not None:
            pulumi.set(__self__, "behavior_on_mx_failure", behavior_on_mx_failure)

    @property
    @pulumi.getter
    def domain(self) -> pulumi.Input[str]:
        """
        Verified domain name or email identity to generate DKIM tokens for.
        """
        return pulumi.get(self, "domain")

    @domain.setter
    def domain(self, value: pulumi.Input[str]):
        pulumi.set(self, "domain", value)

    @property
    @pulumi.getter(name="mailFromDomain")
    def mail_from_domain(self) -> pulumi.Input[str]:
        """
        Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)

        The following arguments are optional:
        """
        return pulumi.get(self, "mail_from_domain")

    @mail_from_domain.setter
    def mail_from_domain(self, value: pulumi.Input[str]):
        pulumi.set(self, "mail_from_domain", value)

    @property
    @pulumi.getter(name="behaviorOnMxFailure")
    def behavior_on_mx_failure(self) -> Optional[pulumi.Input[str]]:
        """
        The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        """
        return pulumi.get(self, "behavior_on_mx_failure")

    @behavior_on_mx_failure.setter
    def behavior_on_mx_failure(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "behavior_on_mx_failure", value)


@pulumi.input_type
class _MailFromState:
    def __init__(__self__, *,
                 behavior_on_mx_failure: Optional[pulumi.Input[str]] = None,
                 domain: Optional[pulumi.Input[str]] = None,
                 mail_from_domain: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering MailFrom resources.
        :param pulumi.Input[str] behavior_on_mx_failure: The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        :param pulumi.Input[str] domain: Verified domain name or email identity to generate DKIM tokens for.
        :param pulumi.Input[str] mail_from_domain: Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)
               
               The following arguments are optional:
        """
        if behavior_on_mx_failure is not None:
            pulumi.set(__self__, "behavior_on_mx_failure", behavior_on_mx_failure)
        if domain is not None:
            pulumi.set(__self__, "domain", domain)
        if mail_from_domain is not None:
            pulumi.set(__self__, "mail_from_domain", mail_from_domain)

    @property
    @pulumi.getter(name="behaviorOnMxFailure")
    def behavior_on_mx_failure(self) -> Optional[pulumi.Input[str]]:
        """
        The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        """
        return pulumi.get(self, "behavior_on_mx_failure")

    @behavior_on_mx_failure.setter
    def behavior_on_mx_failure(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "behavior_on_mx_failure", value)

    @property
    @pulumi.getter
    def domain(self) -> Optional[pulumi.Input[str]]:
        """
        Verified domain name or email identity to generate DKIM tokens for.
        """
        return pulumi.get(self, "domain")

    @domain.setter
    def domain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain", value)

    @property
    @pulumi.getter(name="mailFromDomain")
    def mail_from_domain(self) -> Optional[pulumi.Input[str]]:
        """
        Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)

        The following arguments are optional:
        """
        return pulumi.get(self, "mail_from_domain")

    @mail_from_domain.setter
    def mail_from_domain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "mail_from_domain", value)


class MailFrom(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 behavior_on_mx_failure: Optional[pulumi.Input[str]] = None,
                 domain: Optional[pulumi.Input[str]] = None,
                 mail_from_domain: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides an SES domain MAIL FROM resource.

        > **NOTE:** For the MAIL FROM domain to be fully usable, this resource should be paired with the ses.DomainIdentity resource. To validate the MAIL FROM domain, a DNS MX record is required. To pass SPF checks, a DNS TXT record may also be required. See the [Amazon SES MAIL FROM documentation](https://docs.aws.amazon.com/ses/latest/dg/mail-from.html) for more information.

        ## Example Usage
        ### Domain Identity MAIL FROM

        ```python
        import pulumi
        import pulumi_aws as aws

        # Example SES Domain Identity
        example_domain_identity = aws.ses.DomainIdentity("exampleDomainIdentity", domain="example.com")
        example_mail_from = aws.ses.MailFrom("exampleMailFrom",
            domain=example_domain_identity.domain,
            mail_from_domain=example_domain_identity.domain.apply(lambda domain: f"bounce.{domain}"))
        # Example Route53 MX record
        example_ses_domain_mail_from_mx = aws.route53.Record("exampleSesDomainMailFromMx",
            zone_id=aws_route53_zone["example"]["id"],
            name=example_mail_from.mail_from_domain,
            type="MX",
            ttl=600,
            records=["10 feedback-smtp.us-east-1.amazonses.com"])
        # Change to the region in which `aws_ses_domain_identity.example` is created
        # Example Route53 TXT record for SPF
        example_ses_domain_mail_from_txt = aws.route53.Record("exampleSesDomainMailFromTxt",
            zone_id=aws_route53_zone["example"]["id"],
            name=example_mail_from.mail_from_domain,
            type="TXT",
            ttl=600,
            records=["v=spf1 include:amazonses.com -all"])
        ```
        ### Email Identity MAIL FROM

        ```python
        import pulumi
        import pulumi_aws as aws

        # Example SES Email Identity
        example_email_identity = aws.ses.EmailIdentity("exampleEmailIdentity", email="user@example.com")
        example_mail_from = aws.ses.MailFrom("exampleMailFrom",
            domain=example_email_identity.email,
            mail_from_domain="mail.example.com")
        ```

        ## Import

        Using `pulumi import`, import MAIL FROM domain using the `domain` attribute. For example:

        ```sh
         $ pulumi import aws:ses/mailFrom:MailFrom example example.com
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] behavior_on_mx_failure: The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        :param pulumi.Input[str] domain: Verified domain name or email identity to generate DKIM tokens for.
        :param pulumi.Input[str] mail_from_domain: Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)
               
               The following arguments are optional:
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: MailFromArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an SES domain MAIL FROM resource.

        > **NOTE:** For the MAIL FROM domain to be fully usable, this resource should be paired with the ses.DomainIdentity resource. To validate the MAIL FROM domain, a DNS MX record is required. To pass SPF checks, a DNS TXT record may also be required. See the [Amazon SES MAIL FROM documentation](https://docs.aws.amazon.com/ses/latest/dg/mail-from.html) for more information.

        ## Example Usage
        ### Domain Identity MAIL FROM

        ```python
        import pulumi
        import pulumi_aws as aws

        # Example SES Domain Identity
        example_domain_identity = aws.ses.DomainIdentity("exampleDomainIdentity", domain="example.com")
        example_mail_from = aws.ses.MailFrom("exampleMailFrom",
            domain=example_domain_identity.domain,
            mail_from_domain=example_domain_identity.domain.apply(lambda domain: f"bounce.{domain}"))
        # Example Route53 MX record
        example_ses_domain_mail_from_mx = aws.route53.Record("exampleSesDomainMailFromMx",
            zone_id=aws_route53_zone["example"]["id"],
            name=example_mail_from.mail_from_domain,
            type="MX",
            ttl=600,
            records=["10 feedback-smtp.us-east-1.amazonses.com"])
        # Change to the region in which `aws_ses_domain_identity.example` is created
        # Example Route53 TXT record for SPF
        example_ses_domain_mail_from_txt = aws.route53.Record("exampleSesDomainMailFromTxt",
            zone_id=aws_route53_zone["example"]["id"],
            name=example_mail_from.mail_from_domain,
            type="TXT",
            ttl=600,
            records=["v=spf1 include:amazonses.com -all"])
        ```
        ### Email Identity MAIL FROM

        ```python
        import pulumi
        import pulumi_aws as aws

        # Example SES Email Identity
        example_email_identity = aws.ses.EmailIdentity("exampleEmailIdentity", email="user@example.com")
        example_mail_from = aws.ses.MailFrom("exampleMailFrom",
            domain=example_email_identity.email,
            mail_from_domain="mail.example.com")
        ```

        ## Import

        Using `pulumi import`, import MAIL FROM domain using the `domain` attribute. For example:

        ```sh
         $ pulumi import aws:ses/mailFrom:MailFrom example example.com
        ```

        :param str resource_name: The name of the resource.
        :param MailFromArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(MailFromArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 behavior_on_mx_failure: Optional[pulumi.Input[str]] = None,
                 domain: Optional[pulumi.Input[str]] = None,
                 mail_from_domain: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = MailFromArgs.__new__(MailFromArgs)

            __props__.__dict__["behavior_on_mx_failure"] = behavior_on_mx_failure
            if domain is None and not opts.urn:
                raise TypeError("Missing required property 'domain'")
            __props__.__dict__["domain"] = domain
            if mail_from_domain is None and not opts.urn:
                raise TypeError("Missing required property 'mail_from_domain'")
            __props__.__dict__["mail_from_domain"] = mail_from_domain
        super(MailFrom, __self__).__init__(
            'aws:ses/mailFrom:MailFrom',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            behavior_on_mx_failure: Optional[pulumi.Input[str]] = None,
            domain: Optional[pulumi.Input[str]] = None,
            mail_from_domain: Optional[pulumi.Input[str]] = None) -> 'MailFrom':
        """
        Get an existing MailFrom resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] behavior_on_mx_failure: The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        :param pulumi.Input[str] domain: Verified domain name or email identity to generate DKIM tokens for.
        :param pulumi.Input[str] mail_from_domain: Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)
               
               The following arguments are optional:
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _MailFromState.__new__(_MailFromState)

        __props__.__dict__["behavior_on_mx_failure"] = behavior_on_mx_failure
        __props__.__dict__["domain"] = domain
        __props__.__dict__["mail_from_domain"] = mail_from_domain
        return MailFrom(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="behaviorOnMxFailure")
    def behavior_on_mx_failure(self) -> pulumi.Output[Optional[str]]:
        """
        The action that you want Amazon SES to take if it cannot successfully read the required MX record when you send an email. Defaults to `UseDefaultValue`. See the [SES API documentation](https://docs.aws.amazon.com/ses/latest/APIReference/API_SetIdentityMailFromDomain.html) for more information.
        """
        return pulumi.get(self, "behavior_on_mx_failure")

    @property
    @pulumi.getter
    def domain(self) -> pulumi.Output[str]:
        """
        Verified domain name or email identity to generate DKIM tokens for.
        """
        return pulumi.get(self, "domain")

    @property
    @pulumi.getter(name="mailFromDomain")
    def mail_from_domain(self) -> pulumi.Output[str]:
        """
        Subdomain (of above domain) which is to be used as MAIL FROM address (Required for DMARC validation)

        The following arguments are optional:
        """
        return pulumi.get(self, "mail_from_domain")

