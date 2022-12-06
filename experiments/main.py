""" 
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

from time import time
from my_utils import main_utils, check_path
from dfg_offline import get_incr_model, from_log_to_dfg


# def execution_function_times()

if __name__ == "__main__":
    from sys import argv
    if len(argv) < 12 or len(argv) > 14:
        print("Error: number of input argument wrong ({}). Program terminates.".format(len(argv)))
        exit(0)
    
    nruns = int(argv[10])
    path = "my_log_files/"
    filename = "filecsv.csv"
    if len(argv) > 12:
        if len(argv) == 14:
            path = argv[13]
        filename = argv[12]
    
    lists = []
    i = 0
    while i < 3:
        # i=0: n_traces in a file, i=1: n_events in each trace, i=2: split the file log in many little ones
        lists.append(range(int(argv[i*3+1]), int(argv[i*3+2])+1, int(argv[i*3+3])))
        i += 1
    
    save_times_path = check_path("times/")
    for n_traces in lists[0]:
        for n_events in lists[1]:
            main_utils([n_traces, n_events, argv[11], filename, path, lists[2][0]]) #argv[11] = str<events>
            # taking times (within and outside) for the whole file log
            t_start = time()
            dfg, t_incr_int = from_log_to_dfg(filename, path, duration=True)
            t_incr_ext = time() - t_start
            for i in range(1, nruns):
                t_start = time()
                _, t_int = from_log_to_dfg(filename, path, duration=True)
                t_incr_ext += time() - t_start
                t_incr_int += t_int
            times_ext = [t_incr_ext/nruns]
            times_int = [t_incr_int/nruns]

            # taking average times (within and outside)
            # the whole file log splitted in smaller files
            t_incr_int = 0
            t_incr_ext = 0
            for i in range(nruns):
                t_start = time()
                _, t_int = get_incr_model(filename, path, lists[2][0], dfg, True)
                t_incr_ext += time() - t_start
                t_incr_int += t_int
            times_int.append(t_incr_int/nruns)
            times_ext.append(t_incr_ext/nruns)

            for n_files in lists[2][1:]:
                main_utils([filename, path, n_files])
                t_incr_int = 0
                t_incr_ext = 0
                for i in range(nruns):
                    t_start = time()
                    _, t_int = get_incr_model(filename, path, n_files, dfg, True)
                    t_incr_ext += time() - t_start
                    t_incr_int += t_int
                times_int.append(t_incr_int/nruns)
                times_ext.append(t_incr_ext/nruns)

            # print("Lap {} made\n".format(n_files))
            with open("{}trs{}_evs{}.csv".format(save_times_path, n_traces, n_events), 'w', newline='') as f:
                from csv import writer
                writer = writer(f)

                writer.writerow(["n_traces", "n_events", "n_files", "total_func_time", "total_int_time"])
                writer.writerow([n_traces, n_events, 1, "%.4f" % times_ext[0], "%.4f" % times_int[0]])
                for index, n_files in enumerate(lists[2]):
                    writer.writerow([n_traces, n_events, n_files, "%.4f" % times_ext[index+1], "%.4f" % times_int[index+1]])