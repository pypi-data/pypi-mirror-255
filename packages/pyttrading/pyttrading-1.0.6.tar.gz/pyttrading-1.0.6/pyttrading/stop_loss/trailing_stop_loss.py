from scipy.optimize import minimize
from pyttrading.backtesting_custom.generic_backtesting import get_backtesting


class TrailingStopLoss:

    default_params = [0.05, 0.05]


    def __init__(self, init_capital: float = 2000, column_action_name: str = "actions", sell_value: int = 2, data=None):
        self.init_capital = init_capital
        self.column_action_name = column_action_name
        self.sell_value = sell_value
        self.data = data

    def stop_loss(self, params: list = default_params):
        trailing_stop_price, trailing_stop_pct = params

        price_buy = None
        qty_buy = None
        capital = self.init_capital
        trailing_stop_price = None

        dff = self.data.copy()
        for i, action in enumerate(dff["actions"]):
            if action == 1:
                price_buy = dff["close"].iloc[i]
                price_buy = float(price_buy)
                capital = float(capital)
                trailing_stop_price = price_buy

                qty_buy = capital / price_buy

            if qty_buy and trailing_stop_price:
                current_capital = qty_buy * dff["close"].iloc[i]
                current_trailing_stop_price = price_buy * (1 - trailing_stop_pct)

                if dff["close"].iloc[i] < current_trailing_stop_price:
                    dff.loc[dff.index[i], self.column_action_name] = self.sell_value

                    qty_buy = None
                    trailing_stop_price = None

                    try:
                        filtered_df = dff.iloc[i + 1:]
                        idx = filtered_df.index[filtered_df["actions"] == 2][0]
                        dff.at[idx, 'actions'] = 0
                    except:
                        pass

            if trailing_stop_price and current_trailing_stop_price > trailing_stop_price:
                trailing_stop_price = current_trailing_stop_price

        return dff

    def objective_function(self, params: list = default_params):
        df_stop_loss = self.stop_loss(params=params)
        return_data, _ = get_backtesting(df=df_stop_loss)

        print(f"SEARCH THE BEST STOP LOSS SL TRAILING: {params} RETURN: {return_data}")
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

