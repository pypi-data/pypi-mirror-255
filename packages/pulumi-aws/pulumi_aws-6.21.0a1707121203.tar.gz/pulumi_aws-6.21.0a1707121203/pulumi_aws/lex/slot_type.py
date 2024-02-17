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

__all__ = ['SlotTypeArgs', 'SlotType']

@pulumi.input_type
class SlotTypeArgs:
    def __init__(__self__, *,
                 enumeration_values: pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]],
                 create_version: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 value_selection_strategy: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a SlotType resource.
        :param pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]] enumeration_values: A list of EnumerationValue objects that defines the values that
               the slot type can take. Each value can have a list of synonyms, which are additional values that help
               train the machine learning model about the values that it resolves for a slot. Attributes are
               documented under enumeration_value.
        :param pulumi.Input[bool] create_version: Determines if a new slot type version is created when the initial resource is created and on each
               update. Defaults to `false`.
        :param pulumi.Input[str] description: A description of the slot type. Must be less than or equal to 200 characters in length.
        :param pulumi.Input[str] name: The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        :param pulumi.Input[str] value_selection_strategy: Determines the slot resolution strategy that Amazon Lex
               uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
               value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
               if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        """
        pulumi.set(__self__, "enumeration_values", enumeration_values)
        if create_version is not None:
            pulumi.set(__self__, "create_version", create_version)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if value_selection_strategy is not None:
            pulumi.set(__self__, "value_selection_strategy", value_selection_strategy)

    @property
    @pulumi.getter(name="enumerationValues")
    def enumeration_values(self) -> pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]]:
        """
        A list of EnumerationValue objects that defines the values that
        the slot type can take. Each value can have a list of synonyms, which are additional values that help
        train the machine learning model about the values that it resolves for a slot. Attributes are
        documented under enumeration_value.
        """
        return pulumi.get(self, "enumeration_values")

    @enumeration_values.setter
    def enumeration_values(self, value: pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]]):
        pulumi.set(self, "enumeration_values", value)

    @property
    @pulumi.getter(name="createVersion")
    def create_version(self) -> Optional[pulumi.Input[bool]]:
        """
        Determines if a new slot type version is created when the initial resource is created and on each
        update. Defaults to `false`.
        """
        return pulumi.get(self, "create_version")

    @create_version.setter
    def create_version(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "create_version", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description of the slot type. Must be less than or equal to 200 characters in length.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="valueSelectionStrategy")
    def value_selection_strategy(self) -> Optional[pulumi.Input[str]]:
        """
        Determines the slot resolution strategy that Amazon Lex
        uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
        value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
        if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        """
        return pulumi.get(self, "value_selection_strategy")

    @value_selection_strategy.setter
    def value_selection_strategy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value_selection_strategy", value)


@pulumi.input_type
class _SlotTypeState:
    def __init__(__self__, *,
                 checksum: Optional[pulumi.Input[str]] = None,
                 create_version: Optional[pulumi.Input[bool]] = None,
                 created_date: Optional[pulumi.Input[str]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enumeration_values: Optional[pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]]] = None,
                 last_updated_date: Optional[pulumi.Input[str]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 value_selection_strategy: Optional[pulumi.Input[str]] = None,
                 version: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering SlotType resources.
        :param pulumi.Input[str] checksum: Checksum identifying the version of the slot type that was created. The checksum is
               not included as an argument because the resource will add it automatically when updating the slot type.
        :param pulumi.Input[bool] create_version: Determines if a new slot type version is created when the initial resource is created and on each
               update. Defaults to `false`.
        :param pulumi.Input[str] created_date: The date when the slot type version was created.
        :param pulumi.Input[str] description: A description of the slot type. Must be less than or equal to 200 characters in length.
        :param pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]] enumeration_values: A list of EnumerationValue objects that defines the values that
               the slot type can take. Each value can have a list of synonyms, which are additional values that help
               train the machine learning model about the values that it resolves for a slot. Attributes are
               documented under enumeration_value.
        :param pulumi.Input[str] last_updated_date: The date when the `$LATEST` version of this slot type was updated.
        :param pulumi.Input[str] name: The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        :param pulumi.Input[str] value_selection_strategy: Determines the slot resolution strategy that Amazon Lex
               uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
               value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
               if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        :param pulumi.Input[str] version: The version of the slot type.
        """
        if checksum is not None:
            pulumi.set(__self__, "checksum", checksum)
        if create_version is not None:
            pulumi.set(__self__, "create_version", create_version)
        if created_date is not None:
            pulumi.set(__self__, "created_date", created_date)
        if description is not None:
            pulumi.set(__self__, "description", description)
        if enumeration_values is not None:
            pulumi.set(__self__, "enumeration_values", enumeration_values)
        if last_updated_date is not None:
            pulumi.set(__self__, "last_updated_date", last_updated_date)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if value_selection_strategy is not None:
            pulumi.set(__self__, "value_selection_strategy", value_selection_strategy)
        if version is not None:
            pulumi.set(__self__, "version", version)

    @property
    @pulumi.getter
    def checksum(self) -> Optional[pulumi.Input[str]]:
        """
        Checksum identifying the version of the slot type that was created. The checksum is
        not included as an argument because the resource will add it automatically when updating the slot type.
        """
        return pulumi.get(self, "checksum")

    @checksum.setter
    def checksum(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "checksum", value)

    @property
    @pulumi.getter(name="createVersion")
    def create_version(self) -> Optional[pulumi.Input[bool]]:
        """
        Determines if a new slot type version is created when the initial resource is created and on each
        update. Defaults to `false`.
        """
        return pulumi.get(self, "create_version")

    @create_version.setter
    def create_version(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "create_version", value)

    @property
    @pulumi.getter(name="createdDate")
    def created_date(self) -> Optional[pulumi.Input[str]]:
        """
        The date when the slot type version was created.
        """
        return pulumi.get(self, "created_date")

    @created_date.setter
    def created_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "created_date", value)

    @property
    @pulumi.getter
    def description(self) -> Optional[pulumi.Input[str]]:
        """
        A description of the slot type. Must be less than or equal to 200 characters in length.
        """
        return pulumi.get(self, "description")

    @description.setter
    def description(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "description", value)

    @property
    @pulumi.getter(name="enumerationValues")
    def enumeration_values(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]]]:
        """
        A list of EnumerationValue objects that defines the values that
        the slot type can take. Each value can have a list of synonyms, which are additional values that help
        train the machine learning model about the values that it resolves for a slot. Attributes are
        documented under enumeration_value.
        """
        return pulumi.get(self, "enumeration_values")

    @enumeration_values.setter
    def enumeration_values(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['SlotTypeEnumerationValueArgs']]]]):
        pulumi.set(self, "enumeration_values", value)

    @property
    @pulumi.getter(name="lastUpdatedDate")
    def last_updated_date(self) -> Optional[pulumi.Input[str]]:
        """
        The date when the `$LATEST` version of this slot type was updated.
        """
        return pulumi.get(self, "last_updated_date")

    @last_updated_date.setter
    def last_updated_date(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "last_updated_date", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="valueSelectionStrategy")
    def value_selection_strategy(self) -> Optional[pulumi.Input[str]]:
        """
        Determines the slot resolution strategy that Amazon Lex
        uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
        value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
        if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        """
        return pulumi.get(self, "value_selection_strategy")

    @value_selection_strategy.setter
    def value_selection_strategy(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "value_selection_strategy", value)

    @property
    @pulumi.getter
    def version(self) -> Optional[pulumi.Input[str]]:
        """
        The version of the slot type.
        """
        return pulumi.get(self, "version")

    @version.setter
    def version(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "version", value)


class SlotType(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 create_version: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enumeration_values: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['SlotTypeEnumerationValueArgs']]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 value_selection_strategy: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Provides an Amazon Lex Slot Type resource. For more information see
        [Amazon Lex: How It Works](https://docs.aws.amazon.com/lex/latest/dg/how-it-works.html)

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        flower_types = aws.lex.SlotType("flowerTypes",
            create_version=True,
            description="Types of flowers to order",
            enumeration_values=[
                aws.lex.SlotTypeEnumerationValueArgs(
                    synonyms=[
                        "Lirium",
                        "Martagon",
                    ],
                    value="lilies",
                ),
                aws.lex.SlotTypeEnumerationValueArgs(
                    synonyms=[
                        "Eduardoregelia",
                        "Podonix",
                    ],
                    value="tulips",
                ),
            ],
            name="FlowerTypes",
            value_selection_strategy="ORIGINAL_VALUE")
        ```

        ## Import

        Using `pulumi import`, import slot types using their name. For example:

        ```sh
         $ pulumi import aws:lex/slotType:SlotType flower_types FlowerTypes
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[bool] create_version: Determines if a new slot type version is created when the initial resource is created and on each
               update. Defaults to `false`.
        :param pulumi.Input[str] description: A description of the slot type. Must be less than or equal to 200 characters in length.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['SlotTypeEnumerationValueArgs']]]] enumeration_values: A list of EnumerationValue objects that defines the values that
               the slot type can take. Each value can have a list of synonyms, which are additional values that help
               train the machine learning model about the values that it resolves for a slot. Attributes are
               documented under enumeration_value.
        :param pulumi.Input[str] name: The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        :param pulumi.Input[str] value_selection_strategy: Determines the slot resolution strategy that Amazon Lex
               uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
               value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
               if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: SlotTypeArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an Amazon Lex Slot Type resource. For more information see
        [Amazon Lex: How It Works](https://docs.aws.amazon.com/lex/latest/dg/how-it-works.html)

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        flower_types = aws.lex.SlotType("flowerTypes",
            create_version=True,
            description="Types of flowers to order",
            enumeration_values=[
                aws.lex.SlotTypeEnumerationValueArgs(
                    synonyms=[
                        "Lirium",
                        "Martagon",
                    ],
                    value="lilies",
                ),
                aws.lex.SlotTypeEnumerationValueArgs(
                    synonyms=[
                        "Eduardoregelia",
                        "Podonix",
                    ],
                    value="tulips",
                ),
            ],
            name="FlowerTypes",
            value_selection_strategy="ORIGINAL_VALUE")
        ```

        ## Import

        Using `pulumi import`, import slot types using their name. For example:

        ```sh
         $ pulumi import aws:lex/slotType:SlotType flower_types FlowerTypes
        ```

        :param str resource_name: The name of the resource.
        :param SlotTypeArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(SlotTypeArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 create_version: Optional[pulumi.Input[bool]] = None,
                 description: Optional[pulumi.Input[str]] = None,
                 enumeration_values: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['SlotTypeEnumerationValueArgs']]]]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 value_selection_strategy: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = SlotTypeArgs.__new__(SlotTypeArgs)

            __props__.__dict__["create_version"] = create_version
            __props__.__dict__["description"] = description
            if enumeration_values is None and not opts.urn:
                raise TypeError("Missing required property 'enumeration_values'")
            __props__.__dict__["enumeration_values"] = enumeration_values
            __props__.__dict__["name"] = name
            __props__.__dict__["value_selection_strategy"] = value_selection_strategy
            __props__.__dict__["checksum"] = None
            __props__.__dict__["created_date"] = None
            __props__.__dict__["last_updated_date"] = None
            __props__.__dict__["version"] = None
        super(SlotType, __self__).__init__(
            'aws:lex/slotType:SlotType',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            checksum: Optional[pulumi.Input[str]] = None,
            create_version: Optional[pulumi.Input[bool]] = None,
            created_date: Optional[pulumi.Input[str]] = None,
            description: Optional[pulumi.Input[str]] = None,
            enumeration_values: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['SlotTypeEnumerationValueArgs']]]]] = None,
            last_updated_date: Optional[pulumi.Input[str]] = None,
            name: Optional[pulumi.Input[str]] = None,
            value_selection_strategy: Optional[pulumi.Input[str]] = None,
            version: Optional[pulumi.Input[str]] = None) -> 'SlotType':
        """
        Get an existing SlotType resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] checksum: Checksum identifying the version of the slot type that was created. The checksum is
               not included as an argument because the resource will add it automatically when updating the slot type.
        :param pulumi.Input[bool] create_version: Determines if a new slot type version is created when the initial resource is created and on each
               update. Defaults to `false`.
        :param pulumi.Input[str] created_date: The date when the slot type version was created.
        :param pulumi.Input[str] description: A description of the slot type. Must be less than or equal to 200 characters in length.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['SlotTypeEnumerationValueArgs']]]] enumeration_values: A list of EnumerationValue objects that defines the values that
               the slot type can take. Each value can have a list of synonyms, which are additional values that help
               train the machine learning model about the values that it resolves for a slot. Attributes are
               documented under enumeration_value.
        :param pulumi.Input[str] last_updated_date: The date when the `$LATEST` version of this slot type was updated.
        :param pulumi.Input[str] name: The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        :param pulumi.Input[str] value_selection_strategy: Determines the slot resolution strategy that Amazon Lex
               uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
               value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
               if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        :param pulumi.Input[str] version: The version of the slot type.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _SlotTypeState.__new__(_SlotTypeState)

        __props__.__dict__["checksum"] = checksum
        __props__.__dict__["create_version"] = create_version
        __props__.__dict__["created_date"] = created_date
        __props__.__dict__["description"] = description
        __props__.__dict__["enumeration_values"] = enumeration_values
        __props__.__dict__["last_updated_date"] = last_updated_date
        __props__.__dict__["name"] = name
        __props__.__dict__["value_selection_strategy"] = value_selection_strategy
        __props__.__dict__["version"] = version
        return SlotType(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def checksum(self) -> pulumi.Output[str]:
        """
        Checksum identifying the version of the slot type that was created. The checksum is
        not included as an argument because the resource will add it automatically when updating the slot type.
        """
        return pulumi.get(self, "checksum")

    @property
    @pulumi.getter(name="createVersion")
    def create_version(self) -> pulumi.Output[Optional[bool]]:
        """
        Determines if a new slot type version is created when the initial resource is created and on each
        update. Defaults to `false`.
        """
        return pulumi.get(self, "create_version")

    @property
    @pulumi.getter(name="createdDate")
    def created_date(self) -> pulumi.Output[str]:
        """
        The date when the slot type version was created.
        """
        return pulumi.get(self, "created_date")

    @property
    @pulumi.getter
    def description(self) -> pulumi.Output[Optional[str]]:
        """
        A description of the slot type. Must be less than or equal to 200 characters in length.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter(name="enumerationValues")
    def enumeration_values(self) -> pulumi.Output[Sequence['outputs.SlotTypeEnumerationValue']]:
        """
        A list of EnumerationValue objects that defines the values that
        the slot type can take. Each value can have a list of synonyms, which are additional values that help
        train the machine learning model about the values that it resolves for a slot. Attributes are
        documented under enumeration_value.
        """
        return pulumi.get(self, "enumeration_values")

    @property
    @pulumi.getter(name="lastUpdatedDate")
    def last_updated_date(self) -> pulumi.Output[str]:
        """
        The date when the `$LATEST` version of this slot type was updated.
        """
        return pulumi.get(self, "last_updated_date")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the slot type. The name is not case sensitive. Must be less than or equal to 100 characters in length.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="valueSelectionStrategy")
    def value_selection_strategy(self) -> pulumi.Output[Optional[str]]:
        """
        Determines the slot resolution strategy that Amazon Lex
        uses to return slot type values. `ORIGINAL_VALUE` returns the value entered by the user if the user
        value is similar to the slot value. `TOP_RESOLUTION` returns the first value in the resolution list
        if there is a resolution list for the slot, otherwise null is returned. Defaults to `ORIGINAL_VALUE`.
        """
        return pulumi.get(self, "value_selection_strategy")

    @property
    @pulumi.getter
    def version(self) -> pulumi.Output[str]:
        """
        The version of the slot type.
        """
        return pulumi.get(self, "version")

