from __future__ import annotations
from enum import Enum

from typing import List, Optional

from pydantic import BaseModel


class ProductStatus(str, Enum):
    Active = "ACTIVE"
    Passive = "PASSIVE"


class Ingredient(BaseModel):
    id: int
    name: str
    price: int
    status: str


class ModifierProduct(BaseModel):
    id: int
    position: int
    price: int


class ModifierGroup(BaseModel):
    id: int
    max: Optional[int]
    min: Optional[int]
    modifierProducts: Optional[List[ModifierProduct]]
    name: Optional[str]
    position: Optional[int]


class MenuProduct(BaseModel):
    id: int
    description: Optional[str]
    ingredients: List[int]
    extraIngredients: List[int]
    modifierGroups: List[ModifierGroup]
    name: str
    originalPrice: Optional[int]
    ownSellable: bool
    sellingPrice: int
    status: str


class SectionProduct(BaseModel):
    id: int
    position: int


class Section(BaseModel):
    name: str
    position: int
    products: List[SectionProduct]
    status: str


class Menu(BaseModel):
    ingredients: List[Ingredient]
    modifierGroups: List[ModifierGroup]
    products: List[MenuProduct]
    sections: List[Section]
