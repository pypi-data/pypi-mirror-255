# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guilayout.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import os
#import pdffunctions
import matplotlib.pyplot as plt
import matplotlib.figure as figure
import numpy as np




class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(702, 657)
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
			
		self.c0 = QtWidgets.QDoubleSpinBox(self.centralwidget)
		self.c0.setGeometry(QtCore.QRect(371, 190, 61, 22))
		self.c0.setProperty("value", 1)
		self.c0.setObjectName("c0")
		self.c0.setDecimals(1)
		self.c0.setSingleStep(0.1)
		
		self.c1 = QtWidgets.QDoubleSpinBox(self.centralwidget)
		self.c1.setGeometry(QtCore.QRect(371, 230, 61, 22))
		self.c1.setProperty("value", 1)
		self.c1.setObjectName("c1")
		self.c1.setDecimals(1)
		self.c1.setSingleStep(0.1)
		
		self.c2 = QtWidgets.QDoubleSpinBox(self.centralwidget)
		self.c2.setGeometry(QtCore.QRect(371, 270, 61, 22))
		self.c2.setProperty("value", 1)
		self.c2.setObjectName("c2")
		self.c2.setDecimals(1)
		self.c2.setSingleStep(0.1)
		
		self.c3 = QtWidgets.QDoubleSpinBox(self.centralwidget)
		self.c3.setGeometry(QtCore.QRect(371, 340, 61, 21))
		self.c3.setProperty("value", 1)
		self.c3.setObjectName("c3")
		self.c3.setSingleStep(0.1)
		self.c3.setDecimals(1)

		self.plotButton = QtWidgets.QPushButton(self.centralwidget)
		self.plotButton.setGeometry(QtCore.QRect(310, 470, 93, 28))
		self.plotButton.setObjectName("plotButton")
		self.updatePlotButton = QtWidgets.QPushButton(self.centralwidget)
		self.updatePlotButton.setGeometry(QtCore.QRect(310, 500, 93, 28))
		self.updatePlotButton.setObjectName("updatePlotButton")
		

		MainWindow.setCentralWidget(self.centralwidget)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)
		
		
		#self.fig = None
		#self.ax = None
		self.x = np.arange(-10,10,0.01)
		
		self.plotButton.clicked.connect(self.run)
		#self.updatePlotButton.clicked.connect(self.plotUpdate)
		
	
	def quad_cubic(self):
		c0value = float(self.c0.text())
		c1value = float(self.c1.text())
		c2value = float(self.c2.text())
		c3value = float(self.c3.text())
		y2 = c0value + c1value*self.x + c2value*self.x**2
		y3 = c0value + c1value*self.x + c2value*self.x**2 + c3value*self.x**3
		return y2,y3


	def run(self):
		self.fig,self.ax = plt.subplots(2,1,dpi = 150)
		self.plotUpdate()
		
	def plotUpdate(self):
		y2,y3 = self.quad_cubic()
		self.ax[0].cla()
		self.ax[1].cla()
		self.ax[0].plot(self.x,y2)
		self.ax[1].plot(self.x,y3)		
		plt.show(block=False)
		print('plotting')
		self.updatePlotButton.clicked.connect(self.plotUpdate)

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())

