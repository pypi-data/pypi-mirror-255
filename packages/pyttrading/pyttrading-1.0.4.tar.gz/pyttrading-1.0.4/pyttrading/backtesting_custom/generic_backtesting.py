import json
from backtesting import Backtest, Strategy
import os
import json
from backtesting import Backtest, Strategy
from pyttrading.utils.logs import log
import pandas as pd


class DataBacktestingLong(Strategy):

    def init(self):

        self.buy_signal = False
        self.sell_signal = False

    def next(self):
        last_action = self.data.actions[-1] 
        if last_action == 1:
            self.position.close()
            self.buy()
        elif last_action == 2:
            self.position.close()
            self.sell()

class DataBacktestingShort(Strategy):

    def init(self):

        self.buy_signal = False
        self.sell_signal = False

    def next(self):
        last_action = self.data.actions[-1]
        if last_action == 2:
            self.position.close()
            self.sell()
        elif last_action == 1:
            self.position.close()
            self.buy()


class GenericBacktesting:


    def __init__(self, df, skip=True, initial_money=2000.0, commission=0.02, plot_result=True, path_save_result=".", print_stacks :bool=False, bk_type :str = 'long', save_bk_figure :bool = False):

        df.index = pd.to_datetime(df.index)

        self.df = df
        self.skip = skip
        self.initial_money = initial_money
        self.commission = commission
        self.plot_result = plot_result
        self.path_save_result = path_save_result
        self.print_stacks = print_stacks
        self.bk_type = bk_type

        self.save_bk_figure = save_bk_figure

    def rename_columns(self):

        self.df_bk = self.df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })

    def calculate_bk(self):

        self.rename_columns()
        self.df_bk_pandas = pd.DataFrame(self.df_bk)
        
        if self.bk_type == 'long':
            strategy_use = DataBacktestingLong
        elif self.bk_type == 'short':
            strategy_use = DataBacktestingShort
        else: 
            raise ValueError('bk_type not valid, need to do long or short')


        bt = Backtest(
                    data=self.df_bk_pandas, 
                    strategy=strategy_use,
                    cash=self.initial_money,
                    commission=self.commission,
                    exclusive_orders=True
                )

        stats = bt.run()
        stats_json = json.loads(stats.to_json())
        if self.print_stacks:
            print(stats)

        if self.save_bk_figure:
            graph_tmp = f'tmp/backtest_{self.bk_type}.html'
            if os.path.exists(graph_tmp):
                os.remove(graph_tmp)

            bt.plot(filename=graph_tmp, open_browser=False)

        profit_factor = stats['Equity Final [$]'] / self.initial_money

        return profit_factor, stats_json
    


def get_backtesting(df=None, initial_money :float = 2000.0, bk_type :str = 'long'):

    back_testing = GenericBacktesting(
                    df=df,
                    skip=True,
                    initial_money=initial_money,
                    commission=0.02,
                    plot_result=False,
                    path_save_result='tmp',
                    print_stacks=False,
                    bk_type=bk_type
                )

    return_data, stats_json = back_testing.calculate_bk()
    
    return return_data, stats_json 


