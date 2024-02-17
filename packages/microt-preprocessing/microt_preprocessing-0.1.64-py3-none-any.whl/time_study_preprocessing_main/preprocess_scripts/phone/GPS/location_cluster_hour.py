from os import sep
import pandas as pd
import numpy as np
from collections import Counter
import warnings

# warnings.filterwarnings("ignore")
NAN = np.nan

def replace_nan_with_str(l):
    l2 = []
    for x in l:
        if type(x) == str:
            l2.append(x)
        elif np.isnan(x):
            l2.append("IN_TRANSIT")
        else:
            l2.append(str(x))
    return l2

def get_location_cluster_hour(df_minute):
    y_list = []
    m_list = []
    d_list = []
    hour_list = []

    y = list(df_minute.YEAR.unique())[0]
    m = list(df_minute.MONTH.unique())[0]
    d = list(df_minute.DAY.unique())[0]

    location_cluster_id_unique_list = df_minute.LOCATION_CLUSTER_ID.unique()



    minute_count_dict = {}
    for clusterID in replace_nan_with_str(location_cluster_id_unique_list):
        minute_count_dict[clusterID] = []

    for hour in range(24):

        df_subset = df_minute[df_minute.HOUR == str(hour)]
        cluster_id_hour_list = replace_nan_with_str(list(df_subset.LOCATION_CLUSTER_ID))
        flat_list = cluster_id_hour_list
        c = Counter(flat_list)
        # print(c)

        for clusterID in minute_count_dict:
            if clusterID in c:
                cluster_minutes = c[clusterID]
                # print(cluster_minutes)
                minute_count_dict[clusterID].append(cluster_minutes)
            else:
                minute_count_dict[clusterID].append(0)

        y_list.append(y)
        m_list.append(m)
        d_list.append(d)
        hour_list.append(hour)

    # print(minute_count_dict)

    df_hour = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "HOUR": hour_list})

    minute_count_dict_sorted = dict(sorted(minute_count_dict.items()))
    # print(minute_count_dict_sorted)
    for clusterID in minute_count_dict_sorted:

        cid = "<{}>".format(clusterID)
        # elif np.isnan(clusterID):
        #     cid = "<IN_TRANSIT>"

        df_hour[cid] = minute_count_dict_sorted[clusterID]

    return df_hour


if __name__ == "__main__":
    df_minute = pd.read_csv(
        r"C:\Users\jixin\Downloads\2020-08-07\phone_location_cluster_minute.csv")
    df_hour = get_location_cluster_hour(df_minute)
    print(df_hour)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")