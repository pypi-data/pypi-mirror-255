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

__all__ = ['DomainArgs', 'Domain']

@pulumi.input_type
class DomainArgs:
    def __init__(__self__, *,
                 endpoint_options: Optional[pulumi.Input['DomainEndpointOptionsArgs']] = None,
                 index_fields: Optional[pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]]] = None,
                 multi_az: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 scaling_parameters: Optional[pulumi.Input['DomainScalingParametersArgs']] = None):
        """
        The set of arguments for constructing a Domain resource.
        :param pulumi.Input['DomainEndpointOptionsArgs'] endpoint_options: Domain endpoint options. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]] index_fields: The index fields for documents added to the domain. Documented below.
        :param pulumi.Input[bool] multi_az: Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        :param pulumi.Input[str] name: The name of the CloudSearch domain.
        :param pulumi.Input['DomainScalingParametersArgs'] scaling_parameters: Domain scaling parameters. Documented below.
        """
        if endpoint_options is not None:
            pulumi.set(__self__, "endpoint_options", endpoint_options)
        if index_fields is not None:
            pulumi.set(__self__, "index_fields", index_fields)
        if multi_az is not None:
            pulumi.set(__self__, "multi_az", multi_az)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if scaling_parameters is not None:
            pulumi.set(__self__, "scaling_parameters", scaling_parameters)

    @property
    @pulumi.getter(name="endpointOptions")
    def endpoint_options(self) -> Optional[pulumi.Input['DomainEndpointOptionsArgs']]:
        """
        Domain endpoint options. Documented below.
        """
        return pulumi.get(self, "endpoint_options")

    @endpoint_options.setter
    def endpoint_options(self, value: Optional[pulumi.Input['DomainEndpointOptionsArgs']]):
        pulumi.set(self, "endpoint_options", value)

    @property
    @pulumi.getter(name="indexFields")
    def index_fields(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]]]:
        """
        The index fields for documents added to the domain. Documented below.
        """
        return pulumi.get(self, "index_fields")

    @index_fields.setter
    def index_fields(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]]]):
        pulumi.set(self, "index_fields", value)

    @property
    @pulumi.getter(name="multiAz")
    def multi_az(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        """
        return pulumi.get(self, "multi_az")

    @multi_az.setter
    def multi_az(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "multi_az", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the CloudSearch domain.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="scalingParameters")
    def scaling_parameters(self) -> Optional[pulumi.Input['DomainScalingParametersArgs']]:
        """
        Domain scaling parameters. Documented below.
        """
        return pulumi.get(self, "scaling_parameters")

    @scaling_parameters.setter
    def scaling_parameters(self, value: Optional[pulumi.Input['DomainScalingParametersArgs']]):
        pulumi.set(self, "scaling_parameters", value)


@pulumi.input_type
class _DomainState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 document_service_endpoint: Optional[pulumi.Input[str]] = None,
                 domain_id: Optional[pulumi.Input[str]] = None,
                 endpoint_options: Optional[pulumi.Input['DomainEndpointOptionsArgs']] = None,
                 index_fields: Optional[pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]]] = None,
                 multi_az: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 scaling_parameters: Optional[pulumi.Input['DomainScalingParametersArgs']] = None,
                 search_service_endpoint: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering Domain resources.
        :param pulumi.Input[str] arn: The domain's ARN.
        :param pulumi.Input[str] document_service_endpoint: The service endpoint for updating documents in a search domain.
        :param pulumi.Input[str] domain_id: An internally generated unique identifier for the domain.
        :param pulumi.Input['DomainEndpointOptionsArgs'] endpoint_options: Domain endpoint options. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]] index_fields: The index fields for documents added to the domain. Documented below.
        :param pulumi.Input[bool] multi_az: Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        :param pulumi.Input[str] name: The name of the CloudSearch domain.
        :param pulumi.Input['DomainScalingParametersArgs'] scaling_parameters: Domain scaling parameters. Documented below.
        :param pulumi.Input[str] search_service_endpoint: The service endpoint for requesting search results from a search domain.
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if document_service_endpoint is not None:
            pulumi.set(__self__, "document_service_endpoint", document_service_endpoint)
        if domain_id is not None:
            pulumi.set(__self__, "domain_id", domain_id)
        if endpoint_options is not None:
            pulumi.set(__self__, "endpoint_options", endpoint_options)
        if index_fields is not None:
            pulumi.set(__self__, "index_fields", index_fields)
        if multi_az is not None:
            pulumi.set(__self__, "multi_az", multi_az)
        if name is not None:
            pulumi.set(__self__, "name", name)
        if scaling_parameters is not None:
            pulumi.set(__self__, "scaling_parameters", scaling_parameters)
        if search_service_endpoint is not None:
            pulumi.set(__self__, "search_service_endpoint", search_service_endpoint)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        The domain's ARN.
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="documentServiceEndpoint")
    def document_service_endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        The service endpoint for updating documents in a search domain.
        """
        return pulumi.get(self, "document_service_endpoint")

    @document_service_endpoint.setter
    def document_service_endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "document_service_endpoint", value)

    @property
    @pulumi.getter(name="domainId")
    def domain_id(self) -> Optional[pulumi.Input[str]]:
        """
        An internally generated unique identifier for the domain.
        """
        return pulumi.get(self, "domain_id")

    @domain_id.setter
    def domain_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "domain_id", value)

    @property
    @pulumi.getter(name="endpointOptions")
    def endpoint_options(self) -> Optional[pulumi.Input['DomainEndpointOptionsArgs']]:
        """
        Domain endpoint options. Documented below.
        """
        return pulumi.get(self, "endpoint_options")

    @endpoint_options.setter
    def endpoint_options(self, value: Optional[pulumi.Input['DomainEndpointOptionsArgs']]):
        pulumi.set(self, "endpoint_options", value)

    @property
    @pulumi.getter(name="indexFields")
    def index_fields(self) -> Optional[pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]]]:
        """
        The index fields for documents added to the domain. Documented below.
        """
        return pulumi.get(self, "index_fields")

    @index_fields.setter
    def index_fields(self, value: Optional[pulumi.Input[Sequence[pulumi.Input['DomainIndexFieldArgs']]]]):
        pulumi.set(self, "index_fields", value)

    @property
    @pulumi.getter(name="multiAz")
    def multi_az(self) -> Optional[pulumi.Input[bool]]:
        """
        Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        """
        return pulumi.get(self, "multi_az")

    @multi_az.setter
    def multi_az(self, value: Optional[pulumi.Input[bool]]):
        pulumi.set(self, "multi_az", value)

    @property
    @pulumi.getter
    def name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the CloudSearch domain.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="scalingParameters")
    def scaling_parameters(self) -> Optional[pulumi.Input['DomainScalingParametersArgs']]:
        """
        Domain scaling parameters. Documented below.
        """
        return pulumi.get(self, "scaling_parameters")

    @scaling_parameters.setter
    def scaling_parameters(self, value: Optional[pulumi.Input['DomainScalingParametersArgs']]):
        pulumi.set(self, "scaling_parameters", value)

    @property
    @pulumi.getter(name="searchServiceEndpoint")
    def search_service_endpoint(self) -> Optional[pulumi.Input[str]]:
        """
        The service endpoint for requesting search results from a search domain.
        """
        return pulumi.get(self, "search_service_endpoint")

    @search_service_endpoint.setter
    def search_service_endpoint(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "search_service_endpoint", value)


class Domain(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_options: Optional[pulumi.Input[pulumi.InputType['DomainEndpointOptionsArgs']]] = None,
                 index_fields: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DomainIndexFieldArgs']]]]] = None,
                 multi_az: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 scaling_parameters: Optional[pulumi.Input[pulumi.InputType['DomainScalingParametersArgs']]] = None,
                 __props__=None):
        """
        Provides an CloudSearch domain resource.

        The provider waits for the domain to become `Active` when applying a configuration.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.cloudsearch.Domain("example",
            index_fields=[
                aws.cloudsearch.DomainIndexFieldArgs(
                    analysis_scheme="_en_default_",
                    highlight=False,
                    name="headline",
                    return_=True,
                    search=True,
                    sort=True,
                    type="text",
                ),
                aws.cloudsearch.DomainIndexFieldArgs(
                    facet=True,
                    name="price",
                    return_=True,
                    search=True,
                    sort=True,
                    source_fields="headline",
                    type="double",
                ),
            ],
            scaling_parameters=aws.cloudsearch.DomainScalingParametersArgs(
                desired_instance_type="search.medium",
            ))
        ```

        ## Import

        Using `pulumi import`, import CloudSearch Domains using the `name`. For example:

        ```sh
         $ pulumi import aws:cloudsearch/domain:Domain example example-domain
        ```

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[pulumi.InputType['DomainEndpointOptionsArgs']] endpoint_options: Domain endpoint options. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DomainIndexFieldArgs']]]] index_fields: The index fields for documents added to the domain. Documented below.
        :param pulumi.Input[bool] multi_az: Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        :param pulumi.Input[str] name: The name of the CloudSearch domain.
        :param pulumi.Input[pulumi.InputType['DomainScalingParametersArgs']] scaling_parameters: Domain scaling parameters. Documented below.
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: Optional[DomainArgs] = None,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Provides an CloudSearch domain resource.

        The provider waits for the domain to become `Active` when applying a configuration.

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.cloudsearch.Domain("example",
            index_fields=[
                aws.cloudsearch.DomainIndexFieldArgs(
                    analysis_scheme="_en_default_",
                    highlight=False,
                    name="headline",
                    return_=True,
                    search=True,
                    sort=True,
                    type="text",
                ),
                aws.cloudsearch.DomainIndexFieldArgs(
                    facet=True,
                    name="price",
                    return_=True,
                    search=True,
                    sort=True,
                    source_fields="headline",
                    type="double",
                ),
            ],
            scaling_parameters=aws.cloudsearch.DomainScalingParametersArgs(
                desired_instance_type="search.medium",
            ))
        ```

        ## Import

        Using `pulumi import`, import CloudSearch Domains using the `name`. For example:

        ```sh
         $ pulumi import aws:cloudsearch/domain:Domain example example-domain
        ```

        :param str resource_name: The name of the resource.
        :param DomainArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(DomainArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 endpoint_options: Optional[pulumi.Input[pulumi.InputType['DomainEndpointOptionsArgs']]] = None,
                 index_fields: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DomainIndexFieldArgs']]]]] = None,
                 multi_az: Optional[pulumi.Input[bool]] = None,
                 name: Optional[pulumi.Input[str]] = None,
                 scaling_parameters: Optional[pulumi.Input[pulumi.InputType['DomainScalingParametersArgs']]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = DomainArgs.__new__(DomainArgs)

            __props__.__dict__["endpoint_options"] = endpoint_options
            __props__.__dict__["index_fields"] = index_fields
            __props__.__dict__["multi_az"] = multi_az
            __props__.__dict__["name"] = name
            __props__.__dict__["scaling_parameters"] = scaling_parameters
            __props__.__dict__["arn"] = None
            __props__.__dict__["document_service_endpoint"] = None
            __props__.__dict__["domain_id"] = None
            __props__.__dict__["search_service_endpoint"] = None
        super(Domain, __self__).__init__(
            'aws:cloudsearch/domain:Domain',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            document_service_endpoint: Optional[pulumi.Input[str]] = None,
            domain_id: Optional[pulumi.Input[str]] = None,
            endpoint_options: Optional[pulumi.Input[pulumi.InputType['DomainEndpointOptionsArgs']]] = None,
            index_fields: Optional[pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DomainIndexFieldArgs']]]]] = None,
            multi_az: Optional[pulumi.Input[bool]] = None,
            name: Optional[pulumi.Input[str]] = None,
            scaling_parameters: Optional[pulumi.Input[pulumi.InputType['DomainScalingParametersArgs']]] = None,
            search_service_endpoint: Optional[pulumi.Input[str]] = None) -> 'Domain':
        """
        Get an existing Domain resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: The domain's ARN.
        :param pulumi.Input[str] document_service_endpoint: The service endpoint for updating documents in a search domain.
        :param pulumi.Input[str] domain_id: An internally generated unique identifier for the domain.
        :param pulumi.Input[pulumi.InputType['DomainEndpointOptionsArgs']] endpoint_options: Domain endpoint options. Documented below.
        :param pulumi.Input[Sequence[pulumi.Input[pulumi.InputType['DomainIndexFieldArgs']]]] index_fields: The index fields for documents added to the domain. Documented below.
        :param pulumi.Input[bool] multi_az: Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        :param pulumi.Input[str] name: The name of the CloudSearch domain.
        :param pulumi.Input[pulumi.InputType['DomainScalingParametersArgs']] scaling_parameters: Domain scaling parameters. Documented below.
        :param pulumi.Input[str] search_service_endpoint: The service endpoint for requesting search results from a search domain.
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _DomainState.__new__(_DomainState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["document_service_endpoint"] = document_service_endpoint
        __props__.__dict__["domain_id"] = domain_id
        __props__.__dict__["endpoint_options"] = endpoint_options
        __props__.__dict__["index_fields"] = index_fields
        __props__.__dict__["multi_az"] = multi_az
        __props__.__dict__["name"] = name
        __props__.__dict__["scaling_parameters"] = scaling_parameters
        __props__.__dict__["search_service_endpoint"] = search_service_endpoint
        return Domain(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        The domain's ARN.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="documentServiceEndpoint")
    def document_service_endpoint(self) -> pulumi.Output[str]:
        """
        The service endpoint for updating documents in a search domain.
        """
        return pulumi.get(self, "document_service_endpoint")

    @property
    @pulumi.getter(name="domainId")
    def domain_id(self) -> pulumi.Output[str]:
        """
        An internally generated unique identifier for the domain.
        """
        return pulumi.get(self, "domain_id")

    @property
    @pulumi.getter(name="endpointOptions")
    def endpoint_options(self) -> pulumi.Output['outputs.DomainEndpointOptions']:
        """
        Domain endpoint options. Documented below.
        """
        return pulumi.get(self, "endpoint_options")

    @property
    @pulumi.getter(name="indexFields")
    def index_fields(self) -> pulumi.Output[Optional[Sequence['outputs.DomainIndexField']]]:
        """
        The index fields for documents added to the domain. Documented below.
        """
        return pulumi.get(self, "index_fields")

    @property
    @pulumi.getter(name="multiAz")
    def multi_az(self) -> pulumi.Output[bool]:
        """
        Whether or not to maintain extra instances for the domain in a second Availability Zone to ensure high availability.
        """
        return pulumi.get(self, "multi_az")

    @property
    @pulumi.getter
    def name(self) -> pulumi.Output[str]:
        """
        The name of the CloudSearch domain.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="scalingParameters")
    def scaling_parameters(self) -> pulumi.Output['outputs.DomainScalingParameters']:
        """
        Domain scaling parameters. Documented below.
        """
        return pulumi.get(self, "scaling_parameters")

    @property
    @pulumi.getter(name="searchServiceEndpoint")
    def search_service_endpoint(self) -> pulumi.Output[str]:
        """
        The service endpoint for requesting search results from a search domain.
        """
        return pulumi.get(self, "search_service_endpoint")

