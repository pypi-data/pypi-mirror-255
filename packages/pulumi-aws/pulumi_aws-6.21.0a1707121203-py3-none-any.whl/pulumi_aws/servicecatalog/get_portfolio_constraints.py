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
    'GetPortfolioConstraintsResult',
    'AwaitableGetPortfolioConstraintsResult',
    'get_portfolio_constraints',
    'get_portfolio_constraints_output',
]

@pulumi.output_type
class GetPortfolioConstraintsResult:
    """
    A collection of values returned by getPortfolioConstraints.
    """
    def __init__(__self__, accept_language=None, details=None, id=None, portfolio_id=None, product_id=None):
        if accept_language and not isinstance(accept_language, str):
            raise TypeError("Expected argument 'accept_language' to be a str")
        pulumi.set(__self__, "accept_language", accept_language)
        if details and not isinstance(details, list):
            raise TypeError("Expected argument 'details' to be a list")
        pulumi.set(__self__, "details", details)
        if id and not isinstance(id, str):
            raise TypeError("Expected argument 'id' to be a str")
        pulumi.set(__self__, "id", id)
        if portfolio_id and not isinstance(portfolio_id, str):
            raise TypeError("Expected argument 'portfolio_id' to be a str")
        pulumi.set(__self__, "portfolio_id", portfolio_id)
        if product_id and not isinstance(product_id, str):
            raise TypeError("Expected argument 'product_id' to be a str")
        pulumi.set(__self__, "product_id", product_id)

    @property
    @pulumi.getter(name="acceptLanguage")
    def accept_language(self) -> Optional[str]:
        return pulumi.get(self, "accept_language")

    @property
    @pulumi.getter
    def details(self) -> Sequence['outputs.GetPortfolioConstraintsDetailResult']:
        """
        List of information about the constraints. See details below.
        """
        return pulumi.get(self, "details")

    @property
    @pulumi.getter
    def id(self) -> str:
        """
        The provider-assigned unique ID for this managed resource.
        """
        return pulumi.get(self, "id")

    @property
    @pulumi.getter(name="portfolioId")
    def portfolio_id(self) -> str:
        """
        Identifier of the portfolio the product resides in. The constraint applies only to the instance of the product that lives within this portfolio.
        """
        return pulumi.get(self, "portfolio_id")

    @property
    @pulumi.getter(name="productId")
    def product_id(self) -> Optional[str]:
        """
        Identifier of the product the constraint applies to. A constraint applies to a specific instance of a product within a certain portfolio.
        """
        return pulumi.get(self, "product_id")


class AwaitableGetPortfolioConstraintsResult(GetPortfolioConstraintsResult):
    # pylint: disable=using-constant-test
    def __await__(self):
        if False:
            yield self
        return GetPortfolioConstraintsResult(
            accept_language=self.accept_language,
            details=self.details,
            id=self.id,
            portfolio_id=self.portfolio_id,
            product_id=self.product_id)


def get_portfolio_constraints(accept_language: Optional[str] = None,
                              portfolio_id: Optional[str] = None,
                              product_id: Optional[str] = None,
                              opts: Optional[pulumi.InvokeOptions] = None) -> AwaitableGetPortfolioConstraintsResult:
    """
    Provides information on Service Catalog Portfolio Constraints.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.servicecatalog.get_portfolio_constraints(portfolio_id="port-3lli3b3an")
    ```


    :param str accept_language: Language code. Valid values: `en` (English), `jp` (Japanese), `zh` (Chinese). Default value is `en`.
    :param str portfolio_id: Portfolio identifier.
           
           The following arguments are optional:
    :param str product_id: Product identifier.
    """
    __args__ = dict()
    __args__['acceptLanguage'] = accept_language
    __args__['portfolioId'] = portfolio_id
    __args__['productId'] = product_id
    opts = pulumi.InvokeOptions.merge(_utilities.get_invoke_opts_defaults(), opts)
    __ret__ = pulumi.runtime.invoke('aws:servicecatalog/getPortfolioConstraints:getPortfolioConstraints', __args__, opts=opts, typ=GetPortfolioConstraintsResult).value

    return AwaitableGetPortfolioConstraintsResult(
        accept_language=pulumi.get(__ret__, 'accept_language'),
        details=pulumi.get(__ret__, 'details'),
        id=pulumi.get(__ret__, 'id'),
        portfolio_id=pulumi.get(__ret__, 'portfolio_id'),
        product_id=pulumi.get(__ret__, 'product_id'))


@_utilities.lift_output_func(get_portfolio_constraints)
def get_portfolio_constraints_output(accept_language: Optional[pulumi.Input[Optional[str]]] = None,
                                     portfolio_id: Optional[pulumi.Input[str]] = None,
                                     product_id: Optional[pulumi.Input[Optional[str]]] = None,
                                     opts: Optional[pulumi.InvokeOptions] = None) -> pulumi.Output[GetPortfolioConstraintsResult]:
    """
    Provides information on Service Catalog Portfolio Constraints.

    ## Example Usage
    ### Basic Usage

    ```python
    import pulumi
    import pulumi_aws as aws

    example = aws.servicecatalog.get_portfolio_constraints(portfolio_id="port-3lli3b3an")
    ```


    :param str accept_language: Language code. Valid values: `en` (English), `jp` (Japanese), `zh` (Chinese). Default value is `en`.
    :param str portfolio_id: Portfolio identifier.
           
           The following arguments are optional:
    :param str product_id: Product identifier.
    """
    ...
