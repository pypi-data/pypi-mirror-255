from os import sep
import pandas as pd
import numpy as np
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
colnames = ["YEAR_MONTH_DAY", "HOUR", "MINUTE", "SWAN_PREDICTION_NUM", "SWAN_PREDICTION"]


def get_swan_matrix_minute(df_swan_day):
    if df_swan_day.shape[0] == 0:
        return None

    # transform df_mims_day
    ymd_list = []
    hour_list = []
    minute_list = []
    # tz_list = []
    for time_str in df_swan_day["START_TIME"]:
        hour_min_second = time_str.split(" ")[1]
        hour_min_second_components = hour_min_second.split(":")

        hour_list.append(int(hour_min_second_components[0]))
        minute_list.append(int(hour_min_second_components[1]))
        ymd_list.append(time_str.split(" ")[0])
        # tz_list.append(time_str.split(" ")[2])

    df_swan_day.loc[:, "Hour"] = hour_list
    df_swan_day.loc[:, "Minute"] = minute_list
    df_swan_day.loc[:, "Date"] = ymd_list

    ymd_list = [x for x in ymd_list if len(x) > 0]
    YMD = list(set(ymd_list))[0]

    df_swan_day = df_swan_day[df_swan_day.Date == YMD]
    df_swan_day.reset_index(inplace=True, drop=True)

    # iterate through all minutes in a day and find matched time in df_***_day
    hour_min_dict = dict()
    for hour in range(24):
        for min in range(60):
            hour_min = str(hour) + "_" + str(min)

            df_swan_hour = df_swan_day[df_swan_day.Hour == hour]
            df_swan_min = df_swan_hour[df_swan_hour.Minute == min]
            if len(df_swan_min) > 0:
                hour_min_dict[hour_min] = dict()
                hour_min_dict[hour_min]["SWAN_PREDICTION_NUM"] = len(df_swan_min)
                swan_pred_list = list(df_swan_min["PREDICTION"])
                hour_min_dict[hour_min]["SWAN_PREDICTION"] = swan_pred_list[0] if len(
                    set(swan_pred_list)) == 1 else "INDECISIVE"
            else:
                hour_min_dict[hour_min] = {"SWAN_PREDICTION_NUM": 0, "SWAN_PREDICTION": NAN}

    rows = []
    for hour_min in hour_min_dict:
        row = [YMD, hour_min.split("_")[0], hour_min.split("_")[1], hour_min_dict[hour_min]["SWAN_PREDICTION_NUM"],
               hour_min_dict[hour_min]["SWAN_PREDICTION"]]
        rows.append(row)

    df_minute = pd.DataFrame(rows, columns=colnames)
    # parse YMD
    y_list, m_list, d_list = parse_YMD(df_minute.YEAR_MONTH_DAY)
    df_minute["YEAR"] = y_list
    df_minute["MONTH"] = m_list
    df_minute["DAY"] = d_list
    return df_minute


if __name__ == "__main__":
    df_swan_day = pd.read_csv(
        r"D:\data\TIME\intermediate_sample\idealistsustainerexpansive@timestudy_com\2021-11-07\watch_accelerometer_swan_clean_2021-11-07.csv")
    df_minute = get_swan_matrix_minute(df_swan_day)
    print(df_minute)
    df_minute.to_csv(r"C:\Users\Jixin\Downloads\swan_minute.csv")
