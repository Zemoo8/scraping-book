"""
analysis.py — KPI statistics and summary tables from the cleaned book DataFrame.
"""

import pandas as pd


def get_kpis(df: pd.DataFrame) -> dict:
    """Return key performance indicators as a dictionary."""
    if df.empty:
        return {}
    return {
        "total_books": len(df),
        "total_categories": df["category"].nunique(),
        "min_price": df["price"].min(),
        "max_price": df["price"].max(),
        "avg_price": df["price"].mean(),
        "median_price": df["price"].median(),
        "avg_rating": df["rating"].mean(),
        "in_stock_count": (df["availability"] == "In Stock").sum(),
    }


def top_expensive(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return (
        df[["title", "category", "price", "rating", "availability"]]
        .sort_values("price", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def top_cheapest(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return (
        df[["title", "category", "price", "rating", "availability"]]
        .sort_values("price", ascending=True)
        .head(n)
        .reset_index(drop=True)
    )


def top_rated(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    return (
        df[["title", "category", "price", "rating", "availability"]]
        .sort_values(["rating", "price"], ascending=[False, True])
        .head(n)
        .reset_index(drop=True)
    )


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return per-category book count, avg/min/max price."""
    if df.empty:
        return pd.DataFrame()
    return (
        df.groupby("category")
        .agg(
            book_count=("title", "count"),
            avg_price=("price", "mean"),
            min_price=("price", "min"),
            max_price=("price", "max"),
            avg_rating=("rating", "mean"),
        )
        .reset_index()
        .sort_values("book_count", ascending=False)
    )


def rating_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return count of books per rating value."""
    if df.empty:
        return pd.DataFrame()
    label_map = {1: "1 - Poor", 2: "2 - Fair", 3: "3 - Good", 4: "4 - Very Good", 5: "5 - Excellent"}
    dist = (
        df["rating"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "rating", "count": "count"})
    )
    # Ensure correct column names regardless of pandas version
    dist.columns = ["rating", "count"]
    dist["rating_label"] = dist["rating"].map(label_map)
    return dist.sort_values("rating")
