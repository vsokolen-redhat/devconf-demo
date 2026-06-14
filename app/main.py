"""DevConf.CZ 2026 Schedule API — Flask app for the conference demo."""

import os
import requests
from flask import Flask, jsonify

app = Flask(__name__)

PRETALX_BASE = "https://pretalx.devconf.info/api/events/devconf-cz-2026"


def pretalx_get(endpoint, params=None):
    """Fetch all pages from a Pretalx API endpoint."""
    url = f"{PRETALX_BASE}/{endpoint}/"
    items = []
    while url:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items.extend(data.get("results", []))
        url = data.get("next")
        params = None
    return items


@app.route("/")
def index():
    return jsonify({
        "app": "DevConf.CZ 2026 Schedule API",
        "version": "1.0.0",
        "source": "pretalx.devconf.info",
        "endpoints": [
            "/api/event",
            "/api/stats",
            "/api/rooms",
            "/api/types",
            "/api/self",
        ],
    })


@app.route("/api/event")
def event_info():
    resp = requests.get(f"{PRETALX_BASE}/", timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return jsonify({
        "name": data["name"]["en"],
        "slug": data["slug"],
        "date_from": data["date_from"],
        "date_to": data["date_to"],
        "timezone": data["timezone"],
    })


@app.route("/api/stats")
def stats():
    submissions = pretalx_get("submissions")
    types = pretalx_get("submission-types")
    rooms = pretalx_get("rooms")

    type_map = {t["id"]: t["name"]["en"] for t in types}
    breakdown = {}
    for s in submissions:
        type_name = type_map.get(s["submission_type"], "Unknown")
        breakdown[type_name] = breakdown.get(type_name, 0) + 1

    unique_speakers = set()
    for s in submissions:
        for sp in s.get("speakers", []):
            unique_speakers.add(sp)

    return jsonify({
        "total_sessions": len(submissions),
        "unique_speakers": len(unique_speakers),
        "rooms": len(rooms),
        "breakdown_by_type": breakdown,
    })


@app.route("/api/rooms")
def rooms():
    room_list = pretalx_get("rooms")
    return jsonify({
        "count": len(room_list),
        "rooms": [r["name"]["en"] for r in room_list],
    })


@app.route("/api/types")
def session_types():
    types = pretalx_get("submission-types")
    return jsonify({
        "count": len(types),
        "types": [
            {"name": t["name"]["en"], "default_duration": t["default_duration"]}
            for t in types
        ],
    })


@app.route("/api/self")
def self_talk():
    """Find this talk's own entry — the app presenting itself."""
    submissions = pretalx_get("submissions")
    for s in submissions:
        if "Podman" in s.get("title", "") and "Konflux" in s.get("title", ""):
            return jsonify({
                "meta": "This app found its own talk in the DevConf schedule!",
                "code": s["code"],
                "title": s["title"],
                "duration": s["duration"],
                "state": s["state"],
                "type_id": s["submission_type"],
            })
    return jsonify({"meta": "Talk not found in schedule yet"}), 404


@app.route("/healthz")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
