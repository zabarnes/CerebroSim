'''
Application example using build() + return
==========================================

An application can be built if you return a widget on build(), or if you set
self.root.
'''

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock 
from functools import partial
from pcbWrapper import pcbWrapper

class TestApp(App):
    def movePattern(self,dt):
        pins = self.pcb.update()
        self.updateGraphics(pins)
        return
    def updateGraphics(self, pins):
        for col in range(10): #create grid 
            for row in range(80):
                if(pins[row][col]==1):
                    self.graph[row][col].background_color = [2,2,1,1]
                else:
                    self.graph[row][col].background_color = [1,1,1,1]
    def build(self):
        layout = GridLayout(cols=10, rows=80)
        self.graph = [[0 for x in range(10)] for x in range(80)]
        for row in reversed(range(80)): #create grid 
            self.graph.append([0 for i in range(10)])
            for col in range(10):
        	    self.graph[row][col] = Button(text='', background_color = [1,1,1,1]) 
        	    layout.add_widget(self.graph[row][col])

        self.pcb = pcbWrapper()
        self.pcb.start(1)
        Clock.schedule_interval(self.movePattern,1)
        return layout

if __name__ == '__main__':
    TestApp().run()