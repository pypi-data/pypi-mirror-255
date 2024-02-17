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

__all__ = [
    'GetConfigurationProfileResult',
    'AwaitableGetConfigurationProfileResult',
    'get_configuration_profile',
    'get_configuration_profile_output',
]

@pulumi.output_type
class GetConfigurationProfileResult:
    """
    A collection of values returned by getConfigurationProfile.
    """
    def __init__(__self__, application_id=None, arn=None, configuration_profile_id=None, description=None, id=None, kms_key_identifier=None, location_uri=None, name=None, retrieval_role_arn=None, tags=None, type=None, validators=None):
        if application_id and not isinstance(application_id, str):
            raise TypeError("Expected argument 'application_id' to be a str")
        pulumi.set(__self__, "application_id", application_id)
        if arn and not isinstance(arn, str):
            raise TypeError("Expected argument 'arn' to be a str")
        pulumi.set(__self__, "arn", arn)
        if configuration_profile_id and not isinstance(configuration_profile_id, str):
            raise TypeError("Expected argument 'configuration_profile_id' to be a str")
        pulumi.set(__self__, "configuration_profile_id", configuration_profile_id)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if kms_key_identifier and not isinstance(kms_key_identifier, str):
            raise TypeError("Expected argument 'kms_key_identifier' to be a str")
        pulumi.set(__self__, "kms_key_identifier", kms_key_identifier)
        if location_uri and not isinstance(location_uri, str):
            raise TypeError("Expected argument 'location_uri' to be a str")
        pulumi.set(__self__, "location_uri", location_uri)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if retrieval_role_arn and not isinstance(retrieval_role_arn, str):
            raise TypeError("Expected argument 'retrieval_role_arn' to be a str")
        pulumi.set(__self__, "retrieval_role_arn", retrieval_role_arn)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if type and not isinstance(type, str):
            raise TypeError("Expected argument 'type' to be a str")
        pulumi.set(__self__, "type", type)
        if validators and not isinstance(validators, list):
            raise TypeError("Expected argument 'validators' to be a list")
        pulumi.set(__self__, "validators", validators)

    @property
    @pulumi.getter(name="applicationId")
    def application_id(self) -> str:
        return pulumi.get(self, "application_id")

    @property
    @pulumi.getter
    def arn(self) -> str:
        """
        ARN of the Configuration Profile.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="configurationProfileId")
    def configuration_profile_id(self) -> str:
        return pulumi.get(self, "configuration_profile_id")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        Description of the Configuration Profile.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="kmsKeyIdentifier")
    def kms_key_identifier(self) -> str:
        return pulumi.get(self, "kms_key_identifier")

    @property
    @pulumi.getter(name="locationUri")
    def location_uri(self) -> str:
        """
        Location URI of the Configuration Profile.
        """
        return pulumi.get(self, "location_uri")

    @property
    @pulumi.getter
    def name(self) -> str:
        """
        Name of the Configuration Profile.
        """
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="retrievalRoleArn")
    def retrieval_role_arn(self) -> str:
        """
        ARN of an IAM role with permission to access the configuration at the specified location_uri.
        """
        return pulumi.get(self, "retrieval_role_arn")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        Map of tags for the resource.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter
    def type(self) -> str:
        """
        Type of validator. Valid values: JSON_SCHEMA and LAMBDA.
        """
        return pulumi.get(self, "type")

    @property
    @pulumi.getter
    def validators(self) -> Sequence['outputs.GetConfigurationProfileValidatorResult']:
        """
        Nested list of methods for validating the configuration.
        """
        return pulumi.get(self, "validators")


class AwaitableGetConfigurationProfileResult(GetConfigurationProfileResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetConfigurationProfileResult(
            application_id=self.application_id,
            arn=self.arn,
            configuration_profile_id=self.configuration_profile_id,
            description=self.description,
            id=self.id,
            kms_key_identifier=self.kms_key_identifier,
            location_uri=self.location_uri,
            name=self.name,
            retrieval_role_arn=self.retrieval_role_arn,
            tags=self.tags,
            type=self.type,
            validators=self.validators)


def get_configuration_profile(application_id: Optional[str] = None,
                              configuration_profile_id: Optional[str] = None,
                              tags: Optional[Mapping[str, str]] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetConfigurationProfileResult:
    """
    Provides access to an AppConfig Configuration Profile.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.appconfig.get_configuration_profile(application_id="b5d5gpj",
        configuration_profile_id="qrbb1c1")
    ```


    :param str application_id: ID of the AppConfig application to which this configuration profile belongs.
    :param str configuration_profile_id: ID of the Configuration Profile.
    :param Mapping[str, str] tags: Map of tags for the resource.
    """
    __args__ = dict()
    __args__['applicationId'] = application_id
    __args__['configurationProfileId'] = configuration_profile_id
    __args__['tags'] = tags
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:appconfig/getConfigurationProfile:getConfigurationProfile', __args__, opts=opts, typ=GetConfigurationProfileResult).value

    return AwaitableGetConfigurationProfileResult(
        application_id=pulumi.get(__ret__, 'application_id'),
        arn=pulumi.get(__ret__, 'arn'),
        configuration_profile_id=pulumi.get(__ret__, 'configuration_profile_id'),
        description=pulumi.get(__ret__, 'description'),
        id=pulumi.get(__ret__, 'id'),
        kms_key_identifier=pulumi.get(__ret__, 'kms_key_identifier'),
        location_uri=pulumi.get(__ret__, 'location_uri'),
        name=pulumi.get(__ret__, 'name'),
        retrieval_role_arn=pulumi.get(__ret__, 'retrieval_role_arn'),
        tags=pulumi.get(__ret__, 'tags'),
        type=pulumi.get(__ret__, 'type'),
        validators=pulumi.get(__ret__, 'validators'))


@_utilities.lift_output_func(get_configuration_profile)
def get_configuration_profile_output(application_id: Optional[pulumi.Input[str]] = None,
                                     configuration_profile_id: Optional[pulumi.Input[str]] = None,
                                     tags: Optional[pulumi.Input[Optional[Mapping[str, str]]]] = None,
                                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetConfigurationProfileResult]:
    """
    Provides access to an AppConfig Configuration Profile.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.appconfig.get_configuration_profile(application_id="b5d5gpj",
        configuration_profile_id="qrbb1c1")
    ```


    :param str application_id: ID of the AppConfig application to which this configuration profile belongs.
    :param str configuration_profile_id: ID of the Configuration Profile.
    :param Mapping[str, str] tags: Map of tags for the resource.
    """
    ...
