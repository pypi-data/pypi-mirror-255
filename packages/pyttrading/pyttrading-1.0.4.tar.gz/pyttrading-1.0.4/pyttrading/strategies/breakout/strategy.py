from ...backtesting_custom.generic_backtesting import GenericBacktesting
from ...utils.pre_processing import remove_noise_trading
from scipy.optimize import minimize

# this strategy is breakout

class Strategy: 

    def __init__(self, df=None):
        
        pass         
    def eval(self,df=None, params= None):
        
        breakout_threshold = int(params)
        
        print(breakout_threshold)
        # Calcular el rango de ruptura (breakout range)
        df['breakout_range'] = df['height'] - df['low']

        df['actions'] = 0  # Inicializar todas las acciones como "mantener"
        df.loc[df['close'] > df['open'] + breakout_threshold * df['breakout_range'], 'actions'] = 1  # Señal de compra
        df.loc[df['close'] < df['open'] - breakout_threshold * df['breakout_range'], 'actions'] = 2  # Señal de venta

        # Eliminar señales consecutivas repetidas
        df['actions'] = df['actions'].mask(df['actions'].eq(df['actions'].shift()))
        # Reemplazar NaN por 0
        df['actions'] = df['actions'].fillna(0)

        df['actions'] = remove_noise_trading(actions=df['actions'])

        return df
    

    def objective_function(self,params, df=None):

        self.df = df
        result_df = self.eval(df=df, params=params)

        back_testing = GenericBacktesting(
            df=result_df,
            skip=True,
            initial_money=2000.0,
            commission=0.02,
            plot_result=False,
            path_save_result="."
        )

        return_data, _ = back_testing.calculate_bk()

        return -return_data
    
    def optimize(self, parms: list =  [(0.1, 1.3)], initial_guess: list = [0.02], df=None, method: str = 'Nelder-Mead'):

        threshold_bounds = parms

        # Realizar la optimización
        result = minimize(self.objective_function, initial_guess, bounds=threshold_bounds, args=(df), method=method)
        # Obtener el mejor valor de breakout_threshold y el mejor retorno
        best_breakout_threshold = result.x[0]
        best_return = -result.fun
        
        return best_return, best_breakout_threshold  
    

    def experiment(self, df=None, parms=[(0.1, 1.3)],initial_guess=[0.02]):
        
        methods_list = [
            'Nelder-Mead',
            'Powell',
            'CG',
            'BFGS',
            'L-BFGS-B',
            # 'TNC',
            'COBYLA',
            'SLSQP',
            'trust-constr',
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
            results_methods[method] = best_return, best_sma_threshold
            

        # get the max value of results_method_list
        optimize = results_method_list.index(max(results_method_list))
        method = result_method_name[optimize]
        best_return, best_sma_threshold = results_methods[method]
        
        return method, best_return, best_sma_threshold