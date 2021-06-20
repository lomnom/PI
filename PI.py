import time as t
import ESCAPES as e
import TERMINALFUNC as tf
from sys import argv
import FUNC as f

def generatePi():
	k,a,b,a1,b1 = 2,4,1,12,4
	while True:
		p,q,k = k * k, 2 * k + 1, k + 1
		a,b,a1,b1 = a1, b1, p*a + q*a1, p*b + q*b1
		d,d1 = a/b, a1/b1
		while d == d1:
			yield int(d)
			a,a1 = 10*(a % b), 10*(a1 % b1)
			d,d1 = a/b, a1/b1

def initScr():
	global homePos
	homePos=tf.getPosition()

	tf.echoKeys(disable=True)
	tf.cursorVisibility(hide=True)
	tf.raw(enable=True)

	tf.changeStyle(reset=True)
	tf.fillWithSpaces(saveCursor=False)
	tf.moveCursor(home=True)

def unInitScr():
	tf.cursorVisibility(show=True)
	tf.echoKeys(enable=True)
	tf.raw(disable=True)
	tf.moveCursor(to={"row":terminalSize["rows"],"column":0})
	tf.changeStyle(reset=True)
	tf.fillRowWithSpaces()
	tf.moveCursor(column=0)

def getColorPallete():
	global digitColors
	digitColors={
		"1":tf.style(color8="cyan",foreground=True),
		"2":tf.style(color8="magenta",foreground=True),
		"3":tf.style(color8="red",foreground=True),
		"4":tf.style(color8="yellow",foreground=True),
		"5":tf.style(color8="green",foreground=True),
		"6":tf.style(color8="cyan",foreground=True,dim=True),
		"7":tf.style(color8="magenta",foreground=True,dim=True),
		"8":tf.style(color8="red",foreground=True,dim=True),
		"9":tf.style(color8="yellow",foreground=True,dim=True),
		"0":tf.style(color8="green",foreground=True,dim=True)
	}

def calculatePi():
	global piDigits
	global piDigit
	global rateWatcher
	global calculatingPi
	global piGenerator

	if not "piGenerator" in globals():
		piGenerator=generatePi()

	if not "piDigit" in globals():
		piDigit=0

	if not "piDigits" in globals():
		piDigits=""

	calculatingPi=True

	rateWatcher=tf.FramerateTracker()

	while calculatingPi:
		rateWatcher.startFrame()

		digit=next(piGenerator)

		if not piDigit==0:
			rateWatcher.endFrame()
		rateWatcher.startFrame()

		piDigits+=str(digit)
		piDigit+=1

		rateWatcher.endFrame()

def getBar(text,moveCursor=False):
	global lastPosition
	renderString=""
	if moveCursor:
		renderString+=tf.cursor(to={"row":lastPosition[1]+1,"column":1})
	renderString+=tf.style(reset=True)
	renderString+=tf.style(italic=True,invert=True,bold=True)
	renderString+=tf.clearer(line=True)
	renderString+=text
	renderString+=tf.style(reset=True)

	return renderString

def pause():
	global calculatingPi, renderingPi
	global paused
	paused=True
	calculatingPi=False
	renderingPi=False

def unPause():
	global paused

	if paused:
		f.runInParallel([[calculatePi,()]])
		f.runInParallel([[renderPi,()]])

	paused=False

def stopAndStartPi():
	global paused

	if paused:
		unPause()
		tf.print(getBar("",moveCursor=True))
	else:
		pause()
		t.sleep(0.5)
		tf.print(getBar("paused",moveCursor=True))

def halt():
	global keyHandler

	pause()

	unInitScr()
	keyHandler.halt()

def bellButItTakesArgs(*args):
	tf.bell()

def initKeyHandler():
	global keyHandler

	keyHandler=tf.KeyHandler(
		{
			"p":[stopAndStartPi,()],
			"q":[exitMenu,()],
			"s":[save,()],
			"default":bellButItTakesArgs
		}
	)

def renderPi():
	global renderingPi
	
	renderingPi=True
	framerateLimiter=tf.FramerateLimiter(60)

	while renderingPi:
		framerateLimiter.startFrame()

		tf.print(getPiRender(getPiProgressBar()))

		framerateLimiter.endFrame()
		framerateLimiter.delayTillNextFrame()

def save():
	global piDigits, terminalSize
	global lastPosition
	global keyHandler
	pause()
	oldKeys=keyHandler.actions
	keyHandler.actions={"default":bellButItTakesArgs}

	t.sleep(1)

	digitChunks=f.splitString(piDigits,(len(piDigits)//100)+1) #split digits into a 100 chunks

	f.write("pi.txt","") #delete digits that are already there

	tf.moveCursor(to={"row":lastPosition[1]+1,"column":0})
	tf.clear(line=True)

	for digit in f.everyIndexInList(digitChunks): #save the digits
		f.appendTo("pi.txt",digitChunks[digit]) #append the next chunk
		tf.changeStyle(italic=True,invert=True,bold=True)
		tf.print("{}% done saving".format(digit+1))
		tf.moveCursor(to={"row":lastPosition[1]+1,"column":0}) #go to bottom left

	if pause:
		unPause()

	keyHandler.actions=oldKeys

def startKeyHandler():
	global keyHandler

	initKeyHandler()

	keyHandler.start()

def getPiRender(progressBar): #(gets render of unrendered)
	global terminalSize, lastPosition
	global piDigits
	global haltRenderPi
	global renderedDigits
	global digitColors
	global homePos

	renderString=""

	if not "lastPosition" in globals():
		lastPosition=[1,1]

	if not "renderedDigits" in globals():
		renderedDigits=0

	renderString+=tf.cursor(to={"row":lastPosition[1]+1,"column":0})
	renderString+=progressBar+tf.clearer(fromCursor=True,line=True,toEnd=True)+tf.style(reset=True)

	haltRenderPi=False

	unRenderedDigits=piDigits[renderedDigits:]
	renderedDigits=len(piDigits)

	if lastPosition[1]>=terminalSize["rows"]-1:
		renderString+=tf.cursor(to={"row":terminalSize["rows"]-1,"column":lastPosition[0]})
	else:
		renderString+=tf.cursor(to={"row":lastPosition[1],"column":lastPosition[0]})

	for digit in unRenderedDigits:
		renderString+=digitColors[digit]+digit+tf.style(reset=True)
		lastPosition[0]+=1

		if lastPosition[0]==terminalSize["columns"]+1:
			renderString+="\r\n\n"+progressBar+tf.style(reset=True)
			renderString+=tf.cursor(column=1)+tf.cursor(up=1)
			renderString+=tf.clearer(line=True)

			lastPosition[0]=1
			lastPosition[1]+=1

	return renderString

def getPiProgressBar():
	global piDigit,rateWatcher
	return getBar(
				"currently at {}th digit of pi. Avg digits per second: {}d/s."\
					.format(piDigit,rateWatcher.calculateAverageFPS())
				)

def saveAndHalt():
	save()
	halt()

def exitMenu():
	global keyHandler
	global oldActions
	pause()
	oldActions=keyHandler.actions
	keyHandler.actions={
		"y":[saveAndHalt,()],
		"n":[halt,()],
		"c":[cancelExit,()],
		"default":bellButItTakesArgs
	}

	tf.print(
		getBar("Do you want to save befor exiting? Press y/n to save/not save. Press c to cancel.",moveCursor=True)
		)

def cancelExit():
	global oldActions, keyHandler
	unPause()
	keyHandler.actions=oldActions

def main():
	global paused
	paused=False

	global piGenerator, terminalSize
	terminalSize=tf.getTerminalSize()

	getColorPallete()
	initScr()
	f.runInParallel([[calculatePi,()]])
	f.runInParallel([[renderPi,()]])
	startKeyHandler()

main()
