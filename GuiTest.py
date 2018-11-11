
import pygame
import time

import sys
import os
import numpy as np

import argparse
import binascii
from datetime import datetime
import errno
import inspect
import logging.handlers
import select
import StringIO
import struct
import sys,os
import threading
import time
import types
import usb.core
import usb.util
import pdb
import serial


from xbee import XBee

import ieee15dot4 as ieee

import pyCCsnifferOriginal

from pyCCsnifferOriginal import PacketHandler
from pyCCsnifferOriginal import arg_parser
from pyCCsnifferOriginal import CC2531EMK
from pyCCsnifferOriginal import SniffedPacket
from pyCCsnifferOriginal import CapturedFrame
from pyCCsnifferOriginal import CustomAssertFrame

#inits
pygame.init()


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FORWARD DECLARES
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#globals
global silencer 
silencer = False

global setNewGame
setNewGame = False

global gunList
gunList = []

global timer
timer = 5

global packetHandler
packetHandler = None

global killMatrix
killMatrix = np.zeros((30,30))

global killList
killList = np.zeros(30)

#display variables
disp_height = 600
disp_width = 300
button_w = 120
button_h = 60
defFont = 'freesansbold.ttf'

#company data
companyName = "Zoomz Paintball LLC"
largestGunNumber = 28
sendTries = 3

#radio information
radioTarget = '/dev/ttyUSB0'
radioBaud = 19200

#init clock
clock = pygame.time.Clock()


#colors
black = (0,0,0)
white = (255,255,255)

red = (200,0,0)
green = (0,200,0)
blue = (0,0,200)

brightRed = (255,0,0)
brightGreen = (0,255,0)
brightBlue = (0,0,255)


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ RADIO FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def radioProgram(pkg, newGame = False):
	#send code package over radio

	global gunList
	xbee = XBee(serial.Serial(radioTarget, radioBaud))

	pref='\x40\x06\x00'

	if len(gunList) == 0: 
		gunList=range(1,largestGunNumber)
	dest = ['\x00'+str(unichr(int(gun))) for gun in gunList]

	if type(pkg) != list: pkg=[pkg]

	for i in range(sendTries):
		for c1 in code:
			for gun in dest:
				x = xbee.send('tx', dest_addr=gun, data=pref)
				x = xbee.send('tx', dest_addr=gun, data=c1)
			time.sleep(0.5)

	if newGame: 
		time.sleep(0.3)
		newGame(gunList) 

		pass

def endGame():
	"""list of gun numbers (integers); if this is empty, then new game all guns"""
	xbee = XBee(serial.Serial(radioTarget, radioBaud))
	global gunList

	if len(gunList) == 0: 
		dest=['\xff\xff']
	else:
		dest=[]
		for gun in gunList:
			dest.append('\x00'+str(unichr(int(gun)))) # append gun number

	pref='\x40\x03\x07' # end game code

	for i in range(sendTries):
		for gun in dest:
			x = xbee.send('tx', dest_addr=gun, data=pref)
		time.sleep(0.5)
	pass

def newGame():
	xbee = XBee(serial.Serial(radioTarget, radioBaud))
	if len(gunList) == 0: 
		dest=['\xff\xff']
		# dest=['\x00'+str(unichr(kk)) for kk in range(1,27) ]
	else:
		dest=[]
		for ii in gunList:
			dest.append('\x00'+str(unichr(int(ii)))) # append gun number

	pref='\x40\x03\x05' # new game code

	for ii in range(3):
		for gun in dest:
			x = xbee.send('tx', dest_addr=gun, data=pref)
		time.sleep(0.8)
	pass


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def drawRect(_window, _startX, _startY, _w, _h, _color):
	pygame.draw.rect(_window, _color, [_startX, _startY, _w, _h])

def drawNormalText(_window, text, font, size,  _x, _y):
	textObj = pygame.font.Font(font,size)
	TextSurf = textObj.render(text, True, black)
	TextRect = TextSurf.get_rect()
	TextRect.center = ((_x),(_y))
	_window.blit(TextSurf, TextRect)

def pyGameButton(_window, _caption, _fontSize, _fontInc, _colorInactive, _colorActive, _startX, _startY, _w, _h, _action = None):
	#get mouse pos
	mouse = pygame.mouse.get_pos()
	click = pygame.mouse.get_pressed()

	if _startX + _w > mouse[0] > _startX and _startY + _h > mouse[1] > _startY:
		drawRect(_window, _startX, _startY, _w, _h, _colorActive)
		drawNormalText(_window, _caption, defFont, _fontSize + _fontInc, ((_startX * 2)+_w)//2, ((_startY * 2) + _h)//2)
		
		if click[0] == 1 and _action != None:
			_action()

	else:
		drawRect(_window, _startX, _startY, _w, _h, _colorInactive)
		drawNormalText(_window, _caption, defFont, _fontSize, ((_startX * 2)+_w)//2, ((_startY * 2) + _h)//2)
	pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ BUTTON FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def silencerBool(_window = None):
	global silencer 
	silencer = not silencer
	time.sleep(0.1)
	pass

def newGameBool(_window = None):
	global setNewGame 
	setNewGame = not setNewGame
	time.sleep(0.1)
	pass

def addTime(_window = None):
	global timer 
	timer += 1
	time.sleep(0.1)
	pass

def removeTime(_window = None):
	global timer 
	if (timer - 1) > 0:
		timer -= 1
	time.sleep(0.1)
	pass

def AR():
	global silencer

	if silencer:
		package = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x05', '\x0F', '\xC8', '\x01', '\x03', '\x02', '\x04', '\x01', '\x14', '\x00', '\x02', '\x00', '\x00', '\x00', '\x00']
	else:
		package = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x05', '\x0F', '\xC8', '\x01', '\x03', '\x02', '\x04', '\x01', '\x14', '\x01', '\x01', '\x00', '\x00', '\x00', '\x00']
	
	pkg = ''.join(package)
	#radioProgram(pkg)

	pass

def SUB():
	global silencer

	if not silencer:
		package = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x05', '\x14', '\xC8', '\x02', '\x03', '\x06', '\x03', '\x01', '\x14', '\x01', '\x0A', '\x00', '\x00', '\x00', '\x00']
	else: 
		package = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x05', '\x14', '\xC8', '\x02', '\x03', '\x06', '\x03', '\x01', '\x14', '\x00', '\x0B', '\x00', '\x00', '\x00', '\x00']
	pkg = ''.join(package)
	#programGun(pkg)

def SNIPER():
	global silencer

	if not silencer:
		package = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x0A', '\x05', '\xC8', '\x00', '\x03', '\x00', '\x05', '\x01', '\x14', '\x01', '\xFA', '\x00', '\x00', '\x00', '\x00']
	else: 
		package = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x0A', '\x05', '\xC8', '\x00', '\x03', '\x00', '\x05', '\x01', '\x14', '\x00', '\xFB', '\x00', '\x00', '\x00', '\x00']
	pkg = ''.join(package)
	#programGun(pkg)
	pass

def LMG():
	global silencer
	#LMG
	if not silencer:
		package = ['\x06', '\xFF', '\x00', '\x02', '\x04', '\x00', '\x04', '\x32', '\xC8', '\x02', '\x03', '\x03', '\x08', '\x01', '\x14', '\x01', '\x29', '\x00', '\x00', '\x00', '\x00']
	else: 
		package = ['\x06', '\xFF', '\x02', '\x02', '\x04', '\x00', '\x04', '\x32', '\xC8', '\x02', '\x03', '\x03', '\x08', '\x01', '\x14', '\x00', '\x2A', '\x00', '\x00', '\x00', '\x00']
	pkg = ''.join(package)
	#programGun(pkg)
	pass

def TDM():
	global setNewGame
	command = ['\x07', '\xFF', '\x1C', '\x00', '\x00', '\x00', '\x00', '\x45', '\x00', '\x00', '\x00', '\x00', '\x1A', '\x00', '\x03', '\x05', '\x82', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	#programGun(cmd, setNewGame)
	pass

def FFA():
	global setNewGame

	command = ['\x07', '\xFF', '\x1C', '\x00', '\x00', '\x00', '\x04', '\x45', '\x00', '\x00', '\x00', '\x00', '\x00', '\x00', '\x03', '\x05', '\x6C', '\x00', '\x00', '\x00', '\x00']
	cmd = ''.join(command)
	#programGun(cmd, setNewGame)
	pass

def scoreDisplay(_window, _offsetX = 0, _offsetY = 0):

	global killMatrix
	global killList
	_blueScore = 0
	_redScore = 0
	packetData = []

	# Need to have packet captures
	for _i in range(len(packetHandler.captures)):
		packet = packetHandler.captures[0]
		if (packet.frame.msdu[2] == 32 or packet.frame.msdu[2] == 37) and packet.frame.msdu[4] < 50 and len(packet.frame.msdu) > 4:
			packetData.append([packet.frame.msdu[3], packet.frame.msdu[4], packet.frame.timestamp])
		del packetHandler.captures[0]

	print(packetData)
	if len(packetData) > 0:
		packetData.sort()

		timeDeath = np.diff(np.array(packetData)[:,2]) # time between kills
		killer = np.array(packetData)[:,1] #array for gun killers
		victim = np.array(packetData)[:,0] # array of guns killed

		for kill in range(len(killer)):
			print(kill)
			if kill > 0:
				if victim[kill] == victim[kill - 1] and abs(timeDeath[kill - 1]) < 100000:
					#double kill found
					continue #move to next loop
				#Need to work out how to kill base
				if victim[kill] > largestGunNumber:
					print("BASE KILL")
					#this is a base kill
					self.baseKill = True
					if victim[kill] % 2 == 0:
						#blue base killed
						self.winner = 'red'
					else:
						self.winner = 'blue'
					continue
			#add kill to the passed in data Structs
			killMatrix[int(victim[kill]), int(killer[kill])] += 1
			killList[int(killer[kill])] += 1
	#display the top players
	sortedList = []
	for gun in range(len(killList)):
		sortedList.append((killList[gun], gun))

	sortedList.sort(reverse = True)
	print(sortedList)
	drawNormalText(_window, "- Top Players -", defFont, 20,300 + _offsetX,75 + _offsetY)
	for x in range(5):
		topGuns = str(x+1)  + ' : ' + str(int(sortedList[x][0]))
		drawNormalText(_window, topGuns, defFont, 20,300 + _offsetX,125+(25*x) + _offsetY)
	#end Scoreing

	for gun in range(len(killList)):
		if gun % 2 == 0:
			_blueScore += killList[gun]
		else:
			_redScore += killList[gun]

	bString = 'Blue: ' + str(int(_blueScore))
	drawNormalText(_window, bString, defFont, 20,100+ _offsetX,100+_offsetY)

	bString = 'Red: ' + str(int(_redScore))
	drawNormalText(_window, bString, defFont, 20,500+_offsetX,100+_offsetY)

	pass

def displayTopPlayers():

	pass


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ WINDOW FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def gunMenu(_window = None):
	#make a new screen?
	gunScreen = pygame.display.set_mode((disp_height,disp_width))
	pygame.display.set_caption(companyName)

	settingGuns = True

	while settingGuns:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.QUIT:
				quit()
				mainScreen()

		gunScreen.fill(white)
		drawNormalText(gunScreen, "Gun Mode Controls", defFont,  30, 300, 25)
		menuFont = 12

		if silencer:
			pyGameButton(gunScreen, "Silencer: ON", menuFont, 4, green, brightGreen, 15, 15, button_w, button_h, silencerBool)
		else:
			pyGameButton(gunScreen, "Silencer: OFF", menuFont, 4, red, brightRed, 15, 15, button_w, button_h, silencerBool)
		
		pyGameButton(gunScreen, "Assult Rifle", menuFont, 4, green, brightGreen, 100, 100, button_w, button_h, AR)
		pyGameButton(gunScreen, "Sub Machine Gun", menuFont-2, 2, green, brightGreen, 250, 100, button_w, button_h, SUB)
		pyGameButton(gunScreen, "Sniper", menuFont, 4, green, brightGreen, 100, 200, button_w, button_h, SNIPER)
		pyGameButton(gunScreen, "LMG", menuFont, 4, green, brightGreen, 250, 200, button_w, button_h, LMG)
		pyGameButton(gunScreen, "Return", menuFont+4, 4, red, brightRed, 450, 225, button_w, button_h, mainScreen)
		
		pygame.display.update()
		clock.tick(60)
	pass

def gameMenu(_window = None):
	gameScreen = pygame.display.set_mode((disp_height,disp_width))
	pygame.display.set_caption(companyName)
	global setNewGame
	settingGame = True

	while settingGame:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.QUIT:
				quit()
				mainScreen()

		gameScreen.fill(white)
		drawNormalText(gameScreen, "Gun Mode Controls", defFont,  30, 300, 25)
		menuFont = 12

		
		if setNewGame:
			pyGameButton(gameScreen, "New Game: On", menuFont, 4, green, brightGreen, 15, 15, button_w, button_h, newGameBool)
		else:
			pyGameButton(gameScreen, "New Game: Off", menuFont, 4, red, brightRed, 15, 15, button_w, button_h, newGameBool)
		
		pyGameButton(gameScreen, "TDM", menuFont, 4, green, brightGreen, 100, 100, button_w, button_h, TDM)
		pyGameButton(gameScreen, "FFA: No Respawn", menuFont-2, 2, green, brightGreen, 250, 100, button_w, button_h, FFA)
		pyGameButton(gameScreen, "FFA: Respawn (WIP)", menuFont-2, 2, green, brightGreen, (350//2), 200, button_w, button_h, None)
		pyGameButton(gameScreen, "Return", menuFont+4, 4, red, brightRed, 450, 225, button_w, button_h, mainScreen)
		
		pygame.display.update()
		clock.tick(60)
	pass

def scoreScreen(_window = None):
	scorePage = pygame.display.set_mode((disp_height,disp_width))
	pygame.display.set_caption(companyName)
	stopGame = False

	displayScore = True
	while not stopGame:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.QUIT:
				quit()
				mainScreen()

		scorePage.fill(white)
		drawNormalText(scorePage, "END OF GAME", defFont,  30, 300, 25)
		menuFont = 12

		#end game
		pyGameButton(scorePage, "Return to Main", menuFont+4, 4, red, brightRed, 450, 225, button_w*1.3, button_h, mainScreen)
		time.sleep(.2)
		scoreDisplay(scorePage, 0, -20)

		pygame.display.update()
		clock.tick(60)
	pass		


def gameTime(_window = None):
	gameDisplay = pygame.display.set_mode((disp_height,disp_width))
	pygame.display.set_caption(companyName)

	global timer
	global packetHandler
	global killMatrix
	global killList


	killList = np.zeros(30)

	stopGame = False
	blueScore = 0
	redScore = 0

	newGame()
	startTime = pygame.time.get_ticks()
	while not stopGame:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.QUIT:
				scoreScreen()

		gameDisplay.fill(white)
		drawNormalText(gameDisplay, "Score", defFont,  30, 300, 25)
		menuFont = 12
		currentTime = (pygame.time.get_ticks() - startTime) // 1000
		timeLeft = (timer * 60) - currentTime
		minLeft = timeLeft // 60
		secLeft = (timeLeft - (minLeft * 60))
		if secLeft < 10:
			passString = 'Time Left: ' + str(minLeft) + ':0' + str(secLeft)
		else:
			passString = 'Time Left: ' + str(minLeft) + ':' + str(secLeft)

		if timeLeft < 0:
			scoreScreen()

		drawNormalText(gameDisplay, passString, defFont, 20,300,50)
		#end game
		pyGameButton(gameDisplay, "End Game", menuFont+4, 4, red, brightRed, 450, 225, button_w, button_h, scoreScreen)
		time.sleep(.2)
		scoreDisplay(gameDisplay)
		#parse score and do simple display of team on team and best 5 guns

		
		pygame.display.update()
		clock.tick(60)
	pass

def StartGame(_window = None):
	startScreen = pygame.display.set_mode((disp_height,disp_width))
	pygame.display.set_caption(companyName)
	global timer
	settingUp = True
	timer = 5
	while settingUp:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.QUIT:
				quit()
		startScreen.fill(white)
		drawNormalText(startScreen, "Start Game", defFont,  30, 300, 25)
		menuFont = 12

		drawNormalText(startScreen, "Select Time (Minutes)", defFont, 16,  300, 100)
		drawNormalText(startScreen, str(timer), defFont, 16,  310, 150)
		
		pyGameButton(startScreen, "( + )", 18, 4, green, brightGreen, 350, 115, 75, button_h, addTime)
		pyGameButton(startScreen, "( - )", 18, 4, red, brightRed, 200, 115, 75, button_h, removeTime)
		pyGameButton(startScreen, "Start Game?", 22, 4, blue, brightBlue, 200, 200, 200, button_h, gameTime)
		pyGameButton(startScreen, "Return", menuFont+4, 4, red, brightRed, 450, 225, button_w, button_h, mainScreen)
		
		pygame.display.update()
		clock.tick(60)
	pass

def mainScreen(_window = None):
	gameScreen = pygame.display.set_mode((disp_height,disp_width))
	pygame.display.set_caption(companyName)

	global killMatrix
	killMatrix = np.zeros((30,30))

	global killList
	killList = np.zeros(30)


	main = True
	while main:
		for event in pygame.event.get():
			print(event)
			if event.type == pygame.QUIT:
				quit()
				return True

		gameScreen.fill(white)

		#Title of Screen
		drawNormalText(gameScreen, "Laser Tag Controls", defFont,  30, 300, 25)

		#makes buttons highlight

		menuFont = 14
		pyGameButton(gameScreen, "Gun Mode", menuFont, 4, green, brightGreen, 75, 100, button_w, button_h, gunMenu)
		pyGameButton(gameScreen, "Game Mode", menuFont, 4, green, brightGreen, 225, 100, button_w, button_h, gameMenu)
		pyGameButton(gameScreen, "Start Game", menuFont, 4, blue, brightBlue, 75, 200, button_w, button_h, StartGame)
		pyGameButton(gameScreen, "End Game", menuFont, 4, red, brightRed, 225, 200, button_w, button_h, None) #endGame
		pyGameButton(gameScreen, "Exit", menuFont+4, 4, red, brightRed, 400, 150, button_w, button_h, quitGame)
		
		pygame.display.update()
		clock.tick(60)
	return False
	pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FUNCTIONS
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def quitGame():
	pygame.quit()
	quit()
	pass
#main functions

def main():
	exitGame = False

	#TODO: CHECK SNIFFER LOADING
	#Need to start packet Handeler here?
	args = arg_parser()
	args.channel=int(12)

	global packetHandler

	packetHandler = PacketHandler()
	packetHandler.enable()

	if args.annotation is not None:
		packetHandler.setAnnotation(args.annotation)

	handlers = [packetHandler]

	def handlerDispatcher(timestamp, macPDU):
		if len(macPDU) > 0:
			packet = SniffedPacket(macPDU, timestamp)
			for handler in handlers:
				handler.handleSniffedPacket(packet)

	snifferDev = CC2531EMK(handlerDispatcher, args.channel)
	snifferDev.start()

	while not exitGame:
		exitGame = mainScreen(None)

	pygame.quit()
	quit()

if __name__ == "__main__":
	main()
