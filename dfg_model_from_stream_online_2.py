from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.algo.discovery.dfg import algorithm as dfg_discovery
#from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.convert import convert_to_dataframe#, convert_to_event_stream
from pm4py.objects.log.obj import EventStream#, Event
from pm4py import discover_dfg, get_start_activities, get_end_activities#, view_dfg, read_xes
from pm4py.vis import save_vis_dfg
from pandas import read_csv, concat#, DataFrame 

display = True
show = False
images_path = "images/"
log_data_path = "log_data/"
HOST = "127.0.0.1"
PORT = 8192
encoding = "utf-8"
case_id = "case:concept:name"
activity = "concept:name"
timestamp = "time:timestamp"
from_csv_to_dfg = {"case":case_id, "activity":activity, "time":timestamp}
from_dfg_to_csv = {case_id:"case", activity:"activity", timestamp:"time"}

def enhance_dfg(new_dfg):
    global dfg
    if dfg is None:
        dfg = new_dfg
        print(dfg)
        print("Ma questo qua su?:/")
        return

    keys = dfg.keys()
    for edge in new_dfg.keys():
        if edge in keys:
            dfg[edge] += new_dfg[edge]
        else:
            dfg[edge] = new_dfg[edge]


def function(stream_dfg_disc, logs, copy = True):
    global total_log
    if total_log is None:
        total_log = convert_to_dataframe(EventStream(logs))
    else:
        total_log = concat([total_log, convert_to_dataframe(EventStream(logs))], ignore_index=True)
    
    if copy:
        total_log.copy().rename(columns=from_dfg_to_csv).to_csv(log_data_path + "Saved_event_log.csv", sep=';')
        return dict()
    
    dfg_stream, _, _, _ = stream_dfg_disc.get()
    total_log.rename(columns=from_dfg_to_csv).to_csv(log_data_path + "Saved_event_log.csv", sep=';')
    return dfg_stream


def check_string_arrived(s):
    index = s.find('&&&')

    # str not contains placeholder in the
    # exact place 
    if index == -1 or index != len(s) - 3:
        return s, False

    return s[:index], True


def log_stream_from_network(live_stream, stream_dfg_disc, window, png_filename):
    import socket
    logs = []
    i = 0
    # print(type(total_log.tail(1)))
    # print(total_log.loc[len(total_log)-1].at[case_id])
    if total_log is None:
        last_case = ''
    else:
        last_case = total_log.loc[len(total_log)-1].at[case_id]
    # print("\t\t", last_case)
    import sys
    if len(sys.argv) != 3:
        print("Errore! Numero di argomenti passati errato")
        sys.exit(-1)


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((sys.argv[1], int(sys.argv[2])))
        s.listen(1)
        print("Server ready...")
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}\n\n")
            live_stream.start()
            ss = ""
            while True:
                data = conn.recv(16)
                if not data:
                    print("Usciamo fuori")
                    break
                
                ss += data.decode(encoding)
                print(f"{'Reading data...':<20}", ss)
                event_str, complete = check_string_arrived(ss)
                if not complete:
                    continue

                ss = ""
                elems = event_str.split(';')
                index = int(elems[0])
                # print("\tInsert event log received:", index, "\n")
                event = {case_id: elems[1], activity: elems[2], timestamp: elems[3]}
                
                if event[case_id] != last_case:
                    last_case = event[case_id]
                    # print("!NUOVO CASE? -->", last_case, "con activity:", elems[2])
                    if len(logs) > 0:
                        # print("Case finito...\n")
                        function(stream_dfg_disc, logs)
                        # print("Ho creato nuovo dfg!\n")
                        logs = []
                        logs.append(event)
                        live_stream.append(event)
                        i = index
                        conn.sendall(event_str.encode(encoding))
                        continue        
                        # print("e qui?\n")
                
                live_stream.append(event)
                logs.append(event)
                # print("Adding new event...", type(logs))

                # finestra piena di eventi dello stesso case 
                if index - i == window:
                    # print("\tFinestra di eventi piena!")
                    function(stream_dfg_disc, logs)
                    # print("\nlog È lungo ", len(log_collected), "\n")
                    logs = []
                    i = index

                conn.sendall(event_str.encode(encoding))
                

            live_stream.stop()
            dfg_stream = function(stream_dfg_disc, logs, False)
            # print(dfg_stream)
            enhance_dfg(dfg_stream)
            # print(f"{'DFG TEST':^64}\n")
            global start_activities, end_activities
            start_activities = get_start_activities(total_log)
            end_activities = get_end_activities(total_log)
            save_vis_dfg(dfg, start_activities, end_activities, images_path + png_filename)
    

def execute_script(window = 8, png_filename = "prova.png"):
    live_stream = LiveEventStream()
    stream_dfg_disc = dfg_discovery.apply()
    live_stream.register(stream_dfg_disc)
    log_stream_from_network(live_stream, stream_dfg_disc, window, png_filename)
    

if __name__ == "__main__":
    global total_log, dfg, start_activities, end_activities
    from os.path import exists
    if exists(log_data_path + "prova"):
        total_log = read_csv(log_data_path + "prova.csv", sep=';').rename(columns = from_csv_to_dfg)
        dfg, start_activities, end_activities = discover_dfg(total_log)
        save_vis_dfg(dfg, start_activities, end_activities, images_path + "starting_event_log.png")
    else:
        total_log = None
        dfg = None

    execute_script()
    #display = True
    execute_script(4, "prova_finale.png")
    # print(f"\n\n{'TOTAL DFG':^64}\n")
    dfg_t, s_a, e_a = discover_dfg(read_csv(log_data_path + "New_event_log_2.csv", sep=';').rename(columns=from_csv_to_dfg))
    save_vis_dfg(dfg_t, s_a, e_a, images_path + "total_event_log_parsed.png")
    dfg_t, s_a, e_a = discover_dfg(read_csv(log_data_path + "Saved_event_log.csv", sep=';').rename(columns=from_csv_to_dfg))
    save_vis_dfg(dfg_t, s_a, e_a, images_path + "saved_event_log.png")
