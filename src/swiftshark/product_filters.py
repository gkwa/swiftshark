"""Product filtering module for swiftshark."""

import abc
import logging
import re
import typing


class ProductFilter(abc.ABC):
    """Abstract base class for product filters."""

    @abc.abstractmethod
    def filter(
        self, products: typing.List[typing.Dict[str, str]]
    ) -> typing.List[typing.Dict[str, str]]:
        """Filter a list of products.

        Args:
            products: List of product dictionaries

        Returns:
            Filtered list of products
        """
        pass


class DiscriminatorFilter(ProductFilter):
    """Filter to remove duplicate products that differ only by a discriminator suffix."""

    def __init__(self):
        """Initialize the discriminator filter."""
        self.logger = logging.getLogger(__name__)
        self.discriminator_pattern = re.compile(r"#\d+$")

    def filter(
        self, products: typing.List[typing.Dict[str, str]]
    ) -> typing.List[typing.Dict[str, str]]:
        """Remove duplicate products that differ only by a discriminator suffix.

        Args:
            products: List of product dictionaries

        Returns:
            Filtered list with duplicates removed
        """
        self.logger.debug(
            f"Filtering {len(products)} products for discriminator duplicates"
        )

        # Dictionary to track unique products by their base name (without discriminator)
        unique_products = {}

        for product in products:
            domain = product["domain"]
            name = product["name"]

            # Check if the name has a discriminator suffix (like #1, #2, etc.)
            base_name = self.discriminator_pattern.sub("", name)

            # Create a key using domain and base name
            product_key = f"{domain}#{base_name}"

            # If this is the first time we're seeing this product or
            # the current product doesn't have a discriminator but a previously
            # stored one does, store/replace it
            current_has_discriminator = name != base_name

            if product_key not in unique_products:
                # Store the product with its base name for reference
                product_copy = product.copy()
                product_copy["_base_name"] = base_name
                unique_products[product_key] = product_copy
            elif (
                not current_has_discriminator
                and unique_products[product_key]["name"] != base_name
            ):
                # Replace with non-discriminator version
                product_copy = product.copy()
                product_copy["_base_name"] = base_name
                unique_products[product_key] = product_copy

        # Return the list of unique products, removing the temporary '_base_name' key
        result = []
        for product in unique_products.values():
            product_copy = product.copy()
            product_copy.pop("_base_name", None)
            result.append(product_copy)

        self.logger.debug(f"Filtered to {len(result)} products")
        return result


class ProductFilterManager:
    """Manager for applying multiple product filters."""

    def __init__(self, filters: typing.List[ProductFilter] = None):
        """Initialize the filter manager.

        Args:
            filters: List of ProductFilter instances to apply
        """
        self.filters = filters or []
        self.logger = logging.getLogger(__name__)

    def add_filter(self, product_filter: ProductFilter) -> None:
        """Add a new filter to the manager.

        Args:
            product_filter: A ProductFilter instance
        """
        self.filters.append(product_filter)

    def apply_filters(
        self, products: typing.List[typing.Dict[str, str]]
    ) -> typing.List[typing.Dict[str, str]]:
        """Apply all filters to the product list.

        Args:
            products: List of product dictionaries

        Returns:
            Filtered list of products
        """
        filtered_products = products

        for product_filter in self.filters:
            filtered_products = product_filter.filter(filtered_products)

        return filtered_products
