import socket
import struct
import datetime
import logging
import threading

ICMP_ECHO_REQUEST = 8  # ICMP type for echo request

def calculate_icmp_checksum(icmp_packet):
    """
    Calculates the checksum of an ICMP packet.

    Args:
        icmp_packet (bytes): The ICMP packet data.

    Returns:
        int: The checksum value.
    """
    # Convert the packet data to a list of 16-bit words
    packet_words = [icmp_packet[i:i+2] for i in range(0, len(icmp_packet), 2)]

    # Calculate the checksum
    checksum = 0
    for word in packet_words:
        checksum += int.from_bytes(word, 'big')

    # Add the carry
    checksum = (checksum & 0xffff) + (checksum >> 16)

    # Negate the checksum
    checksum ^= 0xffff

    return checksum


def send_data(dest_ip, custom_data):

    custom_data = b"\\"+custom_data
    # Create ICMP packet with custom data
    icmp_packet = struct.pack('!BBHHH',
                              ICMP_ECHO_REQUEST,
                              socket.htons(0),
                              socket.htons(1),
                              len(custom_data),
                              0  # checksum placeholder
                              )+custom_data
    checksum = calculate_icmp_checksum(icmp_packet)
    # remake icmp packet
    icmp_packet = struct.pack('!BBHHH',
                              ICMP_ECHO_REQUEST,
                              socket.htons(0),
                              socket.htons(1),
                              len(custom_data),
                              checksum  # checksum placeholder
                              )+custom_data
    # Send the ICMP packet
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
    sock.sendto(icmp_packet, (dest_ip, 0))




def receive_data(dest_ip,func):
    # received_data = []

    # Create a raw socket for ICMP traffic
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    # Set the receive buffer size
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)

    # Receive ICMP packets
    while True:
        receive_time = datetime.datetime.now()
        # if datetime.timedelta.total_seconds(datetime.datetime.now() - start_time) > time_limit:
        #     return received_data
        data, addr = sock.recvfrom(1024)
        # receiver = threading.Thread(target=sock.recvfrom, args=(1024))
        # receiver.start()
        if addr[0] == dest_ip:
            func(addr,data,receive_time)


        # print(receiver.join(time_limit))
            



def receive_data_server(dest_ip):

    # Create a raw socket for ICMP traffic
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    # Set the receive buffer size
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)

    # Receive ICMP packets
    while True:
        data, addr = sock.recvfrom(1024)
        any_ip =  dest_ip == "*"
        if addr[0] == dest_ip or any_ip:
            # Parse the received ICMP packet
            icmp_header = struct.unpack_from('!BBHHH', data, 20)
            icmp_type = icmp_header[0]
            icmp_code = icmp_header[1]

            # Process the ICMP packet based on its type and code
            if icmp_type == 8:  # Echo Request
                yield (addr[0], data)
                


def send_custom_answer(dist_ip,custom_data):
    custom_data = b"\\"+custom_data

    # Create a raw socket for ICMP traffic
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    # Set the receive buffer size
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024)


    echo_reply = struct.pack('!BBHHH', 0, 0, 0, 5, 0)+custom_data
    echo_reply = struct.pack('!BBHHH', 0, 0, 0, 5, calculate_icmp_checksum(echo_reply))+custom_data
    sock.sendto(echo_reply, (dist_ip,0))
