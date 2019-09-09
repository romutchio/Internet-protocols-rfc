import socket
import time
from concurrent.futures import ThreadPoolExecutor
from socket import socket, AF_INET, SOCK_DGRAM
from struct import pack, unpack, Struct


TIME_1970 = 2208988800
'''

Наименование	Код	Когда генерируется
Начальное время	Т1	Время отправки запроса клиентом
Время приёма	Т2	Время приёма запроса сервером
Время отправки	Т3	Время отправки ответа сервером
Время прибытия	Т4	Время приёма ответа клиентом

Timestamp Name          ID   When Generated
------------------------------------------------------------
Originate Timestamp     T1   time request sent by client
Receive Timestamp       T2   time request received at server
Transmit Timestamp      T3   time reply sent by server
Destination Timestamp   T4   time reply received at client

В качестве текущего времени устанавливается значение Т4 с поправкой на сдвиг локального времени. 
Сдвиг локального времени t и задержка передачи пакетов d вычисляется по формулам:

d = (Т4 – T3) + (T2 – T1)
t = ((Т2 – Т1) + (Т3 – Т4)) / 2

http://www.netping.ru/Blog/chem-otlichaetsya-protokol-sinhronizatsii-vremeni-ntp-ot-sntp

'''


class SNTP_Server:
    def __init__(self, delay):
        self.delay = delay
        self.port = 123
        self.sock = socket(AF_INET, SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', self.port))

        self.leap_indicator = 0
        self.version_number = 4
        self.mode = 4
        self.stratum = 3
        self.pool = 0
        self.precision = 0
        self.root_delay = 0
        self.root_dispersion = 0
        self.reference_id = b'0000'

    def run(self):
        print('Listening on {}'.format(self.port))
        pool = ThreadPoolExecutor(128)

        while True:
            data, addr = self.sock.recvfrom(1024)
            pool.submit(self.handle, data, addr)

    def handle(self, data, addr):
        start_time = unpack('!BBBBII4sQQQQ', data)[10]
        timestamp = self.get_timestamp()
        packet = self.build_packet(start_time, timestamp)
        self.sock.sendto(packet, addr)
        print('Sent a packet to {}.'.format(addr))

    def get_timestamp(self):
        return int((TIME_1970 + time.time() + self.delay) * (2 ** 32))

    def build_packet(self, start_time, timestamp):
        packet = Struct('!BBBBII4sQQQQ').pack(
            0b00100100,
            self.stratum,
            self.pool,
            self.precision,
            self.root_delay,
            self.root_dispersion,
            self. reference_id,
            self.get_timestamp(),  # reference timestamp
            start_time,  # originate timestamp
            timestamp,  # receive timestamp
            self.get_timestamp())  # transmit timestamp
        return packet


def main():
    with open('delay.txt', 'r') as f:
        delay = int(f.read())
    server = SNTP_Server(delay)
    server.run()


if __name__ == '__main__':
    main()
