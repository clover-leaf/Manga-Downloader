import requests
import shutil
from PyQt5 import QtCore
import website

class Thread:
	def __init__(self):
		self.websites = website.DICT

	def handleError(self, func, package, signal):
		try:
			func(package)
		except requests.ConnectionError:
			signal.emit([False, 1])
		except requests.Timeout:
			signal.emit([False, 5])
		except requests.exceptions.HTTPError:
			signal.emit([False, 2])
		except IndexError:
			signal.emit([False, 3])
		except Exception as e:
			print(e)
			signal.emit([False, 4])

class refreshThread(QtCore.QObject, Thread):
	
	""" Refresh manga list of website """

	updateDone = QtCore.pyqtSignal(list)

	def __init__(self, parent=None, **kwargs):
		super().__init__(parent, **kwargs)

	def handleManga(self, package):
		for i in package:
			self.websites[i].updateManga()
		self.updateDone.emit([True, package])

	@QtCore.pyqtSlot(list)
	def update(self, package):
		self.handleError(self.handleManga, package, self.updateDone)

class updateThread(QtCore.QObject, Thread):
	
	""" Get chapters """

	chapterOut = QtCore.pyqtSignal(list)
	info = QtCore.pyqtSignal(list)

	def __init__(self, parent=None, **kwargs):
		super().__init__(parent, **kwargs)

	def handleChapter(self, package):
		website, url = package
		result = self.websites[website].updateChapter(url)
		self.chapterOut.emit([True, result])

	def infoManga(self, package):
		title, website, path, url = package
		info = self.websites[website].updateChapter(url)
		urls = [info[x][1] for x in info]
		urls.reverse()
		self.info.emit([title, website, path, url, urls])

	@QtCore.pyqtSlot(list)
	def updateChapter(self, package):
		self.handleError(self.handleChapter, package, self.chapterOut)

	@QtCore.pyqtSlot(list)
	def sendInfo(self, package):
		self.handleError(self.infoManga, package, self.info)

class downloadThread(QtCore.QObject, Thread):

	""" Download ONE chapter/time """

	signalOut = QtCore.pyqtSignal(int)
	
	def __init__(self, parent=None, **kwargs):
		super().__init__(parent, **kwargs)
		
	@QtCore.pyqtSlot(list)
	def downChap(self, package):
		try:
			Zip, website, path, url = package
			path = self.websites[website].download(path, url)
			if Zip:
				shutil.make_archive(path, 'zip', path)
			self.signalOut.emit(0)
		except requests.ConnectionError:
			self.signalOut.emit(1)
		except requests.Timeout:
			self.signalOut.emit(5)
		except requests.exceptions.HTTPError:
			self.signalOut.emit(2)
		except IndexError:
			self.signalOut.emit(3)
		except FileNotFoundError:
			self.signalOut.emit(6)
		except Exception as e:
			print(e)
			self.signalOut.emit(4)
