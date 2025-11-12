from marshmallow import Schema, fields, validate, pre_load


def non_empty_list(item_type, field_name: str):
    return fields.List(item_type, required=True, validate=validate.Length(min=1), data_key=field_name)


class RecipeBaseSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1), description="Title of the recipe")
    description = fields.String(allow_none=True, missing=None, description="Recipe description")
    ingredients = non_empty_list(fields.String(validate=validate.Length(min=1)), "ingredients")
    steps = non_empty_list(fields.String(validate=validate.Length(min=1)), "steps")
    tags = fields.List(fields.String(validate=validate.Length(min=1)), missing=list, description="Tags")
    prep_time = fields.Integer(allow_none=True, missing=None, validate=validate.Range(min=0))
    cook_time = fields.Integer(allow_none=True, missing=None, validate=validate.Range(min=0))
    servings = fields.Integer(allow_none=True, missing=None, validate=validate.Range(min=1))

    @pre_load
    def ensure_lists(self, in_data, **kwargs):
        # Convert None to [] for optional list fields and strip strings
        for key in ["ingredients", "steps", "tags"]:
            if key in in_data and in_data[key] is None:
                in_data[key] = []
            if key in in_data and isinstance(in_data[key], list):
                in_data[key] = [str(x).strip() for x in in_data[key] if str(x).strip() != ""]
        return in_data


class RecipeListQuerySchema(Schema):
    """Query params for listing recipes with search, tag and pagination."""
    # PUBLIC_INTERFACE
    search = fields.String(
        allow_none=True,
        required=False,
        metadata={"description": "Search text to match title or description (case-insensitive)"},
    )
    # PUBLIC_INTERFACE
    tag = fields.String(
        allow_none=True,
        required=False,
        metadata={"description": "Filter results by exact tag text"},
    )
    # PUBLIC_INTERFACE
    page = fields.Integer(
        required=False,
        missing=1,
        validate=validate.Range(min=1),
        metadata={"description": "Page number (default 1)"},
    )
    # PUBLIC_INTERFACE
    page_size = fields.Integer(
        required=False,
        missing=10,
        validate=validate.Range(min=1, max=100),
        metadata={"description": "Items per page (default 10, max 100)"},
    )

class RecipeCreateSchema(RecipeBaseSchema):
    pass


class RecipeUpdateSchema(RecipeBaseSchema):
    pass


class RecipePatchSchema(Schema):
    title = fields.String(validate=validate.Length(min=1))
    description = fields.String(allow_none=True)
    ingredients = fields.List(fields.String(validate=validate.Length(min=1)))
    steps = fields.List(fields.String(validate=validate.Length(min=1)))
    tags = fields.List(fields.String(validate=validate.Length(min=1)))
    prep_time = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    cook_time = fields.Integer(allow_none=True, validate=validate.Range(min=0))
    servings = fields.Integer(allow_none=True, validate=validate.Range(min=1))

    @pre_load
    def clean_lists(self, in_data, **kwargs):
        for key in ["ingredients", "steps", "tags"]:
            if key in in_data and isinstance(in_data[key], list):
                in_data[key] = [str(x).strip() for x in in_data[key] if str(x).strip() != ""]
        return in_data


class RecipeSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    description = fields.String(allow_none=True)
    ingredients = fields.List(fields.String())
    steps = fields.List(fields.String())
    tags = fields.List(fields.String())
    prep_time = fields.Integer(allow_none=True)
    cook_time = fields.Integer(allow_none=True)
    servings = fields.Integer(allow_none=True)
    created_at = fields.String(allow_none=True)
    updated_at = fields.String(allow_none=True)


class PaginatedRecipesSchema(Schema):
    items = fields.List(fields.Nested(RecipeSchema))
    total = fields.Integer()
    page = fields.Integer()
    page_size = fields.Integer()
