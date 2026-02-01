from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import numpy as np
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import bcrypt

# ---------------- ENV & APP ---------------- #
load_dotenv()
app = FastAPI(title="Dynamic RL Recommender API")

DATABASE_URL = os.getenv("DATABASE_URL")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_conn():
    return psycopg2.connect(DATABASE_URL)


# ---------------- REQUEST MODELS ---------------- #
class SignupRequest(BaseModel):
    name: str
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class RecommendRequest(BaseModel):
    user_id: int
    genre: str
    agent_type: str = "thompson"

class FeedbackRequest(BaseModel):
    user_id: int
    content_id: int
    reward: int
    genre: str
    agent_type: str


# ---------------- HELPER FUNCTIONS ---------------- #
def fetch_youtube_videos(genre, max_results=5):
    """Fetch YouTube videos for a given genre."""
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": genre,
        "type": "video",
        "maxResults": max_results
    }
    res = requests.get(url, params=params).json()
    videos = []
    for item in res.get("items", []):
        title = item["snippet"]["title"]
        vid = item["id"]["videoId"]
        videos.append((genre, title, f"https://www.youtube.com/watch?v={vid}"))
    return videos

def thompson_sample(alpha, beta):
    """Thompson Sampling: draw from Beta distribution."""
    return np.random.beta(alpha, beta)

def epsilon_greedy(alpha, beta, epsilon=0.2):
    """Epsilon-Greedy: random exploration with probability ε."""
    if np.random.rand() < epsilon:
        return np.random.rand()  # explore
    return alpha / (alpha + beta)  # exploit


# ---------------- AUTH ENDPOINTS ---------------- #
@app.post("/signup")
def signup(req: SignupRequest):
    conn = get_conn()
    cur = conn.cursor()

    # Check duplicate username
    cur.execute("SELECT id FROM users WHERE username=%s", (req.username,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password & create user
    hashed_pw = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    cur.execute("""
        INSERT INTO users (name, username, password, preferred_genre, created_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (req.name, req.username, hashed_pw, None, datetime.now()))

    user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "user_id": user_id,
        "username": req.username,
        "message": "Account created successfully ✅"
    }


@app.post("/login")
def login(req: LoginRequest):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT id, name, password, preferred_genre FROM users WHERE username=%s", (req.username,))
    user = cur.fetchone()
    conn.close()

    if not user or not bcrypt.checkpw(req.password.encode(), user[2].encode()):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "user_id": user[0],
        "username": req.username,
        "name": user[1],
        "preferred_genre": user[3]
    }


# ---------------- RECOMMENDATION LOGIC ---------------- #
@app.post("/recommend")
def recommend(req: RecommendRequest):
    """
    Selects a recommended video using Thompson Sampling or Epsilon-Greedy.
    Does NOT log any reward automatically — waits for explicit user feedback.
    """
    conn = get_conn()
    cur = conn.cursor()

    # 1️ Get available videos in this genre
    cur.execute("SELECT id, title, url FROM content WHERE genre=%s", (req.genre,))
    contents = cur.fetchall()

    # 2️ If none, fetch new YouTube data
    if not contents:
        videos = fetch_youtube_videos(req.genre)
        for g, t, u in videos:
            cur.execute("INSERT INTO content (genre, title, url) VALUES (%s, %s, %s)", (g, t, u))
        conn.commit()
        cur.execute("SELECT id, title, url FROM content WHERE genre=%s", (req.genre,))
        contents = cur.fetchall()

    # 3️ Load user model (α, β)
    cur.execute("SELECT content_id, alpha, beta FROM user_models WHERE user_id=%s AND genre=%s",
                (req.user_id, req.genre))
    user_model = {cid: (a, b) for cid, a, b in cur.fetchall()}

    # 4️ Compute scores
    scores = []
    for cid, title, url in contents:
        alpha, beta = user_model.get(cid, (1, 1))
        score = epsilon_greedy(alpha, beta) if req.agent_type == "epsilon" else thompson_sample(alpha, beta)
        scores.append((cid, title, url, score))

    # 5 Choose the best-scoring video
    best = max(scores, key=lambda x: x[3])

    conn.close()
    return {
        "content_id": best[0],
        "title": best[1],
        "url": best[2],
        "agent_type": req.agent_type
    }


# ---------------- FEEDBACK LOGIC ---------------- #
@app.post("/feedback")
def feedback(req: FeedbackRequest):
    """
    Stores explicit user feedback (1 for relevant, 0 for not relevant).
    This is the ONLY place reward values are inserted.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO interactions (user_id, content_id, agent_type, reward, genre, ts)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        req.user_id, req.content_id, req.agent_type, req.reward, req.genre, datetime.now()
    ))

    conn.commit()
    conn.close()
    return {"status": "Feedback saved successfully!"}