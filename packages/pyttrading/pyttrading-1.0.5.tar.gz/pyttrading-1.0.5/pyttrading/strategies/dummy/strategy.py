import numpy as np
from pyttrading.utils.logs import log
from scipy.optimize import minimize
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import os
from pyttrading.utils.pre_processing import remove_noise_trading
import pandas as pd
from ...backtesting_custom.generic_backtesting import GenericBacktesting

params_default = [(0.2, 0.4)]
params_init = 0.3


class Strategy: 

    def __init__(self, df=None, strategy_name :str = "StrategyName"):
        self.name = 'DUMMY'
        self.open_long = 1
        self.close_long = 2
        self.keep = 0
        self.strategy_name = strategy_name
    
    def plot(self, df=None, show_graph :bool = True, save_figure: bool = False, params=None, title: str = 'Title figure'):
        
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=('Price and EMA', 'RSI'))
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price', line=dict(color='blue')), row=1, col=1)
        buy_indices = df.index[df['actions'] == 1]
        sell_indices = df.index[df['actions'] == 2]
        fig.add_trace(go.Scatter(x=buy_indices, y=df['close'].loc[buy_indices], mode='markers', name='Buy', marker=dict(color='green', symbol='circle', size=10)), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_indices, y=df['close'].loc[sell_indices], mode='markers', name='Sell', marker=dict(color='red', symbol='circle', size=10)), row=1, col=1)
        fig.update_layout(template='plotly_dark', title=title, xaxis_title='Date', height=600)

        if show_graph:
            fig.show()

        if save_figure:
            if not os.path.exists('tmp'):
                os.makedirs('tmp')
            filename = f'figure_{self.name}.html'
            fig.write_html(os.path.join('tmp', filename))
            filename = f'figure_{self.name}.png'
            fig.write_image(os.path.join('tmp', filename))

    def eval(self, df=None, params=params_default):

        random_1  = params
        if isinstance(random_1, list):
            random_2 = 0.4 - random_1[0]
        else:
            random_2 = 0.4 - random_1

        random_1 = 0.2
        random_2 = 0.2
        df2 = df.copy()
        probabilities = [0.6, 0.2, 0.2]

        df['actions'] = np.random.choice([0,1,2], size=len(df2), p=probabilities)
        df['actions'] = remove_noise_trading(actions=df['actions'])

        return df
    
    def objective_function(self, params=params_default, df=None):
        
        result_df = self.eval(df=df.copy(), params=params)
        
        back_testing = GenericBacktesting(
            df=result_df,
            skip=True,
            initial_money=2000.0,
            commission=0.02,
            plot_result=False,
            path_save_result=".",
            print_stacks=False
        )
        return_data, _ = back_testing.calculate_bk()
        
        log.info(f'Strategy: {self.name} RETURN: {return_data} PARAMS: {params}')
        # Minimize the negative return to maximize the return
        return -return_data
    
    def optimize(self, params: list = params_default, initial_guess: list = params_init, df=None, method: str = "Nelder-Mead"):
        threshold_bounds = params
        result = minimize(self.objective_function, initial_guess, bounds=threshold_bounds, args=(df,), method=method)
        best_parameters = result.x
        best_return = -result.fun
        return best_return, best_parameters
    
    def experiment(self, df=None, params=params_default, initial_guess=params_init):
        methods_list = [
            # 'Nelder-Mead',
            'Powell',
            # 'CG',
            # 'L-BFGS-B',
            # 'COBYLA',
            # 'trust-constr'
        ]
        results_methods = {}
        results_method_list = []
        result_method_name = []
        
        for method in methods_list:
            print(f"Method: {method}")
            best_return, best_parameters = self.optimize(params=params, initial_guess=initial_guess, df=df, method=method)
            results_method_list.append(best_return)
            result_method_name.append(method)
            results_methods[method] = best_return, best_parameters
        
        optimize = results_method_list.index(max(results_method_list))
        method = result_method_name[optimize]
        best_return, best_parameters = results_methods[method]
        
        return method, best_return, best_parameters