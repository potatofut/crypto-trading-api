# Algoritmic Trading API

This project is an algorithmic trading system with a Python backend API using Flask, collecting sentiment data from Twitter and RSS feeds, and providing price data from BitMEX. Data is stored in MongoDB.

**GitHub Repository**: [https://github.com/potatofut/crypto-trading-api](https://github.com/potatofut/crypto-trading-api)

## Setup Instructions

1. **Git and GitHub:**
   - The repository is already initialized locally.
   - To connect to GitHub:
     - Create a new repository on GitHub (e.g., `crypto-trading-api`).
     - Copy the repository URL.
     - Run: `git remote add origin <your-repo-url>`
     - Run: `git push -u origin master`

2. **Virtual Environment:**
   - Already created as `venv`.
   - To activate: `.\venv\Scripts\activate` (on Windows)

3. **Dependencies:**
   - Already installed and listed in `requirements.txt`.
   - To reinstall: `pip install -r requirements.txt`

4. **Environment Variables:**
   - Credentials are set in `.env` (ensure it's not committed).
   - For Twitter API v2, add your Bearer Token to `TWITTER_BEARER_TOKEN` in `.env`.

## Running the Program

Activate the virtual environment and run:
```
python main.py
```

The API will start on `http://localhost:5000`

Endpoints:
- `/api/sentimiento`: Get sentiment summary
- `/api/precios?symbol=<SYMBOL>`: Get historical prices for a symbol

## Project Structure

- `main.py`: Main application file
- `.env`: Environment variables (not committed)
- `requirements.txt`: Python dependencies
- `.gitignore`: Git ignore file
- `venv/`: Virtual environment

## Issues and Fixes

- **Twitter API**: ✅ Working! Bearer Token is valid and API is accessible.
  - Currently disabled to avoid rate limits (Free plan: 300 requests/month)
  - To enable: Uncomment `get_twitter_data()` in main.py
  - Rate limit optimizations applied (2 symbols, 5 tweets each, 2s delay)
- **RSS Feeds**: Working correctly.
- **MongoDB**: Ensure the connection string is valid.

## Next Steps

- For the frontend, a Next.js project has been created in `c:\Proyectos\Web\crypto-frontend`. Open this folder in VS Code to work on it.
- Connect the frontend to the API endpoints.
