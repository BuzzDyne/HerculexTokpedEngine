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

    def _testFnGetOrders(self, from_date = None, to_date = None):
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
                f'https://fs.tokopedia.net/v2/order/list?fs_id={self.fsID}&from_date={from_date}&to_date={to_date}&page=1&per_page=20&shop_id={self.shopID}',
                headers = header
            ) 
        except requests.RequestException as e:
            raise SystemExit(e)

        return response.json()['data']