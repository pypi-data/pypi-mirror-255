from os import sep
import pandas as pd
import numpy as np
from collections import Counter
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan


def get_location_cluster_day(df_hour):
    y_list = []
    m_list = []
    d_list = []

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    colname_list = list(df_hour.columns)
    colname_list.remove("HOUR")
    clusterID_list = [x for x in colname_list if x not in ["YEAR","MONTH","DAY"]]
    df_hour = df_hour[clusterID_list]
    df_day = pd.DataFrame(df_hour.sum(axis=0)).T
    # df_day["YEAR_MONTH_DAY"] = ymd
    y_list.append(y)
    m_list.append(m)
    d_list.append(d)
    df_day["YEAR"] = y_list
    df_day["MONTH"] = m_list
    df_day["DAY"] = d_list

    df_day = df_day[colname_list]

    return df_day


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\jixin\Downloads\2020-08-07\phone_location_cluster_minute.csv")
    df_hour = get_location_cluster_day(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
