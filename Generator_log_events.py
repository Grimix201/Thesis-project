from pandas import DataFrame, read_csv, concat
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 8192  # The port used by the server
encoding = "utf-8"

from platform import system
print(system())
import sys
# len = len(sys.argv)
# if len < 2 and len > 5:
#     print("Errore! Argomenti passati in input non validi\nDevi passare nell'ordine:\n - file csv;\n - indice inizio raccolta log; (opzionale)\n - indice fine raccolta log. (opzionale)")
#     sys.exit(-1)

# start = 0
# stop = None
# if len > 2:
#     if len == 4:
#         stop = int(sys.argv[3]) + 1
#     start = int(sys.argv[2])
from time import sleep

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    sending_log = read_csv(sys.argv[1], sep=';')#[start:stop]
    #select_log = sending_log[:20]
    print(sending_log.head(20).to_markdown())
    # s.sendall(b"Hello, world")
    # data = s.recv(1024)
    print(f"{'FOREACH':^64}\n")
    for index, row in sending_log.iterrows():
        #print(index, row['case'], row['activity'], row['time'])
        ss = f"{index};{row[0]};{row[1]};{row[2]}&&&"
        #print(ss)
        s.sendall(ss.encode(encoding))
        data = s.recv(128)
        print(f"{'Received data:':<20}", index, data.decode(encoding))
        sleep(5)
    s.sendall(b'')
    print("Connessione chiusa")
