from time import time
from csv import writer
from os.path import join
from my_utils import main_utils, check_path
from dfg_offline import get_incr_model, from_log_to_dfg
from sys import argv

# taking times (within and outside) for either the whole file log
# or the n_files in which it is splitted    
def func(filename, path, iters, n_files = 1, dfg = None):
    if n_files > 1:
        t_incr_dfg = 0
        t_incr_func = 0
        i = 0

        while i < iters:
            t_start = time()
            _, t_int = get_incr_model(filename, path, n_files, dfg, True)
            t_incr_func += time() - t_start
            t_incr_dfg += t_int
            i += 1

    else:
        # despite the time variables name is misleading (t_incr_xxx),
        # here we use them to take times also on the total file log
                     
        t_start = time()
        dfg, t_incr_dfg = from_log_to_dfg(filename, path, duration=True)
        t_incr_func = time() - t_start
        i = 1
        while i < iters:
            t_start = time()
            _, t_int = from_log_to_dfg(filename, path, duration=True)
            t_incr_func += time() - t_start
            t_incr_dfg += t_int
            i += 1
    
    return t_incr_dfg/iters, t_incr_func/iters, dfg


if __name__ == "__main__":
    # check arguments and initialization variables and paths
    if len(argv) < 12 or len(argv) > 14:
        print("Error: number of input argument wrong ({}). Program terminates.".format(len(argv)))
        exit(0)
    
    nruns = int(argv[10])
    if nruns < 1:
        nruns = 1

    path = "exp/"
    filename = "filecsv.csv"
    if len(argv) > 12:
        if len(argv) == 14:
            path = argv[13]
        filename = argv[12]
    
    times_dir = check_path(join(path, "times/"))
    images_dir = check_path(join(path, "images/"))

    lists = []
    i = 0
    # lists[0]: number of traces in a log file,
    # lists[1]: number of events in each trace,
    # lists[2]: how many files the whole log file is splitted in
        
    while i < 3:
        lists.append(range(int(argv[i*3+1]), int(argv[i*3+2])+1, int(argv[i*3+3])))
        i += 1
    
    times_dfg = [0] * (len(lists[2])+1)
    times_func = [0] * (len(lists[2])+1)

    for n_events in lists[1]:
        type = 'w'
        for n_traces in lists[0]:
            main_utils([n_traces, n_events, argv[11], filename, path, lists[2][0]]) #argv[11] = str<events>
            times_dfg[0], times_func[0], dfg = func(filename, path, nruns)

            times_dfg[1], times_func[1], _ = func(filename, path, nruns, lists[2][0], dfg)
            
            for i, n_files in enumerate(lists[2][1:], 2):
                main_utils([filename, path, n_files])
                times_dfg[i], times_func[i], _ = func(filename, path, nruns, n_files, dfg)
                
            # print("Lap {} done\n".format(n_files))
            # print(times_dfg)

            with open("{}evs{}_times.csv".format(times_dir, n_events), type, newline='') as f:
                csv = writer(f)

                if type == 'w':
                    type = 'a'
                    csv.writerow(["n_traces", "n_files", "dfg_time", "func_time"])

                csv.writerow([n_traces, 1, "%.4f" % times_dfg[0], "%.4f" % times_func[0]])
                for index, n_files in enumerate(lists[2]):
                    csv.writerow([n_traces, n_files, "%.4f" % times_dfg[index+1], "%.4f" % times_func[index+1]])