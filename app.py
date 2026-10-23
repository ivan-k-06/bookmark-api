import os
import sqlite3
from contextlib import closing
from urllib.parse import urlsplit
from flask import Flask, g, jsonify, render_template, request


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(g.database_path)
        g.db.row_factory = sqlite3.Row
    return g.db


def create_app(database_path=None):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
    app.config["DATABASE"] = database_path or os.getenv("DATABASE_PATH", "bookmarks.sqlite3")

    @app.before_request
    def set_database():
        g.database_path = app.config["DATABASE"]

    @app.teardown_appcontext
    def close_database(error=None):
        database = g.pop("db", None)
        if database is not None:
            database.close()

    with closing(sqlite3.connect(app.config["DATABASE"])) as database:
        database.execute("CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL UNIQUE, tag TEXT NOT NULL)")

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/bookmarks")
    def list_bookmarks():
        tag = request.args.get("tag", "").strip()
        if tag:
            rows = get_db().execute("SELECT * FROM bookmarks WHERE tag = ? ORDER BY id DESC", (tag,))
        else:
            rows = get_db().execute("SELECT * FROM bookmarks ORDER BY id DESC")
        return jsonify([dict(row) for row in rows])

    @app.post("/api/bookmarks")
    def add_bookmark():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return {"error": "Нужен JSON-объект"}, 400
        title, url, tag = (data.get(key, "") for key in ("title", "url", "tag"))
        if not all(isinstance(value, str) for value in (title, url, tag)):
            return {"error": "Поля должны быть строками"}, 400
        title, url, tag = title.strip(), url.strip(), tag.strip().lower()
        try:
            parsed = urlsplit(url)
            valid_url = parsed.scheme in ("http", "https") and bool(parsed.hostname)
        except ValueError:
            valid_url = False
        if not title or len(title) > 150 or len(url) > 2000 or len(tag) > 40 or not valid_url:
            return {"error": "Укажи заголовок до 150 символов, HTTP(S) URL до 2000 и тег до 40"}, 400
        database = get_db()
        try:
            cursor = database.execute("INSERT INTO bookmarks(title, url, tag) VALUES (?, ?, ?)", (title, url, tag))
            database.commit()
        except sqlite3.IntegrityError:
            return {"error": "Такая ссылка уже есть"}, 409
        return {"id": cursor.lastrowid, "title": title, "url": url, "tag": tag}, 201

    @app.delete("/api/bookmarks/<int:bookmark_id>")
    def delete_bookmark(bookmark_id):
        database = get_db()
        cursor = database.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
        database.commit()
        if cursor.rowcount == 0:
            return {"error": "Закладка не найдена"}, 404
        return "", 204

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000)
