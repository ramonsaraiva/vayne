# -*- coding: utf-8 -*-

from connection import Connection
from threading import Thread

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

	K = {
		#game
		'mode': 'gameMode', #classic
		'stype': 'subType', #normal, ranked5x5
		's1': 'spell1',
		's2': 'spell2',
		#game stats
		'win': 'win',
		'lvl': 'level',
		'gold': 'goldEarned',
		'spent': 'goldSpent',
		'cs': 'minionsKilled',
		'jcs': 'neutralMinionsKilled',
		'k': 'championsKilled',
		'd': 'numDeaths',
		'a': 'assists',
	}

	CHAMPIONS = {
		'1': 'Annie',
		'2': 'Olaf',
		'3': 'Galio',
		'4': 'TwistedFate',
		'5': 'XinZhao',
		'6': 'Urgot',
		'7': 'Leblanc',
		'8': 'Vladimir',
		'9': 'FiddleSticks',
		'10': 'Kayle',
		'11': 'MasterYi',
		'12': 'Alistar',
		'13': 'Ryze',
		'14': 'Sion',
		'15': 'Sivir',
		'16': 'Soraka',
		'17': 'Teemo',
		'18': 'Tristana',
		'19': 'Warwick',
		'20': 'Nunu',
		'21': 'MissFortune',
		'22': 'Ashe',
		'23': 'Tryndamere',
		'24': 'Jax',
		'25': 'Morgana',
		'26': 'Zilean',
		'27': 'Singed',
		'28': 'Evelynn',
		'29': 'Twitch',
		'30': 'Karthus',
		'31': 'Chogath',
		'32': 'Amumu',
		'33': 'Rammus',
		'34': 'Anivia',
		'35': 'Shaco',
		'36': 'DrMundo',
		'37': 'Sona',
		'38': 'Kassadin',
		'39': 'Irelia',
		'40': 'Janna',
		'41': 'Gangplank',
		'42': 'Corki',
		'43': 'Karma',
		'44': 'Taric',
		'45': 'Veigar',
		'48': 'Trundle',
		'50': 'Swain',
		'51': 'Caitlyn',
		'53': 'Blitzcrank',
		'54': 'Malphite',
		'55': 'Katarina',
		'56': 'Nocturne',
		'57': 'Maokai',
		'58': 'Renekton',
		'59': 'JarvanIV',
		'60': 'Elise',
		'61': 'Orianna',
		'62': 'MonkeyKing',
		'63': 'Brand',
		'64': 'LeeSin',
		'67': 'Vayne',
		'68': 'Rumble',
		'69': 'Cassiopeia',
		'72': 'Skarner',
		'74': 'Heimerdinger',
		'75': 'Nasus',
		'76': 'Nidalee',
		'77': 'Udyr',
		'78': 'Poppy',
		'79': 'Gragas',
		'80': 'Pantheon',
		'81': 'Ezreal',
		'82': 'Mordekaiser',
		'83': 'Yorick',
		'84': 'Akali',
		'85': 'Kennen',
		'86': 'Garen',
		'89': 'Leona',
		'90': 'Malzahar',
		'91': 'Talon',
		'92': 'Riven',
		'96': 'KogMaw',
		'98': 'Shen',
		'99': 'Lux',
		'101': 'Xerath',
		'102': 'Shyvana',
		'103': 'Ahri',
		'104': 'Graves',
		'105': 'Fizz',
		'106': 'Volibear',
		'107': 'Rengar',
		'110': 'Varus',
		'111': 'Nautilus',
		'112': 'Viktor',
		'113': 'Sejuani',
		'114': 'Fiora',
		'115': 'Ziggs',
		'117': 'Lulu',
		'119': 'Draven',
		'120': 'Hecarim',
		'121': 'Khazix',
		'122': 'Darius',
		'126': 'Jayce',
		'127': 'Lissandra',
		'131': 'Diana',
		'133': 'Quinn',
		'134': 'Syndra',
		'143': 'Zyra',
		'154': 'Zac',
		'157': 'Yasuo',
		'161': 'Velkoz',
		'201': 'Braum',
		'222': 'Jinx',
		'236': 'Lucian',
		'238': 'Zed',
		'254': 'Vi',
		'266': 'Aatrox',
		'267': 'Nami',
		'412': 'Thresh',
	}

	SPELLS = {
		'11': 'Smite',
		'10': 'Revive',
		'13': 'Clarity',
		'12': 'Teleport',
		'21': 'Barrier',
		'17': 'Garrison',
		'1': 'Cleanse',
		'3': 'Exhaust',
		'2': 'Clairvoyance',
		'4': 'Flash',
		'7': 'Heal',
		'6': 'Ghost',
		'14': 'Ignite',
	}


	def __init__(self, nick):
		self.__connections = []
		self.__buffers = []
		self.__channels = []
		self.__threads = {}
		self.__vnc = {}
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
		
		if (cmd == 'last'):
			if not self.check_args(args, 2):
				return

			lol = self.lolit()
			lol.set_api_region(args[1])
			try:
				lol.set_summoner(args[0])
				s = lol.get_summoner_games()
				last = s[0]
				stats = last['stats']
				l_win = 'WON' if stats[self.K['win']] else 'LOST'
				l_champ = str(last['championId'])
				l_type = last[self.K['stype']]
				l_lvl = stats[self.K['lvl']]
				l_spell1 = str(last[self.K['s1']])
				l_spell2 = str(last[self.K['s2']])
				l_kills = stats[self.K['k']]
				l_deaths = stats[self.K['d']]
				l_assists = 0
				if self.K['a'] in stats:
					l_assists = stats[self.K['a']]
				l_kda = (float(l_kills) + float(l_deaths)) / float(l_assists)
				l_cs = stats[self.K['cs']]
				l_gold = stats[self.K['gold']]

				self.printayne('{0} {1} his last game ({2}) as Lv. {3} {4} running {5}/{6}. KDA: {7}/{8}/{9} ({10:.2f}) CS: {11}, Total gold: {12}.'.format(args[0], l_win, l_type, l_lvl, self.CHAMPIONS[l_champ], self.SPELLS[l_spell1], self.SPELLS[l_spell2], l_kills, l_deaths, l_assists, l_kda, l_cs, l_gold), self.__channels)

			except RiotError, e:
				print self.printayne('riot error => {0}'.format(e.error_msg), self.__channels)

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
	bot.add_connection('irc.quakenet.org', 6667)
	bot.set_channels(['#leagueoflegends'])
	bot.connect()
