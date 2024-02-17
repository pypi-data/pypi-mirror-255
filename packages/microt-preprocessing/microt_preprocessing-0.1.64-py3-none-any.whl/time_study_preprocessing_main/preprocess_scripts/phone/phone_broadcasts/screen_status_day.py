from os import sep
import pandas as pd
import numpy as np
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan


def get_screen_status_matrix_day(df_hour):
    y_list = []
    m_list = []
    d_list = []
    screen_on_seconds_list = []
    unlock_events_num_list = []

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    screen_on_seconds_hour = df_hour.SCREEN_ON_SECONDS.sum()
    unlock_events_num = df_hour.UNLOCK_EVENTS_NUM.sum()

    y_list.append(y)
    m_list.append(m)
    d_list.append(d)

    screen_on_seconds_list.append(screen_on_seconds_hour)
    unlock_events_num_list.append(unlock_events_num)

    df_day = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "SCREEN_ON_SECONDS": screen_on_seconds_list,
         "UNLOCK_EVENTS_NUM": unlock_events_num_list})

    return df_day


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\screen_minute.csv")
    df_hour = get_screen_status_matrix_day(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
