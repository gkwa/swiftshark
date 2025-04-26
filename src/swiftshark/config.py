"""Configuration module for swiftshark."""

import dataclasses


@dataclasses.dataclass
class AppConfig:
    """Application configuration."""

    table_name: str
    region: str
    category: str
    output_format: str
    verbosity: int
    filter_discriminators: bool = False
