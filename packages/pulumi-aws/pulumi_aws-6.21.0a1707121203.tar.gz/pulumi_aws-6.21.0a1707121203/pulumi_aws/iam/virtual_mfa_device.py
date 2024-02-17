# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['VirtualMfaDeviceArgs', 'VirtualMfaDevice']

@pulumi.input_type
class VirtualMfaDeviceArgs:
    def __init__(__self__, *,
                 virtual_mfa_device_name: pulumi.Input[str],
                 path: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a VirtualMfaDevice resource.
        :param pulumi.Input[str] virtual_mfa_device_name: The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        :param pulumi.Input[str] path: The path for the virtual MFA device.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "virtual_mfa_device_name", virtual_mfa_device_name)
        if path is not None:
            pulumi.set(__self__, "path", path)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="virtualMfaDeviceName")
    def virtual_mfa_device_name(self) -> pulumi.Input[str]:
        """
        The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        """
        return pulumi.get(self, "virtual_mfa_device_name")

    @virtual_mfa_device_name.setter
    def virtual_mfa_device_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "virtual_mfa_device_name", value)

    @property
    @pulumi.getter
    def path(self) -> Optional[pulumi.Input[str]]:
        """
        The path for the virtual MFA device.
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "path", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _VirtualMfaDeviceState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 base32_string_seed: Optional[pulumi.Input[str]] = None,
                 enable_date: Optional[pulumi.Input[str]] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 qr_code_png: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 user_name: Optional[pulumi.Input[str]] = None,
                 virtual_mfa_device_name: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering VirtualMfaDevice resources.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) specifying the virtual mfa device.
        :param pulumi.Input[str] base32_string_seed: The base32 seed defined as specified in [RFC3548](https://tools.ietf.org/html/rfc3548.txt). The `base_32_string_seed` is base64-encoded.
        :param pulumi.Input[str] enable_date: The date and time when the virtual MFA device was enabled.
        :param pulumi.Input[str] path: The path for the virtual MFA device.
        :param pulumi.Input[str] qr_code_png: A QR code PNG image that encodes `otpauth://totp/$virtualMFADeviceName@$AccountName?secret=$Base32String` where `$virtualMFADeviceName` is one of the create call arguments. AccountName is the user name if set (otherwise, the account ID), and Base32String is the seed in base32 format.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[str] user_name: The associated IAM User name if the virtual MFA device is enabled.
        :param pulumi.Input[str] virtual_mfa_device_name: The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if base32_string_seed is not None:
            pulumi.set(__self__, "base32_string_seed", base32_string_seed)
        if enable_date is not None:
            pulumi.set(__self__, "enable_date", enable_date)
        if path is not None:
            pulumi.set(__self__, "path", path)
        if qr_code_png is not None:
            pulumi.set(__self__, "qr_code_png", qr_code_png)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)
        if user_name is not None:
            pulumi.set(__self__, "user_name", user_name)
        if virtual_mfa_device_name is not None:
            pulumi.set(__self__, "virtual_mfa_device_name", virtual_mfa_device_name)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Resource Name (ARN) specifying the virtual mfa device.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="base32StringSeed")
    def base32_string_seed(self) -> Optional[pulumi.Input[str]]:
        """
        The base32 seed defined as specified in [RFC3548](https://tools.ietf.org/html/rfc3548.txt). The `base_32_string_seed` is base64-encoded.
        """
        return pulumi.get(self, "base32_string_seed")

    @base32_string_seed.setter
    def base32_string_seed(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "base32_string_seed", value)

    @property
    @pulumi.getter(name="enableDate")
    def enable_date(self) -> Optional[pulumi.Input[str]]:
        """
        The date and time when the virtual MFA device was enabled.
        """
        return pulumi.get(self, "enable_date")

    @enable_date.setter
    def enable_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "enable_date", value)

    @property
    @pulumi.getter
    def path(self) -> Optional[pulumi.Input[str]]:
        """
        The path for the virtual MFA device.
        """
        return pulumi.get(self, "path")

    @path.setter
    def path(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "path", value)

    @property
    @pulumi.getter(name="qrCodePng")
    def qr_code_png(self) -> Optional[pulumi.Input[str]]:
        """
        A QR code PNG image that encodes `otpauth://totp/$virtualMFADeviceName@$AccountName?secret=$Base32String` where `$virtualMFADeviceName` is one of the create call arguments. AccountName is the user name if set (otherwise, the account ID), and Base32String is the seed in base32 format.
        """
        return pulumi.get(self, "qr_code_png")

    @qr_code_png.setter
    def qr_code_png(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "qr_code_png", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> Optional[pulumi.Input[str]]:
        """
        The associated IAM User name if the virtual MFA device is enabled.
        """
        return pulumi.get(self, "user_name")

    @user_name.setter
    def user_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_name", value)

    @property
    @pulumi.getter(name="virtualMfaDeviceName")
    def virtual_mfa_device_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        """
        return pulumi.get(self, "virtual_mfa_device_name")

    @virtual_mfa_device_name.setter
    def virtual_mfa_device_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "virtual_mfa_device_name", value)


class VirtualMfaDevice(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 virtual_mfa_device_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides an IAM Virtual MFA Device.

        > **Note:** All attributes will be stored in the raw state as plain-text.
        **Note:** A virtual MFA device cannot be directly associated with an IAM User from the provider.
          To associate the virtual MFA device with a user and enable it, use the code returned in either `base_32_string_seed` or `qr_code_png` to generate TOTP authentication codes.
          The authentication codes can then be used with the AWS CLI command [`aws iam enable-mfa-device`](https://docs.aws.amazon.com/cli/latest/reference/iam/enable-mfa-device.html) or the AWS API call [`EnableMFADevice`](https://docs.aws.amazon.com/IAM/latest/APIReference/API_EnableMFADevice.html).

        ## Example Usage

        **Using certs on file:**

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.iam.VirtualMfaDevice("example", virtual_mfa_device_name="example")
        ```

        ## Import

        Using `pulumi import`, import IAM Virtual MFA Devices using the `arn`. For example:

        ```sh
         $ pulumi import aws:iam/virtualMfaDevice:VirtualMfaDevice example arn:aws:iam::123456789012:mfa/example
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] path: The path for the virtual MFA device.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[str] virtual_mfa_device_name: The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: VirtualMfaDeviceArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an IAM Virtual MFA Device.

        > **Note:** All attributes will be stored in the raw state as plain-text.
        **Note:** A virtual MFA device cannot be directly associated with an IAM User from the provider.
          To associate the virtual MFA device with a user and enable it, use the code returned in either `base_32_string_seed` or `qr_code_png` to generate TOTP authentication codes.
          The authentication codes can then be used with the AWS CLI command [`aws iam enable-mfa-device`](https://docs.aws.amazon.com/cli/latest/reference/iam/enable-mfa-device.html) or the AWS API call [`EnableMFADevice`](https://docs.aws.amazon.com/IAM/latest/APIReference/API_EnableMFADevice.html).

        ## Example Usage

        **Using certs on file:**

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.iam.VirtualMfaDevice("example", virtual_mfa_device_name="example")
        ```

        ## Import

        Using `pulumi import`, import IAM Virtual MFA Devices using the `arn`. For example:

        ```sh
         $ pulumi import aws:iam/virtualMfaDevice:VirtualMfaDevice example arn:aws:iam::123456789012:mfa/example
        ```

        :param str resource_name: The name of the resource.
        :param VirtualMfaDeviceArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(VirtualMfaDeviceArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 path: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 virtual_mfa_device_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = VirtualMfaDeviceArgs.__new__(VirtualMfaDeviceArgs)

            __props__.__dict__["path"] = path
            __props__.__dict__["tags"] = tags
            if virtual_mfa_device_name is None and not opts.urn:
                raise TypeError("Missing required property 'virtual_mfa_device_name'")
            __props__.__dict__["virtual_mfa_device_name"] = virtual_mfa_device_name
            __props__.__dict__["arn"] = None
            __props__.__dict__["base32_string_seed"] = None
            __props__.__dict__["enable_date"] = None
            __props__.__dict__["qr_code_png"] = None
            __props__.__dict__["tags_all"] = None
            __props__.__dict__["user_name"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(VirtualMfaDevice, __self__).__init__(
            'aws:iam/virtualMfaDevice:VirtualMfaDevice',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            base32_string_seed: Optional[pulumi.Input[str]] = None,
            enable_date: Optional[pulumi.Input[str]] = None,
            path: Optional[pulumi.Input[str]] = None,
            qr_code_png: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            user_name: Optional[pulumi.Input[str]] = None,
            virtual_mfa_device_name: Optional[pulumi.Input[str]] = None) -> 'VirtualMfaDevice':
        """
        Get an existing VirtualMfaDevice resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The Amazon Resource Name (ARN) specifying the virtual mfa device.
        :param pulumi.Input[str] base32_string_seed: The base32 seed defined as specified in [RFC3548](https://tools.ietf.org/html/rfc3548.txt). The `base_32_string_seed` is base64-encoded.
        :param pulumi.Input[str] enable_date: The date and time when the virtual MFA device was enabled.
        :param pulumi.Input[str] path: The path for the virtual MFA device.
        :param pulumi.Input[str] qr_code_png: A QR code PNG image that encodes `otpauth://totp/$virtualMFADeviceName@$AccountName?secret=$Base32String` where `$virtualMFADeviceName` is one of the create call arguments. AccountName is the user name if set (otherwise, the account ID), and Base32String is the seed in base32 format.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[str] user_name: The associated IAM User name if the virtual MFA device is enabled.
        :param pulumi.Input[str] virtual_mfa_device_name: The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _VirtualMfaDeviceState.__new__(_VirtualMfaDeviceState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["base32_string_seed"] = base32_string_seed
        __props__.__dict__["enable_date"] = enable_date
        __props__.__dict__["path"] = path
        __props__.__dict__["qr_code_png"] = qr_code_png
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        __props__.__dict__["user_name"] = user_name
        __props__.__dict__["virtual_mfa_device_name"] = virtual_mfa_device_name
        return VirtualMfaDevice(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The Amazon Resource Name (ARN) specifying the virtual mfa device.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="base32StringSeed")
    def base32_string_seed(self) -> pulumi.Output[str]:
        """
        The base32 seed defined as specified in [RFC3548](https://tools.ietf.org/html/rfc3548.txt). The `base_32_string_seed` is base64-encoded.
        """
        return pulumi.get(self, "base32_string_seed")

    @property
    @pulumi.getter(name="enableDate")
    def enable_date(self) -> pulumi.Output[str]:
        """
        The date and time when the virtual MFA device was enabled.
        """
        return pulumi.get(self, "enable_date")

    @property
    @pulumi.getter
    def path(self) -> pulumi.Output[Optional[str]]:
        """
        The path for the virtual MFA device.
        """
        return pulumi.get(self, "path")

    @property
    @pulumi.getter(name="qrCodePng")
    def qr_code_png(self) -> pulumi.Output[str]:
        """
        A QR code PNG image that encodes `otpauth://totp/$virtualMFADeviceName@$AccountName?secret=$Base32String` where `$virtualMFADeviceName` is one of the create call arguments. AccountName is the user name if set (otherwise, the account ID), and Base32String is the seed in base32 format.
        """
        return pulumi.get(self, "qr_code_png")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Map of resource tags for the virtual mfa device. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> pulumi.Output[str]:
        """
        The associated IAM User name if the virtual MFA device is enabled.
        """
        return pulumi.get(self, "user_name")

    @property
    @pulumi.getter(name="virtualMfaDeviceName")
    def virtual_mfa_device_name(self) -> pulumi.Output[str]:
        """
        The name of the virtual MFA device. Use with path to uniquely identify a virtual MFA device.
        """
        return pulumi.get(self, "virtual_mfa_device_name")

