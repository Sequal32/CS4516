import unittest
import time

from RtpPacket import RtpPacket


def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder="big")


class TestRtpPacket(unittest.TestCase):
    def generate_test_packet_bytes(
        self,
        version,
        padding,
        extension,
        cc,
        marker,
        pt,
        seqnum,
        timestamp,
        ssrc,
        payload,
    ):
        """
        Generate RTP packet bytes for testing. Uses Python's built in binary string building
        to construct the raw bytes.
        """
        correct_bytes = (
            bin(version)[2:].zfill(2)
            + bin(padding)[2:].zfill(1)
            + bin(extension)[2:].zfill(1)
            + bin(cc)[2:].zfill(4)
            + bin(marker)[2:].zfill(1)
            + bin(pt)[2:].zfill(7)
            + bin(seqnum)[2:].zfill(16)
            + bin(timestamp)[2:].zfill(32)
            + bin(ssrc)[2:].zfill(32)
        )
        return bitstring_to_bytes(correct_bytes) + payload

    """
    The fields of a test packet to test
    """
    TEST_PACKET_FIELDS = {
        "version": 2,
        "padding": 1,
        "extension": 1,
        "cc": 0xC,
        "marker": 1,
        "seqnum": 0xDEAD,
        "pt": 0x56,
        "ssrc": 0xDEADBEEF,
        "payload": bytearray([0xA, 0xB, 0xC]),
    }

    def test_decode(self):
        packet = RtpPacket()
        packet.decode(
            self.generate_test_packet_bytes(
                **TestRtpPacket.TEST_PACKET_FIELDS, timestamp=int(time.time())
            )
        )

        self.assertEqual(packet.version(), TestRtpPacket.TEST_PACKET_FIELDS["version"])
        self.assertEqual(packet.seqNum(), TestRtpPacket.TEST_PACKET_FIELDS["seqnum"])
        self.assertEqual(packet.payloadType(), TestRtpPacket.TEST_PACKET_FIELDS["pt"])
        self.assertEqual(
            packet.getPayload(), TestRtpPacket.TEST_PACKET_FIELDS["payload"]
        )

    def test_encode(self):
        packet = RtpPacket()
        cur_time = int(time.time())  # FIXME: how to make more deterministic?

        packet.encode(**TestRtpPacket.TEST_PACKET_FIELDS)
        correct_bytes = self.generate_test_packet_bytes(
            **TestRtpPacket.TEST_PACKET_FIELDS, timestamp=cur_time
        )

        self.assertEqual(packet.getPacket(), correct_bytes)

    def test_encode_decode(self):
        packet = RtpPacket()
        packet.encode(**TestRtpPacket.TEST_PACKET_FIELDS)
        packet.decode(packet.getPacket())

        self.assertEqual(packet.version(), TestRtpPacket.TEST_PACKET_FIELDS["version"])
        self.assertEqual(packet.seqNum(), TestRtpPacket.TEST_PACKET_FIELDS["seqnum"])
        self.assertEqual(packet.payloadType(), TestRtpPacket.TEST_PACKET_FIELDS["pt"])
        self.assertEqual(
            packet.getPayload(), TestRtpPacket.TEST_PACKET_FIELDS["payload"]
        )

    def test_error_raised_in_limits(self):
        packet = RtpPacket()

        self.assertRaises(
            ValueError, packet.encode, 4, 0, 0, 0, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 2, 0, 0, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 2, 0, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 16, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, 65536, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, 0, 128, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, 0, 0, 0, 4294967296, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, -1, 0, 0, 0, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, -1, 0, 0, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, -1, 0, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, -1, 0, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, -1, 0, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, 0, -1, 0, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, 0, 0, -1, 0, bytearray()
        )
        self.assertRaises(
            ValueError, packet.encode, 0, 0, 0, 0, 0, 0, 0, -1, bytearray()
        )


if __name__ == "__main__":
    unittest.main()
