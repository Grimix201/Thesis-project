""" 
!CONFRONTO FILE LOG vs MERGE FILE LOG!
#### Process Mining (singolo@Pm4Py, multiplo@Tuo) ok

#### Generazione di tracce randomiche ok

#### Experiments ok

python experiments.py 100 1000 100 5 20 5 2 10 2 ...

for n in range(100, 1001, 100):
    for t in range(5, 20, 5):
        ## Generazione di tracce randomiche 1 singole file [n, t]
        ## Tempo di Process Mining [singolo file] --> csv
        for s in range(2, 10, 2):
            ## Split singolo file in s file [singolo file, s]
            ## Tempo di Process Mining [s file] --> csv
        salvataggio file in directory
 """

from my_utils import main_utils, check_path
from dfg_offline import get_incr_model, from_log_to_dfg


if __name__ == "__main__":
    from sys import argv
    if len(argv) < 11 or len(argv) > 15:
        print("Error: number of input argument wrong ({}). Program terminates.".format(len(argv)))
        exit(0)
    
    nruns = 7
    path = "my_log_files/"
    filename = "filecsv.csv"
    if len(argv) > 11:
        if len(argv) == 14:
            path = argv[13]
        if len(argv) == 13:
            filename = argv[12]
        nruns = argv[11]
    
    lists = []
    i = 0
    while i < 3:
        # i=0: n_events in a file, i=1: n_traces in an event, i=2: split the file log in many little ones
        lists.append(range(int(argv[i*3+1]), int(argv[i*3+2])+1, int(argv[i*3+3])))
        i += 1
    
    save_times_path = check_path("times/")
    for n_events in lists[0]:
        for n_traces in lists[1]:
            main_utils([n_events, n_traces, argv[10], filename, path, lists[2][0]]) #argv[10] = str<events>
            dfg, time_single = from_log_to_dfg(filename, path, duration=True)
            # time start
            for i in range(0, nruns):
            _, time = get_incr_model(filename, path, lists[2][0], dfg, True)
            # time end
            time_n_files = [time]
            for n_files in lists[2][1:]:
                main_utils([filename, path, n_files])
                avg_ext_time = 0
                time_int = 0
                arr_time[]
                for i in range(0,nruns):
                    avg_time_start
                    _, time = get_incr_model(filename, path, n_files, dfg, True)
                    # _, tot_sav_time = from_log_to_dfg("saved_event_log", path, duration=True)
                    time_ext += avg_time_end 
                    time_int += time

                time_int_files.append(time_int/n)
                time_ext_files.append(time_ext/n)
                # print("Lap {} made\n".format(n_files))
            with open("{}ev{}_tr{}.csv".format(save_times_path, n_events, n_traces), 'w', newline='') as f:
                from csv import writer
                writer = writer(f)

                writer.writerow(["n_events", "n_traces", "n_files", "total_time"])
                writer.writerow([n_events, n_traces, 1, "%.4f" % time_single])
                for index, n_files in enumerate(lists[2]):
                    writer.writerow([n_events, n_traces, n_files, "%.4f" % time_n_files[index]])