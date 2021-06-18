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
	# prepare the screen
	tf.fillWithSpaces()
	tf.moveCursor(home=True)
	tf.echoKeys(disable=True)
	tf.cursorVisibility(hide=True)

	#set the progress variables
	currentDigit=0
	currentChar=0

	size=tf.getTerminalSize()
	saver=tf.CursorSaver()
	digits=""

	try:
		frameLimiter=tf.FramerateLimiter(1/int(argv[1]))
	except ZeroDivisionError:
		frameLimiter=tf.FramerateLimiter(None)
	frameChecker=tf.FramerateTracker()

	for digit in generatePi():
		if not currentDigit==0:
			frameLimiter.endFrame()
			frameLimiter.delayTillNextFrame()
			frameChecker.endFrame()

		frameChecker.startFrame()
		frameLimiter.startFrame()

		digits+=str(digit) #add digit to cache

		tf.print(
					tf.style(reset=True)+
					digitColors[digit]+
					str(digit)
				)

		if currentDigit==0: #print decimal point
			tf.print(tf.style(bold=True,color8="blue",foreground=True)+".")
			currentChar+=1
			digits+="." #add dp to cache

		# update progress
		currentDigit+=1
		currentChar+=1

		# check if at end of line, move all pi digits up if so
		if currentChar%size["columns"]==0:
			tf.print("\n\n")
			tf.changeStyle(reset=True)
			tf.moveCursor(up=1)
			tf.clear(line=True) #clear the now higher progress

		saver.save(0) #save the position to the next pi digit

		tf.moveCursor(to={"column":0,"row":size["rows"]}) #move to bottom left
		tf.changeStyle(reset=True) #clear the pi digit color
		tf.changeStyle(invert=True,bold=True,italic=True) #get the progress bar style
		tf.clear(line=True) #clear the old progress bar

		#draw progress bar
		tf.print("currently at "+str(currentDigit)+
			"th digit of pi. Avg digits per second: "+str(frameChecker.calculateAverageFPS())+
			"d/s.")

		saver.load(0) #go back to the position of pi

except KeyboardInterrupt:
	from math import floor
	tf.changeStyle(reset=True)
	tf.moveCursor(to={"column":0,"row":size["rows"]}) #go to bottom left
	tf.clear(line=True) #clear progress bar

	digits=f.splitString(digits,(currentDigit//100)+1) #split digits into a 100 chunks

	for digit in f.everyIndexInList(digits): #save the digits
		f.appendTo("pi.txt",digits[digit]) #append the next chunk
		tf.moveCursor(to={"column":0,"row":size["rows"]}) #go to bottom left
		#draw saving progress bar
		tf.print(str(digit+1)+" % done saving ("+
			str((digit*((currentDigit//100)+1))+len(digits[digit]))+"/"+
			str(currentDigit+1)+")") #the +1 is for the d.p

	# make the screen normal again
	tf.cursorVisibility(show=True)
	tf.echoKeys(enable=True)

	tf.moveCursor(to={"column":0,"row":size["rows"]}) #go to bottom left
	tf.changeStyle(reset=True)
	tf.clear(line=True) #clear the progress bar
	exit(0)
