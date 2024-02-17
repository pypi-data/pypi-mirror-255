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

__all__ = ['RepositoryAssociationArgs', 'RepositoryAssociation']

@pulumi.input_type
class RepositoryAssociationArgs:
    def __init__(__self__, *,
                 repository: pulumi.Input['RepositoryAssociationRepositoryArgs'],
                 kms_key_details: Optional[pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a RepositoryAssociation resource.
        :param pulumi.Input['RepositoryAssociationRepositoryArgs'] repository: An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.
               
               The following arguments are optional:
        :param pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs'] kms_key_details: An object describing the KMS key to asssociate. Block is documented below.
        """
        pulumi.set(__self__, "repository", repository)
        if kms_key_details is not None:
            pulumi.set(__self__, "kms_key_details", kms_key_details)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter
    def repository(self) -> pulumi.Input['RepositoryAssociationRepositoryArgs']:
        """
        An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.

        The following arguments are optional:
        """
        return pulumi.get(self, "repository")

    @repository.setter
    def repository(self, value: pulumi.Input['RepositoryAssociationRepositoryArgs']):
        pulumi.set(self, "repository", value)

    @property
    @pulumi.getter(name="kmsKeyDetails")
    def kms_key_details(self) -> Optional[pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs']]:
        """
        An object describing the KMS key to asssociate. Block is documented below.
        """
        return pulumi.get(self, "kms_key_details")

    @kms_key_details.setter
    def kms_key_details(self, value: Optional[pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs']]):
        pulumi.set(self, "kms_key_details", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _RepositoryAssociationState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 association_id: Optional[pulumi.Input[str]] = None,
                 connection_arn: Optional[pulumi.Input[str]] = None,
                 kms_key_details: Optional[pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 owner: Optional[pulumi.Input[str]] = None,
                 provider_type: Optional[pulumi.Input[str]] = None,
                 repository: Optional[pulumi.Input['RepositoryAssociationRepositoryArgs']] = None,
                 s3_repository_details: Optional[pulumi.Input[Sequence[pulumi.Input['RepositoryAssociationS3RepositoryDetailArgs']]]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 state_reason: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering RepositoryAssociation resources.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) identifying the repository association.
        :param pulumi.Input[str] association_id: The ID of the repository association.
        :param pulumi.Input[str] connection_arn: The Amazon Resource Name (ARN) of an AWS CodeStar Connections connection.
        :param pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs'] kms_key_details: An object describing the KMS key to asssociate. Block is documented below.
        :param pulumi.Input[str] name: The name of the third party source repository.
        :param pulumi.Input[str] owner: The username for the account that owns the repository.
        :param pulumi.Input[str] provider_type: The provider type of the repository association.
        :param pulumi.Input['RepositoryAssociationRepositoryArgs'] repository: An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.
               
               The following arguments are optional:
        :param pulumi.Input[str] state: The state of the repository association.
        :param pulumi.Input[str] state_reason: A description of why the repository association is in the current state.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if association_id is not None:
            pulumi.set(__self__, "association_id", association_id)
        if connection_arn is not None:
            pulumi.set(__self__, "connection_arn", connection_arn)
        if kms_key_details is not None:
            pulumi.set(__self__, "kms_key_details", kms_key_details)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if owner is not None:
            pulumi.set(__self__, "owner", owner)
        if provider_type is not None:
            pulumi.set(__self__, "provider_type", provider_type)
        if repository is not None:
            pulumi.set(__self__, "repository", repository)
        if s3_repository_details is not None:
            pulumi.set(__self__, "s3_repository_details", s3_repository_details)
        if state is not None:
            pulumi.set(__self__, "state", state)
        if state_reason is not None:
            pulumi.set(__self__, "state_reason", state_reason)
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
        The Amazon Resource Name (ARN) identifying the repository association.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="associationId")
    def association_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the repository association.
        """
        return pulumi.get(self, "association_id")

    @association_id.setter
    def association_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "association_id", value)

    @property
    @pulumi.getter(name="connectionArn")
    def connection_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) of an AWS CodeStar Connections connection.
        """
        return pulumi.get(self, "connection_arn")

    @connection_arn.setter
    def connection_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "connection_arn", value)

    @property
    @pulumi.getter(name="kmsKeyDetails")
    def kms_key_details(self) -> Optional[pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs']]:
        """
        An object describing the KMS key to asssociate. Block is documented below.
        """
        return pulumi.get(self, "kms_key_details")

    @kms_key_details.setter
    def kms_key_details(self, value: Optional[pulumi.Input['RepositoryAssociationKmsKeyDetailsArgs']]):
        pulumi.set(self, "kms_key_details", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the third party source repository.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter
    def owner(self) -> Optional[pulumi.Input[str]]:
        """
        The username for the account that owns the repository.
        """
        return pulumi.get(self, "owner")

    @owner.setter
    def owner(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "owner", value)

    @property
    @pulumi.getter(name="providerType")
    def provider_type(self) -> Optional[pulumi.Input[str]]:
        """
        The provider type of the repository association.
        """
        return pulumi.get(self, "provider_type")

    @provider_type.setter
    def provider_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "provider_type", value)

    @property
    @pulumi.getter
    def repository(self) -> Optional[pulumi.Input['RepositoryAssociationRepositoryArgs']]:
        """
        An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.

        The following arguments are optional:
        """
        return pulumi.get(self, "repository")

    @repository.setter
    def repository(self, value: Optional[pulumi.Input['RepositoryAssociationRepositoryArgs']]):
        pulumi.set(self, "repository", value)

    @property
    @pulumi.getter(name="s3RepositoryDetails")
    def s3_repository_details(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['RepositoryAssociationS3RepositoryDetailArgs']]]]:
        return pulumi.get(self, "s3_repository_details")

    @s3_repository_details.setter
    def s3_repository_details(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['RepositoryAssociationS3RepositoryDetailArgs']]]]):
        pulumi.set(self, "s3_repository_details", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input[str]]:
        """
        The state of the repository association.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="stateReason")
    def state_reason(self) -> Optional[pulumi.Input[str]]:
        """
        A description of why the repository association is in the current state.
        """
        return pulumi.get(self, "state_reason")

    @state_reason.setter
    def state_reason(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "state_reason", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
        pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")

        return pulumi.get(self, "tags_all")

    @tags_all.setter
    def tags_all(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags_all", value)


class RepositoryAssociation(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 kms_key_details: Optional[pulumi.Input[pulumi.InputType['RepositoryAssociationKmsKeyDetailsArgs']]] = None,
                 repository: Optional[pulumi.Input[pulumi.InputType['RepositoryAssociationRepositoryArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Resource for managing an AWS CodeGuru Reviewer Repository Association.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_key = aws.kms.Key("exampleKey")
        example_repository = aws.codecommit.Repository("exampleRepository", repository_name="example-repo")
        example_repository_association = aws.codegurureviewer.RepositoryAssociation("exampleRepositoryAssociation",
            repository=aws.codegurureviewer.RepositoryAssociationRepositoryArgs(
                codecommit=aws.codegurureviewer.RepositoryAssociationRepositoryCodecommitArgs(
                    name=example_repository.repository_name,
                ),
            ),
            kms_key_details=aws.codegurureviewer.RepositoryAssociationKmsKeyDetailsArgs(
                encryption_option="CUSTOMER_MANAGED_CMK",
                kms_key_id=example_key.key_id,
            ))
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['RepositoryAssociationKmsKeyDetailsArgs']] kms_key_details: An object describing the KMS key to asssociate. Block is documented below.
        :param pulumi.Input[pulumi.InputType['RepositoryAssociationRepositoryArgs']] repository: An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.
               
               The following arguments are optional:
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RepositoryAssociationArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing an AWS CodeGuru Reviewer Repository Association.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_key = aws.kms.Key("exampleKey")
        example_repository = aws.codecommit.Repository("exampleRepository", repository_name="example-repo")
        example_repository_association = aws.codegurureviewer.RepositoryAssociation("exampleRepositoryAssociation",
            repository=aws.codegurureviewer.RepositoryAssociationRepositoryArgs(
                codecommit=aws.codegurureviewer.RepositoryAssociationRepositoryCodecommitArgs(
                    name=example_repository.repository_name,
                ),
            ),
            kms_key_details=aws.codegurureviewer.RepositoryAssociationKmsKeyDetailsArgs(
                encryption_option="CUSTOMER_MANAGED_CMK",
                kms_key_id=example_key.key_id,
            ))
        ```

        :param str resource_name: The name of the resource.
        :param RepositoryAssociationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RepositoryAssociationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 kms_key_details: Optional[pulumi.Input[pulumi.InputType['RepositoryAssociationKmsKeyDetailsArgs']]] = None,
                 repository: Optional[pulumi.Input[pulumi.InputType['RepositoryAssociationRepositoryArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RepositoryAssociationArgs.__new__(RepositoryAssociationArgs)

            __props__.__dict__["kms_key_details"] = kms_key_details
            if repository is None and not opts.urn:
                raise TypeError("Missing required property 'repository'")
            __props__.__dict__["repository"] = repository
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["association_id"] = None
            __props__.__dict__["connection_arn"] = None
            __props__.__dict__["name"] = None
            __props__.__dict__["owner"] = None
            __props__.__dict__["provider_type"] = None
            __props__.__dict__["s3_repository_details"] = None
            __props__.__dict__["state"] = None
            __props__.__dict__["state_reason"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(RepositoryAssociation, __self__).__init__(
            'aws:codegurureviewer/repositoryAssociation:RepositoryAssociation',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            association_id: Optional[pulumi.Input[str]] = None,
            connection_arn: Optional[pulumi.Input[str]] = None,
            kms_key_details: Optional[pulumi.Input[pulumi.InputType['RepositoryAssociationKmsKeyDetailsArgs']]] = None,
            name: Optional[pulumi.Input[str]] = None,
            owner: Optional[pulumi.Input[str]] = None,
            provider_type: Optional[pulumi.Input[str]] = None,
            repository: Optional[pulumi.Input[pulumi.InputType['RepositoryAssociationRepositoryArgs']]] = None,
            s3_repository_details: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['RepositoryAssociationS3RepositoryDetailArgs']]]]] = None,
            state: Optional[pulumi.Input[str]] = None,
            state_reason: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'RepositoryAssociation':
        """
        Get an existing RepositoryAssociation resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) identifying the repository association.
        :param pulumi.Input[str] association_id: The ID of the repository association.
        :param pulumi.Input[str] connection_arn: The Amazon Resource Name (ARN) of an AWS CodeStar Connections connection.
        :param pulumi.Input[pulumi.InputType['RepositoryAssociationKmsKeyDetailsArgs']] kms_key_details: An object describing the KMS key to asssociate. Block is documented below.
        :param pulumi.Input[str] name: The name of the third party source repository.
        :param pulumi.Input[str] owner: The username for the account that owns the repository.
        :param pulumi.Input[str] provider_type: The provider type of the repository association.
        :param pulumi.Input[pulumi.InputType['RepositoryAssociationRepositoryArgs']] repository: An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.
               
               The following arguments are optional:
        :param pulumi.Input[str] state: The state of the repository association.
        :param pulumi.Input[str] state_reason: A description of why the repository association is in the current state.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _RepositoryAssociationState.__new__(_RepositoryAssociationState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["association_id"] = association_id
        __props__.__dict__["connection_arn"] = connection_arn
        __props__.__dict__["kms_key_details"] = kms_key_details
        __props__.__dict__["name"] = name
        __props__.__dict__["owner"] = owner
        __props__.__dict__["provider_type"] = provider_type
        __props__.__dict__["repository"] = repository
        __props__.__dict__["s3_repository_details"] = s3_repository_details
        __props__.__dict__["state"] = state
        __props__.__dict__["state_reason"] = state_reason
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return RepositoryAssociation(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) identifying the repository association.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="associationId")
    def association_id(self) -> pulumi.Output[str]:
        """
        The ID of the repository association.
        """
        return pulumi.get(self, "association_id")

    @property
    @pulumi.getter(name="connectionArn")
    def connection_arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) of an AWS CodeStar Connections connection.
        """
        return pulumi.get(self, "connection_arn")

    @property
    @pulumi.getter(name="kmsKeyDetails")
    def kms_key_details(self) -> pulumi.Output[Optional['outputs.RepositoryAssociationKmsKeyDetails']]:
        """
        An object describing the KMS key to asssociate. Block is documented below.
        """
        return pulumi.get(self, "kms_key_details")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the third party source repository.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter
    def owner(self) -> pulumi.Output[str]:
        """
        The username for the account that owns the repository.
        """
        return pulumi.get(self, "owner")

    @property
    @pulumi.getter(name="providerType")
    def provider_type(self) -> pulumi.Output[str]:
        """
        The provider type of the repository association.
        """
        return pulumi.get(self, "provider_type")

    @property
    @pulumi.getter
    def repository(self) -> pulumi.Output['outputs.RepositoryAssociationRepository']:
        """
        An object describing the repository to associate. Valid values: `bitbucket`, `codecommit`, `github_enterprise_server`, or `s3_bucket`. Block is documented below. Note: for repositories that leverage CodeStar connections (ex. `bitbucket`, `github_enterprise_server`) the connection must be in `Available` status prior to creating this resource.

        The following arguments are optional:
        """
        return pulumi.get(self, "repository")

    @property
    @pulumi.getter(name="s3RepositoryDetails")
    def s3_repository_details(self) -> pulumi.Output[Sequence['outputs.RepositoryAssociationS3RepositoryDetail']]:
        return pulumi.get(self, "s3_repository_details")

    @property
    @pulumi.getter
    def state(self) -> pulumi.Output[str]:
        """
        The state of the repository association.
        """
        return pulumi.get(self, "state")

    @property
    @pulumi.getter(name="stateReason")
    def state_reason(self) -> pulumi.Output[str]:
        """
        A description of why the repository association is in the current state.
        """
        return pulumi.get(self, "state_reason")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> pulumi.Output[Mapping[str, str]]:
        warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
        pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")

        return pulumi.get(self, "tags_all")

