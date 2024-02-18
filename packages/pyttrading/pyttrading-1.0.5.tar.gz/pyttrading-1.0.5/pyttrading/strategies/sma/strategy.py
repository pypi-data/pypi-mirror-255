from ...backtesting_custom.generic_backtesting import GenericBacktesting
from ...utils.pre_processing import remove_noise_trading
from scipy.optimize import minimize
from ta.trend import SMAIndicator
from pyttrading.utils.logs import log
from scipy.optimize import minimize
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

params_default = [(5, 30), (10, 100)]

params_init = []
for param in params_default:
    param_low = param[0]
    params_init.append(param_low)

class Strategy: 

    def __init__(self, df=None, strategy_name :str = "StrategyName", bk_initial_money :float = 2000.0, bk_commission :float = 0.02):
        self.name = 'SMA'
        self.open_long = 1
        self.close_long = 2
        self.keep = 0
        self.strategy_name = strategy_name
        self.bk_initial_money = bk_initial_money
        self.bk_commission = bk_commission
    
    def plot(self, df=None, show_graph :bool = True, save_figure: bool = False, title :str = 'Title', params=None):
        
        fig = make_subplots(rows=1, cols=1, shared_xaxes=True, vertical_spacing=0.05, subplot_titles=('Price and EMA', 'RSI'))
        fig.add_trace(go.Scatter(x=df.index, y=df['close'], mode='lines', name='Close Price', line=dict(color='blue')), row=1, col=1)
        buy_indices = df.index[df['actions'] == 1]
        sell_indices = df.index[df['actions'] == 2]
        fig.add_trace(go.Scatter(x=buy_indices, y=df['close'].loc[buy_indices], mode='markers', name='Buy', marker=dict(color='green', symbol='circle', size=10)), row=1, col=1)
        fig.add_trace(go.Scatter(x=sell_indices, y=df['close'].loc[sell_indices], mode='markers', name='Sell', marker=dict(color='red', symbol='circle', size=10)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['fast_ma'], mode='lines', name='fast_ma', line=dict(color='red', width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['slow_ma'], mode='lines', name='slow_ma', line=dict(color='yellow', width=1)), row=1, col=1)

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

    def eval(self, df=None, params=[10, 30]):
        
        fast_ma_period, slow_ma_period = params
        
        df['fast_ma'] = SMAIndicator(df['close'], int(fast_ma_period), True).sma_indicator()
        df['slow_ma']  = SMAIndicator(df['close'], int(slow_ma_period), True).sma_indicator()
        df['actions'] = self.keep
        df.loc[df['fast_ma'] > df['slow_ma'], 'actions'] = self.open_long
        df.loc[df['fast_ma'] < df['slow_ma'], 'actions'] = self.close_long
        df['actions'] = df['actions'].mask(df['actions'].eq(df['actions'].shift()))
        df['actions'] = df['actions'].fillna(0)
        df['actions'] = remove_noise_trading(actions=df['actions'])
        
        return df
    
    def objective_function(self, params=params_init, df=None):
        
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
    
    def optimize(self, parms: list =params_default, initial_guess: list = [10, 20], df=None, method: str = "Nelder-Mead"):
        
        threshold_bounds = parms
        
        result = minimize(self.objective_function, initial_guess, bounds=threshold_bounds, args=(df), method=method)
        
        best_breakout_threshold = result
        
        best_return = -result.fun

        return best_return, best_breakout_threshold
    


    def experiment(self, df=None, parms=params_default,initial_guess=params_init):
        
        log.info(f"Start Experiment, Strategy: {self.name} Name: {self.strategy_name}")
        methods_list = [
            # 'Nelder-Mead',
            'Powell',
            # 'CG',
            # 'L-BFGS-B',
            # 'COBYLA',
            # 'trust-constr',
            # 'BFGS',
            # 'TNC',
            # 'SLSQP',
            # 'dogleg',
            # 'trust-ncg',
            # 'trust-exact',
            # 'trust-krylov'
        ]
        
        results_methods = {}
        results_method_list = []
        result_method_name = []
        
        for method in methods_list:
            print(f"Method: {method}")
    
            best_return, best_sma_threshold = self.optimize(
                parms=parms, 
                initial_guess=initial_guess,
                df=df, 
                method=method
            )
    
            results_method_list.append(best_return)
            result_method_name.append(method)
    
            results_methods[method] = best_return, best_sma_threshold.x
            

        # get the max value of results_method_list
        optimize = results_method_list.index(max(results_method_list))
        method = result_method_name[optimize]
        best_return, best_sma_threshold = results_methods[method]
        
        return method, best_return, best_sma_threshold