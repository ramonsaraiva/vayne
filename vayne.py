# -*- coding: utf-8 -*-

import sys

from connection import Connection
from threading import Thread

from lolclean.lolclean import LOLClean

class Bot:
	END_OF_MOTDS = ['376', '422']
	PREFIX = 'v'
	TAG = '(vayne)'

	OWNERS = ['vayne']

	def __init__(self, nick):
		self.__connections = []
		self.__buffers = []
		self.__channels = []
		self.__threads = {}
		self.__vnc = {}
		self.__key = 0
		self.__nick = nick
		self.__lol = LOLClean('1201f800-aced-4abb-9083-714dcf58a36e')

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

		if args[0] in self.END_OF_MOTDS:
			for channel in self.__channels:
				self.currcon.write(('JOIN', channel))
			return	

		if text:
			if text[0] == self.PREFIX and len(text.split(' ')) >= 2:
				self.parse_cmd(text, source)

	def check_args(self, args, req):
		if len(args) < req:
			self.printayne('?', self.__channels)
			return False
		return True

	def check_owner(self, source):
		if source in self.OWNERS:
			return True
		self.printayne('who the fuck are you?', self.__channels)
		return False

	def add_jobs(self, key, jobs):
		if key not in self.__threads:
			self.__threads[key] = []
		for job in jobs:
			self.__threads[key].append(job)

	def lolit(self):
		return LeagueOfLegends(self.RIOT_API_KEY)

	def parse_cmd(self, cmd, source):
		args = cmd[2:].split(' ')
		if len(args) > 1:
			cmd, args = cmd[2:].split(' ', 1)
		else:
			cmd = args[0]
			args = ''
		args = args.split(' ')
		source = source.split('!')[0]

		if (cmd == 'nick'):
			if not self.check_owner(source):
				return
			if not self.check_args(args, 1):
				return

			self.currcon.write(('NICK', args[0]))
		if (cmd == 'join'):
			if not self.check_owner(source):
				return
			if not self.check_args(args, 1):
				return
			self.currcon.write(('JOIN', args[0]))

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

		if (cmd == 'summoner'):
			if not self.check_args(args, 2):
				return

			lol = self.lolit()
			lol.set_api_region(args[1])

			try:
				data = lol.get_summoner_by_name(args[0])
				s_name = data.iterkeys().next()
				s_data = data[s_name]
				s_id = s_data['id']
				s_level = s_data['summonerLevel']
				self.printayne('{0} => id {1} # level {2}'.format(s_name, s_id, s_level), self.__channels)
			except RiotError, e:
				self.printayne('riot error => {0}'.format(e.error_msg), self.__channels)

		if (cmd == 'rank'):
			if not self.check_args(args, 2):
				return
			fine, output = self.__lol.rank(args[0], args[1])
			if fine:
				for line in output:
					self.printayne(line, self.__channels)
			else:
				self.printayne(output, self.__channels)

		if (cmd == 'last'):
			if not self.check_args(args, 2):
				return
			fine, output = self.__lol.last(args[0], args[1])
			self.printayne(output, self.__channels)

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
	bot = Bot('vayneluwl')
	#bot.add_connection('google.root-network.org', 6667)
	bot.add_connection(sys.argv[1], 6667)
	channels = ['#{0}'.format(x) for x in sys.argv[2:]]
	bot.set_channels(channels)
	bot.connect()
