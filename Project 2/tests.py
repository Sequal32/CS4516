import unittest
import time
import textwrap

from RtpPacket import RtpPacket
from RtspPacket import RtspRequest, RtspMethod, RtspResponse, RtspStatus


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
    TEST_PACKET_FIELDS_1 = {
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

    TEST_PACKET_FIELDS_2 = {
        "version": 1,
        "padding": 0,
        "extension": 0,
        "cc": 0xA,
        "marker": 0,
        "seqnum": 0xBEEF,
        "pt": 0x24,
        "ssrc": 0xBEEFDEAD,
        "payload": bytearray([0x1, 0x2, 0x3]),
    }

    def _single_decode_test(self, test_packet_fields):
        packet = RtpPacket()
        packet.decode(
            self.generate_test_packet_bytes(
                **test_packet_fields, timestamp=int(time.time())
            )
        )

        self.assertEqual(packet.version(), test_packet_fields["version"])
        self.assertEqual(packet.seqNum(), test_packet_fields["seqnum"])
        self.assertEqual(packet.payloadType(), test_packet_fields["pt"])
        self.assertEqual(packet.getPayload(), test_packet_fields["payload"])

    def test_decode(self):
        self._single_decode_test(TestRtpPacket.TEST_PACKET_FIELDS_1)
        self._single_decode_test(TestRtpPacket.TEST_PACKET_FIELDS_2)

    def _single_encode_test(self, test_packet_fields):
        packet = RtpPacket()
        cur_time = int(time.time())  # FIXME: how to make more deterministic?

        packet.encode(**test_packet_fields)
        correct_bytes = self.generate_test_packet_bytes(
            **test_packet_fields, timestamp=cur_time
        )

        self.assertEqual(packet.getPacket(), correct_bytes)

    def test_encode(self):
        self._single_encode_test(TestRtpPacket.TEST_PACKET_FIELDS_1)
        self._single_encode_test(TestRtpPacket.TEST_PACKET_FIELDS_2)

    def _single_encode_decode_test(self, test_packet_fields):
        packet = RtpPacket()
        packet.encode(**test_packet_fields)
        packet.decode(packet.getPacket())

        self.assertEqual(packet.version(), test_packet_fields["version"])
        self.assertEqual(packet.seqNum(), test_packet_fields["seqnum"])
        self.assertEqual(packet.payloadType(), test_packet_fields["pt"])
        self.assertEqual(packet.getPayload(), test_packet_fields["payload"])

    def test_encode_decode(self):
        self._single_encode_decode_test(TestRtpPacket.TEST_PACKET_FIELDS_1)
        self._single_encode_decode_test(TestRtpPacket.TEST_PACKET_FIELDS_2)

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


class TestRtspPacket(unittest.TestCase):
    def test_rtsp_request_init(self):
        packet = RtspRequest(RtspMethod.PLAY, "movie.Mjpeg")

        self.assertEqual(packet.method(), RtspMethod.PLAY)
        self.assertEqual(packet.filename(), "movie.Mjpeg")

    def test_rtsp_packet_header_get_set(self):
        packet = RtspRequest(RtspMethod.PLAY, "movie.Mjpeg")
        packet.set_header("CSeq", "1")
        packet.set_header("Test", "200")

        self.assertEqual(packet.get_header("CSeq"), "1")
        self.assertEqual(packet.get_header("Test"), "200")

    def test_rtsp_request_encode(self):
        packet = RtspRequest(RtspMethod.PLAY, "movie.Mjpeg")

        self.assertEqual(
            packet.encode().strip(),
            f"""
                PLAY movie.Mjpeg RTSP/1.0
            """.strip(),
        )

        packet = RtspRequest(RtspMethod.SETUP, "movie.Mjpeg")

        self.assertEqual(
            packet.encode().strip(),
            f"""
                SETUP movie.Mjpeg RTSP/1.0
            """.strip(),
        )

    def test_rtsp_request_encode_with_headers(self):
        packet = RtspRequest(RtspMethod.PLAY, "movie.Mjpeg")
        packet.set_header("CSeq", "1")
        packet.set_header("Test", "200")

        packet_str = packet.encode().split("\n")

        self.assertEqual(packet_str[0], "PLAY movie.Mjpeg RTSP/1.0")
        self.assertIn("CSeq: 1", packet_str)
        self.assertIn("Test: 200", packet_str)

    def test_rtsp_request_decode(self):
        packet = RtspRequest.decode("PLAY movie.Mjpeg RTSP/1.0")

        self.assertEqual(packet.method(), RtspMethod.PLAY)
        self.assertEqual(packet.filename(), "movie.Mjpeg")

    def test_rtsp_request_decode_with_headers(self):
        packet = RtspRequest.decode(
            """PLAY movie.Mjpeg RTSP/1.0
CSeq: 1
Test: 200"""
        )

        self.assertEqual(packet.method(), RtspMethod.PLAY)
        self.assertEqual(packet.filename(), "movie.Mjpeg")

    def test_rtsp_response_init(self):
        packet = RtspResponse(RtspStatus.OK)
        self.assertEqual(packet.status(), RtspStatus.OK)

    def test_rtsp_response_header_get_set(self):
        packet = RtspResponse(RtspStatus.OK)
        packet.set_header("CSeq", "1")
        packet.set_header("Test", "200")

        self.assertEqual(packet.get_header("CSeq"), "1")
        self.assertEqual(packet.get_header("Test"), "200")

    def test_rtsp_response_encode(self):
        packet = RtspResponse(RtspStatus.OK)

        self.assertEqual(
            packet.encode().strip(),
            "RTSP/1.0 200 OK",
        )

    def test_rtsp_response_encode_with_headers(self):
        packet = RtspResponse(RtspStatus.OK)
        packet.set_header("CSeq", "1")
        packet.set_header("Test", "200")

        part_str = packet.encode().split("\n")

        self.assertEqual(part_str[0], "RTSP/1.0 200 OK")
        self.assertIn("CSeq: 1", part_str)
        self.assertIn("Test: 200", part_str)

    def test_rtsp_response_decode_with_headers(self):
        packet = RtspResponse.decode("RTSP/1.0 200 OK\nCSeq: 1\nTest: 200")

        self.assertEqual(packet.status(), RtspStatus.OK)
        self.assertEqual(packet.get_header("CSeq"), "1")
        self.assertEqual(packet.get_header("Test"), "200")


if __name__ == "__main__":
    unittest.main()
