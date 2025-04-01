import socket
import struct
import random
import threading
import time

SLEEP = 10 #RTCP keepalive interval

def send_dummy_rtcp(service_ip: str, service_port: int, ssrc: int, source_port: int = 0) -> None:
    """
    Sends a dummy RTP packet to initialize the session stream and resends it every 10 seconds.
    :param service_ip: Destination IP for the RTCP stream.
    :param service_port: Destination port for the RTCP stream.
    :param ssrc: session id
    :param source_port: Optional source port to send the RTCP packets from (0 for random).
    """
    
    def create_rtcp_rr(ssrc: int) -> bytes:
        """
        Creates an RTCP Receiver Report (RR) packet identical to the Java implementation.
    
        :param ssrc: Synchronization Source (SSRC) identifier of the sender.
        :return: Bytes object containing the RTCP RR packet.
        """
        rtcp_rr = struct.pack(
            "!BBHIIIII",  # Now exactly 32 bytes (matching Java ByteBuffer.allocate(32))
            0x81,   # Version (2), Padding (0), Report Count (1)
            201,    # RTCP Packet Type: 201 (Receiver Report)
            7,      # Length in 32-bit words minus one
            ssrc,   # SSRC of sender
            0,      # SSRC of source being reported
            0,      # Fraction lost (8 bits) + Cumulative packet loss (24 bits)
            0,      # Extended highest sequence number received
            0,      # Interarrival jitter
            #0,      # Last Sender Report (LSR) timestamp
            #0       # Delay since last LSR
        )
    
        return rtcp_rr

    def send_packet():
        """Send RTP packet repeatedly every 10 seconds."""
        # Create a UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to a specific source port if provided (0 means let OS choose)
        try:
            sock.bind(("0.0.0.0", source_port))
            local_ip, assigned_port = sock.getsockname()  # Get the actual bound port
            print(f"🌐 Using source port: {assigned_port} (IP: {local_ip})")
        except Exception as e:
            print(f"❌ Failed to bind socket to port {source_port}: {e}")
            return

        # RTP Header Fields (Example Values)
 #       version = 2
 #       padding = 0
 #       extension = 0
 #       cc = 0
 #       marker = 0
 #       payload_type = 96  # Dynamic RTP type for video/audio
 #       sequence_number = random.randint(1000, 65535)  # Random sequence number
 #       timestamp = random.randint(100000, 999999)  # Random timestamp
 #       #ssrc = random.randint(1000000, 9999999)  # Random SSRC (Synchronization Source)
#
 #       # Construct RTP Header (First 12 bytes)
 #       rtp_header = struct.pack(
 #           "!BBHII",
 #           (version << 6) | (padding << 5) | (extension << 4) | cc,
 #           (marker << 7) | payload_type,
 #           sequence_number,
 #           timestamp,
 #           ssrc
 #       )
#
 #       # Dummy Payload (2 bytes of zeros)
 #       payload = b"\x00\x00"
#
 #       # Combine RTP Header + Payload
 #       rtp_packet = rtp_header + payload
        rtcp_rr_packet = create_rtcp_rr(ssrc)
        print(f">> RTCP RR Packet: {rtcp_rr_packet.hex()}")

        try:
            while True:
                # Send the packet to the destination IP & port
                sock.sendto(rtcp_rr_packet, (service_ip, service_port))
                print(f"✅ Dummy RTP packet sent to {service_ip}:{service_port} from {local_ip}:{assigned_port} for SSRC:{ssrc}")

                # Wait for 10 seconds before sending the next packet
                time.sleep(SLEEP)

        except Exception as e:
            print(f"\n❌ Failed to send RTP packet: {e}\n")

        finally:
            # Close the socket
            sock.close()

    # Start the packet-sending function in a background thread
    thread = threading.Thread(target=send_packet)
    thread.daemon = True  # Ensure the thread ends when the main program exits
    thread.start()

    print(f"\n🎯 Background thread started to send dummy RTP packets to {service_ip}:{service_port}")
