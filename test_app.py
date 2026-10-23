import tempfile
import unittest
from pathlib import Path
from app import create_app

class BookmarkTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path = str(Path(self.directory.name) / "test.sqlite3")
        self.client = create_app(self.path).test_client()
        self.bookmark = {"title": "Python docs", "url": "https://docs.python.org/3/", "tag": "Python"}

    def tearDown(self):
        self.directory.cleanup()

    def test_create_filter_delete_and_persistence(self):
        response = self.client.post("/api/bookmarks", json=self.bookmark)
        self.assertEqual(response.status_code, 201)
        item_id = response.json["id"]
        new_client = create_app(self.path).test_client()
        self.assertEqual(len(new_client.get("/api/bookmarks?tag=python").json), 1)
        self.assertEqual(new_client.get("/api/bookmarks?tag=java").json, [])
        self.assertEqual(new_client.delete(f"/api/bookmarks/{item_id}").status_code, 204)
        self.assertEqual(new_client.delete(f"/api/bookmarks/{item_id}").status_code, 404)

    def test_duplicate(self):
        self.client.post("/api/bookmarks", json=self.bookmark)
        self.assertEqual(self.client.post("/api/bookmarks", json=self.bookmark).status_code, 409)

    def test_invalid_payloads(self):
        for payload in ([], None, {"title": 12}, {**self.bookmark, "url": "javascript:alert(1)"}, {**self.bookmark, "title": " "}):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/api/bookmarks", json=payload).status_code, 400)

    def test_sql_values_are_not_executable(self):
        self.client.post("/api/bookmarks", json={**self.bookmark, "tag": "'; drop table bookmarks;--"})
        self.assertEqual(len(self.client.get("/api/bookmarks").json), 1)
