# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['ProxyTargetArgs', 'ProxyTarget']

@pulumi.input_type
class ProxyTargetArgs:
    def __init__(__self__, *,
                 db_proxy_name: pulumi.Input[str],
                 target_group_name: pulumi.Input[str],
                 db_cluster_identifier: Optional[pulumi.Input[str]] = None,
                 db_instance_identifier: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a ProxyTarget resource.
        :param pulumi.Input[str] db_proxy_name: The name of the DB proxy.
        :param pulumi.Input[str] target_group_name: The name of the target group.
        :param pulumi.Input[str] db_cluster_identifier: DB cluster identifier.
               
               **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        :param pulumi.Input[str] db_instance_identifier: DB instance identifier.
        """
        pulumi.set(__self__, "db_proxy_name", db_proxy_name)
        pulumi.set(__self__, "target_group_name", target_group_name)
        if db_cluster_identifier is not None:
            pulumi.set(__self__, "db_cluster_identifier", db_cluster_identifier)
        if db_instance_identifier is not None:
            pulumi.set(__self__, "db_instance_identifier", db_instance_identifier)

    @property
    @pulumi.getter(name="dbProxyName")
    def db_proxy_name(self) -> pulumi.Input[str]:
        """
        The name of the DB proxy.
        """
        return pulumi.get(self, "db_proxy_name")

    @db_proxy_name.setter
    def db_proxy_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "db_proxy_name", value)

    @property
    @pulumi.getter(name="targetGroupName")
    def target_group_name(self) -> pulumi.Input[str]:
        """
        The name of the target group.
        """
        return pulumi.get(self, "target_group_name")

    @target_group_name.setter
    def target_group_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "target_group_name", value)

    @property
    @pulumi.getter(name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> Optional[pulumi.Input[str]]:
        """
        DB cluster identifier.

        **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        """
        return pulumi.get(self, "db_cluster_identifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "db_cluster_identifier", value)

    @property
    @pulumi.getter(name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> Optional[pulumi.Input[str]]:
        """
        DB instance identifier.
        """
        return pulumi.get(self, "db_instance_identifier")

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "db_instance_identifier", value)


@pulumi.input_type
class _ProxyTargetState:
    def __init__(__self__, *,
                 db_cluster_identifier: Optional[pulumi.Input[str]] = None,
                 db_instance_identifier: Optional[pulumi.Input[str]] = None,
                 db_proxy_name: Optional[pulumi.Input[str]] = None,
                 endpoint: Optional[pulumi.Input[str]] = None,
                 port: Optional[pulumi.Input[int]] = None,
                 rds_resource_id: Optional[pulumi.Input[str]] = None,
                 target_arn: Optional[pulumi.Input[str]] = None,
                 target_group_name: Optional[pulumi.Input[str]] = None,
                 tracked_cluster_id: Optional[pulumi.Input[str]] = None,
                 type: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering ProxyTarget resources.
        :param pulumi.Input[str] db_cluster_identifier: DB cluster identifier.
               
               **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        :param pulumi.Input[str] db_instance_identifier: DB instance identifier.
        :param pulumi.Input[str] db_proxy_name: The name of the DB proxy.
        :param pulumi.Input[str] endpoint: Hostname for the target RDS DB Instance. Only returned for `RDS_INSTANCE` type.
        :param pulumi.Input[int] port: Port for the target RDS DB Instance or Aurora DB Cluster.
        :param pulumi.Input[str] rds_resource_id: Identifier representing the DB Instance or DB Cluster target.
        :param pulumi.Input[str] target_arn: Amazon Resource Name (ARN) for the DB instance or DB cluster. Currently not returned by the RDS API.
        :param pulumi.Input[str] target_group_name: The name of the target group.
        :param pulumi.Input[str] tracked_cluster_id: DB Cluster identifier for the DB Instance target. Not returned unless manually importing an `RDS_INSTANCE` target that is part of a DB Cluster.
        :param pulumi.Input[str] type: Type of targetE.g., `RDS_INSTANCE` or `TRACKED_CLUSTER`
        """
        if db_cluster_identifier is not None:
            pulumi.set(__self__, "db_cluster_identifier", db_cluster_identifier)
        if db_instance_identifier is not None:
            pulumi.set(__self__, "db_instance_identifier", db_instance_identifier)
        if db_proxy_name is not None:
            pulumi.set(__self__, "db_proxy_name", db_proxy_name)
        if endpoint is not None:
            pulumi.set(__self__, "endpoint", endpoint)
        if port is not None:
            pulumi.set(__self__, "port", port)
        if rds_resource_id is not None:
            pulumi.set(__self__, "rds_resource_id", rds_resource_id)
        if target_arn is not None:
            pulumi.set(__self__, "target_arn", target_arn)
        if target_group_name is not None:
            pulumi.set(__self__, "target_group_name", target_group_name)
        if tracked_cluster_id is not None:
            pulumi.set(__self__, "tracked_cluster_id", tracked_cluster_id)
        if type is not None:
            pulumi.set(__self__, "type", type)

    @property
    @pulumi.getter(name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> Optional[pulumi.Input[str]]:
        """
        DB cluster identifier.

        **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        """
        return pulumi.get(self, "db_cluster_identifier")

    @db_cluster_identifier.setter
    def db_cluster_identifier(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "db_cluster_identifier", value)

    @property
    @pulumi.getter(name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> Optional[pulumi.Input[str]]:
        """
        DB instance identifier.
        """
        return pulumi.get(self, "db_instance_identifier")

    @db_instance_identifier.setter
    def db_instance_identifier(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "db_instance_identifier", value)

    @property
    @pulumi.getter(name="dbProxyName")
    def db_proxy_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the DB proxy.
        """
        return pulumi.get(self, "db_proxy_name")

    @db_proxy_name.setter
    def db_proxy_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "db_proxy_name", value)

    @property
    @pulumi.getter
    def endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        Hostname for the target RDS DB Instance. Only returned for `RDS_INSTANCE` type.
        """
        return pulumi.get(self, "endpoint")

    @endpoint.setter
    def endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "endpoint", value)

    @property
    @pulumi.getter
    def port(self) -> Optional[pulumi.Input[int]]:
        """
        Port for the target RDS DB Instance or Aurora DB Cluster.
        """
        return pulumi.get(self, "port")

    @port.setter
    def port(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "port", value)

    @property
    @pulumi.getter(name="rdsResourceId")
    def rds_resource_id(self) -> Optional[pulumi.Input[str]]:
        """
        Identifier representing the DB Instance or DB Cluster target.
        """
        return pulumi.get(self, "rds_resource_id")

    @rds_resource_id.setter
    def rds_resource_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "rds_resource_id", value)

    @property
    @pulumi.getter(name="targetArn")
    def target_arn(self) -> Optional[pulumi.Input[str]]:
        """
        Amazon Resource Name (ARN) for the DB instance or DB cluster. Currently not returned by the RDS API.
        """
        return pulumi.get(self, "target_arn")

    @target_arn.setter
    def target_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "target_arn", value)

    @property
    @pulumi.getter(name="targetGroupName")
    def target_group_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the target group.
        """
        return pulumi.get(self, "target_group_name")

    @target_group_name.setter
    def target_group_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "target_group_name", value)

    @property
    @pulumi.getter(name="trackedClusterId")
    def tracked_cluster_id(self) -> Optional[pulumi.Input[str]]:
        """
        DB Cluster identifier for the DB Instance target. Not returned unless manually importing an `RDS_INSTANCE` target that is part of a DB Cluster.
        """
        return pulumi.get(self, "tracked_cluster_id")

    @tracked_cluster_id.setter
    def tracked_cluster_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "tracked_cluster_id", value)

    @property
    @pulumi.getter
    def type(self) -> Optional[pulumi.Input[str]]:
        """
        Type of targetE.g., `RDS_INSTANCE` or `TRACKED_CLUSTER`
        """
        return pulumi.get(self, "type")

    @type.setter
    def type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "type", value)


class ProxyTarget(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 db_cluster_identifier: Optional[pulumi.Input[str]] = None,
                 db_instance_identifier: Optional[pulumi.Input[str]] = None,
                 db_proxy_name: Optional[pulumi.Input[str]] = None,
                 target_group_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides an RDS DB proxy target resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_proxy = aws.rds.Proxy("exampleProxy",
            debug_logging=False,
            engine_family="MYSQL",
            idle_client_timeout=1800,
            require_tls=True,
            role_arn=aws_iam_role["example"]["arn"],
            vpc_security_group_ids=[aws_security_group["example"]["id"]],
            vpc_subnet_ids=[aws_subnet["example"]["id"]],
            auths=[aws.rds.ProxyAuthArgs(
                auth_scheme="SECRETS",
                description="example",
                iam_auth="DISABLED",
                secret_arn=aws_secretsmanager_secret["example"]["arn"],
            )],
            tags={
                "Name": "example",
                "Key": "value",
            })
        example_proxy_default_target_group = aws.rds.ProxyDefaultTargetGroup("exampleProxyDefaultTargetGroup",
            db_proxy_name=example_proxy.name,
            connection_pool_config=aws.rds.ProxyDefaultTargetGroupConnectionPoolConfigArgs(
                connection_borrow_timeout=120,
                init_query="SET x=1, y=2",
                max_connections_percent=100,
                max_idle_connections_percent=50,
                session_pinning_filters=["EXCLUDE_VARIABLE_SETS"],
            ))
        example_proxy_target = aws.rds.ProxyTarget("exampleProxyTarget",
            db_instance_identifier=aws_db_instance["example"]["identifier"],
            db_proxy_name=example_proxy.name,
            target_group_name=example_proxy_default_target_group.name)
        ```

        ## Import

        Provisioned Clusters:

        __Using `pulumi import` to import__ RDS DB Proxy Targets using the `db_proxy_name`, `target_group_name`, target type (such as `RDS_INSTANCE` or `TRACKED_CLUSTER`), and resource identifier separated by forward slashes (`/`). For example:

        Instances:

        ```sh
         $ pulumi import aws:rds/proxyTarget:ProxyTarget example example-proxy/default/RDS_INSTANCE/example-instance
        ```
         Provisioned Clusters:

        ```sh
         $ pulumi import aws:rds/proxyTarget:ProxyTarget example example-proxy/default/TRACKED_CLUSTER/example-cluster
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] db_cluster_identifier: DB cluster identifier.
               
               **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        :param pulumi.Input[str] db_instance_identifier: DB instance identifier.
        :param pulumi.Input[str] db_proxy_name: The name of the DB proxy.
        :param pulumi.Input[str] target_group_name: The name of the target group.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: ProxyTargetArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an RDS DB proxy target resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example_proxy = aws.rds.Proxy("exampleProxy",
            debug_logging=False,
            engine_family="MYSQL",
            idle_client_timeout=1800,
            require_tls=True,
            role_arn=aws_iam_role["example"]["arn"],
            vpc_security_group_ids=[aws_security_group["example"]["id"]],
            vpc_subnet_ids=[aws_subnet["example"]["id"]],
            auths=[aws.rds.ProxyAuthArgs(
                auth_scheme="SECRETS",
                description="example",
                iam_auth="DISABLED",
                secret_arn=aws_secretsmanager_secret["example"]["arn"],
            )],
            tags={
                "Name": "example",
                "Key": "value",
            })
        example_proxy_default_target_group = aws.rds.ProxyDefaultTargetGroup("exampleProxyDefaultTargetGroup",
            db_proxy_name=example_proxy.name,
            connection_pool_config=aws.rds.ProxyDefaultTargetGroupConnectionPoolConfigArgs(
                connection_borrow_timeout=120,
                init_query="SET x=1, y=2",
                max_connections_percent=100,
                max_idle_connections_percent=50,
                session_pinning_filters=["EXCLUDE_VARIABLE_SETS"],
            ))
        example_proxy_target = aws.rds.ProxyTarget("exampleProxyTarget",
            db_instance_identifier=aws_db_instance["example"]["identifier"],
            db_proxy_name=example_proxy.name,
            target_group_name=example_proxy_default_target_group.name)
        ```

        ## Import

        Provisioned Clusters:

        __Using `pulumi import` to import__ RDS DB Proxy Targets using the `db_proxy_name`, `target_group_name`, target type (such as `RDS_INSTANCE` or `TRACKED_CLUSTER`), and resource identifier separated by forward slashes (`/`). For example:

        Instances:

        ```sh
         $ pulumi import aws:rds/proxyTarget:ProxyTarget example example-proxy/default/RDS_INSTANCE/example-instance
        ```
         Provisioned Clusters:

        ```sh
         $ pulumi import aws:rds/proxyTarget:ProxyTarget example example-proxy/default/TRACKED_CLUSTER/example-cluster
        ```

        :param str resource_name: The name of the resource.
        :param ProxyTargetArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(ProxyTargetArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 db_cluster_identifier: Optional[pulumi.Input[str]] = None,
                 db_instance_identifier: Optional[pulumi.Input[str]] = None,
                 db_proxy_name: Optional[pulumi.Input[str]] = None,
                 target_group_name: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = ProxyTargetArgs.__new__(ProxyTargetArgs)

            __props__.__dict__["db_cluster_identifier"] = db_cluster_identifier
            __props__.__dict__["db_instance_identifier"] = db_instance_identifier
            if db_proxy_name is None and not opts.urn:
                raise TypeError("Missing required property 'db_proxy_name'")
            __props__.__dict__["db_proxy_name"] = db_proxy_name
            if target_group_name is None and not opts.urn:
                raise TypeError("Missing required property 'target_group_name'")
            __props__.__dict__["target_group_name"] = target_group_name
            __props__.__dict__["endpoint"] = None
            __props__.__dict__["port"] = None
            __props__.__dict__["rds_resource_id"] = None
            __props__.__dict__["target_arn"] = None
            __props__.__dict__["tracked_cluster_id"] = None
            __props__.__dict__["type"] = None
        super(ProxyTarget, __self__).__init__(
            'aws:rds/proxyTarget:ProxyTarget',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            db_cluster_identifier: Optional[pulumi.Input[str]] = None,
            db_instance_identifier: Optional[pulumi.Input[str]] = None,
            db_proxy_name: Optional[pulumi.Input[str]] = None,
            endpoint: Optional[pulumi.Input[str]] = None,
            port: Optional[pulumi.Input[int]] = None,
            rds_resource_id: Optional[pulumi.Input[str]] = None,
            target_arn: Optional[pulumi.Input[str]] = None,
            target_group_name: Optional[pulumi.Input[str]] = None,
            tracked_cluster_id: Optional[pulumi.Input[str]] = None,
            type: Optional[pulumi.Input[str]] = None) -> 'ProxyTarget':
        """
        Get an existing ProxyTarget resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] db_cluster_identifier: DB cluster identifier.
               
               **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        :param pulumi.Input[str] db_instance_identifier: DB instance identifier.
        :param pulumi.Input[str] db_proxy_name: The name of the DB proxy.
        :param pulumi.Input[str] endpoint: Hostname for the target RDS DB Instance. Only returned for `RDS_INSTANCE` type.
        :param pulumi.Input[int] port: Port for the target RDS DB Instance or Aurora DB Cluster.
        :param pulumi.Input[str] rds_resource_id: Identifier representing the DB Instance or DB Cluster target.
        :param pulumi.Input[str] target_arn: Amazon Resource Name (ARN) for the DB instance or DB cluster. Currently not returned by the RDS API.
        :param pulumi.Input[str] target_group_name: The name of the target group.
        :param pulumi.Input[str] tracked_cluster_id: DB Cluster identifier for the DB Instance target. Not returned unless manually importing an `RDS_INSTANCE` target that is part of a DB Cluster.
        :param pulumi.Input[str] type: Type of targetE.g., `RDS_INSTANCE` or `TRACKED_CLUSTER`
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _ProxyTargetState.__new__(_ProxyTargetState)

        __props__.__dict__["db_cluster_identifier"] = db_cluster_identifier
        __props__.__dict__["db_instance_identifier"] = db_instance_identifier
        __props__.__dict__["db_proxy_name"] = db_proxy_name
        __props__.__dict__["endpoint"] = endpoint
        __props__.__dict__["port"] = port
        __props__.__dict__["rds_resource_id"] = rds_resource_id
        __props__.__dict__["target_arn"] = target_arn
        __props__.__dict__["target_group_name"] = target_group_name
        __props__.__dict__["tracked_cluster_id"] = tracked_cluster_id
        __props__.__dict__["type"] = type
        return ProxyTarget(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="dbClusterIdentifier")
    def db_cluster_identifier(self) -> pulumi.Output[Optional[str]]:
        """
        DB cluster identifier.

        **NOTE:** Either `db_instance_identifier` or `db_cluster_identifier` should be specified and both should not be specified together
        """
        return pulumi.get(self, "db_cluster_identifier")

    @property
    @pulumi.getter(name="dbInstanceIdentifier")
    def db_instance_identifier(self) -> pulumi.Output[Optional[str]]:
        """
        DB instance identifier.
        """
        return pulumi.get(self, "db_instance_identifier")

    @property
    @pulumi.getter(name="dbProxyName")
    def db_proxy_name(self) -> pulumi.Output[str]:
        """
        The name of the DB proxy.
        """
        return pulumi.get(self, "db_proxy_name")

    @property
    @pulumi.getter
    def endpoint(self) -> pulumi.Output[str]:
        """
        Hostname for the target RDS DB Instance. Only returned for `RDS_INSTANCE` type.
        """
        return pulumi.get(self, "endpoint")

    @property
    @pulumi.getter
    def port(self) -> pulumi.Output[int]:
        """
        Port for the target RDS DB Instance or Aurora DB Cluster.
        """
        return pulumi.get(self, "port")

    @property
    @pulumi.getter(name="rdsResourceId")
    def rds_resource_id(self) -> pulumi.Output[str]:
        """
        Identifier representing the DB Instance or DB Cluster target.
        """
        return pulumi.get(self, "rds_resource_id")

    @property
    @pulumi.getter(name="targetArn")
    def target_arn(self) -> pulumi.Output[str]:
        """
        Amazon Resource Name (ARN) for the DB instance or DB cluster. Currently not returned by the RDS API.
        """
        return pulumi.get(self, "target_arn")

    @property
    @pulumi.getter(name="targetGroupName")
    def target_group_name(self) -> pulumi.Output[str]:
        """
        The name of the target group.
        """
        return pulumi.get(self, "target_group_name")

    @property
    @pulumi.getter(name="trackedClusterId")
    def tracked_cluster_id(self) -> pulumi.Output[str]:
        """
        DB Cluster identifier for the DB Instance target. Not returned unless manually importing an `RDS_INSTANCE` target that is part of a DB Cluster.
        """
        return pulumi.get(self, "tracked_cluster_id")

    @property
    @pulumi.getter
    def type(self) -> pulumi.Output[str]:
        """
        Type of targetE.g., `RDS_INSTANCE` or `TRACKED_CLUSTER`
        """
        return pulumi.get(self, "type")

