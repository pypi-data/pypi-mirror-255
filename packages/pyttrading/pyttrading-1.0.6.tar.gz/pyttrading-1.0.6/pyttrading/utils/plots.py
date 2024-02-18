
import matplotlib.pyplot as plt
import plotly.graph_objs as go


def generate_market_value_plot(df_action_market, stop_loss_constant, stop_loss_trailing):

    # Data traces
    trace_original = go.Scatter(
        x=df_action_market.index,
        y=df_action_market['market_value'],
        mode='lines',
        name='Original'
    )

    sl_constant = go.Scatter(
        x=stop_loss_constant.index,
        y=stop_loss_constant['market_value'],
        mode='lines',
        name='SL'
    )

    trace_trailing = go.Scatter(
        x=stop_loss_trailing.index,
        y=stop_loss_trailing['market_value'],
        mode='lines',
        name='SL Trailing'
    )

    # Create layout with 'plotly_dark' template
    layout = go.Layout(
        title='Operation Values',
        xaxis=dict(title='Fecha'),
        yaxis=dict(title='Valor de Mercado'),
        template='plotly_dark'
    )

    # Combine data traces and layout, then plot
    fig = go.Figure(data=[trace_original, sl_constant,trace_trailing], layout=layout)

    fig.write_html('tmp/market_value_plot.html')

    # fig.show()

    return 'tmp/market_value_plot.png'

def generate_actions_plot(df_action_market):
    
    actions_1 = df_action_market[df_action_market['actions'] == 1]
    actions_2 = df_action_market[df_action_market['actions'] == 2]
    actions_2_sl = df_action_market[df_action_market['actions'] == 2]

    plt.figure(figsize=(10, 6))
    plt.scatter(actions_1.index, actions_1['open'], color='green', label='BUY')
    plt.scatter(actions_2.index, actions_2['open'], color='red', label='SELL')
    plt.scatter(actions_2_sl.index, actions_2_sl['open'], color='orange', label='StopLoss')
    plt.plot(df_action_market.index, df_action_market['close'], label='Close', linestyle='-')
    plt.xlabel('Index')
    plt.ylabel('Values')
    plt.title('Scatter Plot for Actions 1 and 2 with Closing Line')
    plt.legend()
    plt.savefig('tmp/actions_plot.png')
    plt.close()  # Close the figure to free memory

    return 'tmp/actions_plot.png'