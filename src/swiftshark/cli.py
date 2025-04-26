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

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch products for a category")
    fetch_parser.add_argument("category", help="Product category to fetch")
    fetch_parser.add_argument(
        "--table", help="DynamoDB table name", default="dreamydungbeetle"
    )
    fetch_parser.add_argument("--region", help="AWS region", default="us-east-1")
    fetch_parser.add_argument(
        "--format",
        help="Output format",
        choices=["category#domain#product", "domain#product", "pretty"],
        default="category#domain#product",
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
        logger.error("No command specified. Use 'swiftshark fetch' to fetch products.")
        sys.exit(1)

    if args.command == "fetch":
        config = swiftshark.config.AppConfig(
            table_name=args.table,
            region=args.region,
            category=args.category,
            output_format=args.format,
            verbosity=verbosity_level,
        )

        logger.debug(f"Configuration: {config}")

        try:
            dynamodb_service = swiftshark.dynamodb_service.DynamoDBService(
                table_name=config.table_name, region=config.region
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
