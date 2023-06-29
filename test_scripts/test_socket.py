import socket
import datetime

message = f"00dv=all,{datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S')};"

target_ip = '255.255.255.255'
target_port = 8888

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(message.encode(), (target_ip, target_port))
sock.settimeout(5)

while True:
    try:
        data, addr = sock.recvfrom(1024)
        raw_result = data.decode()
        print("Raw Result:", raw_result)
    except socket.timeout:
        print("Socket timeout occurred.")
        break

sock.close()
