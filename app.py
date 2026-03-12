from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import json
import csv
import os
import re
from datetime import datetime
from textblob import TextBlob
import io

app = Flask(__name__)

# ─── Sample tweet datasets per topic ────────────────────────────────────────
SAMPLE_TWEETS = {
    "python": [
        "Python is absolutely amazing for data science projects!",
        "I hate Python's indentation rules, so frustrating",
        "Just finished my Python course, feeling great!",
        "Python 3.12 has some interesting new features",
        "Why is Python so slow compared to C++?",
        "Python makes machine learning so accessible to everyone",
        "Debugging Python code is a nightmare sometimes",
        "Love the Python community, always so helpful",
        "Python libraries like pandas are incredibly powerful",
        "Python syntax is clean and readable, love it",
        "Python for web development with Flask is decent",
        "Honestly Python is overrated, change my mind",
        "My first Python project just went live, so excited!",
        "Python packaging is a total mess with pip issues",
        "Python is the best language for beginners, hands down",
    ],
    "ai": [
        "Artificial Intelligence is revolutionizing every industry!",
        "AI is going to take all our jobs, very concerning",
        "The progress in AI research this year is mind-blowing",
        "AI chatbots are still too unreliable for serious work",
        "I love how AI can now generate realistic images",
        "AI ethics is something we seriously need to address",
        "AI tools have made me 10x more productive at work",
        "The hype around AI is completely overblown right now",
        "AI in healthcare is genuinely saving lives every day",
        "Scared about the future with AI advancing so fast",
        "AI coding assistants are genuinely helpful for developers",
        "AI generated art feels soulless and uninspired to me",
        "Excited to see where AI takes us in the next decade",
        "AI bias is a real and dangerous problem we must fix",
        "AI is the most transformative technology of our generation",
    ],
    "climate": [
        "Climate change is the biggest threat facing humanity today",
        "Climate activists are just overreacting to normal weather cycles",
        "Renewable energy adoption is growing faster than expected!",
        "Climate policies are destroying jobs and hurting families",
        "The coral reef recovery news gives me so much hope",
        "Climate scientists are heroes for warning us about this",
        "Electric vehicles are finally becoming affordable for everyone",
        "Climate doom and gloom reporting is getting exhausting",
        "Young people fighting for climate justice are so inspiring",
        "Climate change is real and we need urgent action now",
        "Solar panel prices dropping is genuinely great news",
        "Climate misinformation spreads faster than actual facts online",
        "Carbon capture technology could be a real game changer",
        "Climate change affects the poorest communities the most, tragic",
        "We can solve climate change with innovation and cooperation",
    ],
    "twitter": [
        "Twitter has changed so much since the ownership change",
        "Really miss the old Twitter, it was better before",
        "Twitter is still the best place for real-time news",
        "Twitter's algorithm is completely broken and unfair now",
        "Found so many amazing people to follow on Twitter",
        "Twitter bots are completely ruining the platform experience",
        "Twitter spaces are actually really useful for discussions",
        "Getting shadowbanned on Twitter for no reason is awful",
        "Twitter drama is entertaining but exhausting to follow",
        "Twitter still has the best tech community anywhere online",
        "My tweets never get any engagement, so discouraging",
        "Twitter is irreplaceable for following breaking news live",
        "The verification chaos on Twitter is really confusing now",
        "Twitter helped me land my dream job through networking",
        "Twitter feels more toxic than ever these days, sadly",
    ],
    "football": [
        "That match last night was absolutely incredible to watch!",
        "My team lost again, this season is so disappointing",
        "The new signing looks like a brilliant player for us",
        "Football is getting too commercial and losing its soul",
        "VAR decisions are ruining the natural flow of the game",
        "Nothing beats watching live football with passionate fans",
        "The young players coming through this year are so talented",
        "Ticket prices are making football unaffordable for normal fans",
        "What an incredible goal, best of the season without doubt",
        "Football managers deserve more respect for their hard work",
        "Penalty shootouts give me heart attacks every single time",
        "Football brings people together like nothing else can",
        "The referee was absolutely terrible in that game today",
        "Watching my son play football fills me with so much pride",
        "Modern football tactics are fascinating to analyze and study",
    ],
}


def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.1:
        label = "Positive"
        emoji = "😊"
        color = "#00d4aa"
    elif polarity < -0.1:
        label = "Negative"
        emoji = "😞"
        color = "#ff4d6d"
    else:
        label = "Neutral"
        emoji = "😐"
        color = "#ffd166"

    return {
        "text": text,
        "polarity": round(polarity, 3),
        "subjectivity": round(subjectivity, 3),
        "label": label,
        "emoji": emoji,
        "color": color,
    }


def get_summary(results):
    positive = sum(1 for r in results if r["label"] == "Positive")
    negative = sum(1 for r in results if r["label"] == "Negative")
    neutral = sum(1 for r in results if r["label"] == "Neutral")
    total = len(results)

    avg_polarity = round(sum(r["polarity"] for r in results) / total, 3) if total else 0
    avg_subjectivity = round(sum(r["subjectivity"] for r in results) / total, 3) if total else 0

    if avg_polarity > 0.1:
        overall = "Mostly Positive 😊"
    elif avg_polarity < -0.1:
        overall = "Mostly Negative 😞"
    else:
        overall = "Mostly Neutral 😐"

    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positive_pct": round(positive / total * 100, 1) if total else 0,
        "negative_pct": round(negative / total * 100, 1) if total else 0,
        "neutral_pct": round(neutral / total * 100, 1) if total else 0,
        "avg_polarity": avg_polarity,
        "avg_subjectivity": avg_subjectivity,
        "overall": overall,
    }


@app.route("/")
def index():
    topics = list(SAMPLE_TWEETS.keys())
    return render_template("index.html", topics=topics)


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    topic = data.get("topic", "").lower().strip()
    custom_text = data.get("custom_text", "").strip()

    results = []

    if custom_text:
        # Analyze line by line or as one block
        lines = [l.strip() for l in custom_text.split("\n") if l.strip()]
        if not lines:
            lines = [custom_text]
        for line in lines:
            results.append(analyze_sentiment(line))
    elif topic in SAMPLE_TWEETS:
        for tweet in SAMPLE_TWEETS[topic]:
            results.append(analyze_sentiment(tweet))
    else:
        # Search across all topics or use as custom
        results.append(analyze_sentiment(topic))

    summary = get_summary(results)

    # Store in session file for export
    export_data = {"topic": topic or "custom", "results": results, "summary": summary}
    with open("data/last_analysis.json", "w") as f:
        json.dump(export_data, f)

    return jsonify({"results": results, "summary": summary})


@app.route("/export")
def export_csv():
    try:
        with open("data/last_analysis.json") as f:
            data = json.load(f)
    except:
        return "No analysis data found. Run an analysis first.", 400

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Tweet", "Sentiment", "Polarity", "Subjectivity"])
    for r in data["results"]:
        writer.writerow([r["text"], r["label"], r["polarity"], r["subjectivity"]])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"sentiment_{data['topic']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)