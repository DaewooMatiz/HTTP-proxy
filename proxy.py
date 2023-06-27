import sys, socket
from concurrent.futures import thread

BACKLOG = 50
MAX_DATA_RECV = 999999
DEBUG = True
BLOCKED = []



def main():
    if (len(sys.argv) < 2):
        print
        "NO PORT GIVEN"
        port = 8080
    else:
        port = int(sys.argv[1])  # port from argument

    host = ''

    print
    "PROXY STARTED, RUNNING ON ", host, ":", port

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(BACKLOG)

    except socket.error as (value, message):
        if s:
            s.close()
        print
        "COULDN't OPEN SOCKET", message
        sys.exit(1)

    while 1:
        conn, client_addr = s.accept()
        thread.start_new_thread(proxy_thread, (conn, client_addr))

    s.close()

def printout(type, request, address):
    if "Block" in type or "Blacklist" in type:
        colornum = 91
    elif "Request" in type:
        colornum = 92
    elif "Reset" in type:
        colornum = 93

    print
    "\033[", colornum, "m", address[0], "\t", type, "\t", request, "\033[0m"

def proxy_thread(conn, client_addr):
    request = conn.recv(MAX_DATA_RECV)
    first_line = request.split('\n')[0]
    url = first_line.split(' ')[1]

    for i in range(0, len(BLOCKED)):
        if BLOCKED[i] in url:
            printout("Blacklisted", first_line, client_addr)
            conn.close()
            sys.exit(1)

    printout("Request", first_line, client_addr)
    http_pos = url.find("://")
    if (http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos + 3):]

    port_pos = temp.find(":")
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos):
        port = 80
        webserver = temp[:webserver_pos]
    else:
        port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
        webserver = temp[:port_pos]

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(request)

        while 1:
            data = s.recv(MAX_DATA_RECV)

            if (len(data) > 0):
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except socket.error as (value, message):
        if s:
            s.close()
        if conn:
            conn.close()
        printout("Peer Reset", first_line, client_addr)
        sys.exit(1)

if __name__ == '__main__':
    main()
