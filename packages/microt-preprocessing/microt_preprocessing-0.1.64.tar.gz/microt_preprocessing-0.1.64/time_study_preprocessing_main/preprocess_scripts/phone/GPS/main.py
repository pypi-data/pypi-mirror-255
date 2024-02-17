import os
import shutil
from os import path, makedirs

from ...utils.validate_dates import *
from ...utils.validate_hours import validate_hours
from .parse import *
from .location_cluster_hour import *
from .location_cluster_minute import *
from .location_cluster_day import *
from ...utils.numerical_id import *
from ...utils.convert_timestamp import *
import warnings
# import zipFile
import pyminizip
import mhealthlab_client.mhlab as mhlab

warnings.filterwarnings("ignore")

area = "data"
device = "phone"
file_shortname = "GPS"

# since the battery file name is mixed with irregular numbers, file name matching is needed.
name_pattern = "GPS"
cluster_label_table_folder_path = "/work/mhealthresearchgroup/TIME_STD/location_clustering/visit_table"

def reg_exp_matching(hour_folder_path, name_pattern):
    file_list = listdir(hour_folder_path)
    matched_name_list = []
    for file_str in file_list:
        if file_str.startswith(name_pattern):
            if not file_str.endswith("done"):
                matched_name_list.append(file_str)
    return matched_name_list


def pre_process(microT_root_path, intermediate_file_save_path, p_id, decrypt_password, date):
    participant_folder_path = microT_root_path
    area_folder_path = participant_folder_path + sep + area
    hours_with_target_file_list = {}  # included in participant stats report
    # step 2: iterate through all hour folders for each date
    if path.exists(area_folder_path):
        date_folder_path = area_folder_path + sep + date
        if path.exists(date_folder_path):
            file_save_date_path = intermediate_file_save_path + sep + "intermediate_file" + sep + p_id + sep + date
            if not path.exists(file_save_date_path):
                makedirs(file_save_date_path)
            day_file_name = device + "_" + file_shortname + "_clean_" + date + ".csv"
            day_file_save_path = file_save_date_path + sep + day_file_name
            day_zip_file_save_path = day_file_save_path + '.zip'
            if not path.exists(day_zip_file_save_path):
                df_participant = pd.DataFrame()
                # check hourly folder
                validated_hour_list, HAVE_ALL_HOURS = validate_hours(date_folder_path)
                if len(validated_hour_list) == 0:
                    print("Cannot find hour folders in {} data".format(date))
                # iterate through hour folders
                hours_with_target_file = len(validated_hour_list)  # included in participant stats report
                for hour in validated_hour_list:
                    hour_folder_path = date_folder_path + sep + hour
                    if not path.exists(hour_folder_path):
                        continue
                    # step 2.1: read target hourly file
                    target_files_matched = reg_exp_matching(hour_folder_path, name_pattern)

                    if len(target_files_matched) > 0:
                        for target_file in target_files_matched:
                            if target_file.endswith("zip"):
                                target_file_path = hour_folder_path + sep + target_file
                                mhlab.decrypt_file(target_file_path, hour_folder_path, decrypt_password.encode())
                                target_file = target_file.replace(".zip", "")

                            target_file_path = hour_folder_path + sep + target_file
                            try:
                                df_hour_raw = pd.read_csv(target_file_path, header=None)
                            except:
                                # print("Empty csv file", target_file_path)
                                continue
                    else:
                        hours_with_target_file -= 1
                        continue

                    # step 2.2: parse target hourly file
                    if df_hour_raw.shape[0] != 0:
                        df_hour_parsed = parse_raw_df(df_hour_raw)
                        # step 2.4: concatenate hourly file in day level
                        if df_hour_parsed.shape[0] != 0:
                            df_participant = pd.concat([df_participant, df_hour_parsed])

                hours_with_target_file_list[date] = hours_with_target_file
                if hours_with_target_file != 0:
                    # step 3:  write out day file for participant
                    pid = p_id.split("@timestudy_com")[0]
                    df_participant["PARTICIPANT_ID_TEXT"] = [pid] * len(df_participant)
                    numerical_id = getNumericalID(pid)
                    df_participant["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_participant)
                    df_participant["LOCATION_TIMESTAMP"] = [convert_readable_time_to_timestamp(x) for x in
                                                            df_participant["LOCATION_TIME"]]
                    df_participant = df_participant[
                        ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC", "LOG_TIME", "LOCATION_TIME", "LOCATION_TIMESTAMP", "LAT", "LONG", "HORIZONTAL_ACCURACY", "PROVIDER", "SPEED", "ALTITUDE", "BEARING"]]
                    df_participant.to_csv(day_file_save_path, index=False)
                    pyminizip.compress(day_file_save_path, None, day_zip_file_save_path, decrypt_password, 0)
                    os.remove(day_file_save_path)

    file_save_date_path = intermediate_file_save_path + sep + "intermediate_file" + sep + p_id + sep + date
    ind_cluster_label_intermediate_path_minute = os.path.join(file_save_date_path, "phone_location_cluster_minute_{}.csv".format(date))
    ind_cluster_label_intermediate_path_hour = os.path.join(file_save_date_path, "phone_location_cluster_hour_{}.csv".format(date))
    ind_cluster_label_intermediate_path_day = os.path.join(file_save_date_path, "phone_location_cluster_day_{}.csv".format(date))
    if not path.exists(ind_cluster_label_intermediate_path_minute) or not path.exists(ind_cluster_label_intermediate_path_hour):
        if not path.exists(file_save_date_path):
            makedirs(file_save_date_path)
        ind_cluster_label_table_path = os.path.join(cluster_label_table_folder_path, p_id + "_cluster_label_table.csv")
        if path.exists(ind_cluster_label_table_path):
            df_cluster_minute = get_location_cluster_minute(ind_cluster_label_table_path, date)
            if df_cluster_minute is not None:
                # add participant_id and numerical_id
                pid = p_id.split("@timestudy_com")[0]
                numerical_id = getNumericalID(pid)
                minute_colnames = list(df_cluster_minute.keys())
                df_cluster_minute["PARTICIPANT_ID_TEXT"] = [pid] * len(df_cluster_minute)
                df_cluster_minute["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_cluster_minute)
                # df_cluster_minute["LOG_TIMESTAMP"] = [convert_readable_time_list_to_timestamp(x) for x in
                #                                    df_cluster_minute["LOG_TIME"]]
                df_cluster_minute = df_cluster_minute[
                    ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC"]+minute_colnames]
                df_cluster_minute.to_csv(ind_cluster_label_intermediate_path_minute, index=False)


                df_cluster_hour = get_location_cluster_hour(df_cluster_minute)
                hour_colnames = list(df_cluster_hour.keys())
                df_cluster_hour["PARTICIPANT_ID_TEXT"] = [pid] * len(df_cluster_hour)
                df_cluster_hour["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_cluster_hour)
                # df_cluster_hour["LOG_TIMESTAMP"] = [convert_readable_time_list_to_timestamp(x) for x in
                #                                    df_cluster_hour["LOG_TIME"]]
                df_cluster_hour = df_cluster_hour[
                    ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC"]+hour_colnames]
                df_cluster_hour.to_csv(ind_cluster_label_intermediate_path_hour, index=False)


                df_cluster_day = get_location_cluster_day(df_cluster_hour)
                day_colnames = list(df_cluster_day.keys())
                df_cluster_day["PARTICIPANT_ID_TEXT"] = [pid] * len(df_cluster_day)
                df_cluster_day["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_cluster_day)
                # df_cluster_hour["LOG_TIMESTAMP"] = [convert_readable_time_list_to_timestamp(x) for x in
                #                                    df_cluster_hour["LOG_TIME"]]
                df_cluster_day = df_cluster_day[
                    ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC"]+day_colnames]
                df_cluster_day.to_csv(ind_cluster_label_intermediate_path_day, index=False)



if __name__ == "__main__":
    microT_root_path = r"E:\data\wocket\Wockets-win32-x64\resources\app\src\srv\MICROT"
    intermediate_file_save_path = r"C:\Users\jixin\Desktop\temp"
    p_id_list = ["aditya4_internal@timestudy_com"]
    date_start = "2020-01-01"
    date_end = "2020-07-01"

    pre_process(microT_root_path, intermediate_file_save_path, p_id_list, date_start, date_end)
