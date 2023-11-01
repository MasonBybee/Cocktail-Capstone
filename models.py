from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()


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

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    @classmethod
    def signup(cls, username, password, email):
        """Sign up user.

        Hashes password and adds user to database.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(username=username, email=email, password=hashed_pwd)
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class Comments(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text(), nullable=False)
    cocktail_id = db.Column(db.Integer, nullable=False)
    dateCreated = db.Column(db.Text, nullable=False)
    dateUpdated = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Comment #{self.id}>"


class UserFeedback(db.Model):
    __tablename__ = "userFeedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    cocktail_id = db.Column(db.Integer, nullable=False)
    like_boolean = db.Column(db.Boolean)
    favorited = db.Column(db.Boolean, nullable=False)
