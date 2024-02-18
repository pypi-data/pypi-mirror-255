from scipy.optimize import minimize
from ..backtesting_custom.generic_backtesting import get_backtesting
import plotly.graph_objs as go
from scipy.optimize import minimize
from pyttrading.backtesting_custom.generic_backtesting import get_backtesting

def stop_loss_simple(data=None, stop_loss=-0.05, init_capital :float = 2000, column_action_name :str = 'actions', sell_value :int = 2):
    
    price_buy = None
    qty_buy = None
    capital = init_capital

    dff = data.copy()
    for i, action in enumerate(dff['actions']):
        if action == 1:
            # price_buy = dff['close'][i]
            price_buy = dff['close'].iloc[i]
            price_buy = float(price_buy)
            capital = float(capital)

            qty_buy = capital/price_buy

        if qty_buy:
            # current_capital = qty_buy * dff['close'][i]
            current_capital = qty_buy * dff['close'].iloc[i]

            equity = (current_capital-capital)/capital

            if equity < stop_loss:
                dff.loc[dff.index[i], column_action_name] = sell_value

                qty_buy = None
                
                try:
                    filtered_df = dff.iloc[i+1:]
                    idx = filtered_df.index[filtered_df["actions"] == 2][0]
                    dff.at[idx, 'actions'] = 0
                except:
                    pass
        
    return dff


# Optimization Stop Loss

def objective_function(stop_loss, df_original, init_capital=2000, sell_value=2):

    df_stop_loss = stop_loss_simple(data=df_original, stop_loss=stop_loss, init_capital=init_capital, sell_value=sell_value)
    return_data, _ = get_backtesting(df=df_stop_loss)

    print(f"SEARCH THE BEST STOP LOSS SL: {stop_loss} RETURN: {return_data}")
    return -return_data

def optimize_stop_loss_simple(df_original, st_from=0.01, st_to=10):

    #method='Nelder-Mead'
    method='Powell'
    result = minimize(objective_function, x0=0, args=(df_original,), bounds=[(st_from, st_to)], method=method, options={'maxiter': 1000})
    best_stop_loss = result.x[0]
    best_return = -result.fun
    
    return best_stop_loss, best_return




class TrailingStopLoss:

    default_params = [0.05, 0.05]

    def __init__(self, init_capital: float = 2000, column_action_name: str = "actions", sell_value: int = 2, data=None):
        self.init_capital = init_capital
        self.column_action_name = column_action_name
        self.sell_value = sell_value
        self.data = data

    def stop_loss(self, params: list = default_params):
        stop_loss_constant, stop_loss_trailing = params

        qty_buy = None
        capital = self.init_capital
        start_capital = self.init_capital

        dff = self.data.copy()
        for i, action in enumerate(dff["actions"]):
            if i > 1:

                price_current = dff["close"].iloc[i]
                price_last = dff["close"].iloc[i-1]

                if action == 1:
                    qty_buy = capital / price_current

                if qty_buy:
                    capital_current = price_current * qty_buy
                    if price_current  >= price_last and capital_current >= start_capital:
                        capital = capital_current
                        qty_buy = capital / price_current
                    else:
                        equity_constant = (capital_current-start_capital)/start_capital

                        activate_stop_loss = False
                        if equity_constant < stop_loss_constant:
                            activate_stop_loss = True

                        equity = (capital_current-capital)/capital

                        if equity < stop_loss_trailing:
                            activate_stop_loss = True

                        if activate_stop_loss:
                            start_capital = capital
                            dff.loc[dff.index[i], self.column_action_name] = self.sell_value
                            qty_buy = None
                            try:
                                filtered_df = dff.iloc[i + 1:]
                                idx = filtered_df.index[filtered_df["actions"] == 2][0]
                                dff.at[idx, 'actions'] = 0
                            except:
                                pass

        return dff

    def objective_function(self, params: list = default_params):
        df_stop_loss = self.stop_loss(params=params)
        return_data, _ = get_backtesting(df=df_stop_loss)

        return -return_data

    def optimize(self, params: list = default_params):

        params_init = []
        for param in params:
            param_low = param[0]
            params_init.append(param_low)

        method = "Powell"
        result = minimize(self.objective_function,x0=params_init,  bounds=params, method=method, options={"maxiter": 1000})

        best_parameters = result.x
        best_return = -result.fun

        return best_return, best_parameters




class ConstantStopLoss:

    default_params = [0.05]


    def __init__(self, init_capital: float = 2000, column_action_name: str = "actions", sell_value: int = 2, data=None):
        
        self.init_capital = init_capital
        self.column_action_name = column_action_name
        self.sell_value = sell_value
        self.data = data

    def stop_loss(self, params: list = default_params):

        stop_loss = params
        price_buy = None
        qty_buy = None
        capital = self.init_capital

        dff = self.data.copy()
        for i, action in enumerate(dff['actions']):
            if action == 1:
                price_buy = dff['close'].iloc[i]
                price_buy = float(price_buy)
                capital = float(capital)

                qty_buy = capital/price_buy

            if qty_buy:
                current_capital = qty_buy * dff['close'].iloc[i]

                equity = (current_capital-capital)/capital

                # if equity < stop_loss:
                if any(equity < stop_loss):
                    dff.loc[dff.index[i], self.column_action_name] = self.sell_value
                    qty_buy = None
                    
                    try:
                        filtered_df = dff.iloc[i+1:]
                        idx = filtered_df.index[filtered_df["actions"] == 2][0]
                        dff.at[idx, 'actions'] = 0
                    except:
                        pass
            
        return dff

    def objective_function(self, params = default_params):

        df_stop_loss = self.stop_loss( params=params)
        return_data, _ = get_backtesting(df=df_stop_loss)

        print(f"SEARCH THE BEST STOP LOSS SL: {params} RETURN: {return_data}")
        return -return_data

    def optimize(self, params: list = default_params):

        params_init = []
        for param in params:
            param_low = param[0]
            params_init.append(param_low)

        method = "Powell"
        result = minimize(self.objective_function,x0=params_init,  bounds=params, method=method, options={"maxiter": 1000})

        best_parameters = result.x
        best_return = -result.fun

        return best_return, best_parameters