"""
app.py — Books Price Intelligence Dashboard
Streamlit web application entry point.
"""

import sys
from pathlib import Path

# Ensure src/ is importable regardless of launch directory
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.scraper import scrape_books
from src.cleaner import clean_books
from src.database import save_books, load_books, db_exists
from src.analysis import (
    get_kpis, top_expensive, top_cheapest, top_rated,
    category_summary, rating_distribution,
)
from src.prediction import predict_next_page_price

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Books Price Intelligence",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global font & background */
html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e3a5f 0%, #16213e 100%);
    border: 1px solid #0f3460;
    border-radius: 12px;
    padding: 16px 20px;
    color: white;
}
div[data-testid="metric-container"] label {
    color: #a0c4ff !important;
    font-size: 0.82rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 1.6rem;
    font-weight: 700;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f3460 0%, #16213e 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0e0;
}
[data-testid="stSidebar"] .stRadio label {
    color: #ffffff !important;
    font-weight: 500;
}

/* Section headers */
.section-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1e3a5f;
    border-left: 4px solid #0f3460;
    padding-left: 10px;
    margin: 24px 0 14px 0;
}

/* Info banner */
.info-banner {
    background: linear-gradient(90deg, #e8f4f8, #d0e8f2);
    border-left: 5px solid #1e88e5;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 12px 0;
    color: #1a1a2e;
}

/* Table styling */
.styled-table th {
    background-color: #1e3a5f;
    color: white;
}

/* Button override */
.stButton > button {
    background: linear-gradient(135deg, #0f3460, #1e88e5);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1.4rem;
    font-weight: 600;
    transition: opacity 0.2s;
}
.stButton > button:hover {
    opacity: 0.88;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📚 Books Intelligence")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📊 Dashboard", "🗃️ Data Table", "🔮 Prediction", "ℹ️ About"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#aaa'>Data source: books.toscrape.com<br>"
        "School project — educational use only</small>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
if page == "🏠 Home":
    st.title("📚 Books Price Intelligence Dashboard")
    st.markdown(
        "<div class='info-banner'>"
        "Welcome! This application scrapes live book data from "
        "<strong>books.toscrape.com</strong>, cleans and stores it, then "
        "provides interactive analytics and a simple price-trend prediction."
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("### What this project covers")
        features = [
            ("🌐", "HTTP scraping with requests + BeautifulSoup"),
            ("🧹", "Data cleaning: price, rating, availability"),
            ("🗄️", "SQLite storage + CSV export"),
            ("📊", "Interactive Plotly visualisations"),
            ("🔍", "Sidebar filters: category, rating, price, availability"),
            ("🔮", "LinearRegression price-trend prediction"),
            ("🖥️", "Multi-page Streamlit dashboard"),
        ]
        for icon, text in features:
            st.markdown(f"- {icon} {text}")

    with col2:
        status = "✅ Database ready" if db_exists() else "⚠️ No data yet — please scrape below"
        st.info(status)
        if db_exists():
            df_preview = load_books()
            st.metric("Books in database", len(df_preview))
            st.metric("Categories", df_preview["category"].nunique() if not df_preview.empty else 0)

    st.markdown("---")
    st.markdown("### Launch Data Collection")
    st.markdown(
        "Use the slider to choose how many catalogue pages to scrape "
        "(each page ≈ 20 books). More pages = richer analysis but longer wait."
    )

    n_pages = st.slider("Pages to scrape", min_value=1, max_value=50, value=10, step=1)
    st.caption(f"Estimated books: ~{n_pages * 20} | Estimated time: ~{n_pages * 5}–{n_pages * 8} seconds")

    if st.button("🚀 Launch Scraping / Update Data"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current, total):
            progress_bar.progress(current / total)
            status_text.text(f"Scraping page {current} of {total}…")

        with st.spinner("Scraping in progress — please wait…"):
            try:
                raw = scrape_books(max_pages=n_pages, progress_callback=update_progress)
                df_clean = clean_books(raw)

                if df_clean.empty:
                    st.error("Scraping returned no data. Check your connection.")
                else:
                    save_books(df_clean)

                    # CSV export
                    export_path = Path(__file__).parent / "exports" / "books_clean.csv"
                    export_path.parent.mkdir(parents=True, exist_ok=True)
                    df_clean.to_csv(export_path, index=False, encoding="utf-8-sig")

                    progress_bar.progress(1.0)
                    status_text.text("Done!")
                    st.success(
                        f"✅ Scraped **{len(df_clean)}** books across **{n_pages}** pages. "
                        f"Saved to database and CSV."
                    )
                    st.balloons()
            except Exception as exc:
                st.error(f"Scraping failed: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📊 Dashboard":
    st.title("📊 Analytics Dashboard")

    if not db_exists():
        st.warning("No data found. Go to **Home** and launch scraping first.")
        st.stop()

    df_full = load_books()

    # ── Sidebar filters ───────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Filters")

        categories = sorted(df_full["category"].dropna().unique().tolist())
        sel_cats = st.multiselect("Category", categories, default=categories[:])

        ratings = sorted(df_full["rating"].dropna().unique().tolist())
        sel_ratings = st.multiselect("Rating (stars)", ratings, default=ratings)

        price_min = float(df_full["price"].min())
        price_max = float(df_full["price"].max())
        sel_price = st.slider(
            "Price range (£)",
            min_value=price_min,
            max_value=price_max,
            value=(price_min, price_max),
            step=0.5,
        )

        avail_options = df_full["availability"].unique().tolist()
        sel_avail = st.multiselect("Availability", avail_options, default=avail_options)

    # Apply filters
    df = df_full[
        df_full["category"].isin(sel_cats) &
        df_full["rating"].isin(sel_ratings) &
        df_full["price"].between(sel_price[0], sel_price[1]) &
        df_full["availability"].isin(sel_avail)
    ]

    if df.empty:
        st.warning("No books match the current filters.")
        st.stop()

    # ── KPI cards ─────────────────────────────────────────────────────────────
    kpis = get_kpis(df)
    st.markdown("<div class='section-title'>Key Metrics</div>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Books", f"{kpis['total_books']:,}")
    c2.metric("Categories", kpis["total_categories"])
    c3.metric("Avg Price", f"£{kpis['avg_price']:.2f}")
    c4.metric("Median Price", f"£{kpis['median_price']:.2f}")
    c5.metric("Min / Max", f"£{kpis['min_price']:.2f} / £{kpis['max_price']:.2f}")
    c6.metric("In Stock", kpis["in_stock_count"])

    st.markdown("---")

    # ── Charts ────────────────────────────────────────────────────────────────
    cat_sum = category_summary(df)
    rat_dist = rating_distribution(df)

    # Row 1
    st.markdown("<div class='section-title'>Category Analysis</div>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        top10 = cat_sum.nlargest(10, "book_count")
        fig1 = px.bar(
            top10, x="book_count", y="category", orientation="h",
            title="Top 10 Categories by Number of Books",
            color="book_count",
            color_continuous_scale="Blues",
            labels={"book_count": "Books", "category": "Category"},
        )
        fig1.update_layout(
            yaxis={"categoryorder": "total ascending"},
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=0),
            height=380,
        )
        st.plotly_chart(fig1, width="stretch")

    with col_b:
        fig2 = px.bar(
            cat_sum.nlargest(15, "book_count"),
            x="category", y="avg_price",
            title="Average Price by Category (Top 15)",
            color="avg_price",
            color_continuous_scale="Oranges",
            labels={"avg_price": "Avg Price (£)", "category": "Category"},
        )
        fig2.update_layout(
            xaxis_tickangle=-40,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=80),
            height=380,
        )
        st.plotly_chart(fig2, width="stretch")

    # Row 2
    st.markdown("<div class='section-title'>Price & Rating Distribution</div>", unsafe_allow_html=True)
    col_c, col_d = st.columns(2)

    with col_c:
        fig3 = px.histogram(
            df, x="price", nbins=40,
            title="Price Distribution",
            color_discrete_sequence=["#1e88e5"],
            labels={"price": "Price (£)", "count": "Books"},
        )
        fig3.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=340)
        st.plotly_chart(fig3, width="stretch")

    with col_d:
        if not rat_dist.empty:
            fig4 = px.pie(
                rat_dist, values="count", names="rating_label",
                title="Rating Distribution",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                hole=0.35,
            )
            fig4.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=340)
            st.plotly_chart(fig4, width="stretch")

    # Scatter (optional)
    st.markdown("<div class='section-title'>Price vs Rating</div>", unsafe_allow_html=True)
    fig5 = px.scatter(
        df, x="rating", y="price", color="category",
        title="Price vs Rating (coloured by category)",
        labels={"rating": "Rating (stars)", "price": "Price (£)"},
        opacity=0.65,
        size_max=10,
    )
    fig5.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig5, width="stretch")

    # ── Top/Bottom tables ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("<div class='section-title'>Book Rankings</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["💰 Most Expensive", "💸 Cheapest", "⭐ Highest Rated"])

    with t1:
        st.dataframe(top_expensive(df), width="stretch", hide_index=True)
    with t2:
        st.dataframe(top_cheapest(df), width="stretch", hide_index=True)
    with t3:
        st.dataframe(top_rated(df), width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA TABLE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🗃️ Data Table":
    st.title("🗃️ Full Data Table")

    if not db_exists():
        st.warning("No data found. Go to **Home** and launch scraping first.")
        st.stop()

    df = load_books()

    # Search
    search = st.text_input("Search by title or category", "")
    if search:
        mask = (
            df["title"].str.contains(search, case=False, na=False) |
            df["category"].str.contains(search, case=False, na=False)
        )
        df = df[mask]

    st.markdown(f"Showing **{len(df)}** books")
    st.dataframe(
        df[["title", "category", "price", "rating", "availability", "page_number"]],
        width="stretch",
        hide_index=True,
        height=500,
    )

    # CSV download
    export_path = Path(__file__).parent / "exports" / "books_clean.csv"
    if export_path.exists():
        with open(export_path, "rb") as f:
            st.download_button(
                label="⬇️ Download CSV",
                data=f,
                file_name="books_clean.csv",
                mime="text/csv",
            )
    else:
        csv_bytes = df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_bytes,
            file_name="books_clean.csv",
            mime="text/csv",
        )


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PREDICTION
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "🔮 Prediction":
    st.title("🔮 Price Trend Prediction")

    st.markdown(
        "<div class='info-banner'>"
        "<strong>Academic disclaimer:</strong> This is a simplified linear model "
        "using <em>page number</em> as a proxy for time/order. "
        "Books.toscrape.com does not publish prices over time, so this is not a "
        "real market forecast — it demonstrates a machine-learning workflow for "
        "educational purposes."
        "</div>",
        unsafe_allow_html=True,
    )

    if not db_exists():
        st.warning("No data found. Go to **Home** and launch scraping first.")
        st.stop()

    df = load_books()
    result = predict_next_page_price(df)

    if not result["success"]:
        st.error(result["message"])
        st.stop()

    # ── Result cards ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Next Page", f"Page {result['next_page']}")
    col2.metric("Predicted Avg Price", f"£{result['predicted_price']}")
    col3.metric("Trend", result["trend"])
    col4.metric("Model R²", f"{result['r2']:.3f}")

    # Trend emoji
    trend_icon = {"Increasing": "📈", "Decreasing": "📉", "Stable": "➡️"}.get(result["trend"], "")
    st.markdown(
        f"<div class='info-banner'>"
        f"{trend_icon} The model predicts a <strong>{result['trend']}</strong> trend "
        f"with a slope of <strong>{result['slope']}</strong> £ per page."
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Chart ─────────────────────────────────────────────────────────────────
    page_avg = result["page_avg_df"].copy()
    next_row = pd.DataFrame(
        {"page_number": [result["next_page"]], "avg_price": [result["predicted_price"]]}
    )

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=page_avg["page_number"], y=page_avg["avg_price"],
        mode="lines+markers",
        name="Observed Avg Price",
        line=dict(color="#1e88e5", width=2),
        marker=dict(size=6),
    ))
    fig.add_trace(go.Scatter(
        x=[result["next_page"]], y=[result["predicted_price"]],
        mode="markers",
        name="Predicted (next page)",
        marker=dict(color="#e53935", size=14, symbol="star"),
    ))
    # Dashed line connecting last observed to prediction
    last_row = page_avg.iloc[-1]
    fig.add_trace(go.Scatter(
        x=[last_row["page_number"], result["next_page"]],
        y=[last_row["avg_price"], result["predicted_price"]],
        mode="lines",
        name="Projected",
        line=dict(color="#e53935", width=2, dash="dash"),
        showlegend=False,
    ))
    fig.update_layout(
        title="Average Book Price per Page (with Prediction)",
        xaxis_title="Page Number",
        yaxis_title="Average Price (£)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(l=0, r=0, t=50, b=0),
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("---")
    st.markdown("**Raw data used for training:**")
    st.dataframe(page_avg, width="stretch", hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "ℹ️ About":
    st.title("ℹ️ About This Project")

    st.markdown("""
## Books Price Intelligence Dashboard

A school project demonstrating an end-to-end Python data pipeline:
**web scraping → cleaning → storage → analysis → visualisation → prediction**.

---

### Technologies Used

| Layer | Tool |
|---|---|
| Web scraping | `requests`, `BeautifulSoup4`, `lxml` |
| Data cleaning | `pandas` |
| Storage | `SQLite3` (via Python stdlib) |
| Analysis | `pandas` |
| Visualisation | `plotly` |
| ML Prediction | `scikit-learn` (LinearRegression) |
| Web interface | `Streamlit` |

---

### Ethical Scraping Statement

- **Target site:** `books.toscrape.com` — a public sandbox created specifically for scraping practice. No real personal data is involved.
- **Politeness:** The scraper uses a 0.2-second delay between requests and a descriptive User-Agent identifying this as a school project.
- **No bypass:** No CAPTCHA solving, no proxies, no login circumvention.
- **Rate limits:** Respected via `timeout=10` and `time.sleep(0.2)`.
- **Data use:** All data is stored locally for academic analysis only.

---

### Prediction Methodology

The app uses `page_number` as a pseudo-time axis because BooksToScrape does not
publish historical prices. A `LinearRegression` model is fitted on the mean price
per page and used to extrapolate one step forward. This illustrates a typical
ML workflow (feature selection → training → inference → visualisation) in a
fully controlled, offline-safe way.

**R²** indicates how well page order explains price variance — values near 0
are expected since the catalogue ordering is not truly temporal.

---

### Project Team

- Student project — academic submission
- Data source: [books.toscrape.com](https://books.toscrape.com/)
""")
