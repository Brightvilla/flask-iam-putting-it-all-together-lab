from random import randint

from faker import Faker

from config import app, db
from models import User, Recipe

fake = Faker()

def create_users(count=5):
    users = []

    for i in range(count):
        username = f"user{i+1}"
        user = User(
            username=username,
            image_url=fake.image_url(),
            bio=fake.sentence(nb_words=10),
        )
        # simple password like "password1", etc.
        user.password_hash = f"password{i+1}"
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    return users

def create_recipes(users, count=10):
    recipes = []

    for i in range(count):
        user = fake.random_element(users)
        title = fake.sentence(nb_words=3)
        # ensure instructions length >= 50 chars
        instructions = " ".join(fake.sentences(nb=5))
        minutes_to_complete = randint(5, 120)

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=minutes_to_complete,
            user_id=user.id,
        )
        recipes.append(recipe)

    db.session.add_all(recipes)
    db.session.commit()
    return recipes

if __name__ == "__main__":
    with app.app_context():
        print("Clearing data...")
        Recipe.query.delete()
        User.query.delete()
        db.session.commit()

        print("Creating users...")
        users = create_users()

        print("Creating recipes...")
        create_recipes(users)

        print("Seeding complete.")