"""DynamoDB service module for interacting with AWS DynamoDB."""

import logging
import typing

import boto3

import swiftshark.product_filters


class DynamoDBService:
    """Service for interacting with DynamoDB."""

    def __init__(
        self, table_name: str, region: str, filter_discriminators: bool = False
    ):
        """Initialize the DynamoDB service.

        Args:
            table_name: Name of the DynamoDB table
            region: AWS region name
            filter_discriminators: Whether to filter out products with discriminator suffixes
        """
        self.table_name = table_name
        self.region = region
        self.filter_discriminators = filter_discriminators
        self.logger = logging.getLogger(__name__)
        self.dynamodb = boto3.client("dynamodb", region_name=region)

        # Initialize filter manager only if discriminator filtering is enabled
        self.filter_manager = None
        if self.filter_discriminators:
            self.filter_manager = swiftshark.product_filters.ProductFilterManager(
                [swiftshark.product_filters.DiscriminatorFilter()]
            )

    def fetch_products_by_category(
        self, category: str
    ) -> typing.List[typing.Dict[str, str]]:
        """Fetch all products for a given category.

        Args:
            category: The product category to query

        Returns:
            A list of product dictionaries with domain and name keys
        """
        self.logger.debug(f"Querying DynamoDB for category: {category}")

        paginator = self.dynamodb.get_paginator("query")
        page_iterator = paginator.paginate(
            TableName=self.table_name,
            KeyConditionExpression="category = :cat",
            ExpressionAttributeValues={":cat": {"S": category}},
            ProjectionExpression="category, #dom, #nm, #ts, #url",
            ExpressionAttributeNames={
                "#dom": "domain",
                "#nm": "name",
                "#ts": "timestamp",
                "#url": "url",
            },
        )

        products = []
        for page in page_iterator:
            for item in page.get("Items", []):
                product_data = {
                    "domain": item.get("domain", {}).get("S", "unknown"),
                    "name": item.get("name", {}).get("S", "unknown"),
                    "timestamp": item.get("timestamp", {}).get("S", ""),
                    "url": item.get("url", {}).get("S", ""),
                }
                products.append(product_data)

        self.logger.debug(f"Found {len(products)} products for category: {category}")

        # Apply filters to products if discriminator filtering is enabled
        if self.filter_discriminators and self.filter_manager:
            filtered_products = self.filter_manager.apply_filters(products)
            self.logger.debug(
                f"After filtering: {len(filtered_products)} unique products"
            )
            return filtered_products

        return products
