'''
PyInvaders - PyS60 Camera Tracking Game

Marcel Pinheiro Caraciolo <caraciol@gmail.com>
Marlon Luz <marlon.luz@gmail.com> (Author of the JavaME Real Invaders Game)


0.1  2009-02-19 Initial Creation.
'''

#@TODO :  Remove Error when quiting the application, change the icons, use some extension lib to change the softkey labels


import sys
import appuifw
import graphics
import e32
import camera
import random
import time

VERSION = '0.1'

ICON_FILE = u'E:\\Python\\res\\carman_icons.mif'
SPLASH_FILE = u'E:\\Python\\res\\splash.jpg'
TARGET_IMG_FILE = u'E:\\Python\\res\\target.PNG'
UFO_IMG_FILE = u'E:\\Python\\res\\ufo2.PNG'
TOP_IMG_FILE = u'E:\\Python\\res\\top2.jpg'
BOTTON_IMG_FILE = u'E:\\Python\\res\\botton2.jpg'
SHOT_IMG_FILE = u'E:\\Python\\res\\ray.PNG'

RGB_BLACK = (0, 0, 0)

buf = None
canvas = None
keyboard = None
screenSize = None
game = None
gg = None

#Cenario images
shotImg = None
trans_shotImg  = None
targetImg = None
ufoImg = None


#Bool
DRAWING = False

layerGroup = {"cameraSize": (240,180),
			  "cameraPosition": (0,40)}



def handle_redraw(dummy=(0, 0, 0, 0)):
    if not buf:
        return
    canvas.blit(buf)

def handle_camera(img):
	if not img:
		return
	
	buf.blit(img,target=layerGroup["cameraPosition"])
	buf.blit(targetImg,target=((layerGroup["cameraSize"][0]/2 - targetImg.size[0]/2) + layerGroup["cameraPosition"][0], (layerGroup["cameraSize"][1]/2 - targetImg.size[1]/2) + layerGroup["cameraPosition"][1]))
	if DRAWING:
		buf.blit(trans_shotImg,target=(screenSize[0]/2 - shotImg.size[0], layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1] - shotImg.size[1]))
		buf.blit(shotImg,target=(screenSize[0]/2 - shotImg.size[0], layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1] - shotImg.size[1]))	
	handle_redraw(())

	
class Ufo(object):
		def __init__(self,maxFarAwayXFromTarget,maxFarAwayYFromTarget,minFarAwayFromTarget,maxUFOSpeed):
			self.maxFarAwayXFromTarget = random.randrange(0,maxFarAwayXFromTarget) + minFarAwayFromTarget
			self.maxFarAwayYFromTarget = random.randrange(0,maxFarAwayYFromTarget) + minFarAwayFromTarget
			self.minFarAwayFromTarget = minFarAwayFromTarget
			self.frameWidth,self.frameHeight  = ufoImg.size[0]/8 , ufoImg.size[1]
			print self.frameWidth,self.frameHeight
			self.isAlive = True
			self.speed = 0
			while self.speed == 0:
				self.speed = random.randrange(0,maxUFOSpeed)
			self.aliveFrameSequence = [0,2,1]
			

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
		self.ufosCountDown = 0
		self.totalUfosLevel = 10
		self.level = 1
		self.maxUfoScreen = 5
		self.maxUFOSpeed = 4
		self.minFarAwayFromTarget = 20;
		self.maxFarAwayXFromTarget = 100;
		self.maxFarAwayYFromTarget = 60;
		self.ufoList = []
	
	def createUfos(self):
		for i in range(self.maxUfoScreen):
			self.ufoList.append(Ufo(self.maxFarAwayXFromTarget,self.maxFarAwayYFromTarget,self.minFarAwayFromTarget,self.maxUFOSpeed))
		
	def startGame(self):
		self.createUfos()
		gg.drawMain()
		gg.start_camera()
	
	
class GameGraphics(object):
	def __init__(self):
		global shotImg, trans_shotImg, targetImg, ufoImg
		#Initialize the components
		self.topImg =  graphics.Image.open(TOP_IMG_FILE)
		self.bottonImg =  graphics.Image.open(BOTTON_IMG_FILE)
		#Dealing with shot images is different from the others.
		shotImg =  graphics.Image.open(SHOT_IMG_FILE)
		trans_shotImg = shotImg.transpose(graphics.FLIP_LEFT_RIGHT)
		targetImg = graphics.Image.open(TARGET_IMG_FILE)
		ufoImg =  graphics.Image.open(UFO_IMG_FILE)
	
	def drawCockpit(self):
		buf.blit(self.topImg)
		buf.blit(self.bottonImg,target=(0,layerGroup["cameraSize"][1] + layerGroup["cameraPosition"][1]))	
		
	def start_camera(self):
		camera.start_finder(handle_camera,size=layerGroup["cameraSize"])
	
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
		
		global game
		game = GameLogic()
		
		global gg
		gg = GameGraphics()
		
		global buf
		buf=graphics.Image.new(screenSize)
		
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
		app_lock.signal()
		#appuifw.app.set_exit()
		
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


