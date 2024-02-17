import pandas as pd

def getNumericalID(participant_id):

    filter_file_path = "/work/mhealthresearchgroup/cluster_helper_scripts/id_filter_220624_WLW.csv"
    fileter_df = pd.read_csv(filter_file_path)
    record_id_dict = dict(fileter_df[["user_account", "id"]].values)

    record_id = None
    if participant_id in record_id_dict:
        record_id = record_id_dict[participant_id]

    return record_id

if __name__ == "__main__":
    participant_id = "aditya4_internal@timestudy_com"
    getNumericalID(participant_id)
