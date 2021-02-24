from tkinter import *
import socket, threading
ip = str(input('enter ip > '))
port = int(input('enter port > '))
bufsize = 4096
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((ip, port))
sock.sendall('client\0'.encode('ascii'))
username = input('username> ')
sock.sendall((username + '\0').encode('ascii'))


root = Tk()
root.configure(background='#393e46')
def send():
	print('sending')
	message = sendBox.get()
	message += '\0'
	sock.sendall(message.encode('ascii'))
	sendBox.delete(0, 'end')

usernameVar = StringVar()
messageBox = Text(root)
messageScroll = Scrollbar(root, orient=VERTICAL, command=messageBox.yview)
messageScroll.configure(background='#23262e')
messageBox.configure(borderwidth=20, relief='flat', foreground='#eeeeee', background='#23262e', font=('Courier', 13), yscrollcommand=messageScroll.set)
sendBox = Entry(root, text='enter here')
sendBox.configure(foreground='#eeeeee', background='#23262e', font=('Courier', 13))
sendButton = Button(root, text='send', command=send)
sendButton.configure(foreground='#23262e', background='#23262e', activeforeground='#23262e')
usernameBox = Label(root, textvariable=usernameVar, anchor='nw')
usernameBox.configure(borderwidth=5, relief='flat', justify='left', foreground='#eeeeee', background='#23262e', font=('Courier', 15))

#grid stuff
messageBox.grid(column=0, row=0, rowspan=3, columnspan=2, sticky='nesw', padx=10, pady=5)
messageScroll.grid(column=2, row=0, rowspan=3, sticky='ns', pady=5)
sendBox.grid(column=0, row=4, rowspan=2, sticky='nsew', padx=10, pady=5)
sendButton.grid(column=1, row=4, rowspan=2, sticky='nsew', padx=10, pady=5)
usernameBox.grid(column=3, row=0, rowspan=6, sticky='nsew', padx=10, pady=5)

#upsizing stuff
root.columnconfigure(0, weight=2)
root.rowconfigure(0, weight=1)
root.columnconfigure(3, weight=1)

def recvAll(sock, leftoverData):
	newLeftoverData = ''
	text = b''
	messages = []
	print('recvAll executed')
	while True:
		text += sock.recv(bufsize)
		if b'\0' in text:
			print('found a message')
			text = text.decode('ascii')
			while True:
				if '\0' in text:
					location = text.find('\0')
					messages.append(text[0:location])
					text = text[location+1:]
					#message doesn't include \0
				else:
					if text != '':
						newLeftoverData = text[0:]
					break
			print('received something')
			break
	#add the leftoverData from last recvAll
	messages[0] = leftoverData + messages[0]
	return messages, newLeftoverData

def receive(ip, port):
	messageBox.insert('end', 'Begining of chat\n')
	"""usernameStr = recvAll(sock)
	usernameStr = usernameStr.decode('ascii')
	print(usernameStr)
	length = len(usernameStr)
	usernameVar.set(usernameVar.get() + usernameStr[1:length])"""
	leftoverData = ''
	while True:
		messageBox['state'] = 'disabled'
		messages, leftoverData = recvAll(sock, leftoverData)
		messageBox['state'] = 'normal'
		for message in messages:
			method = message[0]
			content = message[1:len(message)]
			#new user
			if method == '0':
				messageBox.insert('end', content + ' has joined\n')
				continue
			#usernames
			elif method == '1':
				usernameVar.set(content)
				continue
			else:
				messageBox.insert('end', content + '\n')

recvThread = threading.Thread(target=receive, args=[ip, port]).start()
root.mainloop()