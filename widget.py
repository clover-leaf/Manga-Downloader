#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import webbrowser
import pyperclip

from PyQt5 import QtCore, QtGui, QtWidgets

from SecondaryThread import updateThread, downloadThread, refreshThread
from classdata import Manga, Chapter, Container
import website


# Status
INQUEUE = "In Queue"
COMPLETED = "Completed"
STOP = "Stop"
DOWNLOADING = "Downloading"
FAILED = "Failed"

chapter = "Chapter"
manga = "Manga"

class childWidget(QtWidgets.QWidget):
	# Add signal
	signalUpdate = QtCore.pyqtSignal(list)
	signalUpChap = QtCore.pyqtSignal(list)
	signalDownChap = QtCore.pyqtSignal(list)
	signalAddQueue = QtCore.pyqtSignal(list)

	def __init__(self, path, z):
		super().__init__()
		self.websites = website.DICT
		self.dictChapter = {}
		self.web = "Blogtruyen"
		self.path = path
		self.zip = z
		self.running = False
		self.chapboxWeb = self.web
		self.selected = []
		self.onQueue = None
		self.mangaPath = None
		self.pivot = 0
		self.done = True

		self.initUi()

	def initUi(self):

		self.headerManga = QtWidgets.QHBoxLayout()

		self.searchBox = QtWidgets.QLineEdit(placeholderText='Press Enter to search')
		self.searchBox.setMaximumHeight(30)

		self.statusicon = QtWidgets.QLabel()
		self.statusicon.setObjectName("loading")
		self.statusicon.setStyleSheet("image: url(:/{}.png);".format(self.web))
		self.loading = QtGui.QMovie(':/loading.gif')
		self.loading.setScaledSize(QtCore.QSize(22, 22))
		self.loading.setSpeed(150)
		self.loading.start()

		self.headerManga.addWidget(self.statusicon)
		self.headerManga.addWidget(self.searchBox)

		self.mangaBox = QtWidgets.QListWidget()
		self.mangaBox.setVerticalScrollMode(\
			QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.mangaBox.installEventFilter(self)
		
		self.topLeft = QtWidgets.QVBoxLayout()
		self.topLeft.addLayout(self.headerManga)
		self.topLeft.addWidget(self.mangaBox)

		self.chapterBox = QtWidgets.QListWidget()
		self.chapterBox.setVerticalScrollMode(\
			QtWidgets.QAbstractItemView.ScrollPerPixel)
		self.chapterBox.installEventFilter(self)
		self.chapterBox.setSelectionMode(\
			QtWidgets.QAbstractItemView.ExtendedSelection)

		self.top = QtWidgets.QHBoxLayout()
		self.top.addLayout(self.topLeft)
		self.top.addWidget(self.chapterBox)

		self.queueTable = QtWidgets.QTableWidget()
		self.queueTable.verticalHeader().hide()
		self.queueTable.installEventFilter(self)
		self.queueTable.setColumnCount(5)
		self.queueTable.setHorizontalHeaderLabels(['Title',\
			 'Status', 'Type', 'Site', 'Save to'])
		self.queueTable.setAlternatingRowColors(True)
		self.queueTable.setEditTriggers(\
			QtWidgets.QTableWidget.NoEditTriggers)
		self.queueTable.setSelectionBehavior(\
			QtWidgets.QTableWidget.SelectRows)
		# self.queueTable.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
		self.queueTable.setSelectionMode(\
			QtWidgets.QTableWidget.ExtendedSelection)
		header = self.queueTable.horizontalHeader()
		header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

		self.buttonGroup = QtWidgets.QHBoxLayout()
		self.start_btn = QtWidgets.QPushButton('Start')
		self.stop_btn = QtWidgets.QPushButton('Stop')
		self.clr_btn = QtWidgets.QPushButton('Clear')
		self.start_btn.setMinimumWidth(60)

		self.buttonGroup.addWidget(self.start_btn)
		self.buttonGroup.addWidget(self.stop_btn)
		self.buttonGroup.addWidget(self.clr_btn)
		self.buttonGroup.addStretch()

		self.bottom = QtWidgets.QVBoxLayout()
		self.bottom.addLayout(self.buttonGroup)
		self.bottom.addWidget(self.queueTable)

		self.screen = QtWidgets.QVBoxLayout(self)
		self.screen.addLayout(self.top)
		self.screen.addLayout(self.bottom)
		font = QtGui.QFont()
		font.setFamily("Times New Roman")
		font.setPointSize(10)
		self.setFont(font)
		self.setLayout(self.screen)

		self.queueContainer = Container()
		self.chapMenu = QtWidgets.QMenu(self)
		self.addChapAction = self.createAction(text='Add to Queue')
		self.copyUrlAction = self.createAction(text='Copy URL')
		self.viewOnlineAction = self.createAction(text='View online')
		self.addChapAction.triggered.connect(self.addChapQueue)
		self.copyUrlAction.triggered.connect(self.copyUrl)
		self.viewOnlineAction.triggered.connect(self.openUrl)
		self.addActions(self.chapMenu, [self.addChapAction, \
			self.copyUrlAction, self.viewOnlineAction])

		self.mangaMenu = QtWidgets.QMenu(self)
		self.addMangaAction = self.createAction(text='Add to Queue')
		self.addMangaAction.triggered.connect(self.addMangaQueue)
		self.addActions(self.mangaMenu, [self.addMangaAction, \
			self.copyUrlAction, self.viewOnlineAction])

		self.queueMenu = QtWidgets.QMenu(self)
		self.queueRemove = self.createAction(text='Remove')
		self.queueRemove.triggered.connect(self.removeQueue)
		self.queueOpen = self.createAction(text='Open')
		self.queueOpen.triggered.connect(self.openQueue)
		self.addActions(self.queueMenu, [self.queueRemove, self.queueOpen])

		# Event Handle
		self.mangaBox.itemDoubleClicked.connect(self.getChapterUrl)
		self.start_btn.clicked.connect(self.startQueue)
		self.stop_btn.clicked.connect(self.stopQueue)
		self.clr_btn.clicked.connect(self.clearQueue)
		self.stop_btn.setEnabled(False)
		self.searchBox.returnPressed.connect(self.searchEngine)

		# Thread Handle
		self.threadGet = QtCore.QThread()
		self._threadGet = updateThread(chapterOut=self.updateChapter,\
										info=self.addQueueThread)
		self.signalUpChap.connect(self._threadGet.updateChapter)
		self.signalAddQueue.connect(self._threadGet.sendInfo)
		self._threadGet.moveToThread(self.threadGet)
		self.threadGet.start()

		self.threadDown = QtCore.QThread()
		self._threadDown = downloadThread(signalOut=self.doneQueue)
		self.signalDownChap.connect(self._threadDown.downChap)
		self._threadDown.moveToThread(self.threadDown)
		self.threadDown.start()

		self.threadUpdate = QtCore.QThread()
		self._threadUpdate = refreshThread(updateDone=self.doneUpdate)
		self.signalUpdate.connect(self._threadUpdate.update)
		self._threadUpdate.moveToThread(self.threadUpdate)
		self.threadUpdate.start()
		
		self.refreshManga()
		self.updateQueue()

	def createAction(self, text, slot=None, shortcut=None,\
			icon=None):
			action = QtWidgets.QAction(text, self)
			if icon is not None:
				action.setIcon(QtGui.QIcon(":/{}.png".format(icon)))
			if shortcut is not None:
				action.setShortcut(shortcut)
			return action

	def addActions(self, target, actions):
		for action in actions:
			if action is not None:
				target.addAction(action)
			else:
				target.addSeparator()

	def eventFilter(self, source, event):
		if (event.type() == QtCore.QEvent.ContextMenu and
			source is self.chapterBox):
			self.selected = [x.row() for x in 
							self.chapterBox.selectedIndexes()]
			self.chapMenu.exec_(event.globalPos())
			self.chapterBox.clearSelection()
		if (event.type() == QtCore.QEvent.ContextMenu and
			source is self.mangaBox):
			self.selected = []
			for x in source.selectedItems():
				self.selected.append(x.text())
			self.mangaMenu.exec_(event.globalPos())
			self.mangaBox.clearSelection()
		if (event.type() == QtCore.QEvent.ContextMenu and
			source is self.queueTable):
			self.queueMenu.exec_(event.globalPos())
			self.queueTable.clearSelection()

		return super().eventFilter(source, event)

	def dialog(self, msg, title="Warning"):
		d = QtWidgets.QDialog(self)
		v = QtWidgets.QVBoxLayout()
		l = QtWidgets.QLabel(msg)
		v.addWidget(l)
		b = QtWidgets.QPushButton("Ok")
		b.clicked.connect(d.close)
		v.addWidget(b)
		d.setLayout(v)
		d.setWindowTitle(title)
		d.exec_()

	def changeWebsite(self, web):
		if self.web != web:
			self.web = web
			self.refreshManga()
			self.mangaBox.verticalScrollBar().setValue(0)
			self.mangaBox.horizontalScrollBar().setValue(0)

	def refreshManga(self):
		self.mangaBox.clear()
		self.dictManga = self.websites[self.web].loadManga()
		for title in self.dictManga:
			self.mangaBox.addItem(title)
		self.statusicon.setStyleSheet(
				"image: url(:/{}.png);".format(self.web.lower()))

	def loadingProcess(self):
		self.statusicon.setMovie(self.loading)

	def loadingCompleted(self):
		m = QtGui.QMovie()
		self.statusicon.setMovie(m)
		self.statusicon.setStyleSheet("image: url(:/{}.png);".format(self.web.lower()))

	def getChapterUrl(self):
		self.chapterBox.clear()
		self.loadingProcess()
		for manga in self.mangaBox.selectedItems():
			mangaUrl = self.dictManga[manga.text()]
			self.signalUpChap.emit([self.web, mangaUrl])
		self.chapboxWeb = self.web

	@QtCore.pyqtSlot(list)
	def updateChapter(self, package):
		if package[0]:
			self.dictChapter = package[1]
			self.chapterBox.clear()
			for Id in self.dictChapter:
				self.chapterBox.addItem(self.dictChapter[Id][0])
		else:
			self.catchError(package[1])
		self.loadingCompleted()

	def updateMangarequest(self, package):
		self.signalUpdate.emit(package)

	@QtCore.pyqtSlot(list)
	def doneUpdate(self, package):
		if package[0]:
			msg = "{} have been updated.".format(", ".join(package[1:]))
			self.dialog(msg, title="Information")
		else:
			self.catchError(package[1])

	def addChapQueue(self):
		for x in self.selected:
			if self.dictChapter[x][0] not in self.queueContainer:
				self.queueContainer.add(Chapter(self.dictChapter[x][0],\
							INQUEUE, chapter, self.chapboxWeb, self.path,\
								self.dictChapter[x][1]))
		self.updateQueue()

	def addMangaQueue(self):
		self.loadingProcess()
		self.signalAddQueue.emit([self.selected[0] ,self.web, self.path, \
								self.dictManga[self.selected[0]]])

	@QtCore.pyqtSlot(list)
	def addQueueThread(self, package):
		if package[0]:
			title, web, path, url, urls = package
			self.queueContainer.add(Manga(title, INQUEUE, manga, web, path, url, urls))
			self.updateQueue()
		else:
			self.catchError(package[1])
		self.loadingCompleted()

	def copyUrl(self):
		try:
			selectedUrl = [self.dictManga[x] for x in self.selected]
			for url in selectedUrl:
				pyperclip.copy(url)
		except KeyError:
			selectedUrl = [self.dictChapter[x][1] for x in self.selected]
			for url in selectedUrl:
				pyperclip.copy(url)

	def openUrl(self):
		try:
			selectedUrl = [self.dictManga[x] for x in self.selected]
			for url in selectedUrl:
				webbrowser.open(url)
		except KeyError:
			selectedUrl = [self.dictChapter[x][1] for x in self.selected]
			for url in selectedUrl:
				webbrowser.open(url)
			
	def searchEngine(self):
		text = self.searchBox.text()
		if str(text) != "":
			result = [x for x in self.dictManga if str(text).lower() in x.lower()]
			self.mangaBox.clear()
			for title in result:
				self.mangaBox.addItem(title)
		else:
			self.mangaBox.clear()
			for title in self.dictManga:
				self.mangaBox.addItem(title)

	def startQueue(self):
		self.running = True
		self.emitSthIDK()
		self.updateQueue()

	def stopQueue(self):
		if self.onQueue is not None:
			if self.onQueue.type_ == manga:
				self.onQueue.status = STOP
		self.running = False
		self.start_btn.setEnabled(True)
		self.stop_btn.setEnabled(False)
		self.updateQueue()

	def conditionCheck(self):
		if not self.done:
			return False, None
		if not self.running:
			return False, None
		for item in self.queueContainer:
			if item.status == INQUEUE or \
				item.status == STOP or \
				item.status == FAILED or \
				"/" in item.status:
				return True, item
		return False, None

	def emitSthIDK(self):
		coutinue, item = self.conditionCheck()
		if coutinue:
			self.onQueue = item
			self.done = False
			if item.type_ == chapter:
				item.status = DOWNLOADING
				if self.zip:
					self.signalDownChap.emit([True, item.web, item.path, item.url])
				else:
					self.signalDownChap.emit([False, item.web, item.path, item.url])
			else:
				if self.pivot == 0:
					self.mangaPath = self.websites[item.web].prepareFolder(item.path, item.url)
				item.status = "{}/{}".format(self.pivot, len(item.urlChap))
				if self.zip:
					self.signalDownChap.emit([True, item.web, self.mangaPath, item.urlChap[self.pivot]])
				else:
					self.signalDownChap.emit([False, item.web, self.mangaPath, item.urlChap[self.pivot]])
			self.start_btn.setEnabled(False)
			self.stop_btn.setEnabled(True)
	
	def queueComplete(self):
		for item in self.queueContainer:
			if item.status != COMPLETED:
				return False
		return True

	def catchError(self, Num):
		if Num == 1:
			self.dialog("No connection is avaiable!")
		elif Num == 2:
			self.dialog("Address has error!")
		elif Num == 3:
			self.dialog("Could not find data in this address!")
		elif Num == 5:
			self.dialog("Connection is too slow to loading!")
		elif Num == 6:
			self.dialog("Directory is not found")
		else:
			self.dialog("Something went wrong")

	@QtCore.pyqtSlot(int)
	def doneQueue(self, receive):
		if receive == 0:
			self.done = True
			if self.onQueue is not None:
				if self.onQueue.type_ == chapter:
					self.onQueue.status = COMPLETED
				else:
					self.pivot += 1
					if self.pivot == len(self.onQueue.urlChap):
						self.pivot = 0
						self.onQueue.status = COMPLETED
			self.emitSthIDK()
			self.updateQueue()

			if self.queueComplete():
				self.running = False
				self.start_btn.setEnabled(True)
				self.stop_btn.setEnabled(False)
		else:
			self.catchError(receive)
			self.onQueue.status = FAILED
			self.pivot = 0
			self.onQueue = None
			self.done = True
			self.running = False
			self.start_btn.setEnabled(True)
			self.stop_btn.setEnabled(False)
			self.updateQueue()

	def removeQueue(self):
		indexes = self.queueTable.selectionModel().selectedRows()
		indexes.sort()
		indexes.reverse()
		if self.onQueue is not None:
			for index in indexes:
				if self.queueTable.item(index.row(), 0).text()\
					 == self.onQueue.title:
					 self.onQueue = None
					 self.pivot = 0
				self.queueContainer.delete(index.row())
		else:
			for index in indexes:
				self.queueContainer.delete(index.row())
		self.updateQueue()

	def clearQueue(self):
		self.queueContainer.clear()
		self.updateQueue()

	def openQueue(self):
		indexes = self.queueTable.selectionModel().selectedRows()
		for index in indexes:
			os.startfile(self.queueTable.item(index.row(), 4).text())

	def updateQueue(self, current=None):
		self.queueTable.setRowCount(self.queueContainer.length())
		selected = None

		for row, manga in enumerate(self.queueContainer):
			item = QtWidgets.QTableWidgetItem(manga.title)
			if current is not None and current == id(manga):
				selected = item
			item.setData(QtCore.Qt.UserRole, \
				QtCore.QVariant(id(manga)))
			self.queueTable.setItem(row, 0, item)
			item = QtWidgets.QTableWidgetItem(manga.status)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.queueTable.setItem(row, 1, item)
			item = QtWidgets.QTableWidgetItem(manga.type_)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.queueTable.setItem(row, 2, item)
			item = QtWidgets.QTableWidgetItem(manga.web)
			item.setTextAlignment(QtCore.Qt.AlignCenter)
			self.queueTable.setItem(row, 3, item)
			item = QtWidgets.QTableWidgetItem(manga.path)
			self.queueTable.setItem(row, 4, item)

		if selected is not None:
			selected.setSelected(True)
			self.queueTable.setCurrentItem(selected)
			self.queueTable.scrollToItem(selected)