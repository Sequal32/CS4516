import sys
from time import time
HEADER_SIZE = 12

class RtpPacket:	
	header = bytearray(HEADER_SIZE)
	
	def __init__(self):
		pass
		
	def encode(self, version, padding, extension, cc, seqnum, marker, pt, ssrc, payload):
		"""Encode the RTP packet with header fields and payload."""
		timestamp = int(time())
		header = bytearray(HEADER_SIZE)
		
		#Fill in Start
		# Fill the header bytearray with RTP header fields
		# header[0] = ...
		# ...
		# till
		# header[11] = ...
		
		#self.header = ...
		
		# Get the payload from the argument
		self.payload = ....
		#Fill in End

	def decode(self, byteStream):
		"""Decode the RTP packet."""
		self.header = bytearray(byteStream[:HEADER_SIZE])
		self.payload = byteStream[HEADER_SIZE:]
	
	def version(self):
		"""Return RTP version."""
		return int(self.header[0] >> 6)
	
	def seqNum(self):
		"""Return sequence (frame) number."""
		#Fill in Start
		seqNum = ...
		#Fill in End
		return int(seqNum)
	
	def timestamp(self):
		"""Return timestamp."""
		#Fill in Start
		timestamp = ...
		#Fill in End
		return int(timestamp)
	
	def payloadType(self):
		"""Return payload type."""
		#Fill in Start
		pt = ...
		#Fill in End
		return int(pt)
	
	def getPayload(self):
		"""Return payload."""
		return self.payload
		
	def getPacket(self):
		"""Return RTP packet."""
		return self.header + self.payload