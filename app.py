from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from models import db, connect_db, User, UserFeedback, Comments
from forms import NewUserForm, LoginUserForm
import requests
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime
import os

from dotenv import load_dotenv


load_dotenv()
apiKey = os.getenv("apiKey")

CURR_USER_ID = "curr_user"

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cocktaildb"
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///cocktaildb_test"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["SECRET_KEY"] = "password123"


connect_db(app)

base_api = f"https://www.thecocktaildb.com/api/json/v2/{apiKey}"


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


def user_data():
    return {"user_id": session.get("curr_user")}


app.context_processor(user_data)


@app.route("/")
def show_home():
    """Shows landing page"""
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def search():
    """Helper function for homepage Search
    Searches API for cocktails and ingredients matching the args given
    """
    query = request.args.get("query", "")
    resp = requests.get(base_api + f"/search.php?s={query}")
    result = requests.get(base_api + f"/search.php?i={query}")
    return [resp.text, result.text]


@app.route("/user/signup", methods=["GET", "POST"])
def user_signup():
    """Shows signup page/Handles user signup"""
    if g.user:
        flash("A user is already logged in.", "danger")
        return redirect("/")
    form = NewUserForm()
    if form.validate_on_submit():
        if form.password.data == form.confirm_password.data:
            username = form.username.data
            password = form.password.data
            email = form.email.data
            user = User.signup(username=username, password=password, email=email)
            db.session.commit()
            flash(f"Happy Mixing, {username}", "success")
            do_login(user)
            return redirect("/")
        else:
            flash("Passwords must match!", "danger")

    return render_template("/user/signup.html", form=form)


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    """Shows login page/Handles user login"""
    if g.user:
        flash("A user is already logged in.", "danger")
        return redirect("/")

    form = LoginUserForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("user/login.html", form=form)


@app.route("/user/logout")
def logout():
    """Handle logout of user."""
    if session[CURR_USER_ID]:
        session.pop(CURR_USER_ID)
        flash("You have successfully logged out!", "success")
    else:
        flash("You do not have access to this page", "danger")
    return redirect("/")


@app.route("/cocktails")
def list_cocktails():
    """Shows list of popular cocktails"""
    user = None
    favorites = None
    response = requests.get(base_api + "/popular.php")
    data = response.json()
    if g.user:
        user = g.user
        favorites = user.favorites()
    return render_template(
        "cocktails.html", cocktails=data["drinks"], user=user, favorites=favorites
    )


@app.route("/cocktails/<int:id>")
def show_cocktail_detail(id):
    """Shows the detail page for cocktail of id"""
    response = requests.get(base_api + f"/lookup.php?i={id}")
    data = response.json()
    cocktail = data["drinks"]
    ingredients_list = [
        ingredient.get(f"strIngredient{i}")
        for ingredient in cocktail
        for i in range(1, 15)
        if ingredient.get(f"strIngredient{i}") is not None
    ]
    ingredients = {}
    for i, ingredient in enumerate(ingredients_list):
        ingredients[ingredient] = cocktail[0].get(f"strMeasure{i+1}")
    cocktail[0]["strInstructions"] = cocktail[0]["strInstructions"].replace(
        ".", ".<br>"
    )

    if g.user:
        try:
            feedback = UserFeedback.query.filter(
                UserFeedback.user_id == g.user.id, UserFeedback.cocktail_id == id
            ).one()
        except NoResultFound:
            feedback = None
    else:
        feedback = None
    all_feedback = UserFeedback.query.filter(UserFeedback.cocktail_id == id).all()
    likes = len(
        [feedback for feedback in all_feedback if feedback.like_boolean == True]
    )
    dislikes = len(
        [feedback for feedback in all_feedback if feedback.like_boolean == False]
    )
    comments = Comments.query.filter(Comments.cocktail_id == id).all()

    return render_template(
        "cocktail.html",
        comments=comments,
        cocktail=cocktail[0],
        ingredients=ingredients,
        user=g.user,
        feedback=feedback,
        likes=likes,
        dislikes=dislikes,
    )


@app.route("/ingredients/<ingredient>")
def list_ingredients(ingredient):
    """Shows detail page for ingredient"""
    response = requests.get(base_api + f"/search.php?i={ingredient}")
    ingredientJson = response.json()

    res = requests.get(base_api + f"/filter.php?i={ingredient}")
    cocktails = res.json()

    return render_template(
        "ingredients.html",
        ingredient=ingredientJson["ingredients"][0],
        cocktails=cocktails["drinks"],
    )


@app.route("/user/favorite/<int:id>", methods=["POST"])
def add_favorite(id):
    """Creates/Edits user feedback to add or remove a favorite for cocktail of id"""
    if not g.user:
        flash("Not Authorized to perform this action", "danger")
        return redirect(f"/cocktails/{id}")
    try:
        feedback = UserFeedback.query.filter(
            UserFeedback.cocktail_id == id, UserFeedback.user_id == g.user.id
        ).one()
        print(feedback)
    except NoResultFound:
        feedback = None
    if feedback == None:
        new_feedback = UserFeedback(
            user_id=g.user.id, cocktail_id=id, favorite_boolean=True
        )
        db.session.add(new_feedback)
        db.session.commit()
    elif feedback.favorite_boolean == True:
        feedback.favorite_boolean = False
    else:
        feedback.favorite_boolean = True
    db.session.commit()
    return redirect(f"/cocktails/{id}")


@app.route("/user/favorites")
def list_favorites():
    """Views users favorite cocktails"""
    if not g.user:
        flash("Not Authorized to perform this action", "danger")
        return redirect("/")
    favorites = []
    for favorite_id in g.user.favorites():
        resp = requests.get(base_api + f"/lookup.php?i={favorite_id}")
        json_data = resp.json()
        favorites.append(json_data["drinks"][0])
    print(g.user.favorites())
    return render_template(
        "/user/favorites.html",
        user=g.user,
        cocktails=favorites,
        favorites=g.user.favorites(),
    )


@app.route("/user/like/<int:id>", methods=["POST"])
def add_like(id):
    """Creates/Edits user feedback to add or remove a like for cocktail of id"""
    if not g.user:
        flash("Not Authorized to perform this action", "danger")
        return redirect(f"/cocktails/{id}")
    try:
        feedback = UserFeedback.query.filter(
            UserFeedback.cocktail_id == id, UserFeedback.user_id == g.user.id
        ).one()
    except NoResultFound:
        feedback = None
    if feedback == None:
        new_feedback = UserFeedback(
            user_id=g.user.id, cocktail_id=id, favorite_boolean=False, like_boolean=True
        )
        db.session.add(new_feedback)
        db.session.commit()
    elif feedback.like_boolean == True:
        feedback.like_boolean = None
    else:
        feedback.like_boolean = True
    db.session.commit()

    return redirect(f"/cocktails/{id}")


@app.route("/user/dislike/<int:id>", methods=["POST"])
def add_dislike(id):
    """Creates/Edits user feedback to add or remove a dislike for cocktail of id"""
    if not g.user:
        flash("Not Authorized to perform this action", "danger")
        return redirect("/")
    try:
        feedback = UserFeedback.query.filter(
            UserFeedback.cocktail_id == id, UserFeedback.user_id == g.user.id
        ).one()
    except NoResultFound:
        feedback = None
    if feedback == None:
        new_feedback = UserFeedback(
            user_id=g.user.id,
            cocktail_id=id,
            favorite_boolean=False,
            like_boolean=False,
        )
        db.session.add(new_feedback)
        db.session.commit()
    elif feedback.like_boolean == False:
        feedback.like_boolean = None
    else:
        feedback.like_boolean = False
    db.session.commit()

    return redirect(f"/cocktails/{id}")


@app.route("/cocktails/addcomment/<int:cocktail_id>", methods=["POST"])
def add_comment(cocktail_id):
    """Adds a comment from user for cocktail_id"""
    if not g.user:
        flash("Not Authorized to perform this action", "danger")
        return redirect(f"/cocktails/{cocktail_id}")
    data = request.form.get("commentInput")
    if len(data.strip()) == 0:
        flash("Invalid comment, must contain text", "danger")
        return redirect(f"/cocktails/{cocktail_id}")
    now = datetime.now()
    time = now.strftime("%m/%d/%Y %H:%M:%S")
    comment = Comments(
        comment=data,
        cocktail_id=cocktail_id,
        user_id=g.user.id,
        dateCreated=time,
        dateUpdated=time,
    )
    db.session.add(comment)
    db.session.commit()

    return redirect(f"/cocktails/{cocktail_id}")


@app.route("/cocktails/deletecomment/<int:comment_id>", methods=["POST"])
def delete_comment(comment_id):
    """Deletes comment of comment_id"""
    comment = Comments.query.filter(Comments.id == comment_id).one()
    if not g.user:
        flash("Not Authorized to perform this action", "danger")
        return redirect(f"/cocktails/{comment.cocktail_id}")
    db.session.delete(comment)
    db.session.commit()
    return redirect(f"/cocktails/{comment.cocktail_id}")
