import requests
import uuid

class AlpacaTrading:

    def __init__(self, api_key, api_secret, is_papertrade=True):
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://paper-api.alpaca.markets' if is_papertrade else 'https://api.alpaca.markets'

        self.headers = {
            'APCA-API-KEY-ID': self.api_key,
            'APCA-API-SECRET-KEY': self.api_secret
        }

        self.is_papertrade = is_papertrade

    def _send_get_request(self, endpoint, params=None):
        url = self.base_url + endpoint
        response = requests.get(url, headers=self.headers, params=params)
        return response

    def _send_post_request(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.post(url, json=data, headers=self.headers)
        return response

    def _send_delete_request(self, endpoint, data):
        url = self.base_url + endpoint
        response = requests.delete(url, json=data, headers=self.headers)
        return response

    def get_open_positions(self):
        endpoint = '/v2/positions'
        response = self._send_get_request(endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def get_orders(self, order_id=None):
        endpoint = f'/v2/orders/{order_id}'
        response = self._send_get_request(endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
        

    def get_orders_list(self):

        endpoint = '/v2/orders'
        response = self._send_get_request(endpoint)
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
        
    def open_position(self, symbol, quantity, stop_loss, strategy_name, return_client_order_id :bool = False, time_in_force :str = 'gtc'):
        positions = self.get_open_positions()
        
        if positions:
            symbol_filter = symbol.replace('/', '')
            existing_positions = [pos for pos in positions if pos.get('symbol') == symbol_filter]
            if existing_positions:
                print(f'Position for {symbol_filter} already exists')
                return
        
        client_order_id = strategy_name + '@' + str(uuid.uuid4()).replace('-','')[:10]
        endpoint = '/v2/orders'
        order_data = {
            'symbol': symbol,
            'notional': quantity,
            'side': 'buy', 
            'type': 'market',
            'time_in_force': time_in_force,
            'stop_loss': {
                'stop_price': stop_loss
            },
            'client_order_id': client_order_id

        }
        
        response = self._send_post_request(endpoint, order_data)
        
        if response.status_code == 200:
            print(f"Position opened for {symbol}")
            if not return_client_order_id:
                return response.json()
            else:
                return client_order_id
        else:
            return None

    def close_position(self, symbol):
        endpoint = '/v2/positions'
        position_data = {
            'symbol': symbol
        }
        
        response = self._send_delete_request(endpoint, position_data)
        
        if response.status_code == 200:
            return True
        else:
            return False
