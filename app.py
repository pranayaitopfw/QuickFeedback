
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("feedback.db")

PHRASES = [
    "Good service",
    "Delicious food",
    "Friendly staff",
    "Comfortable ambience",
    "Quick service",
    "Good value for money",
]


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant TEXT NOT NULL,
                phrases TEXT NOT NULL,
                suggestion TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/")
def home():
    restaurant = request.args.get("restaurant", "shop name")
    google_review_url = request.args.get("google_review_url", "")

    return render_template(
        "index.html",
        restaurant=restaurant,
        phrases=PHRASES,
        google_review_url=google_review_url,
    )


@app.route("/submit", methods=["POST"])
def submit():
    restaurant = request.form.get("restaurant", "shop name").strip()
    selected_phrases = request.form.getlist("phrases")
    suggestion = request.form.get("suggestion", "").strip()

    # Accept only phrases defined by the application.
    selected_phrases = [
        phrase for phrase in selected_phrases if phrase in PHRASES
    ]

    if not selected_phrases:
        return "Please select at least one experience phrase.", 400

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """INSERT INTO feedback (restaurant, phrases, suggestion)
               VALUES (?, ?, ?)""",
            (restaurant, " | ".join(selected_phrases), suggestion),
        )

    google_review_url = request.form.get("google_review_url", "").strip()

    return render_template(
        "thank_you.html",
        restaurant=restaurant,
        google_review_url=google_review_url,
    )


@app.route("/health")
def health():
    return {"status": "ok", "app": "QuickFeedback"}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
