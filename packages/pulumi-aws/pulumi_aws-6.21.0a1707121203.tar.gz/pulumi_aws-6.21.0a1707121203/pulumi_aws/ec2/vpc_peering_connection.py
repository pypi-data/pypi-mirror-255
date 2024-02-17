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

__all__ = ['VpcPeeringConnectionArgs', 'VpcPeeringConnection']

@pulumi.input_type
class VpcPeeringConnectionArgs:
    def __init__(__self__, *,
                 peer_vpc_id: pulumi.Input[str],
                 vpc_id: pulumi.Input[str],
                 accepter: Optional[pulumi.Input['VpcPeeringConnectionAccepterArgs']] = None,
                 auto_accept: Optional[pulumi.Input[bool]] = None,
                 peer_owner_id: Optional[pulumi.Input[str]] = None,
                 peer_region: Optional[pulumi.Input[str]] = None,
                 requester: Optional[pulumi.Input['VpcPeeringConnectionRequesterArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a VpcPeeringConnection resource.
        :param pulumi.Input[str] peer_vpc_id: The ID of the target VPC with which you are creating the VPC Peering Connection.
        :param pulumi.Input[str] vpc_id: The ID of the requester VPC.
        :param pulumi.Input['VpcPeeringConnectionAccepterArgs'] accepter: An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
               the peering connection (a maximum of one).
        :param pulumi.Input[bool] auto_accept: Accept the peering (both VPCs need to be in the same AWS account and region).
        :param pulumi.Input[str] peer_owner_id: The AWS account ID of the target peer VPC.
               Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        :param pulumi.Input[str] peer_region: The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
               and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        :param pulumi.Input['VpcPeeringConnectionRequesterArgs'] requester: A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
               the peering connection (a maximum of one).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "peer_vpc_id", peer_vpc_id)
        pulumi.set(__self__, "vpc_id", vpc_id)
        if accepter is not None:
            pulumi.set(__self__, "accepter", accepter)
        if auto_accept is not None:
            pulumi.set(__self__, "auto_accept", auto_accept)
        if peer_owner_id is not None:
            pulumi.set(__self__, "peer_owner_id", peer_owner_id)
        if peer_region is not None:
            pulumi.set(__self__, "peer_region", peer_region)
        if requester is not None:
            pulumi.set(__self__, "requester", requester)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="peerVpcId")
    def peer_vpc_id(self) -> pulumi.Input[str]:
        """
        The ID of the target VPC with which you are creating the VPC Peering Connection.
        """
        return pulumi.get(self, "peer_vpc_id")

    @peer_vpc_id.setter
    def peer_vpc_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "peer_vpc_id", value)

    @property
    @pulumi.getter(name="vpcId")
    def vpc_id(self) -> pulumi.Input[str]:
        """
        The ID of the requester VPC.
        """
        return pulumi.get(self, "vpc_id")

    @vpc_id.setter
    def vpc_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "vpc_id", value)

    @property
    @pulumi.getter
    def accepter(self) -> Optional[pulumi.Input['VpcPeeringConnectionAccepterArgs']]:
        """
        An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
        the peering connection (a maximum of one).
        """
        return pulumi.get(self, "accepter")

    @accepter.setter
    def accepter(self, value: Optional[pulumi.Input['VpcPeeringConnectionAccepterArgs']]):
        pulumi.set(self, "accepter", value)

    @property
    @pulumi.getter(name="autoAccept")
    def auto_accept(self) -> Optional[pulumi.Input[bool]]:
        """
        Accept the peering (both VPCs need to be in the same AWS account and region).
        """
        return pulumi.get(self, "auto_accept")

    @auto_accept.setter
    def auto_accept(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "auto_accept", value)

    @property
    @pulumi.getter(name="peerOwnerId")
    def peer_owner_id(self) -> Optional[pulumi.Input[str]]:
        """
        The AWS account ID of the target peer VPC.
        Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        """
        return pulumi.get(self, "peer_owner_id")

    @peer_owner_id.setter
    def peer_owner_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "peer_owner_id", value)

    @property
    @pulumi.getter(name="peerRegion")
    def peer_region(self) -> Optional[pulumi.Input[str]]:
        """
        The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
        and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        """
        return pulumi.get(self, "peer_region")

    @peer_region.setter
    def peer_region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "peer_region", value)

    @property
    @pulumi.getter
    def requester(self) -> Optional[pulumi.Input['VpcPeeringConnectionRequesterArgs']]:
        """
        A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
        the peering connection (a maximum of one).
        """
        return pulumi.get(self, "requester")

    @requester.setter
    def requester(self, value: Optional[pulumi.Input['VpcPeeringConnectionRequesterArgs']]):
        pulumi.set(self, "requester", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _VpcPeeringConnectionState:
    def __init__(__self__, *,
                 accept_status: Optional[pulumi.Input[str]] = None,
                 accepter: Optional[pulumi.Input['VpcPeeringConnectionAccepterArgs']] = None,
                 auto_accept: Optional[pulumi.Input[bool]] = None,
                 peer_owner_id: Optional[pulumi.Input[str]] = None,
                 peer_region: Optional[pulumi.Input[str]] = None,
                 peer_vpc_id: Optional[pulumi.Input[str]] = None,
                 requester: Optional[pulumi.Input['VpcPeeringConnectionRequesterArgs']] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vpc_id: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering VpcPeeringConnection resources.
        :param pulumi.Input[str] accept_status: The status of the VPC Peering Connection request.
        :param pulumi.Input['VpcPeeringConnectionAccepterArgs'] accepter: An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
               the peering connection (a maximum of one).
        :param pulumi.Input[bool] auto_accept: Accept the peering (both VPCs need to be in the same AWS account and region).
        :param pulumi.Input[str] peer_owner_id: The AWS account ID of the target peer VPC.
               Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        :param pulumi.Input[str] peer_region: The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
               and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        :param pulumi.Input[str] peer_vpc_id: The ID of the target VPC with which you are creating the VPC Peering Connection.
        :param pulumi.Input['VpcPeeringConnectionRequesterArgs'] requester: A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
               the peering connection (a maximum of one).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[str] vpc_id: The ID of the requester VPC.
        """
        if accept_status is not None:
            pulumi.set(__self__, "accept_status", accept_status)
        if accepter is not None:
            pulumi.set(__self__, "accepter", accepter)
        if auto_accept is not None:
            pulumi.set(__self__, "auto_accept", auto_accept)
        if peer_owner_id is not None:
            pulumi.set(__self__, "peer_owner_id", peer_owner_id)
        if peer_region is not None:
            pulumi.set(__self__, "peer_region", peer_region)
        if peer_vpc_id is not None:
            pulumi.set(__self__, "peer_vpc_id", peer_vpc_id)
        if requester is not None:
            pulumi.set(__self__, "requester", requester)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)
        if tags_all is not None:
            warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
            pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")
        if tags_all is not None:
            pulumi.set(__self__, "tags_all", tags_all)
        if vpc_id is not None:
            pulumi.set(__self__, "vpc_id", vpc_id)

    @property
    @pulumi.getter(name="acceptStatus")
    def accept_status(self) -> Optional[pulumi.Input[str]]:
        """
        The status of the VPC Peering Connection request.
        """
        return pulumi.get(self, "accept_status")

    @accept_status.setter
    def accept_status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "accept_status", value)

    @property
    @pulumi.getter
    def accepter(self) -> Optional[pulumi.Input['VpcPeeringConnectionAccepterArgs']]:
        """
        An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
        the peering connection (a maximum of one).
        """
        return pulumi.get(self, "accepter")

    @accepter.setter
    def accepter(self, value: Optional[pulumi.Input['VpcPeeringConnectionAccepterArgs']]):
        pulumi.set(self, "accepter", value)

    @property
    @pulumi.getter(name="autoAccept")
    def auto_accept(self) -> Optional[pulumi.Input[bool]]:
        """
        Accept the peering (both VPCs need to be in the same AWS account and region).
        """
        return pulumi.get(self, "auto_accept")

    @auto_accept.setter
    def auto_accept(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "auto_accept", value)

    @property
    @pulumi.getter(name="peerOwnerId")
    def peer_owner_id(self) -> Optional[pulumi.Input[str]]:
        """
        The AWS account ID of the target peer VPC.
        Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        """
        return pulumi.get(self, "peer_owner_id")

    @peer_owner_id.setter
    def peer_owner_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "peer_owner_id", value)

    @property
    @pulumi.getter(name="peerRegion")
    def peer_region(self) -> Optional[pulumi.Input[str]]:
        """
        The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
        and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        """
        return pulumi.get(self, "peer_region")

    @peer_region.setter
    def peer_region(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "peer_region", value)

    @property
    @pulumi.getter(name="peerVpcId")
    def peer_vpc_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the target VPC with which you are creating the VPC Peering Connection.
        """
        return pulumi.get(self, "peer_vpc_id")

    @peer_vpc_id.setter
    def peer_vpc_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "peer_vpc_id", value)

    @property
    @pulumi.getter
    def requester(self) -> Optional[pulumi.Input['VpcPeeringConnectionRequesterArgs']]:
        """
        A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
        the peering connection (a maximum of one).
        """
        return pulumi.get(self, "requester")

    @requester.setter
    def requester(self, value: Optional[pulumi.Input['VpcPeeringConnectionRequesterArgs']]):
        pulumi.set(self, "requester", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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
    @pulumi.getter(name="vpcId")
    def vpc_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID of the requester VPC.
        """
        return pulumi.get(self, "vpc_id")

    @vpc_id.setter
    def vpc_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "vpc_id", value)


class VpcPeeringConnection(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 accepter: Optional[pulumi.Input[pulumi.InputType['VpcPeeringConnectionAccepterArgs']]] = None,
                 auto_accept: Optional[pulumi.Input[bool]] = None,
                 peer_owner_id: Optional[pulumi.Input[str]] = None,
                 peer_region: Optional[pulumi.Input[str]] = None,
                 peer_vpc_id: Optional[pulumi.Input[str]] = None,
                 requester: Optional[pulumi.Input[pulumi.InputType['VpcPeeringConnectionRequesterArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vpc_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides a resource to manage a VPC peering connection.

        > **NOTE on VPC Peering Connections and VPC Peering Connection Options:** This provider provides
        both a standalone VPC Peering Connection Options and a VPC Peering Connection
        resource with `accepter` and `requester` attributes. Do not manage options for the same VPC peering
        connection in both a VPC Peering Connection resource and a VPC Peering Connection Options resource.
        Doing so will cause a conflict of options and will overwrite the options.
        Using a VPC Peering Connection Options resource decouples management of the connection options from
        management of the VPC Peering Connection and allows options to be set correctly in cross-account scenarios.

        > **Note:** For cross-account (requester's AWS account differs from the accepter's AWS account) or inter-region
        VPC Peering Connections use the `ec2.VpcPeeringConnection` resource to manage the requester's side of the
        connection and use the `ec2.VpcPeeringConnectionAccepter` resource to manage the accepter's side of the connection.

        > **Note:** Creating multiple `ec2.VpcPeeringConnection` resources with the same `peer_vpc_id` and `vpc_id` will not produce an error. Instead, AWS will return the connection `id` that already exists, resulting in multiple `ec2.VpcPeeringConnection` resources with the same `id`.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        foo = aws.ec2.VpcPeeringConnection("foo",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=aws_vpc["bar"]["id"],
            vpc_id=aws_vpc["foo"]["id"])
        ```

        Basic usage with connection options:

        ```python
        import pulumi
        import pulumi_aws as aws

        foo = aws.ec2.VpcPeeringConnection("foo",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=aws_vpc["bar"]["id"],
            vpc_id=aws_vpc["foo"]["id"],
            accepter=aws.ec2.VpcPeeringConnectionAccepterArgs(
                allow_remote_vpc_dns_resolution=True,
            ),
            requester=aws.ec2.VpcPeeringConnectionRequesterArgs(
                allow_remote_vpc_dns_resolution=True,
            ))
        ```

        Basic usage with tags:

        ```python
        import pulumi
        import pulumi_aws as aws

        foo_vpc = aws.ec2.Vpc("fooVpc", cidr_block="10.1.0.0/16")
        bar = aws.ec2.Vpc("bar", cidr_block="10.2.0.0/16")
        foo_vpc_peering_connection = aws.ec2.VpcPeeringConnection("fooVpcPeeringConnection",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=bar.id,
            vpc_id=foo_vpc.id,
            auto_accept=True,
            tags={
                "Name": "VPC Peering between foo and bar",
            })
        ```

        Basic usage with region:

        ```python
        import pulumi
        import pulumi_aws as aws

        foo_vpc = aws.ec2.Vpc("fooVpc", cidr_block="10.1.0.0/16",
        opts=pulumi.ResourceOptions(provider=aws["us-west-2"]))
        bar = aws.ec2.Vpc("bar", cidr_block="10.2.0.0/16",
        opts=pulumi.ResourceOptions(provider=aws["us-east-1"]))
        foo_vpc_peering_connection = aws.ec2.VpcPeeringConnection("fooVpcPeeringConnection",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=bar.id,
            vpc_id=foo_vpc.id,
            peer_region="us-east-1")
        ```
        ## Notes

        If both VPCs are not in the same AWS account and region do not enable the `auto_accept` attribute.
        The accepter can manage its side of the connection using the `ec2.VpcPeeringConnectionAccepter` resource
        or accept the connection manually using the AWS Management Console, AWS CLI, through SDKs, etc.

        ## Import

        Using `pulumi import`, import VPC Peering resources using the VPC peering `id`. For example:

        ```sh
         $ pulumi import aws:ec2/vpcPeeringConnection:VpcPeeringConnection test_connection pcx-111aaa111
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['VpcPeeringConnectionAccepterArgs']] accepter: An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
               the peering connection (a maximum of one).
        :param pulumi.Input[bool] auto_accept: Accept the peering (both VPCs need to be in the same AWS account and region).
        :param pulumi.Input[str] peer_owner_id: The AWS account ID of the target peer VPC.
               Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        :param pulumi.Input[str] peer_region: The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
               and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        :param pulumi.Input[str] peer_vpc_id: The ID of the target VPC with which you are creating the VPC Peering Connection.
        :param pulumi.Input[pulumi.InputType['VpcPeeringConnectionRequesterArgs']] requester: A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
               the peering connection (a maximum of one).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[str] vpc_id: The ID of the requester VPC.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: VpcPeeringConnectionArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides a resource to manage a VPC peering connection.

        > **NOTE on VPC Peering Connections and VPC Peering Connection Options:** This provider provides
        both a standalone VPC Peering Connection Options and a VPC Peering Connection
        resource with `accepter` and `requester` attributes. Do not manage options for the same VPC peering
        connection in both a VPC Peering Connection resource and a VPC Peering Connection Options resource.
        Doing so will cause a conflict of options and will overwrite the options.
        Using a VPC Peering Connection Options resource decouples management of the connection options from
        management of the VPC Peering Connection and allows options to be set correctly in cross-account scenarios.

        > **Note:** For cross-account (requester's AWS account differs from the accepter's AWS account) or inter-region
        VPC Peering Connections use the `ec2.VpcPeeringConnection` resource to manage the requester's side of the
        connection and use the `ec2.VpcPeeringConnectionAccepter` resource to manage the accepter's side of the connection.

        > **Note:** Creating multiple `ec2.VpcPeeringConnection` resources with the same `peer_vpc_id` and `vpc_id` will not produce an error. Instead, AWS will return the connection `id` that already exists, resulting in multiple `ec2.VpcPeeringConnection` resources with the same `id`.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        foo = aws.ec2.VpcPeeringConnection("foo",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=aws_vpc["bar"]["id"],
            vpc_id=aws_vpc["foo"]["id"])
        ```

        Basic usage with connection options:

        ```python
        import pulumi
        import pulumi_aws as aws

        foo = aws.ec2.VpcPeeringConnection("foo",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=aws_vpc["bar"]["id"],
            vpc_id=aws_vpc["foo"]["id"],
            accepter=aws.ec2.VpcPeeringConnectionAccepterArgs(
                allow_remote_vpc_dns_resolution=True,
            ),
            requester=aws.ec2.VpcPeeringConnectionRequesterArgs(
                allow_remote_vpc_dns_resolution=True,
            ))
        ```

        Basic usage with tags:

        ```python
        import pulumi
        import pulumi_aws as aws

        foo_vpc = aws.ec2.Vpc("fooVpc", cidr_block="10.1.0.0/16")
        bar = aws.ec2.Vpc("bar", cidr_block="10.2.0.0/16")
        foo_vpc_peering_connection = aws.ec2.VpcPeeringConnection("fooVpcPeeringConnection",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=bar.id,
            vpc_id=foo_vpc.id,
            auto_accept=True,
            tags={
                "Name": "VPC Peering between foo and bar",
            })
        ```

        Basic usage with region:

        ```python
        import pulumi
        import pulumi_aws as aws

        foo_vpc = aws.ec2.Vpc("fooVpc", cidr_block="10.1.0.0/16",
        opts=pulumi.ResourceOptions(provider=aws["us-west-2"]))
        bar = aws.ec2.Vpc("bar", cidr_block="10.2.0.0/16",
        opts=pulumi.ResourceOptions(provider=aws["us-east-1"]))
        foo_vpc_peering_connection = aws.ec2.VpcPeeringConnection("fooVpcPeeringConnection",
            peer_owner_id=var["peer_owner_id"],
            peer_vpc_id=bar.id,
            vpc_id=foo_vpc.id,
            peer_region="us-east-1")
        ```
        ## Notes

        If both VPCs are not in the same AWS account and region do not enable the `auto_accept` attribute.
        The accepter can manage its side of the connection using the `ec2.VpcPeeringConnectionAccepter` resource
        or accept the connection manually using the AWS Management Console, AWS CLI, through SDKs, etc.

        ## Import

        Using `pulumi import`, import VPC Peering resources using the VPC peering `id`. For example:

        ```sh
         $ pulumi import aws:ec2/vpcPeeringConnection:VpcPeeringConnection test_connection pcx-111aaa111
        ```

        :param str resource_name: The name of the resource.
        :param VpcPeeringConnectionArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(VpcPeeringConnectionArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 accepter: Optional[pulumi.Input[pulumi.InputType['VpcPeeringConnectionAccepterArgs']]] = None,
                 auto_accept: Optional[pulumi.Input[bool]] = None,
                 peer_owner_id: Optional[pulumi.Input[str]] = None,
                 peer_region: Optional[pulumi.Input[str]] = None,
                 peer_vpc_id: Optional[pulumi.Input[str]] = None,
                 requester: Optional[pulumi.Input[pulumi.InputType['VpcPeeringConnectionRequesterArgs']]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 vpc_id: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = VpcPeeringConnectionArgs.__new__(VpcPeeringConnectionArgs)

            __props__.__dict__["accepter"] = accepter
            __props__.__dict__["auto_accept"] = auto_accept
            __props__.__dict__["peer_owner_id"] = peer_owner_id
            __props__.__dict__["peer_region"] = peer_region
            if peer_vpc_id is None and not opts.urn:
                raise TypeError("Missing required property 'peer_vpc_id'")
            __props__.__dict__["peer_vpc_id"] = peer_vpc_id
            __props__.__dict__["requester"] = requester
            __props__.__dict__["tags"] = tags
            if vpc_id is None and not opts.urn:
                raise TypeError("Missing required property 'vpc_id'")
            __props__.__dict__["vpc_id"] = vpc_id
            __props__.__dict__["accept_status"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(VpcPeeringConnection, __self__).__init__(
            'aws:ec2/vpcPeeringConnection:VpcPeeringConnection',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            accept_status: Optional[pulumi.Input[str]] = None,
            accepter: Optional[pulumi.Input[pulumi.InputType['VpcPeeringConnectionAccepterArgs']]] = None,
            auto_accept: Optional[pulumi.Input[bool]] = None,
            peer_owner_id: Optional[pulumi.Input[str]] = None,
            peer_region: Optional[pulumi.Input[str]] = None,
            peer_vpc_id: Optional[pulumi.Input[str]] = None,
            requester: Optional[pulumi.Input[pulumi.InputType['VpcPeeringConnectionRequesterArgs']]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            vpc_id: Optional[pulumi.Input[str]] = None) -> 'VpcPeeringConnection':
        """
        Get an existing VpcPeeringConnection resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] accept_status: The status of the VPC Peering Connection request.
        :param pulumi.Input[pulumi.InputType['VpcPeeringConnectionAccepterArgs']] accepter: An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
               the peering connection (a maximum of one).
        :param pulumi.Input[bool] auto_accept: Accept the peering (both VPCs need to be in the same AWS account and region).
        :param pulumi.Input[str] peer_owner_id: The AWS account ID of the target peer VPC.
               Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        :param pulumi.Input[str] peer_region: The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
               and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        :param pulumi.Input[str] peer_vpc_id: The ID of the target VPC with which you are creating the VPC Peering Connection.
        :param pulumi.Input[pulumi.InputType['VpcPeeringConnectionRequesterArgs']] requester: A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
               the peering connection (a maximum of one).
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: A map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        :param pulumi.Input[str] vpc_id: The ID of the requester VPC.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _VpcPeeringConnectionState.__new__(_VpcPeeringConnectionState)

        __props__.__dict__["accept_status"] = accept_status
        __props__.__dict__["accepter"] = accepter
        __props__.__dict__["auto_accept"] = auto_accept
        __props__.__dict__["peer_owner_id"] = peer_owner_id
        __props__.__dict__["peer_region"] = peer_region
        __props__.__dict__["peer_vpc_id"] = peer_vpc_id
        __props__.__dict__["requester"] = requester
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        __props__.__dict__["vpc_id"] = vpc_id
        return VpcPeeringConnection(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="acceptStatus")
    def accept_status(self) -> pulumi.Output[str]:
        """
        The status of the VPC Peering Connection request.
        """
        return pulumi.get(self, "accept_status")

    @property
    @pulumi.getter
    def accepter(self) -> pulumi.Output['outputs.VpcPeeringConnectionAccepter']:
        """
        An optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that accepts
        the peering connection (a maximum of one).
        """
        return pulumi.get(self, "accepter")

    @property
    @pulumi.getter(name="autoAccept")
    def auto_accept(self) -> pulumi.Output[Optional[bool]]:
        """
        Accept the peering (both VPCs need to be in the same AWS account and region).
        """
        return pulumi.get(self, "auto_accept")

    @property
    @pulumi.getter(name="peerOwnerId")
    def peer_owner_id(self) -> pulumi.Output[str]:
        """
        The AWS account ID of the target peer VPC.
        Defaults to the account ID the [AWS provider][1] is currently connected to, so must be managed if connecting cross-account.
        """
        return pulumi.get(self, "peer_owner_id")

    @property
    @pulumi.getter(name="peerRegion")
    def peer_region(self) -> pulumi.Output[str]:
        """
        The region of the accepter VPC of the VPC Peering Connection. `auto_accept` must be `false`,
        and use the `ec2.VpcPeeringConnectionAccepter` to manage the accepter side.
        """
        return pulumi.get(self, "peer_region")

    @property
    @pulumi.getter(name="peerVpcId")
    def peer_vpc_id(self) -> pulumi.Output[str]:
        """
        The ID of the target VPC with which you are creating the VPC Peering Connection.
        """
        return pulumi.get(self, "peer_vpc_id")

    @property
    @pulumi.getter
    def requester(self) -> pulumi.Output['outputs.VpcPeeringConnectionRequester']:
        """
        A optional configuration block that allows for [VPC Peering Connection](https://docs.aws.amazon.com/vpc/latest/peering/what-is-vpc-peering.html) options to be set for the VPC that requests
        the peering connection (a maximum of one).
        """
        return pulumi.get(self, "requester")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        A map of tags to assign to the resource. .If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
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
    @pulumi.getter(name="vpcId")
    def vpc_id(self) -> pulumi.Output[str]:
        """
        The ID of the requester VPC.
        """
        return pulumi.get(self, "vpc_id")

