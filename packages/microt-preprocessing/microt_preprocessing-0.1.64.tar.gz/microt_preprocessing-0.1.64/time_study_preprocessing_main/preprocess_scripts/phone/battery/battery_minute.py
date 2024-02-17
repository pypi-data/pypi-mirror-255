from os import sep
import pandas as pd
import numpy as np
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
colnames = ["YEAR_MONTH_DAY", "HOUR", "MINUTE", "BATTERY_LEVEL", "CHARGING_STATUS"]


def get_battery_matrix_minute(df_battery_day):
    if df_battery_day.shape[0] == 0:
        return None

    # transform df_mims_day
    ymd_list = []
    hour_list = []
    minute_list = []
    # tz_list = []
    for time_str in df_battery_day["LOG_TIME"]:
        hour_min_second = time_str.split(" ")[1]
        hour_min_second_components = hour_min_second.split(":")

        hour_list.append(int(hour_min_second_components[0]))
        minute_list.append(int(hour_min_second_components[1]))
        ymd_list.append(time_str.split(" ")[0])
        # tz_list.append(time_str.split(" ")[2])

    df_battery_day.loc[:, "Hour"] = hour_list
    df_battery_day.loc[:, "Minute"] = minute_list
    df_battery_day.loc[:, "Date"] = ymd_list

    ymd_list = [x for x in ymd_list if len(x) > 0]
    YMD = list(set(ymd_list))[0]

    df_battery_day = df_battery_day[df_battery_day.Date == YMD]
    df_battery_day.reset_index(inplace=True, drop=True)

    df_battery_day = df_battery_day.drop_duplicates(subset=['Date', 'Hour', 'Minute'], keep='last')
    # iterate through all minutes in a day and find matched time in df_***_day
    hour_min_dict = dict()
    for hour in range(24):
        for min in range(60):
            hour_min = str(hour) + "_" + str(min)

            df_battery_hour = df_battery_day[df_battery_day.Hour == hour]
            df_battery_min = df_battery_hour[df_battery_hour.Minute == min]
            if len(df_battery_min) > 0:
                hour_min_dict[hour_min] = dict()
                hour_min_dict[hour_min]["battery_level"] = list(df_battery_min["Percentage"])[0]
                hour_min_dict[hour_min]["charging_status"] = list(df_battery_min["isCharging"])[0]
            else:
                hour_min_dict[hour_min] = {"battery_level": NAN, "charging_status": NAN}

    rows = []
    for hour_min in hour_min_dict:
        row = [YMD, hour_min.split("_")[0], hour_min.split("_")[1],
               hour_min_dict[hour_min]["battery_level"], hour_min_dict[hour_min]["charging_status"]]
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
