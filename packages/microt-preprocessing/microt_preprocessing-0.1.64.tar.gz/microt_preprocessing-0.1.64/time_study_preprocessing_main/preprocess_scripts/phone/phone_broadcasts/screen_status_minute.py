from os import sep
import pandas as pd
import numpy as np
from datetime import datetime
from ...utils.parse_YMD import *
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
colnames = ["YEAR_MONTH_DAY", "HOUR", "MINUTE", "SCREEN_STATUS", "SCREEN_ON_SECONDS", "UNLOCK_EVENTS_NUM"]
converter = lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f")

def transform_dataset(df):

    df = df.dropna(subset=['LOG_TIME'])
    df.reset_index(inplace=True, drop=True)
    df = df[df.PHONE_EVENT.isin(["PHONE_SCREEN_ON", "PHONE_SCREEN_OFF"])]
    df["LOG_TIME"] = [x.split(' ')[0] + " " + x.split(' ')[1]  for x in
                                         list(df["LOG_TIME"])]
    log_datetime_list = list(map(converter, df["LOG_TIME"]))
    df.reset_index(inplace=True, drop=True)

    return df, log_datetime_list

def transform_dataset_unlock(df):

    df = df.dropna(subset=['LOG_TIME'])
    df.reset_index(inplace=True, drop=True)
    df = df[df.PHONE_EVENT.isin(["PHONE_UNLOCKED"])]
    df["LOG_TIME"] = [x.split(' ')[0] + " " + x.split(' ')[1]  for x in
                                         list(df["LOG_TIME"])]

    log_datetime_list = list(map(converter, df["LOG_TIME"]))
    df["HOUR"] = [x.hour for x in log_datetime_list]
    df["MINUTE"] = [x.minute for x in log_datetime_list]
    df.reset_index(inplace=True, drop=True)

    return df

def find_closest_time(prompt_time, subset_time_list):
    # find the closest ahead. If there is none before, return the closest one after
    previous_timestamps = subset_time_list[subset_time_list < prompt_time]
    reverse = False
    if len(previous_timestamps) > 0:
        closet_time = previous_timestamps.max()
    else:
        after_timestamps = subset_time_list[subset_time_list > prompt_time]
        closet_time = after_timestamps.min()
        reverse = True
    return closet_time, reverse

def check_same_time(dt1, dt2):
    same = False
    if dt1.hour == dt2.hour:
        if dt1.minute == dt2.minute:
            same = True
    return same

def get_unlock_events(df_day_unlock, hour, minute):
    num_unlock_events = 0
    df_day_unlock_hour_minute = df_day_unlock[(df_day_unlock["HOUR"] == hour) & (df_day_unlock["MINUTE"] == minute)]
    if len(df_day_unlock_hour_minute) > 0:
        num_unlock_events = len(df_day_unlock_hour_minute)
    return num_unlock_events

def get_screen_status(df_day, log_datetime_list, hm_datetime):

    subset_time_list = np.array(log_datetime_list)
    if len(subset_time_list) == 0:
        return np.nan, np.nan

    closest_time, reverse = find_closest_time(hm_datetime, subset_time_list)
    idx = log_datetime_list.index(closest_time)
    screen_event = df_day.loc[idx, "PHONE_EVENT"]

    # to determine screen on/off
    if not reverse:
        if screen_event == "PHONE_SCREEN_ON":
            screen_status = "On"
            screen_on_seconds = 60
            if idx+1 < len(df_day):
                next_event_time = subset_time_list[idx+1]
                if check_same_time(next_event_time, hm_datetime):
                    screen_status = "On"
                    screen_on_seconds = next_event_time.second
        elif screen_event == "PHONE_SCREEN_OFF":
            screen_status = "Off"
            screen_on_seconds = 0
            if idx+1 < len(df_day):
                next_event_time = subset_time_list[idx+1]
                if check_same_time(next_event_time, hm_datetime):
                    screen_status = "On"
                    screen_on_seconds = 60 - next_event_time.second
        else:
            screen_status = np.nan
    else:
        if screen_event == "PHONE_SCREEN_ON":
            screen_status = "Off"
            screen_on_seconds = 0
            if check_same_time(closest_time, hm_datetime):
                screen_status = "On"
                screen_on_seconds = 60 - closest_time.second
        elif screen_event == "PHONE_SCREEN_OFF":
            screen_status = "On"
            screen_on_seconds = 60
            if check_same_time(closest_time, hm_datetime):
                screen_on_seconds = closest_time.second
        else:
            screen_status = np.nan

    return screen_status, screen_on_seconds

def get_screen_status_matrix_minute(df_day, date):
    df_day = df_day.loc[df_day["LOG_TIME"].str.startswith('2', na=False)]
    df_day.reset_index(inplace=True, drop=True)
    df_day_unlock = transform_dataset_unlock(df_day)
    df_day_screen, log_datetime_list = transform_dataset(df_day)

    # transform df_mims_day
    ymd_list = []
    hour_list = []
    minute_list = []
    # tz_list = []
    for time_str in df_day_screen["LOG_TIME"]:
        hour_min_second = time_str.split(" ")[1]
        hour_min_second_components = hour_min_second.split(":")

        hour_list.append(int(hour_min_second_components[0]))
        minute_list.append(int(hour_min_second_components[1]))
        ymd_list.append(time_str.split(" ")[0])
        # tz_list.append(time_str.split(" ")[2])

    df_day_screen.loc[:, "Hour"] = hour_list
    df_day_screen.loc[:, "Minute"] = minute_list
    df_day_screen.loc[:, "Date"] = ymd_list

    YMD = date
    df_day_screen = df_day_screen[df_day_screen.Date == YMD]
    df_day_screen.reset_index(inplace=True, drop=True)

    # iterate through all minutes in a day and find matched time in df_***_day
    hour_min_dict = dict()
    for hour in range(24):
        for minute in range(60):
            hour_min = str(hour) + "_" + str(minute)
            hour_min_dict[hour_min] = dict()

            hm_datetime = datetime.strptime(YMD + " " + str(hour) + ":" + str(minute), "%Y-%m-%d %H:%M")
            screen_status, screen_on_seconds = get_screen_status(df_day_screen, log_datetime_list, hm_datetime)
            num_unlock_events = get_unlock_events(df_day_unlock, hour, minute)
            hour_min_dict[hour_min]["SCREEN_STATUS"] = screen_status
            hour_min_dict[hour_min]["SCREEN_ON_SECONDS"] = screen_on_seconds
            hour_min_dict[hour_min]["UNLOCK_EVENTS_NUM"] = num_unlock_events

    rows = []
    for hour_min in hour_min_dict:
        row = [YMD, hour_min.split("_")[0], hour_min.split("_")[1], hour_min_dict[hour_min]["SCREEN_STATUS"], hour_min_dict[hour_min]["SCREEN_ON_SECONDS"], hour_min_dict[hour_min]["UNLOCK_EVENTS_NUM"]]
        rows.append(row)

    df_minute = pd.DataFrame(rows, columns=colnames)
    # parse YMD
    y_list, m_list, d_list = parse_YMD(df_minute.YEAR_MONTH_DAY)
    df_minute["YEAR"] = y_list
    df_minute["MONTH"] = m_list
    df_minute["DAY"] = d_list

    return df_minute


if __name__ == "__main__":
    df_day = pd.read_csv(
        r"C:\Users\Jixin\Downloads\phone_system_events_clean_2022-02-06.csv")
    df_minute = get_screen_status_matrix_minute(df_day, "2022-02-06")
    print(df_minute)
    df_minute.to_csv(r"C:\Users\Jixin\Downloads\screen_minute.csv")
