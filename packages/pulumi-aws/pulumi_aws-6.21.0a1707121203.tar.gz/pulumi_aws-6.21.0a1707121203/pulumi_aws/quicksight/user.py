# coding=utf-8
# *** WARNING: this file was generated by the Pulumi Terraform Bridge (tfgen) Tool. ***
# *** Do not edit by hand unless you're certain you know what you are doing! ***

import copy
import warnings
import pulumi
import pulumi.runtime
from typing import Any, Mapping, Optional, Sequence, Union, overload
from .. import _utilities

__all__ = ['UserArgs', 'User']

@pulumi.input_type
class UserArgs:
    def __init__(__self__, *,
                 email: pulumi.Input[str],
                 identity_type: pulumi.Input[str],
                 user_role: pulumi.Input[str],
                 aws_account_id: Optional[pulumi.Input[str]] = None,
                 iam_arn: Optional[pulumi.Input[str]] = None,
                 namespace: Optional[pulumi.Input[str]] = None,
                 session_name: Optional[pulumi.Input[str]] = None,
                 user_name: Optional[pulumi.Input[str]] = None):
        """
        The set of arguments for constructing a User resource.
        :param pulumi.Input[str] email: The email address of the user that you want to register.
        :param pulumi.Input[str] identity_type: Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        :param pulumi.Input[str] user_role: The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        :param pulumi.Input[str] aws_account_id: The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        :param pulumi.Input[str] iam_arn: The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        :param pulumi.Input[str] namespace: The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        :param pulumi.Input[str] session_name: The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        :param pulumi.Input[str] user_name: The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        """
        pulumi.set(__self__, "email", email)
        pulumi.set(__self__, "identity_type", identity_type)
        pulumi.set(__self__, "user_role", user_role)
        if aws_account_id is not None:
            pulumi.set(__self__, "aws_account_id", aws_account_id)
        if iam_arn is not None:
            pulumi.set(__self__, "iam_arn", iam_arn)
        if namespace is not None:
            pulumi.set(__self__, "namespace", namespace)
        if session_name is not None:
            pulumi.set(__self__, "session_name", session_name)
        if user_name is not None:
            pulumi.set(__self__, "user_name", user_name)

    @property
    @pulumi.getter
    def email(self) -> pulumi.Input[str]:
        """
        The email address of the user that you want to register.
        """
        return pulumi.get(self, "email")

    @email.setter
    def email(self, value: pulumi.Input[str]):
        pulumi.set(self, "email", value)

    @property
    @pulumi.getter(name="identityType")
    def identity_type(self) -> pulumi.Input[str]:
        """
        Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        """
        return pulumi.get(self, "identity_type")

    @identity_type.setter
    def identity_type(self, value: pulumi.Input[str]):
        pulumi.set(self, "identity_type", value)

    @property
    @pulumi.getter(name="userRole")
    def user_role(self) -> pulumi.Input[str]:
        """
        The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        """
        return pulumi.get(self, "user_role")

    @user_role.setter
    def user_role(self, value: pulumi.Input[str]):
        pulumi.set(self, "user_role", value)

    @property
    @pulumi.getter(name="awsAccountId")
    def aws_account_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        """
        return pulumi.get(self, "aws_account_id")

    @aws_account_id.setter
    def aws_account_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "aws_account_id", value)

    @property
    @pulumi.getter(name="iamArn")
    def iam_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        """
        return pulumi.get(self, "iam_arn")

    @iam_arn.setter
    def iam_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "iam_arn", value)

    @property
    @pulumi.getter
    def namespace(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        """
        return pulumi.get(self, "namespace")

    @namespace.setter
    def namespace(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "namespace", value)

    @property
    @pulumi.getter(name="sessionName")
    def session_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        """
        return pulumi.get(self, "session_name")

    @session_name.setter
    def session_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "session_name", value)

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        """
        return pulumi.get(self, "user_name")

    @user_name.setter
    def user_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_name", value)


@pulumi.input_type
class _UserState:
    def __init__(__self__, *,
                 arn: Optional[pulumi.Input[str]] = None,
                 aws_account_id: Optional[pulumi.Input[str]] = None,
                 email: Optional[pulumi.Input[str]] = None,
                 iam_arn: Optional[pulumi.Input[str]] = None,
                 identity_type: Optional[pulumi.Input[str]] = None,
                 namespace: Optional[pulumi.Input[str]] = None,
                 session_name: Optional[pulumi.Input[str]] = None,
                 user_name: Optional[pulumi.Input[str]] = None,
                 user_role: Optional[pulumi.Input[str]] = None):
        """
        Input properties used for looking up and filtering User resources.
        :param pulumi.Input[str] arn: Amazon Resource Name (ARN) of the user
        :param pulumi.Input[str] aws_account_id: The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        :param pulumi.Input[str] email: The email address of the user that you want to register.
        :param pulumi.Input[str] iam_arn: The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        :param pulumi.Input[str] identity_type: Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        :param pulumi.Input[str] namespace: The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        :param pulumi.Input[str] session_name: The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        :param pulumi.Input[str] user_name: The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        :param pulumi.Input[str] user_role: The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        """
        if arn is not None:
            pulumi.set(__self__, "arn", arn)
        if aws_account_id is not None:
            pulumi.set(__self__, "aws_account_id", aws_account_id)
        if email is not None:
            pulumi.set(__self__, "email", email)
        if iam_arn is not None:
            pulumi.set(__self__, "iam_arn", iam_arn)
        if identity_type is not None:
            pulumi.set(__self__, "identity_type", identity_type)
        if namespace is not None:
            pulumi.set(__self__, "namespace", namespace)
        if session_name is not None:
            pulumi.set(__self__, "session_name", session_name)
        if user_name is not None:
            pulumi.set(__self__, "user_name", user_name)
        if user_role is not None:
            pulumi.set(__self__, "user_role", user_role)

    @property
    @pulumi.getter
    def arn(self) -> Optional[pulumi.Input[str]]:
        """
        Amazon Resource Name (ARN) of the user
        """
        return pulumi.get(self, "arn")

    @arn.setter
    def arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "arn", value)

    @property
    @pulumi.getter(name="awsAccountId")
    def aws_account_id(self) -> Optional[pulumi.Input[str]]:
        """
        The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        """
        return pulumi.get(self, "aws_account_id")

    @aws_account_id.setter
    def aws_account_id(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "aws_account_id", value)

    @property
    @pulumi.getter
    def email(self) -> Optional[pulumi.Input[str]]:
        """
        The email address of the user that you want to register.
        """
        return pulumi.get(self, "email")

    @email.setter
    def email(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "email", value)

    @property
    @pulumi.getter(name="iamArn")
    def iam_arn(self) -> Optional[pulumi.Input[str]]:
        """
        The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        """
        return pulumi.get(self, "iam_arn")

    @iam_arn.setter
    def iam_arn(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "iam_arn", value)

    @property
    @pulumi.getter(name="identityType")
    def identity_type(self) -> Optional[pulumi.Input[str]]:
        """
        Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        """
        return pulumi.get(self, "identity_type")

    @identity_type.setter
    def identity_type(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "identity_type", value)

    @property
    @pulumi.getter
    def namespace(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        """
        return pulumi.get(self, "namespace")

    @namespace.setter
    def namespace(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "namespace", value)

    @property
    @pulumi.getter(name="sessionName")
    def session_name(self) -> Optional[pulumi.Input[str]]:
        """
        The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        """
        return pulumi.get(self, "session_name")

    @session_name.setter
    def session_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "session_name", value)

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        """
        return pulumi.get(self, "user_name")

    @user_name.setter
    def user_name(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_name", value)

    @property
    @pulumi.getter(name="userRole")
    def user_role(self) -> Optional[pulumi.Input[str]]:
        """
        The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        """
        return pulumi.get(self, "user_role")

    @user_role.setter
    def user_role(self, value: Optional[pulumi.Input[str]]):
        pulumi.set(self, "user_role", value)


class User(pulumi.CustomResource):
    @overload
    def __init__(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 aws_account_id: Optional[pulumi.Input[str]] = None,
                 email: Optional[pulumi.Input[str]] = None,
                 iam_arn: Optional[pulumi.Input[str]] = None,
                 identity_type: Optional[pulumi.Input[str]] = None,
                 namespace: Optional[pulumi.Input[str]] = None,
                 session_name: Optional[pulumi.Input[str]] = None,
                 user_name: Optional[pulumi.Input[str]] = None,
                 user_role: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        """
        Resource for managing QuickSight User

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.quicksight.User("example",
            email="author@example.com",
            iam_arn="arn:aws:iam::123456789012:user/Example",
            identity_type="IAM",
            namespace="foo",
            session_name="an-author",
            user_role="AUTHOR")
        ```

        ## Import

        You cannot import this resource.

        :param str resource_name: The name of the resource.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] aws_account_id: The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        :param pulumi.Input[str] email: The email address of the user that you want to register.
        :param pulumi.Input[str] iam_arn: The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        :param pulumi.Input[str] identity_type: Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        :param pulumi.Input[str] namespace: The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        :param pulumi.Input[str] session_name: The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        :param pulumi.Input[str] user_name: The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        :param pulumi.Input[str] user_role: The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        """
        ...
    @overload
    def __init__(__self__,
                 resource_name: str,
                 args: UserArgs,
                 opts: Optional[pulumi.ResourceOptions] = None):
        """
        Resource for managing QuickSight User

        ## Example Usage

        ```python
        import pulumi
        import pulumi_aws as aws

        example = aws.quicksight.User("example",
            email="author@example.com",
            iam_arn="arn:aws:iam::123456789012:user/Example",
            identity_type="IAM",
            namespace="foo",
            session_name="an-author",
            user_role="AUTHOR")
        ```

        ## Import

        You cannot import this resource.

        :param str resource_name: The name of the resource.
        :param UserArgs args: The arguments to use to populate this resource's properties.
        :param pulumi.ResourceOptions opts: Options for the resource.
        """
        ...
    def __init__(__self__, resource_name: str, *args, **kwargs):
        resource_args, opts = _utilities.get_resource_args_opts(UserArgs, pulumi.ResourceOptions, *args, **kwargs)
        if resource_args is not None:
            __self__._internal_init(resource_name, opts, **resource_args.__dict__)
        else:
            __self__._internal_init(resource_name, *args, **kwargs)

    def _internal_init(__self__,
                 resource_name: str,
                 opts: Optional[pulumi.ResourceOptions] = None,
                 aws_account_id: Optional[pulumi.Input[str]] = None,
                 email: Optional[pulumi.Input[str]] = None,
                 iam_arn: Optional[pulumi.Input[str]] = None,
                 identity_type: Optional[pulumi.Input[str]] = None,
                 namespace: Optional[pulumi.Input[str]] = None,
                 session_name: Optional[pulumi.Input[str]] = None,
                 user_name: Optional[pulumi.Input[str]] = None,
                 user_role: Optional[pulumi.Input[str]] = None,
                 __props__=None):
        opts = pulumi.ResourceOptions.merge(_utilities.get_resource_opts_defaults(), opts)
        if not isinstance(opts, pulumi.ResourceOptions):
            raise TypeError('Expected resource options to be a ResourceOptions instance')
        if opts.id is None:
            if __props__ is not None:
                raise TypeError('__props__ is only valid when passed in combination with a valid opts.id to get an existing resource')
            __props__ = UserArgs.__new__(UserArgs)

            __props__.__dict__["aws_account_id"] = aws_account_id
            if email is None and not opts.urn:
                raise TypeError("Missing required property 'email'")
            __props__.__dict__["email"] = email
            __props__.__dict__["iam_arn"] = iam_arn
            if identity_type is None and not opts.urn:
                raise TypeError("Missing required property 'identity_type'")
            __props__.__dict__["identity_type"] = identity_type
            __props__.__dict__["namespace"] = namespace
            __props__.__dict__["session_name"] = session_name
            __props__.__dict__["user_name"] = user_name
            if user_role is None and not opts.urn:
                raise TypeError("Missing required property 'user_role'")
            __props__.__dict__["user_role"] = user_role
            __props__.__dict__["arn"] = None
        super(User, __self__).__init__(
            'aws:quicksight/user:User',
            resource_name,
            __props__,
            opts)

    @staticmethod
    def get(resource_name: str,
            id: pulumi.Input[str],
            opts: Optional[pulumi.ResourceOptions] = None,
            arn: Optional[pulumi.Input[str]] = None,
            aws_account_id: Optional[pulumi.Input[str]] = None,
            email: Optional[pulumi.Input[str]] = None,
            iam_arn: Optional[pulumi.Input[str]] = None,
            identity_type: Optional[pulumi.Input[str]] = None,
            namespace: Optional[pulumi.Input[str]] = None,
            session_name: Optional[pulumi.Input[str]] = None,
            user_name: Optional[pulumi.Input[str]] = None,
            user_role: Optional[pulumi.Input[str]] = None) -> 'User':
        """
        Get an existing User resource's state with the given name, id, and optional extra
        properties used to qualify the lookup.

        :param str resource_name: The unique name of the resulting resource.
        :param pulumi.Input[str] id: The unique provider ID of the resource to lookup.
        :param pulumi.ResourceOptions opts: Options for the resource.
        :param pulumi.Input[str] arn: Amazon Resource Name (ARN) of the user
        :param pulumi.Input[str] aws_account_id: The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        :param pulumi.Input[str] email: The email address of the user that you want to register.
        :param pulumi.Input[str] iam_arn: The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        :param pulumi.Input[str] identity_type: Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        :param pulumi.Input[str] namespace: The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        :param pulumi.Input[str] session_name: The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        :param pulumi.Input[str] user_name: The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        :param pulumi.Input[str] user_role: The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        """
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(id=id))

        __props__ = _UserState.__new__(_UserState)

        __props__.__dict__["arn"] = arn
        __props__.__dict__["aws_account_id"] = aws_account_id
        __props__.__dict__["email"] = email
        __props__.__dict__["iam_arn"] = iam_arn
        __props__.__dict__["identity_type"] = identity_type
        __props__.__dict__["namespace"] = namespace
        __props__.__dict__["session_name"] = session_name
        __props__.__dict__["user_name"] = user_name
        __props__.__dict__["user_role"] = user_role
        return User(resource_name, opts=opts, __props__=__props__)

    @property
    @pulumi.getter
    def arn(self) -> pulumi.Output[str]:
        """
        Amazon Resource Name (ARN) of the user
        """
        return pulumi.get(self, "arn")

    @property
    @pulumi.getter(name="awsAccountId")
    def aws_account_id(self) -> pulumi.Output[str]:
        """
        The ID for the AWS account that the user is in. Currently, you use the ID for the AWS account that contains your Amazon QuickSight account.
        """
        return pulumi.get(self, "aws_account_id")

    @property
    @pulumi.getter
    def email(self) -> pulumi.Output[str]:
        """
        The email address of the user that you want to register.
        """
        return pulumi.get(self, "email")

    @property
    @pulumi.getter(name="iamArn")
    def iam_arn(self) -> pulumi.Output[Optional[str]]:
        """
        The ARN of the IAM user or role that you are registering with Amazon QuickSight.
        """
        return pulumi.get(self, "iam_arn")

    @property
    @pulumi.getter(name="identityType")
    def identity_type(self) -> pulumi.Output[str]:
        """
        Amazon QuickSight supports several ways of managing the identity of users. This parameter accepts either  `IAM` or `QUICKSIGHT`. If `IAM` is specified, the `iam_arn` must also be specified.
        """
        return pulumi.get(self, "identity_type")

    @property
    @pulumi.getter
    def namespace(self) -> pulumi.Output[Optional[str]]:
        """
        The Amazon Quicksight namespace to create the user in. Defaults to `default`.
        """
        return pulumi.get(self, "namespace")

    @property
    @pulumi.getter(name="sessionName")
    def session_name(self) -> pulumi.Output[Optional[str]]:
        """
        The name of the IAM session to use when assuming roles that can embed QuickSight dashboards. Only valid for registering users using an assumed IAM role. Additionally, if registering multiple users using the same IAM role, each user needs to have a unique session name.
        """
        return pulumi.get(self, "session_name")

    @property
    @pulumi.getter(name="userName")
    def user_name(self) -> pulumi.Output[Optional[str]]:
        """
        The Amazon QuickSight user name that you want to create for the user you are registering. Only valid for registering a user with `identity_type` set to `QUICKSIGHT`.
        """
        return pulumi.get(self, "user_name")

    @property
    @pulumi.getter(name="userRole")
    def user_role(self) -> pulumi.Output[str]:
        """
        The Amazon QuickSight role of the user. The user role can be one of the following: `READER`, `AUTHOR`, or `ADMIN`
        """
        return pulumi.get(self, "user_role")

