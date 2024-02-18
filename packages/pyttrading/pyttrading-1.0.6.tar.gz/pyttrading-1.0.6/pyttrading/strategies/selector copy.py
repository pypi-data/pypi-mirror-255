from importlib import import_module
import json
import os
from ..backtesting_custom import GenericBacktesting

class ModelSelector: 
    
    def __init__(self, 
                model_name: str= "macd", 
                model_folder: str="strategies",
                type_model: str="basic",
                configuration=None,
                path_model :str ="",
                symbol :str = "",
                df=None,
                interval=None, 
                mlflow=None,
                bk_initial_money = 2000,
                bk_commission=0.02

            ):
        
        self.mlflow = mlflow
        self.model_name = model_name
        self.model_folder = model_folder
        self.type_model = type_model
        self.configuration = configuration
        self.df = df
        self.path_model = path_model
        self.symbol = symbol
        self.interval = interval

        self.bk_initial_money = bk_initial_money
        self.bk_commission = bk_commission
        
        self.strategy_id=f"{self.model_name}_{symbol.lower()}_{interval}"

    def init_tmp_path(self):
         
        image_folder = self.path_model + "/images"

        if not os.path.exists(image_folder):
            os.mkdir(image_folder)
    
    def run_experiments(self):

        self.basic_strategies  = self.basic_models()
        self.strategy = self.basic_strategies (
                    strategy_name=self.model_name
                )
        method, best_return, best_parameters = self.strategy.experiment(
                    df=self.df
                )

        return method, best_return, best_parameters

    def save_mlflow(self):


        self.mlflow.set_tag("strategy", self.model_name)
        self.mlflow.set_tag("method", self.params.get('method'))
        self.mlflow.log_param("optimized_params", json.dumps(self.params))
        self.mlflow.log_metric('best_return',  self.params.get('best_return'))

        for key, value in self.stats_json.items():
            key_s = key.replace(" ",'').replace('[%]','').replace('.','').replace('&','').replace('[$]','').replace('(','').replace(')','').replace('#','')
            if '_' not in key_s:
                try:
                    self.mlflow.log_metric(key_s, value)
                except Exception:
                    pass

    def get_backtesting(self, bk_type='short', df=None):

        back_testing_short = GenericBacktesting(
                    df=df,
                    skip=True,
                    initial_money=self.bk_initial_money,
                    commission=self.bk_commission,
                    plot_result=False,
                    path_save_result=self.path_model,
                    print_stacks=False,
                    save_bk_figure=True,
                    bk_type=bk_type
                )

        best_return, stats_json = back_testing_short.calculate_bk()

        return best_return, stats_json

    def select(self):
        best_return = None
        best_return_short = None


        method, best_return, best_parameters = self.run_experiments()

        self.params = {
                    "type": self.type_model,
                    "method": method,
                    "best_return": best_return,
                    "best_parameters": list(best_parameters),
                    "params": list(best_parameters), 
                    "strategy": self.model_name
                }


        df_actions = self.strategy.eval(df=self.df, params=best_parameters)

        return_data, stats_json = self.get_backtesting(df=df_actions, bk_type='long')
        self.stats_json = stats_json
        self.save_mlflow()
        self.init_tmp_path()

        back_testing = GenericBacktesting(
                    df=df_actions,
                    skip=True,
                    initial_money=self.bk_initial_money,
                    commission=self.bk_commission,
                    plot_result=False,
                    path_save_result=self.path_model,
                    print_stacks=False,
                    save_bk_figure=True
                )

        return_data, self.stats_json = back_testing.calculate_bk()
        self.strategy.plot(df=df_actions, save_figure=True, show_graph=False, params=best_parameters, title=f"Strategy: {self.model_name} Return: {return_data}")

        best_return_short, _ = self.get_backtesting(df=df_actions, bk_type='short')
                
        return self.basic_strategies, self.params, best_return, best_return_short
        
        
    def basic_models(self):
        
        libray_trading = f"pyttrading.strategies.{self.model_name}"
        model_module = import_module(libray_trading)
        strategy = getattr(model_module, "Strategy")
        
        return strategy
    
    
    def execute(self, df):
        
        _strategy, params, best_return, best_return_short = self.select()
        strategy = _strategy()
        df_action = strategy.eval(df=df, params=params.get('params'))
        
        return best_return, df_action, best_return_short
        
    
    
    
    
     
    
    
    