import os
import json
from flask import Flask, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import tweepy
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['crypto_trading']

# Collections
activos = db['activos']
tweets_sentimiento = db['tweets_sentimiento']
noticias_sentimiento = db['noticias_sentimiento']
sentimiento_resumen = db['sentimiento_resumen']
usuarios = db['usuarios']
fuentes_de_noticias = db['fuentes_de_noticias']

# Initialize fuentes_de_noticias if empty
if fuentes_de_noticias.count_documents({}) == 0:
    fuentes = [
        {"url": 'https://www.coindesk.com/arc/outboundfeeds/rss/', "nombre": "CoinDesk"},
        {"url": 'https://cointelegraph.com/rss', "nombre": "CoinTelegraph"},
        {"url": 'https://api.theblockcrypto.com/rss', "nombre": "The Block"},
        {"url": 'https://decrypt.co/feed', "nombre": "Decrypt"},
        {"url": 'https://dailyhodl.com/feed/', "nombre": "Daily Hodl"},
        {"url": 'https://www.binance.com/en/rss', "nombre": "Binance"},
        {"url": 'https://www.financemagnates.com/tag/cryptocurrencies/feed/', "nombre": "Finance Magnates"}
    ]
    fuentes_de_noticias.insert_many(fuentes)

# Function to initialize activos from BitMEX
def initialize_activos():
    if activos.count_documents({}) == 0:
        url = "https://www.bitmex.com/api/v1/instrument?count=50"
        response = requests.get(url)
        if response.status_code == 200:
            instruments = response.json()
            for inst in instruments:
                if inst.get('state') == 'Open':
                    activos.insert_one({
                        'symbol': inst['symbol'],
                        'rootSymbol': inst.get('rootSymbol'),
                        'state': inst['state']
                    })

# Function to collect Twitter data
def get_twitter_data():
    client = tweepy.Client(
        consumer_key=os.getenv('TWITTER_API_KEY'),
        consumer_secret=os.getenv('TWITTER_API_SECRET'),
        access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    )
    analyzer = SentimentIntensityAnalyzer()
    assets = list(activos.find({}, {'symbol': 1}))
    symbols = [a['symbol'] for a in assets if a['symbol'].endswith('USDT') or a['symbol'].endswith('USD')]  # Filter to stable pairs or USD
    tweets_data = []
    for symbol in symbols[:5]:  # Limit to 5 symbols to avoid rate limits
        query = f"{symbol} crypto"
        try:
            tweets = client.search_recent_tweets(query=query, max_results=20, tweet_fields=['created_at', 'text'])
            if tweets.data:
                for tweet in tweets.data:
                    score = analyzer.polarity_scores(tweet.text)['compound']
                    tweet_doc = {
                        'symbol': symbol,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'sentiment_score': score
                    }
                    tweets_data.append(tweet_doc)
                    tweets_sentimiento.insert_one(tweet_doc)
        except Exception as e:
            print(f"Error fetching tweets for {symbol}: {e}")
    return tweets_data

# Function to collect RSS news data
def get_rss_data():
    fuentes = list(fuentes_de_noticias.find())
    analyzer = SentimentIntensityAnalyzer()
    news_data = []
    for fuente in fuentes:
        try:
            feed = feedparser.parse(fuente['url'])
            for entry in feed.entries[:10]:  # Limit to 10 entries per feed
                text = entry.title + ' ' + (entry.description if 'description' in entry else '')
                score = analyzer.polarity_scores(text)['compound']
                news_doc = {
                    'fuente': fuente['nombre'],
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published if 'published' in entry else str(datetime.now()),
                    'sentiment_score': score
                }
                news_data.append(news_doc)
                noticias_sentimiento.insert_one(news_doc)
        except Exception as e:
            print(f"Error fetching RSS from {fuente['nombre']}: {e}")
    return news_data

# Function to calculate sentiment summary
def calculate_sentiment_summary():
    # Aggregate average sentiment by symbol from tweets
    pipeline = [
        {"$group": {"_id": "$symbol", "avg_sentiment": {"$avg": "$sentiment_score"}}}
    ]
    summary_tweets = list(tweets_sentimiento.aggregate(pipeline))
    for s in summary_tweets:
        sentimiento_resumen.insert_one({
            'type': 'tweets',
            'symbol': s['_id'],
            'avg_sentiment': s['avg_sentiment'],
            'timestamp': datetime.now()
        })
    # Aggregate average sentiment by fuente from news
    pipeline_news = [
        {"$group": {"_id": "$fuente", "avg_sentiment": {"$avg": "$sentiment_score"}}}
    ]
    summary_news = list(noticias_sentimiento.aggregate(pipeline_news))
    for s in summary_news:
        sentimiento_resumen.insert_one({
            'type': 'news',
            'fuente': s['_id'],
            'avg_sentiment': s['avg_sentiment'],
            'timestamp': datetime.now()
        })

# Function to get historical prices from BitMEX
def get_prices(symbol):
    url = f"https://www.bitmex.com/api/v1/trade?symbol={symbol}&count=100&reverse=true"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except Exception as e:
        print(f"Error fetching prices for {symbol}: {e}")
        return []

# Flask app
app = Flask(__name__)

@app.route('/api/sentimiento')
def get_sentimiento():
    summary = list(sentimiento_resumen.find().sort('timestamp', -1).limit(20))
    return jsonify(summary)

@app.route('/api/precios')
def get_precios():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    prices = get_prices(symbol)
    return jsonify(prices)

if __name__ == '__main__':
    initialize_activos()
    get_twitter_data()
    get_rss_data()
    calculate_sentiment_summary()
    app.run(debug=True)
