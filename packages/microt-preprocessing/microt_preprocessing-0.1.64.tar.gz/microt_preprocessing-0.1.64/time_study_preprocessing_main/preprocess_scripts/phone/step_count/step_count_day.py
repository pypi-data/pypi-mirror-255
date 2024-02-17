from os import sep
import pandas as pd
import numpy as np
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan


def get_stepcount_matrix_day(df_stepcount):
    if df_stepcount.shape[0] == 0:
        return None

    # transform df_mims_day
    ymd_list = []
    tz_list = []
    for time_str in df_stepcount["LOG_TIME"]:
        ymd_list.append(time_str.split(" ")[0])
        tz_list.append(time_str.split(" ")[2])

    ymd_list = [x for x in ymd_list if len(x) > 0]
    YMD = list(set(ymd_list))[0]
    tz = list(set(tz_list))[0]
    y = int(YMD.split("-")[0])
    m = int(YMD.split("-")[1])
    d = int(YMD.split("-")[2])
    ttsteps = df_stepcount.STEPS_LAST_HOUR.sum()

    df_day = pd.DataFrame(
        {"YEAR": [y], "MONTH": [m], "DAY": [d], "TOTAL_STEPS": [ttsteps]})

    return df_day


if __name__ == "__main__":
    pass
