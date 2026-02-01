import streamlit as st
import requests
import psycopg2
import pandas as pd
import plotly.express as px
import os
import random
import time

# ---------------- CONFIG ---------------- #
st.set_page_config(page_title="Personalized Content Recommendation System using MAB", layout="centered")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_hyYzdvKVD36u@ep-green-hat-ad09amv9-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
)
API_URL = "http://127.0.0.1:8000"

def get_conn():
    return psycopg2.connect(DATABASE_URL)

# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if not st.session_state["logged_in"]:
    from auth import login_page, signup_page
    page = st.sidebar.radio("Navigation", ["Login", "Sign Up"])
    if page == "Login":
        login_page()
    else:
        signup_page()
    st.stop()

# ---------------- SIDEBAR ---------------- #
st.sidebar.markdown("Navigation")
if st.sidebar.button("Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

st.sidebar.markdown("---")

# ---------------- MAIN TITLE ---------------- #
st.title("Personalized Content Recommendation System using Multi-Armed Bandit")
st.info(f"Logged in as {st.session_state['name']} (@{st.session_state['username']})")

user_id = st.session_state["user_id"]

# ---------------- GENRES ---------------- #
available_genres = [
    "Tech", "Music", "Fitness", "Cooking",
    "Education", "Science", "Travel", "Comedy", "Anime"
]
selected_genres = st.multiselect(
    "🎵 Choose up to 3 Preferred Genres",
    available_genres,
    default=st.session_state.get("genres", []),
    max_selections=3
)
st.session_state["genres"] = selected_genres
if not selected_genres:
    st.warning("Please select at least one genre.")
    st.stop()

# ---------------- RL AGENT ---------------- #
agent = st.selectbox("Select RL Agent", ["thompson", "epsilon"])

# ---------------- RECOMMENDER ---------------- #
st.markdown("---")
st.subheader("Your Personalized Video Feed")

# Session keys
if "current_video" not in st.session_state:
    st.session_state["current_video"] = None
if "current_genre" not in st.session_state:
    st.session_state["current_genre"] = None

def fetch_new_video():
    """Fetch next recommendation from backend."""
    genre = random.choice(selected_genres)
    res = requests.post(f"{API_URL}/recommend", json={
        "user_id": user_id,
        "genre": genre,
        "agent_type": agent
    })
    if res.status_code == 200:
        data = res.json()
        st.session_state["current_video"] = data
        st.session_state["current_genre"] = genre
    else:
        st.error(f"Backend error: {res.status_code} - {res.text}")
        st.session_state["current_video"] = None

def record_feedback(reward: int):
    """Send user feedback and get next video automatically."""
    data = st.session_state["current_video"]
    genre = st.session_state["current_genre"]

    if data:
        try:
            requests.post(f"{API_URL}/feedback", json={
                "user_id": user_id,
                "content_id": data["content_id"],
                "reward": reward,
                "genre": genre,
                "agent_type": agent
            })
        except Exception as e:
            st.error(f"Could not send feedback: {e}")

    # Fetch next video immediately
    time.sleep(0.6)
    fetch_new_video()
    st.rerun()

# ---------------- VIDEO DISPLAY ---------------- #
if st.button("Start Recommendations"):
    fetch_new_video()

data = st.session_state.get("current_video", None)
if data:
    genre = st.session_state["current_genre"]
    st.markdown(f"From: `{genre.title()}`")
    st.subheader(data["title"])

    # Centered medium-size video
    st.markdown(
        f"""
        <div style='display: flex; justify-content: center;'>
            <iframe width="600" height="340" src="{data['url'].replace('watch?v=', 'embed/')}"
            frameborder="0" allowfullscreen></iframe>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👍 Relevant"):
            record_feedback(1)
    with col2:
        if st.button("👎 Not Relevant"):
            record_feedback(0)
else:
    st.info("Click **Start Recommendations** to begin your personalized feed.")

st.caption("💡 After feedback, the next video loads automatically!")

# ---------------- DASHBOARD ---------------- #
st.markdown("---")
st.header("RL Insights Dashboard")

try:
    with get_conn() as conn:
        # 1️ Total reward and penalty points
        reward_df = pd.read_sql("""
            SELECT 
                SUM(CASE WHEN reward = 1 THEN 1 ELSE 0 END) AS total_rewards,
                SUM(CASE WHEN reward = 0 THEN 1 ELSE 0 END) AS total_penalties
            FROM interactions
            WHERE user_id = %s
        """, conn, params=(user_id,))
        total_rewards = int(reward_df["total_rewards"][0]) if not reward_df.empty else 0
        total_penalties = int(reward_df["total_penalties"][0]) if not reward_df.empty else 0

        col1, col2 = st.columns(2)
        col1.metric("Reward Points", total_rewards)
        col2.metric("Penalty Points", total_penalties)

        # 2️ Agent-Specific Dashboards
        if agent == "thompson":
            st.subheader("Thompson Sampling Parameters (α / β)")

            model_df = pd.read_sql("""
                SELECT u.genre AS genre, u.alpha, u.beta, c.title
                FROM user_models u
                JOIN content c ON u.content_id = c.id
                WHERE u.user_id = %s
                ORDER BY u.genre
            """, conn, params=(user_id,))

            if not model_df.empty:
                st.dataframe(model_df, use_container_width=True)

                fig = px.scatter(
                    model_df,
                    x="alpha",
                    y="beta",
                    color="genre",
                    hover_data=["title"],
                    title="α (Success) vs β (Failure) across genres"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No α/β data yet — run `trainer.py` to update models.")

            st.caption("Thompson Sampling models user feedback using Bayesian α/β parameters (success & failure counts).")

        elif agent == "epsilon":
            st.subheader("Epsilon-Greedy Performance Overview")

            eps_df = pd.read_sql("""
                SELECT genre,
                       COUNT(*) FILTER (WHERE reward = 1) AS rewards,
                       COUNT(*) FILTER (WHERE reward = 0) AS penalties,
                       ROUND(AVG(reward::numeric), 2) AS avg_success_rate
                FROM interactions
                WHERE user_id = %s AND reward IS NOT NULL
                GROUP BY genre
                ORDER BY avg_success_rate DESC
            """, conn, params=(user_id,))

            if not eps_df.empty:
                st.dataframe(eps_df, use_container_width=True)

                fig = px.bar(
                    eps_df,
                    x="genre",
                    y="avg_success_rate",
                    title="Average Success Rate per Genre (ε-Greedy)",
                    text="avg_success_rate",
                    color="genre"
                )
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No feedback data yet for epsilon agent.")

            st.caption("Note : Epsilon-Greedy explores randomly with probability ε and exploits the best-known genres based on average success rate.")

except Exception as e:
    st.warning(f"Dashboard unavailable: {e}")