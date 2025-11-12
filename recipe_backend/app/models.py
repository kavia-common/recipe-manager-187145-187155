from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship


# SQLAlchemy database instance (initialized in app factory)
db = SQLAlchemy()


class Recipe(db.Model):
    """Recipe model representing a cooking recipe."""
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    description: Mapped[Optional[str]]
    prep_time: Mapped[Optional[int]]  # minutes
    cook_time: Mapped[Optional[int]]  # minutes
    servings: Mapped[Optional[int]]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    ingredients: Mapped[List["Ingredient"]] = relationship("Ingredient", cascade="all, delete-orphan", backref="recipe")
    steps: Mapped[List["Step"]] = relationship("Step", cascade="all, delete-orphan", backref="recipe")
    tags: Mapped[List["Tag"]] = relationship("Tag", cascade="all, delete-orphan", backref="recipe")

    def to_dict(self) -> dict:
        """Convert the recipe with related fields to a dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "ingredients": [i.text for i in sorted(self.ingredients, key=lambda x: x.position or 0)],
            "steps": [s.text for s in sorted(self.steps, key=lambda x: x.position or 0)],
            "tags": [t.text for t in sorted(self.tags, key=lambda x: x.text)],
            "prep_time": self.prep_time,
            "cook_time": self.cook_time,
            "servings": self.servings,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(db.ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    text: Mapped[str]
    position: Mapped[Optional[int]]


class Step(db.Model):
    __tablename__ = "steps"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(db.ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    text: Mapped[str]
    position: Mapped[Optional[int]]


class Tag(db.Model):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_id: Mapped[int] = mapped_column(db.ForeignKey("recipes.id", ondelete="CASCADE"), index=True)
    text: Mapped[str]
