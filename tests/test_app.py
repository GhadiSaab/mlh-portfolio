import unittest
import os

# Must be set before importing app, which picks its database at import time.
os.environ['TESTING'] = 'true'

from app import app, mydb, TimelinePost


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        # Start each test from an empty table.
        mydb.connect(reuse_if_open=True)
        mydb.drop_tables([TimelinePost])
        mydb.create_tables([TimelinePost])
        mydb.close()

    def tearDown(self):
        mydb.connect(reuse_if_open=True)
        mydb.drop_tables([TimelinePost])
        mydb.close()

    def post_json(self, name, email, content):
        return self.client.post(
            "/api/timeline_post",
            json={"name": name, "email": email, "content": content},
        )

    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>MLH Fellows</title>" in html

        # Every person in the about section is rendered.
        assert "Andrei" in html
        assert "Ghadi" in html
        assert "Computer Science student at University College Cork" in html

        # Work experience and education entries reach the page.
        assert "Claude Soc&#39;s Tutor" in html
        assert "Genvia" in html
        assert "BSc Computer Science" in html
        assert "M.Eng Devops Engineering" in html

        # Nav bar links to every page.
        assert 'href="/hobbies"' in html
        assert 'href="/timeline"' in html

    def test_timeline_page(self):
        response = self.client.get("/timeline")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>Timeline</title>" in html
        # The page ships the form and the container the posts render into.
        assert 'id="timeline-form"' in html
        assert 'id="timeline-posts"' in html

    def test_timeline(self):
        # Empty to start. The API returns a bare JSON array, which is what
        # timeline.html iterates.
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        assert response.get_json() == []

        # POST returns the created post
        created = self.post_json("John Doe", "john@example.com", "Hello world!")
        assert created.status_code == 201
        post_id = created.get_json()["id"]

        # POSTed posts come back out of GET
        self.post_json("Jane Doe", "jane@example.com", "Hi from Jane!")
        posts = self.client.get("/api/timeline_post").get_json()
        assert len(posts) == 2
        posts_by_name = {post["name"]: post for post in posts}
        assert posts_by_name["John Doe"]["email"] == "john@example.com"
        assert posts_by_name["John Doe"]["content"] == "Hello world!"
        assert posts_by_name["Jane Doe"]["content"] == "Hi from Jane!"

        # DELETE removes only the post asked for.
        assert self.client.delete(f"/api/timeline_post/{post_id}").status_code == 204
        posts = self.client.get("/api/timeline_post").get_json()
        assert len(posts) == 1
        assert posts[0]["name"] == "Jane Doe"

    def test_malformed_timeline_post(self):
        # POST request missing name
        response = self.client.post("/api/timeline_post", data=
{"email": "john@example.com", "content": "Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html

        # POST request with empty content
        response = self.client.post("/api/timeline_post", data=
{"name": "John Doe", "email": "john@example.com", "content": ""})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html

        # POST request with malformed email
        response = self.client.post("/api/timeline_post", data=
{"name": "John Doe", "email": "not-an-email", "content": "Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html


if __name__ == "__main__":
    unittest.main()
