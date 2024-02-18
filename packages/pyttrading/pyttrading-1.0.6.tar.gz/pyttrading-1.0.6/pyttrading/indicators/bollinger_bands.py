import numpy as np
from numba import njit

def bollinger_bands(bar_data, lookback=20, num_std_dev=2):

    @njit  # Enable Numba JIT.
    def vec_bollinger(values, lookback, num_std_dev):
        n = len(values)
        upper_band = np.array([np.nan for _ in range(n)])
        lower_band = np.array([np.nan for _ in range(n)])
        middle_band = np.array([np.nan for _ in range(n)])

        for i in range(lookback - 1, n):
            window = values[i - lookback + 1:i + 1]
            mean = np.mean(window)
            std = np.std(window)

            middle_band[i] = mean
            upper_band[i] = mean + (std * num_std_dev)
            lower_band[i] = mean - (std * num_std_dev)

        return upper_band, middle_band, lower_band

    return vec_bollinger(bar_data.close, lookback, num_std_dev)


import numpy as np
from numba import njit

def bands_middle(bar_data, lookback=20, num_std_dev=2):

    @njit
    def vec_bollinger(values, lookback, num_std_dev):
        n = len(values)
        middle_band = np.array([np.nan for _ in range(n)])

        for i in range(lookback - 1, n):
            window = values[i - lookback + 1:i + 1]
            mean = np.mean(window)
            middle_band[i] = mean

        return middle_band

    return vec_bollinger(bar_data.close, lookback, num_std_dev)


def bands_upper(bar_data, lookback=20, num_std_dev=2):

    @njit
    def vec_bollinger(values, lookback, num_std_dev):
        n = len(values)
        upper_band = np.array([np.nan for _ in range(n)])

        for i in range(lookback - 1, n):
            window = values[i - lookback + 1:i + 1]
            mean = np.mean(window)
            std = np.std(window)

            upper_band[i] = mean + (std * num_std_dev)

        return upper_band

    return vec_bollinger(bar_data.close, lookback, num_std_dev)


def bands_lower(bar_data, lookback=20, num_std_dev=2):

    @njit
    def vec_bollinger(values, lookback, num_std_dev):
        n = len(values)
        lower_band = np.array([np.nan for _ in range(n)])
        for i in range(lookback - 1, n):
            window = values[i - lookback + 1:i + 1]
            mean = np.mean(window)
            std = np.std(window)

            lower_band[i] = mean - (std * num_std_dev)

        return lower_band

    return vec_bollinger(bar_data.close, lookback, num_std_dev)
