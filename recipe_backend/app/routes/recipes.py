from typing import Any, Dict, Optional

from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

from ..models import db, Recipe, Ingredient, Step, Tag
from ..schemas import (
    RecipeSchema,
    RecipeCreateSchema,
    RecipeUpdateSchema,
    RecipePatchSchema,
    PaginatedRecipesSchema,
    RecipeListQuerySchema,
)


blp = Blueprint(
    "Recipes",
    "recipes",
    url_prefix="/api/recipes",
    description="Endpoints for creating, listing, updating and deleting recipes",
)


def success(data: Any, status: int = 200):
    return {"data": data, "error": None}, status


def fail(code: str, message: str, details: Optional[Dict] = None, status: int = 400):
    return {"data": None, "error": {"code": code, "message": message, "details": details or {}}}, status


def apply_collections(recipe: Recipe, data: Dict):
    """Replace related collections (ingredients, steps, tags) on a recipe from input lists."""
    if "ingredients" in data:
        recipe.ingredients.clear()
        for idx, text in enumerate(data.get("ingredients", []), start=1):
            recipe.ingredients.append(Ingredient(text=text, position=idx))

    if "steps" in data:
        recipe.steps.clear()
        for idx, text in enumerate(data.get("steps", []), start=1):
            recipe.steps.append(Step(text=text, position=idx))

    if "tags" in data:
        recipe.tags.clear()
        for text in sorted(set(data.get("tags", []))):
            recipe.tags.append(Tag(text=text))


@blp.route("/")
class RecipesList(MethodView):
    @blp.arguments(schema=RecipeListQuerySchema, location="query")
    @blp.response(200, PaginatedRecipesSchema)
    def get(self, args=None):
        """
        List recipes with optional search and tag filters.

        Query parameters:
        - search: Search in title or description (case-insensitive).
        - tag: Filter by tag text.
        - page: Page number (default 1).
        - page_size: Items per page (default 10).
        """
        q = Recipe.query
        # Prefer parsed args if provided by schema, otherwise fall back to request.args for safety
        search = (args or {}).get("search") if isinstance(args, dict) else None
        if search is None:
            search = request.args.get("search", type=str)
        tag = (args or {}).get("tag") if isinstance(args, dict) else None
        if tag is None:
            tag = request.args.get("tag", type=str)
        page = (args or {}).get("page") if isinstance(args, dict) else None
        if page is None:
            page = request.args.get("page", default=1, type=int)
        page_size = (args or {}).get("page_size") if isinstance(args, dict) else None
        if page_size is None:
            page_size = request.args.get("page_size", default=10, type=int)

        if search:
            like = f"%{search.lower()}%"
            q = q.filter(
                db.or_(db.func.lower(Recipe.title).like(like), db.func.lower(Recipe.description).like(like))
            )

        if tag:
            q = q.join(Recipe.tags).filter(Tag.text == tag)

        total = q.count()
        items = q.order_by(Recipe.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        data = {
            "items": [r.to_dict() for r in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
        return success(data)[0]

    @blp.arguments(RecipeCreateSchema)
    @blp.response(201, RecipeSchema)
    def post(self, json_data):
        """
        Create a new recipe.

        Required fields: title, ingredients, steps.
        """
        # Validate required lists exist (handled by schema), then create record
        recipe = Recipe(
            title=json_data["title"],
            description=json_data.get("description"),
            prep_time=json_data.get("prep_time"),
            cook_time=json_data.get("cook_time"),
            servings=json_data.get("servings"),
        )
        apply_collections(recipe, json_data)
        db.session.add(recipe)
        db.session.commit()
        return success(recipe.to_dict(), status=201)[0]


@blp.route("/<int:recipe_id>")
class RecipeDetail(MethodView):
    @blp.response(200, RecipeSchema)
    def get(self, recipe_id: int):
        """
        Retrieve a recipe by id.
        """
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return fail("not_found", "Recipe not found", status=404)
        return success(recipe.to_dict())[0]

    @blp.arguments(RecipeUpdateSchema)
    @blp.response(200, RecipeSchema)
    def put(self, json_data, recipe_id: int):
        """
        Full update a recipe by id.
        """
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return fail("not_found", "Recipe not found", status=404)
        recipe.title = json_data["title"]
        recipe.description = json_data.get("description")
        recipe.prep_time = json_data.get("prep_time")
        recipe.cook_time = json_data.get("cook_time")
        recipe.servings = json_data.get("servings")
        apply_collections(recipe, json_data)
        db.session.commit()
        return success(recipe.to_dict())[0]

    @blp.arguments(RecipePatchSchema)
    @blp.response(200, RecipeSchema)
    def patch(self, json_data, recipe_id: int):
        """
        Partial update a recipe by id.
        """
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return fail("not_found", "Recipe not found", status=404)

        for field in ["title", "description", "prep_time", "cook_time", "servings"]:
            if field in json_data:
                setattr(recipe, field, json_data.get(field))
        apply_collections(recipe, json_data)
        db.session.commit()
        return success(recipe.to_dict())[0]

    @blp.response(204)
    def delete(self, recipe_id: int):
        """
        Delete a recipe by id.
        """
        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return fail("not_found", "Recipe not found", status=404)
        db.session.delete(recipe)
        db.session.commit()
        # Return a standard success structure but with 204, Flask will drop body.
        return success(None, status=204)[0]
