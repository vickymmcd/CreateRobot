# Imports
from Tkinter import *
import struct
import serial

# Global variables
connection = None

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

# Send command functions
def sendCommandRaw(command):
    global connection

    try:
        if connection is not None:
            connection.write(command)
        else:
            print "Not connected!"
    except serial.SerialException:
        print "Lost connection!"
        connection = None

    print ' '.join([str(ord(c)) for c in command])
    text.insert(END, ' '.join([str(ord(c)) for c in command]))
    text.insert(END, '\n')
    text.see(END)

# sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
def sendCommandASCII(command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        sendCommandRaw(cmd)
    
# Keyboard Event Function
def callbackKey(event):
    k = event.keysym.upper()
    motionChange = False

    if event.type == '2':
        if k == 'P': #Passive mode
            sendCommandASCII('128')
        elif k == 'S': #Safe Mode
            sendCommandASCII('131')
        elif k == 'F': #Full Mode
            sendCommandASCII('132')
        elif k == 'C': #Clean Mode
            sendCommandASCII('135')
        elif k == 'D': #Dock Mode
            sendCommandASCII('143')
        elif k == 'SPACE': #Beep
            sendCommandASCII('140 3 1 64 16 141 3')
        elif k == 'R': #Reset
            sendCommandASCII('7')
        elif k == 'UP': #Forward
            callbackKey.up = True
            motionChange = True
        elif k == 'DOWN': #Backward
            callbackKey.down = True
            motionChange = True
        elif k == 'LEFT': #Counterclockwise
            callbackKey.left = True
            motionChange = True
        elif k == 'RIGHT': #Clockwise
            callbackKey.right = True
            motionChange = True
        else:
            print repr(k), "not handled"
    elif event.type == '3': # KeyRelease; need to figure out how to get constant
        if k == 'UP':
           callbackKeyUp = False
           motionChange = True
        elif k == 'DOWN':
           callbackKeyDown = False
           motionChange = True
        elif k == 'LEFT':
            callbackKeyLeft = False
            motionChange = True
        elif k == 'RIGHT':
            callbackKeyRight = False
            motionChange = True

    if motionChange == True:
        velocity = 0
        velocity += VELOCITYCHANGE if callbackKey.up is True else 0
        velocity -= VELOCITYCHANGE if callbackKey.down is True else 0
        rotation = 0
        rotation += ROTATIONCHANGE if callbackKey.left is True else 0
        rotation -= ROTATIONCHANGE if callbackKey.right is True else 0

        #Compute wheel velocities
        vr = velocity + (rotation/2)
        vl = velocity - (rotation/2)

        #Send drive command
        cmd = struct.pack(">Bhh", 145, vr, vl)
        if cmd != callbackKey.lastDriveCommand:
            sendCommandRaw(cmd)
            callbackKey.lastDriveCommand = cmd

#Connect Function
def onConnect():
    global connection

    port = "COM4"

    try:
        connection = serial.Serial(port, baudrate=115200, timeout=1)
        print "Connected!"
    except serial.SerialException:
        print "Failed to connect!"

#Quit Function
def onQuit():
    root.destroy()

#Main Body
callbackKey.up = False
callbackKey.down = False
callbackKey.left = False
callbackKey.right = False
callbackKey.lastDriveCommand = ''

#Program Window
root = Tk()

menu = Menu(root)
menu.add_command(label="Connect", command=onConnect)
menu.add_command(label="Quit", command=onQuit)
root.config(menu=menu)

text = Text(root, height=16, width=40, wrap=WORD)
scroll = Scrollbar(root, command=text.yview)
text.configure(yscrollcommand=scroll.set)
text.pack(side=LEFT, fill=BOTH, expand=True)
scroll.pack(side=RIGHT, fill=Y)

#Bind keyboard commands
root.bind("<Key>", callbackKey)
root.bind("<KeyRelease>", callbackKey)

#start main loop
root.mainloop()

    
