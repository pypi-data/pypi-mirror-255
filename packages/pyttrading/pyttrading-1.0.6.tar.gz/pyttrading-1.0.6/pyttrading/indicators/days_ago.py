import numpy as np


def _add_days_ago2(bar_data, days):
    # Asegurarse de que hay suficientes datos para el desplazamiento
    if len(bar_data.close) < days:
        raise ValueError("No hay suficientes datos para el desplazamiento solicitado")

    # Crear el atributo para 'days' días atrás
    shifted_close = np.roll(bar_data.close, days)
    # Establecer los primeros 'days' valores como NaN
    shifted_close[:days] = np.nan

    return shifted_close


def _add_days_ago(data, days):
    for i in range(1, days + 1):
        data[f'd{i}'] = data['close'].shift(i)
    data.dropna(inplace=True)
    data['date'] = data.index
    return data

def days_ago(data, days):
    days = _add_days_ago2(data, days)
    return days

