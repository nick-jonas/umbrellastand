import bluetooth

#insert here the address of the Pi that you noted earlier
bd_addr = "00:02:72:D6:A4:8C"
#port must be consistent with server
port = 1

#create a socket and connect to the server
sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr,port))

#we're now ready to send data!

#This will repeatedly send what a user types, you will probably want to 
#decide a format and check for it here so it can be easily decoded the 
#other side

while True:
  input = raw_input("What would you like to send? ")
  if (input == "quit"):
    break
  else:
    sock.send(input)
#close up when finished
sock.close()
