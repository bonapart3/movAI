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

# API keys loaded from .streamlit/secrets.toml (local) or Streamlit Cloud secrets
OMDB_API_KEY = st.secrets.get("OMDB_API_KEY", "")
RAPIDAPI_KEY = st.secrets.get("RAPIDAPI_KEY", "")

OMDB_URL = "http://www.omdbapi.com/"
STREAMING_BASE_URL = "https://streaming-availability.p.rapidapi.com/shows/"


def fetch_movie_info(title):
    """Fetch movie details from OMDB."""
    resp = requests.get(
        OMDB_URL,
        params={"t": title, "apikey": OMDB_API_KEY, "plot": "short"},
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


def format_streaming(data):
    """Parse Streaming Availability API response into readable options."""
    if not data:
        return "Streaming information unavailable."

    # API returns show object directly; no "result" wrapper
    options = data.get("streamingOptions", {}).get("us", [])
    if not options:
        return "Not currently available for streaming in the US."

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

        # Parse availability date if present
        date_str = ""
        available_from = opt.get("availableFrom")
        if available_from:
            try:
                release_date = datetime.fromisoformat(available_from.rstrip("Z"))
                if release_date > now:
                    day = release_date.day
                    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
                    date_str = release_date.strftime(f"%B {day}{suffix}, %Y")
            except (ValueError, TypeError):
                pass

        prio = type_priority.get(mtype, 99)
        current = best.get(platform)
        if current is None:
            best[platform] = (prio, price_amount, price_formatted, mtype, date_str)
        elif prio < current[0]:
            best[platform] = (prio, price_amount, price_formatted, mtype, date_str)
        elif prio == current[0] and price_amount is not None:
            if current[1] is None or price_amount < current[1]:
                best[platform] = (prio, price_amount, price_formatted, mtype, date_str)

    lines = []
    for platform in sorted(best, key=lambda p: best[p][0]):
        prio, price_val, price_fmt, mtype, date_str = best[platform]
        label_map = {
            "subscription": "Subscription",
            "free": "Free",
            "ads": "Free with Ads",
            "rent": "Rent",
            "buy": "Buy",
            "addon": "Add-on",
        }
        label = label_map.get(mtype, mtype.capitalize())
        line = f"{platform} ({label}{' ' + price_fmt if price_fmt else ''})"
        if date_str:
            line += f" - {date_str}"
        lines.append(line)

    if not lines:
        return "Not currently available for streaming."
    return "\n  ".join(lines)


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


# ---- Streamlit UI ----
st.title("Movie Info Lookup")

movie_name = st.text_input("Enter Movie Name:")
if st.button("Search"):
    if not movie_name.strip():
        st.write("Enter a movie name.")
    elif not OMDB_API_KEY:
        st.write("Error: Please set your OMDB API key in .streamlit/secrets.toml")
    else:
        with st.spinner("Searching..."):
            try:
                omdb = fetch_movie_info(movie_name)
                if omdb.get("Response") == "False":
                    st.write("Movie not found.")
                else:
                    title = omdb.get("Title", "N/A")
                    plot = truncate_plot(omdb.get("Plot", "N/A"))
                    released = omdb.get("Released", "N/A")
                    imdb_id = omdb.get("imdbID")

                    streaming_data = fetch_streaming(imdb_id) if imdb_id else None
                    streaming = format_streaming(streaming_data)

                    st.text(
                        f"Movie Title: {title}\n"
                        f"Brief Synopsis: {plot}\n"
                        f"Theatrical Release Date: {released}\n"
                        f"Streaming Options: {streaming}"
                    )
            except requests.exceptions.RequestException:
                st.write("Error: Could not connect. Check your internet and API keys.")
            except Exception as e:
                st.write(f"Error: {e}")
