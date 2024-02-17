import os
import pandas as pd
import numpy as np


NAN = np.nan

def get_mims_matrix_day(df_hour):
    y_list = []
    m_list = []
    d_list = []
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

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    # tz = list(df_hour.TIMEZONE.unique())[0]
    mims_sample_num_day = df_hour.MIMS_SAMPLE_NUM.sum()
    mims_invalid_sample_num_day = NAN
    mims_sample_num_day_wear = NAN
    mims_sample_num_day_nonwear = NAN
    mims_sample_num_day_sleep = NAN
    mims_sum_day = NAN
    mims_sum_day_wear = NAN
    mims_sum_day_nonwear = NAN
    mims_sum_day_sleep = NAN

    if mims_sample_num_day != 0:
        mims_invalid_sample_num_day = df_hour.MIMS_INVALID_SAMPLE_NUM.sum()
        mims_sum_day = df_hour.MIMS_SUM.sum()

        mims_sample_num_day_wear = df_hour.MIMS_SAMPLE_NUM_WEAR.sum()
        mims_sample_num_day_nonwear = df_hour.MIMS_SAMPLE_NUM_NONWEAR.sum()
        mims_sample_num_day_sleep = df_hour.MIMS_SAMPLE_NUM_SLEEP.sum()

        mims_sum_day_wear = df_hour.MIMS_SUM_WEAR.sum()
        mims_sum_day_nonwear = df_hour.MIMS_SUM_NONWEAR.sum()
        mims_sum_day_sleep = df_hour.MIMS_SUM_SLEEP.sum()


    y_list.append(y)
    m_list.append(m)
    d_list.append(d)
    # tz_list.append(tz)
    mims_sample_num_list.append(mims_sample_num_day)
    mims_sample_num_wear_list.append(mims_sample_num_day_wear)
    mims_sample_num_nonwear_list.append(mims_sample_num_day_nonwear)
    mims_sample_num_sleep_list.append(mims_sample_num_day_sleep)
    mims_invalid_sample_num_list.append(mims_invalid_sample_num_day)
    mims_sum_list.append(mims_sum_day)
    mims_sum_wear_list.append(mims_sum_day_wear)
    mims_sum_nonwear_list.append(mims_sum_day_nonwear)
    mims_sum_sleep_list.append(mims_sum_day_sleep)

    df_day = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "MIMS_SAMPLE_NUM": mims_sample_num_list,
         "MIMS_INVALID_SAMPLE_NUM": mims_invalid_sample_num_list, "MIMS_SUM": mims_sum_list,
         "MIMS_SAMPLE_NUM_WEAR": mims_sample_num_wear_list, "MIMS_SAMPLE_NUM_NONWEAR": mims_sample_num_nonwear_list,
         "MIMS_SAMPLE_NUM_SLEEP": mims_sample_num_sleep_list, "MIMS_SUM_WEAR": mims_sum_wear_list,
         "MIMS_SUM_NONWEAR": mims_sum_nonwear_list, "MIMS_SUM_SLEEP": mims_sum_sleep_list})

    return df_day


if __name__ == "__main__":
    df_hour = pd.read_csv(
        r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_minute_2021-02-04.csv")
    df_day = get_mims_matrix_day(df_hour)
    print(df_day)
    df_day.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
