import streamlit as st
from auth import try_login, try_signup
from tmdb import (
    trending,
    search_movies,
    search_person,
    person_movie_credits,
    genres,
    discover_by_genre,
    movie_details,
    movie_videos,
    poster_url,
)
import textwrap
import base64
from pathlib import Path
import os

st.set_page_config(page_title="Movie Explorer", page_icon="🎬", layout="wide")

# ---------------- Background helpers ----------------
def get_base64_image_str(image_path: str) -> str:
    p = Path(image_path)
    if not p.exists():
        return ""
    try:
        return base64.b64encode(p.read_bytes()).decode()
    except Exception:
        return ""

def background_css_for_source(source: str) -> str:
    # This helper previously injected a background-image from a URL or local file.
    # For privacy/consistency we avoid injecting external images and instead
    # return a neutral gradient background CSS when a source is provided.
    if not source:
        return ""

    css = """
    <style>
    .stApp {
        /* Use a neutral, dark gradient instead of an image */
        background: linear-gradient(180deg, #071225 0%, #021021 100%) !important;
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        min-height: 100vh;
    }
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.35);
        pointer-events: none;
    }
    </style>
    """
    return css

def set_background(image_source: str):
    css = background_css_for_source(image_source)
    if css:
        st.markdown(css, unsafe_allow_html=True)

# ---------------- Mode-based backgrounds ----------------

# Map UI modes to background image sources. Empty strings mean no image.
MODE_BACKGROUNDS = {
    "Trending": "",
    "Search": "",
    "Actor": "",
    "Genre": "",
}

AUTH_BACKGROUND = ""

# ---------------- Base UI CSS ----------------
base_ui_css = """
<style>
/* full screen background (image removed - use gradient) */
.stApp {
    background: linear-gradient(180deg, #071225 0%, #021021 100%);
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    min-height: 100vh;
}

/* center wrapper */
.login-center-wrapper {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* login card */
.login-card {
  background: rgba(0,0,0,0.55) !important;
  border-radius: 10px !important;
  padding: 12px 14px !important;   /* less padding */
  max-width: 300px !important;     /* smaller width */
}


/* shrink inputs inside card */
.login-card .stTextInput, 
.login-card .stTextInput > div {
  max-width: 100% !important;
}

.login-card .stTextInput > div > div > input {
  border-radius: 20px;
  padding: 10px 14px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  border: none;
}

/* button inside card */
.login-card .stButton > button {
  width: 100%;
  margin-top: 12px;
  border-radius: 20px;
  background: #6a0dad;
  color: #fff;
  font-weight: 600;
  border: none;
  padding: 10px;
}

/* Movie details sizing (increased for readability) */
.movie-details {
    font-size: 26px;
    line-height: 2.0;
    color: #f5f7fb;
    max-width: 980px; /* keep long overviews readable */
}
.movie-details h2 {
    font-size: 64px;
    margin-bottom: 14px;
    font-weight: 800;
}
.movie-details .meta {
    font-size: 24px;
    color: rgba(255,255,255,0.98);
    margin-bottom: 14px;
    display: flex;
    gap: 14px;
    align-items: baseline;
}
.movie-details .meta .label {
    font-weight: 800;
    min-width: 140px;
    color: rgba(255,255,255,0.95);
}
.movie-details .meta .value { font-weight:700; color: rgba(245,247,251,0.98); }
.movie-details p.overview { font-size: 22px; color: rgba(245,247,251,0.96); }

/* Responsive adjustments: scale down on small screens */
@media (max-width: 1200px) {
    .movie-details { font-size: 20px; max-width: 760px; }
    .movie-details h2 { font-size: 44px; }
    .movie-details .meta { font-size: 18px; }
    .movie-details p.overview { font-size: 18px; }
}

@media (max-width: 768px) {
    .movie-details { font-size: 16px; max-width: 100%; }
    .movie-details h2 { font-size: 28px; }
    .movie-details .meta { font-size: 14px; display:block; gap:6px; }
    .movie-details p.overview { font-size: 15px; }
}

.login-card .stButton > button:hover {
  background: #8a2be2;
}

/* hide Streamlit header */
header[role="banner"] { display: none; }
</style>

"""
st.markdown(base_ui_css, unsafe_allow_html=True)

# Right-side movie card styling (listing cards on browse pages)
card_right_css = """
<style>
/* larger right-side card text */
.card-title { font-size: 40px !important; font-weight: 800 !important; color: #fff !important; margin: 0 0 8px 0 !important; }
.card-meta { font-size: 20px !important; color: rgba(255,255,255,0.95) !important; margin-bottom: 10px !important; }
.card-overview { font-size: 18px !important; color: rgba(245,247,251,0.95) !important; }

@media (max-width: 1400px) {
    .card-title { font-size: 34px !important; }
    .card-meta { font-size: 18px !important; }
    .card-overview { font-size: 16px !important; }
}

@media (max-width: 1024px) {
    .card-title { font-size: 28px !important; }
    .card-meta, .card-overview { font-size: 15px !important; }
}
/* Sidebar: increase Browse header and radio labels */
section[data-testid="stSidebar"] .sidebar-title,
div[data-testid="stSidebar"] .sidebar-title,
.stSidebar .sidebar-title,
.sidebar .sidebar-title {
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #fff !important;
    margin-bottom: 10px !important;
}

section[data-testid="stSidebar"] label,
div[data-testid="stSidebar"] label,
.stSidebar label,
.sidebar label,
section[data-testid="stSidebar"] .stRadio,
div[data-testid="stSidebar"] .stRadio {
    font-size: 18px !important;
    color: rgba(255,255,255,0.95) !important;
}
</style>
"""
st.markdown(card_right_css, unsafe_allow_html=True)

# ---------------- Login background + centered card (fixed) ----------------
# Use the Windows path you provided
AUTH_IMAGE_PATH_WINDOWS = r"C:\Users\aelil\OneDrive\Desktop\Arasa\assets\bg_login.jpg"

def inject_login_background_and_center_card(image_path: str):
    """
    Safe CSS injector:
     - embeds local background image (if present)
     - centers a fixed-width login card (300px) and prevents Streamlit children from stretching
     - DOES NOT hide the rest of Streamlit content (no aggressive display:none rules)
    Replace any previous injector with this exact function.
    """
    bg_url = ""
    try:
        p = Path(image_path)
        if p.exists():
            b64 = base64.b64encode(p.read_bytes()).decode()
            mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
            bg_url = f"data:{mime};base64,{b64}"
    except Exception:
        bg_url = ""

    css_template = """
    <style id="login-css-safe">
    /* MARKER: INJECT_LOGIN_CSS_DONE */

    /* Page reset that avoids forcing display:none on other blocks */
    html, body, .stApp, .appview-container, .main, .block-container {
      height: 100vh !important;
      width: 100% !important;
      margin: 0 !important;
      padding: 0 !important;
      overflow: auto !important; /* allow normal scrolling if needed */
      box-sizing: border-box !important;
    }
    .block-container { padding-top: 0 !important; padding-left: 0 !important; padding-right: 0 !important; }

    /* Background */
        /* Use a neutral gradient background instead of images */
        .stApp {
            background: linear-gradient(180deg, #071225 0%, #021021 100%) !important;
            min-height: 100vh !important;
        }
        .stApp::before { content: "" !important; position: fixed !important; inset: 0 !important;
                                         background: rgba(0,0,0,0.00) !important; pointer-events: none !important; }

    /* Center wrapper: centers the card without hiding other page elements */
    .login-center-wrapper {
      position: fixed !important;
      left: 50% !important;
      top: 50% !important;
      transform: translate(-50%, -50%) !important;
      width: 100% !important;
      display: flex !important;
      justify-content: center !important;
      align-items: center !important;
      z-index: 2147483647 !important;
      pointer-events: auto !important;
      pointer-events: none; /* let underlying page interactions work unless over the card */
    }

    /* Card styling: fixed width and centered */
    .login-card {
      width: 300px !important;
      max-width: 300px !important;
      background: rgba(0,0,0,0.65) !important;
      color: #fff !important;
      border-radius: 12px !important;
      padding: 12px 14px !important;
      box-shadow: 0 12px 36px rgba(0,0,0,0.65) !important;
      margin: 0 auto !important;
      text-align: center !important;
      border: 1px solid rgba(255,255,255,0.03) !important;
      box-sizing: border-box !important;
      pointer-events: auto !important; /* make the card interactive */
    }

    /* Ensure Streamlit children inside the card do not stretch beyond card */
    .login-card .stForm,
    .login-card form,
    .login-card .stTextInput,
    .login-card .stTextInput > div,
    .login-card .stButton,
    .login-card .stCheckbox,
    .login-card .stRadio,
    .login-card .stSelectbox {
      width: 100% !important;
      max-width: 100% !important;
      margin-left: auto !important;
      margin-right: auto !important;
      box-sizing: border-box !important;
      display: block !important;
    }

    /* Input styling */
    .login-card .stTextInput > div > div > input,
    .login-card .stTextInput > div > div > textarea {
      width: 100% !important;
      box-sizing: border-box !important;
      border-radius: 14px !important;
      padding: 10px 12px !important;
      background: rgba(255,255,255,0.06) !important;
      color: #fff !important;
      border: 1px solid rgba(255,255,255,0.06) !important;
      height: 40px !important;
      font-size: 14px !important;
    }

    /* Buttons full width inside card */
    .login-card .stButton > button {
      width: 100% !important;
      border-radius: 12px !important;
      padding: 10px 12px !important;
      margin-top: 10px !important;
      background: linear-gradient(90deg,#7b2cff 0%,#4b61ff 100%) !important;
      color: #fff !important;
      border: none !important;
      font-weight: 600 !important;
    }

    /* small logo spacing */
    .login-card .logo-row { margin-bottom: 6px !important; display:flex; justify-content:center; gap:8px; align-items:center; }
    .login-card .logo-text { font-weight:700 !important; font-size:1rem !important; color:#fff !important; }

    /* keep header visible if you prefer; comment out the next line to show Streamlit header */
    header[role="banner"] { display: none !important; }

    @media (max-width: 360px) {
      .login-card { width: calc(100% - 24px) !important; max-width: calc(100% - 24px) !important; }
    }
    </style>
    """
    css = css_template
    st.markdown(css, unsafe_allow_html=True)
    st.markdown("<!-- INJECT_LOGIN_CSS_DONE -->", unsafe_allow_html=True)




# ---------------- Session helpers ----------------
def set_logged_in(user):
    st.session_state["user"] = user

def is_logged_in():
    return "user" in st.session_state and st.session_state["user"]

# --------------- AUTH UI (labels fixed for accessibility) ------------------
def login_signup_ui():
    """
    Renders the centered, fixed-width login card and forms.
    Replace the old login_signup_ui() with this to ensure the card wrapper is used.
    """
    # Inject CSS/background
    inject_login_background_and_center_card(AUTH_IMAGE_PATH_WINDOWS)

    # Start wrapper + card
    st.markdown('<div class="login-center-wrapper">', unsafe_allow_html=True)
    st.markdown('<div class="login-card">', unsafe_allow_html=True)

    # small inline logo/title (tight)
    st.markdown(
        """
        <div class="logo-row">
          <div style="width:24px;height:24px;border-radius:6px;background:rgba(255,255,255,0.06);display:inline-block;margin-right:8px;"></div>
          <div class="logo-text">Movie Explorer</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tabs for Login / Signup
    tabs = st.tabs(["Log in", "Sign up"])

    # --- Log in tab ---
    with tabs[0]:
        with st.form("login_form", clear_on_submit=False):
            # email (label collapsed for accessibility)
            st.markdown('<div class="stTextInput login-username">', unsafe_allow_html=True)
            email = st.text_input("Email", key="login_email", placeholder="Username or email", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            # password
            st.markdown('<div class="stTextInput login-password">', unsafe_allow_html=True)
            password = st.text_input("Password", type="password", key="login_password", placeholder="Password", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)

            # checkbox + forgot
            col1, col2 = st.columns([1, 1])
            with col1:
                st.checkbox("Remember me", key="remember_me")
            with col2:
                st.markdown("<div style='text-align:right;'><a href='#' style='color:rgba(255,255,255,0.9);font-size:0.9rem;'>Forgot?</a></div>", unsafe_allow_html=True)

            # submit
            submitted = st.form_submit_button("Log in")
            if submitted:
                ok, res = try_login(email, password)
                if ok:
                    set_logged_in(res)
                    st.rerun()
                else:
                    st.error(res)

    # --- Sign up tab ---
    with tabs[1]:
        with st.form("signup_form", clear_on_submit=False):
            name = st.text_input("Full name", key="signup_name", placeholder="Your name", label_visibility="collapsed")
            email2 = st.text_input("Email", key="signup_email", placeholder="you@example.com", label_visibility="collapsed")
            password2 = st.text_input("Password", type="password", key="signup_password", placeholder="Create a password", label_visibility="collapsed")
            confirm = st.text_input("Confirm password", type="password", key="signup_confirm", placeholder="Confirm password", label_visibility="collapsed")

            submitted2 = st.form_submit_button("Create account")
            if submitted2:
                ok, res = try_signup(email2, name, password2, confirm)
                if ok:
                    set_logged_in({"name": name, "email": email2})
                    st.rerun()
                else:
                    st.error(res)

    # Close card + wrapper
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    # debug marker
    st.markdown("<!-- LOGIN_UI_RENDERED -->", unsafe_allow_html=True)



# -------------- Browse UI & helpers (unchanged) -------------------
def movie_card(movie, key_prefix=""):
    mtitle = movie.get("title") or movie.get("original_title") or "Untitled"
    poster = poster_url(movie.get("poster_path"))
    col1, col2 = st.columns([1, 3])
    with col1:
        if poster:
            # Try to find a YouTube trailer for this movie. If found, make the poster a clickable
            # link that opens the trailer (so tapping the poster plays the trailer).
            try:
                vids = movie_videos(movie.get("id"))
                yt = next((v for v in vids if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser")), None)
            except Exception:
                yt = None

            if yt and yt.get("key"):
                url = f"https://www.youtube.com/watch?v={yt.get('key')}"
                # Render the poster as a linked image that opens in a new tab/window.
                st.markdown(f'<a href="{url}" target="_blank"><img src="{poster}" style="width:100%;border-radius:4px;"/></a>', unsafe_allow_html=True)
            else:
                st.image(poster, use_column_width=True)
    with col2:
        # Render right-side information with classes so CSS can style it
        rating = movie.get("vote_average", 0.0)
        count = movie.get("vote_count", 0)
        rel = movie.get("release_date", "—")
        overview = movie.get("overview") or "No overview available."

        st.markdown(f"<div class='card-right'>\n  <h3 class='card-title'>{mtitle}</h3>\n  <div class='card-meta'><strong>Rating:</strong> {rating:.1f} ({count} votes) &nbsp; | &nbsp; <strong>Release:</strong> {rel}</div>\n  <div class='card-overview'>{textwrap.shorten(overview, width=400, placeholder='…')}</div>\n</div>", unsafe_allow_html=True)

        if st.button("View details & trailer", key=f"btn_{key_prefix}{movie.get('id')}"):
            st.session_state["selected_movie"] = movie.get("id")

def render_movie_details(movie_id):
    det = movie_details(movie_id)
    st.markdown("---")
    # container for styled movie details
    st.markdown('<div class="movie-details">', unsafe_allow_html=True)
    st.markdown(f"<h2>{det.get('title')}</h2>", unsafe_allow_html=True)
    cols = st.columns([1, 2])
    with cols[0]:
        p = poster_url(det.get("poster_path"))
        if p:
            st.image(p, use_column_width=True)
    with cols[1]:
        st.markdown(f"<div class='meta'><span class='label'>Rating</span><span class='value'>{det.get('vote_average',0.0):.1f} ({det.get('vote_count',0)} votes)</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='meta'><span class='label'>Release</span><span class='value'>{det.get('release_date','—')}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='meta'><span class='label'>Runtime</span><span class='value'>{det.get('runtime','—')} min</span></div>", unsafe_allow_html=True)
        st.markdown(f"<p class='overview'>{det.get('overview') or 'No overview available.'}</p>", unsafe_allow_html=True)
    vids = movie_videos(movie_id)
    yt = next((v for v in vids if v.get("site") == "YouTube" and v.get("type") in ("Trailer", "Teaser")), None)
    if yt:
        st.subheader("Trailer")
        st.video(f"https://www.youtube.com/watch?v={yt.get('key')}")
    else:
        st.info("No trailer found.")
    st.markdown('</div>', unsafe_allow_html=True)

def browse_ui():
    st.title("🎬 Movie Explorer")
    st.caption("Trending • Search • Actor • Genre")

    # Inject CSS to make sidebar radio options (Trending/Search/Actor/Genre) equal size
    st.markdown(
        """
        <style>
        /* Target Streamlit radio options in the sidebar */
        .css-1avcm0n .stRadio > div > label, /* generic label in some Streamlit versions */
        .stSidebar .stRadio > div > label,
        .stRadio > div > label {
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            width: 160px !important; /* fixed width so all options match */
            padding: 8px 12px !important;
            margin: 6px 0 !important;
            border-radius: 8px !important;
            background: rgba(255,255,255,0.03) !important;
            color: #ddd !important;
            box-sizing: border-box !important;
        }

        /* Make selected option more prominent */
        .stRadio > div > label[aria-checked="true"],
        .stRadio > div > label:has(input:checked) {
            background: linear-gradient(90deg, rgba(78,154,241,0.15), rgba(78,154,241,0.05)) !important;
            border: 1px solid rgba(78,154,241,0.25) !important;
            color: #fff !important;
        }

        /* Ensure radio text wraps and centers properly */
        .stRadio > div > label .stMarkdown, .stRadio > div > label > div {
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.success(f"Logged in as **{st.session_state['user']['name']}**")
        if st.button("Log out", use_container_width=True):
            st.session_state.pop("user", None)
            st.rerun()
        st.markdown("---")
        st.markdown("<div class='sidebar-title'>Browse</div>", unsafe_allow_html=True)
        mode = st.radio("Choose a section:", ["Trending", "Search", "Actor", "Genre"], index=0)

    set_background(MODE_BACKGROUNDS.get(mode, ""))

    if st.session_state.get("selected_movie"):
        if st.button("⬅ Back to list"):
            st.session_state.pop("selected_movie")
            st.rerun()
        render_movie_details(st.session_state["selected_movie"])
        return

    if mode == "Trending":
        period = st.radio("Period", ["day", "week"], index=0, horizontal=True)
        movies = trending(period=period or "day")
        st.subheader(f"Trending this {period}")
        for m in movies:
            st.container()
            movie_card(m, key_prefix=f"tr_{period}_")
    elif mode == "Search":
        q = st.text_input("Search for a movie title")
        if q:
            movies = search_movies(q)
            st.subheader(f"Results for “{q}”")
            if not movies:
                st.info("No results.")
            for m in movies:
                st.container()
                movie_card(m, key_prefix="search_")
        else:
            st.info("Type to search titles.")
    elif mode == "Actor":
        q = st.text_input("Search for an actor / person")
        if q:
            people = search_person(q)
            if not people:
                st.info("No people found.")
            else:
                # Present only the person's name to the user (no id shown).
                options = [p.get("name") for p in people]
                choice = st.selectbox("", options)
                if choice:
                    # Find the first matching person and use their id to fetch credits.
                    pid = next((p.get("id") for p in people if p.get("name") == choice), None)
                    if pid:
                        movies = person_movie_credits(pid)
                        st.subheader(f"Movies for {choice}")
                        for m in movies:
                            st.container()
                            movie_card(m, key_prefix="actor_")
        else:
            # Intentionally show nothing when the actor search field is empty.
            pass
    elif mode == "Genre":
        gens = genres()
        name_to_id = {g["name"]: g["id"] for g in gens}
        name = st.selectbox("Pick a genre", list(name_to_id.keys()) if name_to_id else [])
        if name:
            movies = discover_by_genre(name_to_id[name])
            st.subheader(f"{name} movies")
            for m in movies:
                st.container()
                movie_card(m, key_prefix="genre_")

# ---------------- MAIN ----------------
# Auto-skip login: when the app starts, ensure there's a default "Guest" user
# so the browse/home page opens directly instead of showing the login/signup UI.
if not is_logged_in():
    # set a minimal guest user so browse_ui() can rely on st.session_state['user']
    set_logged_in({"id": 0, "name": "Guest", "email": "guest@local"})

# Always show the browse homepage
browse_ui()

