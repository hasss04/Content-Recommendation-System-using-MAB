# 🎯 Personalized Content Recommendation System using Multi-Armed Bandit

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-NeonDB-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

*A real-time adaptive recommendation engine powered by Reinforcement Learning*

[Features](#-features) • [Demo](#-how-it-works) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture)

</div>

---

## 📖 Overview

This project implements a **self-learning personalized video recommendation system** that continuously adapts to user preferences using **Multi-Armed Bandit (MAB)** algorithms. Unlike traditional recommender systems that require massive datasets and struggle with cold-start problems, this RL-based approach learns efficiently from minimal user feedback in real-time.

### Why Multi-Armed Bandit?

- ✅ **No Cold Start Problem**: Starts learning from the first interaction
- ✅ **Real-time Adaptation**: Updates preferences after every feedback
- ✅ **Exploration-Exploitation Balance**: Discovers new content while serving preferred genres
- ✅ **Lightweight**: No need for deep learning or extensive historical data

---

## ✨ Features

- 🤖 **Dual RL Algorithms**: Thompson Sampling (Bayesian) & Epsilon-Greedy
- ⚡ **Real-time Learning**: Updates user models after every interaction
- 🎬 **YouTube Integration**: Fetches videos dynamically via YouTube Data API v3
- 📊 **Interactive Dashboard**: Visualizes α–β parameters, success rates, and reward metrics
- 🔐 **Secure Authentication**: bcrypt-hashed passwords with PostgreSQL storage
- 🌐 **Cloud-Ready**: NeonDB PostgreSQL for scalable persistence
- 📈 **Live Metrics**: Track exploration vs exploitation balance in real-time

---

## 🎯 How It Works

### Multi-Armed Bandit Approach

Each **genre** is treated as an "arm" in a slot machine. The system learns which arms (genres) yield the highest rewards (user engagement) through continuous feedback.

```
User Action → Feedback (👍/👎) → Model Update → Better Recommendations
```

### Algorithm Comparison

| Algorithm | Exploration Strategy | Adaptation | Best For |
|-----------|---------------------|------------|----------|
| **Thompson Sampling** | Probability matching via Beta(α, β) | Fully adaptive (Bayesian updates) | Long-term personalization |
| **Epsilon-Greedy** | Random ε% of the time | Fixed exploration rate | Baseline comparison |

#### 🔵 Thompson Sampling

**How it works:**
- Models each genre's success probability using a Beta distribution
- Parameters: α (successes) and β (failures)
- Samples from Beta(α, β) and picks the highest value

```python
def thompson_sample(alpha, beta):
    return np.random.beta(alpha, beta)
```

**Updates:**
- 👍 Relevant → α increases
- 👎 Not Relevant → β increases

**Interpretation:**
- **(1,1)**: No prior preference (uniform distribution)
- **(5,1)**: Genre is preferred (skewed toward success)
- **(1,5)**: Genre is disliked (skewed toward failure)

#### 🟢 Epsilon-Greedy

**How it works:**
- With probability ε (20%), explores randomly
- Otherwise, exploits the best-known genre

```python
def epsilon_greedy(alpha, beta, epsilon=0.2):
    if np.random.rand() < epsilon:
        return np.random.rand()  # Explore
    return alpha / (alpha + beta)  # Exploit
```

**Updates:**
- Calculates average success rate: α / (α + β)
- Fixed exploration rate (non-adaptive)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                    (Streamlit Frontend)                      │
│  • Sign Up / Login                                           │
│  • Genre Selection                                           │
│  • RL Agent Selection                                        │
│  • Video Player + Feedback Buttons                          │
│  • Real-time Dashboard (Plotly Charts)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓ HTTP Requests
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND API                             │
│                    (FastAPI Server)                          │
│                                                              │
│  Endpoints:                                                  │
│  • POST /signup         → Create user account               │
│  • POST /login          → Authenticate user                 │
│  • POST /recommend      → Get RL-based video suggestion     │
│  • POST /feedback       → Record user feedback              │
│                                                              │
│  RL Logic:                                                   │
│  • thompson_sample(α, β)                                    │
│  • epsilon_greedy(α, β, ε)                                  │
│  • fetch_youtube_videos(genre)                              │
└────────────┬────────────────────────┬───────────────────────┘
             │                        │
             ↓                        ↓
┌─────────────────────┐    ┌──────────────────────────────────┐
│   YouTube API v3    │    │     PostgreSQL Database          │
│                     │    │        (NeonDB)                  │
│ • Search videos     │    │                                  │
│ • Fetch metadata    │    │  Tables:                         │
│ • Return URLs       │    │  • users (credentials)           │
└─────────────────────┘    │  • content (videos by genre)     │
                           │  • interactions (feedback logs)  │
                           │  • user_models (α/β parameters)  │
                           └──────────────────────────────────┘
```

### Database Schema

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `users` | User credentials and profiles | `id`, `username`, `password`, `preferred_genre` |
| `content` | YouTube videos by genre | `id`, `genre`, `title`, `url` |
| `interactions` | User feedback logs | `user_id`, `content_id`, `reward`, `agent_type`, `genre` |
| `user_models` | RL parameters (α, β) per user/genre | `user_id`, `genre`, `content_id`, `alpha`, `beta` |

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL database (NeonDB recommended)
- YouTube Data API v3 key ([Get it here](https://console.cloud.google.com/))

### Step 1: Clone Repository

```bash
git clone https://github.com/hasss04/Content-Recommendation-System-using-MAB.git
cd Content-Recommendation-System-using-MAB
```

### Step 2: Install Dependencies

```bash
# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
pip install streamlit plotly pandas psycopg2-binary
```

**Backend requirements** (`backend/requirements.txt`):
```txt
fastapi
uvicorn[standard]
psycopg2-binary
numpy
requests
python-dotenv
bcrypt
pydantic
```

### Step 3: Environment Configuration

Create a `.env` file in the **root directory**:

```env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**Getting YouTube API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **YouTube Data API v3**
4. Create credentials (API Key)
5. Copy the key to `.env`

### Step 4: Database Setup

Run this SQL schema in your PostgreSQL database:

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    preferred_genre VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content table
CREATE TABLE content (
    id SERIAL PRIMARY KEY,
    genre VARCHAR(50) NOT NULL,
    title VARCHAR(255),
    url VARCHAR(255)
);

-- Interactions table
CREATE TABLE interactions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    content_id INT REFERENCES content(id),
    agent_type VARCHAR(20),
    reward INT CHECK (reward IN (0, 1)),
    genre VARCHAR(50),
    ts TIMESTAMP DEFAULT NOW()
);

-- User models table (RL parameters)
CREATE TABLE user_models (
    user_id INT,
    genre VARCHAR(50),
    content_id INT,
    alpha FLOAT DEFAULT 1.0,
    beta FLOAT DEFAULT 1.0,
    last_trained TIMESTAMP,
    PRIMARY KEY (user_id, genre, content_id)
);
```

---

## 💻 Usage

### Method 1: Run Everything at Once (Recommended)

```bash
python run_all.py
```

This will start both the backend API and frontend Streamlit app automatically.

### Method 2: Manual Start

**Terminal 1 - Start Backend API:**
```bash
cd backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`

📌 **API Documentation**: Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI

**Terminal 2 - Run Frontend:**
```bash
cd frontend
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Update RL Models (Optional)

Run the trainer script to batch-update α/β parameters:

```bash
cd backend
python trainer.py
```

> **Note**: The system updates models automatically on each feedback. This script is for batch retraining if needed.

---

## 📱 User Workflow

### 1️⃣ **Authentication**
- Sign up with username and password (bcrypt-hashed)
- Login to access personalized feed

### 2️⃣ **Genre Selection**
- Choose up to 3 preferred genres:
  - Tech, Music, Fitness, Cooking, Education, Science, Travel, Comedy, Anime

### 3️⃣ **RL Agent Selection**
- **Thompson Sampling** (recommended for adaptive learning)
- **Epsilon-Greedy** (baseline with fixed exploration)

### 4️⃣ **Get Recommendations**
- Click "Start Recommendations"
- System randomly picks a genre and uses RL to select best video

### 5️⃣ **Provide Feedback**
- **👍 Relevant** → Reward = 1 → Increase α (success)
- **👎 Not Relevant** → Reward = 0 → Increase β (failure)

### 6️⃣ **Watch Learning Progress**
- Real-time dashboard shows:
  - Total rewards & penalties
  - α/β scatter plots (Thompson Sampling)
  - Success rate bar charts (Epsilon-Greedy)

---

## 📊 Dashboard Insights

### Thompson Sampling Dashboard

**Displays:**
- **α/β Parameter Table**: Shows alpha (successes) and beta (failures) for each genre-video pair
- **Scatter Plot**: Visualizes α vs β across genres
  - Top-right quadrant: Popular content (high α)
  - Bottom-right quadrant: Disliked content (high β)
  - Center: Neutral or new content

**Interpretation:**
```
High α, Low β  → Preferred content
Low α, High β  → Disliked content
Equal α, β     → Uncertain (needs more data)
```

### Epsilon-Greedy Dashboard

**Displays:**
- **Success Rate Table**: Average success rate per genre
- **Bar Chart**: Visual comparison of genre performance

**Interpretation:**
```
Success Rate = α / (α + β)
> 0.7  → Highly preferred
0.4-0.7 → Moderately liked
< 0.4  → Not preferred
```

---

## 🔬 Algorithm Deep Dive

### Thompson Sampling (Bayesian Approach)

**Mathematical Foundation:**
- Uses Beta distribution: `Beta(α, β)`
- Prior: `Beta(1, 1)` (uniform distribution)
- Posterior update:
  - Success → `α = α + 1`
  - Failure → `β = β + 1`

**Advantages:**
- ✅ Naturally balances exploration/exploitation
- ✅ Adapts to changing preferences
- ✅ Probabilistic, not deterministic

**Code Implementation:**
```python
# In backend/main.py (FastAPI backend)
def recommend(req: RecommendRequest):
    # Load user's α, β for each content
    user_model = {cid: (alpha, beta) for cid, alpha, beta in db_results}
    
    # Sample from Beta distribution for each video
    scores = []
    for content_id, title, url in contents:
        alpha, beta = user_model.get(content_id, (1, 1))
        score = np.random.beta(alpha, beta)
        scores.append((content_id, title, url, score))
    
    # Pick highest scoring video
    best = max(scores, key=lambda x: x[3])
    return best
```

### Epsilon-Greedy (Simple Baseline)

**Mathematical Foundation:**
- With probability ε (e.g., 0.2): explore randomly
- With probability 1-ε: exploit best option
- Best option = highest `α / (α + β)`

**Advantages:**
- ✅ Simple and interpretable
- ✅ Guaranteed exploration
- ✅ Good baseline for comparison

**Disadvantages:**
- ❌ Fixed exploration rate (not adaptive)
- ❌ Wastes exploration on poor options

**Code Implementation:**
```python
def epsilon_greedy(alpha, beta, epsilon=0.2):
    if np.random.rand() < epsilon:
        return np.random.rand()  # Random exploration
    return alpha / (alpha + beta)  # Greedy exploitation
```

---

## 🧪 Experimental Results

### Convergence Behavior

| Metric | Thompson Sampling | Epsilon-Greedy |
|--------|------------------|----------------|
| **Convergence Speed** | Faster (adaptive) | Slower (fixed ε) |
| **Final Accuracy** | Higher (personalized) | Moderate |
| **Exploration Efficiency** | Smart (probability-based) | Wasteful (random) |

### Key Findings

1. **Thompson Sampling** adapts faster to user preferences
2. **Epsilon-Greedy** provides consistent baseline performance
3. Both algorithms avoid cold-start problem effectively
4. Real-time model updates crucial for personalization

---

## 📁 Project Structure

```
Content-Recommendation-System-using-MAB/
│
├── backend/
│   ├── main.py                 # FastAPI backend (API endpoints)
│   ├── trainer.py              # Batch RL model updater
│   ├── test_db.py              # Database connection tester
│   ├── requirements.txt        # Backend dependencies
│   └── __pycache__/            # Python cache files
│
├── frontend/
│   ├── app.py                  # Streamlit main application
│   ├── auth.py                 # Authentication logic (signup/login)
│   └── __pycache__/            # Python cache files
│
├── run_all.py                  # Script to start both backend & frontend
├── test.py                     # General testing script
├── .env                        # Environment variables (DO NOT COMMIT)
└── README.md                   # This file
```

---

## 🔮 Future Enhancements

1. **Contextual Bandits**: Incorporate user context (time, device, session length)
2. **NLP Integration**: Analyze video titles/descriptions for semantic matching
3. **Deep RL**: Implement DQN for sequence-based recommendations
4. **A/B Testing**: Compare multiple RL algorithms simultaneously
5. **Docker Deployment**: Containerize for easy cloud deployment
6. **Collaborative Filtering**: Hybrid approach combining MAB + CF
7. **Multi-Platform Support**: Extend beyond YouTube (Spotify, Netflix, etc.)

---

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Error**
```
Error: could not connect to server
```
**Solution**: 
- Check `DATABASE_URL` in `.env` file
- Ensure PostgreSQL/NeonDB is running
- Verify database credentials
- Test connection with `python backend/test_db.py`

**2. YouTube API Quota Exceeded**
```
Error: quotaExceeded
```
**Solution**: 
- YouTube API has daily limits (10,000 units/day)
- Wait 24 hours or use another API key
- Reduce `max_results` parameter in `fetch_youtube_videos()`

**3. Backend Not Running**
```
Error: Could not connect to backend API
```
**Solution**: 
- Ensure FastAPI is running: `cd backend && uvicorn main:app --reload`
- Check if port 8000 is already in use
- Verify API_URL in `frontend/app.py` matches backend address

**4. No Videos Showing**
```
Info: No α/β data yet
```
**Solution**: 
- Start giving feedback (👍/👎) to build the model
- Run `python backend/trainer.py` to batch-update models
- Check database has entries in `interactions` table

**5. Module Import Errors**
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution**: 
- Install dependencies: `cd backend && pip install -r requirements.txt`
- For frontend: `pip install streamlit plotly pandas psycopg2-binary`

**6. .env File Not Found**
```
Error: DATABASE_URL or YOUTUBE_API_KEY not set
```
**Solution**: 
- Create `.env` file in root directory
- Add required environment variables (see Installation Step 3)

---

## 🧪 Testing

### Test Database Connection
```bash
cd backend
python test_db.py
```

### Test API Endpoints
Visit `http://127.0.0.1:8000/docs` after starting backend to test endpoints interactively.

### Manual Testing
```bash
python test.py
```

---

## 📚 References

1. Sutton, R.S. & Barto, A.G. (2018). *Reinforcement Learning: An Introduction*. MIT Press.
2. Russo, D., Van Roy, B., Osband, I. (2018). *A Tutorial on Thompson Sampling and Bandit Algorithms*.
3. [Streamlit Documentation](https://docs.streamlit.io/)
4. [FastAPI Documentation](https://fastapi.tiangolo.com/)
5. [NeonDB Documentation](https://neon.tech/docs)
6. [YouTube Data API v3](https://developers.google.com/youtube/v3)

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚠️ Important Notes

- **Do not commit `.env` file** - It contains sensitive API keys and database credentials
- Add `.env` to `.gitignore` before committing
- Use environment variables for all sensitive configuration
- Backend must be running before starting frontend


<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ using FastAPI, Streamlit, and Reinforcement Learning

</div>
