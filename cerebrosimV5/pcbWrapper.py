#import RPi.#GPIO as #GPIO
import time

####  Board class  ####

class Board:
	def __init__(self, num, pin):
		self.number = num
		self.serial_pin = pin
		if(num%2==0): #board 0: 0-39 pins, board1:40-79 pins, board2: 80-119 etc. 
			self.rowEnd = 39
		else:
			self.rowEnd = 79
		self.col = num/2
		return
	def set40(self, currentPin , pins):
		if(pins[self.rowEnd-currentPin][self.col]==1): #set pins in reverse 
			x=1#GPIO.output(self.serial_pin,#GPIO.HIGH)
		else:
			x=1#GPIO.output(self.serial_pin,#GPIO.LOW)
		return 
	
####  main methods ####
class pcbWrapper: 
	def __init__(self):

		self.cycleSec = 0.001
		 
		#create two sets of pins
		self.currentPins = [[0 for x in range(10)] for x in range(80)] #create pin array, 80 rows, 10 columns, pins[y][x], where 0<=x<=10, 0<=y<=80
		self.nextPins = [[0 for x in range(10)] for x in range(80)]

		#connect boards & serial pin
		self.numBoards = 20
		self.boards = []
		serials = [4,17,27,22,10,9,11,5,6,13,19,26,21,20,16,12,7,8,25,24]
		for x in range(0,20):
			self.boards.append(Board(x,serials[x])) #make all board/serial port associations 

		##GPIO/necessary setup 
		self.chan_list = range(0,30)
		self.shiftPin = [23]
		self.latchPin = [18]

		#GPIO.setmode(#GPIO.BCM) 
		#GPIO.setup(chan_list, #GPIO.OUT)
		return

	def start( self, mode ):
		self.mode = mode
		if(mode == 1): 	#init master arrays
			self.initBlock(self.currentPins,0,0,0,0) #(colstart, numcols, rowstart, numrows)
			self.initBlock(self.nextPins,4,3,0,3)
		elif(mode == 2): 	#init master arrays
			self.initBlock(self.currentPins,0,0,0,0) #(colstart, numcols, rowstart, numrows)
			self.initBlock(self.nextPins,4,2,39,2)
		elif(mode == 3): 	#init master arrays
			self.initBlock(self.currentPins,0,0,0,0) #(colstart, numcols, rowstart, numrows)
			self.initBlock(self.nextPins,1,3,0,3) 
		#self.refresh(self.nextPins)
		#self.printPins(self.currentPins)
		return self.currentPins

	def update(self):
		#self.clockCycle(self.cycleSec, self.latchPin) #latch currently loaded 
		self.copyArray(self.nextPins,self.currentPins)
		if(self.mode == 1): #do math
			self.linear(self.nextPins)
		elif(self.mode == 2): #do math
			self.ring(self.nextPins)
		elif(self.mode == 3): #do math
			self.split(self.nextPins)
		#self.refresh(self.nextPins) #set boards with next pattern
		#self.printPins(self.currentPins) 	
		return self.currentPins

	def refresh( self, pins ):
		for i in range(0,40): #40 clock cycles 
				for j in range(0,self.numBoards): #set serial pins for all boards 
					self.boards[j].set40(i,pins) 
				self.clockCycle(self.cycleSec, self.shiftPin) #shift in	
		return	 

	def stop(self):
		self.currentPins = [[0 for x in range(10)] for x in range(80)]
		self.nextPins = [[0 for x in range(10)] for x in range(80)]
		#GPIO.cleanup() ##?????? 
		return

	def clockCycle( self,cycle_time, pins ):
		#GPIO.output(pins, #GPIO.HIGH)
		#time.sleep((cycle_time/2))
		#GPIO.output(pins, #GPIO.LOW)
		#time.sleep((cycle_time/2))
		return

	def initBlock(self, pins, xbot, xsize, ybot, ysize ):
		for x in range(ybot, ysize+ybot):
			for y in range(xbot, xsize+xbot):
				pins[x][y] = 1
		return

	def initBlock_direct(self, pins, xbot, xtop, ybot, ytop, value ):
		for x in range(ybot, ytop):
			for y in range(xbot, xtop):
				pins[x][y] = value
		return

	def printPins( self, pins ):
		for row in range(len(pins)):
				print pins[len(pins)-row-1]
		return 

	def linear(self, pins):
		for row in reversed(range(len(pins))):
			for col in range(len(pins[row])):
				if(pins[row][col] == 1):
					if(row+1<len(pins)):
						pins[row+1][col] = 1
					pins[row][col] = 0
		return

	def split(self, pins):
	
		colstart = 10
		collength = 0
		rowlength = 0
		rowend = 0
		for row in reversed(range(len(pins))):
			for col in range(len(pins[row])):
				if(pins[row][col] == 1):
					if(col<=colstart and row>=rowend):
						colstart=col
						rowend=row
					elif(col>colstart and row==rowend):
						collength=collength+1
					elif(row<rowend and col==colstart):
						rowlength=rowend-row

		colend=colstart+collength
		rowstart=rowend-rowlength
		
		if(rowend==5 and rowstart==3):
			self.initBlock_direct(pins,max(0,colstart),min(colend+1,10),max(rowstart,0),min(rowend+2,80),1)
			self.initBlock_direct(pins,max(0,colstart),min(colend+2,10),max(rowstart,0),min(rowend+1,80),1)
			pins[rowstart][colstart]=0
		elif(rowend==6 and rowstart ==4):
			self.initBlock_direct(pins,max(0,colstart),min(colend+1,10),max(rowstart,0),min(rowend+2,80),1)
			self.initBlock_direct(pins,max(0,colstart+1),min(colend+3,10),max(rowstart-1,0),min(rowend,80),1)
			self.initBlock_direct(pins, colstart, colstart+2, rowstart-1, rowstart+1,0)
		elif(rowend==7 and rowstart ==5):
			self.initBlock_direct(pins,max(0,colstart),min(colend+1,10),max(rowstart,0),min(rowend+2,80),1)
			self.initBlock_direct(pins,max(0,colstart+2),min(colend+4,10),max(rowstart-2,0),min(rowend-1,80),1)
			self.initBlock_direct(pins, colstart, colstart+3, rowstart-2, rowstart+1,0)
		elif(rowend==8 and rowstart ==6):
			self.initBlock_direct(pins,max(0,colstart),min(colend+1,10),max(rowstart,0),min(rowend+2,80),1)
			self.initBlock_direct(pins,max(0,colstart+3),min(colend+5,10),max(rowstart-3,0),min(rowend-2,80),1)
			self.initBlock_direct(pins, colstart, colstart+4, rowstart-3, rowstart+1,0)

		else:
			self.linear(pins)

		return 

	def ring(self, pins):
		colstart = 11
		collength = 0
		rowlength = 0
		rowend = -1
		for row in reversed(range(len(pins))):
			for col in range(len(pins[row])):
				if(pins[row][col] == 1):
					if(col<=colstart and row>=rowend):
						colstart=col
						rowend=row
					elif(col>colstart and row==rowend):
						collength=collength+1
					elif(row<rowend and col==colstart):
						rowlength=rowend-row 

		colend=colstart+collength
		rowstart=rowend-rowlength

		self.initBlock_direct(pins,max(0,colstart-1),min(colend+2,10),max(rowstart-1,0),min(rowend+2,80),1)
		self.initBlock_direct(pins,max(0,colstart),min(colend+1,10),max(rowstart,0),min(rowend+1,80),0)
		return  

	def copyArray(self, from_array, to_array):
		for row in range(len(to_array)):
			for col in range(len((to_array[row]))):
				to_array[row][col] = from_array[row][col]
		return

def main():
	test = pcbWrapper()
	test.start(1)
	while(1):
		test.update()
		time.sleep(3)

	test.stop()
	return

if(__name__ == "__main__"):
	main()
	# EXAMPLE					  (x,y) = (80,10)
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	# [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	#  ^ (x,y) = (0,0)
