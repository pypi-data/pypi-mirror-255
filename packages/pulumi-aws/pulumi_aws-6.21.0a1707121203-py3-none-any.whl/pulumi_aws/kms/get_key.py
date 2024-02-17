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
    'GetKeyResult',
    'AwaitableGetKeyResult',
    'get_key',
    'get_key_output',
]

@pulumi.output_type
class GetKeyResult:
    """
    A collection of values returned by getKey.
    """
    def __init__(__self__, arn=None, aws_account_id=None, cloud_hsm_cluster_id=None, creation_date=None, custom_key_store_id=None, customer_master_key_spec=None, deletion_date=None, description=None, enabled=None, expiration_model=None, grant_tokens=None, id=None, key_id=None, key_manager=None, key_spec=None, key_state=None, key_usage=None, multi_region=None, multi_region_configurations=None, origin=None, pending_deletion_window_in_days=None, valid_to=None, xks_key_configurations=None):
        if arn and not isinstance(arn, str):
            raise TypeError("Expected argument 'arn' to be a str")
        pulumi.set(__self__, "arn", arn)
        if aws_account_id and not isinstance(aws_account_id, str):
            raise TypeError("Expected argument 'aws_account_id' to be a str")
        pulumi.set(__self__, "aws_account_id", aws_account_id)
        if cloud_hsm_cluster_id and not isinstance(cloud_hsm_cluster_id, str):
            raise TypeError("Expected argument 'cloud_hsm_cluster_id' to be a str")
        pulumi.set(__self__, "cloud_hsm_cluster_id", cloud_hsm_cluster_id)
        if creation_date and not isinstance(creation_date, str):
            raise TypeError("Expected argument 'creation_date' to be a str")
        pulumi.set(__self__, "creation_date", creation_date)
        if custom_key_store_id and not isinstance(custom_key_store_id, str):
            raise TypeError("Expected argument 'custom_key_store_id' to be a str")
        pulumi.set(__self__, "custom_key_store_id", custom_key_store_id)
        if customer_master_key_spec and not isinstance(customer_master_key_spec, str):
            raise TypeError("Expected argument 'customer_master_key_spec' to be a str")
        pulumi.set(__self__, "customer_master_key_spec", customer_master_key_spec)
        if deletion_date and not isinstance(deletion_date, str):
            raise TypeError("Expected argument 'deletion_date' to be a str")
        pulumi.set(__self__, "deletion_date", deletion_date)
        if description and not isinstance(description, str):
            raise TypeError("Expected argument 'description' to be a str")
        pulumi.set(__self__, "description", description)
        if enabled and not isinstance(enabled, bool):
            raise TypeError("Expected argument 'enabled' to be a bool")
        pulumi.set(__self__, "enabled", enabled)
        if expiration_model and not isinstance(expiration_model, str):
            raise TypeError("Expected argument 'expiration_model' to be a str")
        pulumi.set(__self__, "expiration_model", expiration_model)
        if grant_tokens and not isinstance(grant_tokens, list):
            raise TypeError("Expected argument 'grant_tokens' to be a list")
        pulumi.set(__self__, "grant_tokens", grant_tokens)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if key_id and not isinstance(key_id, str):
            raise TypeError("Expected argument 'key_id' to be a str")
        pulumi.set(__self__, "key_id", key_id)
        if key_manager and not isinstance(key_manager, str):
            raise TypeError("Expected argument 'key_manager' to be a str")
        pulumi.set(__self__, "key_manager", key_manager)
        if key_spec and not isinstance(key_spec, str):
            raise TypeError("Expected argument 'key_spec' to be a str")
        pulumi.set(__self__, "key_spec", key_spec)
        if key_state and not isinstance(key_state, str):
            raise TypeError("Expected argument 'key_state' to be a str")
        pulumi.set(__self__, "key_state", key_state)
        if key_usage and not isinstance(key_usage, str):
            raise TypeError("Expected argument 'key_usage' to be a str")
        pulumi.set(__self__, "key_usage", key_usage)
        if multi_region and not isinstance(multi_region, bool):
            raise TypeError("Expected argument 'multi_region' to be a bool")
        pulumi.set(__self__, "multi_region", multi_region)
        if multi_region_configurations and not isinstance(multi_region_configurations, list):
            raise TypeError("Expected argument 'multi_region_configurations' to be a list")
        pulumi.set(__self__, "multi_region_configurations", multi_region_configurations)
        if origin and not isinstance(origin, str):
            raise TypeError("Expected argument 'origin' to be a str")
        pulumi.set(__self__, "origin", origin)
        if pending_deletion_window_in_days and not isinstance(pending_deletion_window_in_days, int):
            raise TypeError("Expected argument 'pending_deletion_window_in_days' to be a int")
        pulumi.set(__self__, "pending_deletion_window_in_days", pending_deletion_window_in_days)
        if valid_to and not isinstance(valid_to, str):
            raise TypeError("Expected argument 'valid_to' to be a str")
        pulumi.set(__self__, "valid_to", valid_to)
        if xks_key_configurations and not isinstance(xks_key_configurations, list):
            raise TypeError("Expected argument 'xks_key_configurations' to be a list")
        pulumi.set(__self__, "xks_key_configurations", xks_key_configurations)

    @property
    @pulumi.getter
    def arn(self) -> str:
        """
        The key ARN of a primary or replica key of a multi-Region key.
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="awsAccountId")
    def aws_account_id(self) -> str:
        """
        The twelve-digit account ID of the AWS account that owns the key
        """
        return pulumi.get(self, "aws_account_id")

    @property
    @pulumi.getter(name="cloudHsmClusterId")
    def cloud_hsm_cluster_id(self) -> str:
        """
        The cluster ID of the AWS CloudHSM cluster that contains the key material for the KMS key.
        """
        return pulumi.get(self, "cloud_hsm_cluster_id")

    @property
    @pulumi.getter(name="creationDate")
    def creation_date(self) -> str:
        """
        The date and time when the key was created
        """
        return pulumi.get(self, "creation_date")

    @property
    @pulumi.getter(name="customKeyStoreId")
    def custom_key_store_id(self) -> str:
        """
        A unique identifier for the custom key store that contains the KMS key.
        """
        return pulumi.get(self, "custom_key_store_id")

    @property
    @pulumi.getter(name="customerMasterKeySpec")
    def customer_master_key_spec(self) -> str:
        """
        Specifies whether the key contains a symmetric key or an asymmetric key pair and the encryption algorithms or signing algorithms that the key supports
        """
        return pulumi.get(self, "customer_master_key_spec")

    @property
    @pulumi.getter(name="deletionDate")
    def deletion_date(self) -> str:
        """
        The date and time after which AWS KMS deletes the key. This value is present only when `key_state` is `PendingDeletion`, otherwise this value is 0
        """
        return pulumi.get(self, "deletion_date")

    @property
    @pulumi.getter
    def description(self) -> str:
        """
        The description of the key.
        """
        return pulumi.get(self, "description")

    @property
    @pulumi.getter
    def enabled(self) -> bool:
        """
        Specifies whether the key is enabled. When `key_state` is `Enabled` this value is true, otherwise it is false
        """
        return pulumi.get(self, "enabled")

    @property
    @pulumi.getter(name="expirationModel")
    def expiration_model(self) -> str:
        """
        Specifies whether the Key's key material expires. This value is present only when `origin` is `EXTERNAL`, otherwise this value is empty
        """
        return pulumi.get(self, "expiration_model")

    @property
    @pulumi.getter(name="grantTokens")
    def grant_tokens(self) -> Optional[Sequence[str]]:
        return pulumi.get(self, "grant_tokens")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="keyId")
    def key_id(self) -> str:
        return pulumi.get(self, "key_id")

    @property
    @pulumi.getter(name="keyManager")
    def key_manager(self) -> str:
        """
        The key's manager
        """
        return pulumi.get(self, "key_manager")

    @property
    @pulumi.getter(name="keySpec")
    def key_spec(self) -> str:
        """
        Describes the type of key material in the KMS key.
        """
        return pulumi.get(self, "key_spec")

    @property
    @pulumi.getter(name="keyState")
    def key_state(self) -> str:
        """
        The state of the key
        """
        return pulumi.get(self, "key_state")

    @property
    @pulumi.getter(name="keyUsage")
    def key_usage(self) -> str:
        """
        Specifies the intended use of the key
        """
        return pulumi.get(self, "key_usage")

    @property
    @pulumi.getter(name="multiRegion")
    def multi_region(self) -> bool:
        """
        Indicates whether the KMS key is a multi-Region (`true`) or regional (`false`) key.
        """
        return pulumi.get(self, "multi_region")

    @property
    @pulumi.getter(name="multiRegionConfigurations")
    def multi_region_configurations(self) -> Sequence['outputs.GetKeyMultiRegionConfigurationResult']:
        """
        Lists the primary and replica keys in same multi-Region key. Present only when the value of `multi_region` is `true`.
        """
        return pulumi.get(self, "multi_region_configurations")

    @property
    @pulumi.getter
    def origin(self) -> str:
        """
        When this value is `AWS_KMS`, AWS KMS created the key material. When this value is `EXTERNAL`, the key material was imported from your existing key management infrastructure or the CMK lacks key material
        """
        return pulumi.get(self, "origin")

    @property
    @pulumi.getter(name="pendingDeletionWindowInDays")
    def pending_deletion_window_in_days(self) -> int:
        """
        The waiting period before the primary key in a multi-Region key is deleted.
        """
        return pulumi.get(self, "pending_deletion_window_in_days")

    @property
    @pulumi.getter(name="validTo")
    def valid_to(self) -> str:
        """
        The time at which the imported key material expires. This value is present only when `origin` is `EXTERNAL` and whose `expiration_model` is `KEY_MATERIAL_EXPIRES`, otherwise this value is 0
        """
        return pulumi.get(self, "valid_to")

    @property
    @pulumi.getter(name="xksKeyConfigurations")
    def xks_key_configurations(self) -> Sequence['outputs.GetKeyXksKeyConfigurationResult']:
        """
        Information about the external key that is associated with a KMS key in an external key store.
        """
        return pulumi.get(self, "xks_key_configurations")


class AwaitableGetKeyResult(GetKeyResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetKeyResult(
            arn=self.arn,
            aws_account_id=self.aws_account_id,
            cloud_hsm_cluster_id=self.cloud_hsm_cluster_id,
            creation_date=self.creation_date,
            custom_key_store_id=self.custom_key_store_id,
            customer_master_key_spec=self.customer_master_key_spec,
            deletion_date=self.deletion_date,
            description=self.description,
            enabled=self.enabled,
            expiration_model=self.expiration_model,
            grant_tokens=self.grant_tokens,
            id=self.id,
            key_id=self.key_id,
            key_manager=self.key_manager,
            key_spec=self.key_spec,
            key_state=self.key_state,
            key_usage=self.key_usage,
            multi_region=self.multi_region,
            multi_region_configurations=self.multi_region_configurations,
            origin=self.origin,
            pending_deletion_window_in_days=self.pending_deletion_window_in_days,
            valid_to=self.valid_to,
            xks_key_configurations=self.xks_key_configurations)


def get_key(grant_tokens: Optional[Sequence[str]] = None,
            key_id: Optional[str] = None,
            opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetKeyResult:
    """
    Use this data source to get detailed information about
    the specified KMS Key with flexible key id input.
    This can be useful to reference key alias
    without having to hard code the ARN as input.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    by_alias = aws.kms.get_key(key_id="alias/my-key")
    by_id = aws.kms.get_key(key_id="1234abcd-12ab-34cd-56ef-1234567890ab")
    by_alias_arn = aws.kms.get_key(key_id="arn:aws:kms:us-east-1:111122223333:alias/my-key")
    by_key_arn = aws.kms.get_key(key_id="arn:aws:kms:us-east-1:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab")
    ```


    :param Sequence[str] grant_tokens: List of grant tokens
    :param str key_id: Key identifier which can be one of the following format:
           * Key ID. E.g: `1234abcd-12ab-34cd-56ef-1234567890ab`
           * Key ARN. E.g.: `arn:aws:kms:us-east-1:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab`
           * Alias name. E.g.: `alias/my-key`
           * Alias ARN: E.g.: `arn:aws:kms:us-east-1:111122223333:alias/my-key`
    """
    __args__ = dict()
    __args__['grantTokens'] = grant_tokens
    __args__['keyId'] = key_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:kms/getKey:getKey', __args__, opts=opts, typ=GetKeyResult).value

    return AwaitableGetKeyResult(
        arn=pulumi.get(__ret__, 'arn'),
        aws_account_id=pulumi.get(__ret__, 'aws_account_id'),
        cloud_hsm_cluster_id=pulumi.get(__ret__, 'cloud_hsm_cluster_id'),
        creation_date=pulumi.get(__ret__, 'creation_date'),
        custom_key_store_id=pulumi.get(__ret__, 'custom_key_store_id'),
        customer_master_key_spec=pulumi.get(__ret__, 'customer_master_key_spec'),
        deletion_date=pulumi.get(__ret__, 'deletion_date'),
        description=pulumi.get(__ret__, 'description'),
        enabled=pulumi.get(__ret__, 'enabled'),
        expiration_model=pulumi.get(__ret__, 'expiration_model'),
        grant_tokens=pulumi.get(__ret__, 'grant_tokens'),
        id=pulumi.get(__ret__, 'id'),
        key_id=pulumi.get(__ret__, 'key_id'),
        key_manager=pulumi.get(__ret__, 'key_manager'),
        key_spec=pulumi.get(__ret__, 'key_spec'),
        key_state=pulumi.get(__ret__, 'key_state'),
        key_usage=pulumi.get(__ret__, 'key_usage'),
        multi_region=pulumi.get(__ret__, 'multi_region'),
        multi_region_configurations=pulumi.get(__ret__, 'multi_region_configurations'),
        origin=pulumi.get(__ret__, 'origin'),
        pending_deletion_window_in_days=pulumi.get(__ret__, 'pending_deletion_window_in_days'),
        valid_to=pulumi.get(__ret__, 'valid_to'),
        xks_key_configurations=pulumi.get(__ret__, 'xks_key_configurations'))


@_utilities.lift_output_func(get_key)
def get_key_output(grant_tokens: Optional[pulumi.Input[Optional[Sequence[str]]]] = None,
                   key_id: Optional[pulumi.Input[str]] = None,
                   opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetKeyResult]:
    """
    Use this data source to get detailed information about
    the specified KMS Key with flexible key id input.
    This can be useful to reference key alias
    without having to hard code the ARN as input.

    ## Example Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    by_alias = aws.kms.get_key(key_id="alias/my-key")
    by_id = aws.kms.get_key(key_id="1234abcd-12ab-34cd-56ef-1234567890ab")
    by_alias_arn = aws.kms.get_key(key_id="arn:aws:kms:us-east-1:111122223333:alias/my-key")
    by_key_arn = aws.kms.get_key(key_id="arn:aws:kms:us-east-1:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab")
    ```


    :param Sequence[str] grant_tokens: List of grant tokens
    :param str key_id: Key identifier which can be one of the following format:
           * Key ID. E.g: `1234abcd-12ab-34cd-56ef-1234567890ab`
           * Key ARN. E.g.: `arn:aws:kms:us-east-1:111122223333:key/1234abcd-12ab-34cd-56ef-1234567890ab`
           * Alias name. E.g.: `alias/my-key`
           * Alias ARN: E.g.: `arn:aws:kms:us-east-1:111122223333:alias/my-key`
    """
    ...
