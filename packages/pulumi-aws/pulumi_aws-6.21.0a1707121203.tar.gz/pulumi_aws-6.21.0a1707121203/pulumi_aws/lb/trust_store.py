# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['TrustStoreArgs', 'TrustStore']

@pulumi.input_type
class TrustStoreArgs:
    def __init__(__self__, *,
                 ca_certificates_bundle_s3_bucket: pulumi.Input[str],
                 ca_certificates_bundle_s3_key: pulumi.Input[str],
                 ca_certificates_bundle_s3_object_version: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 name_prefix: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a TrustStore resource.
        :param pulumi.Input[str] ca_certificates_bundle_s3_bucket: S3 Bucket name holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_key: S3 object key holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_object_version: Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        :param pulumi.Input[str] name: Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        :param pulumi.Input[str] name_prefix: Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "ca_certificates_bundle_s3_bucket", ca_certificates_bundle_s3_bucket)
        pulumi.set(__self__, "ca_certificates_bundle_s3_key", ca_certificates_bundle_s3_key)
        if ca_certificates_bundle_s3_object_version is not None:
            pulumi.set(__self__, "ca_certificates_bundle_s3_object_version", ca_certificates_bundle_s3_object_version)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if name_prefix is not None:
            pulumi.set(__self__, "name_prefix", name_prefix)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="caCertificatesBundleS3Bucket")
    def ca_certificates_bundle_s3_bucket(self) -> pulumi.Input[str]:
        """
        S3 Bucket name holding the client certificate CA bundle.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_bucket")

    @ca_certificates_bundle_s3_bucket.setter
    def ca_certificates_bundle_s3_bucket(self, value: pulumi.Input[str]):
        pulumi.set(self, "ca_certificates_bundle_s3_bucket", value)

    @property
    @pulumi.getter(name="caCertificatesBundleS3Key")
    def ca_certificates_bundle_s3_key(self) -> pulumi.Input[str]:
        """
        S3 object key holding the client certificate CA bundle.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_key")

    @ca_certificates_bundle_s3_key.setter
    def ca_certificates_bundle_s3_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "ca_certificates_bundle_s3_key", value)

    @property
    @pulumi.getter(name="caCertificatesBundleS3ObjectVersion")
    def ca_certificates_bundle_s3_object_version(self) -> Optional[pulumi.Input[str]]:
        """
        Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_object_version")

    @ca_certificates_bundle_s3_object_version.setter
    def ca_certificates_bundle_s3_object_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "ca_certificates_bundle_s3_object_version", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="namePrefix")
    def name_prefix(self) -> Optional[pulumi.Input[str]]:
        """
        Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        """
        return pulumi.get(self, "name_prefix")

    @name_prefix.setter
    def name_prefix(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name_prefix", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _TrustStoreState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 arn_suffix: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_bucket: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_key: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_object_version: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 name_prefix: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering TrustStore resources.
        :param pulumi.Input[str] arn: ARN of the Trust Store (matches `id`).
        :param pulumi.Input[str] arn_suffix: ARN suffix for use with CloudWatch Metrics.
        :param pulumi.Input[str] ca_certificates_bundle_s3_bucket: S3 Bucket name holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_key: S3 object key holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_object_version: Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        :param pulumi.Input[str] name: Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        :param pulumi.Input[str] name_prefix: Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if arn_suffix is not None:
            pulumi.set(__self__, "arn_suffix", arn_suffix)
        if ca_certificates_bundle_s3_bucket is not None:
            pulumi.set(__self__, "ca_certificates_bundle_s3_bucket", ca_certificates_bundle_s3_bucket)
        if ca_certificates_bundle_s3_key is not None:
            pulumi.set(__self__, "ca_certificates_bundle_s3_key", ca_certificates_bundle_s3_key)
        if ca_certificates_bundle_s3_object_version is not None:
            pulumi.set(__self__, "ca_certificates_bundle_s3_object_version", ca_certificates_bundle_s3_object_version)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if name_prefix is not None:
            pulumi.set(__self__, "name_prefix", name_prefix)
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
        ARN of the Trust Store (matches `id`).
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="arnSuffix")
    def arn_suffix(self) -> Optional[pulumi.Input[str]]:
        """
        ARN suffix for use with CloudWatch Metrics.
        """
        return pulumi.get(self, "arn_suffix")

    @arn_suffix.setter
    def arn_suffix(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn_suffix", value)

    @property
    @pulumi.getter(name="caCertificatesBundleS3Bucket")
    def ca_certificates_bundle_s3_bucket(self) -> Optional[pulumi.Input[str]]:
        """
        S3 Bucket name holding the client certificate CA bundle.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_bucket")

    @ca_certificates_bundle_s3_bucket.setter
    def ca_certificates_bundle_s3_bucket(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "ca_certificates_bundle_s3_bucket", value)

    @property
    @pulumi.getter(name="caCertificatesBundleS3Key")
    def ca_certificates_bundle_s3_key(self) -> Optional[pulumi.Input[str]]:
        """
        S3 object key holding the client certificate CA bundle.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_key")

    @ca_certificates_bundle_s3_key.setter
    def ca_certificates_bundle_s3_key(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "ca_certificates_bundle_s3_key", value)

    @property
    @pulumi.getter(name="caCertificatesBundleS3ObjectVersion")
    def ca_certificates_bundle_s3_object_version(self) -> Optional[pulumi.Input[str]]:
        """
        Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_object_version")

    @ca_certificates_bundle_s3_object_version.setter
    def ca_certificates_bundle_s3_object_version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "ca_certificates_bundle_s3_object_version", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="namePrefix")
    def name_prefix(self) -> Optional[pulumi.Input[str]]:
        """
        Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        """
        return pulumi.get(self, "name_prefix")

    @name_prefix.setter
    def name_prefix(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name_prefix", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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


class TrustStore(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 ca_certificates_bundle_s3_bucket: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_key: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_object_version: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 name_prefix: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Provides a ELBv2 Trust Store for use with Application Load Balancer Listener resources.

        ## Example Usage
        ### Trust Store Load Balancer Listener

        ```python
        import pulumi
        import pulumi_aws as aws

        test = aws.lb.TrustStore("test",
            ca_certificates_bundle_s3_bucket="...",
            ca_certificates_bundle_s3_key="...")
        example = aws.lb.Listener("example",
            load_balancer_arn=aws_lb["example"]["id"],
            default_actions=[aws.lb.ListenerDefaultActionArgs(
                target_group_arn=aws_lb_target_group["example"]["id"],
                type="forward",
            )],
            mutual_authentication=aws.lb.ListenerMutualAuthenticationArgs(
                mode="verify",
                trust_store_arn=test.arn,
            ))
        ```

        ## Import

        Using `pulumi import`, import Target Groups using their ARN. For example:

        ```sh
         $ pulumi import aws:lb/trustStore:TrustStore example arn:aws:elasticloadbalancing:us-west-2:187416307283:truststore/my-trust-store/20cfe21448b66314
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] ca_certificates_bundle_s3_bucket: S3 Bucket name holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_key: S3 object key holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_object_version: Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        :param pulumi.Input[str] name: Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        :param pulumi.Input[str] name_prefix: Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: TrustStoreArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a ELBv2 Trust Store for use with Application Load Balancer Listener resources.

        ## Example Usage
        ### Trust Store Load Balancer Listener

        ```python
        import pulumi
        import pulumi_aws as aws

        test = aws.lb.TrustStore("test",
            ca_certificates_bundle_s3_bucket="...",
            ca_certificates_bundle_s3_key="...")
        example = aws.lb.Listener("example",
            load_balancer_arn=aws_lb["example"]["id"],
            default_actions=[aws.lb.ListenerDefaultActionArgs(
                target_group_arn=aws_lb_target_group["example"]["id"],
                type="forward",
            )],
            mutual_authentication=aws.lb.ListenerMutualAuthenticationArgs(
                mode="verify",
                trust_store_arn=test.arn,
            ))
        ```

        ## Import

        Using `pulumi import`, import Target Groups using their ARN. For example:

        ```sh
         $ pulumi import aws:lb/trustStore:TrustStore example arn:aws:elasticloadbalancing:us-west-2:187416307283:truststore/my-trust-store/20cfe21448b66314
        ```

        :param str resource_name: The name of the resource.
        :param TrustStoreArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(TrustStoreArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 ca_certificates_bundle_s3_bucket: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_key: Optional[pulumi.Input[str]] = None,
                 ca_certificates_bundle_s3_object_version: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 name_prefix: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = TrustStoreArgs.__new__(TrustStoreArgs)

            if ca_certificates_bundle_s3_bucket is None and not opts.urn:
                raise TypeError("Missing required property 'ca_certificates_bundle_s3_bucket'")
            __props__.__dict__["ca_certificates_bundle_s3_bucket"] = ca_certificates_bundle_s3_bucket
            if ca_certificates_bundle_s3_key is None and not opts.urn:
                raise TypeError("Missing required property 'ca_certificates_bundle_s3_key'")
            __props__.__dict__["ca_certificates_bundle_s3_key"] = ca_certificates_bundle_s3_key
            __props__.__dict__["ca_certificates_bundle_s3_object_version"] = ca_certificates_bundle_s3_object_version
            __props__.__dict__["name"] = name
            __props__.__dict__["name_prefix"] = name_prefix
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["arn_suffix"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(TrustStore, __self__).__init__(
            'aws:lb/trustStore:TrustStore',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            arn_suffix: Optional[pulumi.Input[str]] = None,
            ca_certificates_bundle_s3_bucket: Optional[pulumi.Input[str]] = None,
            ca_certificates_bundle_s3_key: Optional[pulumi.Input[str]] = None,
            ca_certificates_bundle_s3_object_version: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            name_prefix: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'TrustStore':
        """
        Get an existing TrustStore resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: ARN of the Trust Store (matches `id`).
        :param pulumi.Input[str] arn_suffix: ARN suffix for use with CloudWatch Metrics.
        :param pulumi.Input[str] ca_certificates_bundle_s3_bucket: S3 Bucket name holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_key: S3 object key holding the client certificate CA bundle.
        :param pulumi.Input[str] ca_certificates_bundle_s3_object_version: Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        :param pulumi.Input[str] name: Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        :param pulumi.Input[str] name_prefix: Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _TrustStoreState.__new__(_TrustStoreState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["arn_suffix"] = arn_suffix
        __props__.__dict__["ca_certificates_bundle_s3_bucket"] = ca_certificates_bundle_s3_bucket
        __props__.__dict__["ca_certificates_bundle_s3_key"] = ca_certificates_bundle_s3_key
        __props__.__dict__["ca_certificates_bundle_s3_object_version"] = ca_certificates_bundle_s3_object_version
        __props__.__dict__["name"] = name
        __props__.__dict__["name_prefix"] = name_prefix
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return TrustStore(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        ARN of the Trust Store (matches `id`).
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="arnSuffix")
    def arn_suffix(self) -> pulumi.Output[str]:
        """
        ARN suffix for use with CloudWatch Metrics.
        """
        return pulumi.get(self, "arn_suffix")

    @property
    @pulumi.getter(name="caCertificatesBundleS3Bucket")
    def ca_certificates_bundle_s3_bucket(self) -> pulumi.Output[str]:
        """
        S3 Bucket name holding the client certificate CA bundle.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_bucket")

    @property
    @pulumi.getter(name="caCertificatesBundleS3Key")
    def ca_certificates_bundle_s3_key(self) -> pulumi.Output[str]:
        """
        S3 object key holding the client certificate CA bundle.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_key")

    @property
    @pulumi.getter(name="caCertificatesBundleS3ObjectVersion")
    def ca_certificates_bundle_s3_object_version(self) -> pulumi.Output[Optional[str]]:
        """
        Version Id of CA bundle S3 bucket object, if versioned, defaults to latest if omitted.
        """
        return pulumi.get(self, "ca_certificates_bundle_s3_object_version")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Name of the Trust Store. If omitted, the provider will assign a random, unique name. This name must be unique per region per account, can have a maximum of 32 characters, must contain only alphanumeric characters or hyphens, and must not begin or end with a hyphen.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="namePrefix")
    def name_prefix(self) -> pulumi.Output[str]:
        """
        Creates a unique name beginning with the specified prefix. Conflicts with `name`. Cannot be longer than 6 characters.
        """
        return pulumi.get(self, "name_prefix")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Map of tags to assign to the resource. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

