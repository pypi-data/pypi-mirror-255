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
    'DelegationSignerRecordSigningAttributesArgs',
    'DelegationSignerRecordTimeoutsArgs',
    'RegisteredDomainAdminContactArgs',
    'RegisteredDomainNameServerArgs',
    'RegisteredDomainRegistrantContactArgs',
    'RegisteredDomainTechContactArgs',
]

@pulumi.input_type
class DelegationSignerRecordSigningAttributesArgs:
    def __init__(__self__, *,
                 algorithm: pulumi.Input[int],
                 flags: pulumi.Input[int],
                 public_key: pulumi.Input[str]):
        """
        :param pulumi.Input[int] algorithm: Algorithm which was used to generate the digest from the public key.
        :param pulumi.Input[int] flags: Defines the type of key. It can be either a KSK (key-signing-key, value `257`) or ZSK (zone-signing-key, value `256`).
        :param pulumi.Input[str] public_key: The base64-encoded public key part of the key pair that is passed to the registry.
        """
        pulumi.set(__self__, "algorithm", algorithm)
        pulumi.set(__self__, "flags", flags)
        pulumi.set(__self__, "public_key", public_key)

    @property
    @pulumi.getter
    def algorithm(self) -> pulumi.Input[int]:
        """
        Algorithm which was used to generate the digest from the public key.
        """
        return pulumi.get(self, "algorithm")

    @algorithm.setter
    def algorithm(self, value: pulumi.Input[int]):
        pulumi.set(self, "algorithm", value)

    @property
    @pulumi.getter
    def flags(self) -> pulumi.Input[int]:
        """
        Defines the type of key. It can be either a KSK (key-signing-key, value `257`) or ZSK (zone-signing-key, value `256`).
        """
        return pulumi.get(self, "flags")

    @flags.setter
    def flags(self, value: pulumi.Input[int]):
        pulumi.set(self, "flags", value)

    @property
    @pulumi.getter(name="publicKey")
    def public_key(self) -> pulumi.Input[str]:
        """
        The base64-encoded public key part of the key pair that is passed to the registry.
        """
        return pulumi.get(self, "public_key")

    @public_key.setter
    def public_key(self, value: pulumi.Input[str]):
        pulumi.set(self, "public_key", value)


@pulumi.input_type
class DelegationSignerRecordTimeoutsArgs:
    def __init__(__self__, *,
                 create: Optional[pulumi.Input[str]] = None,
                 delete: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] create: A string that can be [parsed as a duration](https://pkg.go.dev/time#ParseDuration) consisting of numbers and unit suffixes, such as "30s" or "2h45m". Valid time units are "s" (seconds), "m" (minutes), "h" (hours).
        :param pulumi.Input[str] delete: A string that can be [parsed as a duration](https://pkg.go.dev/time#ParseDuration) consisting of numbers and unit suffixes, such as "30s" or "2h45m". Valid time units are "s" (seconds), "m" (minutes), "h" (hours). Setting a timeout for a Delete operation is only applicable if changes are saved into state before the destroy operation occurs.
        """
        if create is not None:
            pulumi.set(__self__, "create", create)
        if delete is not None:
            pulumi.set(__self__, "delete", delete)

    @property
    @pulumi.getter
    def create(self) -> Optional[pulumi.Input[str]]:
        """
        A string that can be [parsed as a duration](https://pkg.go.dev/time#ParseDuration) consisting of numbers and unit suffixes, such as "30s" or "2h45m". Valid time units are "s" (seconds), "m" (minutes), "h" (hours).
        """
        return pulumi.get(self, "create")

    @create.setter
    def create(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "create", value)

    @property
    @pulumi.getter
    def delete(self) -> Optional[pulumi.Input[str]]:
        """
        A string that can be [parsed as a duration](https://pkg.go.dev/time#ParseDuration) consisting of numbers and unit suffixes, such as "30s" or "2h45m". Valid time units are "s" (seconds), "m" (minutes), "h" (hours). Setting a timeout for a Delete operation is only applicable if changes are saved into state before the destroy operation occurs.
        """
        return pulumi.get(self, "delete")

    @delete.setter
    def delete(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "delete", value)


@pulumi.input_type
class RegisteredDomainAdminContactArgs:
    def __init__(__self__, *,
                 address_line1: Optional[pulumi.Input[str]] = None,
                 address_line2: Optional[pulumi.Input[str]] = None,
                 city: Optional[pulumi.Input[str]] = None,
                 contact_type: Optional[pulumi.Input[str]] = None,
                 country_code: Optional[pulumi.Input[str]] = None,
                 email: Optional[pulumi.Input[str]] = None,
                 extra_params: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 fax: Optional[pulumi.Input[str]] = None,
                 first_name: Optional[pulumi.Input[str]] = None,
                 last_name: Optional[pulumi.Input[str]] = None,
                 organization_name: Optional[pulumi.Input[str]] = None,
                 phone_number: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 zip_code: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] address_line1: First line of the contact's address.
        :param pulumi.Input[str] address_line2: Second line of contact's address, if any.
        :param pulumi.Input[str] city: The city of the contact's address.
        :param pulumi.Input[str] contact_type: Indicates whether the contact is a person, company, association, or public organization. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-ContactType) for valid values.
        :param pulumi.Input[str] country_code: Code for the country of the contact's address. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-CountryCode) for valid values.
        :param pulumi.Input[str] email: Email address of the contact.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] extra_params: A key-value map of parameters required by certain top-level domains.
        :param pulumi.Input[str] fax: Fax number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        :param pulumi.Input[str] first_name: First name of contact.
        :param pulumi.Input[str] last_name: Last name of contact.
        :param pulumi.Input[str] organization_name: Name of the organization for contact types other than `PERSON`.
        :param pulumi.Input[str] phone_number: The phone number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        :param pulumi.Input[str] state: The state or province of the contact's city.
        :param pulumi.Input[str] zip_code: The zip or postal code of the contact's address.
        """
        if address_line1 is not None:
            pulumi.set(__self__, "address_line1", address_line1)
        if address_line2 is not None:
            pulumi.set(__self__, "address_line2", address_line2)
        if city is not None:
            pulumi.set(__self__, "city", city)
        if contact_type is not None:
            pulumi.set(__self__, "contact_type", contact_type)
        if country_code is not None:
            pulumi.set(__self__, "country_code", country_code)
        if email is not None:
            pulumi.set(__self__, "email", email)
        if extra_params is not None:
            pulumi.set(__self__, "extra_params", extra_params)
        if fax is not None:
            pulumi.set(__self__, "fax", fax)
        if first_name is not None:
            pulumi.set(__self__, "first_name", first_name)
        if last_name is not None:
            pulumi.set(__self__, "last_name", last_name)
        if organization_name is not None:
            pulumi.set(__self__, "organization_name", organization_name)
        if phone_number is not None:
            pulumi.set(__self__, "phone_number", phone_number)
        if state is not None:
            pulumi.set(__self__, "state", state)
        if zip_code is not None:
            pulumi.set(__self__, "zip_code", zip_code)

    @property
    @pulumi.getter(name="addressLine1")
    def address_line1(self) -> Optional[pulumi.Input[str]]:
        """
        First line of the contact's address.
        """
        return pulumi.get(self, "address_line1")

    @address_line1.setter
    def address_line1(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "address_line1", value)

    @property
    @pulumi.getter(name="addressLine2")
    def address_line2(self) -> Optional[pulumi.Input[str]]:
        """
        Second line of contact's address, if any.
        """
        return pulumi.get(self, "address_line2")

    @address_line2.setter
    def address_line2(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "address_line2", value)

    @property
    @pulumi.getter
    def city(self) -> Optional[pulumi.Input[str]]:
        """
        The city of the contact's address.
        """
        return pulumi.get(self, "city")

    @city.setter
    def city(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "city", value)

    @property
    @pulumi.getter(name="contactType")
    def contact_type(self) -> Optional[pulumi.Input[str]]:
        """
        Indicates whether the contact is a person, company, association, or public organization. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-ContactType) for valid values.
        """
        return pulumi.get(self, "contact_type")

    @contact_type.setter
    def contact_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "contact_type", value)

    @property
    @pulumi.getter(name="countryCode")
    def country_code(self) -> Optional[pulumi.Input[str]]:
        """
        Code for the country of the contact's address. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-CountryCode) for valid values.
        """
        return pulumi.get(self, "country_code")

    @country_code.setter
    def country_code(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "country_code", value)

    @property
    @pulumi.getter
    def email(self) -> Optional[pulumi.Input[str]]:
        """
        Email address of the contact.
        """
        return pulumi.get(self, "email")

    @email.setter
    def email(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "email", value)

    @property
    @pulumi.getter(name="extraParams")
    def extra_params(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A key-value map of parameters required by certain top-level domains.
        """
        return pulumi.get(self, "extra_params")

    @extra_params.setter
    def extra_params(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "extra_params", value)

    @property
    @pulumi.getter
    def fax(self) -> Optional[pulumi.Input[str]]:
        """
        Fax number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        """
        return pulumi.get(self, "fax")

    @fax.setter
    def fax(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "fax", value)

    @property
    @pulumi.getter(name="firstName")
    def first_name(self) -> Optional[pulumi.Input[str]]:
        """
        First name of contact.
        """
        return pulumi.get(self, "first_name")

    @first_name.setter
    def first_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "first_name", value)

    @property
    @pulumi.getter(name="lastName")
    def last_name(self) -> Optional[pulumi.Input[str]]:
        """
        Last name of contact.
        """
        return pulumi.get(self, "last_name")

    @last_name.setter
    def last_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "last_name", value)

    @property
    @pulumi.getter(name="organizationName")
    def organization_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the organization for contact types other than `PERSON`.
        """
        return pulumi.get(self, "organization_name")

    @organization_name.setter
    def organization_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organization_name", value)

    @property
    @pulumi.getter(name="phoneNumber")
    def phone_number(self) -> Optional[pulumi.Input[str]]:
        """
        The phone number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        """
        return pulumi.get(self, "phone_number")

    @phone_number.setter
    def phone_number(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "phone_number", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input[str]]:
        """
        The state or province of the contact's city.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="zipCode")
    def zip_code(self) -> Optional[pulumi.Input[str]]:
        """
        The zip or postal code of the contact's address.
        """
        return pulumi.get(self, "zip_code")

    @zip_code.setter
    def zip_code(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "zip_code", value)


@pulumi.input_type
class RegisteredDomainNameServerArgs:
    def __init__(__self__, *,
                 name: pulumi.Input[str],
                 glue_ips: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]] = None):
        """
        :param pulumi.Input[str] name: The fully qualified host name of the name server.
        :param pulumi.Input[Sequence[pulumi.Input[str]]] glue_ips: Glue IP addresses of a name server. The list can contain only one IPv4 and one IPv6 address.
        """
        pulumi.set(__self__, "name", name)
        if glue_ips is not None:
            pulumi.set(__self__, "glue_ips", glue_ips)

    @property
    @pulumi.getter
    def name(self) -> pulumi.Input[str]:
        """
        The fully qualified host name of the name server.
        """
        return pulumi.get(self, "name")

    @name.setter
    def name(self, value: pulumi.Input[str]):
        pulumi.set(self, "name", value)

    @property
    @pulumi.getter(name="glueIps")
    def glue_ips(self) -> Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]:
        """
        Glue IP addresses of a name server. The list can contain only one IPv4 and one IPv6 address.
        """
        return pulumi.get(self, "glue_ips")

    @glue_ips.setter
    def glue_ips(self, value: Optional[pulumi.Input[Sequence[pulumi.Input[str]]]]):
        pulumi.set(self, "glue_ips", value)


@pulumi.input_type
class RegisteredDomainRegistrantContactArgs:
    def __init__(__self__, *,
                 address_line1: Optional[pulumi.Input[str]] = None,
                 address_line2: Optional[pulumi.Input[str]] = None,
                 city: Optional[pulumi.Input[str]] = None,
                 contact_type: Optional[pulumi.Input[str]] = None,
                 country_code: Optional[pulumi.Input[str]] = None,
                 email: Optional[pulumi.Input[str]] = None,
                 extra_params: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 fax: Optional[pulumi.Input[str]] = None,
                 first_name: Optional[pulumi.Input[str]] = None,
                 last_name: Optional[pulumi.Input[str]] = None,
                 organization_name: Optional[pulumi.Input[str]] = None,
                 phone_number: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 zip_code: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] address_line1: First line of the contact's address.
        :param pulumi.Input[str] address_line2: Second line of contact's address, if any.
        :param pulumi.Input[str] city: The city of the contact's address.
        :param pulumi.Input[str] contact_type: Indicates whether the contact is a person, company, association, or public organization. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-ContactType) for valid values.
        :param pulumi.Input[str] country_code: Code for the country of the contact's address. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-CountryCode) for valid values.
        :param pulumi.Input[str] email: Email address of the contact.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] extra_params: A key-value map of parameters required by certain top-level domains.
        :param pulumi.Input[str] fax: Fax number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        :param pulumi.Input[str] first_name: First name of contact.
        :param pulumi.Input[str] last_name: Last name of contact.
        :param pulumi.Input[str] organization_name: Name of the organization for contact types other than `PERSON`.
        :param pulumi.Input[str] phone_number: The phone number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        :param pulumi.Input[str] state: The state or province of the contact's city.
        :param pulumi.Input[str] zip_code: The zip or postal code of the contact's address.
        """
        if address_line1 is not None:
            pulumi.set(__self__, "address_line1", address_line1)
        if address_line2 is not None:
            pulumi.set(__self__, "address_line2", address_line2)
        if city is not None:
            pulumi.set(__self__, "city", city)
        if contact_type is not None:
            pulumi.set(__self__, "contact_type", contact_type)
        if country_code is not None:
            pulumi.set(__self__, "country_code", country_code)
        if email is not None:
            pulumi.set(__self__, "email", email)
        if extra_params is not None:
            pulumi.set(__self__, "extra_params", extra_params)
        if fax is not None:
            pulumi.set(__self__, "fax", fax)
        if first_name is not None:
            pulumi.set(__self__, "first_name", first_name)
        if last_name is not None:
            pulumi.set(__self__, "last_name", last_name)
        if organization_name is not None:
            pulumi.set(__self__, "organization_name", organization_name)
        if phone_number is not None:
            pulumi.set(__self__, "phone_number", phone_number)
        if state is not None:
            pulumi.set(__self__, "state", state)
        if zip_code is not None:
            pulumi.set(__self__, "zip_code", zip_code)

    @property
    @pulumi.getter(name="addressLine1")
    def address_line1(self) -> Optional[pulumi.Input[str]]:
        """
        First line of the contact's address.
        """
        return pulumi.get(self, "address_line1")

    @address_line1.setter
    def address_line1(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "address_line1", value)

    @property
    @pulumi.getter(name="addressLine2")
    def address_line2(self) -> Optional[pulumi.Input[str]]:
        """
        Second line of contact's address, if any.
        """
        return pulumi.get(self, "address_line2")

    @address_line2.setter
    def address_line2(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "address_line2", value)

    @property
    @pulumi.getter
    def city(self) -> Optional[pulumi.Input[str]]:
        """
        The city of the contact's address.
        """
        return pulumi.get(self, "city")

    @city.setter
    def city(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "city", value)

    @property
    @pulumi.getter(name="contactType")
    def contact_type(self) -> Optional[pulumi.Input[str]]:
        """
        Indicates whether the contact is a person, company, association, or public organization. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-ContactType) for valid values.
        """
        return pulumi.get(self, "contact_type")

    @contact_type.setter
    def contact_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "contact_type", value)

    @property
    @pulumi.getter(name="countryCode")
    def country_code(self) -> Optional[pulumi.Input[str]]:
        """
        Code for the country of the contact's address. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-CountryCode) for valid values.
        """
        return pulumi.get(self, "country_code")

    @country_code.setter
    def country_code(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "country_code", value)

    @property
    @pulumi.getter
    def email(self) -> Optional[pulumi.Input[str]]:
        """
        Email address of the contact.
        """
        return pulumi.get(self, "email")

    @email.setter
    def email(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "email", value)

    @property
    @pulumi.getter(name="extraParams")
    def extra_params(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A key-value map of parameters required by certain top-level domains.
        """
        return pulumi.get(self, "extra_params")

    @extra_params.setter
    def extra_params(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "extra_params", value)

    @property
    @pulumi.getter
    def fax(self) -> Optional[pulumi.Input[str]]:
        """
        Fax number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        """
        return pulumi.get(self, "fax")

    @fax.setter
    def fax(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "fax", value)

    @property
    @pulumi.getter(name="firstName")
    def first_name(self) -> Optional[pulumi.Input[str]]:
        """
        First name of contact.
        """
        return pulumi.get(self, "first_name")

    @first_name.setter
    def first_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "first_name", value)

    @property
    @pulumi.getter(name="lastName")
    def last_name(self) -> Optional[pulumi.Input[str]]:
        """
        Last name of contact.
        """
        return pulumi.get(self, "last_name")

    @last_name.setter
    def last_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "last_name", value)

    @property
    @pulumi.getter(name="organizationName")
    def organization_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the organization for contact types other than `PERSON`.
        """
        return pulumi.get(self, "organization_name")

    @organization_name.setter
    def organization_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organization_name", value)

    @property
    @pulumi.getter(name="phoneNumber")
    def phone_number(self) -> Optional[pulumi.Input[str]]:
        """
        The phone number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        """
        return pulumi.get(self, "phone_number")

    @phone_number.setter
    def phone_number(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "phone_number", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input[str]]:
        """
        The state or province of the contact's city.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="zipCode")
    def zip_code(self) -> Optional[pulumi.Input[str]]:
        """
        The zip or postal code of the contact's address.
        """
        return pulumi.get(self, "zip_code")

    @zip_code.setter
    def zip_code(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "zip_code", value)


@pulumi.input_type
class RegisteredDomainTechContactArgs:
    def __init__(__self__, *,
                 address_line1: Optional[pulumi.Input[str]] = None,
                 address_line2: Optional[pulumi.Input[str]] = None,
                 city: Optional[pulumi.Input[str]] = None,
                 contact_type: Optional[pulumi.Input[str]] = None,
                 country_code: Optional[pulumi.Input[str]] = None,
                 email: Optional[pulumi.Input[str]] = None,
                 extra_params: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]] = None,
                 fax: Optional[pulumi.Input[str]] = None,
                 first_name: Optional[pulumi.Input[str]] = None,
                 last_name: Optional[pulumi.Input[str]] = None,
                 organization_name: Optional[pulumi.Input[str]] = None,
                 phone_number: Optional[pulumi.Input[str]] = None,
                 state: Optional[pulumi.Input[str]] = None,
                 zip_code: Optional[pulumi.Input[str]] = None):
        """
        :param pulumi.Input[str] address_line1: First line of the contact's address.
        :param pulumi.Input[str] address_line2: Second line of contact's address, if any.
        :param pulumi.Input[str] city: The city of the contact's address.
        :param pulumi.Input[str] contact_type: Indicates whether the contact is a person, company, association, or public organization. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-ContactType) for valid values.
        :param pulumi.Input[str] country_code: Code for the country of the contact's address. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-CountryCode) for valid values.
        :param pulumi.Input[str] email: Email address of the contact.
        :param pulumi.Input[Mapping[str, pulumi.Input[str]]] extra_params: A key-value map of parameters required by certain top-level domains.
        :param pulumi.Input[str] fax: Fax number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        :param pulumi.Input[str] first_name: First name of contact.
        :param pulumi.Input[str] last_name: Last name of contact.
        :param pulumi.Input[str] organization_name: Name of the organization for contact types other than `PERSON`.
        :param pulumi.Input[str] phone_number: The phone number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        :param pulumi.Input[str] state: The state or province of the contact's city.
        :param pulumi.Input[str] zip_code: The zip or postal code of the contact's address.
        """
        if address_line1 is not None:
            pulumi.set(__self__, "address_line1", address_line1)
        if address_line2 is not None:
            pulumi.set(__self__, "address_line2", address_line2)
        if city is not None:
            pulumi.set(__self__, "city", city)
        if contact_type is not None:
            pulumi.set(__self__, "contact_type", contact_type)
        if country_code is not None:
            pulumi.set(__self__, "country_code", country_code)
        if email is not None:
            pulumi.set(__self__, "email", email)
        if extra_params is not None:
            pulumi.set(__self__, "extra_params", extra_params)
        if fax is not None:
            pulumi.set(__self__, "fax", fax)
        if first_name is not None:
            pulumi.set(__self__, "first_name", first_name)
        if last_name is not None:
            pulumi.set(__self__, "last_name", last_name)
        if organization_name is not None:
            pulumi.set(__self__, "organization_name", organization_name)
        if phone_number is not None:
            pulumi.set(__self__, "phone_number", phone_number)
        if state is not None:
            pulumi.set(__self__, "state", state)
        if zip_code is not None:
            pulumi.set(__self__, "zip_code", zip_code)

    @property
    @pulumi.getter(name="addressLine1")
    def address_line1(self) -> Optional[pulumi.Input[str]]:
        """
        First line of the contact's address.
        """
        return pulumi.get(self, "address_line1")

    @address_line1.setter
    def address_line1(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "address_line1", value)

    @property
    @pulumi.getter(name="addressLine2")
    def address_line2(self) -> Optional[pulumi.Input[str]]:
        """
        Second line of contact's address, if any.
        """
        return pulumi.get(self, "address_line2")

    @address_line2.setter
    def address_line2(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "address_line2", value)

    @property
    @pulumi.getter
    def city(self) -> Optional[pulumi.Input[str]]:
        """
        The city of the contact's address.
        """
        return pulumi.get(self, "city")

    @city.setter
    def city(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "city", value)

    @property
    @pulumi.getter(name="contactType")
    def contact_type(self) -> Optional[pulumi.Input[str]]:
        """
        Indicates whether the contact is a person, company, association, or public organization. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-ContactType) for valid values.
        """
        return pulumi.get(self, "contact_type")

    @contact_type.setter
    def contact_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "contact_type", value)

    @property
    @pulumi.getter(name="countryCode")
    def country_code(self) -> Optional[pulumi.Input[str]]:
        """
        Code for the country of the contact's address. See the [AWS API documentation](https://docs.aws.amazon.com/Route53/latest/APIReference/API_domains_ContactDetail.html#Route53Domains-Type-domains_ContactDetail-CountryCode) for valid values.
        """
        return pulumi.get(self, "country_code")

    @country_code.setter
    def country_code(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "country_code", value)

    @property
    @pulumi.getter
    def email(self) -> Optional[pulumi.Input[str]]:
        """
        Email address of the contact.
        """
        return pulumi.get(self, "email")

    @email.setter
    def email(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "email", value)

    @property
    @pulumi.getter(name="extraParams")
    def extra_params(self) -> Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]:
        """
        A key-value map of parameters required by certain top-level domains.
        """
        return pulumi.get(self, "extra_params")

    @extra_params.setter
    def extra_params(self, value: Optional[pulumi.Input[Mapping[str, pulumi.Input[str]]]]):
        pulumi.set(self, "extra_params", value)

    @property
    @pulumi.getter
    def fax(self) -> Optional[pulumi.Input[str]]:
        """
        Fax number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        """
        return pulumi.get(self, "fax")

    @fax.setter
    def fax(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "fax", value)

    @property
    @pulumi.getter(name="firstName")
    def first_name(self) -> Optional[pulumi.Input[str]]:
        """
        First name of contact.
        """
        return pulumi.get(self, "first_name")

    @first_name.setter
    def first_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "first_name", value)

    @property
    @pulumi.getter(name="lastName")
    def last_name(self) -> Optional[pulumi.Input[str]]:
        """
        Last name of contact.
        """
        return pulumi.get(self, "last_name")

    @last_name.setter
    def last_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "last_name", value)

    @property
    @pulumi.getter(name="organizationName")
    def organization_name(self) -> Optional[pulumi.Input[str]]:
        """
        Name of the organization for contact types other than `PERSON`.
        """
        return pulumi.get(self, "organization_name")

    @organization_name.setter
    def organization_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "organization_name", value)

    @property
    @pulumi.getter(name="phoneNumber")
    def phone_number(self) -> Optional[pulumi.Input[str]]:
        """
        The phone number of the contact. Phone number must be specified in the format "+[country dialing code].[number including any area code]".
        """
        return pulumi.get(self, "phone_number")

    @phone_number.setter
    def phone_number(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "phone_number", value)

    @property
    @pulumi.getter
    def state(self) -> Optional[pulumi.Input[str]]:
        """
        The state or province of the contact's city.
        """
        return pulumi.get(self, "state")

    @state.setter
    def state(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "state", value)

    @property
    @pulumi.getter(name="zipCode")
    def zip_code(self) -> Optional[pulumi.Input[str]]:
        """
        The zip or postal code of the contact's address.
        """
        return pulumi.get(self, "zip_code")

    @zip_code.setter
    def zip_code(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "zip_code", value)


