#
# class Packet:
#     def __init__(self, delay):
#         self.frac = 2 ** 32
#         self.packet_format = '!B B B b 11I'
#         self.current_time = TIME_1970 + time.time() + delay
#         self.leap_indicator = 0
#         self.version_number = 4
#         self.mode = 4
#         self.stratum = 2
#         self.pool = 10
#         self.precision = 0
#         self.root_delay = 0
#         self.root_dispresion =  0x0aa7
#         self.reference_identifier = 0x808a8c2c
#         self.reference_timestamp = \
#             self.originate_timestamp = \
#             self.receive_timestamp = \
#             self.transmit_timestamp = \
#             self.current_time
#
#     def pack_to_bytes(self):
#         indicator = self.leap_indicator << 6
#         version = self.version_number << 3
#         return struct.pack(self.packet_format,
#                            (indicator | version | self.mode),
#                            self.stratum,
#                            self.pool,
#                            self.precision,
#                            self.root_delay,
#                            self.root_dispresion,
#                            self.reference_identifier,
#
#                            int(self.reference_timestamp),
#                            self.to_fraction_part(self.reference_timestamp),
#
#                            int(self.originate_timestamp),
#                            self.to_fraction_part(self.originate_timestamp),
#
#                            int(self.receive_timestamp),
#                            self.to_fraction_part(self.receive_timestamp),
#
#                            int(self.transmit_timestamp),
#                            self.to_fraction_part(self.transmit_timestamp)
#                            )
#
#     def to_fraction_part(self, cur_time):
#         """Convert the fractional part of current time"""
#         return int(abs(cur_time - int(cur_time)) * self.frac)
#
#
# def main_loop(sock, delay):
#     while 1:
#         data, addr = sock.recvfrom(1024)
#         print(f'Connected from {addr}')
#         packet = Packet(delay)
#         sock.sendto(packet.pack_to_bytes(), addr)
#
#
# def main():
#     with open('delay.txt', 'r') as f:
#         delay = int(f.read())
#
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind(('localhost', 123))
#     main_loop(sock, delay)
#
#
# if __name__ == '__main__':
#     main()
