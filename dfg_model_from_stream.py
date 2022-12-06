from os.path import basename
from os import remove, rename
from re import split
from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.convert import convert_to_event_stream, convert_to_dataframe
from pm4py.objects.log.obj import EventStream
from pm4py import discover_dfg, view_dfg, read_xes, get_start_activities, get_end_activities
from pandas import DataFrame, read_csv, concat

display = False
show = False
HOST = "127.0.0.1"
PORT = 8192
case_id = 'case:concept:name'
from_csv_to_dfg = {'case':case_id, 'activity':'concept:name', 'time':'time:timestamp'}
from_dfg_to_csv = {case_id:'case', 'concept:name':'activity', 'time:timestamp':'time'}


def reading_from_file(file):
    if split(pattern=r'\.', string=basename(file))[-1] == "csv" :
        df = read_csv(file, sep=';').rename(columns = from_csv_to_dfg)
    else:
        df = convert_to_dataframe(read_xes(file)).rename(columns={'event_attr: E:time:time':'time:timestamp'})
    return convert_to_event_stream(df)


def enhance_dfg():
    global dfg
    keys = dfg.keys()
    for edge in dfg_stream.keys():
        if edge in keys:
            dfg[edge] += dfg_stream[edge]
        else:
            dfg[edge] = dfg_stream[edge]
    #print(dfg)


def dfg_production(stream):
    global dfg_stream
    dfg_stream, _, _, _ = stream.get()
    if display:
        print(dfg_stream)
    #enhance_dfg(dfg_stream)
    global start_activities, end_activities
    start_activities = get_start_activities(total_log)
    end_activities = get_end_activities(total_log)
    
    # if show:
    #     print(f"{'DFG TEST':^64}\n")
    #     view_dfg(dfg, start_activities, end_activities)
    #     print("\n\n")
 

def function(stream_dfg_disc, log, copy = True):
    toAppend = convert_to_dataframe(EventStream(log))
    # print(type(toAppend))
    global total_log
    total_log = concat([total_log, toAppend], ignore_index=True)
    dfg_production(stream_dfg_disc)
    if copy:
        total_log.copy().rename(columns=from_dfg_to_csv).to_csv("Saved_event_log.csv", sep=';')
    else:
        total_log.rename(columns=from_dfg_to_csv).to_csv("Saved_event_log.csv", sep=';')


def log_stream_from_file(event_log, live_stream, stream_dfg_disc, window):
    print("In log_stream_from_file, df is", type(event_log))
    log = []
    i = 0
    # print(event_log[0][case_id])
    last_case = event_log[0][case_id]
    live_stream.start()
    

    # fase processazione eventi:
    for index, event in enumerate(event_log, start = 1):
        if index == 1:
            print(type(event))#, "\n-", event, "\n--", event["case:concept:name"])

        if len(log) != 0 and event[case_id] != last_case:
            # print("Case finito...\n")
            function(stream_dfg_disc, log)
            log = []
            log.append(event)
            live_stream.append(event)
            last_case = event[case_id]
            i = index
            continue
        # else:
        live_stream.append(event)
        log.append(event)
        # print("Adding new event...", type(log))

        # finestra piena di eventi dello stesso case 
        if index - i == window:
            print("\tFinestra di eventi piena!")
            function(stream_dfg_disc, log)
            # print("\nlog È lungo ", len(log), "\n")
            log = []
            i = index

    live_stream.stop()
    function(stream_dfg_disc, log, True)
    enhance_dfg()
    print(f"{'DFG TEST':^64}\n")
    view_dfg(dfg, start_activities, end_activities)
    print("\n\n")


# passare parametri come argomento programma da linea di comando
def execute_script(file_path = '', window = 8):
    live_stream = LiveEventStream()
    stream_dfg_disc = dfg_discovery.apply()
    live_stream.register(stream_dfg_disc)

    event_log = reading_from_file(file_path)
    print("Event_log type =", type(event_log))
    log_stream_from_file(event_log, live_stream, stream_dfg_disc, window)


    # remove("Starting_event_log.csv")
    # rename("Saved_event_log.csv", "Starting_event_log.csv")


if __name__ == "__main__":
    global total_log
    total_log = read_csv("Starting_event_log.csv", sep=';').rename(columns = from_csv_to_dfg)
    global dfg, start_activities, end_activities
    dfg, start_activities, end_activities = discover_dfg(total_log)

    print(f"{'INITIAL DFG ':^64}\n")
    view_dfg(dfg, start_activities, end_activities)
    print("\n\n")
    execute_script("New_event_log.csv")
    display = True
    execute_script("New_event_log_2.csv", 4)
    print(f"\n\n{'TOTAL DFG':^64}\n")
    view_dfg(dfg, start_activities, end_activities)    
    dfg_t, s_a, e_a = discover_dfg(read_csv("event_log_choice_1_1000.csv", sep=';').rename(columns=from_csv_to_dfg))
    print(f"\n\n{'DFG FROM ORIGINAL CSV FILE':^64}\n")
    view_dfg(dfg_t, s_a, e_a)
    dfg_t, s_a, e_a = discover_dfg(read_csv("Saved_event_log.csv", sep=';').rename(columns=from_csv_to_dfg))
    print(f"\n\n{'DFG FROM EVENT LOGS GATHERED':^64}\n")
    view_dfg(dfg_t, s_a, e_a)