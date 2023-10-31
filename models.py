from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text(20), nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    comments = db.relationship("Comments", backref="user", cascade="all, delete-orphan")
    userFeedback = db.relationship(
        "UserFeedback", backref="user", cascade="all, delete-orphan"
    )


class Comments(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    cocktail_id = db.Column(db.Integer, nullable=False)
    dateCreated = db.Column(db.Text, nullable=False)
    dateUpdated = db.Column(db.Text, nullable=False)


class UserFeedback(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.Integer, primary_key=False, autoincrement=True)
    user_id = db.Column(db.Integer, ForeignKey=User.id)
    cocktail_id = db.Column(db.Integer, nullable=False)
    like_boolean = db.Column(db.Boolean)
    favorited = db.Column(db.Boolean, nullable=False)
