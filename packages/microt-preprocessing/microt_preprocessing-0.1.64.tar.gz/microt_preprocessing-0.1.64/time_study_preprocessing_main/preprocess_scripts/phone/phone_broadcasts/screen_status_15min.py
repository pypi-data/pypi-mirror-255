from os import sep
import pandas as pd
import numpy as np
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan


def get_screen_status_matrix_minute15(df_minute):
    ymd_list = []
    hour_list = []
    quart_list = [] # 15 min
    screen_on_seconds_list = []
    unlock_events_num_list = []

    ymd = list(df_minute.YEAR_MONTH_DAY.unique())[0]
    df_minute["MINUTE"] = df_minute.MINUTE.astype("int")

    for hour in range(24):
        for quart in range(4):
            df_subset = df_minute[(df_minute.HOUR == str(hour)) & (df_minute.MINUTE >= quart*15) & (df_minute.MINUTE < (quart+1)*15)]
            screen_on_seconds_hour = df_subset.SCREEN_ON_SECONDS.sum()
            unlock_events_num = df_subset.UNLOCK_EVENTS_NUM.sum()

            ymd_list.append(ymd)
            hour_list.append(hour)
            quart_list.append((quart+1)*15)
            screen_on_seconds_list.append(screen_on_seconds_hour)
            unlock_events_num_list.append(unlock_events_num)

    df_hour = pd.DataFrame(
        {"YEAR_MONTH_DAY": ymd_list, "HOUR": hour_list, "MINUTE15": quart_list, "SCREEN_ON_SECONDS": screen_on_seconds_list, "UNLOCK_EVENTS_NUM": unlock_events_num_list})

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\screen_minute.csv")
    df_hour = get_screen_status_matrix_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
