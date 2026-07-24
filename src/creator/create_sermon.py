import argparse
import json
import math
import re
import shutil
import sqlite3
import subprocess
import tempfile
import threading
import uuid
import webbrowser
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from flask import Flask, Response, abort, jsonify, redirect, render_template, request, send_file

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ANDACHTEN_DIR = BASE_DIR / "andachten"
FILES_DIR = ANDACHTEN_DIR / "files"
DB_PATH = ANDACHTEN_DIR / "overview.sqlite"
LOGO_PATH = BASE_DIR / "src" / "logos" / "light.jpeg"

OLLAMA_HOST = "http://localhost:11434"
DEFAULT_AUTHOR = "DailyAndacht Team"
WORDS_PER_MINUTE = 200

REQUIRED_SERMON_FIELDS = ["title", "bible_verse", "body", "prayer"]
REQUIRED_DRAFT_FIELDS = ["title", "bible_verse", "body", "prayer", "activity"]

# German date labels for the promo card (weekday list is Monday-first to match
# datetime.date.weekday()).
MONTHS_DE = [
    "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]
WEEKDAYS_DE = [
    "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag",
]

# Candidate paths for a headless Chrome/Chromium used to render promo images.
CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "google-chrome",
    "chromium",
    "chromium-browser",
    "chrome",
]

app = Flask(__name__)


def find_chrome():
    for cand in CHROME_CANDIDATES:
        if "/" in cand:
            if Path(cand).is_file():
                return cand
        else:
            found = shutil.which(cand)
            if found:
                return found
    return None


def init_db():
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS sermons (
            id                 TEXT PRIMARY KEY,
            date               TEXT NOT NULL,
            title              TEXT NOT NULL,
            author             TEXT NOT NULL,
            read_time_minutes  INTEGER NOT NULL,
            created_at         TEXT NOT NULL
        )"""
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sermons_date ON sermons (date)")
    conn.commit()
    conn.close()


def compute_read_time(*text_parts):
    text = " ".join(text_parts)
    word_count = len(text.split())
    exact = word_count / WORDS_PER_MINUTE
    read_time = math.floor(exact) if exact % 1 < 0.4 else math.ceil(exact)
    return max(read_time, 1), word_count


def next_available_date() -> str:
    """The day after the latest existing sermon, so new sermons always hang onto
    the end of the run and catch up day-by-day, without filling earlier gaps.
    Falls back to today only when there are no sermons yet."""
    conn = sqlite3.connect(DB_PATH)
    latest = conn.execute("SELECT MAX(date) FROM sermons").fetchone()[0]
    conn.close()
    if not latest:
        return datetime.now().date().isoformat()
    return (date_cls.fromisoformat(latest) + timedelta(days=1)).isoformat()


def date_taken(date: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT 1 FROM sermons WHERE date = ? LIMIT 1", (date,)).fetchone()
    conn.close()
    return row is not None


class DateConflictError(Exception):
    pass


def save_sermon(data: dict) -> dict:
    missing = [f for f in REQUIRED_SERMON_FIELDS if not str(data.get(f, "")).strip()]
    if missing:
        raise ValueError(f"Fehlende Felder: {', '.join(missing)}")

    title = data["title"].strip()
    bible_verse = data["bible_verse"].strip()
    body = data["body"].strip()
    prayer = data["prayer"].strip()
    activity = str(data.get("activity", "")).strip()
    author = str(data.get("author", "")).strip() or DEFAULT_AUTHOR
    date = str(data.get("date", "")).strip()
    if date:
        if date_taken(date):
            raise DateConflictError(f"Für den {date} existiert bereits eine Andacht. Bitte ein anderes Datum wählen.")
    else:
        date = next_available_date()

    read_time, word_count = compute_read_time(title, body, prayer, activity)
    sermon_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    record = {
        "id": sermon_id,
        "title": title,
        "bible_verse": bible_verse,
        "body": body,
        "prayer": prayer,
        "activity": activity,
        "author": author,
        "date": date,
        "read_time_minutes": read_time,
        "word_count": word_count,
        "created_at": created_at,
    }

    file_path = FILES_DIR / f"{sermon_id}.json"
    file_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO sermons (id, date, title, author, read_time_minutes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (sermon_id, date, title, author, read_time, created_at),
    )
    conn.commit()
    conn.close()

    return record


class OllamaError(Exception):
    pass


SYSTEM_PROMPT = """Du bist ein erfahrener christlicher Autor, der kurze, tägliche Andachten (Kurzpredigten) auf Deutsch schreibt. Die Andachten sollen mit den lehren der Kirche der Siebenten Tags adventisten übereinstimmen. Die Siebenten-Tags-Adventisten sind eine protestantisch-christliche Freikirche, die den Samstag (siebten Tag) als biblischen Sabbat und Ruhetag hält, an die baldige sichtbare Wiederkunft Christi glaubt und großen Wert auf einen gesunden Lebensstil (u. a. oft vegetarische Ernährung, Verzicht auf Alkohol/Tabak) legt. Theologisch stehen sie in der Tradition des Sola-scriptura-Prinzips, betonen aber zusätzlich Lehren wie den "Untersuchungsgericht" (investigative judgment) und den Zustand der Toten als "Schlaf" bis zur Auferstehung. Nicht alle Andachten müssen sich diesen Themen widmen, sollten aber nicht mit ihnen wiedersprechen.
Antworte AUSSCHLIESSLICH mit einem JSON-Objekt mit genau diesen Feldern:
{"title": "...", "bible_verse": "...", "body": "...", "prayer": "...", "activity": "..."}
- title: ein prägnanter Titel
- bible_verse: die Bibelstelle als Referenz (z.B. "Psalm 19,1-6")
- body: der Haupttext der Andacht (3 - 8 Absätze (300 - 400 Wörter), warm und persönlich im Ton. Vermeide es die Leser direkt anzusprechen. Vermeide die verwendung von ' - '.)
- prayer: ein kurzes abschließendes Gebet
- activity: 1-2 Sätze mit einer konkreten, umsetzbaren Handlungsempfehlung für den Leser
Gib ausschließlich valides JSON zurück, keinen weiteren Text."""


def build_generation_prompt(topic, notes, bible_verse_hint=""):
    parts = [f"Thema: {topic}" if topic else "Thema: (vom Autor nicht vorgegeben, wähle selbst ein passendes Thema)"]
    if bible_verse_hint:
        parts.append(f"Bibelstelle (vom Autor vorgegeben, bitte genau diese verwenden): {bible_verse_hint}")
    parts.append(f"Anweisungen/Notizen des Autors:\n{notes}" if notes else "Der Autor hat keine weiteren Notizen angegeben.")
    parts.append("Schreibe auf Basis dieser Angaben eine vollständige Andacht im geforderten JSON-Format.")
    return "\n\n".join(parts)


def build_revision_prompt(previous_draft: dict, feedback: str):
    return (
        "Hier ist ein vorheriger Entwurf einer Andacht als JSON:\n"
        f"{json.dumps(previous_draft, ensure_ascii=False)}\n\n"
        f"Der Autor möchte folgende Änderungen:\n{feedback}\n\n"
        "Gib eine überarbeitete Version im selben JSON-Format zurück, "
        "die das Feedback berücksichtigt."
    )


def call_ollama(model: str, user_prompt: str) -> dict:
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "format": "json",
                "stream": False,
            },
            timeout=600,
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise OllamaError(
            "Ollama hat nicht rechtzeitig geantwortet (Timeout). Das Modell wird beim ersten "
            "Aufruf evtl. erst geladen, das kann bei großen Modellen einige Minuten dauern. "
            "Bitte erneut versuchen."
        )
    except requests.exceptions.RequestException as e:
        raise OllamaError(f"Ollama ist nicht erreichbar oder hat einen Fehler geliefert: {e}")

    content = resp.json().get("message", {}).get("content", "")
    try:
        draft = json.loads(content)
    except json.JSONDecodeError:
        raise OllamaError("Das Modell hat kein valides JSON zurückgegeben.")

    missing = [f for f in REQUIRED_DRAFT_FIELDS if not str(draft.get(f, "")).strip()]
    if missing:
        raise OllamaError(f"Antwort unvollständig, es fehlen: {', '.join(missing)}")

    return draft


@app.route("/")
def index():
    return redirect(f"/{app.config['DEFAULT_MODE']}")


@app.route("/manual")
def manual_page():
    return render_template("manual.html", default_author=DEFAULT_AUTHOR)


@app.route("/assisted")
def assisted_page():
    return render_template("assisted.html", default_author=DEFAULT_AUTHOR)


@app.route("/image")
def image_page():
    return render_template("image.html")


@app.route("/assets/logo.jpeg")
def asset_logo():
    return send_file(LOGO_PATH)


@app.route("/api/sermons")
def api_sermons():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, date, title, author, read_time_minutes FROM sermons "
        "ORDER BY date DESC, created_at DESC"
    ).fetchall()
    conn.close()
    sermons = [
        {"id": r[0], "date": r[1], "title": r[2], "author": r[3], "read_time_minutes": r[4]}
        for r in rows
    ]
    return jsonify({"ok": True, "sermons": sermons})


def load_sermon_file(sermon_id):
    """Return a sermon's JSON dict, or None if the id is unknown / unsafe."""
    file_path = (FILES_DIR / f"{sermon_id}.json").resolve()
    # Guard against path traversal: the resolved file must live inside FILES_DIR.
    if FILES_DIR.resolve() not in file_path.parents or not file_path.is_file():
        return None
    return json.loads(file_path.read_text(encoding="utf-8"))


@app.route("/api/sermon/<sermon_id>")
def api_sermon(sermon_id):
    sermon = load_sermon_file(sermon_id)
    if sermon is None:
        abort(404)
    return jsonify({"ok": True, "sermon": sermon})


@app.route("/image/card/<sermon_id>")
def image_card(sermon_id):
    """The bare 9:16 promo card (used both for the on-page preview iframe and as
    the target that headless Chrome screenshots)."""
    sermon = load_sermon_file(sermon_id)
    if sermon is None:
        abort(404)

    iso = str(sermon.get("date", ""))
    weekday = date_long = ""
    try:
        y, m, d = (int(x) for x in iso.split("-"))
        dt = date_cls(y, m, d)
        weekday = WEEKDAYS_DE[dt.weekday()]
        date_long = f"{d}. {MONTHS_DE[m - 1]} {y}"
    except (ValueError, IndexError):
        date_long = iso

    paragraphs = [p.strip() for p in re.split(r"\n+", sermon.get("body", "")) if p.strip()]

    return render_template(
        "card.html",
        title=sermon.get("title", ""),
        bible_verse=str(sermon.get("bible_verse", "")).strip(),
        weekday=weekday,
        date_long=date_long,
        read_time=sermon.get("read_time_minutes"),
        paragraphs=paragraphs,
    )


# A 360x640 CSS viewport rendered at 3x device pixels -> a 1080x1920 PNG.
CARD_W, CARD_H, CARD_SCALE = 360, 640, 3


def render_with_playwright(url):
    """Render the card with Playwright's bundled browser engine. Needs no
    system-wide browser install (works on a Safari-only Mac); the user just runs
    `playwright install webkit` once. Returns PNG bytes, or None if Playwright or
    its browsers aren't available."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    try:
        with sync_playwright() as p:
            # Try each installed engine; WebKit is Safari's engine and the
            # smallest download, so it's listed first.
            last_err = None
            for engine_name in ("webkit", "chromium", "firefox"):
                engine = getattr(p, engine_name)
                try:
                    browser = engine.launch()
                except Exception as e:  # engine not installed / failed to launch
                    last_err = e
                    continue
                try:
                    page = browser.new_page(
                        viewport={"width": CARD_W, "height": CARD_H},
                        device_scale_factor=CARD_SCALE,
                    )
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    try:
                        page.evaluate("document.fonts && document.fonts.ready")
                    except Exception:
                        pass
                    page.wait_for_timeout(300)  # let webfonts paint
                    return page.screenshot()
                finally:
                    browser.close()
            if last_err:
                print(f"[image] Playwright hat keine Browser gefunden: {last_err}")
            return None
    except Exception as e:
        print(f"[image] Playwright-Rendern fehlgeschlagen: {e}")
        return None


def render_with_system_chrome(url):
    """Fallback: screenshot with a system Chrome/Chromium/Edge if one exists.
    Returns PNG bytes, or None if no such browser is installed."""
    chrome = find_chrome()
    if not chrome:
        return None
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "promo.png"
        try:
            subprocess.run(
                [
                    chrome,
                    "--headless",
                    "--disable-gpu",
                    "--no-sandbox",
                    "--hide-scrollbars",
                    f"--force-device-scale-factor={CARD_SCALE}",
                    f"--window-size={CARD_W},{CARD_H}",
                    "--virtual-time-budget=8000",  # wait for webfonts + logo
                    f"--screenshot={out}",
                    url,
                ],
                timeout=60,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.SubprocessError, OSError) as e:
            print(f"[image] Chrome-Rendern fehlgeschlagen: {e}")
            return None
        return out.read_bytes() if out.is_file() else None


@app.route("/image/render/<sermon_id>.png")
def image_render(sermon_id):
    """Render the promo card to a 1080x1920 PNG using a real browser engine, so
    the exported image matches the reader's typography exactly (kerning, drop
    cap, fonts). Prefers Playwright's bundled engine (no system browser needed);
    falls back to a system Chrome/Chromium if present."""
    if load_sermon_file(sermon_id) is None:
        abort(404)

    port = app.config.get("PORT", 5050)
    url = f"http://127.0.0.1:{port}/image/card/{sermon_id}"

    data = render_with_playwright(url) or render_with_system_chrome(url)
    if data is None:
        return jsonify({
            "ok": False,
            "error": (
                "Kein Renderer verfügbar. Einmalig einrichten mit: "
                "pip install playwright && playwright install webkit"
            ),
        }), 500

    return Response(
        data,
        mimetype="image/png",
        headers={"Content-Disposition": f'inline; filename="dailyandacht-{sermon_id}.png"'},
    )


@app.route("/manual/save", methods=["POST"])
def manual_save():
    try:
        record = save_sermon(request.get_json(force=True))
        return jsonify({"ok": True, "sermon": record})
    except DateConflictError as e:
        return jsonify({"ok": False, "error": str(e), "error_type": "date_conflict"}), 409
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/assisted/save", methods=["POST"])
def assisted_save():
    try:
        record = save_sermon(request.get_json(force=True))
        return jsonify({"ok": True, "sermon": record})
    except DateConflictError as e:
        return jsonify({"ok": False, "error": str(e), "error_type": "date_conflict"}), 409
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400


@app.route("/api/upcoming-dates")
def upcoming_dates():
    try:
        days = int(request.args.get("days", 7))
    except ValueError:
        days = 7
    days = max(1, min(days, 60))

    start = datetime.now().date()
    end = start + timedelta(days=days)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT date, title FROM sermons WHERE date >= ? AND date < ?",
        (start.isoformat(), end.isoformat()),
    ).fetchall()
    conn.close()
    titles_by_date = dict(rows)

    result = []
    for i in range(days):
        d = (start + timedelta(days=i)).isoformat()
        result.append({"date": d, "title": titles_by_date.get(d)})
    return jsonify({"ok": True, "days": result})


@app.route("/api/ollama/models")
def ollama_models():
    try:
        resp = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m["name"] for m in resp.json().get("models", [])]
        return jsonify({"ok": True, "models": models})
    except requests.exceptions.RequestException:
        return jsonify(
            {"ok": False, "error": f"Ollama ist nicht erreichbar unter {OLLAMA_HOST}. Läuft Ollama?"}
        ), 503


@app.route("/assisted/generate", methods=["POST"])
def assisted_generate():
    payload = request.get_json(force=True)
    model = payload.get("model")
    if not model:
        return jsonify({"ok": False, "error": "Kein Modell ausgewählt."}), 400

    date = str(payload.get("date", "")).strip()
    if date and date_taken(date):
        return jsonify({
            "ok": False,
            "error": f"Für den {date} existiert bereits eine Andacht. Bitte ein anderes Datum wählen.",
            "error_type": "date_conflict",
        }), 409

    if payload.get("previous_draft") and payload.get("feedback"):
        prompt = build_revision_prompt(payload["previous_draft"], payload["feedback"])
    else:
        prompt = build_generation_prompt(
            payload.get("topic", ""), payload.get("notes", ""), payload.get("bible_verse", "")
        )

    try:
        draft = call_ollama(model, prompt)
        return jsonify({"ok": True, "draft": draft})
    except OllamaError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


def main():
    parser = argparse.ArgumentParser(description="DailyAndacht sermon creator")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("-manual", action="store_true")
    mode_group.add_argument("-assisted", action="store_true")
    parser.add_argument("--port", type=int, default=5050)
    args = parser.parse_args()

    app.config["DEFAULT_MODE"] = "manual" if args.manual else "assisted"
    app.config["PORT"] = args.port
    url = f"http://127.0.0.1:{args.port}/"

    print(f"Starting DailyAndacht creator at {url}")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    # threaded=True so /image/render can call back into this server (headless
    # Chrome fetching /image/card) without deadlocking the single worker.
    app.run(port=args.port, debug=False, threaded=True)


init_db()

if __name__ == "__main__":
    main()
