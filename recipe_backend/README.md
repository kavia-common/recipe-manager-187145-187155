# Recipe Backend (Flask)

A simple Flask REST API that allows users to browse, add, update, and delete recipes. It uses SQLite (via SQLAlchemy) by default, includes OpenAPI docs, CORS for local development, and seeds a few recipes on first run.

## Quick Start

- Python 3.10+ recommended
- Install dependencies:

```bash
pip install -r requirements.txt
```

- Run the server:

```bash
python run.py
```

The server starts on http://localhost:3001 and exposes:
- Swagger UI: http://localhost:3001/docs
- OpenAPI JSON: http://localhost:3001/openapi.json

It will create a SQLite DB file `recipes.db` in the working directory and seed a couple of sample recipes if empty.

## Configuration

Environment variables (all optional, sensible defaults provided):
- PORT: Server port (default 3001)
- HOST: Bind host (default 0.0.0.0)
- FLASK_ENV: development or production (default development)
- DATABASE_URL: SQLAlchemy connection string (default sqlite:///recipes.db)
- SECRET_KEY: Flask secret key (default dev-secret)

See `.env.example` for reference.

## API

Base path: `/api/recipes`

Response structure:
- Success: `{ "data": <payload>, "error": null }`
- Error: `{ "data": null, "error": { "code": "<code>", "message": "<message>", "details": { ... } } }`

### List recipes
GET `/api/recipes?search=<str>&tag=<str>&page=<int>&page_size=<int>`

Response:
```
{
  "data": {
    "items": [Recipe],
    "total": 2,
    "page": 1,
    "page_size": 10
  },
  "error": null
}
```

### Create recipe
POST `/api/recipes`
Body (JSON):
```
{
  "title": "Required",
  "description": "Optional",
  "ingredients": ["Required non-empty list of strings"],
  "steps": ["Required non-empty list of strings"],
  "tags": ["optional", "list"],
  "prep_time": 10,
  "cook_time": 15,
  "servings": 4
}
```
Returns 201 with the created recipe.

### Retrieve recipe
GET `/api/recipes/<id>`

### Update recipe (full)
PUT `/api/recipes/<id>` with same fields as create (validation enforced).

### Update recipe (partial)
PATCH `/api/recipes/<id>` with any subset of fields.

### Delete recipe
DELETE `/api/recipes/<id>` returns 204 on success.

## OpenAPI Docs
- Docs: `/docs`
- OpenAPI JSON: `/openapi.json`

## Development Notes
- Uses Flask-Smorest for routing and Swagger.
- Uses Flask-SQLAlchemy for persistence.
- `app/__init__.py` contains the app factory, error handlers, and seeding logic.
- Health check: `GET /` -> `{ "data": { "message": "Healthy" }, "error": null }`
