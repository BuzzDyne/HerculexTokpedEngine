from typing import List
from DataModel.utils import convertISO8601toUnix


class Order:
    def __init__(
        self,
        ecommerce_code,
        feeding_dt,
        pltf_deadline_dt,
        buyer_id,
        ecom_order_id,
        ecom_order_status,
        invoice_ref,
        list_of_items=None,
    ):
        self.ecommerce_code = ecommerce_code
        self.feeding_dt = feeding_dt
        self.pltf_deadline_dt = pltf_deadline_dt
        self.buyer_id = buyer_id
        self.ecom_order_id = ecom_order_id
        self.ecom_order_status = ecom_order_status
        self.invoice_ref = invoice_ref
        self.list_of_items = list_of_items

    def __str__(self) -> str:
        return f"OrderID: {self.ecom_order_id}"


class OrderItem:
    def __init__(
        self,
        order_id,
        product_id,
        product_name,
        quantity,
        product_price,
        order_detail_id=None,
    ):
        self.order_detail_id = order_detail_id
        self.order_id = order_id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.product_price = product_price


def createTokpedOrder(input) -> Order:
    obj = createOrder(input, "T")
    return obj


def createOrder(input, ecom_code) -> Order:
    listOfDetails = createListOfOrderItem(input)

    done_by = input["shipment_fulfillment"]["confirm_shipping_deadline"]

    obj = Order(
        ecommerce_code=ecom_code,
        feeding_dt=input["create_time"],
        buyer_id=input["buyer"]["id"],
        pltf_deadline_dt=convertISO8601toUnix(done_by) if done_by != "" else None,
        ecom_order_id=input["order_id"],
        ecom_order_status=input["order_status"],
        invoice_ref=input["invoice_ref_num"],
        list_of_items=listOfDetails,
    )

    return obj


def createListOfOrderItem(data) -> List[OrderItem]:
    orderID = data["order_id"]

    res = []

    for i in data["products"]:
        res.append(OrderItem(orderID, i["id"], i["name"], i["quantity"], i["price"]))

    return res
