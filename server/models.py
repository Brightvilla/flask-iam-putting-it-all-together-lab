from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from flask_bcrypt import Bcrypt
from marshmallow import Schema, fields

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    bio = db.Column(db.String)

    recipes = db.relationship("Recipe", backref="user", lazy=True)

    @property
    def password_hash(self):
        raise AttributeError("password_hash is not a readable attribute")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(
            password.encode("utf-8")
        ).decode("utf-8")

    def authenticate(self, password):
        return bcrypt.check_password_hash(
            self._password_hash, password.encode("utf-8")
        )

    @validates("username")
    def validate_username(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Username must be present")
        return value

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    @validates("title")
    def validate_title(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Title must be present")
        return value

    @validates("instructions")
    def validate_instructions(self, key, value):
        if not value or value.strip() == "":
            raise ValueError("Instructions must be present")
        if len(value) < 50:
            raise ValueError("Instructions must be at least 50 characters")
        return value

# ---------- Marshmallow schemas ----------

class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    image_url = fields.Str()
    bio = fields.Str()

class RecipeUserSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    image_url = fields.Str()
    bio = fields.Str()

class RecipeSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    instructions = fields.Str()
    minutes_to_complete = fields.Int()
    user = fields.Nested(RecipeUserSchema)

user_schema = UserSchema()
recipe_schema = RecipeSchema()
recipes_schema = RecipeSchema(many=True)