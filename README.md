# DailyAndacht

A website for daily Christian devotionals ("Andachten"). Sermons are stored as static JSON files plus a small SQLite index, and are meant to be read directly in the browser with no backend required. A local Flask tool is used only for *authoring* new sermons, not for serving the site.

## Project structure

```
andachten/
  overview.sqlite     # index of all sermons (date, title, read time, author, id)
  files/               # one {uuid}.json file per sermon
src/
  creator/
    create_sermon.py   # authoring tool (Flask app + CLI)
    templates/
      manual.html       # manual authoring form
      assisted.html      # AI-assisted authoring form (via local Ollama)
  css/main.css          # shared site styles
  logos/                # logo assets
index.html               # public reader page (not yet implemented — see below)
requirements.txt
```

## Data format

Each sermon is a JSON file at `andachten/files/{uuid}.json`:

```json
{
  "id": "uuid",
  "title": "...",
  "bible_verse": "...",
  "body": "...",
  "prayer": "...",
  "activity": "...",
  "author": "...",
  "date": "YYYY-MM-DD",
  "read_time_minutes": 5,
  "word_count": 812,
  "created_at": "2026-07-19T14:32:10+00:00"
}
```

`andachten/overview.sqlite` has a single `sermons` table (`id`, `date`, `title`, `author`, `read_time_minutes`, `created_at`) that indexes those files, so a reader can list/sort sermons without opening every JSON file individually. Sermons are identified by UUID rather than by date, so multiple drafts can exist and dates can be reassigned freely.

## Creating a new sermon

The authoring tool runs locally and opens a small web form in your browser. It's not part of the public site.

1. Install dependencies once (uses the project's `.venv`):
   ```
   ./.venv/bin/pip install -r requirements.txt
   ```
2. Start the tool in whichever mode you want:
   ```
   ./.venv/bin/python src/creator/create_sermon.py -manual
   ./.venv/bin/python src/creator/create_sermon.py -assisted
   ```
   This starts a local Flask server (default port `5050`, override with `--port`) and opens the corresponding page in your browser. Both `/manual` and `/assisted` are always reachable, regardless of which flag started the server.

### Manual mode

Fill in Date, Title, Author, Bible verse, Body, Prayer, and a short suggested activity, then save. Word count and estimated read time are computed automatically.

### Assisted mode

Describe a topic and any notes/quotes/points to include, pick an installed Ollama model (auto-detected from your local Ollama instance at `http://localhost:11434`), and generate a draft. The draft appears in an editable preview where you can:
- edit any field by hand, or
- type feedback and click "regenerate" to have the model revise the draft — repeatable as many times as needed.

Once you're happy with it, save it the same way as the manual flow.

Requires [Ollama](https://ollama.com) running locally with at least one model pulled (e.g. `ollama pull llama3`).

## Public reader site

`index.html` is currently a placeholder — the front-end that reads `overview.sqlite` and `andachten/files/*.json` to display sermons in the browser has not been built yet. This is planned future work; the authoring tool above only produces the data for it.
