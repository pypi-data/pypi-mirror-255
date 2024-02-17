import pandas as pd
import numpy as np

NAN = np.nan


def get_auc_matrix_day(df_hour):
    y_list = []
    m_list = []
    d_list = []
    # tz_list = []
    auc_sample_num_list = []
    auc_x_list = []
    auc_y_list = []
    auc_z_list = []

    y = list(df_hour.YEAR.unique())[0]
    m = list(df_hour.MONTH.unique())[0]
    d = list(df_hour.DAY.unique())[0]

    # tz = list(df_hour.TIMEZONE.unique())[0]

    auc_sample_num_hour = df_hour.SAMPLE_COUNT.sum()
    if auc_sample_num_hour == 0:
        auc_x_day = NAN
        auc_y_day = NAN
        auc_z_day = NAN
    else:
        auc_x_day = df_hour.AUC_X.sum()
        auc_y_day = df_hour.AUC_Y.sum()
        auc_z_day = df_hour.AUC_Z.sum()

    y_list.append(y)
    m_list.append(m)
    d_list.append(d)
    # tz_list.append(tz)
    auc_sample_num_list.append(auc_sample_num_hour)
    auc_x_list.append(auc_x_day)
    auc_y_list.append(auc_y_day)
    auc_z_list.append(auc_z_day)

    df_day = pd.DataFrame(
        {"YEAR": y_list, "MONTH": m_list, "DAY": d_list, "SAMPLE_COUNT": auc_sample_num_list,
         "AUC_X": auc_x_list, "AUC_Y": auc_y_list, "AUC_Z": auc_z_list})

    return df_day


if __name__ == "__main__":
    df_hour = pd.read_csv(
        r"C:\Users\Jixin\Downloads\auc_minute.csv")
    print(df_hour.TIMEZONE)
    df_day = get_auc_matrix_day(df_hour)
    print(df_day)
    # df_hour.to_csv(r"C:\Users\Jixin\Downloads\watch_accelerometer_decompose_hour_2021-02-04.csv")
