import os
import unittest

# Must be set before importing app, which picks its database at import time.
os.environ['TESTING'] = 'true'

from peewee import *

from app import TimelinePost

MODELS = [TimelinePost]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')

class TestTimelinePost(unittest.TestCase):
    def setUp(self):
        # Bind model classes to test db. Since we have a complete list of
        # all models, we do not need to recursively bind dependencies.
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)

        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        # Not strictly necessary since SQLite in-memory databases only live
        # for the duration of the connection, and in the next step we close
        # the connection...but a good practice all the same.
        test_db.drop_tables(MODELS)

        # Close connection to db.
        test_db.close()

    def test_timeline_post(self):
        # Create 2 timeline posts.
        first_post = TimelinePost.create(name='John Doe',
    email='john@example.com', content='Hello world, I\'m John!')
        assert first_post.id == 1
        second_post = TimelinePost.create(name='Jane Doe',
    email='jane@example.com', content='Hello world, I\'m Jane!')
        assert second_post.id == 2
        # Get timeline posts, newest first, the same way the API does.
        timeline_posts = list(
            TimelinePost.select().order_by(TimelinePost.created_at.desc())
        )
        assert len(timeline_posts) == 2

        posts_by_id = {post.id: post for post in timeline_posts}
        assert posts_by_id[1].name == 'John Doe'
        assert posts_by_id[1].email == 'john@example.com'
        assert posts_by_id[1].content == 'Hello world, I\'m John!'
        assert posts_by_id[2].name == 'Jane Doe'
        assert posts_by_id[2].email == 'jane@example.com'
        assert posts_by_id[2].content == 'Hello world, I\'m Jane!'