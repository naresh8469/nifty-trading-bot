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
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
scheduler.add_job(bot_engine.run_all_symbols, "interval", minutes=5, id="trading_job")
scheduler.start()
atexit.register(lambda: scheduler.shutdown())


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
