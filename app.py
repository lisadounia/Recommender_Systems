import streamlit as st
import pandas as pd
import os
import random
import altair as alt
import re

#python -m streamlit run app.py
# Page configuration
st.set_page_config(page_title="CineStream Pro", layout="wide", initial_sidebar_state="expanded")

# --- Definition of specific users ---
SPECIFIC_USERS_DATA = [
    {"id": 300001, "name": "Cyril", "image_file": "Cyril.jpg"},
    {"id": 300002, "name": "Hamza", "image_file": "Hamza.jpg"},
    {"id": 300003, "name": "Lisa", "image_file": "Lisa.jpg"},
    {"id": 300004, "name": "Inas", "image_file": "Inas.jpg"},
]
PROFILE_IMAGE_FOLDER = "profil"

# --- Paths to recommendation CSVs ---
BASE_PATH = r"/Users/lisadounia/Downloads/mlsmm2156-FINAL" # Ensure this path is correct
MAIN_MOVIE_DATA_CSV_PATH = os.path.join(BASE_PATH, "unique_top_movies_enriched.csv") # This is the source for user's "library"
RECO_CONTENT_POOL_CSV_PATH = os.path.join(BASE_PATH, "enriched_top_100_content.csv")
RECO_USER_BASED_CSV_PATH = os.path.join(BASE_PATH, "enriched_top_100_user.csv")
RECO_LATENT_FACTOR_CSV_PATH = os.path.join(BASE_PATH, "enriched_top_100_latent.csv")

# CSS
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<style>
    :root {
        --netflix-red: #e50914; --netflix-red-dark: #b20710; --dark-bg: #141414;
        --medium-bg: #1c1c1c; --light-bg: #282828; --text-light: #f5f5f1;
        --text-medium: #b0b0b0; --text-dark: #808080; --accent-gold: #FFD700;
    }
    body { color: var(--text-light); font-family: 'Roboto', sans-serif; background-color: var(--dark-bg); }
    .main-header { background: linear-gradient(135deg, #000000 0%, var(--medium-bg) 100%); padding: 2.5rem; border-radius: 18px; text-align: center; margin-bottom: 2.5rem; color: white; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border-bottom: 3px solid var(--netflix-red); }
    .main-header h1 { color: var(--netflix-red); text-shadow: 2px 2px 5px rgba(0,0,0,0.7); font-family: 'Montserrat', sans-serif; font-size: 3em; }
    .user-specific-header { background: linear-gradient(120deg, var(--netflix-red) 0%, var(--netflix-red-dark) 100%); padding: 1.2rem 2rem; border-radius: 12px; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto; text-align: center; box-shadow: 0 6px 15px rgba(0,0,0,0.25); } .user-specific-header h2 { margin: 0; font-size: 2em; font-weight: 700; font-family: 'Montserrat', sans-serif; text-shadow: 1px 1px 3px rgba(0,0,0,0.5); } .user-specific-header .header-username { color: #ffffff; font-weight: bold; } .user-specific-header p { margin: 8px 0 0 0; opacity: 0.95; font-size: 1em; color: #e0e0e0; }
    .user-selection { display: flex; flex-wrap: wrap; gap: 25px; justify-content: center; margin: 2.5rem 0; }
    .user-card { background: var(--medium-bg); border: 2px solid #383838; border-radius: 15px; padding: 25px; text-align: center; color: var(--text-light); min-width: 180px; transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
    .user-card:hover { border-color: var(--netflix-red); transform: translateY(-10px) scale(1.05); box-shadow: 0 15px 30px rgba(var(--netflix-red), 0.4); }
    .user-card img.user-avatar { width: 110px; height: 110px; object-fit: cover; border-radius: 50%; margin-bottom: 18px; border: 4px solid var(--netflix-red); box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
    .user-card .user-name-display { font-size: 1.4rem; font-weight: bold; margin-bottom: 8px; color: var(--text-light); }
    .user-card .user-stat { font-size: 0.95rem; color: var(--text-medium); margin-bottom: 5px; }
    .user-card .stButton>button { background-color: var(--netflix-red) !important; color: white !important; border-radius: 8px !important; padding: 10px 15px !important; font-weight: bold !important; margin-top: 15px !important; transition: background-color 0.3s ease !important; }
    .user-card .stButton>button:hover { background-color: var(--netflix-red-dark) !important; }
    
    .section-header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.8rem;
         border-bottom: 3px solid var(--netflix-red);
         padding-bottom: 8px;
    }
    .genre-title {
        color: var(--text-light); 
        font-size: 1.8em; 
        font-weight: bold; 
        font-family: 'Montserrat', sans-serif;
        margin: 0;
        display: inline-block;
    }
    .see-all-button-container button {
        background-color: transparent !important;
        color: var(--text-medium) !important;
        border: 1px solid var(--text-dark) !important;
        padding: 5px 10px !important;
        font-size: 0.9em !important;
        font-weight: normal !important;
        border-radius: 6px !important;
    }
    .see-all-button-container button:hover {
        color: var(--text-light) !important;
        border-color: var(--netflix-red) !important;
    }

    .movie-row-simple { margin-bottom: 2.5rem; }
    .movie-card-grid-item { height: 100%; display:flex; }
    .filtered-movie-card { background-color: var(--medium-bg); border-radius: 10px; padding: 12px; color: var(--text-light); display: flex; flex-direction: column; align-items: center; text-align: center; height: 100%; justify-content: flex-start; box-shadow: 0 4px 12px rgba(0,0,0,0.4); transition: transform 0.3s ease, box-shadow 0.3s ease; border: 1px solid #303030; }
    .filtered-movie-card:hover { transform: scale(1.03); box-shadow: 0 8px 20px rgba(0,0,0,0.5); border-color: var(--netflix-red); }
    .filtered-movie-card img { border-radius: 6px; margin-bottom: 10px; width: 100%; aspect-ratio: 2/3; object-fit: cover; box-shadow: 0 2px 6px rgba(0,0,0,0.3); }
    .filtered-movie-title { font-size: 1rem; font-weight: bold; margin-bottom: 6px; min-height: 2.8em; line-height: 1.4em; color: var(--text-light); overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    .filtered-movie-info { font-size: 0.85rem; color: var(--text-medium); margin-bottom: 4px;}
    .movie-card-actions { margin-top: auto; padding-top: 10px; width: 100%; display: flex; flex-direction: column; gap: 8px; }
    .card-action-button-wrapper { width: 100%; }
    .card-action-button-wrapper button { font-size: 0.8rem !important; padding: 6px 10px !important; border-radius: 6px !important; width: 100% !important; border: none !important; color: white !important; transition: background-color 0.2s ease, transform 0.1s ease; font-weight: bold; }
    .card-action-button-wrapper button:active { transform: scale(0.97); }
    .details-button-class button { background-color: #505050 !important; }
    .details-button-class button:hover { background-color: #606060 !important; }
    .watchlist-add-class button { background-color: var(--accent-gold) !important; color: var(--dark-bg) !important; }
    .watchlist-add-class button:hover { background-color: #FFC107 !important; }
    .watchlist-remove-class button { background-color: var(--netflix-red-dark) !important; }
    .watchlist-remove-class button:hover { background-color: var(--netflix-red) !important; }
    .stTabs [data-baseweb="tab-list"] { background-color: var(--medium-bg); border-radius: 10px; padding: 10px 15px; margin: 0 auto 2rem auto; display: flex; justify-content: center; gap: 12px; max-width: 100%; width: 100%; } .stTabs [data-baseweb="tab"] { background-color: transparent !important; color: var(--text-medium) !important; font-weight: bold; font-size: 1.05rem; padding: 10px 20px; border-radius: 8px; transition: background-color 0.3s ease, color 0.3s ease; flex-grow: 1; text-align: center; } .stTabs [data-baseweb="tab"]:hover { background-color: var(--light-bg) !important; color: var(--text-light) !important; } .stTabs [aria-selected="true"] { background-color: var(--netflix-red) !important; color: white !important; box-shadow: 0 0 10px rgba(229, 9, 20, 0.5); }
    .stSelectbox > div > div, .stMultiSelect > div[data-baseweb="select"] > div { background-color: var(--light-bg) !important; color: var(--text-light) !important; border: 1px solid #484848 !important; border-radius: 6px !important; }
    .stSelectbox > label, .stMultiSelect > label { color: var(--text-light) !important; font-weight: bold; }
    .stMultiSelect span[data-baseweb="tag"] { background-color: var(--netflix-red) !important; color: white !important; border-radius: 4px !important;}
    .stMultiSelect div[role="option"] { background-color: var(--light-bg) !important; color: var(--text-light) !important; }
    .stMultiSelect div[role="option"]:hover { background-color: #404040 !important; }
    .stSlider > label { color: var(--text-light) !important; font-weight: bold; }
    .stSlider [data-baseweb="slider"] > div > div { background-color: var(--netflix-red) !important; }
    .profile-ranking-item { background-color: var(--medium-bg); border-radius: 10px; padding: 15px 20px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; border-left: 6px solid var(--netflix-red); box-shadow: 0 3px 8px rgba(0,0,0,0.3); transition: background-color 0.2s ease, transform 0.2s ease; }
    .profile-ranking-item:hover { background-color: var(--light-bg); transform: translateX(5px); }
    .profile-ranking-item .rank { font-size: 1.6em; font-weight: bold; color: var(--netflix-red); margin-right: 18px; min-width: 35px; text-align: right; }
    .profile-ranking-item .item-icon { margin-right: 12px; color: var(--accent-gold); font-size: 1.4em; }
    .profile-ranking-item .item-name { font-size: 1.15em; flex-grow: 1; color: var(--text-light); font-weight: 500;}
    .profile-ranking-item .item-count { font-size: 1em; color: var(--text-medium); background-color: var(--dark-bg); padding: 4px 10px; border-radius: 6px; }
    .discovery-container { text-align: center; padding: 25px; background-color: var(--medium-bg); border-radius: 15px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
    .discovery-container .stVideo { margin-left: auto; margin-right: auto; max-width: 720px; border-radius: 8px; overflow: hidden;}
    .discovery-title { font-size: 1.8em; margin-bottom: 18px; color: var(--text-light); font-family: 'Montserrat', sans-serif;}
    .clickable-name-container {
        margin-bottom: 10px;
    }
    .clickable-name {
        display: inline-block;
        background-color: var(--light-bg);
        color: var(--text-light);
        padding: 6px 12px;
        margin: 3px 5px 3px 0;
        border-radius: 15px;
        border: 1px solid #484848;
        font-size: 0.9em;
        text-decoration: none;
        cursor: pointer;
        transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    }
    .clickable-name:hover {
        background-color: var(--netflix-red);
        color: white;
        border-color: var(--netflix-red-dark);
    }
    .page-title { 
        color: var(--text-light);
        font-size: 2.2em;
        font-weight: bold;
        font-family: 'Montserrat', sans-serif;
        margin-bottom: 1.5rem;
        text-align: center;
        padding-bottom: 10px;
        border-bottom: 2px solid var(--netflix-red);
    }
    .watched-rating {
        font-size: 1.4rem; color: var(--accent-gold); text-align: center;
        padding: 8px; background-color: rgba(0,0,0,0.2); border-radius: 6px;
        margin: 8px auto 0 auto; width: fit-content;
    }
    .popover-rating-container .stButton button {
        background-color: var(--light-bg); color: var(--text-light); border: 1px solid #555;
        margin: 2px !important; padding: 5px 10px !important; font-size: 1.2rem !important;
    }
    .popover-rating-container .stButton button:hover {
        border-color: var(--accent-gold); color: var(--accent-gold);
    }
    .rating-section-container {
        margin-top: 8px;
    }
    .watched-section-header {
        font-size: 1.8em; font-weight: bold; font-family: 'Montserrat', sans-serif;
        color: var(--accent-gold); margin-top: 2rem; margin-bottom: 1rem;
        padding-bottom: 8px; border-bottom: 2px solid var(--accent-gold);
    }
</style>
""", unsafe_allow_html=True)

# --- Session state and data loading ---
if 'current_user_id' not in st.session_state: st.session_state.current_user_id = None
if 'current_user_name' not in st.session_state: st.session_state.current_user_name = None
if 'selected_movie_id' not in st.session_state: st.session_state.selected_movie_id = None
if 'viewing_genre_page' not in st.session_state: st.session_state.viewing_genre_page = None
if 'viewing_actor_page' not in st.session_state: st.session_state.viewing_actor_page = None
if 'viewing_director_page' not in st.session_state: st.session_state.viewing_director_page = None
if 'previous_view_state' not in st.session_state: st.session_state.previous_view_state = {}
if 'discovery_movie' not in st.session_state: st.session_state.discovery_movie = None
if 'watchlists' not in st.session_state: st.session_state.watchlists = {}
if 'viewing_full_list_details' not in st.session_state: st.session_state.viewing_full_list_details = None
if 'watched_movies' not in st.session_state: st.session_state.watched_movies = {}

def preprocess_movie_df(df, file_source_name="Unknown source"):
    if 'item_id' in df.columns:
        df.rename(columns={'item_id': 'movieId'}, inplace=True)
    elif 'movieId' not in df.columns:
        st.warning(f"File '{file_source_name}' must contain an 'item_id' or 'movieId' column.")
        return pd.DataFrame()

    df["movieId"] = pd.to_numeric(df["movieId"], errors='coerce')
    df.dropna(subset=["movieId"], inplace=True)
    df["movieId"] = df["movieId"].astype(int)

    if 'date' in df.columns:
        df['date'] = pd.to_numeric(df['date'], errors='coerce')
    else:
        df['date'] = pd.NA

    if 'user_score' in df.columns:
        df['user_score'] = pd.to_numeric(df['user_score'], errors='coerce')
    else:
        df['user_score'] = pd.NA

    for col in ['genres', 'actors', 'director', 'trailer_url', 'synopsis', 'tmdbId', 'title']:
        if col in df.columns:
            df[col] = df[col].fillna('')
        else:
            df[col] = ''

    if 'user_id' in df.columns:
        df['user_id'] = pd.to_numeric(df['user_id'], errors='coerce')
        if file_source_name == "User Library Data":
            df.dropna(subset=['user_id'], inplace=True)
            df['user_id'] = df['user_id'].astype(int)
        elif not df['user_id'].isnull().all():
             df['user_id'] = df['user_id'].astype('Int64')

    if file_source_name == "User Library Data":
        df.drop_duplicates(subset=['user_id', 'movieId'], keep='first', inplace=True)
    elif file_source_name in ["User-Based Recommendations", "Latent Factor Recommendations", "Content-Based Pool"]:
        if 'user_id' in df.columns and not df['user_id'].isnull().all():
            df.drop_duplicates(subset=['user_id', 'movieId'], keep='first', inplace=True)
        else:
            df.drop_duplicates(subset=['movieId'], keep='first', inplace=True)
    else:
        if 'user_id' in df.columns and not df['user_id'].isnull().all():
             df.drop_duplicates(subset=['user_id', 'movieId'], keep='first', inplace=True)
        else:
            df.drop_duplicates(subset=['movieId'], keep='first', inplace=True)
    return df

@st.cache_data
def load_user_library_data():
    df = pd.read_csv(MAIN_MOVIE_DATA_CSV_PATH)
    df = preprocess_movie_df(df, "User Library Data")
    specific_user_ids = [user_data["id"] for user_data in SPECIFIC_USERS_DATA]
    df_filtered = df[df['user_id'].isin(specific_user_ids)].copy()
    return df_filtered

@st.cache_data
def load_reco_data_from_file(file_path, file_description):
    try:
        df = pd.read_csv(file_path)
        df = preprocess_movie_df(df, file_description)
        return df
    except FileNotFoundError:
        st.warning(f"Recommendation file '{file_path}' ({file_description}) not found. This recommendation type will be unavailable.")
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Error loading '{file_path}' ({file_description}): {e}")
        return pd.DataFrame()

try:
    df_global = load_user_library_data()
    if df_global.empty:
        st.error("No users from SPECIFIC_USERS_DATA found in the main CSV (library data), or the CSV is empty after filtering.")
        st.stop()
    df_reco_content_pool = load_reco_data_from_file(RECO_CONTENT_POOL_CSV_PATH, "Content-Based Pool")
    df_reco_user_based = load_reco_data_from_file(RECO_USER_BASED_CSV_PATH, "User-Based Recommendations")
    df_reco_latent_factor = load_reco_data_from_file(RECO_LATENT_FACTOR_CSV_PATH, "Latent Factor Recommendations")
except FileNotFoundError:
    st.error(f"❌ Main CSV file (for user library) not found at {MAIN_MOVIE_DATA_CSV_PATH}. Please check the path.")
    st.stop()
except Exception as e:
    st.error(f"General error during data loading: {e}")
    st.stop()

# --- Recommendation Logic Functions ---
def get_precomputed_recommendations_for_user(reco_df, user_id, user_library_df, num_recommendations=-1, exclude_from_library=True):
    if reco_df.empty or 'user_id' not in reco_df.columns:
        return []
    try:
        current_user_id_int = int(user_id)
        user_specific_recos = reco_df[pd.to_numeric(reco_df['user_id'], errors='coerce') == current_user_id_int].copy()
    except ValueError:
        st.warning(f"Invalid user ID: {user_id}")
        return []
    if user_specific_recos.empty:
        return []
        
    if exclude_from_library and user_library_df is not None and not user_library_df.empty:
        user_library_movie_ids = set(user_library_df['movieId'].unique())
        user_specific_recos = user_specific_recos[~user_specific_recos['movieId'].isin(user_library_movie_ids)]

    if 'score' in user_specific_recos.columns and user_specific_recos['score'].notna().any():
        user_specific_recos.sort_values(by='score', ascending=False, inplace=True, na_position='last')
    elif 'predicted_rating' in user_specific_recos.columns and user_specific_recos['predicted_rating'].notna().any():
        user_specific_recos.sort_values(by='predicted_rating', ascending=False, inplace=True, na_position='last')
    elif 'user_score' in user_specific_recos.columns and user_specific_recos['user_score'].notna().any():
        user_specific_recos.sort_values(by='user_score', ascending=False, inplace=True, na_position='last')
    
    if num_recommendations == -1:
        return user_specific_recos.to_dict('records')
    else:
        return user_specific_recos.head(num_recommendations).to_dict('records')

# --- UI Functions (watchlist, buttons, cards) ---
def rate_movie(user_id, movie_id, rating):
    if user_id not in st.session_state.watched_movies:
        st.session_state.watched_movies[user_id] = {}
    st.session_state.watched_movies[user_id][int(movie_id)] = rating
    rating = int(rating)
    st.toast(f"Rated movie with {rating} star{'s' if rating != 1 else ''}!", icon="⭐")
    if user_id in st.session_state.watchlists and int(movie_id) in st.session_state.watchlists[user_id]:
        st.session_state.watchlists[user_id].remove(int(movie_id))

def toggle_watchlist(user_id, movie_id):
    if user_id not in st.session_state.watchlists:
        st.session_state.watchlists[user_id] = set()
    try: movie_id = int(movie_id)
    except ValueError: st.error("Invalid movie ID."); return
    if movie_id in st.session_state.watchlists[user_id]:
        st.session_state.watchlists[user_id].remove(movie_id)
        st.toast(f"Removed from watchlist!", icon="➖")
    else:
        st.session_state.watchlists[user_id].add(movie_id)
        st.toast(f"Added to watchlist!", icon="➕")

def is_in_watchlist(user_id, movie_id):
    if user_id not in st.session_state.watchlists: return False
    try: return int(movie_id) in st.session_state.watchlists[user_id]
    except ValueError: return False

def render_action_button(label, class_name, on_click_action, key, help_text=""):
    st.markdown(f'<div class="card-action-button-wrapper {class_name}">', unsafe_allow_html=True)
    if st.button(label, key=key, help=help_text, use_container_width=True):
        on_click_action()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def display_movie_card_with_actions(movie_data, user_id, key_suffix):
    if isinstance(movie_data, dict):
        movie_data = pd.Series(movie_data)
    movie_id = int(movie_data['movieId'])
    title = movie_data.get('title', 'N/A')
    
    with st.container():
        st.markdown('<div class="filtered-movie-card">', unsafe_allow_html=True)
        
        poster_path = os.path.join("posters_tmdb", f"{movie_id}.jpg")
        if os.path.exists(poster_path):
            st.image(poster_path, use_container_width=True)
        else:
            st.markdown(f"""<div style="width:100%; aspect-ratio: 2/3; background: #333; display:flex; align-items:center; justify-content:center; border-radius:4px; margin-bottom:8px;">🎬<br>{str(title)[:20]}...</div>""", unsafe_allow_html=True)
        
        st.markdown(f'<div class="filtered-movie-title">{title}</div>', unsafe_allow_html=True)
        
        if pd.notna(movie_data.get('user_score')):
            st.markdown(f"<div class=\"filtered-movie-info\">👤 {movie_data['user_score']:.0f}/100</div>", unsafe_allow_html=True)
        if pd.notna(movie_data.get('date')): 
            try:
                year_val = int(movie_data['date'])
                st.markdown(f"<div class=\"filtered-movie-info\">📅 {year_val}</div>", unsafe_allow_html=True)
            except (ValueError, TypeError):
                 st.markdown(f"<div class=\"filtered-movie-info\">📅 N/A</div>", unsafe_allow_html=True)
        
        st.markdown('<div class="movie-card-actions">', unsafe_allow_html=True)
        
        col_details, col_watchlist = st.columns(2)
        
        with col_details:
            def details_action():
                st.session_state.selected_movie_id = movie_id
                st.session_state.viewing_genre_page = None
                st.session_state.viewing_actor_page = None 
                st.session_state.viewing_director_page = None 
                st.session_state.previous_view_state = {
                    'view_type': st.session_state.get('viewing_full_list_details', {}).get('title', 'main_recommendations'), 
                    'full_list_context': st.session_state.get('viewing_full_list_details'), 
                    'current_user_id': user_id,
                    'current_user_name': st.session_state.get('current_user_name'),
                }
            render_action_button("ℹ️", "details-button-class", details_action, key=f"details_card_{key_suffix}_{movie_id}")

        with col_watchlist:
            if user_id:
                in_watchlist = is_in_watchlist(user_id, movie_id)
                watchlist_label = "➖" if in_watchlist else "➕"
                watchlist_class = "watchlist-remove-class" if in_watchlist else "watchlist-add-class"
                def watchlist_toggle_action(): toggle_watchlist(user_id, movie_id)
                render_action_button(watchlist_label, watchlist_class, watchlist_toggle_action, key=f"watchlist_card_{key_suffix}_{movie_id}")

        if user_id:
            st.markdown('<div class="rating-section-container">', unsafe_allow_html=True)
            user_watched_list = st.session_state.watched_movies.get(user_id, {})
            if movie_id in user_watched_list:
                rating = user_watched_list[movie_id]
                st.markdown(f"<div class='watched-rating'>{'⭐' * rating}</div>", unsafe_allow_html=True)
            else:
                popover = st.popover("Seen it? Rate it!", use_container_width=True)
                with popover:
                    st.markdown("<div class='popover-rating-container'>", unsafe_allow_html=True)
                    cols = st.columns(5)
                    for i in range(1, 6):
                        with cols[i-1]:
                            if st.button(f"{'⭐'*i}", key=f"rate_{i}_{key_suffix}_{movie_id}", use_container_width=True):
                                rate_movie(user_id, movie_id, i)
                                st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True) 
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Page Display Functions ---
def show_user_selection():
    st.markdown("""
    <div class="main-header">
        <h1>🎬 CineStream Pro</h1>
        <p style="font-size: 1.2rem; color: #ccc;">Who's watching today?</p>
    </div>
    """, unsafe_allow_html=True)
    cols_per_row = min(len(SPECIFIC_USERS_DATA), 4)
    if cols_per_row == 0: st.warning("No users defined in SPECIFIC_USERS_DATA."); return
    
    cols = st.columns(cols_per_row)
    for i, user_info in enumerate(SPECIFIC_USERS_DATA):
        user_id_val = user_info["id"]
        current_name = user_info["name"]
        image_filename = user_info["image_file"]
        avatar_path = os.path.join(PROFILE_IMAGE_FOLDER, image_filename)
        
        user_library_df = df_global[df_global["user_id"] == user_id_val]
        movie_count = len(user_library_df["movieId"].unique()) 
        all_genres_list = []
        if not user_library_df.empty and "genres" in user_library_df.columns:
            for genres_str_loop in user_library_df["genres"].dropna():
                all_genres_list.extend([g.strip() for g in str(genres_str_loop).split('|') if g.strip()])
        genre_counts_series = pd.Series(all_genres_list).value_counts()
        top_genre = genre_counts_series.index[0] if len(genre_counts_series) > 0 else "Varied"
        
        with cols[i % cols_per_row]:
            card_container = st.container()
            if os.path.exists(avatar_path):
                card_container.image(avatar_path, width=300, use_container_width=False) 
            else:
                card_container.markdown("<div style='width:110px; height:110px; background-color:var(--light-bg); border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:50px; margin: 0 auto 18px auto; border: 4px solid var(--netflix-red);'>👤</div>", unsafe_allow_html=True)

            card_container.markdown(f"""
            <div class="user-card" style="margin-top: -20px; padding-top: 25px;"> 
                <div class="user-name-display">{current_name}</div>
                <div class="user-stat">📚 {movie_count} movies in library</div> 
                <div class="user-stat">🎭 Favorite Genre: {top_genre}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if card_container.button(f"{current_name}'s Profile", key=f"user_select_btn_{user_id_val}", use_container_width=True):
                st.session_state.current_user_id = user_id_val
                st.session_state.current_user_name = current_name
                st.session_state.selected_movie_id = None; st.session_state.viewing_genre_page = None
                st.session_state.viewing_actor_page = None; st.session_state.viewing_director_page = None;
                st.session_state.viewing_full_list_details = None 
                st.session_state.previous_view_state = {}; st.session_state.discovery_movie = None
                if user_id_val not in st.session_state.watchlists:
                    st.session_state.watchlists[user_id_val] = set()
                if user_id_val not in st.session_state.watched_movies:
                    st.session_state.watched_movies[user_id_val] = {}
                st.rerun()

def show_my_library_with_filters(user_df_library):
    current_user_name_display = st.session_state.get('current_user_name', 'User')
    current_user_id_for_filters = st.session_state.get('current_user_id')
    st.markdown(f"### 📚 All Our Recommended Movies ({current_user_name_display})") 
    if user_df_library.empty: st.warning(f"Your library is empty, {current_user_name_display}."); return
    
    all_genres_user = set()
    for genres_str in user_df_library["genres"].dropna().unique():
        for genre in str(genres_str).split('|'):
            if genre.strip(): all_genres_user.add(genre.strip())
    sorted_genres = sorted(list(all_genres_user))
    
    all_actors_user = set()
    for actors_str in user_df_library["actors"].dropna().unique():
        for actor in str(actors_str).split('|'): 
            if actor.strip(): all_actors_user.add(actor.strip())
    sorted_actors = sorted(list(all_actors_user))
    
    all_directors_user = set()
    for director_str in user_df_library["director"].dropna().unique():
        directors_in_row = str(director_str).split(',') 
        for d in directors_in_row:
            if d.strip(): all_directors_user.add(d.strip())
    sorted_directors = sorted(list(all_directors_user))
    
    min_year_user = int(user_df_library['date'].dropna().min()) if not user_df_library['date'].dropna().empty else 1900
    max_year_user = int(user_df_library['date'].dropna().max()) if not user_df_library['date'].dropna().empty else pd.Timestamp('now').year + 1
    min_user_score_val = float(user_df_library['user_score'].dropna().min()) if not user_df_library['user_score'].dropna().empty else 0.0
    max_user_score_val = float(user_df_library['user_score'].dropna().max()) if not user_df_library['user_score'].dropna().empty else 100.0
    
    with st.expander("🔧 Show Filters and Sorting Options", expanded=True):
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        with filter_col1:
            search_title = st.text_input("Search by title:", key="filter_title_library_tab")
            selected_genres_filter = st.multiselect("Genre(s):", sorted_genres, key="filter_genres_library_tab")
        with filter_col2:
            selected_actors = st.multiselect("Actor(s):", sorted_actors, key="filter_actors_library_tab", placeholder="Select actors")
            selected_directors = st.multiselect("Director(s):", sorted_directors, key="filter_directors_library_tab", placeholder="Select directors")
        with filter_col3:
            year_range_filter = st.slider("Release Year:", min_value=min_year_user, max_value=max_year_user, value=(min_year_user, max_year_user), key="filter_year_library_tab")
            if min_user_score_val < max_user_score_val :
                 user_score_range_filter = st.slider("TMDB Score:", min_value=min_user_score_val, max_value=max_user_score_val, value=(min_user_score_val, max_user_score_val), step=1.0, key="filter_user_score_library_tab")
            else:
                user_score_range_filter = (min_user_score_val, max_user_score_val) 
                st.caption(f"TMDB Score (fixed): {min_user_score_val}")
        
        sort_options = {
            "Relevance (default)": None, 
            "TMDB Score (high to low)": ("user_score", False), 
            "TMDB Score (low to high)": ("user_score", True),
            "Release Date (newest)": ("date", False), 
            "Release Date (oldest)": ("date", True),
            "Alphabetical (A-Z)": ("title", True), 
            "Alphabetical (Z-A)": ("title", False),
        }
        selected_sort_option_label = st.selectbox("Sort by:", options=list(sort_options.keys()), key="sort_option_library_films", index=0)
    
    filtered_df_library_movies = user_df_library.copy()
    if search_title: 
        filtered_df_library_movies = filtered_df_library_movies[filtered_df_library_movies['title'].str.contains(search_title, case=False, na=False)]
    if selected_genres_filter:
        def check_genres_func(movie_genres_str):
            if pd.isna(movie_genres_str): return False
            return any(sg.strip() in [g.strip() for g in str(movie_genres_str).split('|') if g.strip()] for sg in selected_genres_filter)
        filtered_df_library_movies = filtered_df_library_movies[filtered_df_library_movies['genres'].apply(check_genres_func)]
    if selected_actors:
        def check_actors_func(movie_actors_str):
            if pd.isna(movie_actors_str): return False
            return any(sa.strip() in [a.strip() for a in str(movie_actors_str).split('|') if a.strip()] for sa in selected_actors)
        filtered_df_library_movies = filtered_df_library_movies[filtered_df_library_movies['actors'].apply(check_actors_func)]
    if selected_directors:
        def check_directors_func(movie_director_str):
            if pd.isna(movie_director_str): return False
            return any(sd.strip() in [d.strip() for d in str(movie_director_str).split(',') if d.strip()] for sd in selected_directors)
        filtered_df_library_movies = filtered_df_library_movies[filtered_df_library_movies['director'].apply(check_directors_func)]
    if year_range_filter: 
        filtered_df_library_movies = filtered_df_library_movies[(filtered_df_library_movies['date'].isna()) | ((filtered_df_library_movies['date'] >= year_range_filter[0]) & (filtered_df_library_movies['date'] <= year_range_filter[1]))]
    if user_score_range_filter and min_user_score_val < max_user_score_val:
        filtered_df_library_movies = filtered_df_library_movies[(filtered_df_library_movies['user_score'].isna()) | ((filtered_df_library_movies['user_score'] >= user_score_range_filter[0]) & (filtered_df_library_movies['user_score'] <= user_score_range_filter[1]))]
    
    sort_column, sort_ascending = sort_options[selected_sort_option_label] if selected_sort_option_label != "Relevance (default)" else (None, None)
    if sort_column:
        if sort_column in ['user_score', 'date']: 
            filtered_df_library_movies = filtered_df_library_movies.sort_values(by=sort_column, ascending=sort_ascending, na_position='last')
        else: 
            filtered_df_library_movies = filtered_df_library_movies.sort_values(by=sort_column, ascending=sort_ascending)
    else: 
        if 'user_score' in filtered_df_library_movies.columns:
            filtered_df_library_movies = filtered_df_library_movies.sort_values(by="user_score", ascending=False, na_position='last')

    st.markdown(f"**{len(filtered_df_library_movies)} movie(s) found.**")
    if not filtered_df_library_movies.empty:
        movies_per_row_library_display = st.select_slider("Movies per row:", options=[3, 4, 5, 6], value=4, key="library_movies_row_tab")
        num_movies_filtered = len(filtered_df_library_movies)
        num_rows_filtered = (num_movies_filtered + movies_per_row_library_display - 1) // movies_per_row_library_display
        for i_row in range(num_rows_filtered):
            cols_display = st.columns(movies_per_row_library_display)
            for j_col in range(movies_per_row_library_display):
                movie_idx_filtered = i_row * movies_per_row_library_display + j_col
                if movie_idx_filtered < num_movies_filtered:
                    movie_item = filtered_df_library_movies.iloc[movie_idx_filtered]
                    with cols_display[j_col]:
                        st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                        display_movie_card_with_actions(movie_item, current_user_id_for_filters, key_suffix=f"library_films_{i_row}_{j_col}")
                        st.markdown('</div>', unsafe_allow_html=True)
    else: st.info("No movies match your criteria.")

def show_watched_movies_page():
    current_user_id = st.session_state.get('current_user_id')
    current_user_name = st.session_state.get('current_user_name', 'User')
    st.markdown(f'<h2 class="page-title">✔️ Watched Movies ({current_user_name})</h2>', unsafe_allow_html=True)

    if not current_user_id:
        st.warning("Please select a user to see their watched movies.")
        return

    watched_dict = st.session_state.watched_movies.get(current_user_id, {})
    if not watched_dict:
        st.info("You haven't rated any movies yet. Use the rating feature on a movie card!")
        return

    all_movie_dfs = [df_global, df_reco_content_pool, df_reco_user_based, df_reco_latent_factor]
    all_movie_dfs_valid = [df for df in all_movie_dfs if df is not None and not df.empty]
    if not all_movie_dfs_valid:
        st.error("No movie data sources available.")
        return
        
    combined_df = pd.concat(all_movie_dfs_valid).drop_duplicates(subset=['movieId'], keep='first')
    watched_movie_ids = list(watched_dict.keys())
    watched_movies_df = combined_df[combined_df['movieId'].isin(watched_movie_ids)].copy()
    watched_movies_df['user_rating'] = watched_movies_df['movieId'].map(watched_dict)
    
    for rating in range(5, 0, -1):
        movies_in_rating = watched_movies_df[watched_movies_df['user_rating'] == rating].sort_values("title")
        if not movies_in_rating.empty:
            plural = "s" if len(movies_in_rating) > 1 else ""
            st.markdown(f"<div class='watched-section-header'>{'⭐' * rating} - {rating} Star{plural} ({len(movies_in_rating)})</div>", unsafe_allow_html=True)
            
            movies_per_row = 5
            num_movies = len(movies_in_rating)
            num_rows = (num_movies + movies_per_row - 1) // movies_per_row
            
            for i_row in range(num_rows):
                cols = st.columns(movies_per_row)
                for j_col in range(movies_per_row):
                    movie_idx = i_row * movies_per_row + j_col
                    if movie_idx < num_movies:
                        movie_item = movies_in_rating.iloc[movie_idx]
                        with cols[j_col]:
                            st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                            display_movie_card_with_actions(movie_item, current_user_id, key_suffix=f"watched_{rating}_{i_row}_{j_col}")
                            st.markdown('</div>', unsafe_allow_html=True)

def show_watchlist_page():
    current_user_id_watchlist = st.session_state.get('current_user_id')
    current_user_name_watchlist = st.session_state.get('current_user_name', 'User')
    st.markdown(f'<h2 class="page-title">🍿 My Watchlist ({current_user_name_watchlist})</h2>', unsafe_allow_html=True)
    if not current_user_id_watchlist: st.warning("Please select a user to see their watchlist."); return
    watchlist_movie_ids = st.session_state.watchlists.get(current_user_id_watchlist, set())
    if not watchlist_movie_ids: st.info("Your watchlist is empty. Add some movies!"); return
    
    watchlist_movie_ids_int = {int(mid) for mid in watchlist_movie_ids}
    
    all_available_movies_for_watchlist = []
    if not df_global.empty:
        all_available_movies_for_watchlist.append(df_global.drop_duplicates(subset=['movieId']))
    if df_reco_user_based is not None and not df_reco_user_based.empty: 
        all_available_movies_for_watchlist.append(df_reco_user_based.drop_duplicates(subset=['movieId']))
    if df_reco_latent_factor is not None and not df_reco_latent_factor.empty: 
        all_available_movies_for_watchlist.append(df_reco_latent_factor.drop_duplicates(subset=['movieId']))
    if df_reco_content_pool is not None and not df_reco_content_pool.empty: 
        all_available_movies_for_watchlist.append(df_reco_content_pool.drop_duplicates(subset=['movieId']))
        
    if not all_available_movies_for_watchlist:
        st.info("No movie sources available to populate the watchlist.")
        return

    combined_df_for_watchlist = pd.concat(all_available_movies_for_watchlist).drop_duplicates(subset=['movieId'], keep='first')
    watchlist_df = combined_df_for_watchlist[combined_df_for_watchlist['movieId'].isin(list(watchlist_movie_ids_int))].copy()

    valid_watchlist_ids = set(watchlist_df['movieId'].unique())
    if valid_watchlist_ids != watchlist_movie_ids_int:
        st.session_state.watchlists[current_user_id_watchlist] = valid_watchlist_ids 
    
    if watchlist_df.empty: st.info("Your watchlist is empty or the movies are no longer available."); return
    
    watchlist_df = watchlist_df.sort_values(by="title") 
    st.markdown(f"You have **{len(watchlist_df)} movie(s)** in your watchlist.")
    movies_per_row_watchlist = st.select_slider("Movies per row:", options=[3, 4, 5, 6], value=4, key="watchlist_movies_per_row")
    num_movies_watchlist = len(watchlist_df)
    num_rows_watchlist = (num_movies_watchlist + movies_per_row_watchlist - 1) // movies_per_row_watchlist
    for i_row in range(num_rows_watchlist):
        cols_watchlist = st.columns(movies_per_row_watchlist)
        for j_col in range(movies_per_row_watchlist):
            movie_idx_watchlist = i_row * movies_per_row_watchlist + j_col
            if movie_idx_watchlist < num_movies_watchlist:
                movie_item_watchlist = watchlist_df.iloc[movie_idx_watchlist]
                with cols_watchlist[j_col]:
                    st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                    display_movie_card_with_actions(movie_item_watchlist, current_user_id_watchlist, key_suffix=f"watchlist_{i_row}_{j_col}")
                    st.markdown('</div>', unsafe_allow_html=True)

def show_user_profile(user_df_library, user_name):
    st.markdown(f'<h2 class="page-title">👤 {user_name}\'s Profile</h2>', unsafe_allow_html=True)
    if user_df_library.empty: st.warning("No movies in your library to generate a profile."); return
    
    st.subheader("General Statistics")
    total_movies_in_library = len(user_df_library['movieId'].unique())
    avg_user_score_in_library = user_df_library['user_score'].mean() if 'user_score' in user_df_library.columns and not user_df_library['user_score'].dropna().empty else 0

    col1, col2 = st.columns(2)
    col1.metric("Movies in Your Library", total_movies_in_library)
    if avg_user_score_in_library > 0:
        col2.metric("Average TMDB Score (Library)", f"{avg_user_score_in_library:.0f} / 100", help="Average TMDB score of the movies in your library")
    else:
        col2.metric("Average TMDB Score (Library)", "N/A")
    st.divider()

    def display_styled_ranking(title, counts_series, item_singular, item_plural, icon="🏆", top_n=10):
        st.subheader(title)
        if not counts_series.empty:
            for i, (item, count) in enumerate(counts_series.head(top_n).items()):
                plural_s = item_plural if count > 1 else item_singular
                item_html = f"""
                <div class="profile-ranking-item">
                    <span class="rank">#{i+1}</span>
                    <span class="item-icon">{icon}</span>
                    <span class="item-name">{item}</span>
                    <span class="item-count">{count} {plural_s}</span>
                </div>"""
                st.markdown(item_html, unsafe_allow_html=True)
        else: st.info(f"Not enough data to display rankings for {item_plural.lower()}.")
        st.markdown("---", unsafe_allow_html=True)
    
    genres_list = user_df_library['genres'].str.split('|').explode()
    genres_list = genres_list[genres_list.notna() & (genres_list.str.strip() != '')] 
    genres_list = genres_list.str.strip()
    genre_counts_data = genres_list.value_counts()
    display_styled_ranking("🎭 Your Favorite Genres (Library)", genre_counts_data, "movie", "movies", icon="🎭")
    
    actors_list = user_df_library['actors'].str.split('|').explode()
    actors_list = actors_list[actors_list.notna() & (actors_list.str.strip() != '')]
    actors_list = actors_list.str.strip()
    actor_counts_data = actors_list.value_counts()
    display_styled_ranking("🌟 Your Favorite Actors (Library)", actor_counts_data, "appearance", "appearances", icon="🌟")
    
    directors_list = user_df_library['director'].str.split(',').explode()
    directors_list = directors_list[directors_list.notna() & (directors_list.str.strip() != '')]
    directors_list = directors_list.str.strip()
    director_counts_data = directors_list.value_counts()
    display_styled_ranking("🎬 Your Favorite Directors (Library)", director_counts_data, "movie", "movies", icon="🎬")
    
    st.subheader("📈 TMDB Score Distribution (Library)") 
    if 'user_score' in user_df_library.columns and not user_df_library['user_score'].dropna().empty:
        tmdb_score_dist_chart = alt.Chart(user_df_library.dropna(subset=['user_score'])).mark_bar(color="#FFD700").encode(
            alt.X('user_score:Q', bin=alt.Bin(maxbins=10), title='TMDB Score', axis=alt.Axis(labelColor='white', titleColor='white')),
            alt.Y('count():Q', title='Number of Movies', axis=alt.Axis(labelColor='white', titleColor='white')),
            tooltip=[alt.Tooltip('user_score:Q', bin=alt.Bin(maxbins=10), title='Score Range'), alt.Tooltip('count():Q', title='Number of Movies')]
        ).properties(title=alt.TitleParams(text='TMDB Score Distribution (Library)', color='white', fontSize=16), background='transparent').configure_view(strokeWidth=0).configure_axis(gridColor='#444')
        st.altair_chart(tmdb_score_dist_chart, use_container_width=True)
    else: st.info("No TMDB scores to display for your library.")
    st.divider()

    st.subheader("📅 Distribution by Release Year (Library)") 
    user_df_dated = user_df_library.dropna(subset=['date']).copy()
    if not user_df_dated.empty:
        user_df_dated['year_int'] = user_df_dated['date'].astype(int)
        year_dist_chart = alt.Chart(user_df_dated).mark_bar(color="#e50914").encode(
            alt.X('year_int:O', bin=alt.Bin(maxbins=20), title='Release Year', axis=alt.Axis(labelAngle=-45, labelColor='white', titleColor='white')),
            alt.Y('count():Q', title='Number of Movies', axis=alt.Axis(labelColor='white', titleColor='white')),
            tooltip=[alt.Tooltip('year_int:O', bin=alt.Bin(maxbins=20), title='Period'), alt.Tooltip('count():Q', title='Number of Movies')]
        ).properties(title=alt.TitleParams(text='Distribution by Release Year (Library)', color='white', fontSize=16), background='transparent').configure_view(strokeWidth=0).configure_axis(gridColor='#444')
        st.altair_chart(year_dist_chart, use_container_width=True)
    else: st.info("No release dates to display for your library.")
    st.divider()

    st.subheader("🌟 Top Movies in Your Library (by TMDB Score)") 
    top_n_films = user_df_library.sort_values(by='user_score', ascending=False, na_position='last').head(10)
    if not top_n_films.empty:
        for idx, row_data in top_n_films.iterrows():
            movie_id_profile = int(row_data['movieId'])
            col_img, col_desc = st.columns([1,4])
            poster_path_profile = os.path.join("posters_tmdb", f"{movie_id_profile}.jpg")
            if os.path.exists(poster_path_profile): col_img.image(poster_path_profile, width=100)
            else: col_img.markdown("🎬", unsafe_allow_html=True)
            
            title_text = f"**{row_data.get('title','N/A')}** ({int(row_data['date']) if pd.notna(row_data.get('date')) else 'N/A'})"
            user_score_text = f"TMDB Score: **{row_data['user_score']:.0f}/100**" if pd.notna(row_data.get('user_score')) else "TMDB Score: N/A"
            genres_text = f"Genres: {row_data.get('genres','N/A')}" if pd.notna(row_data.get('genres')) else ""
            col_desc.markdown(f"{title_text}\n{user_score_text}")
            col_desc.markdown(f"<small>{genres_text}</small>", unsafe_allow_html=True)
            if st.button("View Details", key=f"profile_detail_btn_ranking_{movie_id_profile}"):
                st.session_state.selected_movie_id = movie_id_profile
                st.session_state.viewing_genre_page = None; st.session_state.viewing_actor_page = None; st.session_state.viewing_director_page = None;
                st.session_state.viewing_full_list_details = None 
                st.rerun()
            col_desc.markdown("---")
    else: st.info("No movies to display in the top of your library.")

def show_discovery_page(user_df_library):
    st.markdown('<h2 class="page-title">🎲 Discovery Page</h2>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1em; color: #ccc;'>Discover a random trailer from a movie in your library!</p>", unsafe_allow_html=True) 
    current_user_id_disc = st.session_state.get('current_user_id')
    movies_with_trailers = user_df_library[user_df_library['trailer_url'].ne('') & user_df_library['trailer_url'].notna()].copy()
    if movies_with_trailers.empty:
        st.warning("😕 No movies with trailers available in your library at the moment.") 
        return
    if st.button("🎲 New Random Discovery", key="new_discovery_btn", use_container_width=True, type="primary"):
        st.session_state.discovery_movie = movies_with_trailers.sample(1).iloc[0] 
    if st.session_state.discovery_movie is not None:
        movie = st.session_state.discovery_movie 
        movie_id_disc = int(movie['movieId'])
        title = movie.get('title', 'N/A')
        trailer_url = movie.get('trailer_url')
        year_str = f"({int(movie['date'])})" if pd.notna(movie.get('date')) else "" 
        st.markdown(f"<div class='discovery-container'>", unsafe_allow_html=True)
        st.markdown(f"<h3 class='discovery-title'>{title} </h3>", unsafe_allow_html=True)
        if trailer_url and "youtube.com/watch?v=" in trailer_url:
            try: st.video(trailer_url)
            except Exception as e: st.error(f"Could not load video: {trailer_url}. Error: {e}"); st.markdown(f"You can try watching the [trailer on YouTube]({trailer_url}).")
        elif trailer_url: st.markdown(f"🎬 [View the trailer (external link)]({trailer_url})")
        else: st.info("Trailer link not available for this movie.")
        st.markdown('<div class="movie-card-actions" style="max-width: 400px; margin: 20px auto 0 auto;">', unsafe_allow_html=True)
        def discovery_details_action():
            st.session_state.selected_movie_id = movie_id_disc
            st.session_state.viewing_genre_page = None; st.session_state.viewing_actor_page = None; st.session_state.viewing_director_page = None;
            st.session_state.viewing_full_list_details = None 
            st.session_state.previous_view_state = {
                'view_type': 'discovery_page',
                'discovery_movie_context': st.session_state.discovery_movie.to_dict(), 
                'current_user_id': current_user_id_disc,
                'current_user_name': st.session_state.get('current_user_name')
                }
            st.session_state.discovery_movie = None 
        render_action_button(f"🔍 View Details", "details-button-class", discovery_details_action, key=f"details_discovery_{movie_id_disc}")
        if current_user_id_disc:
            def discovery_watchlist_action(): toggle_watchlist(current_user_id_disc, movie_id_disc)
            in_watchlist_disc = is_in_watchlist(current_user_id_disc, movie_id_disc)
            label_disc = "➖ Watchlist" if in_watchlist_disc else "➕ Watchlist"
            class_disc = "watchlist-remove-class" if in_watchlist_disc else "watchlist-add-class"
            render_action_button(label_disc, class_disc, discovery_watchlist_action, key=f"watchlist_discovery_{movie_id_disc}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown(f"</div>", unsafe_allow_html=True)
    else: st.info("Click 'New Random Discovery' to start!")

def show_movies_for_person(person_name, person_type, user_id, user_name): 
    person_type_label = "actor" if person_type == "actor" else "director"
    st.markdown(f'<h2 class="page-title">Movies with {person_type_label}: {person_name}</h2>', unsafe_allow_html=True)

    if st.button(f"⬅️ Back", key=f"back_from_{person_type}_page"):
        prev_state = st.session_state.get('previous_view_state', {})
        st.session_state.selected_movie_id = prev_state.get('selected_movie_id')
        st.session_state.current_user_id = prev_state.get('current_user_id', user_id) 
        st.session_state.current_user_name = prev_state.get('current_user_name', user_name) 
        st.session_state.viewing_full_list_details = prev_state.get('full_list_context')
        st.session_state[f'viewing_{person_type}_page'] = None 
        st.session_state.previous_view_state = {} 
        st.rerun()

    st.caption("Displaying movies from the entire application catalog.")
    movies_to_filter = df_global.drop_duplicates(subset=['movieId']).copy() 

    if person_type == "actor":
        person_filtered_movies_df = movies_to_filter[
            movies_to_filter['actors'].str.split('|').apply(
                lambda x: person_name.strip() in [a.strip() for a in x] if isinstance(x, list) else False
            )
        ].sort_values(by="user_score", ascending=False, na_position='last')
    elif person_type == "director":
        person_filtered_movies_df = movies_to_filter[
            movies_to_filter['director'].str.split(',').apply(
                lambda x: person_name.strip() in [d.strip() for d in x] if isinstance(x, list) else False
            )
        ].sort_values(by="user_score", ascending=False, na_position='last')
    else:
        st.error("Unrecognized person type.")
        return

    if person_filtered_movies_df.empty:
        st.info(f"No movies found with {person_type_label} '{person_name}' in the entire catalog.")
        return

    st.markdown(f"**{len(person_filtered_movies_df)} movie(s) found.**")
    movies_per_row = st.select_slider("Movies per row:", options=[3, 4, 5, 6, 7, 8], value=5, key=f"{person_type}_page_movies_per_row")

    num_movies = len(person_filtered_movies_df)
    num_rows = (num_movies + movies_per_row - 1) // movies_per_row

    for i_row in range(num_rows):
        cols = st.columns(movies_per_row)
        for j_col in range(movies_per_row):
            movie_idx = i_row * movies_per_row + j_col
            if movie_idx < num_movies:
                movie_item = person_filtered_movies_df.iloc[movie_idx]
                with cols[j_col]:
                    st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                    display_movie_card_with_actions(movie_item, user_id, key_suffix=f"{person_type}_{person_name.replace(' ','_')}_{i_row}_{j_col}")
                    st.markdown('</div>', unsafe_allow_html=True)

def show_movies_for_specific_genre(genre_name, user_id, user_name):
    st.markdown(f'<h2 class="page-title">Movies in Genre: {genre_name}</h2>', unsafe_allow_html=True)

    if st.button(f"⬅️ Back", key=f"back_from_genre_page_{genre_name.replace(' ', '_')}"):
        prev_state = st.session_state.get('previous_view_state', {})
        st.session_state.selected_movie_id = prev_state.get('selected_movie_id')
        st.session_state.current_user_id = prev_state.get('current_user_id', user_id)
        st.session_state.current_user_name = prev_state.get('current_user_name', user_name)
        st.session_state.viewing_full_list_details = prev_state.get('full_list_context')
        st.session_state.viewing_genre_page = None
        st.session_state.previous_view_state = {}
        st.rerun()

    st.caption("Displaying movies from the entire application catalog.")
    movies_to_filter = df_global.drop_duplicates(subset=['movieId']).copy()

    genre_filtered_movies_df = movies_to_filter[
        movies_to_filter['genres'].str.contains(f"\\b{re.escape(genre_name.strip())}\\b", case=False, na=False, regex=True)
    ].sort_values(by="user_score", ascending=False, na_position='last')

    if genre_filtered_movies_df.empty:
        st.info(f"No movies found for the genre '{genre_name}' in the entire catalog.")
        return

    st.markdown(f"**{len(genre_filtered_movies_df)} movie(s) found.**")
    movies_per_row = st.select_slider("Movies per row:", options=[3, 4, 5, 6, 7, 8], value=5, key=f"genre_page_movies_per_row_{genre_name.replace(' ', '_')}")

    num_movies = len(genre_filtered_movies_df)
    num_rows = (num_movies + movies_per_row - 1) // movies_per_row

    for i_row in range(num_rows):
        cols = st.columns(movies_per_row)
        for j_col in range(movies_per_row):
            movie_idx = i_row * movies_per_row + j_col
            if movie_idx < num_movies:
                movie_item = genre_filtered_movies_df.iloc[movie_idx]
                with cols[j_col]:
                    st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                    display_movie_card_with_actions(movie_item, user_id, key_suffix=f"genre_{genre_name.replace(' ','_')}_{i_row}_{j_col}")
                    st.markdown('</div>', unsafe_allow_html=True)

def show_movie_row_simplified(all_movies_data, user_id_for_actions, section_id_tag, section_title_text, max_films_initial=6, total_count_override=None):
    if not all_movies_data and total_count_override is None:
        return

    st.markdown('<div class="section-header-container">', unsafe_allow_html=True)
    st.markdown(f'<h3 class="genre-title">{section_title_text}</h3>', unsafe_allow_html=True)
    
    valid_movies_data = [m for m in all_movies_data if isinstance(m, (dict, pd.Series))]
    
    display_count = total_count_override if total_count_override is not None else len(valid_movies_data)

    if display_count > max_films_initial:
        st.markdown('<div class="see-all-button-container">', unsafe_allow_html=True)
        button_key = f"see_all_{section_id_tag}"
        if st.button(f"See all ({display_count}) →", key=button_key): 
            st.session_state.viewing_full_list_details = {
                'title': section_title_text, 
                'movies': valid_movies_data, 
                'source_section_id': section_id_tag 
            }
            st.session_state.selected_movie_id = None 
            st.session_state.viewing_genre_page = None 
            st.session_state.viewing_actor_page = None
            st.session_state.viewing_director_page = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    with st.container(): 
        st.markdown('<div class="movie-row-simple">', unsafe_allow_html=True)
        if not valid_movies_data:
            st.markdown('</div>', unsafe_allow_html=True) 
            return

        movies_to_display_initially = valid_movies_data[:max_films_initial]
        if not movies_to_display_initially:
            st.markdown('</div>', unsafe_allow_html=True)
            return

        cols_list = st.columns(min(len(movies_to_display_initially), max_films_initial))
        for i_idx, movie_input in enumerate(movies_to_display_initially):
            if isinstance(movie_input, dict): 
                movie_item_for_card = pd.Series(movie_input)
            elif isinstance(movie_input, pd.Series): 
                movie_item_for_card = movie_input 
            else:
                continue
            
            if 'movieId' not in movie_item_for_card or pd.isna(movie_item_for_card['movieId']):
                continue

            with cols_list[i_idx]:
                st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                display_movie_card_with_actions(movie_item_for_card, user_id_for_actions, key_suffix=f"{section_id_tag}_{int(movie_item_for_card['movieId'])}_{i_idx}") 
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def show_full_movie_list_page():
    list_details = st.session_state.viewing_full_list_details
    if not list_details:
        st.warning("No movie list to display.")
        if st.button("⬅️ Back", key="back_from_empty_full_list"):
            st.session_state.viewing_full_list_details = None
            st.rerun()
        return

    section_title = list_details['title']
    full_movie_list = list_details['movies'] 
    source_section_id = list_details.get('source_section_id', 'full_list') 

    st.markdown(f'<h2 class="page-title">All movies for: {section_title}</h2>', unsafe_allow_html=True)

    back_button_text = "⬅️ Back"
    if "reco" in source_section_id or "user_based" in source_section_id or "latent_factor" in source_section_id or "content_based" in source_section_id:
        back_button_text = "⬅️ Back to Our Recommendations"
    elif "user_library" in source_section_id or "top_rated_library" in source_section_id or "genre_reco_library" in source_section_id or "recent_reco_library" in source_section_id:
        back_button_text = "⬅️ Back to All Recommended Movies"

    if st.button(back_button_text, key=f"back_from_full_list_{source_section_id}"): 
        st.session_state.viewing_full_list_details = None
        st.rerun()

    if not full_movie_list:
        st.info("There are no movies in this list.") 
        return

    current_user_id = st.session_state.get('current_user_id')
    st.markdown(f"**{len(full_movie_list)} movie(s) in total.**") 
    movies_per_row = st.select_slider("Movies per row:", options=[3, 4, 5, 6, 7, 8], value=5, key=f"full_list_movies_per_row_{source_section_id}") 
    
    num_movies = len(full_movie_list)
    num_rows = (num_movies + movies_per_row - 1) // movies_per_row

    for i_row in range(num_rows):
        cols = st.columns(movies_per_row)
        for j_col in range(movies_per_row):
            movie_idx = i_row * movies_per_row + j_col
            if movie_idx < num_movies:
                movie_item_data = full_movie_list[movie_idx]
                if isinstance(movie_item_data, dict):
                    movie_item_series = pd.Series(movie_item_data)
                else: 
                    movie_item_series = movie_item_data

                if 'movieId' not in movie_item_series or pd.isna(movie_item_series['movieId']):
                    with cols[j_col]: st.error("Invalid movie data."); continue

                with cols[j_col]:
                    st.markdown('<div class="movie-card-grid-item">', unsafe_allow_html=True)
                    display_movie_card_with_actions(movie_item_series, current_user_id, key_suffix=f"full_list_{source_section_id}_{int(movie_item_series['movieId'])}_{i_row}_{j_col}")
                    st.markdown('</div>', unsafe_allow_html=True)

def show_main_view():
    user_id_current = st.session_state.current_user_id
    user_name_current = st.session_state.current_user_name

    st.markdown(f"""
    <div class="user-specific-header">
        <h2><span class="header-username">{user_name_current}</span></h2>
        <p>Our Recommendations, Watched Movies, Profile, Discovery, and Watchlist</p> 
    </div>""", unsafe_allow_html=True) 

    if st.button("👥 Switch User", type="secondary", key="change_user_main_grid"): 
        st.session_state.current_user_id = None; st.session_state.current_user_name = None
        st.session_state.selected_movie_id = None; st.session_state.viewing_genre_page = None
        st.session_state.viewing_actor_page = None; st.session_state.viewing_director_page = None;
        st.session_state.viewing_full_list_details = None 
        st.session_state.discovery_movie = None; st.rerun()

    user_df_current_library = df_global[df_global["user_id"] == user_id_current].drop_duplicates(subset=['movieId']).copy()
    user_df_current_library = user_df_current_library.sort_values(by="user_score", ascending=False, na_position='last')
    
    user_library_movie_ids = set(user_df_current_library['movieId'].unique())

    tab_titles = ["🌟 Our Recommendations", "📚 All Movies", "✔️ Watched Movies", "👤 Profile", "🎲 Discovery", "🍿 My Watchlist"] 
    tab_reco, tab_my_library, tab_watched, tab_profile, tab_discovery, tab_watchlist = st.tabs(tab_titles)

    with tab_reco:
        st.markdown("### ✨ Our Top Picks For You") 
        any_recos_shown = False
        max_initial_display = 6

        title_user_based = "👥 Based on Similar Users' Tastes" 
        if not df_reco_user_based.empty:
            full_user_based_recos = get_precomputed_recommendations_for_user(df_reco_user_based, user_id_current, user_library_df=None, num_recommendations=-1, exclude_from_library=False)
            total_count = len(full_user_based_recos)
            display_recos = [reco for reco in full_user_based_recos if reco['movieId'] not in user_library_movie_ids]
            if display_recos:
                show_movie_row_simplified(display_recos, user_id_current, "user_based_reco", title_user_based, max_films_initial=max_initial_display, total_count_override=total_count)
                any_recos_shown = True

        title_latent = "🧬 Based on Your Profile & Rating Habits" 
        if not df_reco_latent_factor.empty:
            full_latent_factor_recos = get_precomputed_recommendations_for_user(df_reco_latent_factor, user_id_current, user_library_df=None, num_recommendations=-1, exclude_from_library=False)
            total_count = len(full_latent_factor_recos)
            display_recos = [reco for reco in full_latent_factor_recos if reco['movieId'] not in user_library_movie_ids]
            if display_recos:
                show_movie_row_simplified(display_recos, user_id_current, "latent_factor_reco", title_latent, max_films_initial=max_initial_display, total_count_override=total_count)
                any_recos_shown = True

        title_content = "🌟 More Choices Based on Content" 
        if not df_reco_content_pool.empty:
            full_content_recos = get_precomputed_recommendations_for_user(df_reco_content_pool, user_id_current, user_library_df=None, num_recommendations=-1, exclude_from_library=False)
            total_count = len(full_content_recos)
            display_recos = [reco for reco in full_content_recos if reco['movieId'] not in user_library_movie_ids]
            if display_recos:
                show_movie_row_simplified(display_recos, user_id_current, "content_based_reco", title_content, max_films_initial=max_initial_display, total_count_override=total_count)
                any_recos_shown = True
        
        st.divider()
        st.markdown("### 🎬 Suggestions Based on All Recommended Movies") 

        if not user_df_current_library.empty:
            any_recos_shown = True 
            title_top_rated = "🏆 Top Rated of All Recommended Movies" 
            all_top_rated_movies_from_library = user_df_current_library.head(30).to_dict('records')
            if all_top_rated_movies_from_library:
                show_movie_row_simplified(all_top_rated_movies_from_library, user_id_current, "top_rated_library", title_top_rated, max_films_initial=max_initial_display)

            genre_movies_reco_all = {}
            for _, row_item_series in user_df_current_library.iterrows():
                if pd.notna(row_item_series.get("genres")):
                    genres_list_item = [g.strip() for g in str(row_item_series["genres"]).split('|') if g.strip()]
                    for genre_item_loop in genres_list_item:
                        if genre_item_loop not in genre_movies_reco_all:
                            genre_movies_reco_all[genre_item_loop] = []
                        genre_movies_reco_all[genre_item_loop].append(row_item_series.to_dict())
            
            for genre_display, full_movies_list_for_genre in sorted(genre_movies_reco_all.items()):
                if len(full_movies_list_for_genre) >= 3:
                    sorted_movies_for_genre = sorted(full_movies_list_for_genre, key=lambda x: x.get('user_score', 0) if pd.notna(x.get('user_score')) else 0, reverse=True)
                    title_genre_specific = f"🍿 In the mood for great {genre_display} movies? We have the perfect list:" 
                    show_movie_row_simplified(sorted_movies_for_genre, user_id_current, f"genre_reco_library_{genre_display.replace(' ', '_')}", title_genre_specific, max_films_initial=max_initial_display)
            
            title_recent = "🆕 Recently Added to Our Recommendations"
            max_year_val = user_df_current_library['date'].max() if not user_df_current_library['date'].dropna().empty else pd.Timestamp('now').year
            all_recent_movies_df = user_df_current_library[user_df_current_library['date'] >= max_year_val - 5]
            all_recent_movies_list = all_recent_movies_df.sort_values(by='date', ascending=False).to_dict('records')
            if all_recent_movies_list:
                show_movie_row_simplified(all_recent_movies_list, user_id_current, "recent_reco_library", title_recent, max_films_initial=max_initial_display)
        
        if not any_recos_shown:
             st.info(f"No recommendations to display for {user_name_current} at the moment.") 
                
    with tab_my_library:
        show_my_library_with_filters(user_df_current_library)
    with tab_watched:
        show_watched_movies_page()
    with tab_profile: 
        show_user_profile(user_df_current_library, user_name_current)
    with tab_discovery: 
        show_discovery_page(user_df_current_library)
    with tab_watchlist: 
        show_watchlist_page()

def show_movie_details(movie_id_param_detail):
    movie_data_source = pd.DataFrame()

    current_user_id_detail_s = st.session_state.get('current_user_id')
    if current_user_id_detail_s: 
        temp_source_user_library = df_global[(df_global["movieId"] == movie_id_param_detail) & (df_global["user_id"] == current_user_id_detail_s)]
        if not temp_source_user_library.empty:
            movie_data_source = temp_source_user_library

    if movie_data_source.empty: 
        temp_source_global_catalog = df_global[df_global["movieId"] == movie_id_param_detail]
        if not temp_source_global_catalog.empty:
            movie_data_source = temp_source_global_catalog.drop_duplicates(subset=['movieId'], keep='first')

    if movie_data_source.empty: 
        pools_to_check = [df_reco_user_based, df_reco_latent_factor, df_reco_content_pool]
        for pool_df in pools_to_check:
            if pool_df is not None and not pool_df.empty and 'movieId' in pool_df.columns:
                temp_source_pool = pool_df[pool_df["movieId"] == movie_id_param_detail]
                if not temp_source_pool.empty:
                    movie_data_source = temp_source_pool.drop_duplicates(subset=['movieId'], keep='first') 
                    break

    if movie_data_source.empty:
        st.error(f"❌ Movie ID {movie_id_param_detail} not found in any data source.")
        st.session_state.selected_movie_id = None
        if st.button("⬅️ Back", key="error_return_details_page"):
            st.rerun()
        return

    movie_item_detail = movie_data_source.iloc[0].copy() 

    current_user_name_detail = st.session_state.get('current_user_name', 'this user') 
    current_user_id_detail = st.session_state.get('current_user_id') 

    title_str = movie_item_detail.get('title', 'Unknown Title')
    title_year_detail = title_str
    if pd.notna(movie_item_detail.get('date')):
        try:
            movie_year = int(movie_item_detail['date'])
            title_str_no_year = re.sub(r'\s*\(\d{4}\)$', '', title_str).strip() 
            title_year_detail = f"{title_str_no_year} ({movie_year})"
        except (ValueError, TypeError):
            pass 

    col_title_details, col_watchlist_details_action = st.columns([0.8, 0.2])
    with col_title_details:
        st.markdown(f"<h1 style='color: #e50914; margin-bottom: 10px; margin-top:0;'>🎬 {title_year_detail}</h1>", unsafe_allow_html=True)

    with col_watchlist_details_action:
        if current_user_id_detail: 
            st.markdown("<div style='margin-top: 10px;'>", unsafe_allow_html=True) 
            in_watchlist = is_in_watchlist(current_user_id_detail, movie_id_param_detail)
            watchlist_label = "➖ Watchlist" if in_watchlist else "➕ Watchlist"
            watchlist_class = "watchlist-remove-class" if in_watchlist else "watchlist-add-class"
            def details_watchlist_action(): toggle_watchlist(current_user_id_detail, movie_id_param_detail)
            render_action_button(watchlist_label, watchlist_class, details_watchlist_action, key=f"watchlist_details_page_{movie_id_param_detail}")
            st.markdown("</div>", unsafe_allow_html=True)

    if st.button(f"⬅️ Back", key="details_back_button_main_menu"):
        st.session_state.selected_movie_id = None 
        prev_state = st.session_state.get('previous_view_state', {})
        if prev_state.get('full_list_context'):
            st.session_state.viewing_full_list_details = prev_state['full_list_context']
        else: 
            st.session_state.viewing_full_list_details = None
            st.session_state.viewing_genre_page = prev_state.get('viewing_genre_page')
            st.session_state.viewing_actor_page = prev_state.get('viewing_actor_page')
            st.session_state.viewing_director_page = prev_state.get('viewing_director_page')
            if prev_state.get('discovery_movie_context'): 
                 st.session_state.discovery_movie = pd.Series(prev_state.get('discovery_movie_context'))
        st.session_state.current_user_id = prev_state.get('current_user_id', st.session_state.current_user_id)
        st.session_state.current_user_name = prev_state.get('current_user_name', st.session_state.current_user_name)
        st.session_state.previous_view_state = {} 
        st.rerun()

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        score_val = movie_item_detail.get('user_score')
        st.metric(label="👤 TMDB Score", value=f"{score_val:.0f}/100" if pd.notna(score_val) else "N/A")
    with metric_col2:
        date_val = movie_item_detail.get('date')
        try: year_val_metric = int(date_val) if pd.notna(date_val) else "Unknown"
        except (ValueError, TypeError): year_val_metric = "Unknown"
        st.metric(label="📅 Year", value=year_val_metric)
    with metric_col3:
        tmdb_id_val = movie_item_detail.get('tmdbId')
        try: tmdb_id_int = int(float(tmdb_id_val)) if pd.notna(tmdb_id_val) and str(tmdb_id_val).strip() != '' else "N/A"
        except (ValueError, TypeError): tmdb_id_int = "N/A"
        st.metric(label="🆔 TMDB ID", value=tmdb_id_int)
    st.divider()

    col_poster_detail, col_info_detail = st.columns([1, 2])
    with col_poster_detail:
        poster_path_detail = os.path.join("posters_tmdb", f"{movie_id_param_detail}.jpg")
        if os.path.exists(poster_path_detail):
            st.image(poster_path_detail, width=300, caption=f"Poster - {movie_item_detail.get('title', '')}")
        else:
            st.markdown(f"""<div style="width: 300px; height: 450px; background: #282828; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 12px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.2);"><div style="font-size: 48px; margin-bottom: 10px;">🎬</div><div style="font-size: 16px; font-weight: bold;">Poster Not Available</div><div style="font-size: 12px; opacity: 0.8; margin-top: 5px;">{movie_item_detail.get('title', '')}</div></div>""", unsafe_allow_html=True)

        trailer_url_detail = movie_item_detail.get('trailer_url')
        if pd.notna(trailer_url_detail) and str(trailer_url_detail).strip():
            st.markdown("---"); st.markdown("### 🎥 Trailer")
            if "youtube.com/watch?v=" in str(trailer_url_detail):
                try:
                    video_id_yt = str(trailer_url_detail).split("v=")[1].split("&")[0] 
                    st.video(f"https://www.youtube.com/watch?v={video_id_yt}")
                except: 
                    st.markdown(f"[▶️ Watch on YouTube]({trailer_url_detail})")
            else: 
                st.markdown(f"[▶️ View Trailer]({trailer_url_detail})")

    with col_info_detail:
        st.markdown("### 📋 Detailed Information")
        genres_detail_str = movie_item_detail.get('genres')
        if pd.notna(genres_detail_str) and str(genres_detail_str).strip():
            st.markdown("**🎭 Genres** (click to explore)")
            genres_list_detail = [g.strip() for g in str(genres_detail_str).split('|') if g.strip()]
            num_genre_buttons = len(genres_list_detail)
            if num_genre_buttons > 0:
                genre_cols_per_row = min(num_genre_buttons, 4) 
                for i in range(0, num_genre_buttons, genre_cols_per_row):
                    cols_genres = st.columns(genre_cols_per_row)
                    for j in range(genre_cols_per_row):
                        if i + j < num_genre_buttons:
                            genre_item = genres_list_detail[i+j]
                            with cols_genres[j]:
                                if st.button(genre_item, key=f"genre_nav_details_{genre_item.replace(' ','_')}_{movie_id_param_detail}_{i+j}", help=f"View movies in the {genre_item} genre", use_container_width=True):
                                    st.session_state.viewing_genre_page = genre_item
                                    st.session_state.previous_view_state = {
                                        'view_type': 'movie_details', 'selected_movie_id': movie_id_param_detail,
                                        'current_user_id': current_user_id_detail, 'current_user_name': current_user_name_detail,
                                        'full_list_context': st.session_state.get('viewing_full_list_details')
                                    }
                                    st.session_state.selected_movie_id = None
                                    st.session_state.viewing_full_list_details = None
                                    st.rerun()
            st.markdown("") 

        director_detail_str = movie_item_detail.get('director')
        if pd.notna(director_detail_str) and str(director_detail_str).strip():
            st.markdown(f"**🎬 Director(s):**")
            directors_list_detail = [d.strip() for d in str(director_detail_str).split(',') if d.strip()]
            director_cols_per_row = min(len(directors_list_detail), 3)
            for i in range(0, len(directors_list_detail), director_cols_per_row):
                cols_directors = st.columns(director_cols_per_row)
                for j in range(director_cols_per_row):
                    if i + j < len(directors_list_detail):
                        director_item = directors_list_detail[i+j]
                        with cols_directors[j]:
                            if st.button(director_item, key=f"director_nav_details_{director_item.replace(' ','_')}_{movie_id_param_detail}_{i+j}", help=f"View movies by {director_item}", use_container_width=True):
                                st.session_state.viewing_director_page = director_item
                                st.session_state.previous_view_state = {
                                    'view_type': 'movie_details', 'selected_movie_id': movie_id_param_detail,
                                    'current_user_id': current_user_id_detail, 'current_user_name': current_user_name_detail,
                                    'full_list_context': st.session_state.get('viewing_full_list_details')
                                }
                                st.session_state.selected_movie_id = None
                                st.session_state.viewing_full_list_details = None
                                st.rerun()
            st.markdown("")

        actors_detail_str = movie_item_detail.get('actors')
        if pd.notna(actors_detail_str) and str(actors_detail_str).strip():
            st.markdown("**🌟 Main Actors:** (click to explore)")
            actors_list_detail = [a.strip() for a in str(actors_detail_str).split('|') if a.strip()]
            actors_to_show = actors_list_detail[:8] 
            actor_cols_per_row = min(len(actors_to_show), 4)
            if actors_to_show:
                for i in range(0, len(actors_to_show), actor_cols_per_row):
                    cols_actors = st.columns(actor_cols_per_row)
                    for j in range(actor_cols_per_row):
                        if i + j < len(actors_to_show):
                            actor_name = actors_to_show[i+j]
                            with cols_actors[j]:
                                if st.button(actor_name, key=f"actor_nav_details_{actor_name.replace(' ','_')}_{movie_id_param_detail}_{i+j}", help=f"View movies with {actor_name}", use_container_width=True):
                                    st.session_state.viewing_actor_page = actor_name
                                    st.session_state.previous_view_state = {
                                        'view_type': 'movie_details', 'selected_movie_id': movie_id_param_detail,
                                        'current_user_id': current_user_id_detail, 'current_user_name': current_user_name_detail,
                                        'full_list_context': st.session_state.get('viewing_full_list_details')
                                    }
                                    st.session_state.selected_movie_id = None
                                    st.session_state.viewing_full_list_details = None
                                    st.rerun()
                if len(actors_list_detail) > 8:
                    st.markdown(f"*... and {len(actors_list_detail) - 8} more.*")
            st.markdown("") 

        st.markdown("---"); st.markdown("**🔍 Technical IDs**"); id_col_a, id_col_b = st.columns(2)
        with id_col_a:
            st.markdown(f"**Movie ID (app):** {movie_item_detail['movieId']}")
        with id_col_b:
            if pd.notna(tmdb_id_val) and str(tmdb_id_val).strip() != '': 
                 st.markdown(f"**TMDB ID:** {tmdb_id_int}")
            if 'user_id' in movie_item_detail and pd.notna(movie_item_detail.get('user_id')): 
                try:
                    st.markdown(f"**User ID (source):** {int(movie_item_detail['user_id'])}")
                except (ValueError, TypeError):
                    st.markdown(f"**User ID (source):** {movie_item_detail['user_id']}")

    synopsis_detail = movie_item_detail.get('synopsis')
    if pd.notna(synopsis_detail) and str(synopsis_detail).strip():
        st.markdown("---"); st.markdown("### 📖 Synopsis")
        st.markdown(f"""<div style="background-color: #282828; padding: 20px; border-radius: 10px; border-left: 4px solid #e50914; line-height: 1.6; color: #f5f5f1;">{synopsis_detail}</div>""", unsafe_allow_html=True)
    st.markdown("---")
    
    current_user_id_for_reco_detail_page = st.session_state.get('current_user_id', None)
    if current_user_id_for_reco_detail_page:
        user_library_for_reco_detail = df_global[df_global["user_id"] == current_user_id_for_reco_detail_page].drop_duplicates(subset=['movieId']).copy()
        main_movie_genres_str = movie_item_detail.get('genres')

        if pd.notna(main_movie_genres_str) and str(main_movie_genres_str).strip() and not user_library_for_reco_detail.empty:
            main_movie_genres = [genre.strip() for genre in str(main_movie_genres_str).split('|') if genre.strip()]
            already_recommended_movie_ids = {movie_id_param_detail} 
            
            st.markdown(f"### 🍿 More movies like this (from our recommendations)") 
            for i, genre_to_match in enumerate(main_movie_genres):
                if not genre_to_match: continue
                title_related_genre = f"Similar Genre: {genre_to_match} (from our recommendations)" 
                
                all_related_movies_for_genre = user_library_for_reco_detail[
                    user_library_for_reco_detail['genres'].str.contains(f"\\b{re.escape(genre_to_match)}\\b", case=False, na=False, regex=True) &
                    (user_library_for_reco_detail['movieId'] != movie_id_param_detail) &
                    (~user_library_for_reco_detail['movieId'].isin(already_recommended_movie_ids)) 
                ].sort_values(by="user_score", ascending=False, na_position='last').to_dict('records')

                if all_related_movies_for_genre:
                    show_movie_row_simplified(
                        all_related_movies_for_genre,
                        current_user_id_for_reco_detail_page, 
                        f"related_detail_page_library_genre_{genre_to_match.replace(' ', '_')}_{i}",
                        title_related_genre,
                        max_films_initial=6
                    )
                    for rec_movie in all_related_movies_for_genre[:6]: 
                        already_recommended_movie_ids.add(rec_movie['movieId'])
                if i >= 1 and len(main_movie_genres) > 2 : 
                    break
    st.markdown("---")

# --- Main display logic ---
if st.session_state.viewing_full_list_details is not None:
    show_full_movie_list_page()
elif st.session_state.viewing_actor_page is not None:
    user_id = st.session_state.get('current_user_id')
    user_name = st.session_state.get('current_user_name')
    if user_id and user_name:
        show_movies_for_person(st.session_state.viewing_actor_page, "actor", user_id, user_name)
    else: 
        st.session_state.viewing_actor_page = None
        show_user_selection()
elif st.session_state.viewing_director_page is not None:
    user_id = st.session_state.get('current_user_id')
    user_name = st.session_state.get('current_user_name')
    if user_id and user_name:
        show_movies_for_person(st.session_state.viewing_director_page, "director", user_id, user_name)
    else:
        st.session_state.viewing_director_page = None
        show_user_selection()
elif st.session_state.viewing_genre_page is not None:
    user_id_genre_page = st.session_state.get('current_user_id')
    user_name_genre_page = st.session_state.get('current_user_name')
    if user_id_genre_page and user_name_genre_page:
        show_movies_for_specific_genre(st.session_state.viewing_genre_page, user_id_genre_page, user_name_genre_page)
    else:
        st.warning("User context lost for genre page. Please select a user again.") 
        st.session_state.viewing_genre_page = None; st.session_state.current_user_id = None; st.session_state.current_user_name = None
        show_user_selection()
elif st.session_state.selected_movie_id is not None:
    show_movie_details(st.session_state.selected_movie_id)
elif st.session_state.current_user_id is not None:
    show_main_view()
else:
    show_user_selection()