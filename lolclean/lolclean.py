from leagueoflegends import LeagueOfLegends
from leagueoflegends import RiotError

from api.constants import *
from api.simplifiers import *

class LOLClean():
	__default_region = 'br'

	def __init__(self, key, region=__default_region):
		self.__api = LeagueOfLegends(key)
		self.__default_region = region

	def prepare(self, summoner, region):
		self.__api.set_api_region(region)
		self.__api.set_summoner(summoner)

	# list of strings containing all rank data
	def rank(self, summoner, region=__default_region):
		try:
			self.prepare(summoner, region)
			data = self.__api.get_summoner_leagues_entry()

			queues = {}
			for key, queue in data.items():
				entry = queue['entries'][0]
				queues[key] = {
					'tier': queue['tier'],
					'name': queue['name'],
					'division': entry['division'],
					'wins': entry['wins'],
					'lp': entry['leaguePoints'],
					'ident': entry['playerOrTeamName'].encode('ascii', 'replace'),
				}

			queues_output = []
			for key, queue in queues.items():
				queues_output.append('{0} [{1}] => tier {2} {3} ({4}) # {5} wins # {6} league points'.format(queue['ident'], QUEUES[key], queue['tier'], queue['division'], queue['name'], queue['wins'], queue['lp']))

			return (True, queues_output)
		except RiotError, e:
			return (False, e.error_msg)

	def last(self, summoner, region=__default_region):
		last = {}
		try:
			self.prepare(summoner, region)
			data = self.__api.get_summoner_games()
			lg = data[0]
			lgs = lg['stats']
			last = {
				'win': 'WON' if lgs[KS['win']] else 'LOST',
				'champ': str(lg[KS['champ']]),
				'type': lg[KS['stype']],
				'lvl': lg[KS['lvl']],
				's1': str(lg[KS['s1']]),
				's2': str(lg[KS['s2']]),
				'kills': lgs[KS['k']],
				'deaths': lgs[KS['d']],
				'assists': lgs[KS['a']],
				'cs': lgs[KS['cs']],
				'gold': lgs[KS['gold']],
			}

			last['kda'] = (float(last['kills']) + float(last['assists'])) / float(last['deaths'])

			output = '{0} {1} his last game ({2}) as Lv. {3} {4} running {5}/{6}. KDA: {7}/{8}/{9} ({10:.2f}) CS: {11}, Total gold: {12}.'.format(summoner, last['win'], QUEUES[last['type']], last['lvl'], CHAMPIONS[last['champ']], SPELLS[last['s1']], SPELLS[last['s2']], last['kills'], last['deaths'], last['assists'], last['kda'], last['cs'], last['gold'])
			return (True, output)

		except RiotError, e:
			return (False, e.error_msg)
