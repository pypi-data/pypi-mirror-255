import yaml
import os
from stockstats import StockDataFrame
from ..market_data.opensearch_collector import OpensearchCollector
import mlflow
from config import Config

def get_configuration(func):
    def wrapper(*args, **kwargs):
        with open('config.yaml', 'r') as file:
            cfg = yaml.safe_load(file)
        return func(cfg, *args, **kwargs)
    return wrapper

def label_read_args(func):
    def wrapper(*args, **kwargs):
        config = Config()
        return func(config, *args, **kwargs)

    return wrapper

# Decorador para establecer variables de entorno para MLflow
def label_declare_environment_config_mlflow(func):
    def wrapper(config, *args, **kwargs):
        uri = config.mlflow_host
        os.environ['MLFLOW_TRACKING_USERNAME'] = config.mlflow_username
        os.environ['MLFLOW_TRACKING_PASSWORD'] = config.mlflow_token
        os.environ['MLFLOW_TRACKING_URI'] = uri
        mlflow.set_tracking_uri(uri)
        return func(config, *args, **kwargs)
    return wrapper

def declare_environment_variables_mlflow(func):
    def wrapper(cfg, *args, **kwargs):
        uri = cfg.get('mlflow').get('host')
        os.environ['MLFLOW_TRACKING_USERNAME'] = cfg.get('mlflow').get('username')
        os.environ['MLFLOW_TRACKING_PASSWORD'] = cfg.get('mlflow').get('token')
        os.environ['MLFLOW_TRACKING_URI'] = uri
        mlflow.set_tracking_uri(uri)
        return func(cfg, *args, **kwargs)
    return wrapper

# Decorador para obtener datos del mercado
def get_market_data(func):
    def wrapper(config, *args, **kwargs):

        symbols_periods = kwargs.get('symbols_periods')

        collector = OpensearchCollector(
            url_opensearch=config.url_opensearch,
            url_playground=config.url_playground,
        )
        return func(config, collector, *args, **kwargs)
    return wrapper

def get_indicators(df=None, indicators=None):

    data = StockDataFrame.retype(df)
    for indicator in indicators:
        data[indicator]

    return data

def label_collect_market_data(func):

    def wrapper(config, *args, **kwargs):
        configuration = kwargs.get("strategy_config")

        collector = OpensearchCollector(
            url_opensearch=config.url_opensearch,
            url_playground=config.url_playground,
            time_amount=configuration.get("time_amount", 10)
        )

        data =  collector.market_data(
                symbols=[configuration.get("symbol")],
                start_date=configuration.get("start_date"),
                end_date=configuration.get("end_date"),
                interval=configuration.get("interval"), 
                is_crypto=configuration.get("is_crypto")
            )

        data = get_indicators(df=data, indicators=configuration.get("indicators"))
        
        return func(data, *args, **kwargs)
    return wrapper


# Decorador para obtener datos del mercado
def read_mlflow_model(func):
    def wrapper( *args, **kwargs):
        symbols_periods = kwargs.get('symbols_periods')
        stage = kwargs.get('stage')

        model_uri = f"models:/{symbols_periods}/{stage}"
        model = mlflow.pyfunc.load_model(model_uri)
        
        return func(model,*args, **kwargs)
    return wrapper


def label_get_mlflow_experiment_id(func):
    def wrapper(data, *args, **kwargs):
        strategy_config = kwargs.get("strategy_config")
        experiment_name = f"{strategy_config.get('symbol')}_{strategy_config.get('interval')}_stats"
        
        experiment = mlflow.get_experiment_by_name(experiment_name)

        if experiment is None or experiment.lifecycle_stage == 'deleted':
            if experiment is None:
                experiment_id = mlflow.create_experiment(name=experiment_name)
            else:
                mlflow.tracking.MlflowClient().restore_experiment(experiment.experiment_id)
                experiment_id = experiment.experiment_id
        else:
            experiment_id = experiment.experiment_id

        return func(experiment_id, data, *args, **kwargs)
    return wrapper


def get_mlflow_strategies(func):

    def wrapper(config, *args, **kwargs):

        interval = kwargs.get('interval')
        stage = kwargs.get('stage')

        client = mlflow.tracking.MlflowClient()
        all_strategies = client.search_model_versions()

        strategies = []
        for st in all_strategies:
            if st.current_stage == stage:
                interval_st = st.tags.get('interval')
                stage_st = st.current_stage
            
                if stage_st == stage and interval_st == interval:
                    strategies.append(st)


        return func(strategies, *args, **kwargs)
    return wrapper
