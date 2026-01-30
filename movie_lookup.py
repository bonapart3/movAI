"""
Movie Info Lookup Web App
Fetches movie details from OMDB and streaming availability from Streaming Availability API (RapidAPI).
Run locally: streamlit run movie_lookup.py
Deploy: Push to GitHub, deploy via streamlit.io
Requires: pip install streamlit requests
"""

import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="movAI", page_icon="🎬", layout="centered")

# API keys loaded from .streamlit/secrets.toml (local) or Streamlit Cloud secrets
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY", "")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "")

OMDB_URL = "http://www.omdbapi.com/"
STREAMING_BASE_URL = "https://streaming-availability.p.rapidapi.com/shows/"

NO_POSTER = "https://via.placeholder.com/120x178/1a1a2e/555?text=No+Poster"

# ---- Custom CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    .block-container { max-width: 800px; padding-top: 2rem; }

    .app-header {
        text-align: center;
        padding: 1.5rem 0 0.5rem 0;
    }
    .app-header h1 {
        font-family: 'Inter', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-header p {
        color: #888;
        font-size: 0.95rem;
        font-family: 'Inter', sans-serif;
    }

    .movie-card {
        background: linear-gradient(145deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2a2a4a;
        border-radius: 16px;
        padding: 1.8rem;
        margin-top: 1.5rem;
    }

    .movie-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: #f0f0f0;
        margin-bottom: 0.3rem;
    }
    .movie-meta {
        font-family: 'Inter', sans-serif;
        font-size: 0.85rem;
        color: #999;
        margin-bottom: 1rem;
    }
    .movie-meta span {
        margin-right: 1rem;
    }

    .rating-badge {
        display: inline-block;
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        color: #1a1a2e;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        margin-right: 0.5rem;
    }

    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #667eea;
        margin-bottom: 0.4rem;
        margin-top: 1.2rem;
    }

    .synopsis {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #ccc;
        line-height: 1.6;
    }

    .streaming-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.4rem;
    }
    .stream-chip {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        padding: 0.45rem 0.9rem;
        border-radius: 8px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }
    .stream-chip.subscription {
        background: rgba(72, 187, 120, 0.15);
        border: 1px solid rgba(72, 187, 120, 0.4);
        color: #68d391;
    }
    .stream-chip.free {
        background: rgba(72, 187, 120, 0.15);
        border: 1px solid rgba(72, 187, 120, 0.4);
        color: #68d391;
    }
    .stream-chip.ads {
        background: rgba(237, 137, 54, 0.15);
        border: 1px solid rgba(237, 137, 54, 0.4);
        color: #ed8936;
    }
    .stream-chip.rent {
        background: rgba(99, 179, 237, 0.15);
        border: 1px solid rgba(99, 179, 237, 0.4);
        color: #63b3ed;
    }
    .stream-chip.buy {
        background: rgba(183, 148, 244, 0.15);
        border: 1px solid rgba(183, 148, 244, 0.4);
        color: #b794f4;
    }
    .stream-chip.addon {
        background: rgba(246, 173, 85, 0.15);
        border: 1px solid rgba(246, 173, 85, 0.4);
        color: #f6ad55;
    }
    .stream-date {
        font-size: 0.75rem;
        opacity: 0.8;
    }

    .no-results {
        text-align: center;
        color: #888;
        font-family: 'Inter', sans-serif;
        padding: 2rem;
    }

    .results-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }

    div[data-testid="stTextInput"] label { display: none; }
</style>
""", unsafe_allow_html=True)


# ---- API Functions ----

def fetch_search_results(query):
    """Search OMDB for multiple matching titles."""
    resp = requests.get(
        OMDB_URL,
        params={"s": query, "apikey": OMDB_API_KEY, "type": "movie"},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("Response") == "False":
        return []
    return data.get("Search", [])


def fetch_movie_by_id(imdb_id):
    """Fetch full movie details by IMDB ID."""
    resp = requests.get(
        OMDB_URL,
        params={"i": imdb_id, "apikey": OMDB_API_KEY, "plot": "short"},
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_streaming(imdb_id):
    """Fetch streaming availability using IMDB ID."""
    if not RAPIDAPI_KEY:
        return None
    try:
        resp = requests.get(
            f"{STREAMING_BASE_URL}{imdb_id}",
            headers={
                "X-RapidAPI-Key": RAPIDAPI_KEY,
                "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com",
            },
            params={"country": "us"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


def _format_date(ts):
    """Format a Unix timestamp as 'February 3rd, 2026'."""
    dt = datetime.fromtimestamp(ts)
    day = dt.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return dt.strftime(f"%B {day}{suffix}, %Y")


def parse_streaming(data):
    """Parse Streaming Availability API response into structured list."""
    if not data:
        return []

    options = data.get("streamingOptions", {}).get("us", [])
    if not options:
        return []

    type_priority = {
        "subscription": 0, "free": 1, "ads": 2,
        "rent": 3, "buy": 4, "addon": 5,
    }
    best = {}
    now = datetime.now()

    for opt in options:
        platform = opt.get("service", {}).get("name", "Unknown")
        mtype = opt.get("type", "")
        if not mtype:
            continue

        price_obj = opt.get("price")
        price_amount = float(price_obj.get("amount", 0)) if price_obj and "amount" in price_obj else None
        if price_amount is not None:
            currency = price_obj.get("currency", "USD")
            price_formatted = f"${price_amount:.2f}" if currency == "USD" else f"{price_amount:.2f} {currency}"
        else:
            price_formatted = ""

        date_str = ""
        available_ts = opt.get("availableSince")
        expires_ts = opt.get("expiresOn")
        if available_ts and available_ts > now.timestamp():
            date_str = _format_date(available_ts)
        elif expires_ts and expires_ts > now.timestamp():
            date_str = "until " + _format_date(expires_ts)

        prio = type_priority.get(mtype, 99)
        current = best.get(platform)
        if current is None:
            best[platform] = (prio, price_amount, price_formatted, mtype, date_str)
        elif prio < current[0]:
            best[platform] = (prio, price_amount, price_formatted, mtype, date_str)
        elif prio == current[0] and price_amount is not None:
            if current[1] is None or price_amount < current[1]:
                best[platform] = (prio, price_amount, price_formatted, mtype, date_str)

    label_map = {
        "subscription": "Subscription",
        "free": "Free",
        "ads": "Free with Ads",
        "rent": "Rent",
        "buy": "Buy",
        "addon": "Add-on",
    }
    results = []
    for platform in sorted(best, key=lambda p: best[p][0]):
        prio, price_val, price_fmt, mtype, date_str = best[platform]
        results.append({
            "platform": platform,
            "type": mtype,
            "label": label_map.get(mtype, mtype.capitalize()),
            "price": price_fmt,
            "date": date_str,
        })
    return results


def truncate_plot(plot, max_sentences=3):
    """Limit plot to a few sentences."""
    if not plot or plot == "N/A":
        return plot
    sentences = plot.replace("...", ".").split(". ")
    if len(sentences) <= max_sentences:
        return plot
    truncated = ". ".join(sentences[:max_sentences])
    if not truncated.endswith("."):
        truncated += "."
    return truncated


def render_streaming_chips(options):
    """Render streaming options as styled chips."""
    if not options:
        return '<p style="color:#888; font-family:Inter,sans-serif; font-size:0.9rem;">No streaming options found.</p>'
    chips = []
    for opt in options:
        css_class = opt["type"]
        text = opt["platform"]
        detail = opt["label"]
        if opt["price"]:
            detail += f' {opt["price"]}'
        date_html = f'<span class="stream-date"> &middot; {opt["date"]}</span>' if opt["date"] else ""
        chips.append(
            f'<span class="stream-chip {css_class}">'
            f'{text} &mdash; {detail}{date_html}'
            f'</span>'
        )
    return '<div class="streaming-grid">' + "".join(chips) + '</div>'


def render_detail_card(omdb, streaming_opts):
    """Render the full movie detail card."""
    title = omdb.get("Title", "N/A")
    plot = truncate_plot(omdb.get("Plot", "N/A"))
    released = omdb.get("Released", "N/A")
    year = omdb.get("Year", "")
    rated = omdb.get("Rated", "")
    runtime = omdb.get("Runtime", "")
    genre = omdb.get("Genre", "")
    director = omdb.get("Director", "")
    imdb_rating = omdb.get("imdbRating", "")
    poster = omdb.get("Poster", "")

    meta_parts = []
    if year:
        meta_parts.append(year)
    if rated and rated != "N/A":
        meta_parts.append(rated)
    if runtime and runtime != "N/A":
        meta_parts.append(runtime)
    if genre:
        meta_parts.append(genre)

    rating_html = ""
    if imdb_rating and imdb_rating != "N/A":
        rating_html = f'<span class="rating-badge">IMDb {imdb_rating}</span>'

    director_html = ""
    if director and director != "N/A":
        director_html = f'<div style="margin-bottom:0.8rem;"><span style="color:#aaa;">Directed by {director}</span></div>'

    meta_html = " &bull; ".join(f"<span>{p}</span>" for p in meta_parts)
    streaming_html = render_streaming_chips(streaming_opts)

    poster_html = ""
    if poster and poster != "N/A":
        poster_html = f'<img src="{poster}" style="width:140px; height:auto; border-radius:10px; object-fit:cover; flex-shrink:0;" />'

    return f"""
    <div class="movie-card">
        <div style="display:flex; gap:1.5rem;">
            {poster_html}
            <div style="flex:1; min-width:0;">
                <div class="movie-title">{title}</div>
                <div class="movie-meta">{rating_html} {meta_html}</div>
                {director_html}
                <div class="section-label">Synopsis</div>
                <div class="synopsis">{plot}</div>
                <div class="section-label">Theatrical Release</div>
                <div class="synopsis">{released}</div>
            </div>
        </div>
        <div class="section-label" style="margin-top:1.4rem;">Streaming Options</div>
        {streaming_html}
    </div>
    """


# ---- Session State ----
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "selected_id" not in st.session_state:
    st.session_state.selected_id = None
if "search_query" not in st.session_state:
    st.session_state.search_query = ""


# ---- Streamlit UI ----
st.markdown(
    '<div class="app-header">'
    '<h1>movAI</h1>'
    '<p>Search any movie. Get the details. Find where to stream it.</p>'
    '</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns([5, 1])
with col1:
    movie_name = st.text_input("movie_search", placeholder="Search for a movie...", label_visibility="collapsed")
with col2:
    search_clicked = st.button("Search", use_container_width=True)

# Handle new search
if search_clicked and movie_name and movie_name.strip():
    if not OMDB_API_KEY:
        st.error("Set your OMDB API key in .streamlit/secrets.toml")
    else:
        with st.spinner(""):
            try:
                results = fetch_search_results(movie_name.strip())
                st.session_state.search_results = results
                st.session_state.selected_id = None
                st.session_state.search_query = movie_name.strip()
            except Exception:
                st.error("Could not connect. Check your internet and API keys.")
                st.session_state.search_results = []

# ---- Detail View ----
if st.session_state.selected_id:
    if st.button("← Back to results"):
        st.session_state.selected_id = None
        st.rerun()

    with st.spinner(""):
        try:
            omdb = fetch_movie_by_id(st.session_state.selected_id)
            if omdb.get("Response") == "False":
                st.markdown('<p class="no-results">Could not load movie details.</p>', unsafe_allow_html=True)
            else:
                imdb_id = omdb.get("imdbID")
                streaming_data = fetch_streaming(imdb_id) if imdb_id else None
                streaming_opts = parse_streaming(streaming_data)
                st.markdown(render_detail_card(omdb, streaming_opts), unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading details: {e}")

# ---- Results Grid ----
elif st.session_state.search_results:
    results = st.session_state.search_results
    count = len(results)
    st.markdown(
        f'<p class="results-label">{count} result{"s" if count != 1 else ""} for "{st.session_state.search_query}"</p>',
        unsafe_allow_html=True,
    )

    # Show results in rows of 5
    for row_start in range(0, len(results), 5):
        row = results[row_start:row_start + 5]
        cols = st.columns(5)
        for i, movie in enumerate(row):
            with cols[i]:
                poster = movie.get("Poster", "")
                if poster and poster != "N/A":
                    st.image(poster, use_container_width=True)
                else:
                    st.image(NO_POSTER, use_container_width=True)
                year = movie.get("Year", "")
                st.caption(f'**{movie.get("Title", "?")}**  \n{year}')
                if st.button("Select", key=f"sel_{row_start + i}", use_container_width=True):
                    st.session_state.selected_id = movie.get("imdbID")
                    st.rerun()

elif st.session_state.search_query:
    st.markdown('<p class="no-results">No movies found. Try a different title.</p>', unsafe_allow_html=True)
