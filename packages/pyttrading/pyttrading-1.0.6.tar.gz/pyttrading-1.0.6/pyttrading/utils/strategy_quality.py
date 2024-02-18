
def strategy_quality(config, data):

    if not config.use_quality_model:
        print(" [ ⚠️ MODEL QUALITY]: Disabled")
        return True

    metrics = data.metrics
    save_mode = False
    trades = metrics.get('Trades')
    profit_factor = metrics.get('ProfitFactor')

    print(f" [ 🟦 MODEL QUALITY]: TRADES: {trades} >= {config.min_trades}")
    print(f" [ 🟦 MODEL QUALITY]: PROFIT_FACTOR: {profit_factor} >= {config.min_profit_factor}")
    print(f" [ 🟦 MODEL QUALITY]: BEST_RETURN: {metrics.get('best_return_sl') } >= {metrics.get('best_return')}")

    if trades >= config.min_trades and profit_factor >= config.min_profit_factor:

        if metrics.get('best_return_sl') > metrics.get('best_return'):
            save_mode = True

    return save_mode