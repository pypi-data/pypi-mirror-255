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

__all__ = ['KxDataviewArgs', 'KxDataview']

@pulumi.input_type
class KxDataviewArgs:
    def __init__(__self__, *,
                 auto_update: pulumi.Input[bool],
                 az_mode: pulumi.Input[str],
                 database_name: pulumi.Input[str],
                 environment_id: pulumi.Input[str],
                 availability_zone_id: Optional[pulumi.Input[str]] = None,
                 changeset_id: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 segment_configurations: Optional[pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        The set of arguments for constructing a KxDataview resource.
        :param pulumi.Input[bool] auto_update: The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        :param pulumi.Input[str] az_mode: The number of availability zones you want to assign per cluster. This can be one of the following:
        :param pulumi.Input[str] database_name: The name of the database where you want to create a dataview.
        :param pulumi.Input[str] environment_id: Unique identifier for the KX environment.
        :param pulumi.Input[str] availability_zone_id: The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        :param pulumi.Input[str] changeset_id: A unique identifier of the changeset of the database that you want to use to ingest data.
        :param pulumi.Input[str] description: A description for the dataview.
        :param pulumi.Input[str] name: A unique identifier for the dataview.
               
               The following arguments are optional:
        :param pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]] segment_configurations: The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        pulumi.set(__self__, "auto_update", auto_update)
        pulumi.set(__self__, "az_mode", az_mode)
        pulumi.set(__self__, "database_name", database_name)
        pulumi.set(__self__, "environment_id", environment_id)
        if availability_zone_id is not None:
            pulumi.set(__self__, "availability_zone_id", availability_zone_id)
        if changeset_id is not None:
            pulumi.set(__self__, "changeset_id", changeset_id)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if segment_configurations is not None:
            pulumi.set(__self__, "segment_configurations", segment_configurations)
        if tags is not None:
            pulumi.set(__self__, "tags", tags)

    @property
    @pulumi.getter(name="autoUpdate")
    def auto_update(self) -> pulumi.Input[bool]:
        """
        The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        """
        return pulumi.get(self, "auto_update")

    @auto_update.setter
    def auto_update(self, value: pulumi.Input[bool]):
        pulumi.set(self, "auto_update", value)

    @property
    @pulumi.getter(name="azMode")
    def az_mode(self) -> pulumi.Input[str]:
        """
        The number of availability zones you want to assign per cluster. This can be one of the following:
        """
        return pulumi.get(self, "az_mode")

    @az_mode.setter
    def az_mode(self, value: pulumi.Input[str]):
        pulumi.set(self, "az_mode", value)

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> pulumi.Input[str]:
        """
        The name of the database where you want to create a dataview.
        """
        return pulumi.get(self, "database_name")

    @database_name.setter
    def database_name(self, value: pulumi.Input[str]):
        pulumi.set(self, "database_name", value)

    @property
    @pulumi.getter(name="environmentId")
    def environment_id(self) -> pulumi.Input[str]:
        """
        Unique identifier for the KX environment.
        """
        return pulumi.get(self, "environment_id")

    @environment_id.setter
    def environment_id(self, value: pulumi.Input[str]):
        pulumi.set(self, "environment_id", value)

    @property
    @pulumi.getter(name="availabilityZoneId")
    def availability_zone_id(self) -> Optional[pulumi.Input[str]]:
        """
        The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        """
        return pulumi.get(self, "availability_zone_id")

    @availability_zone_id.setter
    def availability_zone_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "availability_zone_id", value)

    @property
    @pulumi.getter(name="changesetId")
    def changeset_id(self) -> Optional[pulumi.Input[str]]:
        """
        A unique identifier of the changeset of the database that you want to use to ingest data.
        """
        return pulumi.get(self, "changeset_id")

    @changeset_id.setter
    def changeset_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "changeset_id", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description for the dataview.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A unique identifier for the dataview.

        The following arguments are optional:
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="segmentConfigurations")
    def segment_configurations(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]]]:
        """
        The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        """
        return pulumi.get(self, "segment_configurations")

    @segment_configurations.setter
    def segment_configurations(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]]]):
        pulumi.set(self, "segment_configurations", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)


@pulumi.input_type
class _KxDataviewState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 auto_update: Optional[pulumi.Input[bool]] = None,
                 availability_zone_id: Optional[pulumi.Input[str]] = None,
                 az_mode: Optional[pulumi.Input[str]] = None,
                 changeset_id: Optional[pulumi.Input[str]] = None,
                 created_timestamp: Optional[pulumi.Input[str]] = None,
                 database_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 environment_id: Optional[pulumi.Input[str]] = None,
                 last_modified_timestamp: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 segment_configurations: Optional[pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]]] = None,
                 status: Optional[pulumi.Input[str]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None):
        """
        Input properties used for looking up and filtering KxDataview resources.
        :param pulumi.Input[str] arn: Amazon Resource Name (ARN) identifier of the KX dataview.
        :param pulumi.Input[bool] auto_update: The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        :param pulumi.Input[str] availability_zone_id: The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        :param pulumi.Input[str] az_mode: The number of availability zones you want to assign per cluster. This can be one of the following:
        :param pulumi.Input[str] changeset_id: A unique identifier of the changeset of the database that you want to use to ingest data.
        :param pulumi.Input[str] created_timestamp: Timestamp at which the dataview was created in FinSpace. Value determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        :param pulumi.Input[str] database_name: The name of the database where you want to create a dataview.
        :param pulumi.Input[str] description: A description for the dataview.
        :param pulumi.Input[str] environment_id: Unique identifier for the KX environment.
        :param pulumi.Input[str] last_modified_timestamp: The last time that the dataview was updated in FinSpace. The value is determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        :param pulumi.Input[str] name: A unique identifier for the dataview.
               
               The following arguments are optional:
        :param pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]] segment_configurations: The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: Map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if auto_update is not None:
            pulumi.set(__self__, "auto_update", auto_update)
        if availability_zone_id is not None:
            pulumi.set(__self__, "availability_zone_id", availability_zone_id)
        if az_mode is not None:
            pulumi.set(__self__, "az_mode", az_mode)
        if changeset_id is not None:
            pulumi.set(__self__, "changeset_id", changeset_id)
        if created_timestamp is not None:
            pulumi.set(__self__, "created_timestamp", created_timestamp)
        if database_name is not None:
            pulumi.set(__self__, "database_name", database_name)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if environment_id is not None:
            pulumi.set(__self__, "environment_id", environment_id)
        if last_modified_timestamp is not None:
            pulumi.set(__self__, "last_modified_timestamp", last_modified_timestamp)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if segment_configurations is not None:
            pulumi.set(__self__, "segment_configurations", segment_configurations)
        if status is not None:
            pulumi.set(__self__, "status", status)
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
        Amazon Resource Name (ARN) identifier of the KX dataview.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="autoUpdate")
    def auto_update(self) -> Optional[pulumi.Input[bool]]:
        """
        The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        """
        return pulumi.get(self, "auto_update")

    @auto_update.setter
    def auto_update(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "auto_update", value)

    @property
    @pulumi.getter(name="availabilityZoneId")
    def availability_zone_id(self) -> Optional[pulumi.Input[str]]:
        """
        The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        """
        return pulumi.get(self, "availability_zone_id")

    @availability_zone_id.setter
    def availability_zone_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "availability_zone_id", value)

    @property
    @pulumi.getter(name="azMode")
    def az_mode(self) -> Optional[pulumi.Input[str]]:
        """
        The number of availability zones you want to assign per cluster. This can be one of the following:
        """
        return pulumi.get(self, "az_mode")

    @az_mode.setter
    def az_mode(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "az_mode", value)

    @property
    @pulumi.getter(name="changesetId")
    def changeset_id(self) -> Optional[pulumi.Input[str]]:
        """
        A unique identifier of the changeset of the database that you want to use to ingest data.
        """
        return pulumi.get(self, "changeset_id")

    @changeset_id.setter
    def changeset_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "changeset_id", value)

    @property
    @pulumi.getter(name="createdTimestamp")
    def created_timestamp(self) -> Optional[pulumi.Input[str]]:
        """
        Timestamp at which the dataview was created in FinSpace. Value determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        """
        return pulumi.get(self, "created_timestamp")

    @created_timestamp.setter
    def created_timestamp(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "created_timestamp", value)

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the database where you want to create a dataview.
        """
        return pulumi.get(self, "database_name")

    @database_name.setter
    def database_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "database_name", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description for the dataview.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="environmentId")
    def environment_id(self) -> Optional[pulumi.Input[str]]:
        """
        Unique identifier for the KX environment.
        """
        return pulumi.get(self, "environment_id")

    @environment_id.setter
    def environment_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "environment_id", value)

    @property
    @pulumi.getter(name="lastModifiedTimestamp")
    def last_modified_timestamp(self) -> Optional[pulumi.Input[str]]:
        """
        The last time that the dataview was updated in FinSpace. The value is determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        """
        return pulumi.get(self, "last_modified_timestamp")

    @last_modified_timestamp.setter
    def last_modified_timestamp(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "last_modified_timestamp", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        A unique identifier for the dataview.

        The following arguments are optional:
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="segmentConfigurations")
    def segment_configurations(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]]]:
        """
        The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        """
        return pulumi.get(self, "segment_configurations")

    @segment_configurations.setter
    def segment_configurations(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['KxDataviewSegmentConfigurationArgs']]]]):
        pulumi.set(self, "segment_configurations", value)

    @property
    @pulumi.getter
    def status(self) -> Optional[pulumi.Input[str]]:
        return pulumi.get(self, "status")

    @status.setter
    def status(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "status", value)

    @property
    @pulumi.getter
    def tags(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @tags.setter
    def tags(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags", value)

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        Map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
        pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")

        return pulumi.get(self, "tags_all")

    @tags_all.setter
    def tags_all(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "tags_all", value)


class KxDataview(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 auto_update: Optional[pulumi.Input[bool]] = None,
                 availability_zone_id: Optional[pulumi.Input[str]] = None,
                 az_mode: Optional[pulumi.Input[str]] = None,
                 changeset_id: Optional[pulumi.Input[str]] = None,
                 database_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 environment_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 segment_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['KxDataviewSegmentConfigurationArgs']]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        """
        Resource for managing an AWS FinSpace Kx Dataview.

        ## Example Usage

        ## Import

        Using `pulumi import`, import an AWS FinSpace Kx Cluster using the `id` (environment ID and cluster name, comma-delimited). For example:

        ```sh
         $ pulumi import aws:finspace/kxDataview:KxDataview example n3ceo7wqxoxcti5tujqwzs,my-tf-kx-database,my-tf-kx-dataview
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] auto_update: The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        :param pulumi.Input[str] availability_zone_id: The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        :param pulumi.Input[str] az_mode: The number of availability zones you want to assign per cluster. This can be one of the following:
        :param pulumi.Input[str] changeset_id: A unique identifier of the changeset of the database that you want to use to ingest data.
        :param pulumi.Input[str] database_name: The name of the database where you want to create a dataview.
        :param pulumi.Input[str] description: A description for the dataview.
        :param pulumi.Input[str] environment_id: Unique identifier for the KX environment.
        :param pulumi.Input[str] name: A unique identifier for the dataview.
               
               The following arguments are optional:
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['KxDataviewSegmentConfigurationArgs']]]] segment_configurations: The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: KxDataviewArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing an AWS FinSpace Kx Dataview.

        ## Example Usage

        ## Import

        Using `pulumi import`, import an AWS FinSpace Kx Cluster using the `id` (environment ID and cluster name, comma-delimited). For example:

        ```sh
         $ pulumi import aws:finspace/kxDataview:KxDataview example n3ceo7wqxoxcti5tujqwzs,my-tf-kx-database,my-tf-kx-dataview
        ```

        :param str resource_name: The name of the resource.
        :param KxDataviewArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(KxDataviewArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 auto_update: Optional[pulumi.Input[bool]] = None,
                 availability_zone_id: Optional[pulumi.Input[str]] = None,
                 az_mode: Optional[pulumi.Input[str]] = None,
                 changeset_id: Optional[pulumi.Input[str]] = None,
                 database_name: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 environment_id: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 segment_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['KxDataviewSegmentConfigurationArgs']]]]] = None,
                 tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = KxDataviewArgs.__new__(KxDataviewArgs)

            if auto_update is None and not opts.urn:
                raise TypeError("Missing required property 'auto_update'")
            __props__.__dict__["auto_update"] = auto_update
            __props__.__dict__["availability_zone_id"] = availability_zone_id
            if az_mode is None and not opts.urn:
                raise TypeError("Missing required property 'az_mode'")
            __props__.__dict__["az_mode"] = az_mode
            __props__.__dict__["changeset_id"] = changeset_id
            if database_name is None and not opts.urn:
                raise TypeError("Missing required property 'database_name'")
            __props__.__dict__["database_name"] = database_name
            __props__.__dict__["description"] = description
            if environment_id is None and not opts.urn:
                raise TypeError("Missing required property 'environment_id'")
            __props__.__dict__["environment_id"] = environment_id
            __props__.__dict__["name"] = name
            __props__.__dict__["segment_configurations"] = segment_configurations
            __props__.__dict__["tags"] = tags
            __props__.__dict__["arn"] = None
            __props__.__dict__["created_timestamp"] = None
            __props__.__dict__["last_modified_timestamp"] = None
            __props__.__dict__["status"] = None
            __props__.__dict__["tags_all"] = None
        secret_opts = pulumi.ResourceOptions(additional_secret_outputs=["tagsAll"])
        opts = pulumi.ResourceOptions.merge(opts, secret_opts)
        super(KxDataview, __self__).__init__(
            'aws:finspace/kxDataview:KxDataview',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            auto_update: Optional[pulumi.Input[bool]] = None,
            availability_zone_id: Optional[pulumi.Input[str]] = None,
            az_mode: Optional[pulumi.Input[str]] = None,
            changeset_id: Optional[pulumi.Input[str]] = None,
            created_timestamp: Optional[pulumi.Input[str]] = None,
            database_name: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            environment_id: Optional[pulumi.Input[str]] = None,
            last_modified_timestamp: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            segment_configurations: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['KxDataviewSegmentConfigurationArgs']]]]] = None,
            status: Optional[pulumi.Input[str]] = None,
            tags: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
            tags_all: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None) -> 'KxDataview':
        """
        Get an existing KxDataview resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: Amazon Resource Name (ARN) identifier of the KX dataview.
        :param pulumi.Input[bool] auto_update: The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        :param pulumi.Input[str] availability_zone_id: The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        :param pulumi.Input[str] az_mode: The number of availability zones you want to assign per cluster. This can be one of the following:
        :param pulumi.Input[str] changeset_id: A unique identifier of the changeset of the database that you want to use to ingest data.
        :param pulumi.Input[str] created_timestamp: Timestamp at which the dataview was created in FinSpace. Value determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        :param pulumi.Input[str] database_name: The name of the database where you want to create a dataview.
        :param pulumi.Input[str] description: A description for the dataview.
        :param pulumi.Input[str] environment_id: Unique identifier for the KX environment.
        :param pulumi.Input[str] last_modified_timestamp: The last time that the dataview was updated in FinSpace. The value is determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        :param pulumi.Input[str] name: A unique identifier for the dataview.
               
               The following arguments are optional:
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['KxDataviewSegmentConfigurationArgs']]]] segment_configurations: The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags: Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] tags_all: Map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _KxDataviewState.__new__(_KxDataviewState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["auto_update"] = auto_update
        __props__.__dict__["availability_zone_id"] = availability_zone_id
        __props__.__dict__["az_mode"] = az_mode
        __props__.__dict__["changeset_id"] = changeset_id
        __props__.__dict__["created_timestamp"] = created_timestamp
        __props__.__dict__["database_name"] = database_name
        __props__.__dict__["description"] = description
        __props__.__dict__["environment_id"] = environment_id
        __props__.__dict__["last_modified_timestamp"] = last_modified_timestamp
        __props__.__dict__["name"] = name
        __props__.__dict__["segment_configurations"] = segment_configurations
        __props__.__dict__["status"] = status
        __props__.__dict__["tags"] = tags
        __props__.__dict__["tags_all"] = tags_all
        return KxDataview(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        Amazon Resource Name (ARN) identifier of the KX dataview.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="autoUpdate")
    def auto_update(self) -> pulumi.Output[bool]:
        """
        The option to specify whether you want to apply all the future additions and corrections automatically to the dataview, when you ingest new changesets. The default value is false.
        """
        return pulumi.get(self, "auto_update")

    @property
    @pulumi.getter(name="availabilityZoneId")
    def availability_zone_id(self) -> pulumi.Output[Optional[str]]:
        """
        The identifier of the availability zones. If attaching a volume, the volume must be in the same availability zone as the dataview that you are attaching to.
        """
        return pulumi.get(self, "availability_zone_id")

    @property
    @pulumi.getter(name="azMode")
    def az_mode(self) -> pulumi.Output[str]:
        """
        The number of availability zones you want to assign per cluster. This can be one of the following:
        """
        return pulumi.get(self, "az_mode")

    @property
    @pulumi.getter(name="changesetId")
    def changeset_id(self) -> pulumi.Output[Optional[str]]:
        """
        A unique identifier of the changeset of the database that you want to use to ingest data.
        """
        return pulumi.get(self, "changeset_id")

    @property
    @pulumi.getter(name="createdTimestamp")
    def created_timestamp(self) -> pulumi.Output[str]:
        """
        Timestamp at which the dataview was created in FinSpace. Value determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        """
        return pulumi.get(self, "created_timestamp")

    @property
    @pulumi.getter(name="databaseName")
    def database_name(self) -> pulumi.Output[str]:
        """
        The name of the database where you want to create a dataview.
        """
        return pulumi.get(self, "database_name")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A description for the dataview.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="environmentId")
    def environment_id(self) -> pulumi.Output[str]:
        """
        Unique identifier for the KX environment.
        """
        return pulumi.get(self, "environment_id")

    @property
    @pulumi.getter(name="lastModifiedTimestamp")
    def last_modified_timestamp(self) -> pulumi.Output[str]:
        """
        The last time that the dataview was updated in FinSpace. The value is determined as epoch time in milliseconds. For example, the value for Monday, November 1, 2021 12:00:00 PM UTC is specified as 1635768000000.
        """
        return pulumi.get(self, "last_modified_timestamp")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        A unique identifier for the dataview.

        The following arguments are optional:
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="segmentConfigurations")
    def segment_configurations(self) -> pulumi.Output[Optional[Sequence['outputs.KxDataviewSegmentConfiguration']]]:
        """
        The configuration that contains the database path of the data that you want to place on each selected volume. Each segment must have a unique database path for each volume. If you do not explicitly specify any database path for a volume, they are accessible from the cluster through the default S3/object store segment. See segment_configurations below.
        """
        return pulumi.get(self, "segment_configurations")

    @property
    @pulumi.getter
    def status(self) -> pulumi.Output[str]:
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def tags(self) -> pulumi.Output[Optional[Mapping[str, str]]]:
        """
        Key-value mapping of resource tags. If configured with a provider `default_tags` configuration block present, tags with matching keys will overwrite those defined at the provider-level.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter(name="tagsAll")
    def tags_all(self) -> pulumi.Output[Mapping[str, str]]:
        """
        Map of tags assigned to the resource, including those inherited from the provider `default_tags` configuration block.
        """
        warnings.warn("""Please use `tags` instead.""", DeprecationWarning)
        pulumi.log.warn("""tags_all is deprecated: Please use `tags` instead.""")

        return pulumi.get(self, "tags_all")

