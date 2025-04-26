"""Formatter module for output formatting."""

import logging
import typing


class OutputFormatter:
    """Formats product data for output."""

    def __init__(self, format_type: str):
        """Initialize the formatter.

        Args:
            format_type: The output format type
        """
        self.format_type = format_type
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initializing formatter with format: {format_type}")

    def format_products(
        self, category: str, products: typing.List[typing.Dict[str, str]]
    ) -> typing.List[str]:
        """Format product data based on the specified format.

        Args:
            category: The product category
            products: List of product dictionaries

        Returns:
            List of formatted output strings
        """
        if self.format_type == "category#domain#product":
            return [f"{category}#{p['domain']}#{p['name']}" for p in products]

        elif self.format_type == "domain#product":
            return [f"{p['domain']}#{p['name']}" for p in products]

        elif self.format_type == "pretty":
            formatted = []
            for p in products:
                formatted.append(f"Domain: {p['domain']}")
                formatted.append(f"Product: {p['name']}")
                formatted.append("")
            return formatted

        # Default format
        return [f"{category}#{p['domain']}#{p['name']}" for p in products]
