from os.path import join, relpath
from pandas import read_csv, concat
from pm4py import discover_dfg, get_start_activities, get_end_activities, read_xes, convert_to_dataframe
from my_utils import check_csv_file, get_csv_delimiter
from time import time

case_id = "case:concept:name"
activity = "concept:name"
timestamp = "time:timestamp"
from_csv_to_df = {"case": case_id, "activity": activity, "time": timestamp}
from_df_to_csv = {case_id: "case", activity: "activity", timestamp: "time"}


def enhance_dfg(new_dfg):
    global dfg
    keys = dfg.keys()
    for edge in new_dfg.keys():
        if edge in keys:
            dfg[edge] += new_dfg[edge]
        else:
            dfg[edge] = new_dfg[edge]


def get_dfg(log, duration):
    total_time = 0.0
    if duration:
        start_time = time()
        new_dfg, _, _ = discover_dfg(log)
        enhance_dfg(new_dfg)
        total_time = time() - start_time
    else:
        new_dfg, _, _ = discover_dfg(log)
        enhance_dfg(new_dfg)
    global start_activities, end_activities
    start_activities = get_start_activities(df)
    end_activities = get_end_activities(df)
    return total_time


def check_df_read(new_df):
    if df.tail(1).reset_index(drop=True)[case_id].equals(new_df.head(1)[case_id]):
        return concat([df.tail(1), new_df], ignore_index=True)
    return new_df


def reading_from_file(filename, path):
    my_file = join(path, filename)
    if check_csv_file(my_file, True):
        dialect = get_csv_delimiter(my_file)
        if filename.split('.')[0] == "Saved_event_log" :
            return read_csv(my_file, dialect=dialect, index_col=0).rename(columns=from_csv_to_df)
        return read_csv(my_file, dialect=dialect).rename(columns=from_csv_to_df)
    return convert_to_dataframe(read_xes(my_file)).rename(columns={'event_attr: E:time:time':'time:timestamp'})


def from_log_to_dfg(filename, path, firstcall=True, duration=False):
    global df, dfg, start_activities, end_activities
    total_time = 0
    if firstcall:
        df = reading_from_file(filename, path)
        df.copy().rename(columns=from_df_to_csv).to_csv(join(path, "Saved_event_log.csv"))
        if duration:
            start_time = time()
            dfg, start_activities, end_activities = discover_dfg(df)
            total_time = time() - start_time
            return dfg, total_time   
        dfg, start_activities, end_activities = discover_dfg(df)
        return dfg, total_time
    
    new_df = reading_from_file(filename, path)
    log = check_df_read(new_df)
    df = concat([df, new_df], ignore_index=True)
    df.copy().rename(columns=from_df_to_csv).to_csv(join(path, "Saved_event_log.csv"))
    total_time = get_dfg(log, duration)
    return dfg, total_time


def get_incr_model(filename, path, n_files, total_dfg=None, duration=False, check=False):
    if total_dfg is None:
        total_dfg, _ = from_log_to_dfg(filename, path, duration)

    time = 0
    for i in range(1, n_files+1):
        _, t_int = from_log_to_dfg(filename[:-4] + "_{}".format(i) + filename[-4:], path, i == 1, duration)
        time += t_int
    
    if check:
        assert total_dfg == dfg, "Should be the same"
    
        saved_dfg, _ = from_log_to_dfg("Saved_event_log.csv", path)
        assert saved_dfg == total_dfg, "Should be the same"

    return dfg, time


if __name__ == "__main__":
    from sys import argv
    if len(argv) < 2 or len(argv) > 4:
        print("Error: number of input argument wrong ({}). Program terminates.".format(len(argv)))
        exit(0)

    print(relpath("log_data/event_log_choice_1_1000.csv"), "\n\n")
    get_incr_model("event_log_choice_1_1000.csv", "log_data/", 3)
    print("Funzione terminata\n")