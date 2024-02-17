from os import sep
import pandas as pd
import numpy as np
from collections import Counter
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
activity_types = ["IN_VEHICLE", "ON_BIKE", "ON_FOOT", "RUNNING", "STILL", "TILTING", "WALKING", "UNKNOWN"]


def get_activity_matrix_hour(df_minute):
    y_list = []
    m_list = []
    d_list = []
    hour_list = []

    IN_VEHICLE_pred_list = []
    ON_BIKE_pred_list = []
    ON_FOOT_pred_list = []
    RUNNING_pred_list = []
    STILL_pred_list = []
    TILTING_pred_list = []
    WALKING_pred_list = []
    UNKNOWN_pred_list = []
    MISSING_pred_list = []


    y = list(df_minute.YEAR.unique())[0]
    m = list(df_minute.MONTH.unique())[0]
    d = list(df_minute.DAY.unique())[0]

    for hour in range(24):
        df_subset = df_minute[df_minute.HOUR == str(hour)]
        pred_count = Counter(df_subset.PHONE_DETECTED_ACTIVITY)
        if "IN_VEHICLE" in pred_count:
            IN_VEHICLE_pred = pred_count["IN_VEHICLE"]
        else:
            IN_VEHICLE_pred = 0

        if "ON_BIKE" in pred_count:
            ON_BIKE_pred = pred_count["ON_BIKE"]
        else:
            ON_BIKE_pred = 0

        if "ON_FOOT" in pred_count:
            ON_FOOT_pred = pred_count["ON_FOOT"]
        else:
            ON_FOOT_pred = 0

        if "RUNNING" in pred_count:
            RUNNING_pred = pred_count["RUNNING"]
        else:
            RUNNING_pred = 0

        if "STILL" in pred_count:
            STILL_pred = pred_count["STILL"]
        else:
            STILL_pred = 0

        if "TILTING" in pred_count:
            TILTING_pred = pred_count["TILTING"]
        else:
            TILTING_pred = 0

        if "WALKING" in pred_count:
            WALKING_pred = pred_count["WALKING"]
        else:
            WALKING_pred = 0

        if "UNKNOWN" in pred_count:
            UNKNOWN_pred = pred_count["UNKNOWN"]
        else:
            UNKNOWN_pred = 0

        MISSING_pred = 60 - IN_VEHICLE_pred - ON_BIKE_pred - ON_FOOT_pred - RUNNING_pred - STILL_pred - TILTING_pred - WALKING_pred - UNKNOWN_pred

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
        hour_list.append(hour)

        IN_VEHICLE_pred_list.append(IN_VEHICLE_pred)
        ON_BIKE_pred_list.append(ON_BIKE_pred)
        ON_FOOT_pred_list.append(ON_FOOT_pred)
        RUNNING_pred_list.append(RUNNING_pred)
        STILL_pred_list.append(STILL_pred)
        TILTING_pred_list.append(TILTING_pred)
        WALKING_pred_list.append(WALKING_pred)
        UNKNOWN_pred_list.append(UNKNOWN_pred)
        MISSING_pred_list.append(MISSING_pred)

    df_hour = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list,  "HOUR": hour_list, "IN_VEHICLE": IN_VEHICLE_pred_list,
         "ON_BIKE": ON_BIKE_pred_list, "ON_FOOT": ON_FOOT_pred_list, "RUNNING": RUNNING_pred_list,
         "STILL": STILL_pred_list, "TILTING": TILTING_pred_list,
         "WALKING": WALKING_pred_list, "UNKNOWN": UNKNOWN_pred_list, "MISSING": MISSING_pred_list})

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\activity_minute.csv")
    df_hour = get_activity_matrix_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
