
import pandas as pd
from pyttrading.strategies.selector import ModelSelector


def test_collect_market_data():

    data = pd.read_csv('data.csv')

    strategy_config  = { 
        "is_crypto": True,
        "symbol": 'AVAX/USD',
        "interval": '2m',
        "start_date": '11/1/2023',
        "end_date": '12/16/2023',
        "indicators": [
            "boll_ub",
            "boll_lb",
            "close_10_sma",
            "close_12_ema",
            "close_16_ema"
        ],
    }

    strategy_config = ModelSelector(
                    model_name='dummy',
                    path_model="tmp",
                    type_model="basic",
                    configuration=strategy_config, 
                    df=data,
                    symbol=strategy_config.get("symbol"),
                    interval=strategy_config.get("interval"),
                    mlflow=None
                )
    
    Strategy = strategy_config.basic_models()
    strategy = Strategy()
    df_actions = strategy.eval(df=data, params=None)


    assert len(df_actions[['actions']] ) > 0