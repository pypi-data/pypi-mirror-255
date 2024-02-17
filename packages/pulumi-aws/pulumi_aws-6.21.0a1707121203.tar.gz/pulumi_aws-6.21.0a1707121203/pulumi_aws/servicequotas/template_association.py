# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['TemplateAssociationArgs', 'TemplateAssociation']

@pulumi.input_type
class TemplateAssociationArgs:
    def __init__(__self__, *,
                 skip_destroy: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a TemplateAssociation resource.
        """
        if skip_destroy is not None:
            pulumi.set(__self__, "skip_destroy", skip_destroy)

    @property
    @pulumi.getter(name="skipDestroy")
    def skip_destroy(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "skip_destroy")

    @skip_destroy.setter
    def skip_destroy(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "skip_destroy", value)


@pulumi.input_type
class _TemplateAssociationState:
    def __init__(__self__, *,
                 skip_destroy: Optional[pulumi.Input[bool]] = None,
                 status: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering TemplateAssociation resources.
        :param pulumi.Input[str] status: Association status. Creating this resource will result in an `ASSOCIATED` status, and quota increase requests in the template are automatically applied to new AWS accounts in the organization.
        """
        if skip_destroy is not None:
            pulumi.set(__self__, "skip_destroy", skip_destroy)
        if status is not None:
            pulumi.set(__self__, "status", status)

    @property
    @pulumi.getter(name="skipDestroy")
    def skip_destroy(self) -> Optional[pulumi.Input[bool]]:
        return pulumi.get(self, "skip_destroy")

    @skip_destroy.setter
    def skip_destroy(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "skip_destroy", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        """
        Association status. Creating this resource will result in an `ASSOCIATED` status, and quota increase requests in the template are automatically applied to new AWS accounts in the organization.
        """
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)


class TemplateAssociation(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 skip_destroy: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        """
        Resource for managing an AWS Service Quotas Template Association.

        > Only the management account of an organization can associate Service Quota templates, and this must be done from the `us-east-1` region.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.servicequotas.TemplateAssociation("example")
        ```

        ## Import

        Using `pulumi import`, import Service Quotas Template Association using the `id`. For example:

        ```sh
         $ pulumi import aws:servicequotas/templateAssociation:TemplateAssociation example 012345678901
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[TemplateAssociationArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing an AWS Service Quotas Template Association.

        > Only the management account of an organization can associate Service Quota templates, and this must be done from the `us-east-1` region.

        ## Example Usage
        ### Basic Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.servicequotas.TemplateAssociation("example")
        ```

        ## Import

        Using `pulumi import`, import Service Quotas Template Association using the `id`. For example:

        ```sh
         $ pulumi import aws:servicequotas/templateAssociation:TemplateAssociation example 012345678901
        ```

        :param str resource_name: The name of the resource.
        :param TemplateAssociationArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(TemplateAssociationArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 skip_destroy: Optional[pulumi.Input[bool]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = TemplateAssociationArgs.__new__(TemplateAssociationArgs)

            __props__.__dict__["skip_destroy"] = skip_destroy
            __props__.__dict__["status"] = None
        super(TemplateAssociation, __self__).__init__(
            'aws:servicequotas/templateAssociation:TemplateAssociation',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            skip_destroy: Optional[pulumi.Input[bool]] = None,
            status: Optional[pulumi.Input[str]] = None) -> 'TemplateAssociation':
        """
        Get an existing TemplateAssociation resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] status: Association status. Creating this resource will result in an `ASSOCIATED` status, and quota increase requests in the template are automatically applied to new AWS accounts in the organization.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _TemplateAssociationState.__new__(_TemplateAssociationState)

        __props__.__dict__["skip_destroy"] = skip_destroy
        __props__.__dict__["status"] = status
        return TemplateAssociation(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="skipDestroy")
    def skip_destroy(self) -> pulumi.Output[Optional[bool]]:
        return pulumi.get(self, "skip_destroy")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        """
        Association status. Creating this resource will result in an `ASSOCIATED` status, and quota increase requests in the template are automatically applied to new AWS accounts in the organization.
        """
        return pulumi.get(self, "status")

