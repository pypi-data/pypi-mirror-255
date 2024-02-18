import numpy as np



def inflection_points(df, threshold=0.5, column_name='rsi_s', result_column :str = 'actions'):
    
    df_inf = df.copy()

    df_inf['date'] = df_inf.index

    df_inf.reset_index(drop=True, inplace=True)

    differences = np.diff(df_inf[column_name])
    inflection_points = np.where(abs(differences) > threshold)[0]
    df_inf['inf_point'] = 0
    df_inf.loc[inflection_points, 'inf_point'] = 1 

    df_inf[result_column] = 0
    
    for point in inflection_points:
        window = 10
        subset = df_inf[column_name].iloc[point:point + window]
        if len(subset) > 1:
            if subset.iloc[0] < subset.iloc[-1]:
                df_inf.at[point, result_column] = 1  # Increasing
            elif subset.iloc[0] > subset.iloc[-1]:
                df_inf.at[point, result_column] = 2  # Decreasing
            else:
                df_inf.at[point, result_column] = 0
        else:
            df_inf.at[point, result_column] = 0


    df.reset_index(drop=True, inplace=True)  # Si no tienen el mismo índice
    df_inf.reset_index(drop=True, inplace=True)
    df['actions'] = df_inf['actions']

    df.index = df_inf['date']
    
    return df