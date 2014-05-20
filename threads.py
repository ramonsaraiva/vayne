from threading import Thread
import json

threads = []

def tryy(n):
	while True:
		print(n)

def try_all():
	for i in range(5):
		t = Thread(target=tryy, args=(str(i),))
		threads.append(t)

	[t.start() for t in threads]
	#[t.join() for t in threads]

if __name__ == '__main__':
	t = Thread(target=try_all)
	t.start()
