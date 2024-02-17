from os import sep
import pandas as pd
import numpy as np
from collections import Counter
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan
activity_types = ["IN_VEHICLE", "ON_BIKE", "ON_FOOT", "RUNNING", "STILL", "TILTING", "WALKING", "UNKNOWN"]


def get_activity_matrix_day(df_hour):
    y_list = []
    m_list = []
    d_list = []

    IN_VEHICLE_pred_list = []
    ON_BIKE_pred_list = []
    ON_FOOT_pred_list = []
    RUNNING_pred_list = []
    STILL_pred_list = []
    TILTING_pred_list = []
    WALKING_pred_list = []
    UNKNOWN_pred_list = []
    MISSING_pred_list = []

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    IN_VEHICLE_pred = df_hour.IN_VEHICLE.sum()
    ON_BIKE_pred = df_hour.ON_BIKE.sum()
    ON_FOOT_pred = df_hour.ON_FOOT.sum()
    RUNNING_pred = df_hour.RUNNING.sum()
    STILL_pred = df_hour.STILL.sum()
    TILTING_pred = df_hour.TILTING.sum()
    WALKING_pred = df_hour.WALKING.sum()
    UNKNOWN_pred = df_hour.UNKNOWN.sum()
    MISSING_pred = df_hour.MISSING.sum()

    y_list.append(y)
    m_list.append(m)
    d_list.append(d)

    IN_VEHICLE_pred_list.append(IN_VEHICLE_pred)
    ON_BIKE_pred_list.append(ON_BIKE_pred)
    ON_FOOT_pred_list.append(ON_FOOT_pred)
    RUNNING_pred_list.append(RUNNING_pred)
    STILL_pred_list.append(STILL_pred)
    TILTING_pred_list.append(TILTING_pred)
    WALKING_pred_list.append(WALKING_pred)
    UNKNOWN_pred_list.append(UNKNOWN_pred)
    MISSING_pred_list.append(MISSING_pred)

    df_day = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "IN_VEHICLE": IN_VEHICLE_pred_list,
         "ON_BIKE": ON_BIKE_pred_list, "ON_FOOT": ON_FOOT_pred_list, "RUNNING": RUNNING_pred_list,
         "STILL": STILL_pred_list, "TILTING": TILTING_pred_list,
         "WALKING": WALKING_pred_list, "UNKNOWN": UNKNOWN_pred_list, "MISSING": MISSING_pred_list})

    return df_day


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\activity_minute.csv")
    df_hour = get_activity_matrix_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
