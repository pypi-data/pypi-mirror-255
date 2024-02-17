from datetime import datetime, timedelta, timezone
import pandas as pd

time_offset_dict = {
    "CDT": "UTC-05",
    "CST": "UTC-06",
    "MDT": "UTC-06",
    "MST": "UTC-07",
    "PDT": "UTC-07",
    "PST": "UTC-08",
    "EDT": "UTC-04",
    "EST": "UTC-05",
    "AKDT": "UTC-08",
    "AKST": "UTC-09",
    "HDT": "UTC-09",
    "HST": "UTC-10"
}

month_str_dict = {
    "Jan": "01",
    "Feb": "02",
    "Mar": "03",
    "Apr": "04",
    "May": "05",
    "Jun": "06",
    "Jul": "07",
    "Aug": "08",
    "Sep": "09",
    "Oct": "10",
    "Nov": "11",
    "Dec": "12"

}


def parse_time_offset(time_offset):
    sign_str = time_offset.strip('UTC')[0]
    if sign_str == "-":
        sign = -1
    elif sign_str == "+":
        sign = 1
    else:
        sigh = 0

    time_offset_int = int(time_offset.strip('UTC')[1:])
    time_delta = timedelta(hours=time_offset_int)

    return time_delta, sign


def get_time_offset(time_zone_abbr):
    time_delta = timedelta(hours=0)
    sign = 0

    if time_zone_abbr in time_offset_dict:
        time_offset = time_offset_dict[time_zone_abbr]
        time_delta, sign = parse_time_offset(time_offset)

    return time_delta, sign


def convert_timestamp_int_list_to_readable_time(timestamp_int_list, time_zone):
    time_delta, sign = get_time_offset(time_zone)
    if time_zone == "unknownTZ" or sign == 0:
        readable_time_str = ["unknown time zone"] * len(timestamp_int_list)
    else:
        timestamp_naive_list = pd.to_datetime(timestamp_int_list, unit='ms', errors='coerce')
        timestamp_TZaware_list = timestamp_naive_list + sign * time_delta
        converter = lambda x: x.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] if pd.notnull(x) else ''
        readable_time_str = pd.Series(map(converter, timestamp_TZaware_list))
        readable_time_str += " " + time_zone

    return readable_time_str


def convert_readable_time_to_timestamp(readable_time):
    if len(readable_time.split(" ")) < 3:
        timestamp_str = "unknown time zone"
    else:
        time_zone = readable_time.split(" ")[2]
        time_delta, sign = get_time_offset(time_zone)
        if time_zone == "unknownTZ" or sign == 0:
            timestamp_str = "unknown time zone"
        else:
            readable_time = readable_time.split(" ")[0] + " " + readable_time.split(" ")[1]
            if "." in readable_time:
                datetime_time = datetime.strptime(readable_time, "%Y-%m-%d %H:%M:%S.%f")
            else:
                datetime_time = datetime.strptime(readable_time, "%Y-%m-%d %H:%M:%S")
            # datetime_time_tz = datetime_time
            datetime_time_tz = datetime_time - sign * time_delta
            timestamp_str = datetime_time_tz.replace(tzinfo=timezone.utc).timestamp()  # float
            # print(type(timestamp_str))
    return timestamp_str


def convert_month_str_to_num(month_str):
    return month_str_dict[month_str]

def convert_num_to_str(x):
    if len(str(x)) == 1:
        x = "0"+str(x)
    else:
        x = str(x)

    return x


def convert_time_str_to_readable_time(time_str):
    time_parts = time_str.split(" ")
    month_str = convert_month_str_to_num(time_parts[1])
    day_str = convert_num_to_str(time_parts[2])
    hms_str = time_parts[3]
    tz_str = time_parts[4]
    year_str = time_parts[5]

    return year_str + "-" + month_str + "-" + day_str + " " + hms_str + " " + tz_str


if __name__ == "__main__":
    # sample_csv_path = r"E:\intermediate_file\aditya4_internal@timestudy_com\2020-06-03\phone_app_usage_clean_hour_temp\phone_app_usage_clean_03-EDT.csv"
    # time_zone = "EDT"
    # df = pd.read_csv(sample_csv_path)
    # print(convert_timestamp_int_list_to_readable_time(df['LAST_HOUR_TIMESTAMP'], time_zone))
    # print("{} is translated to {} .".format(str(timestamp_int), convert_timestamp2string(timestamp_int, time_zone)))
    readable_time = "2020-08-07 21:11:46.030 CDT"
    print(convert_readable_time_to_timestamp(readable_time))
