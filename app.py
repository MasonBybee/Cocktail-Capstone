from flask import Flask, render_template, request, flash, redirect, session, g
from models import db, User
from forms import NewUserForm

CURR_USER_ID = "curr_user"

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cocktaildb"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cocktaildb_test"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "password123"


def connect_db(app):
    db.app = app
    db.init_app(app)


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_ID in session:
        g.user = User.query.get(session[CURR_USER_ID])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_ID] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_ID in session:
        del session[CURR_USER_ID]


@app.route("/")
def show_home():
    return render_template("home.html")
