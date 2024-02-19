import base64
from requests import Session
from dotenv import load_dotenv
import os

from models.Menu import Menu, ProductStatus
from models.Order import OrderCancelReasonType, OrderResponse, OrderStatus, Order
from models.Restaurant import RestaurantStatus, RestaurantsResponse


class Crawler:
    def __init__(self):
        load_dotenv()
        self.url = os.environ["BASE_URL"]
        
        
        self.headers = {
            "User-Agent": os.environ["USER_AGENT"],
            "Authorization": f"Basic {base64.b64encode(str(os.environ['API_KEY'] + ':' + os.environ['API_SECRET']).encode('ascii')).decode('ascii')}"
        }
        self.session = Session()

    
    def get_restaurants(self) -> RestaurantsResponse:
        url_path = "restaurants"
        params = {
            "page": 0,
            "size": 50
        }
        response = self.session.get(self.url + url_path, headers=self.headers, params=params).json()
        return RestaurantsResponse(**response)

    def update_restaurant_status(self, restaurant_id: str, status: RestaurantStatus):
        url_path = f"restaurants/{restaurant_id}/status"
        
        self.session.put(self.url + url_path, headers=self.headers, json={"status": status})
        
        return "OK."
    
    def get_menu(self, restaurant_id: str) -> Menu:
        url_path = f"restaurants/{restaurant_id}/products"
        return Menu(**self.session.get(self.url + url_path, headers=self.headers).json())
    
    def update_product_status(self, restaurant_id: str, product_id: int, status: ProductStatus):
        url_path = f"restaurants/{restaurant_id}/products/{product_id}/status"
        data = {
            "status": status
        }
        self.session.put(self.url + url_path, headers=self.headers, json=data)
        return "Ok."
    
    def get_orders(self, page: int = 0, size: int = 50, status: OrderStatus = OrderStatus.Created) -> OrderResponse:
        url_path = "packages"
        _headers = self.headers
        _headers.update({
            "x-agentname": "SelfIntegration",
            "x-executor-user": "esat3515@gmail.com"
        }
        )
        params = {
            "page": page,
            "size": size,
            "packageStatuses": status
        }
        return OrderResponse(**self.session.get(self.url + url_path, headers=self.headers, params=params).json(), current_page=page)

    
    
    def cancel_order(self, order: Order, order_cancel_reason: OrderCancelReasonType):
        url_path = "packages/unsupplied"
        _headers = self.headers
        _headers.update({
            "x-agentname": "SelfIntegration",
            "x-executor-user": "esat3515@gmail.com"
        }
        )
        data = {
            "packageId": order.orderId,
            "reasonId": order_cancel_reason,
            "itemIdList": [item.lineItemId for line in order.lines for item in line.items]
        }
        self.session.put(self.url + url_path, headers=self.headers, json=data)
        return "Ok."
    
    
cw = Crawler()

orders = cw.get_orders(status=OrderStatus.UnSupplied)



menu = cw.get_menu(os.environ["RESTAURANT_ID"])




"""for product in menu.products:
    if "test" in product.name.lower():
        print(product.id)
        print(product.name)
        print(product.status)
        cw.update_product_status(product.id, ProductStatus.Active)
"""