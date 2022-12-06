from pandas import DataFrame, read_csv, concat
import socket

encoding = "utf-8"

import sys
# from keyboard import wait
if len(sys.argv) != 4:
    print("Errore! Numero di argomenti passati errato")
    sys.exit(-1)

HOST = sys.argv[2]  # The server's hostname or IP address
PORT = int(sys.argv[3])  # The port used by the server



with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    sending_log = read_csv(sys.argv[1], sep=';')
    # print(sending_log.head(20).to_markdown())
    # print(f"{'FOREACH':^64}\n")
    ss = ""
    last_case = sending_log.at[0, "case"]
    for index, row in sending_log.iterrows():
        #print(index, row['case'], row['activity'], row['time'])
        
        if row[0] != last_case:
            ss += "&&&"
            s.sendall(ss.encode(encoding))
            data = s.recv(1024)
            # print(f"{'Received data:':<20}", index, data.decode(encoding))
            # wait('enter')
            last_case = row[0]
            ss = ""

        ss += f"{index};{row[0]};{row[1]};{row[2]}***"
        # print(len(ss))

    # per invio ultima traccia
    ss += "&&&"
    s.sendall(ss.encode(encoding))
    data = s.recv(1024)
        
    s.sendall(b'')
    print("Connessione chiusa")

#Limitazioni: dati ricevuti senza problemi, tracce generate senza bug
