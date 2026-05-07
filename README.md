# 📚 Books Price Intelligence Dashboard

> A full Python data pipeline project: web scraping → data cleaning → SQLite storage → interactive analytics → ML price-trend prediction — all in a Streamlit web dashboard.

---

## Objective

Collect book data (title, price, rating, availability, category) from **books.toscrape.com**, clean and store it, then display rich analytics and a simple price-prediction model through a polished web interface.

---

## Features

- **Scraping** — HTTP requests + BeautifulSoup, polite delays, descriptive User-Agent
- **Cleaning** — price to float, word rating to integer, availability normalisation, deduplication
- **Storage** — SQLite database (`data/books.db`) + CSV export (`exports/books_clean.csv`)
- **Analysis** — KPI metrics, top/bottom rankings, category summaries
- **Visualisations** — bar charts, histogram, pie chart, scatter plot (Plotly)
- **Filters** — category, rating, price range, availability
- **Prediction** — LinearRegression on avg price per page, trend direction, R²
- **Dashboard** — 5-page Streamlit app with custom CSS

---

## Technologies

| Purpose | Library |
|---|---|
| HTTP requests | `requests` |
| HTML parsing | `beautifulsoup4`, `lxml` |
| Data manipulation | `pandas` |
| Charts | `plotly` |
| Machine learning | `scikit-learn` |
| Storage | `sqlite3` (stdlib) |
| Web UI | `streamlit` |

---

## Setup

```bash
# 1. Clone or unzip the project
cd "scraping book"

# 2. (Recommended) Create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Run

```bash
streamlit run app.py
```

The browser opens automatically at `http://localhost:8501`.

---

## How to Use (Demo Guide)

1. **Home page** → Set pages slider (start with 5–10 pages for a quick demo) → click **Launch Scraping / Update Data**
2. **Dashboard** → View KPI cards and charts → Use sidebar filters to explore
3. **Data Table** → Search books → Download CSV
4. **Prediction** → View price trend chart and next-page forecast
5. **About** → Read ethical scraping statement and tech overview

---

## Project Structure

```
scraping book/
├── app.py                  # Streamlit entry point
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── scraper.py          # HTTP + BeautifulSoup scraping
│   ├── cleaner.py          # Data cleaning & normalisation
│   ├── database.py         # SQLite read/write
│   ├── analysis.py         # KPIs, rankings, summaries
│   └── prediction.py       # LinearRegression price trend
├── data/
│   └── books.db            # SQLite database (auto-created)
└── exports/
    └── books_clean.csv     # CSV export (auto-created)
```

---

## Screenshots

_Add screenshots of the dashboard here after running the app._

| Home | Dashboard | Prediction |
|---|---|---|
| _(placeholder)_ | _(placeholder)_ | _(placeholder)_ |

---

## Prediction Explanation

Because `books.toscrape.com` does not publish historical prices, the app uses **page number** as a proxy for time/order. A `LinearRegression` model is trained on the mean price per page and predicts one step forward. This is an academic demonstration of an ML workflow — not a real market forecast. The UI clearly labels this as such.

---

## Ethical Scraping

- `books.toscrape.com` is a **public sandbox** built for scraping practice
- 0.2-second sleep between requests (polite rate)
- Descriptive `User-Agent` header identifying this as a school project
- No CAPTCHA bypass, no proxies, no login
- Data used for local academic analysis only

---

## Deliverables Checklist

- [x] HTTP data collection
- [x] HTML parsing
- [x] Data cleaning (price, rating, availability, category)
- [x] SQLite storage
- [x] CSV export
- [x] Statistical analysis (min, max, avg, median, top/bottom)
- [x] Error handling (try/except, timeout, user-friendly messages)
- [x] At least 3 charts
- [x] Sidebar filters
- [x] Scraping trigger button
- [x] Export button
- [x] AI/Prediction feature
- [x] Clean, polished UI
