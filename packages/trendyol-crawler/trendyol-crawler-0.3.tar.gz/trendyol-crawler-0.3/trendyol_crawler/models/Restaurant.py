from __future__ import annotations
from enum import Enum

from typing import List, Optional

from pydantic import BaseModel


class RestaurantStatus(str, Enum):
    Open = "Open"
    Closed = "Closed"


class Location(BaseModel):
    longitude: str
    latitude: str


class WorkingHour(BaseModel):
    dayOfWeek: str
    openingTime: str
    closingTime: str


class Restaurant(BaseModel):
    id: int
    name: str
    supplierId: int
    workingStatus: str
    address: str
    location: Location
    averageOrderPreparationTimeInMin: Optional[int]
    deliveryType: str
    phoneNumber: str
    email: str
    creationDate: int
    lastModifiedDate: int
    workingHours: List[WorkingHour]


class RestaurantsResponse(BaseModel):
    restaurants: List[Restaurant]
    totalPages: int
    totalElements: int
