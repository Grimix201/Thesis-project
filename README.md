# Thesis-project

This is a project written in Python about developing a model in an incremental way from data log collected from files or as stream based on the process mining library PM4PY.

## How to install

The following programs/packages are requested to use this project:
- if you haven't installed yet on your machine, install Python (https://www.python.org) version 3.7 or later.
  Here (https://realpython.com/installing-python/) is a guide to install it;
- the PM4PY library (https://pm4py.fit.fraunhofer.de/) (version used: 2.2.32 (legacy)); 

## How to run

### Scripts

To run the scripts, open the terminal, move to the project directory and then insert this command:

```bash
-$ python dfg_offline.py <CSV/XES_filename> <path_to_XES/CSV_files> <n_files_to_use>
```

for the offline tool, or insert this command:

```bash
-$ python dfg_online.py <HOST> <PORT>
```

for the online tool.

### Scripts

To run the experiments, done using the offline version, move to the experiments directory and then insert this command:

```bash
-$ python experiments.py <t1> <t2> <t3> <T1> <T2> <T3> <tt1> <tt2> <tt3> <repetitions> <comma-separated list of activities> [filename, [path]]
```

for run the first experiment. The ts, Ts and tts are triplets corresponding to minimum (1), maximum(2), and additive step(3) to respectively
  - number of cases/traces in a data log,
  - number of activities/events composing each case,
  - number of files in which splitting the generated data log.

To run the second experiment, in the experiments directory type in the terminal the following command:

```bash
-$ python experiments2.py <n_cases> <n_events> <n_files> <repetitions> <comma-separated list of activities> [filename, [path]]
```

to run the second experiment.
