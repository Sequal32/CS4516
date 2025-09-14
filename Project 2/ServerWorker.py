from random import randint
import sys, traceback, threading, socket

from VideoStream import VideoStream
from RtspPacket import RtspMethod, RtspRequest, RtspResponse, RtspStatus
from RtpPacket import RtpPacket


class ServerWorker:
    SETUP = "SETUP"
    PLAY = "PLAY"
    PAUSE = "PAUSE"
    TEARDOWN = "TEARDOWN"

    INIT = 0
    READY = 1
    PLAYING = 2
    state = INIT

    OK_200 = 0
    FILE_NOT_FOUND_404 = 1
    CON_ERR_500 = 2

    clientInfo = {}

    def __init__(self, clientInfo):
        self.clientInfo = clientInfo

    def run(self):
        threading.Thread(target=self.recvRtspRequest).start()

    def recvRtspRequest(self):
        """Receive RTSP request from the client."""
        connSocket = self.clientInfo["rtspSocket"][0]
        while True:
            try:
                data = connSocket.recv(256).decode()
            except ConnectionResetError:
                print("xy: Connection reset by peer")
            if data:
                print("Data received:\n" + data)
                self.processRtspRequest(data)

    def processRtspRequest(self, data):
        """Process RTSP request sent from the client."""
        # Get the request type
        request = RtspRequest.decode(data)

        print("xy request in ServerWorker: ", request)


        seq = request.get_header("CSeq")

        if seq is None:
            raise ValueError("CSeq header is missing")

        # Get the RTSP sequence number
        print("xy seq in ServerWorker: ", seq)

        # Process SETUP request
        if request.method() == RtspMethod.SETUP:
            if self.state == self.INIT:
                # Update state
                print("processing SETUP\n")

                try:
                    self.clientInfo["videoStream"] = VideoStream(request.filename())
                    self.state = self.READY

                    # Generate a randomized RTSP session ID
                    self.clientInfo["session"] = randint(100000, 999999)

                    # Send RTSP reply
                    self.replyRtsp(self.OK_200, seq)

                    # Get the RTP/UDP port used by client from the last line of client request
                    #
                    transport = request.get_header("Transport")

                    if transport is None:
                        raise ValueError("Transport header is missing")

                    # Parse port from transport
                    port_str = transport.split("client_port=")[1]

                    print("xy: found port string", port_str)

                    self.clientInfo['rtpPort'] = int(port_str)
                    print("xy: self.clientInfo['rtpPort']", self.clientInfo["rtpPort"])

                except IOError:
                    self.replyRtsp(self.FILE_NOT_FOUND_404, seq)

        # Process PLAY request
        elif request.method() == RtspMethod.PLAY:
            if self.state == self.READY:
                print("processing PLAY\n")
                self.state = self.PLAYING

                # Fill in start
                # Create a new socket for RTP based on UDP
                self.clientInfo["rtpSocket"] = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Fill in end

                self.replyRtsp(self.OK_200, seq)

                # Create a new thread and start sending RTP packets
                self.clientInfo["event"] = threading.Event()
                self.clientInfo["worker"] = threading.Thread(target=self.sendRtp)
                self.clientInfo["worker"].start()

        # Process PAUSE request
        elif request.method() == RtspMethod.PAUSE:
            if self.state == self.PLAYING:
                print("processing PAUSE\n")
                self.state = self.READY

                # self.clientInfo['event'].set()
                # Handle the error gracefully, such as logging the error or notifying the user
                if "event" in self.clientInfo:
                    self.clientInfo["event"].set()
                else:
                    print(
                        "xy Error: 'event' key does not exist in clientInfo dictionary"
                    )

                self.replyRtsp(self.OK_200, seq)

        # Process TEARDOWN request
        elif request.method() == RtspMethod.TEARDOWN:
            print("processing TEARDOWN\n")

            # Handle the error gracefully, such as logging the error or notifying the user
            if "event" in self.clientInfo:
                self.clientInfo["event"].set()
            else:
                print("xy Error: 'event' key does not exist in clientInfo dictionary")

            self.replyRtsp(self.OK_200, seq)

            # Close the RTP socket
            # Handle the error gracefully, such as logging the error or notifying the user
            if "rtpSocket" in self.clientInfo:
                self.clientInfo["rtpSocket"].close()
            else:
                print(
                    "xy Error: 'rtpSocket' key does not exist in clientInfo dictionary"
                )

    def sendRtp(self):
        """Send RTP packets over UDP."""
        while True:
            self.clientInfo["event"].wait(0.05)

            # Stop sending if request is PAUSE or TEARDOWN
            if self.clientInfo["event"].isSet():
                break

            data = self.clientInfo["videoStream"].nextFrame()
            if data:
                frameNumber = self.clientInfo["videoStream"].frameNbr()
                try:
                    address = self.clientInfo["rtspSocket"][1][0]
                    port = int(self.clientInfo["rtpPort"])
                    self.clientInfo["rtpSocket"].sendto(
                        self.makeRtp(data, frameNumber), (address, port)
                    )
                except:
                    print("Connection Error")
                    # print '-'*60
                    # traceback.print_exc(file=sys.stdout)
                    # print '-'*60

    def makeRtp(self, payload, frameNbr):
        """RTP-packetize the video data."""
        version = 2
        padding = 0
        extension = 0
        cc = 0
        marker = 0
        pt = 26  # MJPEG type
        seqnum = frameNbr
        ssrc = 0

        rtpPacket = RtpPacket()

        rtpPacket.encode(
            version, padding, extension, cc, seqnum, marker, pt, ssrc, payload
        )

        return rtpPacket.getPacket()

    def replyRtsp(self, code, seq):
        """Send RTSP reply to the client."""
        if code == self.OK_200:
            # print "200 OK"
            reply = (
                "RTSP/1.0 200 OK\nCSeq: "
                + seq
                + "\nSession: "
                + str(self.clientInfo["session"])
            )
            connSocket = self.clientInfo["rtspSocket"][0]
            connSocket.send(reply.encode())

        # Error messages
        elif code == self.FILE_NOT_FOUND_404:
            print("404 NOT FOUND")
            # Fill in start
            connSocket = self.clientInfo["rtspSocket"][0]
            reply = RtspResponse(RtspStatus.NOT_FOUND)

            connSocket.send(reply.encode().encode())
            # Fill in end

        elif code == self.CON_ERR_500:
            print("500 CONNECTION ERROR")
            # Fill in start
            connSocket = self.clientInfo["rtspSocket"][0]
            reply = RtspResponse(RtspStatus.CONNECTION_ERROR)

            connSocket.send(reply.encode().encode())
            # Fill in end
