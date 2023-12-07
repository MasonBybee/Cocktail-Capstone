from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from models import db, connect_db, User
from forms import NewUserForm, LoginUserForm
import requests
from secret import apiKey

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
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("query", "")
    resp = requests.get(base_api + f"/search.php?s={query}")
    result = requests.get(base_api + f"/search.php?i={query}")
    # return resp.text
    return [resp.text, result.text]


@app.route("/signup", methods=["GET", "POST"])
def user_signup():
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


@app.route("/login", methods=["GET", "POST"])
def user_login():
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


@app.route("/logout")
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
    response = requests.get(base_api + "/popular.php")
    data = response.json()
    return render_template("cocktails.html", cocktails=data["drinks"])


@app.route("/cocktails/<int:id>")
def show_cocktail_detail(id):
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

    return render_template(
        "cocktail.html", cocktail=cocktail[0], ingredients=ingredients
    )


@app.route("/ingredients/<ingredient>")
def list_ingredients(ingredient):
    response = requests.get(base_api + f"/search.php?i={ingredient}")
    ingredientJson = response.json()

    res = requests.get(base_api + f"/filter.php?i={ingredient}")
    cocktails = res.json()

    return render_template(
        "ingredients.html",
        ingredient=ingredientJson["ingredients"][0],
        cocktails=cocktails["drinks"],
    )
