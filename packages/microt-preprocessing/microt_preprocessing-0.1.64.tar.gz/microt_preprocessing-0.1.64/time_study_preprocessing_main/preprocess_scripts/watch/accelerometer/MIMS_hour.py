import os
from os import sep
import pandas as pd
import numpy as np
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan

def get_mims_matrix_hour(df_minute, day_file_name_swan_minute):
    y_list = []
    m_list = []
    d_list = []
    hour_list = []
    tz_list = []
    mims_sample_num_list = []
    mims_invalid_sample_num_list = []
    mims_sum_list = []
    mims_sum_wear_list = []
    mims_sum_nonwear_list = []
    mims_sum_sleep_list = []
    mims_sample_num_wear_list = []
    mims_sample_num_nonwear_list = []
    mims_sample_num_sleep_list = []

    y = list(df_minute.YEAR.unique())[0]
    m = list(df_minute.MONTH.unique())[0]
    d = list(df_minute.DAY.unique())[0]

    swan_minute_exits = False
    if os.path.exists(day_file_name_swan_minute):
        swan_minute_exits = True
        df_swan_minute = pd.read_csv(day_file_name_swan_minute)
        df_minute['swan'] = df_swan_minute.SWAN_PREDICTION

    for hour in range(24):
        df_subset = df_minute[df_minute.HOUR == str(hour)]
        # tz = list(df_subset.TIMEZONE.unique())[0]
        mims_sample_num_hour = df_subset.MIMS_SAMPLE_NUM.sum()
        mims_invalid_sample_num_hour = NAN
        mims_sample_num_hour_wear = NAN
        mims_sample_num_hour_nonwear = NAN
        mims_sample_num_hour_sleep = NAN
        mims_sum_hour = NAN
        mims_sum_hour_wear = NAN
        mims_sum_hour_nonwear = NAN
        mims_sum_hour_sleep = NAN

        if mims_sample_num_hour != 0:
            mims_invalid_sample_num_hour = df_subset.MIMS_INVALID_SAMPLE_NUM.sum()
            mims_sum_hour = df_subset.MIMS_SUM.sum()

            if swan_minute_exits:
                df_subset_wear = df_subset[df_subset.swan == "Wear"]
                df_subset_nonwear = df_subset[df_subset.swan == "Nonwear"]
                df_subset_sleep = df_subset[df_subset.swan == "Sleep"]

                mims_sample_num_hour_wear = df_subset_wear.MIMS_SAMPLE_NUM.sum()
                mims_sample_num_hour_nonwear = df_subset_nonwear.MIMS_SAMPLE_NUM.sum()
                mims_sample_num_hour_sleep = df_subset_sleep.MIMS_SAMPLE_NUM.sum()

                mims_sum_hour_wear = df_subset_wear.MIMS_SUM.sum()
                mims_sum_hour_nonwear = df_subset_nonwear.MIMS_SUM.sum()
                mims_sum_hour_sleep = df_subset_sleep.MIMS_SUM.sum()

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
        hour_list.append(hour)
        # tz_list.append(tz)

        mims_sample_num_list.append(mims_sample_num_hour)
        mims_sample_num_wear_list.append(mims_sample_num_hour_wear)
        mims_sample_num_nonwear_list.append(mims_sample_num_hour_nonwear)
        mims_sample_num_sleep_list.append(mims_sample_num_hour_sleep)

        mims_invalid_sample_num_list.append(mims_invalid_sample_num_hour)

        mims_sum_list.append(mims_sum_hour)
        mims_sum_wear_list.append(mims_sum_hour_wear)
        mims_sum_nonwear_list.append(mims_sum_hour_nonwear)
        mims_sum_sleep_list.append(mims_sum_hour_sleep)

    df_hour = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "HOUR": hour_list, "MIMS_SAMPLE_NUM": mims_sample_num_list,
         "MIMS_INVALID_SAMPLE_NUM": mims_invalid_sample_num_list, "MIMS_SUM": mims_sum_list,
         "MIMS_SAMPLE_NUM_WEAR": mims_sample_num_wear_list, "MIMS_SAMPLE_NUM_NONWEAR": mims_sample_num_nonwear_list,
         "MIMS_SAMPLE_NUM_SLEEP": mims_sample_num_sleep_list, "MIMS_SUM_WEAR": mims_sum_wear_list,
         "MIMS_SUM_NONWEAR": mims_sum_nonwear_list, "MIMS_SUM_SLEEP": mims_sum_sleep_list})

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_minute_2021-02-04.csv")
    df_hour = get_mims_matrix_hour(df_minute)
    print(df_hour)
    df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
