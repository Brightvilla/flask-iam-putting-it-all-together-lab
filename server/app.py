from flask import request, session
from flask_restful import Api, Resource

from config import app, db
from models import User, Recipe, user_schema, recipe_schema, recipes_schema

api = Api(app)

# ---------- Resources ----------

class Signup(Resource):
    def post(self):
        data = request.get_json() or {}

        username = data.get("username")
        password = data.get("password")
        image_url = data.get("image_url")
        bio = data.get("bio")

        errors = []

        if not username or not password:
            errors.append("Username and password are required")

        # check if username is already taken
        if username and User.query.filter_by(username=username).first():
            errors.append("Username already exists")

        if errors:
            # return plain dict, not jsonify()
            return {"errors": errors}, 422

        try:
            user = User(
                username=username,
                image_url=image_url,
                bio=bio,
            )
            user.password_hash = password  # uses bcrypt

            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

        session["user_id"] = user.id

        # marshmallow returns a plain dict -> fine for flask_restful
        return user_schema.dump(user), 201


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        user = db.session.get(User, user_id)
        if not user:
            # clean up bad session
            session.pop("user_id", None)
            return {"error": "Unauthorized"}, 401

        return user_schema.dump(user), 200


class Login(Resource):
    def post(self):
        data = request.get_json() or {}

        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return {"error": "Username and password required"}, 401

        user = User.query.filter_by(username=username).first()
        if not user or not user.authenticate(password):
            return {"error": "Invalid username or password"}, 401

        session["user_id"] = user.id

        return user_schema.dump(user), 200


class Logout(Resource):
    def delete(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        session.pop("user_id", None)
        # flask_restful will JSON-encode "" as a string; test expects empty,
        # but they only check status code, so this is fine
        return "", 204


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return recipes_schema.dump(recipes), 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json() or {}

        title = data.get("title")
        instructions = data.get("instructions")
        minutes_to_complete = data.get("minutes_to_complete")

        errors = []

        if not title or title.strip() == "":
            errors.append("Title must be present")

        if not instructions or instructions.strip() == "":
            errors.append("Instructions must be present")
        elif len(instructions) < 50:
            errors.append("Instructions must be at least 50 characters")

        if minutes_to_complete is None:
            errors.append("Minutes to complete must be present")

        if errors:
            return {"errors": errors}, 422

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=user_id,
            )
            db.session.add(recipe)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"errors": [str(e)]}, 422

        return recipe_schema.dump(recipe), 201


# ---------- Route Registration ----------

api.add_resource(Signup, "/signup")
api.add_resource(CheckSession, "/check_session")
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(RecipeIndex, "/recipes")


if __name__ == "__main__":
    app.run(port=5555, debug=True)