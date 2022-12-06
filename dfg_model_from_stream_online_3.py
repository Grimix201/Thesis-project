from pm4py.streaming.stream.live_event_stream import LiveEventStream
from pm4py.streaming.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.convert import convert_to_event_stream, convert_to_dataframe
from pm4py.objects.log.obj import EventStream, Event
from pm4py import discover_dfg, view_dfg, read_xes, get_start_activities, get_end_activities
from pm4py.vis import save_vis_dfg
from pandas import DataFrame, read_csv, concat

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
arr = []

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


def log_stream_from_network(conn, addr, window = 8, png_filename = "prova.png"):
    live_stream = LiveEventStream()
    stream_dfg_disc = dfg_discovery.apply()
    live_stream.register(stream_dfg_disc)
    
    if total_log is None:
        last_case = ''
    else:
        last_case = total_log.loc[len(total_log)-1].at[case_id]
    
    with conn:
        print(f"Connected by {addr}\n\n")
        logs = []
        i = 0
        ss = ""
        live_stream.start()
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
            event = {case_id: elems[1], activity: elems[2], timestamp: elems[3]}
            
            if event[case_id] != last_case:
                last_case = event[case_id]
                # print("!NUOVO CASE? -->", last_case, "con activity:", elems[2])
                if len(logs) > 0:
                    function(stream_dfg_disc, logs)
                    logs = []
                    i = index
                    logs.append(event)
                    live_stream.append(event)
                    conn.sendall(event_str.encode(encoding))
                    continue        
            
            live_stream.append(event)
            logs.append(event)
            
            # finestra piena di eventi dello stesso case 
            if index - i == window:
                function(stream_dfg_disc, logs)
                logs = []
                i = index

            conn.sendall(event_str.encode(encoding))

        live_stream.stop()
        dfg_stream = function(stream_dfg_disc, logs, False)
        enhance_dfg(dfg_stream)
        global start_activities, end_activities
        start_activities = get_start_activities(total_log)
        end_activities = get_end_activities(total_log)
        save_vis_dfg(dfg, start_activities, end_activities, images_path + png_filename)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 4:
        print("Errore! Numero di argomenti passati errato")
        sys.exit(-1)

    if len(sys.argv) > 1:
        if len(sys.argv) > 2:
            if len(sys.argv) == 4:
                PORT = int(sys.argv[3])
            HOST = sys.argv[2]
        window = int(sys.argv[1])

    global total_log, dfg, start_activities, end_activities
    from os.path import exists
    if exists(log_data_path + "Starting_event_log.csv"):
        total_log = read_csv(log_data_path + "starting_event_log.csv", sep=';').rename(columns = from_csv_to_dfg)
        dfg, start_activities, end_activities = discover_dfg(total_log)
        save_vis_dfg(dfg, start_activities, end_activities, images_path + "starting_event_log.png")
    else:
        total_log = None
        dfg = None

    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        while True:
            print("Server ready...")
            conn, addr = s.accept()
            conn.settimeout(20.0)
            log_stream_from_network(conn, addr)