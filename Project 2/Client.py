from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import threading, sys, traceback, os
from socket import socket, INADDR_ANY, AF_INET, SOCK_DGRAM
import os

from RtpPacket import RtpPacket

#import sys
#print(sys.executable)

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN)		
		self.master.destroy() # Close the gui window
		cache_file_path = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		if os.path.exists(cache_file_path):
			os.remove(cache_file_path)  # Delete the cache image from video
			print("Cache file deleted:", cache_file_path)
		else:
			print("Cache file does not exist:", cache_file_path)
		#os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the cache image from video


	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			# Create a new thread to listen for RTP packets
			threading.Thread(target=self.listenRtp).start()
			self.playEvent = threading.Event()
			self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		while True:
			try:
				data = self.rtpSocket.recv(20480)
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					
					currFrameNbr = rtpPacket.seqNum()
					print("Current Seq Num: " + str(currFrameNbr))
										
					if currFrameNbr > self.frameNbr: # Discard the late packet
						self.frameNbr = currFrameNbr
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
			except TimeoutError:
				print("xy: Timeout occurred while waiting for data on RTP socket")
				break
				# Handle the timeout error gracefully
			except OSError as e:
				if e.errno == 57:
					print("xy: Socket is not connected")
					break
			except:
				# Stop listening upon requesting PAUSE or TEARDOWN
				if self.playEvent.isSet(): 
					break
				
				# Upon receiving ACK for TEARDOWN request,
				# close the RTP socket
				if self.teardownAcked == 1:
					self.rtpSocket.shutdown(socket.SHUT_RDWR)
					self.rtpSocket.close()
					break
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		cachename = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(cachename, "wb")
		file.write(data)
		file.close()
		
		return cachename
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height=288) 
		self.label.image = photo
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		#Fill in start
		#Create a socket
		self.rtspSocket = ....
		try:
			#make a connection to the serverAddress and port number
			#....
		except:
			messagebox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""
		
		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target=self.recvRtspReply).start()
			#Fill in Start
			# Update RTSP sequence number.
			#self.rtspSeq ...
			# Write the RTSP request to be sent.
			#request = ...
			# Keep track of the sent request.
			#self.requestSent = ...
			#Fill in End	
		
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			#Fill in Start
			# Update RTSP sequence number.
			#self.rtspSeq ...
			# Write the RTSP request to be sent.
			#request = ...
			# Keep track of the sent request.
			#self.requestSent = ...
			#Fill in End
				
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			#Fill in Start
			# Update RTSP sequence number.
			#self.rtspSeq ...
			# Write the RTSP request to be sent.
			#request = ...
			# Keep track of the sent request.
			#self.requestSent = ...
			#Fill in End
			
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			#Fill in Start
			# Update RTSP sequence number.
			#self.rtspSeq ...
			# Write the RTSP request to be sent.
			#request = ...
			# Keep track of the sent request.
			#self.requestSent = ...
			#Fill in End
		else:
			return
		
		# Send the RTSP request using rtspSocket.
			#Fill in Start
			#Fill in End
			
		print('\nData sent:\n' + request)
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while True:
			reply = self.rtspSocket.recv(1024).decode()
			print(reply)
			
			replycode=reply.split(' ')[0]
			#print("replycode is:", replycode)
			if replycode == '404':
				print("xy: the file does not exist on server\n")
			elif replycode == '500':
				print("xy: there is a connection problem\n")
			elif reply: 
				self.parseRtspReply(reply)
			
			# Close the RTSP socket upon requesting Teardown
			if self.requestSent == self.TEARDOWN:
				try:
					if self.rtspSocket.fileno() != -1:  # Check if the socket is connected
						self.rtspSocket.shutdown(socket.SHUT_RDWR)
						self.rtspSocket.close()
				except OSError as e:
					print("Error:", e)
				#self.rtspSocket.shutdown(socket.SHUT_RDWR)
				#self.rtspSocket.close()
				break
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		lines = data.split('\n')
		seqNum = int(lines[1].split(' ')[1])
		
		# Process only if the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])
			# New RTSP session ID
			if self.sessionId == 0:
				self.sessionId = session
			
			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200: 
					if self.requestSent == self.SETUP:
				#Fill in Start
						# Update RTSP state.
						self.state = ...
						# Open RTP port.
						self.openRtpPort()
					elif self.requestSent == self.PLAY:
						self.state = ....
					elif self.requestSent == self.PAUSE:
						self.state = ....
						# The play thread exits. A new thread is created on resume.
						self.playEvent.set()
					elif self.requestSent == self.TEARDOWN:
						self.state = ...
				#Fill in End		
						# Flag the teardownAcked to close the socket.
						self.teardownAcked = 1 
	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#Fill in Start
		# Create a new datagram socket to receive RTP packets from the server
		#self.rtpSocket = socket(AF_INET, SOCK_DGRAM)
		# Set the timeout value of the socket to 0.5sec
		#...
		
		try:
			# Bind the socket to the address using the RTP port given by the client user
			#...
		#Fill in End	
		except:
			tkinter.messagebox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkinter.messagebox.askokcancel("Quit?", "Are you sure you want to quit?"):
			self.exitClient()
		else: # When the user presses cancel, resume playing.
			self.playMovie()
