from __future__ import annotations
from enum import Enum

from typing import List, Optional

from pydantic import BaseModel


class Customer(BaseModel):
    id: int
    firstName: str
    lastName: str


class Address(BaseModel):
    firstName: str
    lastName: str
    company: str
    address1: str
    address2: str
    city: str
    cityCode: int
    cityId: int
    district: str
    districtId: int
    neighborhoodId: int
    neighborhood: str
    apartmentNumber: str
    floor: str
    doorNumber: str
    addressDescription: str
    postalCode: str
    countryCode: str
    latitude: str
    longitude: str
    phone: str


class Amount(BaseModel):
    seller: float


class Promotion(BaseModel):
    promotionId: int
    description: str
    discountType: str
    sellerCoverageRatio: float
    amount: Amount


class Amount1(BaseModel):
    seller: float


class Coupon(BaseModel):
    couponId: str
    description: str
    sellerCoverageRatio: float
    amount: Amount1


class Item(BaseModel):
    packageItemId: str
    lineItemId: int
    isCancelled: bool
    promotions: List[Promotion]
    coupon: Optional[Coupon]


class ModifierProduct1(BaseModel):
    name: str
    price: float
    productId: int
    modifierGroupId: int
    modifierProducts: List
    extraIngredients: List
    removedIngredients: List


class ExtraIngredient(BaseModel):
    id: int
    name: str
    price: float


class RemovedIngredient(BaseModel):
    id: int
    name: str


class ModifierProduct(BaseModel):
    name: str
    price: float
    productId: int
    modifierGroupId: int
    modifierProducts: List[ModifierProduct1]
    extraIngredients: List[ExtraIngredient]
    removedIngredients: List[RemovedIngredient]


class Line(BaseModel):
    price: float
    unitSellingPrice: float
    productId: int
    name: str
    items: List[Item]
    modifierProducts: List[ModifierProduct]
    extraIngredients: List
    removedIngredients: List


class MealCard(BaseModel):
    cardSourceType: str


class CancelInfo(BaseModel):
    reasonCode: int


class Payment(BaseModel):
    paymentType: Optional[str]
    mealCard: Optional[MealCard]
    customerNote: Optional[str]
    lastModifiedDate: Optional[int]
    isCourierNearby: Optional[bool]
    cancelInfo: Optional[CancelInfo]
    eta: Optional[str]
    testPackage: Optional[bool]
    pickupEtaState: Optional[str]
    estimatedPickupTimeMin: Optional[int]
    estimatedPickupTimeMax: Optional[int]


class Order(BaseModel):
    id: str
    supplierId: int
    storeId: int
    orderCode: str
    orderId: str
    orderNumber: str
    packageCreationDate: int
    packageModificationDate: int
    preparationTime: int
    totalPrice: float
    callCenterPhone: str
    deliveryType: str
    customer: Customer
    address: Address
    packageStatus: str
    lines: List[Line]
    payment: Payment



class OrderStatus(str, Enum):
    Created = "Created"
    Picking = "Picking"
    Invoiced = "Invoiced"
    Cancelled = "Cancelled"
    UnSupplied = "UnSupplied"
    Shipped = "Shipped"
    Delivered = "Delivered"


class OrderCancelReasonType(str, Enum):
    SupplyProblem = "621"
    StoreClosed = "622"
    StoreCannotPrepareOrder = "623"
    StoreBusy = "624"
    OutOfArea = "626"
    OrderConfusion = "627"


class OrderResponse(BaseModel):
    current_page: int
    page: int
    size: int
    totalPages: int
    totalCount: int
    content: List[Order]

    @property
    def is_paginated(self) -> bool:
        return self.totalPages > 1
    
    @property
    def has_next_page(self) -> bool:
        return self.current_page < self.totalPages
    