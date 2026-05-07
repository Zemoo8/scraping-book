"""
scraper.py — Fetches book data from https://books.toscrape.com/
Respects robots.txt, uses polite delays, descriptive User-Agent.
"""

import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; BooksScraperBot/1.0; "
        "school-project; books.toscrape.com)"
    )
}
TIMEOUT = 10
SLEEP_BETWEEN_REQUESTS = 0.3


def _get(url: str) -> BeautifulSoup | None:
    """Fetch a URL and return a BeautifulSoup object, or None on failure."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")
    except requests.RequestException as e:
        print(f"[scraper] Request failed for {url}: {e}")
        return None


def _get_category_from_detail(product_url: str, cache: dict) -> str:
    """Visit a book's detail page to extract its category. Results are cached."""
    if product_url in cache:
        return cache[product_url]
    soup = _get(product_url)
    time.sleep(SLEEP_BETWEEN_REQUESTS)
    if soup is None:
        cache[product_url] = "Unknown"
        return "Unknown"
    breadcrumbs = soup.select("ul.breadcrumb li")
    # Breadcrumb order: Home > Category > Book Title
    if len(breadcrumbs) >= 3:
        category = breadcrumbs[-2].get_text(strip=True)
    else:
        category = "Unknown"
    cache[product_url] = category
    return category


def scrape_books(max_pages: int = 10, progress_callback=None) -> list[dict]:
    """
    Scrape books from BooksToScrape for up to max_pages pages.
    Returns a list of raw book dicts (pre-cleaning).
    progress_callback(current, total) is called after each page if provided.
    """
    books = []
    category_cache: dict[str, str] = {}

    for page_num in range(1, max_pages + 1):
        if page_num == 1:
            page_url = BASE_URL
        else:
            page_url = f"{BASE_URL}catalogue/page-{page_num}.html"

        if progress_callback:
            progress_callback(page_num, max_pages)

        soup = _get(page_url)
        if soup is None:
            print(f"[scraper] Skipping page {page_num} — failed to fetch.")
            continue

        articles = soup.select("article.product_pod")
        if not articles:
            print(f"[scraper] No books found on page {page_num}. Stopping.")
            break

        for article in articles:
            title_tag = article.select_one("h3 a")
            title = title_tag["title"] if title_tag else "N/A"

            price_tag = article.select_one("p.price_color")
            price_text = price_tag.get_text(strip=True) if price_tag else "£0"

            rating_tag = article.select_one("p.star-rating")
            rating_text = rating_tag["class"][1] if rating_tag else "Zero"

            avail_tag = article.select_one("p.availability")
            availability = avail_tag.get_text(strip=True) if avail_tag else "Unknown"

            # Build absolute product URL using urljoin to handle relative paths correctly
            raw_href = title_tag["href"] if title_tag else ""
            product_url = urljoin(page_url, raw_href)

            # Build absolute image URL
            img_tag = article.select_one("img")
            img_src = img_tag["src"] if img_tag else ""
            image_url = urljoin(page_url, img_src)

            # Category from detail page (cached to avoid redundant requests)
            category = _get_category_from_detail(product_url, category_cache)
            time.sleep(SLEEP_BETWEEN_REQUESTS)

            books.append({
                "title": title,
                "price_text": price_text,
                "rating_text": rating_text,
                "availability": availability,
                "product_url": product_url,
                "image_url": image_url,
                "page_number": page_num,
                "category": category,
            })

        print(f"[scraper] Page {page_num}/{max_pages} — {len(articles)} books collected.")
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    print(f"[scraper] Done. Total raw books collected: {len(books)}")
    return books
