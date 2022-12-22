import matplotlib.pyplot as plt
from time import time
from os.path import join
from my_utils import main_utils, check_path
from dfg_offline import from_log_to_dfg
import dfg_offline as m


if __name__ == "__main__":
    from sys import argv
    if len(argv) < 6 or len(argv) > 8:
        print("Error: number of input argument wrong ({}). Program terminates.".format(len(argv)))
        exit(0)

    # initialization of variables and paths
    n_traces = int(argv[1])
    n_events = int(argv[2])
    n_files = int(argv[3])
    nruns = int(argv[4])

    path = "exp2/"
    filename = "filecsv.csv"
    img_filename = "image"
    if len(argv) > 6:
        if len(argv) == 8:
            path = argv[7]
        filename = argv[6]
    
    times_dir = check_path(join(path, "times/"))
    images_dir = check_path(join(path, "images/"))
    # print(times_dir,"\n")

    # generating pseudo-event log divided then in tot files
    main_utils([n_traces, n_events, argv[5], filename, path, n_files]) #argv[5]=str<events>
    
    # recording times of both single and total logs
    # nruns times
    i = 0
    t_single_logs = []
    t_total_logs = []
    
    while i < n_files:
        i += 1
        ith_filename = filename[:-4] + f"_{i}" + filename[-4:]    
        t_single = 0
        t_total = 0
        # print(join(path, filename))

        for t in range(nruns):
            
            # restoring backuped dataframe and dfg 
            # after first iteration to get correct results
            if i > 1 and t:
                m.df = backup_df
                m.dfg = backup_dfg 

            _, t_int = from_log_to_dfg(ith_filename, path, i == 1, True)
            t_single += t_int
            _, t_int = from_log_to_dfg("Saved_event_log.csv", path, duration=True)
            t_total += t_int

        t_single_logs.append(t_single / nruns)
        t_total_logs.append(t_total / nruns)


        # because df and dfg variables are global
        # and after the first iteration, at each
        # function call we have to restore starting
        # point for subsequent iterations
        if i != n_files:
            backup_df = m.df
        backup_dfg = m.dfg
        # print(backup_dfg)
    
    total_dfg, _ = from_log_to_dfg(filename, path)
    assert total_dfg == backup_dfg

    # saving times previously recorded in a file
    xs = range(1, n_files+1)
    with open(f"{times_dir}times.csv", 'w', newline='') as f:
        from csv import writer
        writer = writer(f)

        writer.writerow(["file_number", "total_log_time", "single_log_time"])
        for i in xs:
            writer.writerow([i, "%.4f" % t_total_logs[i-1], "%.4f" % t_single_logs[i-1]])
    
    # plot times
    plt.rcParams["figure.figsize"] = [12, 6]
    plt.rcParams["figure.autolayout"] = True
 
    plt.scatter(xs, t_total_logs, s=128, marker='.')
    plt.scatter(xs, t_single_logs, s=128, marker='x')
    
    plt.xlabel("file_number", fontdict={'fontsize' : 24})
    plt.ylabel("execution times (s)", fontdict={'fontsize' : 24})
    plt.legend(["total_log", "single_log"])
    plt.xticks(xs)

    plt.savefig(f"{images_dir}plot_exp2")