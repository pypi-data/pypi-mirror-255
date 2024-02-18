import numpy as np
from ta.momentum import RSIIndicator
from pyttrading.utils.logs import log
from scipy.optimize import minimize
import plotly.graph_objects as go
# import talib
import numpy as np
from plotly.subplots import make_subplots
import os
from pyttrading.utils.inflection_points import inflection_points
from pyttrading.utils.pre_processing import remove_noise_trading
from ...backtesting_custom.generic_backtesting import GenericBacktesting

params_default = [(20, 50), (30, 70), (0.1, 5)]

params_init = []
for param in params_default:
    param_low = param[0]
    params_init.append(param_low)

class Strategy: 

    def __init__(self, df=None, strategy_name :str = "StrategyName", bk_initial_money :float = 2000.0, bk_commission :float = 0.02):
        self.name = 'RSI'
        self.open_long = 1
        self.close_long = 2
        self.keep = 0
        self.strategy_name = strategy_name,

        self.bk_initial_money=bk_initial_money
        self.bk_commission=bk_commission
    
    def plot(self, df=None, show_graph :bool = True, save_figure: bool = False, params=None, title: str = 'Title figure'):
        
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.05, row_heights=[0.7, 0.3], subplot_titles=('Price and EMA', 'RSI'))
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price', line=dict(color='blue')), row=1, col=1)
        buy_indices = df.index[df['actions'] == 1]
        sell_indices = df.index[df['actions'] == 2]
        fig.add_trace(go.Scatter(x=buy_indices, y=df['close'].loc[buy_indices], mode='markers', name='Buy', marker=dict(color='green', symbol='circle', size=10)), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_indices, y=df['close'].loc[sell_indices], mode='markers', name='Sell', marker=dict(color='red', symbol='circle', size=10)), row=1, col=1)
        
        fig.add_trace(go.Scatter(x=df.index, y=df['rsi'], mode='lines', name='RSI', line=dict(color='red', width=1)), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['rsi_s'], mode='lines', name='RSI_S', line=dict(color='yellow', width=1)), row=2, col=1)

        fig.add_trace(go.Scatter(x=buy_indices, y=df['rsi'].loc[buy_indices], mode='markers', name='Buy', marker=dict(color='green', symbol='circle', size=10)), row=2, col=1)
        fig.add_trace(go.Scatter(x=sell_indices, y=df['rsi_s'].loc[sell_indices], mode='markers', name='Sell', marker=dict(color='red', symbol='circle', size=10)), row=2, col=1)

        fig.add_trace(go.Scatter(x=df.index, y=[params[0]] * len(df), mode='lines', name='Buy Threshold', line=dict(color='green', width=1, dash='dash')), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=[params[1]] * len(df), mode='lines', name='Sell Threshold', line=dict(color='blue', width=1, dash='dash')), row=2, col=1)

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
        df = df.copy()
        rsi_length, rsi_smoothed, constant_inflection = params
        rsi_indicator = RSIIndicator(df['close'], window=rsi_length)
        df['rsi'] = rsi_indicator.rsi()
        # df['rsi_s'] = talib.SMA(df['rsi'], timeperiod=int(rsi_smoothed)) # TODO 
        df['rsi_s'] = df['rsi'].ewm(span=int(rsi_smoothed), adjust=False).mean()

        df = inflection_points(df=df, threshold=constant_inflection, column_name='rsi_s')
        df['actions'] = remove_noise_trading(actions=df['actions'])
        
        return df
    
    def objective_function(self, params=params_default, df=None):
        
        # Apply the strategy with the current parameters
        
        result_df = self.eval(df=df.copy(), params=params)
        
        back_testing = GenericBacktesting(
            df=result_df,
            skip=True,
            initial_money=self.bk_initial_money,
            commission=self.bk_commission,
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

        log.info(f"Start Experiment, Strategy: {self.name} Name: {self.strategy_name}")

        methods_list = [
            # 'Nelder-Mead',
            # 'Powell',
            # 'CG',
            # 'L-BFGS-B',
            'COBYLA',
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

# strategy_data = Strategy(df=data)
# method, best_return, best_parameters = strategy_data.experiment(df=data)
# print(f"Best Return: {best_return}")
# print(f"Best params: {best_parameters}")
# print(f"Method: {method}")
# # best_parameters = params_init
# data2 = strategy_data.eval(df=data, params=best_parameters)
# data2.head()
# strategy_data.plot(df=data2, save_figure=True, params=best_parameters, title=f"{best_parameters}")