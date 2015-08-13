import select
import socket
import sys
import argparse
SERVER_HOST = '54.191.34.184'
BACKLOG = 5

class ChatServer():
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.clients = [] #Keep a tab of all the connected clients
		#Initialise the server socket
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
		self.server.bind((self.host, self.port))
		self.server.listen(BACKLOG)
		print "Server listening on port %s" %self.port

		self.inputs = [self.server, sys.stdin] #Keeps a tab of all the incoming connections
		self.outputs = [] #Keep a tab of all the sockets to which we need to send data

	def run(self):
		running =  True
		while running:
			try:
				readable, writable, exceptional = select.select(self.inputs, self.outputs, self.outputs)
			except socket.error, e:
				break

			for sock in readable:
				if sock == self.server:
					#If the readable socket is server then we need to accept connections and receive messages and broadcast them
					client, address = sock.accept() #client contains the socket information and address contains the address information of the client
					print 'Chat server got connected to client %s:%s ' %(address[0],address[1])
					self.clients.append((client, address))
					self.inputs.append(client)
					msg = 'Connected new client %d at %s:%s '%(len(self.clients),address[0],address[1])
					for s in self.outputs:
						s.sendall(msg)
					self.outputs.append(client)
				elif sock == sys.stdin:
					junk = sys.stdin.readline()
					running =  False
				else:
					#All the clients that have been connected to the server
					try:
						data = sock.recv(4096)
						if data:
							msg = 'Client %s:%s says : %s ' %(address[0],address[1],data)
							for s in self.outputs:
								s.sendall(msg)
					except socket.error , e:
						self.inputs.remove(sock)
						self.outputs.remove(sock)

		self.server.close()



class ChatClient():
	def __init__(self,name,port, host = SERVER_HOST):
		self.name = name
		self.host = host
		self.port = port
		self.connected = False
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect((self.host, self.port))
			print 'Client connected to Server at port : %s' %self.port
			self.connected = True
		except socket.error,e:
			print 'Failed to connect to socket server @port: %s' %self.port

	def run(self):
		while self.connected:
			readable, writable, exceptional = select.select([0,self.sock],[],[])
			for sock in readable:
				if sock == 0:
					data = sys.stdin.readline()
					if data:
						self.sock.sendall(data)
				elif sock == self.sock:
					data = self.sock.recv(4096)
					if data:
						sys.stdout.write(data + '\n')
						sys.stdout.flush()
					else:
						print 'Shutting Down'
						self.connected = False
						break



if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Chat Server')
	parser.add_argument('--name',action = 'store', dest = 'name',required = True)
	parser.add_argument('--port', action = 'store', type = int, dest = 'port',required = True)
	givenArgs = parser.parse_args()
	name = givenArgs.name
	port = givenArgs.port

	if name == 'server':
		server = ChatServer(SERVER_HOST, port)
		server.run()
	else:
		client = ChatClient(name,port)
		client.run()