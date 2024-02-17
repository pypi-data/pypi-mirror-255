from os import sep
import pandas as pd
import numpy as np
from collections import Counter
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan


def get_swan_matrix_hour(df_minute):
    y_list = []
    m_list = []
    d_list = []
    hour_list = []
    swan_prediction_num_list = []
    swan_wear_pred_list = []
    swan_nwear_pred_list = []
    swan_sleep_pred_list = []
    swan_indecisive_pred_list = []

    y = list(df_minute.YEAR.unique())[0]
    m = list(df_minute.MONTH.unique())[0]
    d = list(df_minute.DAY.unique())[0]

    for hour in range(24):
        df_subset = df_minute[df_minute.HOUR == str(hour)]

        swan_sample_num_hour = df_subset.SWAN_PREDICTION_NUM.sum()
        if swan_sample_num_hour == 0:
            swan_wear_pred = NAN
            swan_nwear_pred = NAN
            swan_sleep_pred = NAN
            swan_indecisive_pred = NAN
        else:
            pred_count = Counter(df_subset.SWAN_PREDICTION)
            if "Wear" in pred_count:
                swan_wear_pred = pred_count["Wear"]
            else:
                swan_wear_pred = 0

            if "Nonwear" in pred_count:
                swan_nwear_pred = pred_count["Nonwear"]
            else:
                swan_nwear_pred = 0

            if "Sleep" in pred_count:
                swan_sleep_pred = pred_count["Sleep"]
            else:
                swan_sleep_pred = 0

            if "INDECISIVE" in pred_count:
                swan_indecisive_pred = pred_count["INDECISIVE"]
            else:
                swan_indecisive_pred = 0

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
        hour_list.append(hour)

        swan_prediction_num_list.append(swan_sample_num_hour)
        swan_wear_pred_list.append(swan_wear_pred)
        swan_nwear_pred_list.append(swan_nwear_pred)
        swan_sleep_pred_list.append(swan_sleep_pred)
        swan_indecisive_pred_list.append(swan_indecisive_pred)

    df_hour = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "HOUR": hour_list,
         "SWAN_PREDICTION_NUM": swan_prediction_num_list,
         "WEAR_MINUTES": swan_wear_pred_list, "NWEAR_MINUTES": swan_nwear_pred_list,
         "SLEEP_MINUTES": swan_sleep_pred_list, "INDECISIVE_MINUTES": swan_indecisive_pred_list})

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\swan_minute.csv")
    df_hour = get_swan_matrix_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
