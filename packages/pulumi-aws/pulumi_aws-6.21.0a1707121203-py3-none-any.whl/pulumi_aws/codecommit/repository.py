# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['RepositoryArgs', 'Repository']

@pulumi.input_type
class RepositoryArgs:
    def __init__(__self__, *,
                 repository_name: pulumi.Input[str],
                 default_branch: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a Repository resource.
        :param pulumi.Input[str] repository_name: The name for the repository. This needs to be less than 100 characters.
        :param pulumi.Input[str] default_branch: The default branch of the repository. The branch specified here needs to exist.
        :param pulumi.Input[str] description: The description of the repository. This needs to be less than 1000 characters
        :param pulumi.Input[str] kms_key_id: The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "repository_name", repository_name)
        if default_branch is not None:
            pulumi.set(__self__, "default_branch", default_branch)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if kms_key_id is not None:
            pulumi.set(__self__, "kms_key_id", kms_key_id)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="repositoryName")
    def repository_name(self) -> pulumi.Input[str]:
        """
        The name for the repository. This needs to be less than 100 characters.
        """
        return pulumi.get(self, "repository_name")

    @repository_name.setter
    def repository_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "repository_name", value)

    @property
    @pulumi.getter(name="defaultBranch")
    def default_branch(self) -> Optional[pulumi.Input[str]]:
        """
        The default branch of the repository. The branch specified here needs to exist.
        """
        return pulumi.get(self, "default_branch")

    @default_branch.setter
    def default_branch(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "default_branch", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the repository. This needs to be less than 1000 characters
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="kmsKeyId")
    def kms_key_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        """
        return pulumi.get(self, "kms_key_id")

    @kms_key_id.setter
    def kms_key_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kms_key_id", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _RepositoryState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 clone_url_http: Optional[pulumi.Input[str]] = None,
                 clone_url_ssh: Optional[pulumi.Input[str]] = None,
                 default_branch: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 repository_id: Optional[pulumi.Input[str]] = None,
                 repository_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering Repository resources.
        :param pulumi.Input[str] arn: The ARN of the repository
        :param pulumi.Input[str] clone_url_http: The URL to use for cloning the repository over HTTPS.
        :param pulumi.Input[str] clone_url_ssh: The URL to use for cloning the repository over SSH.
        :param pulumi.Input[str] default_branch: The default branch of the repository. The branch specified here needs to exist.
        :param pulumi.Input[str] description: The description of the repository. This needs to be less than 1000 characters
        :param pulumi.Input[str] kms_key_id: The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        :param pulumi.Input[str] repository_id: The ID of the repository
        :param pulumi.Input[str] repository_name: The name for the repository. This needs to be less than 100 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if clone_url_http is not None:
            pulumi.set(__self__, "clone_url_http", clone_url_http)
        if clone_url_ssh is not None:
            pulumi.set(__self__, "clone_url_ssh", clone_url_ssh)
        if default_branch is not None:
            pulumi.set(__self__, "default_branch", default_branch)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if kms_key_id is not None:
            pulumi.set(__self__, "kms_key_id", kms_key_id)
        if repository_id is not None:
            pulumi.set(__self__, "repository_id", repository_id)
        if repository_name is not None:
            pulumi.set(__self__, "repository_name", repository_name)
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
        The ARN of the repository
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="cloneUrlHttp")
    def clone_url_http(self) -> Optional[pulumi.Input[str]]:
        """
        The URL to use for cloning the repository over HTTPS.
        """
        return pulumi.get(self, "clone_url_http")

    @clone_url_http.setter
    def clone_url_http(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "clone_url_http", value)

    @property
    @pulumi.getter(name="cloneUrlSsh")
    def clone_url_ssh(self) -> Optional[pulumi.Input[str]]:
        """
        The URL to use for cloning the repository over SSH.
        """
        return pulumi.get(self, "clone_url_ssh")

    @clone_url_ssh.setter
    def clone_url_ssh(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "clone_url_ssh", value)

    @property
    @pulumi.getter(name="defaultBranch")
    def default_branch(self) -> Optional[pulumi.Input[str]]:
        """
        The default branch of the repository. The branch specified here needs to exist.
        """
        return pulumi.get(self, "default_branch")

    @default_branch.setter
    def default_branch(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "default_branch", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        The description of the repository. This needs to be less than 1000 characters
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="kmsKeyId")
    def kms_key_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        """
        return pulumi.get(self, "kms_key_id")

    @kms_key_id.setter
    def kms_key_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "kms_key_id", value)

    @property
    @pulumi.getter(name="repositoryId")
    def repository_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the repository
        """
        return pulumi.get(self, "repository_id")

    @repository_id.setter
    def repository_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "repository_id", value)

    @property
    @pulumi.getter(name="repositoryName")
    def repository_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name for the repository. This needs to be less than 100 characters.
        """
        return pulumi.get(self, "repository_name")

    @repository_name.setter
    def repository_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "repository_name", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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


class Repository(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 default_branch: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 repository_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides a CodeCommit Repository Resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        test = aws.codecommit.Repository("test",
            description="This is the Sample App Repository",
            repository_name="MyTestRepository")
        ```
        ### AWS KMS Customer Managed Keys (CMK)

        ```python
        import pulumi
        import pulumi_aws as aws

        test_key = aws.kms.Key("testKey",
            description="test",
            deletion_window_in_days=7)
        test_repository = aws.codecommit.Repository("testRepository",
            repository_name="MyTestRepository",
            description="This is the Sample App Repository",
            kms_key_id=test_key.arn)
        ```

        ## Import

        Using `pulumi import`, import CodeCommit repository using repository name. For example:

        ```sh
         $ pulumi import aws:codecommit/repository:Repository imported ExistingRepo
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] default_branch: The default branch of the repository. The branch specified here needs to exist.
        :param pulumi.Input[str] description: The description of the repository. This needs to be less than 1000 characters
        :param pulumi.Input[str] kms_key_id: The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        :param pulumi.Input[str] repository_name: The name for the repository. This needs to be less than 100 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: RepositoryArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a CodeCommit Repository Resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        test = aws.codecommit.Repository("test",
            description="This is the Sample App Repository",
            repository_name="MyTestRepository")
        ```
        ### AWS KMS Customer Managed Keys (CMK)

        ```python
        import pulumi
        import pulumi_aws as aws

        test_key = aws.kms.Key("testKey",
            description="test",
            deletion_window_in_days=7)
        test_repository = aws.codecommit.Repository("testRepository",
            repository_name="MyTestRepository",
            description="This is the Sample App Repository",
            kms_key_id=test_key.arn)
        ```

        ## Import

        Using `pulumi import`, import CodeCommit repository using repository name. For example:

        ```sh
         $ pulumi import aws:codecommit/repository:Repository imported ExistingRepo
        ```

        :param str resource_name: The name of the resource.
        :param RepositoryArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(RepositoryArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 default_branch: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 kms_key_id: Optional[pulumi.Input[str]] = None,
                 repository_name: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = RepositoryArgs.__new__(RepositoryArgs)

            __props__.__dict__["default_branch"] = default_branch
            __props__.__dict__["description"] = description
            __props__.__dict__["kms_key_id"] = kms_key_id
            if repository_name is None and not opts.urn:
                raise TypeError("Missing required property 'repository_name'")
            __props__.__dict__["repository_name"] = repository_name
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["clone_url_http"] = None
            __props__.__dict__["clone_url_ssh"] = None
            __props__.__dict__["repository_id"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(Repository, __self__).__init__(
            'aws:codecommit/repository:Repository',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            clone_url_http: Optional[pulumi.Input[str]] = None,
            clone_url_ssh: Optional[pulumi.Input[str]] = None,
            default_branch: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            kms_key_id: Optional[pulumi.Input[str]] = None,
            repository_id: Optional[pulumi.Input[str]] = None,
            repository_name: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'Repository':
        """
        Get an existing Repository resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The ARN of the repository
        :param pulumi.Input[str] clone_url_http: The URL to use for cloning the repository over HTTPS.
        :param pulumi.Input[str] clone_url_ssh: The URL to use for cloning the repository over SSH.
        :param pulumi.Input[str] default_branch: The default branch of the repository. The branch specified here needs to exist.
        :param pulumi.Input[str] description: The description of the repository. This needs to be less than 1000 characters
        :param pulumi.Input[str] kms_key_id: The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        :param pulumi.Input[str] repository_id: The ID of the repository
        :param pulumi.Input[str] repository_name: The name for the repository. This needs to be less than 100 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _RepositoryState.__new__(_RepositoryState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["clone_url_http"] = clone_url_http
        __props__.__dict__["clone_url_ssh"] = clone_url_ssh
        __props__.__dict__["default_branch"] = default_branch
        __props__.__dict__["description"] = description
        __props__.__dict__["kms_key_id"] = kms_key_id
        __props__.__dict__["repository_id"] = repository_id
        __props__.__dict__["repository_name"] = repository_name
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return Repository(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The ARN of the repository
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="cloneUrlHttp")
    def clone_url_http(self) -> pulumi.Output[str]:
        """
        The URL to use for cloning the repository over HTTPS.
        """
        return pulumi.get(self, "clone_url_http")

    @property
    @pulumi.getter(name="cloneUrlSsh")
    def clone_url_ssh(self) -> pulumi.Output[str]:
        """
        The URL to use for cloning the repository over SSH.
        """
        return pulumi.get(self, "clone_url_ssh")

    @property
    @pulumi.getter(name="defaultBranch")
    def default_branch(self) -> pulumi.Output[Optional[str]]:
        """
        The default branch of the repository. The branch specified here needs to exist.
        """
        return pulumi.get(self, "default_branch")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        The description of the repository. This needs to be less than 1000 characters
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="kmsKeyId")
    def kms_key_id(self) -> pulumi.Output[str]:
        """
        The ARN of the encryption key. If no key is specified, the default `aws/codecommit`` Amazon Web Services managed key is used.
        """
        return pulumi.get(self, "kms_key_id")

    @property
    @pulumi.getter(name="repositoryId")
    def repository_id(self) -> pulumi.Output[str]:
        """
        The ID of the repository
        """
        return pulumi.get(self, "repository_id")

    @property
    @pulumi.getter(name="repositoryName")
    def repository_name(self) -> pulumi.Output[str]:
        """
        The name for the repository. This needs to be less than 100 characters.
        """
        return pulumi.get(self, "repository_name")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Key-value map of resource tags. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

