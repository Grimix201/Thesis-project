''' This script is needed only to plot results taken from the first experiment'''

from pandas import read_csv
from os.path import isfile, join
from os import getcwd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from sys import argv

# arguments check
if (len(argv) < 3 or len(argv) > 4): 
    print("Error: argument passed wrong!\nProgram terminates.")
    exit(0)

if not isfile(argv[1]):
    print("Error: file named", argv[1], "not exists!\nProgram terminates.")
    exit(0)

savefile = "image"
if len(argv) == 4:
    savefile = argv[3]

plt.rcParams["figure.figsize"] = [3.5, 7.5]
plt.rcParams["figure.autolayout"] = True

columns=argv[2].split(',')
# print("\nMy columns are:", columns,"\n")

df = read_csv(argv[1], usecols=columns)

# print(type(df), "\n" + df.head(10).to_markdown(index=False) + "\n")
uniques = df[columns[1]].unique()
# print("\n", type(uniques))
# print("\n", uniques, "\t", type(uniques[0]))

# plot data
# cmap = plt.colormaps["plasma"]
norm = Normalize(uniques[0], uniques[-1])

for i, dff in df.groupby(columns[1]):
    # plt.scatter(dff[columns[0]], dff[columns[2]], s=128, c=cmap(norm(dff[columns[1]])))
    plt.plot(dff[columns[0]], dff[columns[2]], marker='o', markersize=8, label=i)
    # color=cmap(norm(i)), \

font = {'fontsize' : 24}
plt.xlabel(columns[0], fontdict=font)
plt.ylabel("execution times (s)", fontdict=font)
plt.xticks(df.get(columns[0]))
plt.legend(loc="best")

plt.savefig(join(getcwd(), "images/")+savefile)
#plt.show()
