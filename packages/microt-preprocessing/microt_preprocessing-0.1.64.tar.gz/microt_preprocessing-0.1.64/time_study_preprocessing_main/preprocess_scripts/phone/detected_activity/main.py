import os
import shutil
from os import path, makedirs

from ...utils.validate_dates import *
from ...utils.validate_hours import validate_hours
from ...utils.get_time_zone import *
from ...utils.numerical_id import *
from ...utils.convert_timestamp import *
from .parse import *
from .detected_activity_minute import *
from .detected_activity_hour import *
from .detected_activity_day import *
import warnings

warnings.filterwarnings("ignore")

area = "data"
device = "phone"
file_shortname = "detected_activity"

# since the battery file name is mixed with irregular numbers, file name matching is needed.
name_pattern = "ActivityDetected"


def reg_exp_matching(hour_folder_path, name_pattern):
    file_list = listdir(hour_folder_path)
    matched_name = ""
    for file_str in file_list:
        if file_str.startswith(name_pattern):
            matched_name = file_str
            break
    return matched_name


def pre_process(microT_root_path, intermediate_file_save_path, p_id, decrypt_password, date):
    participant_folder_path = microT_root_path
    area_folder_path = participant_folder_path + sep + area
    hours_with_target_file_list = {}  # included in participant stats report
    if path.exists(area_folder_path):
        date_folder_path = area_folder_path + sep + date
        if path.exists(date_folder_path):
            file_save_date_path = intermediate_file_save_path + sep + "intermediate_file" + sep + p_id + sep + date
            if not path.exists(file_save_date_path):
                makedirs(file_save_date_path)
            day_file_name = device + "_" + file_shortname + "_clean_" + date + ".csv"
            day_file_save_path = file_save_date_path + sep + day_file_name
            if not path.exists(day_file_save_path):
                df_participant = pd.DataFrame()
                # time zone
                # time_zone = get_time_zone(date_folder_path)
                # check hourly folder
                validated_hour_list, HAVE_ALL_HOURS = validate_hours(date_folder_path)
                if len(validated_hour_list) == 0:
                    print("Cannot find hour folder in {} data".format(date))
                # iterate through hour folders
                hours_with_target_file = len(validated_hour_list)  # included in participant stats report
                for hour in validated_hour_list:
                    hour_folder_path = date_folder_path + sep + hour
                    # step 2.1: read target hourly file
                    target_file_matched = reg_exp_matching(hour_folder_path, name_pattern)
                    if len(target_file_matched) > 0:
                        target_file_path = hour_folder_path + sep + target_file_matched
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
                        # time zone
                        time_zone = get_time_zone(hour_folder_path)
                        df_hour_parsed = parse_raw_df(df_hour_raw, time_zone)
                        # step 2.4: concatenate hourly file in day level
                        if df_hour_parsed.shape[0] != 0:
                            df_participant = pd.concat([df_participant, df_hour_parsed])

                hours_with_target_file_list[date] = hours_with_target_file
                if hours_with_target_file != 0:
                    # add participant_id and numerical_id
                    pid = p_id.split("@timestudy_com")[0]
                    df_participant["PARTICIPANT_ID_TEXT"] = [pid] * len(df_participant)
                    numerical_id = getNumericalID(pid)
                    df_participant["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_participant)
                    df_participant["LOG_TIMESTAMP"] = [convert_readable_time_to_timestamp(x) for x in
                                                       df_participant["LOG_TIME"]]

                    # step 3:  write out day file for participant
                    day_file_name = device + "_" + file_shortname + "_clean_" + date + ".csv"
                    day_file_save_path = file_save_date_path + sep + day_file_name
                    df_participant = df_participant[
                        ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC", "LOG_TIME", "LOG_TIMESTAMP", "IN_VEHICLE",
                         "ON_BIKE", "ON_FOOT", "RUNNING", "STILL", "TILTING", "WALKING", "UNKNOWN"]]
                    df_participant.to_csv(day_file_save_path, index=False)

                    day_file_name_activity_minute = file_save_date_path + sep + device + "_" + file_shortname + "_minute_" + date + ".csv"
                    day_file_name_activity_hour = file_save_date_path + sep + device + "_" + file_shortname + "_hour_" + date + ".csv"
                    day_file_name_activity_day = file_save_date_path + sep + device + "_" + file_shortname + "_day_" + date + ".csv"

                    if not os.path.exists(day_file_name_activity_minute):
                        # Add a module for minute-level mims sample number
                        df_activity_minute = get_activity_matrix_minute(df_participant)
                        df_activity_minute["PARTICIPANT_ID_TEXT"] = [pid] * len(df_activity_minute)
                        df_activity_minute["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_activity_minute)
                        df_activity_minute = df_activity_minute[
                            ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC", "YEAR", "MONTH", "DAY", "HOUR", "MINUTE",
                             "PHONE_DETECTED_ACTIVITY"]]
                        df_activity_minute.to_csv(day_file_name_activity_minute, index=False)

                        df_activity_hour = get_activity_matrix_hour(df_activity_minute)
                        df_activity_hour["PARTICIPANT_ID_TEXT"] = [pid] * len(df_activity_hour)
                        df_activity_hour["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_activity_hour)
                        df_activity_hour = df_activity_hour[
                            ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC", "YEAR", "MONTH", "DAY", "HOUR",
                             "IN_VEHICLE", "ON_BIKE", "ON_FOOT", "RUNNING", "STILL", "TILTING", "WALKING", "UNKNOWN",
                             "MISSING"]]
                        df_activity_hour.to_csv(day_file_name_activity_hour, index=False)

                        df_activity_day = get_activity_matrix_day(df_activity_hour)
                        df_activity_day["PARTICIPANT_ID_TEXT"] = [pid] * len(df_activity_day)
                        df_activity_day["PARTICIPANT_ID_NUMERIC"] = [numerical_id] * len(df_activity_day)
                        df_activity_day = df_activity_day[
                            ["PARTICIPANT_ID_TEXT", "PARTICIPANT_ID_NUMERIC", "YEAR", "MONTH", "DAY",
                             "IN_VEHICLE", "ON_BIKE", "ON_FOOT", "RUNNING", "STILL", "TILTING", "WALKING", "UNKNOWN",
                             "MISSING"]]
                        df_activity_day.to_csv(day_file_name_activity_day, index=False)


if __name__ == "__main__":
    microT_root_path = r"E:\data\wocket\Wockets-win32-x64\resources\app\src\srv\MICROT"
    intermediate_file_save_path = r"C:\Users\jixin\Desktop\temp"
    p_id_list = ["aditya4_internal@timestudy_com"]
    date_start = "2020-01-01"
    date_end = "2020-07-01"

    pre_process(microT_root_path, intermediate_file_save_path, p_id_list, date_start, date_end)
