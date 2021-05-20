import time
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

digitColors={
	1:e.Escapes.Color8.Foreground.cyan,
	2:e.Escapes.Color8.Foreground.magenta,
	3:e.Escapes.Color8.Foreground.red,
	4:e.Escapes.Color8.Foreground.yellow,
	5:e.Escapes.Color8.Foreground.green,
	6:e.Escapes.Style.dim+e.Escapes.Color8.Foreground.cyan,
	7:e.Escapes.Style.dim+e.Escapes.Color8.Foreground.magenta,
	8:e.Escapes.Style.dim+e.Escapes.Color8.Foreground.red,
	9:e.Escapes.Style.dim+e.Escapes.Color8.Foreground.yellow,
	0:e.Escapes.Style.dim+e.Escapes.Color8.Foreground.green
}

try:
	startTime=time.perf_counter() #for calculating avg later

	tf.fillWithSpaces()
	tf.moveCursor(home=True)
	tf.echoKeys(disable=True)
	tf.cursorVisibility(hide=True)
	tf.stopSleep()

	currentDigit=0
	currentChar=0

	size=tf.getTerminalSize()
	minimumFrameDelta=float(argv[1])

	saver=tf.CursorSaver()
	currentFrameStartTime=time.perf_counter()

	digits=""

	try:
		f.remove("pi.txt")
	except:
		pass

	for digit in generatePi():
		currentFrameEndTime=time.perf_counter()
		currentFrameRenderTime=currentFrameEndTime-currentFrameStartTime

		if currentFrameRenderTime<minimumFrameDelta:
			time.sleep(minimumFrameDelta-currentFrameRenderTime)

		currentFrameStartTime=time.perf_counter()

		digits+=str(digit) #add digit to cache

		tf.print(e.Escapes.Style.reset+
				 digitColors[digit]+
				 str(digit)
				)

		if currentDigit==0: #print decimal point
			tf.changeStyle(bold=True,color8="blue",foreground=True)
			tf.print(".")

			currentChar+=1
			digits+="." #add dp to cache

		currentDigit+=1
		currentChar+=1

		if currentChar%size["columns"]==0:
			tf.print("\n\n")
			tf.changeStyle(reset=True)
			tf.moveCursor(up=1)
			tf.clear(line=True)

		saver.save(0)
		tf.moveCursor(to={"column":0,"row":size["rows"]})
		tf.changeStyle(reset=True)
		tf.changeStyle(invert=True,bold=True,italic=True)
		tf.clear(line=True)

		timeSinceStart=time.perf_counter()-startTime
		avgCompTime=timeSinceStart/currentDigit
		avgDigitsPerSec=currentDigit/timeSinceStart

		tf.print("currently at "+str(currentDigit)+
			"th digit of pi. Avg digits per second: "+str(avgDigitsPerSec)+
			"d/s.")
		saver.load(0)

except KeyboardInterrupt:
	from math import floor
	tf.changeStyle(reset=True)
	tf.moveCursor(to={"column":0,"row":size["rows"]})
	tf.clear(line=True)
	digits=f.splitString(digits,(currentDigit//100)+1)
	for digit in f.everyIndexInList(digits):
		f.appendTo("pi.txt",digits[digit])
		tf.moveCursor(to={"column":0,"row":size["rows"]})
		tf.print(str(digit+1)+" % done saving ("+
			str((digit*((currentDigit//100)+1))+len(digits[digit]))+"/"+
			str(currentDigit+1)+")") #the +1 is for the d.p

	tf.cursorVisibility(show=True)
	tf.moveCursor(to={"column":0,"row":size["rows"]})
	tf.print(e.Escapes.Style.reset)
	tf.clear(line=True)
	tf.echoKeys(enable=True)
	exit(0)