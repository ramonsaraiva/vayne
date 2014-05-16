import socket

CRLF = '\r\n'

class Connection:
	def __init__(self, sv, port):
		self.sv = sv
		self.port = port
		self.socket = None
		self.active = False
		self.nick = ''

	def connect(self, nick):
		self.nick = nick
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.sv, self.port))
		self.handle_connect()

	def handle_connect(self):
		if self.socket is None:
			return
		self.write(('NICK', self.nick))
		self.write(('USER', self.nick, '+iw', self.nick), 'VAYNE')
		print('init data sent')

	def push(self, data):
		print('pushed => {0}'.format(data))
		self.socket.send(data)

	def __write(self, args, text=None):
		try:
			data = ''
			if text:
				#510 cuz CR & LR count
				data = ('{0} :{1}'.format(' '.join(args), text))[:510] + CRLF
			else:
				data = ' '.join(args)[:510] + CRLF
			self.push(data)
		except IndexError:
			print("error")

	def write(self, args, text=None):
		def safe(input):
			input = input.replace('\n', '')
			input = input.replace('\r', '')
			return input.encode('utf-8')
		try:
			args = [safe(arg) for arg in args]
			if text is not None:
				text = safe(text)
			self.__write(args, text)
		except Exception, e: print(e)
