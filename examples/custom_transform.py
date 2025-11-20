"""
Example of custom transforms for ApiLinker.

This module demonstrates how to create custom field transformers that
can be loaded and used with ApiLinker.
"""

import re
from typing import Any, Dict, List, Optional, Union


def phone_formatter(value: Optional[str]) -> Optional[str]:
    """
    Format phone numbers to E.164 format.

    Args:
        value: Phone number string (e.g., "(123) 456-7890")

    Returns:
        E.164 formatted phone number (e.g., "+11234567890")
    """
    if not value:
        return None

    # Remove all non-digit characters
    digits = re.sub(r"\D", "", value)

    # Handle US numbers without country code
    if len(digits) == 10:
        return f"+1{digits}"

    # Add + for international format if not present
    if len(digits) > 10 and not digits.startswith("+"):
        return f"+{digits}"

    return f"+{digits}"


def slugify(value: Optional[str]) -> Optional[str]:
    """
    Convert a string to a URL-friendly slug.

    Args:
        value: String to convert

    Returns:
        URL-friendly slug
    """
    if not value:
        return None

    # Convert to lowercase
    slug = value.lower()

    # Replace spaces with hyphens
    slug = re.sub(r"\s+", "-", slug)

    # Remove special characters
    slug = re.sub(r"[^a-z0-9\-]", "", slug)

    # Remove duplicate hyphens
    slug = re.sub(r"\-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def currency_converter(
    value: Optional[Union[str, float, int]],
    from_currency: str = "USD",
    to_currency: str = "EUR",
    rates: Optional[Dict[str, float]] = None,
) -> Optional[float]:
    """
    Convert amount between currencies.

    Args:
        value: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        rates: Dictionary of exchange rates (defaults to sample rates if not provided)

    Returns:
        Converted amount
    """
    if value is None:
        return None

    # Convert string to float if necessary
    if isinstance(value, str):
        try:
            value = float(value.replace(",", ""))
        except ValueError:
            return None

    # Sample exchange rates (for demonstration only)
    default_rates = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.74,
        "CAD": 1.25,
        "JPY": 110.0,
    }

    # Use provided rates or default rates
    rates = rates or default_rates

    # Validate currencies
    if from_currency not in rates or to_currency not in rates:
        return None

    # Convert to USD first (as base currency)
    amount_usd = value / rates[from_currency]

    # Convert from USD to target currency
    return amount_usd * rates[to_currency]


def list_to_csv(value: Optional[List[Any]]) -> Optional[str]:
    """
    Convert a list to a comma-separated string.

    Args:
        value: List of items

    Returns:
        Comma-separated string
    """
    if not value:
        return None

    if not isinstance(value, list):
        return str(value)

    return ",".join(str(item) for item in value)


def csv_to_list(value: Optional[str]) -> Optional[List[str]]:
    """
    Convert a comma-separated string to a list.

    Args:
        value: Comma-separated string

    Returns:
        List of strings
    """
    if not value:
        return None

    if isinstance(value, list):
        return value

    # Split by comma and trim whitespace
    return [item.strip() for item in value.split(",")]


def address_formatter(value: Dict[str, Any]) -> str:
    """
    Format address components into a single string.

    Args:
        value: Dictionary with address components

    Returns:
        Formatted address string
    """
    if not value or not isinstance(value, dict):
        return ""

    components = []

    # Add street address
    if value.get("street"):
        components.append(value["street"])

    # Add city, state/province, postal code
    city_parts = []
    if value.get("city"):
        city_parts.append(value["city"])

    if value.get("state") or value.get("province"):
        city_parts.append(value.get("state") or value.get("province"))

    if value.get("postal_code") or value.get("zip_code"):
        city_parts.append(value.get("postal_code") or value.get("zip_code"))

    if city_parts:
        components.append(", ".join(city_parts))

    # Add country
    if value.get("country"):
        components.append(value["country"])

    return "\n".join(components)


# Example of using these transformers with ApiLinker
if __name__ == "__main__":
    from apilinker import ApiLinker

    # Create ApiLinker instance
    linker = ApiLinker()

    # Register custom transformers
    linker.mapper.register_transformer("phone_formatter", phone_formatter)
    linker.mapper.register_transformer("slugify", slugify)
    linker.mapper.register_transformer("currency_converter", currency_converter)
    linker.mapper.register_transformer("list_to_csv", list_to_csv)
    linker.mapper.register_transformer("csv_to_list", csv_to_list)
    linker.mapper.register_transformer("address_formatter", address_formatter)

    print("Custom transformers registered successfully!")
