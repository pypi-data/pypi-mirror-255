# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['DomainPermissionsArgs', 'DomainPermissions']

@pulumi.input_type
class DomainPermissionsArgs:
    def __init__(__self__, *,
                 domain: pulumi.Input[str],
                 policy_document: pulumi.Input[str],
                 domain_owner: Optional[pulumi.Input[str]] = None,
                 policy_revision: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a DomainPermissions resource.
        :param pulumi.Input[str] domain: The name of the domain on which to set the resource policy.
        :param pulumi.Input[str] policy_document: A JSON policy string to be set as the access control resource policy on the provided domain.
        :param pulumi.Input[str] domain_owner: The account number of the AWS account that owns the domain.
        :param pulumi.Input[str] policy_revision: The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        """
        pulumi.set(__self__, "domain", domain)
        pulumi.set(__self__, "policy_document", policy_document)
        if domain_owner is not None:
            pulumi.set(__self__, "domain_owner", domain_owner)
        if policy_revision is not None:
            pulumi.set(__self__, "policy_revision", policy_revision)

    @property
    @pulumi.getter
    def domain(self) -> pulumi.Input[str]:
        """
        The name of the domain on which to set the resource policy.
        """
        return pulumi.get(self, "domain")

    @domain.setter
    def domain(self, value: pulumi.Input[str]):
        pulumi.set(self, "domain", value)

    @property
    @pulumi.getter(name="policyDocument")
    def policy_document(self) -> pulumi.Input[str]:
        """
        A JSON policy string to be set as the access control resource policy on the provided domain.
        """
        return pulumi.get(self, "policy_document")

    @policy_document.setter
    def policy_document(self, value: pulumi.Input[str]):
        pulumi.set(self, "policy_document", value)

    @property
    @pulumi.getter(name="domainOwner")
    def domain_owner(self) -> Optional[pulumi.Input[str]]:
        """
        The account number of the AWS account that owns the domain.
        """
        return pulumi.get(self, "domain_owner")

    @domain_owner.setter
    def domain_owner(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain_owner", value)

    @property
    @pulumi.getter(name="policyRevision")
    def policy_revision(self) -> Optional[pulumi.Input[str]]:
        """
        The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        """
        return pulumi.get(self, "policy_revision")

    @policy_revision.setter
    def policy_revision(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_revision", value)


@pulumi.input_type
class _DomainPermissionsState:
    def __init__(__self__, *,
                 domain: Optional[pulumi.Input[str]] = None,
                 domain_owner: Optional[pulumi.Input[str]] = None,
                 policy_document: Optional[pulumi.Input[str]] = None,
                 policy_revision: Optional[pulumi.Input[str]] = None,
                 resource_arn: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering DomainPermissions resources.
        :param pulumi.Input[str] domain: The name of the domain on which to set the resource policy.
        :param pulumi.Input[str] domain_owner: The account number of the AWS account that owns the domain.
        :param pulumi.Input[str] policy_document: A JSON policy string to be set as the access control resource policy on the provided domain.
        :param pulumi.Input[str] policy_revision: The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        :param pulumi.Input[str] resource_arn: The ARN of the resource associated with the resource policy.
        """
        if domain is not None:
            pulumi.set(__self__, "domain", domain)
        if domain_owner is not None:
            pulumi.set(__self__, "domain_owner", domain_owner)
        if policy_document is not None:
            pulumi.set(__self__, "policy_document", policy_document)
        if policy_revision is not None:
            pulumi.set(__self__, "policy_revision", policy_revision)
        if resource_arn is not None:
            pulumi.set(__self__, "resource_arn", resource_arn)

    @property
    @pulumi.getter
    def domain(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the domain on which to set the resource policy.
        """
        return pulumi.get(self, "domain")

    @domain.setter
    def domain(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain", value)

    @property
    @pulumi.getter(name="domainOwner")
    def domain_owner(self) -> Optional[pulumi.Input[str]]:
        """
        The account number of the AWS account that owns the domain.
        """
        return pulumi.get(self, "domain_owner")

    @domain_owner.setter
    def domain_owner(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain_owner", value)

    @property
    @pulumi.getter(name="policyDocument")
    def policy_document(self) -> Optional[pulumi.Input[str]]:
        """
        A JSON policy string to be set as the access control resource policy on the provided domain.
        """
        return pulumi.get(self, "policy_document")

    @policy_document.setter
    def policy_document(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_document", value)

    @property
    @pulumi.getter(name="policyRevision")
    def policy_revision(self) -> Optional[pulumi.Input[str]]:
        """
        The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        """
        return pulumi.get(self, "policy_revision")

    @policy_revision.setter
    def policy_revision(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "policy_revision", value)

    @property
    @pulumi.getter(name="resourceArn")
    def resource_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the resource associated with the resource policy.
        """
        return pulumi.get(self, "resource_arn")

    @resource_arn.setter
    def resource_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "resource_arn", value)


class DomainPermissions(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 domain: Optional[pulumi.Input[str]] = None,
                 domain_owner: Optional[pulumi.Input[str]] = None,
                 policy_document: Optional[pulumi.Input[str]] = None,
                 policy_revision: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a CodeArtifact Domains Permissions Policy Resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_key = aws.kms.Key("exampleKey", description="domain key")
        example_domain = aws.codeartifact.Domain("exampleDomain",
            domain="example",
            encryption_key=example_key.arn)
        test_policy_document = aws.iam.get_policy_document_output(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="*",
                identifiers=["*"],
            )],
            actions=["codeartifact:CreateRepository"],
            resources=[example_domain.arn],
        )])
        test_domain_permissions = aws.codeartifact.DomainPermissions("testDomainPermissions",
            domain=example_domain.domain,
            policy_document=test_policy_document.json)
        ```

        ## Import

        Using `pulumi import`, import CodeArtifact Domain Permissions Policies using the CodeArtifact Domain ARN. For example:

        ```sh
         $ pulumi import aws:codeartifact/domainPermissions:DomainPermissions example arn:aws:codeartifact:us-west-2:012345678912:domain/tf-acc-test-1928056699409417367
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] domain: The name of the domain on which to set the resource policy.
        :param pulumi.Input[str] domain_owner: The account number of the AWS account that owns the domain.
        :param pulumi.Input[str] policy_document: A JSON policy string to be set as the access control resource policy on the provided domain.
        :param pulumi.Input[str] policy_revision: The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: DomainPermissionsArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a CodeArtifact Domains Permissions Policy Resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_key = aws.kms.Key("exampleKey", description="domain key")
        example_domain = aws.codeartifact.Domain("exampleDomain",
            domain="example",
            encryption_key=example_key.arn)
        test_policy_document = aws.iam.get_policy_document_output(statements=[aws.iam.GetPolicyDocumentStatementArgs(
            effect="Allow",
            principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
                type="*",
                identifiers=["*"],
            )],
            actions=["codeartifact:CreateRepository"],
            resources=[example_domain.arn],
        )])
        test_domain_permissions = aws.codeartifact.DomainPermissions("testDomainPermissions",
            domain=example_domain.domain,
            policy_document=test_policy_document.json)
        ```

        ## Import

        Using `pulumi import`, import CodeArtifact Domain Permissions Policies using the CodeArtifact Domain ARN. For example:

        ```sh
         $ pulumi import aws:codeartifact/domainPermissions:DomainPermissions example arn:aws:codeartifact:us-west-2:012345678912:domain/tf-acc-test-1928056699409417367
        ```

        :param str resource_name: The name of the resource.
        :param DomainPermissionsArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(DomainPermissionsArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 domain: Optional[pulumi.Input[str]] = None,
                 domain_owner: Optional[pulumi.Input[str]] = None,
                 policy_document: Optional[pulumi.Input[str]] = None,
                 policy_revision: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = DomainPermissionsArgs.__new__(DomainPermissionsArgs)

            if domain is None and not opts.urn:
                raise TypeError("Missing required property 'domain'")
            __props__.__dict__["domain"] = domain
            __props__.__dict__["domain_owner"] = domain_owner
            if policy_document is None and not opts.urn:
                raise TypeError("Missing required property 'policy_document'")
            __props__.__dict__["policy_document"] = policy_document
            __props__.__dict__["policy_revision"] = policy_revision
            __props__.__dict__["resource_arn"] = None
        super(DomainPermissions, __self__).__init__(
            'aws:codeartifact/domainPermissions:DomainPermissions',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            domain: Optional[pulumi.Input[str]] = None,
            domain_owner: Optional[pulumi.Input[str]] = None,
            policy_document: Optional[pulumi.Input[str]] = None,
            policy_revision: Optional[pulumi.Input[str]] = None,
            resource_arn: Optional[pulumi.Input[str]] = None) -> 'DomainPermissions':
        """
        Get an existing DomainPermissions resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] domain: The name of the domain on which to set the resource policy.
        :param pulumi.Input[str] domain_owner: The account number of the AWS account that owns the domain.
        :param pulumi.Input[str] policy_document: A JSON policy string to be set as the access control resource policy on the provided domain.
        :param pulumi.Input[str] policy_revision: The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        :param pulumi.Input[str] resource_arn: The ARN of the resource associated with the resource policy.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _DomainPermissionsState.__new__(_DomainPermissionsState)

        __props__.__dict__["domain"] = domain
        __props__.__dict__["domain_owner"] = domain_owner
        __props__.__dict__["policy_document"] = policy_document
        __props__.__dict__["policy_revision"] = policy_revision
        __props__.__dict__["resource_arn"] = resource_arn
        return DomainPermissions(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def domain(self) -> pulumi.Output[str]:
        """
        The name of the domain on which to set the resource policy.
        """
        return pulumi.get(self, "domain")

    @property
    @pulumi.getter(name="domainOwner")
    def domain_owner(self) -> pulumi.Output[str]:
        """
        The account number of the AWS account that owns the domain.
        """
        return pulumi.get(self, "domain_owner")

    @property
    @pulumi.getter(name="policyDocument")
    def policy_document(self) -> pulumi.Output[str]:
        """
        A JSON policy string to be set as the access control resource policy on the provided domain.
        """
        return pulumi.get(self, "policy_document")

    @property
    @pulumi.getter(name="policyRevision")
    def policy_revision(self) -> pulumi.Output[str]:
        """
        The current revision of the resource policy to be set. This revision is used for optimistic locking, which prevents others from overwriting your changes to the domain's resource policy.
        """
        return pulumi.get(self, "policy_revision")

    @property
    @pulumi.getter(name="resourceArn")
    def resource_arn(self) -> pulumi.Output[str]:
        """
        The ARN of the resource associated with the resource policy.
        """
        return pulumi.get(self, "resource_arn")

