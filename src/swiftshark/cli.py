"""Command-line interface for swiftshark."""

import argparse
import logging
import sys

import swiftshark.config
import swiftshark.dynamodb_service
import swiftshark.formatter
import swiftshark.logger


def setup_args():
    """Set up and parse command line arguments."""
    parser = argparse.ArgumentParser(description="Fetch product data from DynamoDB")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Categories command (renamed from fetch)
    categories_parser = subparsers.add_parser(
        "categories", aliases=["cat"], help="Fetch products for a category"
    )
    categories_parser.add_argument(
        "category", help="Product category to fetch", nargs="+"
    )
    categories_parser.add_argument(
        "--table", help="DynamoDB table name", default="dreamydungbeetle"
    )
    categories_parser.add_argument("--region", help="AWS region", default="us-east-1")
    categories_parser.add_argument(
        "--format",
        help="Output format",
        choices=["category#domain#product", "domain#product", "pretty", "json"],
        default="category#domain#product",
    )
    categories_parser.add_argument(
        "--out",
        help="Output format (alias for --format)",
        choices=["category#domain#product", "domain#product", "pretty", "json"],
    )
    categories_parser.add_argument(
        "--no-discriminators",
        action="store_true",
        help="Filter out products with discriminator suffixes (e.g., #1, #2)",
        default=False,
    )

    # Common arguments
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase verbosity (can be used multiple times)",
    )

    return parser.parse_args()


def main():
    """Entry point for the application."""
    args = setup_args()

    # Configure logging based on verbosity level
    verbosity_level = swiftshark.logger.setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    if not args.command:
        logger.error(
            "No command specified. Use 'swiftshark categories' to fetch products."
        )
        sys.exit(1)

    # Handle both "categories" and its alias "cat"
    if args.command in ["categories", "cat"]:
        # Join the category words if they were passed as separate arguments
        category = " ".join(args.category)

        # Use --out if provided, otherwise use --format
        output_format = args.out if args.out else args.format

        config = swiftshark.config.AppConfig(
            table_name=args.table,
            region=args.region,
            category=category,
            output_format=output_format,
            verbosity=verbosity_level,
            filter_discriminators=args.no_discriminators,
        )

        logger.debug(f"Configuration: {config}")

        try:
            dynamodb_service = swiftshark.dynamodb_service.DynamoDBService(
                table_name=config.table_name,
                region=config.region,
                filter_discriminators=config.filter_discriminators,
            )

            products = dynamodb_service.fetch_products_by_category(config.category)

            if not products:
                logger.warning(f"No products found for category: {config.category}")
                sys.exit(0)

            logger.info(
                f"Found {len(products)} products for category: {config.category}"
            )

            formatter = swiftshark.formatter.OutputFormatter(config.output_format)
            formatted_output = formatter.format_products(config.category, products)

            # Print to stdout (only output on successful execution)
            for line in formatted_output:
                print(line)

        except Exception as e:
            logger.error(f"Error fetching products: {e}")
            sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
