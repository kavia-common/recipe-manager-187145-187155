from __future__ import annotations

import os
from typing import Dict

from flask import Flask, jsonify
from flask_cors import CORS
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

from .models import db, Recipe, Ingredient, Step, Tag
from .routes.health import blp as health_blp
from .routes.recipes import blp as recipes_blp


def create_app() -> Flask:
    """
    PUBLIC_INTERFACE
    Create and configure the Flask application.

    - Initializes CORS and OpenAPI docs with Flask-Smorest.
    - Configures SQLAlchemy using DATABASE_URL if provided, otherwise SQLite file in instance folder.
    - Creates all tables automatically and seeds initial sample data if DB is empty.
    - Registers health and recipe blueprints.

    Environment variables:
    - DATABASE_URL: SQLAlchemy connection string (default: sqlite:///recipes.db)
    - FLASK_ENV: Flask environment (development/production), used for defaults
    - SECRET_KEY: Secret key for session/CSRF (optional)
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Sensible defaults for configuration
    database_url = os.getenv("DATABASE_URL", "sqlite:///recipes.db")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", database_url)
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
    app.config.setdefault("SECRET_KEY", os.getenv("SECRET_KEY", "dev-secret"))

    # OpenAPI/Swagger config
    # Expose Swagger UI at /docs and OpenAPI JSON at /openapi.json
    # Using flask-smorest defaults with URL prefix at root
    app.config["API_TITLE"] = "Recipe API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Enable CORS for local development
    CORS(app, resources={r"/**": {"origins": "*"}})

    # Init extensions
    db.init_app(app)
    api = Api(app)

    # Register blueprints
    api.register_blueprint(health_blp)
    api.register_blueprint(recipes_blp)

    # Consistent JSON error handling
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"data": None, "error": {"code": "not_found", "message": "Resource not found", "details": {}}}), 404

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"data": None, "error": {"code": "bad_request", "message": "Bad request", "details": {}}}), 400

    @app.errorhandler(422)
    def unprocessable(e):
        # Marshmallow / webargs validation error wrapper
        messages = getattr(e, "data", {}).get("messages", {})
        return jsonify({"data": None, "error": {"code": "validation_error", "message": "Validation error", "details": messages}}), 400

    @app.errorhandler(Exception)
    def generic_error(e):
        # As a fallback, mask internal errors
        return jsonify({"data": None, "error": {"code": "internal_error", "message": "An unexpected error occurred", "details": {}}}), 500

    # Create all tables and seed
    with app.app_context():
        db.create_all()
        _seed_if_empty()

    return app


def _seed_if_empty():
    """Seed database with a few sample recipes if empty (idempotent)."""
    if Recipe.query.count() > 0:
        return

    pancakes = Recipe(
        title="Fluffy Pancakes",
        description="Classic fluffy pancakes perfect for breakfast.",
        prep_time=10,
        cook_time=15,
        servings=4,
    )
    for idx, text in enumerate(
        [
            "1 1/2 cups all-purpose flour",
            "3 1/2 tsp baking powder",
            "1 tsp salt",
            "1 tbsp white sugar",
            "1 1/4 cups milk",
            "1 egg",
            "3 tbsp butter, melted",
        ],
        start=1,
    ):
        pancakes.ingredients.append(Ingredient(text=text, position=idx))
    for idx, text in enumerate(
        [
            "In a large bowl, sift together the flour, baking powder, salt and sugar.",
            "Make a well in the center and pour in the milk, egg and melted butter; mix until smooth.",
            "Heat a lightly oiled griddle over medium high heat.",
            "Pour batter onto the griddle; brown on both sides and serve hot.",
        ],
        start=1,
    ):
        pancakes.steps.append(Step(text=text, position=idx))
    for t in ["breakfast", "sweet", "quick"]:
        pancakes.tags.append(Tag(text=t))

    salad = Recipe(
        title="Simple Garden Salad",
        description="A fresh salad with seasonal vegetables.",
        prep_time=15,
        cook_time=0,
        servings=2,
    )
    for idx, text in enumerate(
        ["2 cups mixed greens", "1 tomato, sliced", "1/2 cucumber, sliced", "Olive oil", "Lemon juice", "Salt", "Pepper"],
        start=1,
    ):
        salad.ingredients.append(Ingredient(text=text, position=idx))
    for idx, text in enumerate(
        [
            "Wash and dry the greens.",
            "Combine greens, tomato, and cucumber in a bowl.",
            "Drizzle with olive oil and lemon juice, season with salt and pepper, toss and serve.",
        ],
        start=1,
    ):
        salad.steps.append(Step(text=text, position=idx))
    for t in ["salad", "healthy", "vegan"]:
        salad.tags.append(Tag(text=t))

    db.session.add_all([pancakes, salad])
    db.session.commit()


# Create a global app instance for run.py compatibility
app = create_app()
