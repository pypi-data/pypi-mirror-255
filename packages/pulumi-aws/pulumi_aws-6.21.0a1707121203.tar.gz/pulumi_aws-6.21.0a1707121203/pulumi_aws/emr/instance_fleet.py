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

__all__ = ['InstanceFleetArgs', 'InstanceFleet']

@pulumi.input_type
class InstanceFleetArgs:
    def __init__(__self__, *,
                 cluster_id: pulumi.Input[str],
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]]] = None,
                 launch_specifications: Optional[pulumi.Input['InstanceFleetLaunchSpecificationsArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None):
        """
        The set of arguments for constructing a InstanceFleet resource.
        :param pulumi.Input[str] cluster_id: ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]] instance_type_configs: Configuration block for instance fleet
        :param pulumi.Input['InstanceFleetLaunchSpecificationsArgs'] launch_specifications: Configuration block for launch specification
        :param pulumi.Input[str] name: Friendly name given to the instance fleet.
        :param pulumi.Input[int] target_on_demand_capacity: The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        :param pulumi.Input[int] target_spot_capacity: The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        pulumi.set(__self__, "cluster_id", cluster_id)
        if instance_type_configs is not None:
            pulumi.set(__self__, "instance_type_configs", instance_type_configs)
        if launch_specifications is not None:
            pulumi.set(__self__, "launch_specifications", launch_specifications)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if target_on_demand_capacity is not None:
            pulumi.set(__self__, "target_on_demand_capacity", target_on_demand_capacity)
        if target_spot_capacity is not None:
            pulumi.set(__self__, "target_spot_capacity", target_spot_capacity)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Input[str]:
        """
        ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "cluster_id")

    @cluster_id.setter
    def cluster_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "cluster_id", value)

    @property
    @pulumi.getter(name="instanceTypeConfigs")
    def instance_type_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]]]:
        """
        Configuration block for instance fleet
        """
        return pulumi.get(self, "instance_type_configs")

    @instance_type_configs.setter
    def instance_type_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]]]):
        pulumi.set(self, "instance_type_configs", value)

    @property
    @pulumi.getter(name="launchSpecifications")
    def launch_specifications(self) -> Optional[pulumi.Input['InstanceFleetLaunchSpecificationsArgs']]:
        """
        Configuration block for launch specification
        """
        return pulumi.get(self, "launch_specifications")

    @launch_specifications.setter
    def launch_specifications(self, value: Optional[pulumi.Input['InstanceFleetLaunchSpecificationsArgs']]):
        pulumi.set(self, "launch_specifications", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Friendly name given to the instance fleet.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        """
        return pulumi.get(self, "target_on_demand_capacity")

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_on_demand_capacity", value)

    @property
    @pulumi.getter(name="targetSpotCapacity")
    def target_spot_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        return pulumi.get(self, "target_spot_capacity")

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_spot_capacity", value)


@pulumi.input_type
class _InstanceFleetState:
    def __init__(__self__, *,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]]] = None,
                 launch_specifications: Optional[pulumi.Input['InstanceFleetLaunchSpecificationsArgs']] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 provisioned_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 provisioned_spot_capacity: Optional[pulumi.Input[int]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None):
        """
        Input properties used for looking up and filtering InstanceFleet resources.
        :param pulumi.Input[str] cluster_id: ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]] instance_type_configs: Configuration block for instance fleet
        :param pulumi.Input['InstanceFleetLaunchSpecificationsArgs'] launch_specifications: Configuration block for launch specification
        :param pulumi.Input[str] name: Friendly name given to the instance fleet.
        :param pulumi.Input[int] provisioned_on_demand_capacity: The number of On-Demand units that have been provisioned for the instance
               fleet to fulfill TargetOnDemandCapacity. This provisioned capacity might be less than or greater than TargetOnDemandCapacity.
        :param pulumi.Input[int] provisioned_spot_capacity: The number of Spot units that have been provisioned for this instance fleet
               to fulfill TargetSpotCapacity. This provisioned capacity might be less than or greater than TargetSpotCapacity.
        :param pulumi.Input[int] target_on_demand_capacity: The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        :param pulumi.Input[int] target_spot_capacity: The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        if cluster_id is not None:
            pulumi.set(__self__, "cluster_id", cluster_id)
        if instance_type_configs is not None:
            pulumi.set(__self__, "instance_type_configs", instance_type_configs)
        if launch_specifications is not None:
            pulumi.set(__self__, "launch_specifications", launch_specifications)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if provisioned_on_demand_capacity is not None:
            pulumi.set(__self__, "provisioned_on_demand_capacity", provisioned_on_demand_capacity)
        if provisioned_spot_capacity is not None:
            pulumi.set(__self__, "provisioned_spot_capacity", provisioned_spot_capacity)
        if target_on_demand_capacity is not None:
            pulumi.set(__self__, "target_on_demand_capacity", target_on_demand_capacity)
        if target_spot_capacity is not None:
            pulumi.set(__self__, "target_spot_capacity", target_spot_capacity)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> Optional[pulumi.Input[str]]:
        """
        ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "cluster_id")

    @cluster_id.setter
    def cluster_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "cluster_id", value)

    @property
    @pulumi.getter(name="instanceTypeConfigs")
    def instance_type_configs(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]]]:
        """
        Configuration block for instance fleet
        """
        return pulumi.get(self, "instance_type_configs")

    @instance_type_configs.setter
    def instance_type_configs(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['InstanceFleetInstanceTypeConfigArgs']]]]):
        pulumi.set(self, "instance_type_configs", value)

    @property
    @pulumi.getter(name="launchSpecifications")
    def launch_specifications(self) -> Optional[pulumi.Input['InstanceFleetLaunchSpecificationsArgs']]:
        """
        Configuration block for launch specification
        """
        return pulumi.get(self, "launch_specifications")

    @launch_specifications.setter
    def launch_specifications(self, value: Optional[pulumi.Input['InstanceFleetLaunchSpecificationsArgs']]):
        pulumi.set(self, "launch_specifications", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        Friendly name given to the instance fleet.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="provisionedOnDemandCapacity")
    def provisioned_on_demand_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        The number of On-Demand units that have been provisioned for the instance
        fleet to fulfill TargetOnDemandCapacity. This provisioned capacity might be less than or greater than TargetOnDemandCapacity.
        """
        return pulumi.get(self, "provisioned_on_demand_capacity")

    @provisioned_on_demand_capacity.setter
    def provisioned_on_demand_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "provisioned_on_demand_capacity", value)

    @property
    @pulumi.getter(name="provisionedSpotCapacity")
    def provisioned_spot_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        The number of Spot units that have been provisioned for this instance fleet
        to fulfill TargetSpotCapacity. This provisioned capacity might be less than or greater than TargetSpotCapacity.
        """
        return pulumi.get(self, "provisioned_spot_capacity")

    @provisioned_spot_capacity.setter
    def provisioned_spot_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "provisioned_spot_capacity", value)

    @property
    @pulumi.getter(name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        """
        return pulumi.get(self, "target_on_demand_capacity")

    @target_on_demand_capacity.setter
    def target_on_demand_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_on_demand_capacity", value)

    @property
    @pulumi.getter(name="targetSpotCapacity")
    def target_spot_capacity(self) -> Optional[pulumi.Input[int]]:
        """
        The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        return pulumi.get(self, "target_spot_capacity")

    @target_spot_capacity.setter
    def target_spot_capacity(self, value: Optional[pulumi.Input[int]]):
        pulumi.set(self, "target_spot_capacity", value)


class InstanceFleet(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetInstanceTypeConfigArgs']]]]] = None,
                 launch_specifications: Optional[pulumi.Input[pulumi.InputType['InstanceFleetLaunchSpecificationsArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        """
        Provides an Elastic MapReduce Cluster Instance Fleet configuration.
        See [Amazon Elastic MapReduce Documentation](https://aws.amazon.com/documentation/emr/) for more information.

        > **NOTE:** At this time, Instance Fleets cannot be destroyed through the API nor
        web interface. Instance Fleets are destroyed when the EMR Cluster is destroyed.
        the provider will resize any Instance Fleet to zero when destroying the resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        task = aws.emr.InstanceFleet("task",
            cluster_id=aws_emr_cluster["cluster"]["id"],
            instance_type_configs=[
                aws.emr.InstanceFleetInstanceTypeConfigArgs(
                    bid_price_as_percentage_of_on_demand_price=100,
                    ebs_configs=[aws.emr.InstanceFleetInstanceTypeConfigEbsConfigArgs(
                        size=100,
                        type="gp2",
                        volumes_per_instance=1,
                    )],
                    instance_type="m4.xlarge",
                    weighted_capacity=1,
                ),
                aws.emr.InstanceFleetInstanceTypeConfigArgs(
                    bid_price_as_percentage_of_on_demand_price=100,
                    ebs_configs=[aws.emr.InstanceFleetInstanceTypeConfigEbsConfigArgs(
                        size=100,
                        type="gp2",
                        volumes_per_instance=1,
                    )],
                    instance_type="m4.2xlarge",
                    weighted_capacity=2,
                ),
            ],
            launch_specifications=aws.emr.InstanceFleetLaunchSpecificationsArgs(
                spot_specifications=[aws.emr.InstanceFleetLaunchSpecificationsSpotSpecificationArgs(
                    allocation_strategy="capacity-optimized",
                    block_duration_minutes=0,
                    timeout_action="TERMINATE_CLUSTER",
                    timeout_duration_minutes=10,
                )],
            ),
            target_on_demand_capacity=1,
            target_spot_capacity=1)
        ```

        ## Import

        Using `pulumi import`, import EMR Instance Fleet using the EMR Cluster identifier and Instance Fleet identifier separated by a forward slash (`/`). For example:

        ```sh
         $ pulumi import aws:emr/instanceFleet:InstanceFleet example j-123456ABCDEF/if-15EK4O09RZLNR
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cluster_id: ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetInstanceTypeConfigArgs']]]] instance_type_configs: Configuration block for instance fleet
        :param pulumi.Input[pulumi.InputType['InstanceFleetLaunchSpecificationsArgs']] launch_specifications: Configuration block for launch specification
        :param pulumi.Input[str] name: Friendly name given to the instance fleet.
        :param pulumi.Input[int] target_on_demand_capacity: The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        :param pulumi.Input[int] target_spot_capacity: The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: InstanceFleetArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an Elastic MapReduce Cluster Instance Fleet configuration.
        See [Amazon Elastic MapReduce Documentation](https://aws.amazon.com/documentation/emr/) for more information.

        > **NOTE:** At this time, Instance Fleets cannot be destroyed through the API nor
        web interface. Instance Fleets are destroyed when the EMR Cluster is destroyed.
        the provider will resize any Instance Fleet to zero when destroying the resource.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        task = aws.emr.InstanceFleet("task",
            cluster_id=aws_emr_cluster["cluster"]["id"],
            instance_type_configs=[
                aws.emr.InstanceFleetInstanceTypeConfigArgs(
                    bid_price_as_percentage_of_on_demand_price=100,
                    ebs_configs=[aws.emr.InstanceFleetInstanceTypeConfigEbsConfigArgs(
                        size=100,
                        type="gp2",
                        volumes_per_instance=1,
                    )],
                    instance_type="m4.xlarge",
                    weighted_capacity=1,
                ),
                aws.emr.InstanceFleetInstanceTypeConfigArgs(
                    bid_price_as_percentage_of_on_demand_price=100,
                    ebs_configs=[aws.emr.InstanceFleetInstanceTypeConfigEbsConfigArgs(
                        size=100,
                        type="gp2",
                        volumes_per_instance=1,
                    )],
                    instance_type="m4.2xlarge",
                    weighted_capacity=2,
                ),
            ],
            launch_specifications=aws.emr.InstanceFleetLaunchSpecificationsArgs(
                spot_specifications=[aws.emr.InstanceFleetLaunchSpecificationsSpotSpecificationArgs(
                    allocation_strategy="capacity-optimized",
                    block_duration_minutes=0,
                    timeout_action="TERMINATE_CLUSTER",
                    timeout_duration_minutes=10,
                )],
            ),
            target_on_demand_capacity=1,
            target_spot_capacity=1)
        ```

        ## Import

        Using `pulumi import`, import EMR Instance Fleet using the EMR Cluster identifier and Instance Fleet identifier separated by a forward slash (`/`). For example:

        ```sh
         $ pulumi import aws:emr/instanceFleet:InstanceFleet example j-123456ABCDEF/if-15EK4O09RZLNR
        ```

        :param str resource_name: The name of the resource.
        :param InstanceFleetArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(InstanceFleetArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 cluster_id: Optional[pulumi.Input[str]] = None,
                 instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetInstanceTypeConfigArgs']]]]] = None,
                 launch_specifications: Optional[pulumi.Input[pulumi.InputType['InstanceFleetLaunchSpecificationsArgs']]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
                 target_spot_capacity: Optional[pulumi.Input[int]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = InstanceFleetArgs.__new__(InstanceFleetArgs)

            if cluster_id is None and not opts.urn:
                raise TypeError("Missing required property 'cluster_id'")
            __props__.__dict__["cluster_id"] = cluster_id
            __props__.__dict__["instance_type_configs"] = instance_type_configs
            __props__.__dict__["launch_specifications"] = launch_specifications
            __props__.__dict__["name"] = name
            __props__.__dict__["target_on_demand_capacity"] = target_on_demand_capacity
            __props__.__dict__["target_spot_capacity"] = target_spot_capacity
            __props__.__dict__["provisioned_on_demand_capacity"] = None
            __props__.__dict__["provisioned_spot_capacity"] = None
        super(InstanceFleet, __self__).__init__(
            'aws:emr/instanceFleet:InstanceFleet',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            cluster_id: Optional[pulumi.Input[str]] = None,
            instance_type_configs: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetInstanceTypeConfigArgs']]]]] = None,
            launch_specifications: Optional[pulumi.Input[pulumi.InputType['InstanceFleetLaunchSpecificationsArgs']]] = None,
            name: Optional[pulumi.Input[str]] = None,
            provisioned_on_demand_capacity: Optional[pulumi.Input[int]] = None,
            provisioned_spot_capacity: Optional[pulumi.Input[int]] = None,
            target_on_demand_capacity: Optional[pulumi.Input[int]] = None,
            target_spot_capacity: Optional[pulumi.Input[int]] = None) -> 'InstanceFleet':
        """
        Get an existing InstanceFleet resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] cluster_id: ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['InstanceFleetInstanceTypeConfigArgs']]]] instance_type_configs: Configuration block for instance fleet
        :param pulumi.Input[pulumi.InputType['InstanceFleetLaunchSpecificationsArgs']] launch_specifications: Configuration block for launch specification
        :param pulumi.Input[str] name: Friendly name given to the instance fleet.
        :param pulumi.Input[int] provisioned_on_demand_capacity: The number of On-Demand units that have been provisioned for the instance
               fleet to fulfill TargetOnDemandCapacity. This provisioned capacity might be less than or greater than TargetOnDemandCapacity.
        :param pulumi.Input[int] provisioned_spot_capacity: The number of Spot units that have been provisioned for this instance fleet
               to fulfill TargetSpotCapacity. This provisioned capacity might be less than or greater than TargetSpotCapacity.
        :param pulumi.Input[int] target_on_demand_capacity: The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        :param pulumi.Input[int] target_spot_capacity: The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _InstanceFleetState.__new__(_InstanceFleetState)

        __props__.__dict__["cluster_id"] = cluster_id
        __props__.__dict__["instance_type_configs"] = instance_type_configs
        __props__.__dict__["launch_specifications"] = launch_specifications
        __props__.__dict__["name"] = name
        __props__.__dict__["provisioned_on_demand_capacity"] = provisioned_on_demand_capacity
        __props__.__dict__["provisioned_spot_capacity"] = provisioned_spot_capacity
        __props__.__dict__["target_on_demand_capacity"] = target_on_demand_capacity
        __props__.__dict__["target_spot_capacity"] = target_spot_capacity
        return InstanceFleet(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter(name="clusterId")
    def cluster_id(self) -> pulumi.Output[str]:
        """
        ID of the EMR Cluster to attach to. Changing this forces a new resource to be created.
        """
        return pulumi.get(self, "cluster_id")

    @property
    @pulumi.getter(name="instanceTypeConfigs")
    def instance_type_configs(self) -> pulumi.Output[Optional[Sequence['outputs.InstanceFleetInstanceTypeConfig']]]:
        """
        Configuration block for instance fleet
        """
        return pulumi.get(self, "instance_type_configs")

    @property
    @pulumi.getter(name="launchSpecifications")
    def launch_specifications(self) -> pulumi.Output[Optional['outputs.InstanceFleetLaunchSpecifications']]:
        """
        Configuration block for launch specification
        """
        return pulumi.get(self, "launch_specifications")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        Friendly name given to the instance fleet.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="provisionedOnDemandCapacity")
    def provisioned_on_demand_capacity(self) -> pulumi.Output[int]:
        """
        The number of On-Demand units that have been provisioned for the instance
        fleet to fulfill TargetOnDemandCapacity. This provisioned capacity might be less than or greater than TargetOnDemandCapacity.
        """
        return pulumi.get(self, "provisioned_on_demand_capacity")

    @property
    @pulumi.getter(name="provisionedSpotCapacity")
    def provisioned_spot_capacity(self) -> pulumi.Output[int]:
        """
        The number of Spot units that have been provisioned for this instance fleet
        to fulfill TargetSpotCapacity. This provisioned capacity might be less than or greater than TargetSpotCapacity.
        """
        return pulumi.get(self, "provisioned_spot_capacity")

    @property
    @pulumi.getter(name="targetOnDemandCapacity")
    def target_on_demand_capacity(self) -> pulumi.Output[Optional[int]]:
        """
        The target capacity of On-Demand units for the instance fleet, which determines how many On-Demand instances to provision.
        """
        return pulumi.get(self, "target_on_demand_capacity")

    @property
    @pulumi.getter(name="targetSpotCapacity")
    def target_spot_capacity(self) -> pulumi.Output[Optional[int]]:
        """
        The target capacity of Spot units for the instance fleet, which determines how many Spot instances to provision.
        """
        return pulumi.get(self, "target_spot_capacity")

