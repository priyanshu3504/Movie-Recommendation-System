import streamlit as st
import pickle
import requests
import pandas as pd

import os
from dotenv import load_dotenv
load_dotenv()


# ─────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide",
)

# ─────────────────────────────────────────────
#  Custom CSS  – cinematic dark theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root palette ── */
:root {
    --bg:        #0b0c10;
    --surface:   #14151a;
    --card:      #1c1d25;
    --accent:    #e5383b;
    --accent2:   #ff6b35;
    --gold:      #f4c430;
    --text:      #e8e8f0;
    --muted:     #6b6c7e;
    --border:    rgba(255,255,255,0.07);
}

/* ── Global ── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Main wrapper ── */
.main .block-container {
    padding: 2rem 3rem 4rem !important;
    max-width: 1200px;
}

/* ── Hero heading ── */
.hero {
    text-align: center;
    padding: 3.5rem 0 2.5rem;
    position: relative;
}
.hero::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 200px;
    background: radial-gradient(ellipse at center,
        rgba(229,56,59,0.18) 0%, transparent 70%);
    pointer-events: none;
}
.hero-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.35em;
    color: var(--accent);
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: clamp(3rem, 8vw, 6.5rem);
    line-height: 0.95;
    color: var(--text);
    letter-spacing: 0.04em;
    margin: 0;
}
.hero-title span {
    color: var(--accent);
}
.hero-sub {
    margin-top: 1rem;
    color: var(--muted);
    font-size: 1rem;
    font-weight: 300;
}

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent, var(--accent), var(--accent2), transparent);
    margin: 0 auto 2.5rem;
    max-width: 500px;
    opacity: 0.6;
}

/* ── Search card ── */
.search-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    max-width: 680px;
    margin: 0 auto 2.5rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.45);
}

/* ── Streamlit selectbox overrides ── */
[data-testid="stSelectbox"] > div > div {
    background: var(--card) !important;
    border: 1px solid rgba(229,56,59,0.4) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stSelectbox"] label {
    color: var(--text) !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 0.4rem !important;
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    letter-spacing: 0.08em !important;
    padding: 0.65rem 2.2rem !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 20px rgba(229,56,59,0.35) !important;
    width: 100% !important;
    margin-top: 1rem !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(229,56,59,0.5) !important;
}

/* ── Section heading ── */
.section-heading {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    letter-spacing: 0.1em;
    color: var(--text);
    text-align: center;
    margin-bottom: 1.5rem;
}
.section-heading span { color: var(--accent); }

/* ── Movie cards row ── */
.movie-grid {
    display: flex;
    gap: 1.2rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 1rem;
}
.movie-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    overflow: hidden;
    width: 180px;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    flex-shrink: 0;
}
.movie-card:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 16px 40px rgba(229,56,59,0.25);
}
.movie-card img {
    width: 100%;
    height: 265px;
    object-fit: cover;
    display: block;
}
.movie-card-info {
    padding: 0.75rem 0.8rem;
}
.movie-card-title {
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--text);
    line-height: 1.35;
    text-align: center;
}
.rank-badge {
    display: inline-block;
    background: var(--accent);
    color: #fff;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    padding: 2px 8px;
    border-radius: 20px;
    margin-bottom: 0.35rem;
}

/* ── Spinner override ── */
[data-testid="stSpinner"] { color: var(--accent) !important; }

/* ── Error / info ── */
[data-testid="stAlert"] {
    background: rgba(229,56,59,0.1) !important;
    border: 1px solid rgba(229,56,59,0.3) !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  Load data
# ─────────────────────────────────────────────
@st.cache_resource
def load_data():
    movies = pickle.load(open("movie_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    return movies, similarity

try:
    movies, similarity = load_data()
except FileNotFoundError as e:
    st.error(f"Could not load model files: {e}. Make sure `movie_list.pkl` and `similarity.pkl` are in the same directory.")
    st.stop()


# ─────────────────────────────────────────────
#  TMDB API helper
#  👉  Replace YOUR_API_KEY_HERE with your key
# ─────────────────────────────────────────────
TMDB_API_KEY = os.getenv("API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

# Reliable inline SVG fallback (no external request needed)
FALLBACK_POSTER = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "width='500' height='750' viewBox='0 0 500 750'%3E"
    "%3Crect width='500' height='750' fill='%231c1d25'/%3E"
    "%3Ctext x='50%25' y='45%25' font-family='sans-serif' font-size='48' "
    "fill='%23e5383b' text-anchor='middle'%3E🎬%3C/text%3E"
    "%3Ctext x='50%25' y='57%25' font-family='sans-serif' font-size='20' "
    "fill='%236b6c7e' text-anchor='middle'%3ENo Poster%3C/text%3E"
    "%3C/svg%3E"
)

@st.cache_data(ttl=3600)
def fetch_poster(movie_id: int) -> str:
    """Return poster URL for a given TMDB movie_id."""
    import time
    time.sleep(0.25)              # 250 ms gap — stays well under TMDB's 40 req/10s limit
    try:
        url = TMDB_BASE_URL.format(movie_id, TMDB_API_KEY)
        response = requests.get(url, timeout=8)
        if response.status_code == 429:          # rate-limited — wait and retry once
            time.sleep(2)
            response = requests.get(url, timeout=8)
        if response.status_code != 200:
            return FALLBACK_POSTER
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return POSTER_BASE_URL + poster_path
    except Exception:
        pass
    return FALLBACK_POSTER


# ─────────────────────────────────────────────
#  Recommendation logic
# ─────────────────────────────────────────────
def recommend(movie_title: str):
    """Return list of (title, poster_url) for top-5 similar movies."""
    idx = movies[movies["title"] == movie_title].index[0]
    distances = sorted(
        list(enumerate(similarity[idx])),
        reverse=True,
        key=lambda x: x[1],
    )
    # Collect movie info first
    top5 = []
    for i in distances[1:6]:          # skip index 0 (the movie itself)
        movie_id = movies.iloc[i[0]].movie_id
        title    = movies.iloc[i[0]].title
        top5.append((title, movie_id))

    # Fetch posters sequentially (0.25s apart) to avoid rate limiting
    results = []
    for title, movie_id in top5:
        poster = fetch_poster(movie_id)
        results.append((title, poster))
    return results


# ─────────────────────────────────────────────
#  UI
# ─────────────────────────────────────────────

# ── Hero ──────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-label">✦ AI-Powered Discovery ✦</div>
    <h1 class="hero-title">Movie<br><span>Recommender</span></h1>
    <p class="hero-sub">Find your next favourite film in seconds</p>
</div>
<div class="divider"></div>
""", unsafe_allow_html=True)

# ── Search card ───────────────────────────────
st.markdown('<div class="search-card">', unsafe_allow_html=True)

movie_list = movies["title"].values
selected_movie = st.selectbox(
    "🎬  Search or select a movie",
    movie_list,
    index=None,
    placeholder="Type a movie name…",
)

recommend_btn = st.button("✦  Get Recommendations")

st.markdown('</div>', unsafe_allow_html=True)

# ── Results ───────────────────────────────────
if recommend_btn:
    if not selected_movie:
        st.warning("Please select a movie first.")
    else:
        st.markdown(
            f'<div class="section-heading">Because you liked <span>{selected_movie}</span></div>',
            unsafe_allow_html=True,
        )

        with st.spinner("Fetching recommendations…"):
            recommendations = recommend(selected_movie)

        # Build HTML movie grid
        cards_html = '<div class="movie-grid">'
        for rank, (title, poster) in enumerate(recommendations, start=1):
            cards_html += f"""
            <div class="movie-card">
                <img src="{poster}" alt="{title}"
                     onerror="this.onerror=null;this.src='https://placehold.co/500x750/1c1d25/e5383b?text=No+Poster';"/>
                <div class="movie-card-info">
                    <div style="text-align:center">
                        <span class="rank-badge">#{rank}</span>
                    </div>
                    <div class="movie-card-title">{title}</div>
                </div>
            </div>"""
        cards_html += '</div>'

        st.markdown(cards_html, unsafe_allow_html=True)
