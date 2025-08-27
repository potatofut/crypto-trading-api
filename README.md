# Algoritmic Trading API

This project is an algorithmic trading system with a Python backend API using Flask, collecting sentiment data from Twitter and RSS feeds, and providing price data from BitMEX. Data is stored in MongoDB.

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

## Next Steps

- For the frontend, create a Next.js project in a separate directory.
- Connect the frontend to the API endpoints.
