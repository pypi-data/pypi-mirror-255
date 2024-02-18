
import pandas as pd
import matplotlib.pyplot as plt
import os


def df_actions_market_value(df=None, capital :float = 2000, save_figure :bool = False, show_figure :bool = False, fig_path = 'tmp/market_value_plot.png', title='Strategy Market' ):

    df['market_value'] = 0
    price_buy = None
    price_buy = None
    qty_buy = None

    for i, action in enumerate(df['actions']):

        if action == 1:  # Compra
            price_buy =  df['close'][i] #TODO verify
            # price_buy = df['close'].iloc[i]

            qty_buy = capital/price_buy
        elif action == 2 and price_buy:  # Venta
            price_buy = None
            qty_buy = None
        
        if qty_buy:
            capital = qty_buy * df['close'][i] #TODO verify
            # capital = qty_buy * df['close'].iloc[i]


        df['market_value'][i] = capital
        # df.at[i, 'market_value'] = capital 

    if os.path.exists(fig_path):
        os.remove(fig_path)

    if save_figure:
        plt.figure(figsize=(10, 6))
        plt.plot(df.index, df['market_value'], color='b')
        plt.title(title)
        plt.xlabel('Date')
        plt.ylabel('Market Value')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(fig_path)
        if show_figure:
            plt.show()

    return df
