from os import sep
import pandas as pd
import numpy as np
from collections import Counter
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan

def get_battery_matrix_day(df_hour):
    y_list = []
    m_list = []
    d_list = []

    BATTERY_LEVEL_list = []
    CHARGING_STATUS_list = []
    MISSING_list = []

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    average_battery_level = df_hour.AVERAGE_BATTERY_LEVEL.mean()
    CHARGING_MINUTES = df_hour.CHARGING_MINUTES.sum()
    MISSING_MINUTES = df_hour.CHARGING_STATES_MISSING_MINUTES.sum()

    y_list.append(y)
    m_list.append(m)
    d_list.append(d)

    BATTERY_LEVEL_list.append(average_battery_level)
    CHARGING_STATUS_list.append(CHARGING_MINUTES)
    MISSING_list.append(MISSING_MINUTES)

    df_day = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "AVERAGE_BATTERY_LEVEL": BATTERY_LEVEL_list, "CHARGING_MINUTES": CHARGING_STATUS_list, "CHARGING_STATES_MISSING_MINUTES": MISSING_list})


    return df_day


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\activity_minute.csv")
    df_hour = get_battery_matrix_day(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
