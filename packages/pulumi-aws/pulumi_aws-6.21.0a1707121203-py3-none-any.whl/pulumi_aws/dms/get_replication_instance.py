# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = [
    'GetReplicationInstanceResult',
    'AwaitableGetReplicationInstanceResult',
    'get_replication_instance',
    'get_replication_instance_output',
]

@pulumi.output_type
class GetReplicationInstanceResult:
    """
    A collection of values returned by getReplicationInstance.
    """
    def __init__(__self__, allocated_storage=None, auto_minor_version_upgrade=None, availability_zone=None, engine_version=None, id=None, kms_key_arn=None, multi_az=None, network_type=None, preferred_maintenance_window=None, publicly_accessible=None, replication_instance_arn=None, replication_instance_class=None, replication_instance_id=None, replication_instance_private_ips=None, replication_instance_public_ips=None, replication_subnet_group_id=None, tags=None, vpc_security_group_ids=None):
        if allocated_storage and not isinstance(allocated_storage, int):
            raise TypeError("Expected argument 'allocated_storage' to be a int")
        pulumi.set(__self__, "allocated_storage", allocated_storage)
        if auto_minor_version_upgrade and not isinstance(auto_minor_version_upgrade, bool):
            raise TypeError("Expected argument 'auto_minor_version_upgrade' to be a bool")
        pulumi.set(__self__, "auto_minor_version_upgrade", auto_minor_version_upgrade)
        if availability_zone and not isinstance(availability_zone, str):
            raise TypeError("Expected argument 'availability_zone' to be a str")
        pulumi.set(__self__, "availability_zone", availability_zone)
        if engine_version and not isinstance(engine_version, str):
            raise TypeError("Expected argument 'engine_version' to be a str")
        pulumi.set(__self__, "engine_version", engine_version)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if kms_key_arn and not isinstance(kms_key_arn, str):
            raise TypeError("Expected argument 'kms_key_arn' to be a str")
        pulumi.set(__self__, "kms_key_arn", kms_key_arn)
        if multi_az and not isinstance(multi_az, bool):
            raise TypeError("Expected argument 'multi_az' to be a bool")
        pulumi.set(__self__, "multi_az", multi_az)
        if network_type and not isinstance(network_type, str):
            raise TypeError("Expected argument 'network_type' to be a str")
        pulumi.set(__self__, "network_type", network_type)
        if preferred_maintenance_window and not isinstance(preferred_maintenance_window, str):
            raise TypeError("Expected argument 'preferred_maintenance_window' to be a str")
        pulumi.set(__self__, "preferred_maintenance_window", preferred_maintenance_window)
        if publicly_accessible and not isinstance(publicly_accessible, bool):
            raise TypeError("Expected argument 'publicly_accessible' to be a bool")
        pulumi.set(__self__, "publicly_accessible", publicly_accessible)
        if replication_instance_arn and not isinstance(replication_instance_arn, str):
            raise TypeError("Expected argument 'replication_instance_arn' to be a str")
        pulumi.set(__self__, "replication_instance_arn", replication_instance_arn)
        if replication_instance_class and not isinstance(replication_instance_class, str):
            raise TypeError("Expected argument 'replication_instance_class' to be a str")
        pulumi.set(__self__, "replication_instance_class", replication_instance_class)
        if replication_instance_id and not isinstance(replication_instance_id, str):
            raise TypeError("Expected argument 'replication_instance_id' to be a str")
        pulumi.set(__self__, "replication_instance_id", replication_instance_id)
        if replication_instance_private_ips and not isinstance(replication_instance_private_ips, list):
            raise TypeError("Expected argument 'replication_instance_private_ips' to be a list")
        pulumi.set(__self__, "replication_instance_private_ips", replication_instance_private_ips)
        if replication_instance_public_ips and not isinstance(replication_instance_public_ips, list):
            raise TypeError("Expected argument 'replication_instance_public_ips' to be a list")
        pulumi.set(__self__, "replication_instance_public_ips", replication_instance_public_ips)
        if replication_subnet_group_id and not isinstance(replication_subnet_group_id, str):
            raise TypeError("Expected argument 'replication_subnet_group_id' to be a str")
        pulumi.set(__self__, "replication_subnet_group_id", replication_subnet_group_id)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if vpc_security_group_ids and not isinstance(vpc_security_group_ids, list):
            raise TypeError("Expected argument 'vpc_security_group_ids' to be a list")
        pulumi.set(__self__, "vpc_security_group_ids", vpc_security_group_ids)

    @property
    @pulumi.getter(name="allocatedStorage")
    def allocated_storage(self) -> int:
        """
        The amount of storage (in gigabytes) to be initially allocated for the replication instance.
        """
        return pulumi.get(self, "allocated_storage")

    @property
    @pulumi.getter(name="autoMinorVersionUpgrade")
    def auto_minor_version_upgrade(self) -> bool:
        """
        Indicates that minor engine upgrades will be applied automatically to the replication instance during the maintenance window.
        """
        return pulumi.get(self, "auto_minor_version_upgrade")

    @property
    @pulumi.getter(name="availabilityZone")
    def availability_zone(self) -> str:
        """
        The EC2 Availability Zone that the replication instance will be created in.
        """
        return pulumi.get(self, "availability_zone")

    @property
    @pulumi.getter(name="engineVersion")
    def engine_version(self) -> str:
        """
        The engine version number of the replication instance.
        """
        return pulumi.get(self, "engine_version")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="kmsKeyArn")
    def kms_key_arn(self) -> str:
        """
        The Amazon Resource Name (ARN) for the KMS key used to encrypt the connection parameters.
        """
        return pulumi.get(self, "kms_key_arn")

    @property
    @pulumi.getter(name="multiAz")
    def multi_az(self) -> bool:
        """
        Specifies if the replication instance is a multi-az deployment.
        """
        return pulumi.get(self, "multi_az")

    @property
    @pulumi.getter(name="networkType")
    def network_type(self) -> str:
        """
        The type of IP address protocol used by the replication instance.
        """
        return pulumi.get(self, "network_type")

    @property
    @pulumi.getter(name="preferredMaintenanceWindow")
    def preferred_maintenance_window(self) -> str:
        """
        The weekly time range during which system maintenance can occur, in Universal Coordinated Time (UTC).
        """
        return pulumi.get(self, "preferred_maintenance_window")

    @property
    @pulumi.getter(name="publiclyAccessible")
    def publicly_accessible(self) -> bool:
        """
        Specifies the accessibility options for the replication instance. A value of true represents an instance with a public IP address. A value of false represents an instance with a private IP address.
        """
        return pulumi.get(self, "publicly_accessible")

    @property
    @pulumi.getter(name="replicationInstanceArn")
    def replication_instance_arn(self) -> str:
        """
        The Amazon Resource Name (ARN) of the replication instance.
        """
        return pulumi.get(self, "replication_instance_arn")

    @property
    @pulumi.getter(name="replicationInstanceClass")
    def replication_instance_class(self) -> str:
        """
        The compute and memory capacity of the replication instance as specified by the replication instance class. See [AWS DMS User Guide](https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.Types.html) for information on instance classes.
        """
        return pulumi.get(self, "replication_instance_class")

    @property
    @pulumi.getter(name="replicationInstanceId")
    def replication_instance_id(self) -> str:
        return pulumi.get(self, "replication_instance_id")

    @property
    @pulumi.getter(name="replicationInstancePrivateIps")
    def replication_instance_private_ips(self) -> Sequence[str]:
        """
        A list of the private IP addresses of the replication instance.
        """
        return pulumi.get(self, "replication_instance_private_ips")

    @property
    @pulumi.getter(name="replicationInstancePublicIps")
    def replication_instance_public_ips(self) -> Sequence[str]:
        """
        A list of the public IP addresses of the replication instance.
        """
        return pulumi.get(self, "replication_instance_public_ips")

    @property
    @pulumi.getter(name="replicationSubnetGroupId")
    def replication_subnet_group_id(self) -> str:
        """
        A subnet group to associate with the replication instance.
        """
        return pulumi.get(self, "replication_subnet_group_id")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="vpcSecurityGroupIds")
    def vpc_security_group_ids(self) -> Sequence[str]:
        """
        A set of VPC security group IDs that are used with the replication instance.
        """
        return pulumi.get(self, "vpc_security_group_ids")


class AwaitableGetReplicationInstanceResult(GetReplicationInstanceResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetReplicationInstanceResult(
            allocated_storage=self.allocated_storage,
            auto_minor_version_upgrade=self.auto_minor_version_upgrade,
            availability_zone=self.availability_zone,
            engine_version=self.engine_version,
            id=self.id,
            kms_key_arn=self.kms_key_arn,
            multi_az=self.multi_az,
            network_type=self.network_type,
            preferred_maintenance_window=self.preferred_maintenance_window,
            publicly_accessible=self.publicly_accessible,
            replication_instance_arn=self.replication_instance_arn,
            replication_instance_class=self.replication_instance_class,
            replication_instance_id=self.replication_instance_id,
            replication_instance_private_ips=self.replication_instance_private_ips,
            replication_instance_public_ips=self.replication_instance_public_ips,
            replication_subnet_group_id=self.replication_subnet_group_id,
            tags=self.tags,
            vpc_security_group_ids=self.vpc_security_group_ids)


def get_replication_instance(replication_instance_id: Optional[str] = None,
                             tags: Optional[Mapping[str, str]] = None,
                             opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetReplicationInstanceResult:
    """
    Data source for managing an AWS DMS (Database Migration) Replication Instance.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    test = aws.dms.get_replication_instance(replication_instance_id=aws_dms_replication_instance["test"]["replication_instance_id"])
    ```


    :param str replication_instance_id: The replication instance identifier.
    """
    __args__ = dict()
    __args__['replicationInstanceId'] = replication_instance_id
    __args__['tags'] = tags
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:dms/getReplicationInstance:getReplicationInstance', __args__, opts=opts, typ=GetReplicationInstanceResult).value

    return AwaitableGetReplicationInstanceResult(
        allocated_storage=pulumi.get(__ret__, 'allocated_storage'),
        auto_minor_version_upgrade=pulumi.get(__ret__, 'auto_minor_version_upgrade'),
        availability_zone=pulumi.get(__ret__, 'availability_zone'),
        engine_version=pulumi.get(__ret__, 'engine_version'),
        id=pulumi.get(__ret__, 'id'),
        kms_key_arn=pulumi.get(__ret__, 'kms_key_arn'),
        multi_az=pulumi.get(__ret__, 'multi_az'),
        network_type=pulumi.get(__ret__, 'network_type'),
        preferred_maintenance_window=pulumi.get(__ret__, 'preferred_maintenance_window'),
        publicly_accessible=pulumi.get(__ret__, 'publicly_accessible'),
        replication_instance_arn=pulumi.get(__ret__, 'replication_instance_arn'),
        replication_instance_class=pulumi.get(__ret__, 'replication_instance_class'),
        replication_instance_id=pulumi.get(__ret__, 'replication_instance_id'),
        replication_instance_private_ips=pulumi.get(__ret__, 'replication_instance_private_ips'),
        replication_instance_public_ips=pulumi.get(__ret__, 'replication_instance_public_ips'),
        replication_subnet_group_id=pulumi.get(__ret__, 'replication_subnet_group_id'),
        tags=pulumi.get(__ret__, 'tags'),
        vpc_security_group_ids=pulumi.get(__ret__, 'vpc_security_group_ids'))


@_utilities.lift_output_func(get_replication_instance)
def get_replication_instance_output(replication_instance_id: Optional[pulumi.Input[str]] = None,
                                    tags: Optional[pulumi.Input[Optional[Mapping[str, str]]]] = None,
                                    opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetReplicationInstanceResult]:
    """
    Data source for managing an AWS DMS (Database Migration) Replication Instance.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    test = aws.dms.get_replication_instance(replication_instance_id=aws_dms_replication_instance["test"]["replication_instance_id"])
    ```


    :param str replication_instance_id: The replication instance identifier.
    """
    ...
