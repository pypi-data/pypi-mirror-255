from os import sep
import pandas as pd
import numpy as np
from collections import Counter
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan

def get_wifi_matrix_hour(df_minute):
    y_list = []
    m_list = []
    d_list = []
    hour_list = []

    WIFI_ON_list = []
    MISSING_list = []

    y = list(df_minute.YEAR.unique())[0]
    m = list(df_minute.MONTH.unique())[0]
    d = list(df_minute.DAY.unique())[0]

    for hour in range(24):
        df_subset = df_minute[df_minute.HOUR == str(hour)]
        pred_count = Counter(df_subset.WIFI_STATUS)
        if "True" in pred_count:
            WIFI_ON = pred_count["True"]
        else:
            WIFI_ON = 0

        MISSING_num = 60 - WIFI_ON

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
        hour_list.append(hour)

        WIFI_ON_list.append(WIFI_ON)
        MISSING_list.append(MISSING_num)

    df_hour = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "HOUR": hour_list, "WIFI_ON": WIFI_ON_list, "MISSING": MISSING_list})

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\activity_minute.csv")
    df_hour = get_wifi_matrix_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
