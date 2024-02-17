from os import sep
import pandas as pd
import numpy as np
from collections import Counter
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan


def get_battery_matrix_hour(df_minute):
    y_list = []
    m_list = []
    d_list = []
    hour_list = []

    BATTERY_LEVEL_list = []
    CHARGING_STATUS_list = []
    MISSING_list = []

    y = list(df_minute.YEAR.unique())[0]
    m = list(df_minute.MONTH.unique())[0]
    d = list(df_minute.DAY.unique())[0]

    for hour in range(24):
        df_subset = df_minute[df_minute.HOUR == str(hour)]
        average_battery_level = np.nanmean(pd.to_numeric(df_subset['BATTERY_LEVEL'], errors='coerce'))

        pred_count = Counter(df_subset.CHARGING_STATUS)
        if 'true' in pred_count:
            CHARGING_STATUS = pred_count['true']
        else:
            CHARGING_STATUS = 0

        MISSING_num = 60 - pred_count['true'] - pred_count['false']

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
        hour_list.append(hour)

        BATTERY_LEVEL_list.append(average_battery_level)
        CHARGING_STATUS_list.append(CHARGING_STATUS)
        MISSING_list.append(MISSING_num)

    df_hour = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "HOUR": hour_list, "AVERAGE_BATTERY_LEVEL": BATTERY_LEVEL_list,
         "CHARGING_MINUTES": CHARGING_STATUS_list, "CHARGING_STATES_MISSING_MINUTES": MISSING_list})

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\activity_minute.csv")
    df_hour = get_battery_matrix_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
