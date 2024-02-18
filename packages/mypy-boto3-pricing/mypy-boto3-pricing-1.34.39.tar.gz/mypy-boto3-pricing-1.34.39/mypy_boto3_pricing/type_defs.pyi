"""
Type annotations for pricing service type definitions.

[Open documentation](https://youtype.github.io/boto3_stubs_docs/mypy_boto3_pricing/type_defs/)

Usage::

    ```python
    from mypy_boto3_pricing.type_defs import AttributeValueTypeDef

    data: AttributeValueTypeDef = ...
    ```
"""

import sys
from datetime import datetime
from typing import Dict, List, Sequence, Union

if sys.version_info >= (3, 12):
    from typing import Literal
else:
    from typing_extensions import Literal
if sys.version_info >= (3, 12):
    from typing import NotRequired
else:
    from typing_extensions import NotRequired
if sys.version_info >= (3, 12):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict

__all__ = (
    "AttributeValueTypeDef",
    "PaginatorConfigTypeDef",
    "DescribeServicesRequestRequestTypeDef",
    "ResponseMetadataTypeDef",
    "ServiceTypeDef",
    "FilterTypeDef",
    "GetAttributeValuesRequestRequestTypeDef",
    "GetPriceListFileUrlRequestRequestTypeDef",
    "TimestampTypeDef",
    "PriceListTypeDef",
    "DescribeServicesRequestDescribeServicesPaginateTypeDef",
    "GetAttributeValuesRequestGetAttributeValuesPaginateTypeDef",
    "GetAttributeValuesResponseTypeDef",
    "GetPriceListFileUrlResponseTypeDef",
    "GetProductsResponseTypeDef",
    "DescribeServicesResponseTypeDef",
    "GetProductsRequestGetProductsPaginateTypeDef",
    "GetProductsRequestRequestTypeDef",
    "ListPriceListsRequestListPriceListsPaginateTypeDef",
    "ListPriceListsRequestRequestTypeDef",
    "ListPriceListsResponseTypeDef",
)

AttributeValueTypeDef = TypedDict(
    "AttributeValueTypeDef",
    {
        "Value": NotRequired[str],
    },
)
PaginatorConfigTypeDef = TypedDict(
    "PaginatorConfigTypeDef",
    {
        "MaxItems": NotRequired[int],
        "PageSize": NotRequired[int],
        "StartingToken": NotRequired[str],
    },
)
DescribeServicesRequestRequestTypeDef = TypedDict(
    "DescribeServicesRequestRequestTypeDef",
    {
        "ServiceCode": NotRequired[str],
        "FormatVersion": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ResponseMetadataTypeDef = TypedDict(
    "ResponseMetadataTypeDef",
    {
        "RequestId": str,
        "HostId": str,
        "HTTPStatusCode": int,
        "HTTPHeaders": Dict[str, str],
        "RetryAttempts": int,
    },
)
ServiceTypeDef = TypedDict(
    "ServiceTypeDef",
    {
        "ServiceCode": str,
        "AttributeNames": NotRequired[List[str]],
    },
)
FilterTypeDef = TypedDict(
    "FilterTypeDef",
    {
        "Type": Literal["TERM_MATCH"],
        "Field": str,
        "Value": str,
    },
)
GetAttributeValuesRequestRequestTypeDef = TypedDict(
    "GetAttributeValuesRequestRequestTypeDef",
    {
        "ServiceCode": str,
        "AttributeName": str,
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
GetPriceListFileUrlRequestRequestTypeDef = TypedDict(
    "GetPriceListFileUrlRequestRequestTypeDef",
    {
        "PriceListArn": str,
        "FileFormat": str,
    },
)
TimestampTypeDef = Union[datetime, str]
PriceListTypeDef = TypedDict(
    "PriceListTypeDef",
    {
        "PriceListArn": NotRequired[str],
        "RegionCode": NotRequired[str],
        "CurrencyCode": NotRequired[str],
        "FileFormats": NotRequired[List[str]],
    },
)
DescribeServicesRequestDescribeServicesPaginateTypeDef = TypedDict(
    "DescribeServicesRequestDescribeServicesPaginateTypeDef",
    {
        "ServiceCode": NotRequired[str],
        "FormatVersion": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetAttributeValuesRequestGetAttributeValuesPaginateTypeDef = TypedDict(
    "GetAttributeValuesRequestGetAttributeValuesPaginateTypeDef",
    {
        "ServiceCode": str,
        "AttributeName": str,
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetAttributeValuesResponseTypeDef = TypedDict(
    "GetAttributeValuesResponseTypeDef",
    {
        "AttributeValues": List[AttributeValueTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetPriceListFileUrlResponseTypeDef = TypedDict(
    "GetPriceListFileUrlResponseTypeDef",
    {
        "Url": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetProductsResponseTypeDef = TypedDict(
    "GetProductsResponseTypeDef",
    {
        "FormatVersion": str,
        "PriceList": List[str],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
DescribeServicesResponseTypeDef = TypedDict(
    "DescribeServicesResponseTypeDef",
    {
        "Services": List[ServiceTypeDef],
        "FormatVersion": str,
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
GetProductsRequestGetProductsPaginateTypeDef = TypedDict(
    "GetProductsRequestGetProductsPaginateTypeDef",
    {
        "ServiceCode": str,
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "FormatVersion": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
GetProductsRequestRequestTypeDef = TypedDict(
    "GetProductsRequestRequestTypeDef",
    {
        "ServiceCode": str,
        "Filters": NotRequired[Sequence[FilterTypeDef]],
        "FormatVersion": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListPriceListsRequestListPriceListsPaginateTypeDef = TypedDict(
    "ListPriceListsRequestListPriceListsPaginateTypeDef",
    {
        "ServiceCode": str,
        "EffectiveDate": TimestampTypeDef,
        "CurrencyCode": str,
        "RegionCode": NotRequired[str],
        "PaginationConfig": NotRequired[PaginatorConfigTypeDef],
    },
)
ListPriceListsRequestRequestTypeDef = TypedDict(
    "ListPriceListsRequestRequestTypeDef",
    {
        "ServiceCode": str,
        "EffectiveDate": TimestampTypeDef,
        "CurrencyCode": str,
        "RegionCode": NotRequired[str],
        "NextToken": NotRequired[str],
        "MaxResults": NotRequired[int],
    },
)
ListPriceListsResponseTypeDef = TypedDict(
    "ListPriceListsResponseTypeDef",
    {
        "PriceLists": List[PriceListTypeDef],
        "NextToken": str,
        "ResponseMetadata": ResponseMetadataTypeDef,
    },
)
