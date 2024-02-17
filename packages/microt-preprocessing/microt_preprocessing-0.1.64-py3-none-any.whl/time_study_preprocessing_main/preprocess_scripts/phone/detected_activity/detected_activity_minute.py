from os import sep
import pandas as pd
import numpy as np
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
colnames = ["YEAR_MONTH_DAY", "HOUR", "MINUTE", "PHONE_DETECTED_ACTIVITY"]
activity_types = ["IN_VEHICLE", "ON_BIKE","ON_FOOT", "RUNNING", "STILL", "TILTING","WALKING", "UNKNOWN"]


def get_activity_matrix_minute(df_activity_day):
    if df_activity_day.shape[0] == 0:
        return None

    # transform df_mims_day
    ymd_list = []
    hour_list = []
    minute_list = []
    # tz_list = []
    for time_str in df_activity_day["LOG_TIME"]:
        hour_min_second = time_str.split(" ")[1]
        hour_min_second_components = hour_min_second.split(":")

        hour_list.append(int(hour_min_second_components[0]))
        minute_list.append(int(hour_min_second_components[1]))
        ymd_list.append(time_str.split(" ")[0])
        # tz_list.append(time_str.split(" ")[2])

    df_activity_day.loc[:, "Hour"] = hour_list
    df_activity_day.loc[:, "Minute"] = minute_list
    df_activity_day.loc[:, "Date"] = ymd_list

    ymd_list = [x for x in ymd_list if len(x) > 0]
    YMD = list(set(ymd_list))[0]

    df_activity_day = df_activity_day[df_activity_day.Date == YMD]
    df_activity_day.reset_index(inplace=True, drop=True)

    # merge confidence values for duplicated rows of the same time
    #df_activity_day = pd.pivot_table(df_activity_day, index=['Date', 'Hour', 'Minute'], values=activity_types, aggfunc='sum')
    #df_activity_day = df_activity_day.reset_index()
    df_pred = df_activity_day[activity_types].apply(pd.to_numeric)

    # select prediction with the highest confidence
    df_activity_day["ACTIVITY_PREDICTION"] = df_pred.idxmax(axis=1)

    # iterate through all minutes in a day and find matched time in df_***_day
    hour_min_dict = dict()
    for hour in range(24):
        for min in range(60):
            hour_min = str(hour) + "_" + str(min)

            df_activity_hour = df_activity_day[df_activity_day.Hour == hour]
            df_activity_min = df_activity_hour[df_activity_hour.Minute == min]
            if len(df_activity_min) > 0:
                hour_min_dict[hour_min] = dict()
                hour_min_dict[hour_min]["ACTIVITY_PREDICTION"] = list(df_activity_min["ACTIVITY_PREDICTION"])[0]
            else:
                hour_min_dict[hour_min] = {"ACTIVITY_PREDICTION": NAN}

    rows = []
    for hour_min in hour_min_dict:
        row = [YMD, hour_min.split("_")[0], hour_min.split("_")[1],
               hour_min_dict[hour_min]["ACTIVITY_PREDICTION"]]
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
