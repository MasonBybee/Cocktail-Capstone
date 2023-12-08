from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    comments = db.relationship("Comments", backref="user", cascade="all, delete-orphan")
    userFeedback = db.relationship(
        "UserFeedback", backref="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}>"

    def favorites(self):
        return [
            str(cocktail.cocktail_id)
            for cocktail in self.userFeedback
            if cocktail.favorite_boolean == True
        ]

    @classmethod
    def signup(cls, username, password, email):
        """Sign up user.

        Hashes password and adds user to database.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode("UTF-8")

        user = User(username=username, password=hashed_pwd, email=email)
        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

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
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Comment #{self.id}>"


class UserFeedback(db.Model):
    __tablename__ = "userfeedback"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    cocktail_id = db.Column(db.Integer, nullable=False)
    like_boolean = db.Column(db.Boolean)
    favorite_boolean = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"<UserFeedback #{self.id} user:{self.user_id}  cocktail:{self.cocktail_id}>"

    @classmethod
    def add_favorite(cls, user_id, cocktail_id):
        feedback = UserFeedback(
            user_id=user_id, cocktail_id=cocktail_id, like_boolean=True, favortied=True
        )
        db.session.add(feedback)
        return feedback

    @classmethod
    def remove_favorite(cls, user_id, cocktail_id):
        return UserFeedback.query.filter(user_id=user_id, cocktail_id=cocktail_id)
