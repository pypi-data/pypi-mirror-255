from os import sep
import pandas as pd
import numpy as np
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
colnames = ["YEAR_MONTH_DAY", "HOUR", "MINUTE", "WIFI_STATUS"]


def get_wifi_matrix_minute(df_wifi_day):
    if df_wifi_day.shape[0] == 0:
        return None

    # transform df_mims_day
    ymd_list = []
    hour_list = []
    minute_list = []
    # tz_list = []
    for time_str in df_wifi_day["LOG_TIME"]:
        hour_min_second = time_str.split(" ")[1]
        hour_min_second_components = hour_min_second.split(":")

        hour_list.append(int(hour_min_second_components[0]))
        minute_list.append(int(hour_min_second_components[1]))
        ymd_list.append(time_str.split(" ")[0])
        # tz_list.append(time_str.split(" ")[2])

    df_wifi_day.loc[:, "Hour"] = hour_list
    df_wifi_day.loc[:, "Minute"] = minute_list
    df_wifi_day.loc[:, "Date"] = ymd_list

    ymd_list = [x for x in ymd_list if len(x) > 0]
    YMD = list(set(ymd_list))[0]

    df_wifi_day = df_wifi_day[df_wifi_day.Date == YMD]
    df_wifi_day.reset_index(inplace=True, drop=True)

    df_wifi_day = df_wifi_day.drop_duplicates(subset=['Date', 'Hour', 'Minute'], keep='last')
    # iterate through all minutes in a day and find matched time in df_***_day
    hour_min_dict = dict()
    for hour in range(24):
        for min in range(60):
            hour_min = str(hour) + "_" + str(min)

            df_wifi_hour = df_wifi_day[df_wifi_day.Hour == hour]
            df_wifi_min = df_wifi_hour[df_wifi_hour.Minute == min]
            if len(df_wifi_min) > 0:
                hour_min_dict[hour_min] = dict()
                hour_min_dict[hour_min]["WIFI"] = list(df_wifi_min["IS_WIFI_ON"])[0]
            else:
                hour_min_dict[hour_min] = {"WIFI": NAN}

    rows = []
    for hour_min in hour_min_dict:
        row = [YMD, hour_min.split("_")[0], hour_min.split("_")[1],
               hour_min_dict[hour_min]["WIFI"]]
        rows.append(row)

    df_minute = pd.DataFrame(rows, columns=colnames)
    # parse YMD
    y_list, m_list, d_list = parse_YMD(df_minute.YEAR_MONTH_DAY)
    df_minute["YEAR"] = y_list
    df_minute["MONTH"] = m_list
    df_minute["DAY"] = d_list

    return df_minute


if __name__ == "__main__":
    pass
