import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
	ssh.connect('85.25.235.97', username='root', password='Guto1508')
except Exception, e:
	print e

"""
except paramiko.AuthenticationException:
	print('{0} - key {1} failed'.format(target, key))
	ssh.close()
	return False
else:
	print('KEY {0} DID ITTTTT'.format(key))
	ssh.close()
	return True
"""
