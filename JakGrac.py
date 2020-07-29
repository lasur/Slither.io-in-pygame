import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class JakGrac(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(JakGrac, self).__init__(parent)
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle('Jak grać')
        self.setFixedSize(352,405)
        self.setModal(True)
        tlo_okna = QtGui.QImage("jak.png")
        skaluj = tlo_okna.scaled(QtCore.QSize(352,405)) # dopasuj obraz do rozmiaru okna
        palette = QtGui.QPalette()
        palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(skaluj))                        
        self.setPalette(palette)
	
    def main(parent = None):
        dialog = JakGrac(parent)
        dialog.show()
        dialog.exec()