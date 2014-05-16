from connection import Connection

class Bot:
	END_OF_MOTD = '376'

	def __init__(self, nick):
		self.connections = []
		self.buffers = []
		self.nick = nick

	def add_connection(self, sv, port):
		con = Connection(sv, port)
		self.connections.append(con)
		self.buffers.append('')

	def set_channels(self, channels):
		self.channels = channels

	def connect(self):
		for con in self.connections:
			if con.active:
				continue
			con.connect(self.nick)
		self.work()

	def parse(self, data, key):
		print(data)
		source = ''
		line = ''
		if data.startswith(':'):
			source, line = data[1:].split(' ', 1)
		else:
			source = None
			p = data.split(' ')
			if p[0] == 'PING':
				self.connections[key].write(('PONG', p[1]))
				print("PONG")
				return

		if ' :' in line:
			argstr, text = line.split(' :', 1)
		else:
			argstr, text = line, ''
		args = argstr.split(' ')
		print(args)

		if args[0] == self.END_OF_MOTD:
			for channel in self.channels:
				self.connections[key].write(('JOIN', channel))
			return	


	def work(self):
		while True:
			for key, con in enumerate(self.connections):
				self.buffers[key] += con.socket.recv(1024)
				temp = self.buffers[key].split('\n')
				self.buffers[key] = temp.pop()
				
				for line in temp:
					self.parse(line, key)

if __name__ == '__main__':
	bot = Bot('woodoozera')
	bot.add_connection('irc.freenode.org', 6667)
	bot.set_channels(['#woodoo'])
	bot.connect()

	"""testing parse
	bot = Bot('aasdjqrr')
	bot.parse('PING HRuiashdiuah jaoisuhras', 1)
	"""
