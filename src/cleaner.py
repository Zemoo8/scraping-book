"""
cleaner.py — Cleans and normalises raw scraped book data.
"""

import re
import pandas as pd

RATING_MAP = {
    "One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5,
    "Zero": 0,
}


def _parse_price(price_text: str) -> float:
    """Convert '£51.77' (any encoding of £) to a float by keeping only digits and dot."""
    try:
        digits_only = re.sub(r"[^\d.]", "", str(price_text))
        return float(digits_only) if digits_only else 0.0
    except (ValueError, AttributeError):
        return 0.0


def _parse_rating(rating_text: str) -> int:
    """Convert word rating ('Three') to integer."""
    return RATING_MAP.get(str(rating_text).strip(), 0)


def _parse_availability(avail_text: str) -> str:
    """Normalize availability string."""
    text = str(avail_text).strip()
    if "In stock" in text:
        return "In Stock"
    if "Out of stock" in text:
        return "Out of Stock"
    return text


def clean_books(raw_books: list[dict]) -> pd.DataFrame:
    """
    Takes raw book dicts from the scraper and returns a clean DataFrame.
    Applies price conversion, rating mapping, availability normalisation,
    duplicate removal, and drops rows with missing critical fields.
    """
    if not raw_books:
        return pd.DataFrame()

    df = pd.DataFrame(raw_books)

    df["price"] = df["price_text"].apply(_parse_price)
    df["rating"] = df["rating_text"].apply(_parse_rating)
    df["availability"] = df["availability"].apply(_parse_availability)

    # Strip extra whitespace from text fields
    for col in ["title", "category", "product_url", "image_url"]:
        if col in df.columns:
            df[col] = df[col].str.strip()

    # Drop helper columns
    df.drop(columns=["price_text", "rating_text"], inplace=True, errors="ignore")

    # Remove duplicates (same URL = same book)
    df.drop_duplicates(subset=["product_url"], inplace=True)

    # Drop rows missing critical fields
    df.dropna(subset=["title", "price"], inplace=True)
    df = df[df["price"] > 0]

    df.reset_index(drop=True, inplace=True)
    return df
