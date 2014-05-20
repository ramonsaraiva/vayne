import socket
from threading import Thread

class IRCSim:
	def __init__(self, port):
		self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.__PORT = port

	def simulate_msg(self, msg):
		return '{0} :{1}\r\n'.format(':simulator PRIVMSG #woodoo', msg)

	def start(self):
		self.__socket.bind(('', self.__PORT))
		self.__socket.listen(1)
		conn, addr = self.__socket.accept()
		while 1:
			data = conn.recv(1024)
			print(data)

			if 'USER' in data:
				print('user in')
				conn.send(':simulator 376\r\n')
			if 'JOIN' in data:
				conn.send(self.simulate_msg('v vnc_global'))
				conn.send(self.simulate_msg('v jobs'))

if __name__ == '__main__':
	sim = IRCSim(8090)
	sim.start()
