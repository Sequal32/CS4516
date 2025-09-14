import sys
from time import time

HEADER_SIZE = 12


class RtpPacket:
    header = bytearray(HEADER_SIZE)

    def __init__(self):
        pass

    def encode(
        self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload
    ):
        """Encode the RTP packet with header fields and payload."""
        timestamp = int(time())
        header = bytearray(HEADER_SIZE)

        # Fill in Start
        # Fill the header bytearray with RTP header fields

        if version < 0 or version > 3:
            raise ValueError("Version must be a 2-bit field (0-3).")

        if padding < 0 or padding > 1:
            raise ValueError("Padding must be a 1-bit field (0-1).")

        if extension < 0 or extension > 1:
            raise ValueError("Extension must be a 1-bit field (0-1).")

        if cc < 0 or cc > 15:
            raise ValueError("CC must be a 4-bit field (0-15).")

        if seqnum < 0 or seqnum > 65535:
            raise ValueError("Sequence number must be a 16-bit field (0-65535).")

        if marker < 0 or marker > 1:
            raise ValueError("Marker must be a 1-bit field (0-1).")

        if pt < 0 or pt > 127:
            raise ValueError("Payload type must be a 7-bit field (0-127).")

        if ssrc < 0 or ssrc > 4294967295:
            raise ValueError("SSRC must be a 32-bit field (0-4294967295).")

        header[0] = version << 6 | padding << 5 | extension << 4 | cc
        header[1] = marker << 7 | pt
        header[2] = (seqnum >> 8) & 0xFF
        header[3] = seqnum & 0xFF
        header[4] = timestamp >> 24 & 0xFF
        header[5] = timestamp >> 16 & 0xFF
        header[6] = timestamp >> 8 & 0xFF
        header[7] = timestamp & 0xFF
        header[8] = ssrc >> 24 & 0xFF
        header[9] = ssrc >> 16 & 0xFF
        header[10] = ssrc >> 8 & 0xFF
        header[11] = ssrc & 0xFF

        self.header = header

        # Get the payload from the argument
        self.payload = payload
        # Fill in End

    def decode(self, byteStream):
        """Decode the RTP packet."""
        self.header = bytearray(byteStream[:HEADER_SIZE])
        self.payload = byteStream[HEADER_SIZE:]

    def version(self):
        """Return RTP version."""
        return int(self.header[0] >> 6)

    def seqNum(self):
        """Return sequence (frame) number."""
        # Fill in Start
        seqNum = self.header[2] << 8 | self.header[3]
        # Fill in End
        return int(seqNum)

    def timestamp(self):
        """Return timestamp."""
        # Fill in Start
        timestamp = (
            self.header[4] << 24
            | self.header[5] << 16
            | self.header[6] << 8
            | self.header[7]
        )
        # Fill in End
        return int(timestamp)

    def payloadType(self):
        """Return payload type."""
        # Fill in Start
        pt = self.header[1] & 0x7F
        # Fill in End
        return int(pt)

    def getPayload(self):
        """Return payload."""
        return self.payload

    def getPacket(self):
        """Return RTP packet."""
        return self.header + self.payload
