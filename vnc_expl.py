import socket

def newb_expl(host):
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.settimeout(2)
	try: 
		sock.connect((host, 5900))
		return True
	except Exception:
		return False
