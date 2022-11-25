from typing import List
from DataModel.utils import convertISO8601toUnix


class Order():
    def __init__(self, order_id, buyer_id, invoice_ref_num, order_status, ts_created, ts_acc_by, ts_ship_by, list_of_items):
        self.order_id           = order_id
        self.buyer_id           = buyer_id
        self.invoice_ref_num    = invoice_ref_num
        self.order_status       = order_status
        self.ts_created         = ts_created
        self.ts_acc_by          = ts_acc_by
        self.ts_ship_by         = ts_ship_by
        self.list_of_items    = list_of_items


class OrderItem():
    def __init__(self, order_id, product_id, product_name, quantity, product_price, order_detail_id=None):
        self.order_detail_id    = order_detail_id
        self.order_id           = order_id
        self.product_id         = product_id
        self.product_name       = product_name
        self.quantity           = quantity
        self.product_price      = product_price


def createOrder(input) -> Order:

    listOfDetails = createListOfOrderItem(input)

    obj = Order(
        input['order_id'],
        input['buyer']['id'],
        input['invoice_ref_num'],
        input['order_status'],
        input['create_time'],
        convertISO8601toUnix(input['shipment_fulfillment']['accept_deadline']),
        convertISO8601toUnix(input['shipment_fulfillment']['confirm_shipping_deadline']),
        listOfDetails
    )

    return obj

def createListOfOrderItem(data) -> List[OrderItem]:
    orderID = data['order_id']

    res = []

    for i in data['products']:
        res.append(OrderItem(orderID, i['id'], i['name'], i['quantity'], i['price']))

    return res
