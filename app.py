"""
app.py
Flask web server that:
1. Serves a mobile-friendly dashboard (open at your Render URL from your phone)
2. Runs the paper trading bot automatically every 5 minutes during market
   hours using a background scheduler (APScheduler)

This is the file Render will run when the bot is deployed.
"""

from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

import bot_engine

app = Flask(__name__)

bot_engine.init_db()


@app.route("/")
def dashboard():
    data = bot_engine.get_dashboard_data()
    return render_template("index.html", data=data)


@app.route("/api/data")
def api_data():
    """Used by the dashboard page to auto-refresh without a full reload."""
    return jsonify(bot_engine.get_dashboard_data())


# ---------------- Background scheduler ----------------
print("Starting background scheduler...", flush=True)
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
# run_date=now-ish via next_run_time so the first check happens immediately
# on startup instead of waiting 5 minutes â€” makes it easy to confirm the
# scheduler is actually alive.
from datetime import datetime
import pytz
scheduler.add_job(
    bot_engine.run_all_symbols,
    "interval",
    minutes=5,
    id="trading_job",
    next_run_time=datetime.now(pytz.timezone("Asia/Kolkata")),
)
scheduler.start()
print("Scheduler started.", flush=True)
atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
