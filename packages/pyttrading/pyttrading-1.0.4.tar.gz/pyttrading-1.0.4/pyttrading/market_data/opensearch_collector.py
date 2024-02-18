import requests
import pandas as pd
import requests
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import pandas as pd
from ..indicators import days_ago
from datetime import datetime
from stockstats import StockDataFrame 


def add_days_ago(data, days):
    for i in range(1, days + 1):
        data[f'd{i}'] = data['close'].shift(i)
    data.dropna(inplace=True)
    return data

class OpensearchCollector:

    def __init__(self,
            url_opensearch: str = "http://localhost:9200",
            url_playground: str = "http://localhost:5005",
            time_amount :str = 10,
            time_unit :str = 'Minute'
            ):

        self.url_opensearch = url_opensearch
        self.url_playground = url_playground
        self.time_amount = time_amount
        self.time_unit = time_unit

    def get_latest_data(self, symbol):
        
        symbol_param = symbol.replace('/', '_')
        url = f"{self.url_opensearch}/{symbol_param.lower()}/_search"

        query = {
            "sort": [
                {"timestamp": {"order": "desc"}}
            ]
        }

        response = requests.get(url, json=query)

        if response.status_code == 200:
            data = response.json()
            hits = data.get("hits", {}).get("hits", [])

            if hits:
                latest_data = hits[0]["_source"]
                df = pd.DataFrame([latest_data])
                date = df['timestamp'][0] 
                date_object = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")


                return date_object
            else:
                print("No se encontraron datos para el rango especificado.")
                return None
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None


    def data_market_collect(self, symbol, interval, start_date, end_date):
        symbol_param = symbol.replace('/', '_')
        url = f"{self.url_opensearch}/{symbol_param.lower()}/_search"
        # "2023-11-01T09:00:00+00:00",
        query = {
            "query": {
                "range": {
                "timestamp": {
                "gte": start_date.strftime('%Y-%m-%dT%H:%M:%S+00:00'),
                "lt": end_date.strftime('%Y-%m-%dT%H:%M:%S+00:00')
                }
            }
            },
            "aggs": {
                "custom": {
                    "date_histogram": {
                        "field": "timestamp",
                        "interval": interval,
                        "format": "yyyy-MM-dd HH:mm:ss"
                    },
                    "aggs": {
                        "open": {
                            "avg": {
                                "field": "open"
                            }
                        },
                        "high": {
                            "max": {
                                "field": "high"
                            }
                        },
                        "low": {
                            "min": {
                                "field": "low"
                            }
                        },
                        "close": {
                            "avg": {
                                "field": "close"
                            }
                        },
                        "volume": {
                            "sum": {
                                "field": "volume"
                            }
                        },
                        "trade_count": {
                            "sum": {
                                "field": "trade_count"
                            }
                        }
                    }
                }
            }
        }

        response = requests.get(url, json=query)

        if response.status_code == 200:
            data = response.json()
            aggregations = data.get("aggregations", {})
            custom = aggregations.get("custom", {})
            buckets =custom.get("buckets", [])

            data_list = []
            for bucket in buckets:
                data_dict = {
                    "timestamp": bucket.get("key_as_string"),
                    "open": bucket.get("open", {}).get("value"),
                    "high": bucket.get("high", {}).get("value"),
                    "low": bucket.get("low", {}).get("value"),
                    "close": bucket.get("close", {}).get("value"),
                    "volume": bucket.get("volume", {}).get("value"),
                    "trade_count": bucket.get("trade_count", {}).get("value")
                }
                data_list.append(data_dict)

            df = pd.DataFrame(data_list)
            if len(df) > 0:
                df = df.dropna(subset=['open'])
                df = df.rename(columns={'timestamp': 'date'})
                df['symbol'] = symbol
            return df
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def save_data_opensearch(self, symbols, start_date, end_date, time_amount, time_unit, is_crypto):
        
        url = f"{self.url_playground}/execute"
        if not is_crypto:
            data_type = 'stock'
        else: 
            data_type = 'crypto'
       
            
        params = {
            "symbols": symbols,
            "start_date.year": start_date.year,
            "start_date.month": start_date.month,
            "start_date.day": start_date.day,
            "start_date.hour": start_date.hour,
            "start_date.minute": start_date.minute,
            "end_date.year": end_date.year,
            "end_date.month": end_date.month,
            "end_date.day": end_date.day,
            "end_date.hour": end_date.hour,
            "end_date.minute": end_date.minute,
            "time_amount": time_amount,
            "time_unit": time_unit,
            "data_type": data_type
        }

        
        headers = {'accept': 'application/json'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None

    def market_data_days_ago(self, delay_minutes: int = 80, search_days_ago :int = 300, symbol :str = 'AMZN', data_type='stock', interval='1h', is_crypto=False):

        now_datetime = datetime.now()
        delta = timedelta(minutes=delay_minutes)
        delta_month = timedelta(days=search_days_ago)
        end_date = now_datetime - delta
        start_date = now_datetime - delta_month
        start_date_request = start_date

        latest_date_ops = self.get_latest_data(symbol=symbol)
        if isinstance(latest_date_ops, datetime):
            start_date = latest_date_ops


        self.save_data_opensearch(
            symbols=symbol, 
            start_date=start_date,
            end_date=end_date, 
            time_amount=self.time_amount, 
            time_unit=self.time_unit, 
            is_crypto=is_crypto
        )


        data = self.data_market_collect(
            symbol=symbol, 
            interval=interval,
            start_date=start_date_request,  
            end_date=end_date
            )



        return data
    

    def market_data(self, symbols: str = 'AMZN', start_date: str = '6/1/2021', end_date: str = '12/1/2021', interval: str = '1h', is_crypto=False):

        print('---------------------- >>')
        print(f'{symbols} {interval} from {start_date} to {end_date}')

        if ':' not in start_date:
            start_date = datetime.strptime(start_date, '%m/%d/%Y') if isinstance(start_date, str) else start_date
        else:
            start_date = datetime.strptime(start_date, '%m/%d/%Y %H:%M') if isinstance(start_date, str) else start_date

        if ':' not in end_date:
            end_date = datetime.strptime(end_date, '%m/%d/%Y') if isinstance(end_date, str) else end_date
        else:
            end_date = datetime.strptime(end_date, '%m/%d/%Y %H:%M') if isinstance(end_date, str) else end_date

        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)
        if end_date.tzinfo is not None:
            end_date = end_date.replace(tzinfo=None)
       
        start_date_required = start_date
        data_list = []

        if not isinstance(symbols,list):
            symbols = [symbols]
        for symbol in symbols:
    
            latest_date_ops = self.get_latest_data(symbol=symbol)
            if isinstance(latest_date_ops, datetime):
             
                if latest_date_ops.tzinfo is not None:
                    latest_date_ops = latest_date_ops.replace(tzinfo=None)
                start_date = max(start_date, latest_date_ops)
            
            self.save_data_opensearch(
                symbols=symbol, 
                start_date=start_date,
                end_date=end_date, 
                time_amount=self.time_amount, 
                time_unit=self.time_unit, 
                is_crypto=is_crypto
            )

            # Obtener datos del mercado
            data = self.data_market_collect(
                symbol=symbol, 
                interval=interval,
                start_date=start_date_required,  
                end_date=end_date
            )


            if hasattr(self, 'indicators') and self.indicators:
                data = StockDataFrame.retype(data)
                for indicator in self.indicators:
                    data[indicator]

            print(data)
            print(data_list)
            print(type(data))
            print(type(data_list))
            data_list.append(data)  # Agregar cada DataFrame a la lista

        data_pd = pd.concat(data_list, ignore_index=True)
        
        # if data_pd.get('date'):
        #     data_pd['date'] = pd.to_datetime(data_pd['date'])
        try:
            if 'date' in data_pd.columns:
                data_pd['date'] = pd.to_datetime(data_pd['date'])
        except:
            if data_pd.get('date'):
                data_pd['date'] = pd.to_datetime(data_pd['date'])

        return  data_pd


    def market_data_old(self, symbols :str = 'AMZN', start_date='6/1/2021', end_date='12/1/2021', interval='1h', points_ago :int =4):


        data_list = []  # Lista para almacenar los DataFrames individuales

        self.points_ago = 5
        self.indicators = ['boll_ub', 'boll_lb', 'boll']

        for symbol in symbols:
            self.save_data_opensearch(
                symbols=symbol, 
                start_date=start_date,
                end_date=end_date, 
                time_amount=self.time_amount, 
                time_unit=self.time_unit
            )

            # Resto del código para obtener datos
            data = self.data_market_collect(
                symbol=symbol, 
                interval=interval,
                start_date=start_date,  
                end_date=end_date
            )


            if self.points_ago:
                data = add_days_ago(data=data, days=self.points_ago)
            if self.indicators:
                data = StockDataFrame.retype(data)
        
            data_list.append(data)  # Agregar cada DataFrame a la lista
            
            data = days_ago(data=data, days=5)
            data_list.append(data)  # 


            for indicator in self.indicators:
                data[indicator]

        if data_list:
            concatenated_data = pd.concat(data_list, ignore_index=True)
            concatenated_data['date'] = pd.to_datetime(concatenated_data['date'])

            return concatenated_data
        else:
            return None

