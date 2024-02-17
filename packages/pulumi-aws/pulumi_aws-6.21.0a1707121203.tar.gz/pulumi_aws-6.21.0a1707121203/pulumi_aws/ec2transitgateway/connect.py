# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ConnectArgs', 'Connect']

@pulumi.input_type
class ConnectArgs:
    def __init__(__self__, *,
                 transit_gateway_id: pulumi.Input[str],
                 transport_attachment_id: pulumi.Input[str],
                 protocol: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 transit_gateway_default_route_table_association: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_default_route_table_propagation: Optional[pulumi.Input[bool]] = None):
        """
        The set of arguments for constructing a Connect resource.
        :param pulumi.Input[str] transit_gateway_id: Identifier of EC2 Transit Gateway.
        :param pulumi.Input[str] transport_attachment_id: The underlaying VPC attachment
        :param pulumi.Input[str] protocol: The tunnel protocol. Valid values: `gre`. Default is `gre`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[bool] transit_gateway_default_route_table_association: Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[bool] transit_gateway_default_route_table_propagation: Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        pulumi.set(__self__, "transit_gateway_id", transit_gateway_id)
        pulumi.set(__self__, "transport_attachment_id", transport_attachment_id)
        if protocol is not None:
            pulumi.set(__self__, "protocol", protocol)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if transit_gateway_default_route_table_association is not None:
            pulumi.set(__self__, "transit_gateway_default_route_table_association", transit_gateway_default_route_table_association)
        if transit_gateway_default_route_table_propagation is not None:
            pulumi.set(__self__, "transit_gateway_default_route_table_propagation", transit_gateway_default_route_table_propagation)

    @property
    @pulumi.getter(name="transitGatewayId")
    def transit_gateway_id(self) -> pulumi.Input[str]:
        """
        Identifier of EC2 Transit Gateway.
        """
        return pulumi.get(self, "transit_gateway_id")

    @transit_gateway_id.setter
    def transit_gateway_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "transit_gateway_id", value)

    @property
    @pulumi.getter(name="transportAttachmentId")
    def transport_attachment_id(self) -> pulumi.Input[str]:
        """
        The underlaying VPC attachment
        """
        return pulumi.get(self, "transport_attachment_id")

    @transport_attachment_id.setter
    def transport_attachment_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "transport_attachment_id", value)

    @property
    @pulumi.getter
    def protocol(self) -> Optional[pulumi.Input[str]]:
        """
        The tunnel protocol. Valid values: `gre`. Default is `gre`.
        """
        return pulumi.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protocol", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="transitGatewayDefaultRouteTableAssociation")
    def transit_gateway_default_route_table_association(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        return pulumi.get(self, "transit_gateway_default_route_table_association")

    @transit_gateway_default_route_table_association.setter
    def transit_gateway_default_route_table_association(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "transit_gateway_default_route_table_association", value)

    @property
    @pulumi.getter(name="transitGatewayDefaultRouteTablePropagation")
    def transit_gateway_default_route_table_propagation(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        return pulumi.get(self, "transit_gateway_default_route_table_propagation")

    @transit_gateway_default_route_table_propagation.setter
    def transit_gateway_default_route_table_propagation(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "transit_gateway_default_route_table_propagation", value)


@pulumi.input_type
class _ConnectState:
    def __init__(__self__, *,
                 protocol: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 transit_gateway_default_route_table_association: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_default_route_table_propagation: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_id: Optional[pulumi.Input[str]] = None,
                 transport_attachment_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering Connect resources.
        :param pulumi.Input[str] protocol: The tunnel protocol. Valid values: `gre`. Default is `gre`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[bool] transit_gateway_default_route_table_association: Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[bool] transit_gateway_default_route_table_propagation: Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[str] transit_gateway_id: Identifier of EC2 Transit Gateway.
        :param pulumi.Input[str] transport_attachment_id: The underlaying VPC attachment
        """
        if protocol is not None:
            pulumi.set(__self__, "protocol", protocol)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)
        if transit_gateway_default_route_table_association is not None:
            pulumi.set(__self__, "transit_gateway_default_route_table_association", transit_gateway_default_route_table_association)
        if transit_gateway_default_route_table_propagation is not None:
            pulumi.set(__self__, "transit_gateway_default_route_table_propagation", transit_gateway_default_route_table_propagation)
        if transit_gateway_id is not None:
            pulumi.set(__self__, "transit_gateway_id", transit_gateway_id)
        if transport_attachment_id is not None:
            pulumi.set(__self__, "transport_attachment_id", transport_attachment_id)

    @property
    @pulumi.getter
    def protocol(self) -> Optional[pulumi.Input[str]]:
        """
        The tunnel protocol. Valid values: `gre`. Default is `gre`.
        """
        return pulumi.get(self, "protocol")

    @protocol.setter
    def protocol(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "protocol", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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
    @pulumi.getter(name="transitGatewayDefaultRouteTableAssociation")
    def transit_gateway_default_route_table_association(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        return pulumi.get(self, "transit_gateway_default_route_table_association")

    @transit_gateway_default_route_table_association.setter
    def transit_gateway_default_route_table_association(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "transit_gateway_default_route_table_association", value)

    @property
    @pulumi.getter(name="transitGatewayDefaultRouteTablePropagation")
    def transit_gateway_default_route_table_propagation(self) -> Optional[pulumi.Input[bool]]:
        """
        Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        return pulumi.get(self, "transit_gateway_default_route_table_propagation")

    @transit_gateway_default_route_table_propagation.setter
    def transit_gateway_default_route_table_propagation(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "transit_gateway_default_route_table_propagation", value)

    @property
    @pulumi.getter(name="transitGatewayId")
    def transit_gateway_id(self) -> Optional[pulumi.Input[str]]:
        """
        Identifier of EC2 Transit Gateway.
        """
        return pulumi.get(self, "transit_gateway_id")

    @transit_gateway_id.setter
    def transit_gateway_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "transit_gateway_id", value)

    @property
    @pulumi.getter(name="transportAttachmentId")
    def transport_attachment_id(self) -> Optional[pulumi.Input[str]]:
        """
        The underlaying VPC attachment
        """
        return pulumi.get(self, "transport_attachment_id")

    @transport_attachment_id.setter
    def transport_attachment_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "transport_attachment_id", value)


class Connect(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 transit_gateway_default_route_table_association: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_default_route_table_propagation: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_id: Optional[pulumi.Input[str]] = None,
                 transport_attachment_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Manages an EC2 Transit Gateway Connect.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.ec2transitgateway.VpcAttachment("example",
            subnet_ids=[aws_subnet["example"]["id"]],
            transit_gateway_id=aws_ec2_transit_gateway["example"]["id"],
            vpc_id=aws_vpc["example"]["id"])
        attachment = aws.ec2transitgateway.Connect("attachment",
            transport_attachment_id=example.id,
            transit_gateway_id=aws_ec2_transit_gateway["example"]["id"])
        ```

        ## Import

        Using `pulumi import`, import `aws_ec2_transit_gateway_connect` using the EC2 Transit Gateway Connect identifier. For example:

        ```sh
         $ pulumi import aws:ec2transitgateway/connect:Connect example tgw-attach-12345678
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] protocol: The tunnel protocol. Valid values: `gre`. Default is `gre`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[bool] transit_gateway_default_route_table_association: Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[bool] transit_gateway_default_route_table_propagation: Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[str] transit_gateway_id: Identifier of EC2 Transit Gateway.
        :param pulumi.Input[str] transport_attachment_id: The underlaying VPC attachment
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ConnectArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Manages an EC2 Transit Gateway Connect.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.ec2transitgateway.VpcAttachment("example",
            subnet_ids=[aws_subnet["example"]["id"]],
            transit_gateway_id=aws_ec2_transit_gateway["example"]["id"],
            vpc_id=aws_vpc["example"]["id"])
        attachment = aws.ec2transitgateway.Connect("attachment",
            transport_attachment_id=example.id,
            transit_gateway_id=aws_ec2_transit_gateway["example"]["id"])
        ```

        ## Import

        Using `pulumi import`, import `aws_ec2_transit_gateway_connect` using the EC2 Transit Gateway Connect identifier. For example:

        ```sh
         $ pulumi import aws:ec2transitgateway/connect:Connect example tgw-attach-12345678
        ```

        :param str resource_name: The name of the resource.
        :param ConnectArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ConnectArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 protocol: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 transit_gateway_default_route_table_association: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_default_route_table_propagation: Optional[pulumi.Input[bool]] = None,
                 transit_gateway_id: Optional[pulumi.Input[str]] = None,
                 transport_attachment_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ConnectArgs.__new__(ConnectArgs)

            __props__.__dict__["protocol"] = protocol
            __props__.__dict__["tags"] = tags
            __props__.__dict__["transit_gateway_default_route_table_association"] = transit_gateway_default_route_table_association
            __props__.__dict__["transit_gateway_default_route_table_propagation"] = transit_gateway_default_route_table_propagation
            if transit_gateway_id is None and not opts.urn:
                raise TypeError("Missing required property 'transit_gateway_id'")
            __props__.__dict__["transit_gateway_id"] = transit_gateway_id
            if transport_attachment_id is None and not opts.urn:
                raise TypeError("Missing required property 'transport_attachment_id'")
            __props__.__dict__["transport_attachment_id"] = transport_attachment_id
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(Connect, __self__).__init__(
            'aws:ec2transitgateway/connect:Connect',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            protocol: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            transit_gateway_default_route_table_association: Optional[pulumi.Input[bool]] = None,
            transit_gateway_default_route_table_propagation: Optional[pulumi.Input[bool]] = None,
            transit_gateway_id: Optional[pulumi.Input[str]] = None,
            transport_attachment_id: Optional[pulumi.Input[str]] = None) -> 'Connect':
        """
        Get an existing Connect resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] protocol: The tunnel protocol. Valid values: `gre`. Default is `gre`.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[bool] transit_gateway_default_route_table_association: Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[bool] transit_gateway_default_route_table_propagation: Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        :param pulumi.Input[str] transit_gateway_id: Identifier of EC2 Transit Gateway.
        :param pulumi.Input[str] transport_attachment_id: The underlaying VPC attachment
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ConnectState.__new__(_ConnectState)

        __props__.__dict__["protocol"] = protocol
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        __props__.__dict__["transit_gateway_default_route_table_association"] = transit_gateway_default_route_table_association
        __props__.__dict__["transit_gateway_default_route_table_propagation"] = transit_gateway_default_route_table_propagation
        __props__.__dict__["transit_gateway_id"] = transit_gateway_id
        __props__.__dict__["transport_attachment_id"] = transport_attachment_id
        return Connect(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def protocol(self) -> pulumi.Output[Optional[str]]:
        """
        The tunnel protocol. Valid values: `gre`. Default is `gre`.
        """
        return pulumi.get(self, "protocol")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Key-value tags for the EC2 Transit Gateway Connect. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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
    @pulumi.getter(name="transitGatewayDefaultRouteTableAssociation")
    def transit_gateway_default_route_table_association(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean whether the Connect should be associated with the EC2 Transit Gateway association default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        return pulumi.get(self, "transit_gateway_default_route_table_association")

    @property
    @pulumi.getter(name="transitGatewayDefaultRouteTablePropagation")
    def transit_gateway_default_route_table_propagation(self) -> pulumi.Output[Optional[bool]]:
        """
        Boolean whether the Connect should propagate routes with the EC2 Transit Gateway propagation default route table. This cannot be configured or perform drift detection with Resource Access Manager shared EC2 Transit Gateways. Default value: `true`.
        """
        return pulumi.get(self, "transit_gateway_default_route_table_propagation")

    @property
    @pulumi.getter(name="transitGatewayId")
    def transit_gateway_id(self) -> pulumi.Output[str]:
        """
        Identifier of EC2 Transit Gateway.
        """
        return pulumi.get(self, "transit_gateway_id")

    @property
    @pulumi.getter(name="transportAttachmentId")
    def transport_attachment_id(self) -> pulumi.Output[str]:
        """
        The underlaying VPC attachment
        """
        return pulumi.get(self, "transport_attachment_id")

