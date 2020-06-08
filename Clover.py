#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import configparser

from PyQt5 import QtCore, QtGui, QtWidgets

import image_rc
import website
from widget import childWidget


# Define Qss
DEFINE = {'Sky': 
				{'@color3': '#1395BA', 
				'@color4' : '#1286A8', 
				'@color2' : '#D0EAF1', 
				'@color1' : '#FFF', 
				'@font'   : "'000 CCMonologous [TeddyBear]'",
				'@checkbox_unchecked': 'checkbox_unchecked',
				'@checkbox_checked'  : 'checkbox_checked',
				'@searchbtn_hover'   : 'searchbtn_hover',
				'@searchbtn_normal'  : 'searchbtn_normal'
				},
		'Tomato': {'@color3': '#E24F3B', 
				'@color4': '#B62F23', 
				'@color2': '#ED6F6D', 
				'@color1': '#FFF', 
				'@font': "'000 CCMonologous [TeddyBear]'",
				'@checkbox_unchecked': 'checkbox_unchecked_orange',
				'@checkbox_checked': 'checkbox_checked_orange',
				'@searchbtn_hover': 'searchbtn_hover_orange',
				'@searchbtn_normal': 'searchbtn_normal'
				},
		'Lime': {'@color3': '#ACCC6A', 
				'@color4': '#55895B', 
				'@color2': '#BCD743', 
				'@color1': '#FFF', 
				'@font': "'000 CCMonologous [TeddyBear]'",
				'@checkbox_unchecked': 'checkbox_unchecked_lime',
				'@checkbox_checked': 'checkbox_checked_lime',
				'@searchbtn_hover': 'searchbtn_hover_lime',
				'@searchbtn_normal': 'searchbtn_normal'
				}
		}

class MainWindow(QtWidgets.QMainWindow):

	def __init__(self):
		super().__init__()
		self.__version__ = 1.4
		self.__author__ = "Thang Nguyen"	
		try:
			# Read config
			config = configparser.ConfigParser()
			config.read('bin/config.ini')
			self.path = config['CONFIG']['PATH']
			self.theme = config['CONFIG']['THEME']
			self.minimize = config.getboolean('CONFIG', 'MINIMIZE')
			self.zip = config.getboolean('CONFIG', 'ZIP')
			if not os.path.isdir(self.path):
				path = os.path.dirname(os.path.abspath(__file__))
			self.initUi()
		except Exception as e:
			self.path = os.path.dirname(os.path.abspath(__file__))
			self.theme = 'Sky'
			self.minimize = False
			self.zip = False
			self.initUi()

	def initUi(self):
		self.resize(1000, 500)
		self.widget = childWidget(self.path, self.zip)
		self.setCentralWidget(self.widget)

		# Menubar
		bar = self.menuBar()

		websiteMenu = bar.addMenu('Website')
		dictAct = {}
		for site in website.DICT:
			dictAct[site] = self.createAction(site, trigger=site)
		self.addActions(websiteMenu, list(dictAct.values()))

		settingMenu = bar.addMenu('Setting')
		settingAction = self.createAction('Config')
		settingAction.triggered.connect(self.settingDialog)
		updateAction = self.createAction('Update')
		updateAction.triggered.connect(self.updateDialog)
		self.addActions(settingMenu, [settingAction, updateAction])

		helpMenu = bar.addMenu('Help')
		aboutAction = self.createAction('About')
		aboutAction.triggered.connect(self.aboutDialog)
		self.addActions(helpMenu, [aboutAction])

		# Task bar
		exit = QtWidgets.QAction("Exit", self)
		exit.triggered.connect(self.exitEvent)
		self.trayIcon = QtWidgets.QSystemTrayIcon(QtGui.QIcon(':/icontaskbar.png'), self)
		menu = QtWidgets.QMenu(self)
		menu.addAction(exit)
		self.trayIcon.setContextMenu(menu)
		self.trayIcon.activated.connect(self.trayIconActivated)
		self.setWindowIcon(QtGui.QIcon(':/icontaskbar.png'))

		self.setWindowTitle("Clover")
		self.themeDict = DEFINE
		self.loadStyle(self.theme)
		self.show()
		self.raise_()

	def trayIconActivated(self, reason):
		if reason == QtWidgets.QSystemTrayIcon.Context:
			self.trayIcon.contextMenu().show()
		elif reason == QtWidgets.QSystemTrayIcon.Trigger:
			self.show()
			self.raise_()

	def closeEvent(self, event):
		if self.minimize:
			self.hide()
			self.trayIcon.show()
			event.setAccepted(True)
			event.ignore()
		elif self.minimize == None:
			event.accept()
		else:
			if self.widget.done:
				self.trayIcon.hide()
				del self.trayIcon
				event.accept()
			else:
				if self.warnMsgBox() == QtWidgets.QMessageBox.Yes:
					event.setAccepted(True)
					event.ignore()
				else:
					del self.trayIcon
					event.accept()
			
	def exitEvent(self):
		self.minimize = None
		self.close()

	def aboutDialog(self):
		d = QtWidgets.QDialog(self)
		v = QtWidgets.QVBoxLayout()
		l = QtWidgets.QLabel("Version: {}".format(self.__version__))
		v.addWidget(l)
		l = QtWidgets.QLabel("Author: "+self.__author__)
		v.addWidget(l)
		d.setLayout(v)
		d.setWindowTitle("About")
		d.exec_()

	def warnMsgBox(self):
		d = QtWidgets.QMessageBox(self)
		d.setText("Queue is still downloading\nDo you want to stay?")
		d.setStandardButtons(QtWidgets.QMessageBox.Yes|
							QtWidgets.QMessageBox.No)
		d.setWindowTitle("Warning")
		return d.exec_()

	def settingDialog(self):
		d = QtWidgets.QDialog(self)
		v = QtWidgets.QVBoxLayout()
		self.c = QtWidgets.QCheckBox("Minimize to taskbar when I close")
		self.c.setChecked(self.minimize)
		v.addWidget(self.c)
		self.z = QtWidgets.QCheckBox("Create Zip for every chapter")
		self.z.setChecked(self.zip)
		v.addWidget(self.z)
		self.cb = QtWidgets.QComboBox(self)
		for theme in self.themeDict:
			self.cb.addItem(theme)
		self.cb.setCurrentText(self.theme)
		self.cb.SizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
		self.cb.currentIndexChanged.connect(self.changeTheme)
		h = QtWidgets.QHBoxLayout()
		l = QtWidgets.QLabel("Theme:")
		h.addWidget(l)
		h.addWidget(self.cb)
		h.addStretch()
		v.addLayout(h)
		l = QtWidgets.QLabel("Download to:")
		v.addWidget(l)
		h = QtWidgets.QHBoxLayout()
		self.e = QtWidgets.QLineEdit()
		self.e.setObjectName("Directory")
		self.e.setText(self.path)
		self.e.setReadOnly(True)
		h.addWidget(self.e)
		b = QtWidgets.QPushButton()
		b.setObjectName('S')
		b.clicked.connect(self.getDirectory)
		self.pathget = self.path
		h.addWidget(b)
		h.addStretch()
		v.addLayout(h)
		b = QtWidgets.QPushButton("Save")
		b.clicked.connect(self.setting_accept)
		b.clicked.connect(d.close)
		v.addWidget(b)
		d.setLayout(v)
		d.setWindowTitle("Setting")
		d.exec_()
		if self.theme != self.cb.currentText():
			self.loadStyle(self.theme)

	def changeTheme(self):
		self.loadStyle(self.cb.currentText())

	def setting_accept(self):
		if self.pathget != "":
			self.path = self.pathget
			self.widget.path = self.pathget
		self.zip = self.z.isChecked()
		self.widget.zip = self.zip
		self.minimize = self.c.isChecked()
		self.theme = self.cb.currentText()
		config = configparser.ConfigParser()
		config['CONFIG'] = {"PATH": self.path, "MINIMIZE": self.minimize,
						'ZIP': self.zip, 'THEME': self.theme}
		with open("bin/config.ini", 'w') as f:
			config.write(f)

	def updateDialog(self):
		d = QtWidgets.QDialog(self)
		v = QtWidgets.QVBoxLayout()
		self.d = {}
		for site in self.widget.websites:
			a = QtWidgets.QCheckBox(site)
			self.d[site] = a
			v.addWidget(a)
		b = QtWidgets.QPushButton("Update")
		b.clicked.connect(self.update_accept)
		b.clicked.connect(d.close)
		v.addWidget(b)
		d.setLayout(v)
		d.setWindowTitle("Update")
		d.exec_()

	def update_accept(self):
		a = [site for site in self.d if self.d[site].isChecked()]
		if a != []:
			self.widget.updateMangarequest(a)

	def loadStyle(self, theme):
		with open("bin/style.qss", 'r') as g:
			data = g.read()
			d = self.themeDict[theme]
			for key in d:
				data = data.replace(key, d[key])
			self.setStyleSheet(data)

	def getDirectory(self):
		self.pathget = str(QtWidgets.QFileDialog.getExistingDirectory(\
							directory=self.path, caption="Select Directory"))
		if self.pathget != '':
			self.e.setText(self.pathget)

	def createAction(self, text, shortcut=None, icon=None, trigger=None):
		action = QtWidgets.QAction(text, self)
		if icon is not None:
			action.setIcon(QtGui.QIcon(":/{}.png".format(icon)))
		if shortcut is not None:
			action.setShortcut(shortcut)
		if trigger is not None:
			action.triggered.connect(lambda :self.widget.changeWebsite(trigger))
		return action

	def addActions(self, target, actions):
		for action in actions:
			if action is not None:
				target.addAction(action)
			else:
				target.addSeparator()

if __name__ == "__main__":
	import sys

	app = QtWidgets.QApplication(sys.argv)
	sd = MainWindow()
	sys.exit(app.exec_())