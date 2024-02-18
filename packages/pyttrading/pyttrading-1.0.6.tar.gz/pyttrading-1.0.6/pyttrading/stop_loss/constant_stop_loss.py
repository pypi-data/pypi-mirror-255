from scipy.optimize import minimize
from pyttrading.backtesting_custom.generic_backtesting import get_backtesting

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



# sl = ConstantStopLoss(data=data2,init_capital=2000)
# # best_return, best_parameters_sl = sl.optimize(params=[(-0.1, -0.01)])

# best_parameters_sl = [-0.05]
# stop_loss_df =  sl.stop_loss(params=best_parameters_sl)
# stop_loss_simple = df_actions_market_value(df=stop_loss_df, capital=2000, save_figure=False)
# market = df_actions_market_value(df=data2, capital=2000, save_figure=False)


# import plotly.graph_objs as go

# # Data traces
# trace_original = go.Scatter(
#     x=market.index,
#     y=market['market_value'],
#     mode='lines',
#     name='Original'
# )

# trace_stop_loss = go.Scatter(
#     x=stop_loss_simple.index,
#     y=stop_loss_simple['market_value'],
#     mode='lines',
#     name='SL'
# )

# # Create layout with 'plotly_dark' template
# layout = go.Layout(
#     title='Comparación del Valor de Mercado con y sin Stop Loss',
#     xaxis=dict(title='Fecha'),
#     yaxis=dict(title='Valor de Mercado'),
#     template='plotly_dark'
# )

# # Combine data traces and layout, then plot
# fig = go.Figure(data=[trace_original, trace_stop_loss], layout=layout)
# fig.show()
