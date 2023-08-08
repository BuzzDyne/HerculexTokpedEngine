import requests
from TokpedPackage import utils as u
from _cred import TokpedCred

class TokpedModule:
    def __init__(self):
        self.fsID           = TokpedCred['fsID']
        self.clientID       = TokpedCred['ClientID']
        self.clientSecret   = TokpedCred['ClientSecret']   
        self.shopID         = TokpedCred['HcxShopID']
        self.clientbase     = u.encode(self.clientID + ':' + self.clientSecret)
        self.accessToken    = self._fnGetAccessToken()

    def _fnGetAccessToken(self):
        try:
            response = requests.post(
                'https://accounts.tokopedia.com/token?grant_type=client_credentials',
                headers={
                'Authorization'   : 'Basic ' + self.clientbase,
                'Content-Length'  : '0',
                'User-Agent'      : 'PostmanRuntime/7.28.4',
                'Accept'          : '*/*',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Connection'      : 'keep-alive'
                }
            ) 
        except requests.RequestException as e:
            raise SystemExit(e)

        return response.json()['access_token']

    def getOrderBetweenTS(self, from_date = None, to_date = None):
        from_date   = from_date if from_date is not None    else '1669202785'
        to_date     = to_date   if to_date  is not None     else '1669312785'

        try:
            header = {
                'Authorization'   : 'Bearer ' + self.accessToken,
                'Content-Length'  : '0',
                'User-Agent'      : 'PostmanRuntime/7.28.4',
                'Accept'          : '*/*',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Connection'      : 'keep-alive'
            }
            
            response = requests.get(
                f'https://fs.tokopedia.net/v2/order/list?fs_id={self.fsID}&from_date={from_date}&to_date={to_date}&page=1&per_page=100&shop_id={self.shopID}',
                headers = header
            ) 
        except requests.RequestException as e:
            raise SystemExit(e)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise SystemExit(f"Error: {str(e)}")

        return response.json()['data']


    def _getOrderDetailByID(self, order_id):
        try:
            header = {
                'Authorization'   : 'Bearer ' + self.accessToken,
                'Content-Length'  : '0',
                'User-Agent'      : 'PostmanRuntime/7.28.4',
                'Accept'          : '*/*',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Connection'      : 'keep-alive'
            }

            response = requests.get(
                f'https://fs.tokopedia.net/v2/fs/{self.fsID}/order?order_id={order_id}',
                headers = header
            )

            response.raise_for_status()

            order_data = response.json()['data']
            return {
                'order_id'      : str(order_data['order_id']),
                'order_status'  : str(order_data['order_status']),
                'shipping_date' : str(order_data['shipping_date'])
            }
        except requests.exceptions.HTTPError as e:
          raise SystemExit(f"Error during API request: {e}")
        except requests.RequestException as e:
            raise SystemExit(f"HTTP Error: {e}")

    def getBatchOrderDetailByIDs(self, list_order_ids):
        '''Returns list of tuples (id, status)'''
        list_of_dicts_order_details = []

        for id in list_order_ids:
            list_of_dicts_order_details.append(self._getOrderDetailByID(id))

        return list_of_dicts_order_details