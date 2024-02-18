import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import logging as log


def register_event(date, data, opensearch_host):

    index_name = IndexList().tt_scheduled
    ops = Opensearch(index_name=index_name, host=opensearch_host)

    data['date'] = date.strftime("%Y-%m-%dT%H:%M:%S+00:00")
    ops.send(
        data=data
    )


class IndexList:
    def __init__(self):
        self.tt_trading_models = 'tt-trading-models'
        self.tt_trades = 'tt-trades'
        self.tt_ml_models = 'tt-ml-models'
        self.tt_scheduled = 'tt-scheduled'
        self.tt_positions = 'tt-positions'

class Opensearch:

    def __init__(self,
                 index_name='tt-trading-models',
                 host :str = None, 
                 username :str = None, 
                 password :str = None
                ):

        if username:
            self.auth = HTTPBasicAuth(self.username, self.password)
        else:
            self.auth = None

        self.host = host
        self.default_header = {"Content-Type": "application/json"}
        self.index_name = index_name

    def _request(self, method :str ='GET',url :str ='/docs'):
        
        response = requests.request(
            method,
            f"{self.host}{self.index_name}{url}",
            headers=self.default_header,
            auth=self.auth,
        )

        return response
    
    def get_one(self, pipeline_id):
        
        response = requests.request(
            "GET",
            f"{self.host}{self.index_name}/_doc/{pipeline_id}",
            headers=self.default_header,
            auth=self.auth,
        )
        response = response.json()
        response = response.get('_source')
        return response
            
    def read(self, query=None):
        """
        Update the status field of a document based on its custom 'id' field.

        Parameters:
            custom_id (str): The custom 'id' of the document.
            new_status (str): The new status to set.
        """
        # Step 1: Search for the document by its custom 'id' to get the OpenSearch _id

        response = requests.request(
            "GET",
            f"{self.host}{self.index_name}/_search",
            headers=self.default_header,
            auth=self.auth,
            json=query
        )

        response.raise_for_status()
        search_results = response.json()
        
        return search_results

    def get_by_id(self, id: str):
        log.info("Opensearch - get_by_id()")

        response = requests.request(
            "GET",
            f"{self.host}{self.index_name}/_doc/{id}",
            headers=self.default_header,
            auth=self.auth,
        )
        response = response.json()

        if response.get('found'):
            response = response.get('_source')
            return response
        else:
            log.warn(f"Record with ID: {id} not found")
            return None

    def send(self, data=None, test_id: str = None):
        
        try:
            _id = data.get('_id')
            if not _id:
                response = requests.request(
                    "POST",  # Changed from PUT to POST for auto-generating IDs
                    self.host + self.index_name + "/_doc/",
                    headers=self.default_header,
                    auth=self.auth,
                    json=data
                )

                log.info("Data sent successfully.")
            else:
                del data['_id']
                log.info(f"User Custom _id {_id}")
                response = requests.request(
                    "PUT",  # Changed from PUT to POST for auto-generating IDs
                    self.host + self.index_name + f"/_doc/{_id}",
                    headers=self.default_header,
                    auth=self.auth,
                    json=data
                )
            
            response.raise_for_status()
            return response
        except Exception as e:
            log.error(data)
            log.error(f"Failed to send data: {e}")

    def create_index(self, index_name: str = "my-first-request", schema=None):

        try:
            response = requests.request(
                "PUT",
                self.host + index_name,
                headers=self.default_header,
                auth=self.auth,
                data=json.dumps(schema)
            )
            
            
            if response.status_code == 400:
                log.warn('Init Index -------')
                log.warn(str(response.text))
                log.warn('-------------------')
                return
            response.raise_for_status()
            log.info(f"Index {index_name} created successfully.")
        except Exception as e:
            log.warn(f"Failed to create index: {e}")

    def get_index_records(self):
        try:
            response = requests.request(
                "GET",
                f"{self.host}{self.index_name}/_search",
                headers=self.default_header,
                auth=self.auth
            )

            response.raise_for_status()
            response = response.json()
            return response
        except Exception as e:
            log.error(f"Query failed: {e}")
            return

    def query_index(self, index_name: str=None, query=None):

        if index_name is None:
            index_name = self.index_name

        if query is None:
            query = {
                "query": {
                    "match_all": {}
                }
            }

        try:
            response = requests.request(
                "GET",
                f"{self.host}{index_name}/_search",
                headers=self.default_header,
                auth=self.auth,
                json=query
            )

            response.raise_for_status()
            log.info(response.json())
            return response.json()
        except Exception as e:
            log.error(f"Query failed: {e}")
            return

    def prepare_bulk_data(self, documents):
        bulk_data = ""
        for doc in documents:
            action = {"index": {"_index": self.index_name}}
            bulk_data += json.dumps(action) + "\n"
            bulk_data += json.dumps(doc["data"]) + "\n"
        return bulk_data

    def update_bulk(self, documents):
        
        try:
            url = f"{self.host}_bulk"
            log.info(url)
            bulk_data = self.prepare_bulk_data(documents)

            response = requests.request(
                "POST",
                url,
                headers=self.default_header,
                auth=self.auth,
                data=bulk_data
            )
            response.raise_for_status()

        except requests.RequestException as e:
    
            log.error(f"Error to send bulk: {e}")


    def update(self, document_id, data, date=None):

        try:
            
            url = f"{self.host}{self.index_name}/_doc/{document_id}"
            
            if not date:
                try:

                    now = datetime.utcnow()
                    now = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
                    log.info(f"[OPENSEARCH DATE FORMAT 1] {now}")
                    
                    data['date'] = now     
                    response = requests.request(
                        "PUT",
                        url,
                        headers=self.default_header,
                        auth=self.auth,
                        json=data
                    )
                    response.raise_for_status()
                except Exception as e:
                    now = datetime.now()
                    now = int(now.timestamp() * 1000)
                    log.info(f"[OPENSEARCH DATE FORMAT 1] {now}")
                    data['date'] = now
                    response = requests.request(
                        "PUT",
                        url,
                        headers=self.default_header,
                        auth=self.auth,
                        json=data
                    )

            else:
                data['date'] = date
                now = date
                log.info(f"[OPENSEARCH DATE FORMAT 3] {now}")
                response = requests.request(
                        "PUT",
                        url,
                        headers=self.default_header,
                        auth=self.auth,
                        json=data
                    )
            
            
            datetime_now = now
            log.info(f'[OPENSEARCH] Save one opensearch: {url} date: {datetime_now}')
            log.info(f'[OPENSEARCH] data: {data}')
            
            response = requests.request(
                "PUT",
                url,
                headers=self.default_header,
                auth=self.auth,
                json=data
            )
            
            if response.status_code == 400:
                log.warn("Not was saved on opensearch the data")
                log.warn(response.text)
                
            response.raise_for_status()
            log.info("Success Update opensearch document.")
            return response
        except Exception as e:
            log.error(f"Opensearch update failed: {e}")
            raise RuntimeError(f"NOT WAS POSSIBLE SAVE THE DATA ON OPENSEARCH, ADD THE FORMAT OF DATE ON OPENSEARCH INDEX {self.index_name} {str(e)}")

    def delete(self, document_id):

        try:

            query = {
                "query": {
                    "match": {
                        "_id": document_id
                    }
                }
            }

            response = requests.request(
                "POST",
                f"{self.host}{self.index_name}/_delete_by_query",
                headers=self.default_header,
                auth=self.auth,
                json=query
            )

            response.raise_for_status()
            log.info(response.json())

        except Exception as e:
            log.error(f"Opensearch update failed: {e}")
            return None

    def delete_all_data(self, index_name=None):

        query = {
            "query": {
                "match_all": {}
            }
        }
        
        response = requests.request(
                "POST",
                f"{self.host}{index_name}/_delete_by_query",
                headers=self.default_header,
                auth=self.auth,
                json=query
            )
        return response



class TradingModels:

    def schema(self):
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "date": {
                        "type": "date"
                        },
                    "name": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "best_return": {"type": "float"},
                    "best_return_sl": {"type": "float"},
                    "trades": {"type": "integer"},
                    "symbol": {"type": "keyword"},
                    "strategy": {"type": "keyword"},
                    "interval": {"type": "keyword"},
                    "is_crypto": {"type": "bool"},
                }
            }
        }


class MLModels:

    def schema(self):
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "date": {
                        "type": "date"
                        },
                    "name": {"type": "keyword"},
                    "stage": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "best_return": {"type": "float"},
                    "best_return_sl": {"type": "float"}
                }
            }
        }


class TTScheduled:

    def schema(self):
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "date": {
                        "type": "date"
                        },
                    "name": {"type": "keyword"},
                    "close": {"type": "float"},
                    "interval": {"type": "keyword"},
                    "action": {"type": "keyword"},
                    "client_order_id":  {"type": "keyword"}
                }
            }
        }



class TTPositions: 

    def schema(self):
        return {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "date": {
                        "type": "date"
                        },
                    "exchange": {"type": "keyword"},
                    "symbol": {"type": "keyword"},
                    "qty": {"type": "float"},
                    "market_value": {"type": "float"},
                    "cost_basis": {"type": "float"},
                    "asset_id": {"type": "text"},
                    "profit": {"type": "float"}
                }
            }
        }


# REGISTER INDEX ON OPENSEARCH
from config import Config

settings = Config()
index_name = IndexList().tt_positions
schema = TTPositions().schema()
ops_tt_positions = Opensearch(index_name=index_name, host=settings.opensearch_host)
ops_tt_positions.create_index(index_name=index_name, schema=schema)

index_name = IndexList().tt_scheduled
schema = TTScheduled().schema()
ops_tt_scheduled = Opensearch(index_name=index_name, host=settings.opensearch_host)
ops_tt_scheduled.create_index(index_name=index_name, schema=schema)

index_name_ml_models = IndexList().tt_ml_models
schema = MLModels().schema()
ops_tt_models = Opensearch(index_name=index_name_ml_models, host=settings.opensearch_host)
ops_tt_models.create_index(index_name=index_name_ml_models, schema=schema)