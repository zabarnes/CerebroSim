from kivy.app import App
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.config import Config
Config.set('graphics','width','480')
Config.set('graphics', 'height','800')
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.widget import Widget
import datetime

import kivy
kivy.require('1.0.7')

from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock 
from functools import partial
from pcbWrapper import pcbWrapper
from kivy.properties import NumericProperty


class SimpleRoot(BoxLayout):
	currentTime=NumericProperty(0)
	def movePattern(self,dt):
		pins = self.pcb.update()
		self.updateGraphics(pins)
		self.currentTime = self.currentTime+self.timeout
		return

	def updateGraphics(self, pins):
		self.circles.redraw(pins)
		# for col in range(10): #create grid 
		# 	for row in range(80):
		# 		if(pins[row][col]==1):
		# 			#self.graph[row][col].changeColor(0.38, 0.267, 0.608)
		# 			self.circles.changeColor(0.38, 0.267, 0.608)
		# 		else:
		# 			self.circles.changeColor(.82,.82,.82)
					#self.graph[row][col].changeColor(.82,.82,.82)

	def simulation(self):

		layout = GridLayout(cols=1, size_hint=(None,1))
		self.circles = MultiCircularWidget()
		#self.circles.background_color(.82,.82,.82,.9)
		self.circles.addCircles()
		# self.graph = [[0 for x in range(10)] for x in range(80)]
		# for row in reversed(range(80)): #create grid 
		# 	self.graph.append([0 for i in range(10)])
		# 	for col in range(10):
		# 		self.circles.addCircle(row,col)
		   # self.graph[row][col] = Button(text='', background_color = [1,1,1,1])
				#self.graph[row][col] = CircularWidget(.82,.82,.82)
				#layout.add_widget(self.graph[row][col
		layout.add_widget(self.circles)
		self.pcb = pcbWrapper()
		self.pcb.start(self.pattern)
		
		self.movePattern(1)
		self.currentTime = 0
		Clock.unschedule(self.movePattern)
		self.clock=Clock.schedule_interval(self.movePattern, self.timeout)
		# self.pcb.start(1)
		# self.clock=Clock.schedule_interval(self.movePattern,self.timeout)
		return layout
	
	def updateTime(self,second,third):
		self.timeRun.text="Simulated Time: %.2f min"%(self.currentTime/60.0)

	def pressed_spinner(self, text):
		self.spinnerText = text
		Clock.unschedule(updateSpinner)
		Clock.schedule_once(updateSpinner)

	def updateSpinner(self):
		self.ids.pattern_spin.text = self.spinnerText

	def content(self, end, pause, pattern, speed):
		layout = GridLayout(cols=2,spacing="20db")
		layout.add_widget(self.simulation())
		currentDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		stop_start = BoxLayout(orientation="vertical", spacing="10db")
		stop_start.add_widget(Label(text="Simulation Information:\n\nDate: %s\nPattern: %s\nSpeed: %s mm/min" % (currentDate, pattern, speed),valign="top"))
		self.timeRun = Label(text="Simulated Time: %.2f min"%(self.currentTime/60.0), valign="top")
		self.bind(currentTime=self.updateTime)
		stop_start.add_widget(self.timeRun)
		stop_start.add_widget(pause)
		stop_start.add_widget(end)
		layout.add_widget(stop_start)
		return layout

	def on_our_btn_release(self, speed, pattern_text):
		self.timeout = 60.0/speed
		if(pattern_text =="Linear"):
			self.pattern = 1
		elif(pattern_text =="Ring"):
			self.pattern = 2
		elif(pattern_text =="Split"):
			self.pattern = 3
		self.currentTime = 0

		end_button = Button(text="End Simulation", id="end", size_hint=(1,.3), background_color=(0.38, 0.267, 0.608, 0.9), font_size="25sp", bold=True)
		self.pause_button = Button(text="Pause", id="pause", size_hint=(1,.2), background_color=(0.902, 0.447, 0.0, 0.9), font_size="25sp", bold=True)
		self.running = 1
		
		simulation_content = self.content(end_button,self.pause_button,pattern_text,speed)
		self.pop_up = Popup(title="CSD simulation in progress......", font_size="25sp", bold=True, content=simulation_content, size_hint=(.65, 1), auto_dismiss=False)
	       
		end_button.bind(on_release=self.end)

		#pause_button.bind(on_release=self.pause)
		self.pause_button.bind(on_release=self.pause_callback)
		self.pop_up.open()
	
	def end(self, second):
		self.pcb.stop()
		self.pop_up.dismiss()	
		Clock.unschedule(self.clock)

	def pause_callback(self, *largs):
	    Clock.unschedule(self.pause)
	    Clock.schedule_once(self.pause)
	
	def pause(self, button):
		self.lastpause=0
		button=self.pause_button
		if(self.running == 1):
			button.background_color=(0.094, 0.384, 0.094, 0.9)
			button.text="Unpause"
			self.running = 0
			Clock.unschedule(self.clock)
		else:
			button.background_color=(0.902, 0.447, 0.0, 0.9)
			button.text="Pause"
			self.running = 1
			Clock.unschedule(self.movePattern)
			self.clock = Clock.schedule_interval(self.movePattern, self.timeout)
		return


class SimpleApp(App):
    def build(self):
        return SimpleRoot()
        # return BoxLayout().add_widget(MultiCircularWidget(0.902, 0.447, 0.0))
        # box = BoxLayout()
        # circles = MultiCircularWidget(0.902, 0.447, 0.0)
        # box.add_widget(circles)
        # return box

class StopStart(BoxLayout):
	pass

class CircularWidget(Widget):
	r = NumericProperty(0)
	g = NumericProperty(0)
	b = NumericProperty(0)
	def __init__(**kwargs):
		super(CircularWidget,self).__init__(**kwargs)
	
	def changeColor(self, new_red, new_green, new_blue):
		self.r=new_red
		self.g=new_green
		self.b=new_blue

class MultiCircularWidget(Widget):

	def __init__(self, **kwargs):
		self.height=735
		self.width=100
		self.x = 96
		self.y = 12
		self.dx = self.width/10
		self.dy =self.height/80

		super(MultiCircularWidget,self).__init__(**kwargs)

	def addCircles(self):
		# with self.canvas:
		# 	for col in range(10): #create grid 
		# 	 	for row in range(80):
		# 			Color(.82,.82,.82)
		# 			Ellipse(pos=(self.dx*col+self.x,self.dy*row+self.y),size=(self.dx,self.dy))
		# with self.canvas:
		# 	Color(.82,.82,.82)
		# 	Rectangle(pos=(self.x,self.y),size=(self.width,self.height))
		return
			# Ellipse(pos=self.pos[1],self.pos(2),size=(self.width/2,self.height/2))
			#Ellipse(pos=self.pos,size=(self.width,self.height))
			#Rectangle(pos=(93,13),size=(self.width,self.height))

	def redraw(self, pins):
		self.canvas.clear()
		with self.canvas:
			Color(.82,.82,.82)
			Rectangle(pos=(self.x,self.y),size=(self.width,self.height))
			for col in range(10): #create grid 
			 	for row in range(80):
			 		if(pins[row][col]==1):
						Color(0.38, 0.267, 0.608)
						Ellipse(pos=(self.dx*col+self.x,self.dy*row+self.y),size=(self.dx,self.dy))



if __name__ == "__main__":
    SimpleApp().run()
