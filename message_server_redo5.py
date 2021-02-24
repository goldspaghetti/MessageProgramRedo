#!/usr/bin/env python3
import socket, select
from tkinter import *
bufsize = 4096
ip = str(input('enter ip > '))
port = int(input('enter port > '))

#def server_creation(ip, port):
	#server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#server.bind((ip, port))
	#server.listen(0)

#server_creation(ip, port)
usernames = {}
def addUsername(sock, username, sockName, fd):
	for items in usernames.items():
		if items[1] == username:
			usernames[fd] = sockName[0]
			return 'username taken'
	usernames[fd] = username
	print(username)
	print(usernames[fd])
	updateUsername()
	print('username added')

def sendMessage(message):
	message += '\0'
	messageSend = '2' + message
	clientAdded = []
	for items in fd_info.items():
		print(items[1][0])
		if items[1][1] == 'client':
			print(items)
			clientAdded.append(items[1][0])
	for clients in clientAdded:
		try:
			clients.sendall(messageSend.encode('ascii'))
		except sock.error:
			del fd_info[clients.fileno()]
			del usernames[clients.fileno()]
			continue


def updateUsername():
	clientAdded = []
	for items in fd_info.items():
		print(items[1][0])
		if items[1][1] == 'client':
			print(items)
			clientAdded.append(items[1][0])
	usernameStr = '1'
	for i in usernames.values():
		usernameStr += i
		usernameStr += '\n'
	usernameStr += '\0'
	print(usernameStr)
	#sendMessage(usernames[sc.fileno()] + ' has connected')
	for clients in clientAdded:
		try:
			clients.sendall(usernameStr.encode('ascii'))
			print('sent usename')
		except socket.error:
			del fd_info[clients.fileno()]
			del usernames[clients.fileno()]
			updateUsername()
			continue

leftoverData = {}
def recvAll(sock):
	text = b''
	messages = []
	while True:
		text += sock.recv(bufsize)
		if b'\0' in text:
			text = text.decode('ascii')
			print(text)
			while True:
				if '\0' in text:
					print(len(text))
					location = text.find('\0')
					messages.append(text[0:location])
					text = text[location+1:]
					#message doesn't include \0
				else:
					if text != '':
						leftoverData[sock] = text[0:]
					print('about to break')
					break
			print('received something')
			break
	#add the leftoverData from last recvAll
	print(messages[0])
	try:
		messages[0] = leftoverData[sock] + messages[0]
	except KeyError:
		print('no leftover')
	return messages

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((ip, port))
server.listen(0)
poller = select.poll()
poller.register(server, select.POLLIN | select.POLLPRI | select.POLLNVAL | select.POLLERR)
fd_info = {
	server.fileno() : [server, 'server']
}
while True:
	events = poller.poll()
	for fd, flag in events:
		try:
			sockInfo = fd_info[fd][1]
		except KeyError:
			continue
		sock = fd_info[fd][0]
		if flag == select.POLLIN:
			if sockInfo == 'server':
				sc, sockName = server.accept()
				print('accepted')
				data = recvAll(sc)
				print(len(data))
				if len(data) < 2:
					username = recvAll(sc)[0]
					print(len(data))
				else:
					username = data[1]
				role = data[0]
				fd_info[sc.fileno()] = [sc, 'client', sockName]
				if role == 'client':
					print('client connection recieved')
					if addUsername(sc, username, sockName, sc.fileno()):
						sc.sendall('2username taken, please use !username to register again\0'.encode('ascii'))
					updateUsername()
					print('moving on')
				poller.register(sc, select.POLLIN | select.POLLPRI | select.POLLNVAL | select.POLLERR)
				sendMessage(usernames[sc.fileno()] + ' has connected')
			if sockInfo == 'client':
				messages = recvAll(sock)
				username = usernames[fd]
				for message in messages:
					if message == '!disconnect':
						sock.close()
						del fd_info[fd]
						del usernames[fd]
					if message[0:9] == '!username':
						print('changing username')
						if addUsername(sc, message[10:len(message)], fd_info[fd][2], fd):
							print(message[10:len(message)])
							sc.sendall('2username taken, please use !username to register again\0'.encode('ascii'))
					message = username + ": " + message
					sendMessage(message)

		if flag == select.POLLERR:
			sock.close()
			del fd_info[fd]
			del usernames[fd]

				#stuff here for distributing message

		