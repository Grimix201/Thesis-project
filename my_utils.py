from csv import writer
from os.path import exists, join, basename, normpath
from os import getcwd, makedirs
from random import sample, choices
traces_input = "How many traces do you want to generate?\nFloat values are truncated to the whole part."
traces_error = "Error: you must enter a valid positive integer number"
traces_min_val = 0
events_input = "How many events do you want in each trace?"
events_error = "Error: you must enter a positive integer number greater than two(2)."
events_min_val = 2
file_ext = ".csv"


def get_csv_delimiter(csvfile):
    from csv import Sniffer
    with open(csvfile) as f:
        return Sniffer().sniff(f.read(1024))


def check_csv_file(file, existing=False):
    if basename(file).split('.')[-1] == file_ext[1:]:
        if existing:
            return exists(file)
        return True
    return False


def save_csv(filename, header, event_log):
    with open(filename, 'w', newline='') as f:
        write = writer(f)
        
        write.writerow(header)
        write.writerows(event_log)


def check_path(path):
    if not exists(path):
        makedirs(path, exist_ok=True)
    return path


def create_path():
    print("My current working directory is", getcwd())
    path = input("Where do you want to save your files?")
    path = normpath(join(getcwd(), path))
    if not (path.endswith('/') or path.endswith('\\')):
        path += '\\'
    
    return check_path(path)


def check(input_str, error_str, min_val, n=None):
    if n is not None:
        return n if n > min_val else min_val
        
    while True:
        n = input(input_str)
        if n.isdecimal() and int(n) > min_val:
            return int(n)
        
        print(error_str)
    

def collecting_events(events):
    if events is None:
        print("""Insert list of events that populate traces.
                Insert empty string to stop insert.""")
        i = 1
        events = []
        while True:
            val = input("Event {}: ".format(i))
            if val == "":
                if len(events) > 2:
                    break
                else:
                    print("Too few events to continue! Try adding some other events.")
                    continue
            
            if val in events:
                print("Error: event inserted already exists in the list. Retry")
                continue
            events.append(val)
            i += 1

    if type(events) is str:
         events = events.split(',')

    if len(events) >= events_min_val:
        start_activity = sample(events, 1)
        while True:
            end_activity = sample(events, 1)
            if end_activity != start_activity:
                # print(end_activity)
                events.remove(end_activity[0])
                return events, start_activity, end_activity
    print("Error: number of events non enough for create traces")
    exit(0)


def generate_traces(n_traces=None, n_events=None, events=None):
    n_traces = check(traces_input, traces_error, traces_min_val, n_traces)
    n_events = check(events_input, events_error, events_min_val, n_events)
    events, start_activity, end_activity = collecting_events(events)

    event_log = []
    for n_case in range(n_traces):
        trace_events = start_activity + choices(events, k=n_events - 2) + end_activity
        for index, elem in enumerate(trace_events):
            event_log.append([n_case + 1, elem[0], index + n_case * n_events])
    return event_log


def save_files(events, n_files, filename, path, header):
    n_events = len(events) / n_files
    i = 1
    start = 0
    while i < n_files:
        save_csv(join(path, basename(filename) + "_{}".format(i) + file_ext), header, events[round(start): round(start + n_events)])
        start += n_events
        i += 1
    save_csv(join(path, basename(filename) + "_{}".format(n_files) + file_ext), header, events[round(start):])
        

def save(log_file=[], filename="", path="", n_files=None):
    # print(filename, " - beginning of save...")
    if n_files is None:
        n_files = check("In how many files do you want to split your event log?", traces_error, 1)

    if path == "":
        path = create_path()
        # print(path)

    if filename == "":        
        filename = input("Digit only the name of the file without extension: ")
        
    if len(log_file) > 0:
        header = ["case", "activity", "time"]
        save_csv(join(getcwd(), path, filename) + file_ext, header, log_file) # total log file
        if n_files > 1:
            save_files(log_file, n_files, filename, path, header)
        return

    if n_files > 1:
        # print(filename)
        # print(join(path, filename))
        dialect = get_csv_delimiter(join(path, filename))
        with open((join(path, filename))) as f:
            from csv import reader
            csv = reader(f, dialect)
            my_list = list(csv)
        
        save_files(my_list[1:], n_files, filename[:-4], path, my_list[0])


def user_interaction():
    val = ""
    while True:
        val = input("""Which option do you select?
        1 - casual generation of traces and storing in one or more file/s;
        2 - insert a file name and split in more shorter files.
        Option: """)
        
        if val == '1' or val == '2':
            break
        
        print("Input not valid. Retry\n")
        
    if val == '1':
        log_file = generate_traces()
        save(log_file)
    else:
        while True:
            val = input("""Insert the file name you want to split.
            Only its name if it is in the same directory of this running program,
            the complete path if it is in a different directory, or the relative
            path if it is in a subdirectory where the running program is.\n>""")
            if exists(val):
                break
            print("Error: file not found. Retry")
        if check_csv_file(val, True):
            save(filename=val)
            return
        print("Error: file is not a csv. Program terminates.")


def main_utils(argv):
    if len(argv) == 0:
        user_interaction()
        return
    if len(argv) == 6:
        log_file = generate_traces(int(argv[0]), int(argv[1]), argv[2].split(','))
        path = check_path(argv[4])
        save(log_file, argv[3][:-4], path, int(argv[5]))
        return
    if len(argv) > 1:
        if check_csv_file(join(argv[1], argv[0])):
            if len(argv) == 3:
                save(filename=argv[0], path=argv[1], n_files=int(argv[2]))
            else:
                save(filename=argv[0], path=argv[1])
            return
        print("Error: path non valid. Program terminates.")
    else:
        print("Error: number of arguments passed from terminal wrong. Program terminates.")


if __name__ == "__main__":
    from sys import argv
    main_utils(argv[1:])