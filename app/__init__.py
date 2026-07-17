import datetime
import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from peewee import (
    MySQLDatabase,
    SqliteDatabase,
    Model,
    CharField,
    TextField,
    DateTimeField,
)
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    # File-backed rather than :memory. the app closes its connection after every
    # request and an in-memory db is dropped once its last connection closes.
    mydb = SqliteDatabase("test.sqlite")
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
    )


class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb


with mydb:
    mydb.create_tables([TimelinePost])


@app.before_request
def _db_connect():
    mydb.connect(reuse_if_open=True)


@app.teardown_request
def _db_close(exc):
    if not mydb.is_closed():
        mydb.close()

# Pages shown in the nav bar
PAGES = [
    {"name": "Home", "url": "/"},
    {"name": "Hobbies", "url": "/hobbies"},
    {"name": "Timeline", "url": "/timeline"},
]

# Placeholders
ABOUT = [
    {
        "name": "Andrei",
        "description": "Computer Science student at University College Cork, heading into my third year. I enjoy building things, contributing to my college's Claude Society, and exploring new places.",
    },
    {
        "name": "Ghadi",
        "description": "DevOps Engineering student at Polytech Montpellier and a DevOps apprentice at Genvia. I'm passionate about automation, cloud technologies, and cooking in my spare time.",
    },
]

WORK_EXP = [
    {
        "name": "Andrei",
        "entries": [
            {
                "title": "Claude Soc's Tutor",
                "dates": "Apr 2026 - Present",
                "description": "Do workshops and organize events",
            },
        ],
    },
    {
        "name": "Ghadi",
        "entries": [
            {
                "title": "Genvia",
                "dates": "Oct 2025 - Aug 2026",
                "description": "DevOps Apprentice",
            },
        ],
    },
]

EDUCATION = [
    {
        "name": "Andrei",
        "entries": [
            {
                "title": "BSc Computer Science",
                "subtitle": "University College Cork",
                "dates": "2024-2028",
                "description": "Currently going into the 3rd year.",
            },
        ],
    },
    {
        "name": "Ghadi",
        "entries": [
            {
                "title": "M.Eng Devops Engineering",
                "subtitle": "Polytech Montpellier",
                "dates": "2025-2028",
                "description": "A CS degree centered around DevOps technologies and methodoligies",
            },
        ],
    },
]

HOBBIES = [
    {
        "name": "Ghadi",
        "color": "#1C539F",
        "entries": [
            {
                "title": "Gym",
                "description": "I enjoy strength training and pushing my limits at the gym to stay strong and focused.",
                "images": ["img/hobbies/ghadi-gym.jpg"],
            },
            {
                "title": "Cooking",
                "description": "Experimenting in the kitchen with new recipes is one of my favorite creative outlets.",
                "images": ["img/hobbies/ghadi-cooking.jpg"],
            },
            {
                "title": "Meeting new people",
                "description": "I love making new connections, hearing different perspectives, and building friendships along the way.",
                "images": ["img/hobbies/ghadi-meeting.jpg"],
            },
        ],
    },
    {
        "name": "Andrei",
        "color": "#e74c3c",
        "entries": [
            {
                "title": "Reading",
                "description": "Whether it's sci-fi or a tech deep-dive, I always have a book within arm's reach.",
                "images": ["img/hobbies/andrei-reading.jpg"],
            },
            {
                "title": "Hiking",
                "description": "Getting out on the trails and into nature is my favorite way to reset on weekends.",
                "images": ["img/hobbies/andrei-hiking.jpg"],
            },
            {
                "title": "Music",
                "description": "I enjoy discovering new artists and curating playlists for every mood.",
                "images": ["img/hobbies/andrei-music.jpg"],
            },
        ],
    },
]

TRAVEL = [
    {
        "name": "Ghadi",
        "color": "#1C539F",
        "countries": [
            {"name": "Lebanon", "lat": 33.8547, "lng": 35.8623},
            {"name": "France", "lat": 46.2276, "lng": 2.2137},
            {"name": "Spain", "lat": 40.4637, "lng": -3.7492},
            {"name": "Turkey", "lat": 38.9637, "lng": 35.2433},
            {"name": "Switzerland", "lat": 46.8182, "lng": 8.2275},
        ],
    },
    {
        "name": "Andrei",
        "color": "#e74c3c",
        "countries": [
            {"name": "Ireland", "lat": 53.1424, "lng": -7.6921},
            {"name": "UK", "lat": 55.3781, "lng": -3.4360},
            {"name": "Singapore", "lat": 1.3521, "lng": 103.8198},
            {"name": "Egypt", "lat": 26.8206, "lng": 30.8025},
            {"name": "Serbia", "lat": 44.0165, "lng": 21.0059},
        ],
    },
]


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="MLH Fellows",
        url=os.getenv("URL"),
        pages=PAGES,
        about=ABOUT,
        work_experiences=WORK_EXP,
        education=EDUCATION,
    )


@app.route("/hobbies")
def hobbies():
    return render_template(
        "hobbies.html",
        title="Hobbies",
        url=os.getenv("URL"),
        pages=PAGES,
        hobbies=HOBBIES,
        travel=TRAVEL,
    )


@app.route("/timeline")
def timeline():
    return render_template(
        "timeline.html",
        title="Timeline",
        url=os.getenv("URL"),
        pages=PAGES,
    )


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@app.route("/api/timeline_post", methods=["POST"])
def create_timeline_post():
    # The timeline page posts JSON; form-encoded bodies are accepted too.
    data = request.get_json(silent=True) or request.form
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    content = (data.get("content") or "").strip()

    if not name:
        return jsonify({"error": "Invalid name"}), 400
    if not content:
        return jsonify({"error": "Invalid content"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email"}), 400

    post = TimelinePost.create(name=name, email=email, content=content)
    return jsonify(model_to_dict(post)), 201


@app.route("/api/timeline_post", methods=["GET"])
def get_timeline_posts():
    posts = TimelinePost.select().order_by(TimelinePost.created_at.desc())
    return jsonify([model_to_dict(post) for post in posts])


@app.route("/api/timeline_post/<int:post_id>", methods=["DELETE"])
def delete_timeline_post(post_id):
    post = TimelinePost.get_or_none(TimelinePost.id == post_id)
    if post is None:
        return jsonify({"error": "not found"}), 404
    post.delete_instance()
    return "", 204
