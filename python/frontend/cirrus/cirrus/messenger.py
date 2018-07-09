import struct
import socket
import time

GET_NUM_CONNS = '\x08\x00\x00\x00'
GET_LAST_TIME_ERROR = '\x09\x00\x00\x00'
GET_ALL_TIME_ERROR = '\x0A\x00\x00\x00'


def get_num_lambdas(ip="127.0.0.1", port=1337):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        clientsocket.connect((ip, port))
        clientsocket.send(GET_NUM_CONNS)  # This sends an 8 to the param server, padded to 32 bytes
        s = clientsocket.recv(32)
        return struct.unpack("I", s)[0] - 1   # Subtract 1, as we don't count the clientsocket as a connection
    except:
        return 100

# FIXME: Add some sort of timeout, in case of error out
def get_last_time_error(ip="127.0.0.1", port=1338):
    #print("Loss: ", port)

    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientsocket.sendto(GET_LAST_TIME_ERROR, (ip, port))
    s = clientsocket.recv(128)
    out = struct.unpack("dd", s)
    #print("Received: ", out)
    return out

def get_all_time_error(ip="127.0.0.1", port=1338):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientsocket.sendto(GET_ALL_TIME_ERROR, (ip, port))
    s = clientsocket.recv(32)
    return "NOT IMPLEMENTED"
if __name__ == "__main__":

    while True:
        time.sleep(1)
        print(get_last_time_error("34.210.71.81", 1340))
        #print(get_last_time_error())
