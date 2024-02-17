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
    'GetSigningProfileResult',
    'AwaitableGetSigningProfileResult',
    'get_signing_profile',
    'get_signing_profile_output',
]

@pulumi.output_type
class GetSigningProfileResult:
    """
    A collection of values returned by getSigningProfile.
    """
    def __init__(__self__, arn=None, id=None, name=None, platform_display_name=None, platform_id=None, revocation_records=None, signature_validity_periods=None, status=None, tags=None, version=None, version_arn=None):
        if arn and not isinstance(arn, str):
            raise TypeError("Expected argument 'arn' to be a str")
        pulumi.set(__self__, "arn", arn)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if name and not isinstance(name, str):
            raise TypeError("Expected argument 'name' to be a str")
        pulumi.set(__self__, "name", name)
        if platform_display_name and not isinstance(platform_display_name, str):
            raise TypeError("Expected argument 'platform_display_name' to be a str")
        pulumi.set(__self__, "platform_display_name", platform_display_name)
        if platform_id and not isinstance(platform_id, str):
            raise TypeError("Expected argument 'platform_id' to be a str")
        pulumi.set(__self__, "platform_id", platform_id)
        if revocation_records and not isinstance(revocation_records, list):
            raise TypeError("Expected argument 'revocation_records' to be a list")
        pulumi.set(__self__, "revocation_records", revocation_records)
        if signature_validity_periods and not isinstance(signature_validity_periods, list):
            raise TypeError("Expected argument 'signature_validity_periods' to be a list")
        pulumi.set(__self__, "signature_validity_periods", signature_validity_periods)
        if status and not isinstance(status, str):
            raise TypeError("Expected argument 'status' to be a str")
        pulumi.set(__self__, "status", status)
        if tags and not isinstance(tags, dict):
            raise TypeError("Expected argument 'tags' to be a dict")
        pulumi.set(__self__, "tags", tags)
        if version and not isinstance(version, str):
            raise TypeError("Expected argument 'version' to be a str")
        pulumi.set(__self__, "version", version)
        if version_arn and not isinstance(version_arn, str):
            raise TypeError("Expected argument 'version_arn' to be a str")
        pulumi.set(__self__, "version_arn", version_arn)

    @property
    @pulumi.getter
    def arn(self) -> str:
        """
        ARN for the signing profile.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter
    def name(self) -> str:
        return pulumi.get(self, "name")

    @property
    @pulumi.getter(name="platformDisplayName")
    def platform_display_name(self) -> str:
        """
        A human-readable name for the signing platform associated with the signing profile.
        """
        return pulumi.get(self, "platform_display_name")

    @property
    @pulumi.getter(name="platformId")
    def platform_id(self) -> str:
        """
        ID of the platform that is used by the target signing profile.
        """
        return pulumi.get(self, "platform_id")

    @property
    @pulumi.getter(name="revocationRecords")
    def revocation_records(self) -> Sequence['outputs.GetSigningProfileRevocationRecordResult']:
        """
        Revocation information for a signing profile.
        """
        return pulumi.get(self, "revocation_records")

    @property
    @pulumi.getter(name="signatureValidityPeriods")
    def signature_validity_periods(self) -> Sequence['outputs.GetSigningProfileSignatureValidityPeriodResult']:
        """
        The validity period for a signing job.
        """
        return pulumi.get(self, "signature_validity_periods")

    @property
    @pulumi.getter
    def status(self) -> str:
        """
        Status of the target signing profile.
        """
        return pulumi.get(self, "status")

    @property
    @pulumi.getter
    def tags(self) -> Mapping[str, str]:
        """
        List of tags associated with the signing profile.
        """
        return pulumi.get(self, "tags")

    @property
    @pulumi.getter
    def version(self) -> str:
        """
        Current version of the signing profile.
        """
        return pulumi.get(self, "version")

    @property
    @pulumi.getter(name="versionArn")
    def version_arn(self) -> str:
        """
        Signing profile ARN, including the profile version.
        """
        return pulumi.get(self, "version_arn")


class AwaitableGetSigningProfileResult(GetSigningProfileResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetSigningProfileResult(
            arn=self.arn,
            id=self.id,
            name=self.name,
            platform_display_name=self.platform_display_name,
            platform_id=self.platform_id,
            revocation_records=self.revocation_records,
            signature_validity_periods=self.signature_validity_periods,
            status=self.status,
            tags=self.tags,
            version=self.version,
            version_arn=self.version_arn)


def get_signing_profile(name: Optional[str] = None,
                        tags: Optional[Mapping[str, str]] = None,
                        opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetSigningProfileResult:
    """
    Provides information about a Signer Signing Profile.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    production_signing_profile = aws.signer.get_signing_profile(name="prod_profile_DdW3Mk1foYL88fajut4mTVFGpuwfd4ACO6ANL0D1uIj7lrn8adK")
    ```


    :param str name: Name of the target signing profile.
    :param Mapping[str, str] tags: List of tags associated with the signing profile.
    """
    __args__ = dict()
    __args__['name'] = name
    __args__['tags'] = tags
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:signer/getSigningProfile:getSigningProfile', __args__, opts=opts, typ=GetSigningProfileResult).value

    return AwaitableGetSigningProfileResult(
        arn=pulumi.get(__ret__, 'arn'),
        id=pulumi.get(__ret__, 'id'),
        name=pulumi.get(__ret__, 'name'),
        platform_display_name=pulumi.get(__ret__, 'platform_display_name'),
        platform_id=pulumi.get(__ret__, 'platform_id'),
        revocation_records=pulumi.get(__ret__, 'revocation_records'),
        signature_validity_periods=pulumi.get(__ret__, 'signature_validity_periods'),
        status=pulumi.get(__ret__, 'status'),
        tags=pulumi.get(__ret__, 'tags'),
        version=pulumi.get(__ret__, 'version'),
        version_arn=pulumi.get(__ret__, 'version_arn'))


@_utilities.lift_output_func(get_signing_profile)
def get_signing_profile_output(name: Optional[pulumi.Input[str]] = None,
                               tags: Optional[pulumi.Input[Optional[Mapping[str, str]]]] = None,
                               opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetSigningProfileResult]:
    """
    Provides information about a Signer Signing Profile.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    production_signing_profile = aws.signer.get_signing_profile(name="prod_profile_DdW3Mk1foYL88fajut4mTVFGpuwfd4ACO6ANL0D1uIj7lrn8adK")
    ```


    :param str name: Name of the target signing profile.
    :param Mapping[str, str] tags: List of tags associated with the signing profile.
    """
    ...
