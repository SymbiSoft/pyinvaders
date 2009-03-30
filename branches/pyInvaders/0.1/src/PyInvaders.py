'''
PyInvaders v0.1 - PyS60 Camera Tracking Game

Copyright (c) 2009 Marcel Pinheiro Caraciolo, Marlon Luz 

Marcel Pinheiro Caraciolo <caraciol@gmail.com>
Marlon Luz <marlon.luz@gmail.com> (Author of the JavaME Real Invaders Game)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License

0.1  2009-02-19 Initial Creation.
'''


#@TODO :  SoftKey Labels, transparency gifs, Ufo threading, 


import sys
import appuifw
import graphics
import e32
import camera
import random
import time
import key_codes

VERSION = '0.1'

ICON_FILE = u'E:\\Python\\res\\carman_icons.mif'
SPLASH_FILE = u'E:\\Python\\res\\splash.jpg'
TARGET_IMG_FILE = u'E:\\Python\\res\\target.PNG'
UFO_IMG_FILE = u'E:\\Python\\res\\ufo2.PNG'
TOP_IMG_FILE = u'E:\\Python\\res\\top2.jpg'
BOTTON_IMG_FILE = u'E:\\Python\\res\\botton2.jpg'
SHOT_IMG_FILE = u'E:\\Python\\res\\ray.PNG'

RGB_BLACK = (0, 0, 0)
RGB_WHITE = (255,255,255)

WIN,LOST = 1,0

#Instances
buf = None
canvas = None
keyboard = None
screenSize = None
game = None
gg = None
ufoList = None
timer = None
timeGame = None
tracking = None
firstCurrentTime = None
lastShotTime = None

#Drawing
ufoImg = None
targetImg = None


#Bool
DRAWING = True
FIRST_TIME = False

layerGroup = {"cameraSize": (240,180),
			  "cameraPosition": (0,40),
			  "sideImageTracking":(100,100)}



def refreshScreen(dummy=(0, 0, 0, 0)):
    if not buf:
        return
    canvas.blit(buf)

	
# Snippet code based on http://larndham.net/service/pys60/getpixel.py
def getPixels(im, bpp=24):
    import struct, zlib
    im.save('C:\\pixels.png', bpp=bpp, compression='no')
    f = open('C:\\pixels.png', 'rb')
    f.seek(8+8+13+4)
    chunk = []
    while 1:
        n = struct.unpack('>L', f.read(4))[0]
        if n==0: break  # 'IEND' chunk
        f.read(4) # 'IDAT'
        chunk.append(f.read(n))
        f.read(4)   # CRC
    f.close()
    return zlib.decompress(''.join(chunk))


def run(img):
	global FIRST_TIME, firstCurrentTime, lastShotTime
	if not img:
		return
	
	#@TODO : Check if it's to blit the box with all game image (buf) or all camera image (img).
	box = graphics.Image.new(layerGroup["sideImageTracking"], 'L')
	#This is a proccess that we can do one time. (Put somewhere!)
	x = (layerGroup["cameraSize"][0]/2) - (targetImg.size[0]/2) - layerGroup["sideImageTracking"][0]
	y = (layerGroup["cameraSize"][1]/2) - (layerGroup["sideImageTracking"][1] /2)
	
	if FIRST_TIME:
		#print x,y
		#print x + layerGroup["sideImageTracking"][0], y +layerGroup["sideImageTracking"][1]
		firstCurrentTime = time.clock()
		lastShotTime = time.clock()
		FIRST_TIME = False
	
	game.checkEndOfGame()
	game.keyInput()

	
	box.blit(img, source=((x,y),(x + layerGroup["sideImageTracking"][0], y +layerGroup["sideImageTracking"][1])))
	data = getPixels(box, 8)
	
	buf.blit(img,target=layerGroup["cameraPosition"])
	gg.drawTarget()
	gg.drawShot(keyPressed=False)
	
	gg.drawUfo(ufoList[0])
	gg.drawUfo(ufoList[1])
	gg.drawStatusLevel()
	refreshScreen(())

class Tracking(object):
	pass
	
class Ufo(object):
		def __init__(self,position,ufoImgSize,maxFarAwayXFromTarget,maxFarAwayYFromTarget,minFarAwayFromTarget,maxUFOSpeed):
			self.position = position
			self.maxFarAwayXFromTarget = random.randrange(0,maxFarAwayXFromTarget) + minFarAwayFromTarget
			self.maxFarAwayYFromTarget = random.randrange(0,maxFarAwayYFromTarget) + minFarAwayFromTarget
			self.minFarAwayFromTarget = minFarAwayFromTarget
			self.frameWidth,self.frameHeight  = ufoImgSize[0]/8 , ufoImgSize[1]
			self.isAlive = True
			self.speed = 0
			self.count_frame_live = 0
			self.countFrameExplosions = 0
			self.count_frame_explosion = 0
			self.newXY = (0,0)
			while self.speed == 0:
				self.speed = random.randrange(0,maxUFOSpeed)
			self.frameSequence = self.setAliveFrameSequence()
			self.currentFrame = random.choice(self.frameSequence)
			
			
		def setAliveFrameSequence(self):
			return [0,2,1]
		
		def setExplosionFrameSequence(self):
			return [7,6,5,4,3]
		
		def crash(self,newXY):
			self.isAlive = False
			self.frameSequence = self.setExplosionFrameSequence()
			self.countFrameExplosions = 0
			self.newXY = newXY
		
		def getFrame(self):
			if self.isAlive:
				self.count_frame_live+=1
				if self.count_frame_live == 3:
					self.count_frame_live = 0
					self.currentFrame = self.frameSequence[((self.frameSequence.index(self.currentFrame) + 1) % 3)]
			else:
				if self.count_frame_explosion == 3:
					self.count_frame_explosion = 0
					self.currentFrame = self.frameSequence[((self.frameSequence.index(self.currentFrame) + 1) % 5)]
				self.countFrameExplosions+=1
				if self.countFrameExplosions== 4:
					self.frameSequence = self.setAliveFrameSequence()
					self.isAlive = True
					self.position = (self.position[0] + self.newXY[0] , self.position[1] + self.newXY[1])
					
			return (self.currentFrame * self.frameWidth,0,self.frameWidth*self.currentFrame+self.frameWidth,self.frameHeight)
			
		def getPosition(self):
			return self.position
		
		def getFrameSize(self):
			return self.frameWidth,self.frameHeight

class SplashScreen(object):
	def __init__(self):
		self.splash=graphics.Image.open(SPLASH_FILE)
		
	def execute(self):
		global buf,canvas
		buf.clear(0)
		buf.blit(self.splash)
		canvas.blit(buf)
		e32.ao_sleep(2) #Sleeps for two seconds
		self.splash = None #kill it.

class Keyboard(object):
    def __init__(self,onevent=lambda:None):
        self._keyboard_state={}
        self._downs={}
        self._onevent=onevent
    def handle_event(self,event):
        if event['type'] == appuifw.EEventKeyDown:
            code=event['scancode']
            if not self.is_down(code):
                self._downs[code]=self._downs.get(code,0)+1
            self._keyboard_state[code]=1
        elif event['type'] == appuifw.EEventKeyUp:
            self._keyboard_state[event['scancode']]=0
        self._onevent()
    def is_down(self,scancode):
        return self._keyboard_state.get(scancode,0)
    def pressed(self,scancode):
        if self._downs.get(scancode,0):
            self._downs[scancode]-=1
            return True
        return False

class GameLogic(object):
	def __init__(self):
		global ufoList
		self.ufosCountDown = 0
		self.totalUfosLevel = 10
		self.level = 1
		self.timeGame = 60
		self.maxUFOScreen = 2 #Default Value: 5
		self.maxUFOSpeed = 4
		self.minFarAwayFromTarget = 20;
		self.maxFarAwayXFromTarget = 100;
		self.maxFarAwayYFromTarget = 60;
		ufoList = []
		self.timeRemain = 0
		self.ufosCountDown = self.totalUfosLevel
	
	def createUfos(self):
		for i in range(self.maxUFOScreen):
			position = (random.randrange(0,layerGroup["cameraSize"][0]), random.randrange(0,layerGroup["cameraSize"][1]))
			ufoList.append(Ufo(position,ufoImg.size,self.maxFarAwayXFromTarget,self.maxFarAwayYFromTarget,self.minFarAwayFromTarget,self.maxUFOSpeed))
		
	def startGame(self):
		global FIRST_TIME
		FIRST_TIME = True
		self.createUfos()
		gg.drawMain()
		gg.start_camera()
	
	def keyInput(self):
		global lastShotTime
		if keyboard.pressed(key_codes.EScancodeSelect):
			#if int(time.clock() - lastShotTime) > 2:
			#	lastShotTime = time.clock()
			gg.drawShot(keyPressed=True)
			for i in range(self.maxUFOScreen):
				if ufoList[i].isAlive and gg.detectCollision(ufoList[i]):
					newPosition = random.randrange(0,4)
					if newPosition == 0:
						ufoList[i].crash((+layerGroup["cameraSize"][0],-layerGroup["cameraSize"][1]))
					elif newPosition == 1:
						ufoList[i].crash((-layerGroup["cameraSize"][0],-layerGroup["cameraSize"][1]))
					elif newPosition == 2:
						ufoList[i].crash((-layerGroup["cameraSize"][0],+layerGroup["cameraSize"][1]))
					elif newPosition == 3:
						ufoList[i].crash((+layerGroup["cameraSize"][0],+layerGroup["cameraSize"][1]))
					self.ufosCountDown-=1
					break
		elif keyboard.pressed(key_codes.EScancodeLeftSoftkey):
			if appuifw.query(u"Are you sure about restart the game ?", "query"):
				gg.stop_camera()
				self.nextLevel()
		
	
	def nextLevel(self):
		global ufoList
		self.totalUfosLevel = 10
		self.level = 1
		self.ufosCountDown = self.totalUfosLevel
		ufoList = []
		self.startGame()
		
		
	def checkEndOfGame(self):
		#timeRemain = self.timeGame - int(time.clock() - firstCurrentTime)
		self.timeRemain = 10
		if self.ufosCountDown <= 0:
			self.totalUfosLevel = int(self.totalUfosLevel * 1.2)
			self.ufosCountDown = self.totalUfosLevel
			self.level+=1
			self.stopGame(WIN)
		elif self.timeRemain == 0:
			self.ufosCountDown = self.totalUfosLevel
			self.stopGame(LOST)
			
	def stopGame(self,gameStatus):
		pass
			
	
	
class GameGraphics(object):
	def __init__(self):
		global  ufoImg,targetImg
		#Initialize the components
		self.topImg =  graphics.Image.open(TOP_IMG_FILE)
		self.bottonImg =  graphics.Image.open(BOTTON_IMG_FILE)
		#Dealing with shot images is different from the others.
		self.shotImg =  graphics.Image.open(SHOT_IMG_FILE)
		self.trans_shotImg = self.shotImg.transpose(graphics.FLIP_LEFT_RIGHT)
		targetImg = graphics.Image.open(TARGET_IMG_FILE)
		ufoImg =  graphics.Image.open(UFO_IMG_FILE)
	
		self.shotNormal = False
		self.shotTrans = False
		self.shotLR = False
		self.totalLoopsShotNormal = 0
		self.totalLoopsShotTrans = 0
	
	
	def detectCollision(self,ufo):
		ufoLeft,ufoTop = ufo.getPosition()
		ufoRight,ufoBottom = (ufoLeft + ufo.getFrameSize()[0], ufoTop +  ufo.getFrameSize()[1])
		targetLeft,targetTop = ((layerGroup["cameraSize"][0]/2 - targetImg.size[0]/2) + layerGroup["cameraPosition"][0], (layerGroup["cameraSize"][1]/2 - targetImg.size[1]/2) + layerGroup["cameraPosition"][1])
		targetRight,targetBottom = (targetLeft + targetImg.size[0], targetTop + targetImg.size[1])
		if not ((targetLeft >= ufoRight) or (targetTop >= ufoBottom) or (targetRight <= ufoLeft) or (targetBottom <= ufoTop)):
			return True
		return False
 
	def drawStatusLevel(self):
		buf.rectangle((55,263,75,280), fill=RGB_BLACK)
		buf.rectangle((145,263,165,280), fill=RGB_BLACK)
		buf.rectangle((110,10,130,25), fill=RGB_BLACK)
		buf.text((60,275),u""+str(game.ufosCountDown),fill=(0,140,140))
		buf.text((150,278),u""+str(game.level),fill=(0,140,140))
		buf.text((115,20),u""+str(game.timeRemain),fill=(0,140,140))
	
	def drawCockpit(self):
		buf.blit(self.topImg)
		buf.blit(self.bottonImg,target=(0,layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1]))	
	
	def drawUfo(self,ufo):
		if DRAWING:
			buf.blit(ufoImg,source = ufo.getFrame(), target = ufo.getPosition())
	
	def stop_camera(self):
		camera.stop_finder()
		
	def start_camera(self):
		camera.start_finder(run,size=layerGroup["cameraSize"])
	
	def drawTarget(self):
		buf.blit(targetImg,target=((layerGroup["cameraSize"][0]/2 - targetImg.size[0]/2) + layerGroup["cameraPosition"][0], (layerGroup["cameraSize"][1]/2 - targetImg.size[1]/2) + layerGroup["cameraPosition"][1]))
	
	def drawShot(self,keyPressed=False):
		if DRAWING:
			if keyPressed:
				if self.shotLR:
					buf.blit(self.shotImg,target=(screenSize[0]/2 - self.shotImg.size[0], layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1] - self.shotImg.size[1]))
					self.shotNormal = True
					self.shotLR = False
				else:
					buf.blit(self.trans_shotImg,target=(screenSize[0]/2 - self.trans_shotImg.size[0], layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1] - self.trans_shotImg.size[1]))
					self.shotTrans = True
					self.shotLR = True
					
			else:
				if self.shotNormal:
					self.totalLoopsShotNormal+=1
					buf.blit(self.shotImg,target=(screenSize[0]/2 - self.shotImg.size[0], layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1] - self.shotImg.size[1]))
					if self.totalLoopsShotNormal == 2:
						self.shotNormal = False
						self.totalLoopsShotNormal = 0
			
				if self.shotTrans:
					self.totalLoopsShotTrans+=1
					buf.blit(self.trans_shotImg,target=(screenSize[0]/2 - self.trans_shotImg.size[0], layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1] - self.trans_shotImg.size[1]))
					if self.totalLoopsShotTrans == 2:
						self.shotTrans = False
						self.totalLoopsShotTrans = 0
		
	
	def drawMain(self):
		buf.clear(RGB_BLACK)
		self.drawCockpit()
		
class Main(object):
	def __init__(self):	
		self._options = []
		self._mainScreen = appuifw.Listbox([u""], lambda:None)
		
		global keyboard
		keyboard = Keyboard()
		
		appuifw.app.title=u"PyInvaders"
		appuifw.app.orientation="portrait"
		appuifw.app.screen="full"
		
		global canvas, screenSize
		canvas=appuifw.Canvas(event_callback=keyboard.handle_event, redraw_callback=None)
		appuifw.app.body=canvas
		screenSize = canvas.size
		
		global tracking
		tracking = Tracking()
		
		global game
		game = GameLogic()
		
		global timeGame
		timeGame = 60
		
		global gg
		gg = GameGraphics()
		
		global buf
		buf=graphics.Image.new(screenSize)
		
		global timer
		timer = e32.Ao_timer()
		
		self._splash = SplashScreen()
		self._splash.execute()
		
		appuifw.app.exit_key_handler = self.handle_quit
		self.game_start()
		
	
	def newGame(self):
		appuifw.app.exit_key_handler = self.handle_quit
		appuifw.app.screen = 'full'
		appuifw.app.body = canvas
		game.startGame()
	
	def showInstructions(self):
		pass
	
	def showAbout(self):
		appuifw.note(u"PyInvaders v"+VERSION+u"\n(c) Marcel Caraciolo")
	
	def showHighScore(self):
		pass
	
	def handle_options(self):
		{0: self.newGame,
		1: self.showInstructions,
		2: self.showAbout,
		3: self.showHighScore}[self._mainScreen.current()]()
	
	def handle_quit(self):
		if appuifw.app.body == self._mainScreen:
			app_lock.signal()
			#appuifw.app.set_exit()
		elif appuifw.app.body == canvas:
			gg.stop_camera()
			self.show_menu()
			
			
		
	def show_menu(self):
		appuifw.app.screen = 'normal'
		self._mainScreen = appuifw.Listbox(self._options, self.handle_options)
		appuifw.app.body = self._mainScreen

	def game_start(self):
		self.start_menu()
		self.show_menu()
	
	def initializeIcons(self):
		self._icon_newGame = appuifw.Icon(ICON_FILE, 16402, 16403)
		self._icon_instructions = appuifw.Icon(ICON_FILE, 16388, 16389)
		self._icon_about = appuifw.Icon(ICON_FILE, 16390, 16391)
		self._icon_highScore = appuifw.Icon(ICON_FILE, 16392, 16393)
	
	def start_menu(self):
		self.initializeIcons()
		self._options = [(u'New Game',u'',self._icon_newGame),(u'Instructions',u'',self._icon_instructions),
						(u'About',u'',self._icon_about), (u'High Scores',u'',self._icon_highScore)]
        
		
################################################################
main = Main()
app_lock = e32.Ao_lock()
app_lock.wait()


