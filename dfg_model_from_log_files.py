from os.path import basename
from re import split
from pandas import read_csv, concat
from pm4py import discover_dfg, get_start_activities, get_end_activities, view_dfg, read_xes, convert_to_dataframe

flag = True
case_id = "case:concept:name"
activity = "concept:name"
timestamp = "time:timestamp"
from_csv_to_df = {"case" : case_id, "activity" : activity, "time" : timestamp}


def enhance_dfg(new_dfg):
    global dfg
    keys = dfg.keys()
    for edge in new_dfg.keys():
        if edge in keys:
            dfg[edge] += new_dfg[edge]
        else:
            dfg[edge] = new_dfg[edge]


def get_dfg(log):
    new_dfg, _, _ = discover_dfg(log)
    enhance_dfg(new_dfg)
    global start_activities, end_activities
    start_activities = get_start_activities(df)
    end_activities = get_end_activities(df)


def check_df_read(new_df):
    if df.tail(1).reset_index(drop=True)[case_id].equals(new_df.head(1)[case_id]):
        return concat([df.tail(1), new_df], ignore_index=True)
    return new_df


def reading_from_file(file, index_col = None):
    file_elems = split(pattern=r'\.', string=basename(file))
    if file_elems[-1] == "csv" :
        if file_elems[0] == "Saved_event_log" :
            index_col = 0
        return read_csv(file, sep=';', index_col = index_col).rename(columns = from_csv_to_df)
    return convert_to_dataframe(read_xes(file)).rename(columns={'event_attr: E:time:time':'time:timestamp'})


def from_log_to_dfg(file_path):
    global flag, df, dfg, start_activities, end_activities
    if flag:
        df = reading_from_file(file_path)
        print(df.head(20).to_markdown())
        dfg, start_activities, end_activities = discover_dfg(df)
        flag = not flag
        return dfg
    
    new_df = reading_from_file(file_path)
    log = check_df_read(new_df)
    df = concat([df, new_df], ignore_index=True)
    get_dfg(log)
    df.to_csv("Saved_event_log.csv", sep=';')

    # print("#start activities: {}\n#end activities: {}".format(start_activities, end_activities))
    # print(f"{'visualizing DFG model':^64}\n")
    # view_dfg(dfg, start_activities, end_activities)
    # print("\n\n")
    

def setFlag():
    global flag
    flag = True


def main():
    # if __name__ == "__main__":
    setFlag()
    # print(f"\n\n{'parsing csv file log':64}\n\n")
    total_dfg = from_log_to_dfg("event_log_choice_1_1000.csv")
    # setFlag()
    # print(f"\n\n{'parsing xes file log':64}\n\n")
    # from_log_to_dfg("event_log_choice_1_1000.xes")
    setFlag()
    # print(f"\n\n{'parsing different file logs':64}\n\n")
    for i in range(1, 3):
        from_log_to_dfg("event_log_choice_1_1000.csv")
    assert total_dfg == dfg, "Should be the same"
    setFlag()
    # print(f"\n\n{'parsing saved file log':64}\n\n")
    # saved_dfg = from_log_to_dfg("Saved_event_log.csv")
    # assert saved_dfg == dfg, "Should be the same"