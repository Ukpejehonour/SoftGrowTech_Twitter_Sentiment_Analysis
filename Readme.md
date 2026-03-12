# 🔬 SentimentScope — Twitter Sentiment Analyzer

A real-time sentiment analysis web app built with Python, Flask and NLP.
SoftGrowTech AI Internship — Project 3

## Tech Stack
- Python & Flask
- TextBlob (NLP)
- Pandas
- HTML, CSS, JavaScript

## Features
- Analyze sentiment of tweets (Positive, Negative, Neutral)
- 5 preloaded topic datasets
- Custom text input
- Animated sentiment charts
- Filter by sentiment category
- Export results to CSV

## Setup
pip install flask textblob pandas
python -m textblob.download_corpora
python app.py

Then open: http://localhost:5000

## How It Works
1. Text is fed into TextBlob
2. Polarity score calculated (-1.0 to +1.0)
3. Classified as Positive, Negative or Neutral
4. Results displayed on dashboard

## Author
Ukpeje Honour — SoftGrowTech AI Internship