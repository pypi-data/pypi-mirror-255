import pandas as pd
import numpy as np
from collections import Counter

NAN = np.nan


def get_swan_matrix_day(df_hour):
    y_list = []
    m_list = []
    d_list = []
    swan_prediction_num_list = []
    swan_wear_pred_list = []
    swan_nwear_pred_list = []
    swan_sleep_pred_list = []
    swan_indecisive_pred_list = []

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    swan_sample_num_hour = df_hour.SWAN_PREDICTION_NUM.sum()
    if swan_sample_num_hour == 0:
        swan_wear_pred = NAN
        swan_nwear_pred = NAN
        swan_sleep_pred = NAN
        swan_indecisive_pred = NAN
    else:
        swan_wear_pred = df_hour.WEAR_MINUTES.sum()
        swan_nwear_pred = df_hour.NWEAR_MINUTES.sum()
        swan_sleep_pred = df_hour.SLEEP_MINUTES.sum()
        swan_indecisive_pred = df_hour.INDECISIVE_MINUTES.sum()

    y_list.append(y)
    m_list.append(m)
    d_list.append(d)

    swan_prediction_num_list.append(swan_sample_num_hour)
    swan_wear_pred_list.append(swan_wear_pred)
    swan_nwear_pred_list.append(swan_nwear_pred)
    swan_sleep_pred_list.append(swan_sleep_pred)
    swan_indecisive_pred_list.append(swan_indecisive_pred)

    df_day = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "SWAN_PREDICTION_NUM": swan_prediction_num_list,
         "WEAR_MINUTES": swan_wear_pred_list, "NWEAR_MINUTES": swan_nwear_pred_list,
         "SLEEP_MINUTES": swan_sleep_pred_list, "INDECISIVE_MINUTES": swan_indecisive_pred_list})

    return df_day


if __name__ == "__main__":
    df_hour = pd.read_csv(
        r"C:\Users\Jixin\Downloads\swan_minute.csv")
    df_day = get_swan_matrix_day(df_hour)
    print(df_day)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
