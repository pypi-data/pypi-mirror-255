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

__all__ = [
    'GetEndpointResult',
    'AwaitableGetEndpointResult',
    'get_endpoint',
    'get_endpoint_output',
]

@pulumi.output_type
class GetEndpointResult:
    """
    A collection of values returned by getEndpoint.
    """
    def __init__(__self__, arn=None, authentication_options=None, client_cidr_block=None, client_connect_options=None, client_login_banner_options=None, client_vpn_endpoint_id=None, connection_log_options=None, description=None, dns_name=None, dns_servers=None, filters=None, id=None, security_group_ids=None, self_service_portal=None, self_service_portal_url=None, server_certificate_arn=None, session_timeout_hours=None, split_tunnel=None, tags=None, transport_protocol=None, vpc_id=None, vpn_port=None):
        if arn and not isinstance(arn, str):
            raise TypeError("Expected argument 'arn' to be a str")
        pulumi.set(__self__, "arn", arn)
        if authentication_options and not isinstance(authentication_options, list):
            raise TypeError("Expected argument 'authentication_options' to be a list")
        pulumi.set(__self__, "authentication_options", authentication_options)
        if client_cidr_block and not isinstance(client_cidr_block, str):
            raise TypeError("Expected argument 'client_cidr_block' to be a str")
        pulumi.set(__self__, "client_cidr_block", client_cidr_block)
        if client_connect_options and not isinstance(client_connect_options, list):
            raise TypeError("Expected argument 'client_connect_options' to be a list")
        pulumi.set(__self__, "client_connect_options", client_connect_options)
        if client_login_banner_options and not isinstance(client_login_banner_options, list):
            raise TypeError("Expected argument 'client_login_banner_options' to be a list")
        pulumi.set(__self__, "client_login_banner_options", client_login_banner_options)
        if client_vpn_endpoint_id and not isinstance(client_vpn_endpoint_id, str):
            raise TypeError("Expected argument 'client_vpn_endpoint_id' to be a str")
        pulumi.set(__self__, "client_vpn_endpoint_id", client_vpn_endpoint_id)
        if connection_log_options and not isinstance(connection_log_options, list):
            raise TypeError("Expected argument 'connection_log_options' to be a list")
        pulumi.set(__self__, "connection_log_options", connection_log_options)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if dns_name and not isinstance(dns_name, str):
            raise TypeError("Expected argument 'dns_name' to be a str")
        pulumi.set(__self__, "dns_name", dns_name)
        if dns_servers and not isinstance(dns_servers, list):
            raise TypeError("Expected argument 'dns_servers' to be a list")
        pulumi.set(__self__, "dns_servers", dns_servers)
        if filters and not isinstance(filters, list):
            raise TypeError("Expected argument 'filters' to be a list")
        pulumi.set(__self__, "filters", filters)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if security_group_ids and not isinstance(security_group_ids, list):
            raise TypeError("Expected argument 'security_group_ids' to be a list")
        pulumi.set(__self__, "security_group_ids", security_group_ids)
        if self_service_portal and not isinstance(self_service_portal, str):
            raise TypeError("Expected argument 'self_service_portal' to be a str")
        pulumi.set(__self__, "self_service_portal", self_service_portal)
        if self_service_portal_url and not isinstance(self_service_portal_url, str):
            raise TypeError("Expected argument 'self_service_portal_url' to be a str")
        pulumi.set(__self__, "self_service_portal_url", self_service_portal_url)
        if server_certificate_arn and not isinstance(server_certificate_arn, str):
            raise TypeError("Expected argument 'server_certificate_arn' to be a str")
        pulumi.set(__self__, "server_certificate_arn", server_certificate_arn)
        if session_timeout_hours and not isinstance(session_timeout_hours, int):
            raise TypeError("Expected argument 'session_timeout_hours' to be a int")
        pulumi.set(__self__, "session_timeout_hours", session_timeout_hours)
        if split_tunnel and not isinstance(split_tunnel, bool):
            raise TypeError("Expected argument 'split_tunnel' to be a bool")
        pulumi.set(__self__, "split_tunnel", split_tunnel)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if transport_protocol and not isinstance(transport_protocol, str):
            raise TypeError("Expected argument 'transport_protocol' to be a str")
        pulumi.set(__self__, "transport_protocol", transport_protocol)
        if vpc_id and not isinstance(vpc_id, str):
            raise TypeError("Expected argument 'vpc_id' to be a str")
        pulumi.set(__self__, "vpc_id", vpc_id)
        if vpn_port and not isinstance(vpn_port, int):
            raise TypeError("Expected argument 'vpn_port' to be a int")
        pulumi.set(__self__, "vpn_port", vpn_port)

    @property
    @pulumi.getter
    def arn(self) -> str:
        """
        The ARN of the Client VPN endpoint.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="authenticationOptions")
    def authentication_options(self) -> Sequence['outputs.GetEndpointAuthenticationOptionResult']:
        """
        Information about the authentication method used by the Client VPN endpoint.
        """
        return pulumi.get(self, "authentication_options")

    @property
    @pulumi.getter(name="clientCidrBlock")
    def client_cidr_block(self) -> str:
        """
        IPv4 address range, in CIDR notation, from which client IP addresses are assigned.
        """
        return pulumi.get(self, "client_cidr_block")

    @property
    @pulumi.getter(name="clientConnectOptions")
    def client_connect_options(self) -> Sequence['outputs.GetEndpointClientConnectOptionResult']:
        """
        The options for managing connection authorization for new client connections.
        """
        return pulumi.get(self, "client_connect_options")

    @property
    @pulumi.getter(name="clientLoginBannerOptions")
    def client_login_banner_options(self) -> Sequence['outputs.GetEndpointClientLoginBannerOptionResult']:
        """
        Options for enabling a customizable text banner that will be displayed on AWS provided clients when a VPN session is established.
        """
        return pulumi.get(self, "client_login_banner_options")

    @property
    @pulumi.getter(name="clientVpnEndpointId")
    def client_vpn_endpoint_id(self) -> str:
        return pulumi.get(self, "client_vpn_endpoint_id")

    @property
    @pulumi.getter(name="connectionLogOptions")
    def connection_log_options(self) -> Sequence['outputs.GetEndpointConnectionLogOptionResult']:
        """
        Information about the client connection logging options for the Client VPN endpoint.
        """
        return pulumi.get(self, "connection_log_options")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Brief description of the endpoint.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="dnsName")
    def dns_name(self) -> str:
        """
        DNS name to be used by clients when connecting to the Client VPN endpoint.
        """
        return pulumi.get(self, "dns_name")

    @property
    @pulumi.getter(name="dnsServers")
    def dns_servers(self) -> Sequence[str]:
        """
        Information about the DNS servers to be used for DNS resolution.
        """
        return pulumi.get(self, "dns_servers")

    @property
    @pulumi.getter
    def filters(self) -> Optional[Sequence['outputs.GetEndpointFilterResult']]:
        return pulumi.get(self, "filters")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="securityGroupIds")
    def security_group_ids(self) -> Sequence[str]:
        """
        IDs of the security groups for the target network associated with the Client VPN endpoint.
        """
        return pulumi.get(self, "security_group_ids")

    @property
    @pulumi.getter(name="selfServicePortal")
    def self_service_portal(self) -> str:
        """
        Whether the self-service portal for the Client VPN endpoint is enabled.
        """
        return pulumi.get(self, "self_service_portal")

    @property
    @pulumi.getter(name="selfServicePortalUrl")
    def self_service_portal_url(self) -> str:
        """
        The URL of the self-service portal.
        """
        return pulumi.get(self, "self_service_portal_url")

    @property
    @pulumi.getter(name="serverCertificateArn")
    def server_certificate_arn(self) -> str:
        """
        The ARN of the server certificate.
        """
        return pulumi.get(self, "server_certificate_arn")

    @property
    @pulumi.getter(name="sessionTimeoutHours")
    def session_timeout_hours(self) -> int:
        """
        The maximum VPN session duration time in hours.
        """
        return pulumi.get(self, "session_timeout_hours")

    @property
    @pulumi.getter(name="splitTunnel")
    def split_tunnel(self) -> bool:
        """
        Whether split-tunnel is enabled in the AWS Client VPN endpoint.
        """
        return pulumi.get(self, "split_tunnel")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="transportProtocol")
    def transport_protocol(self) -> str:
        """
        Transport protocol used by the Client VPN endpoint.
        """
        return pulumi.get(self, "transport_protocol")

    @property
    @pulumi.getter(name="vpcId")
    def vpc_id(self) -> str:
        """
        ID of the VPC associated with the Client VPN endpoint.
        """
        return pulumi.get(self, "vpc_id")

    @property
    @pulumi.getter(name="vpnPort")
    def vpn_port(self) -> int:
        """
        Port number for the Client VPN endpoint.
        """
        return pulumi.get(self, "vpn_port")


class AwaitableGetEndpointResult(GetEndpointResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetEndpointResult(
            arn=self.arn,
            authentication_options=self.authentication_options,
            client_cidr_block=self.client_cidr_block,
            client_connect_options=self.client_connect_options,
            client_login_banner_options=self.client_login_banner_options,
            client_vpn_endpoint_id=self.client_vpn_endpoint_id,
            connection_log_options=self.connection_log_options,
            description=self.description,
            dns_name=self.dns_name,
            dns_servers=self.dns_servers,
            filters=self.filters,
            id=self.id,
            security_group_ids=self.security_group_ids,
            self_service_portal=self.self_service_portal,
            self_service_portal_url=self.self_service_portal_url,
            server_certificate_arn=self.server_certificate_arn,
            session_timeout_hours=self.session_timeout_hours,
            split_tunnel=self.split_tunnel,
            tags=self.tags,
            transport_protocol=self.transport_protocol,
            vpc_id=self.vpc_id,
            vpn_port=self.vpn_port)


def get_endpoint(client_vpn_endpoint_id: Optional[str] = None,
                 filters: Optional[Sequence[pulumi.InputType['GetEndpointFilterArgs']]] = None,
                 tags: Optional[Mapping[str, str]] = None,
                 opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetEndpointResult:
    """
    Get information on an EC2 Client VPN endpoint.

    ## Example Usage
    ### By Filter

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.ec2clientvpn.get_endpoint(filters=[aws.ec2clientvpn.GetEndpointFilterArgs(
        name="tag:Name",
        values=["ExampleVpn"],
    )])
    ```
    ### By Identifier

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.ec2clientvpn.get_endpoint(client_vpn_endpoint_id="cvpn-endpoint-083cf50d6eb314f21")
    ```


    :param str client_vpn_endpoint_id: ID of the Client VPN endpoint.
    :param Sequence[pulumi.InputType['GetEndpointFilterArgs']] filters: One or more configuration blocks containing name-values filters. Detailed below.
    :param Mapping[str, str] tags: Map of tags, each pair of which must exactly match a pair on the desired endpoint.
    """
    __args__ = dict()
    __args__['clientVpnEndpointId'] = client_vpn_endpoint_id
    __args__['filters'] = filters
    __args__['tags'] = tags
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:ec2clientvpn/getEndpoint:getEndpoint', __args__, opts=opts, typ=GetEndpointResult).value

    return AwaitableGetEndpointResult(
        arn=pulumi.get(__ret__, 'arn'),
        authentication_options=pulumi.get(__ret__, 'authentication_options'),
        client_cidr_block=pulumi.get(__ret__, 'client_cidr_block'),
        client_connect_options=pulumi.get(__ret__, 'client_connect_options'),
        client_login_banner_options=pulumi.get(__ret__, 'client_login_banner_options'),
        client_vpn_endpoint_id=pulumi.get(__ret__, 'client_vpn_endpoint_id'),
        connection_log_options=pulumi.get(__ret__, 'connection_log_options'),
        description=pulumi.get(__ret__, 'description'),
        dns_name=pulumi.get(__ret__, 'dns_name'),
        dns_servers=pulumi.get(__ret__, 'dns_servers'),
        filters=pulumi.get(__ret__, 'filters'),
        id=pulumi.get(__ret__, 'id'),
        security_group_ids=pulumi.get(__ret__, 'security_group_ids'),
        self_service_portal=pulumi.get(__ret__, 'self_service_portal'),
        self_service_portal_url=pulumi.get(__ret__, 'self_service_portal_url'),
        server_certificate_arn=pulumi.get(__ret__, 'server_certificate_arn'),
        session_timeout_hours=pulumi.get(__ret__, 'session_timeout_hours'),
        split_tunnel=pulumi.get(__ret__, 'split_tunnel'),
        tags=pulumi.get(__ret__, 'tags'),
        transport_protocol=pulumi.get(__ret__, 'transport_protocol'),
        vpc_id=pulumi.get(__ret__, 'vpc_id'),
        vpn_port=pulumi.get(__ret__, 'vpn_port'))


@_utilities.lift_output_func(get_endpoint)
def get_endpoint_output(client_vpn_endpoint_id: Optional[pulumi.Input[Optional[str]]] = None,
                        filters: Optional[pulumi.Input[Optional[Sequence[pulumi.InputType['GetEndpointFilterArgs']]]]] = None,
                        tags: Optional[pulumi.Input[Optional[Mapping[str, str]]]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetEndpointResult]:
    """
    Get information on an EC2 Client VPN endpoint.

    ## Example Usage
    ### By Filter

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.ec2clientvpn.get_endpoint(filters=[aws.ec2clientvpn.GetEndpointFilterArgs(
        name="tag:Name",
        values=["ExampleVpn"],
    )])
    ```
    ### By Identifier

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.ec2clientvpn.get_endpoint(client_vpn_endpoint_id="cvpn-endpoint-083cf50d6eb314f21")
    ```


    :param str client_vpn_endpoint_id: ID of the Client VPN endpoint.
    :param Sequence[pulumi.InputType['GetEndpointFilterArgs']] filters: One or more configuration blocks containing name-values filters. Detailed below.
    :param Mapping[str, str] tags: Map of tags, each pair of which must exactly match a pair on the desired endpoint.
    """
    ...
