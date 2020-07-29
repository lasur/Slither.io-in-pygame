import os
import sys
import random
import math
from klient import Polaczenie
from PyQt5 import QtCore, QtGui, QtWidgets
from JakGrac import JakGrac
from Segment import Segment
import contextlib
with contextlib.redirect_stdout(None):	#wylacza komunikat o wersji pygame
	import pygame

pygame.font.init()

# Stałe
R_KOLA_GRACZA = 10
V_POCZATKOWE = 2
R_JEDZENIA = 5
W, H = 750, 416
tlo = pygame.image.load('tlo.jpg')
CZCIONKA_GRACZA = pygame.font.SysFont("arial", 18)
CZCIONKA_ZEGARA = pygame.font.SysFont("arial", 24)
CZCIONKA_PUNKTOW = pygame.font.SysFont("arial", 24)

# Zmienne
gracze = {}
jedzenie = []

# FUNKCJE
def czas(t):
	"""
	Konwertuje czas w sekundach na minuty i sekundy

	:param t: int
	:return: string
	"""
	if type(t) == str:
		return t

	if int(t) < 60:
		return str(t) + "s"
	else:
		min = str(t // 60)
		sec = str(t % 60)

		if int(sec) < 10:
			sec = "0" + sec

		return min + ":" + sec
	
def odswiez_widok(gracze, jedzenie, czas_gry, punkty,okno,tlo_x,tlo_y,id_gracza,serwer):
	"""
	rysuje klatki
	:return: None
	"""
	okno.fill((0,0,0)) # wypełnij ekran czarnym
	okno.blit(tlo, (tlo_x, tlo_y))
	# rysuj jedzenie
	for kuleczka in jedzenie:
		kulka=list(kuleczka)
		kulka[0]+=tlo_x
		kulka[1]+=tlo_y
		kuleczka = tuple(kulka)
		pygame.draw.circle(okno, kuleczka[2], (kuleczka[0], kuleczka[1]), R_JEDZENIA)
	# rysuj graczy z listy
	for i in range(len(gracze)+3):
		if(i!=id_gracza):
			try:
				gr = gracze[i]
				if(round(gr["punkty"])<350 and round(gr["punkty"])>=0):
					for i in range(len(gr["segmenty"])):
						pygame.draw.ellipse(okno, gr["segmenty"][len(gr["segmenty"])-1-i].color, (int(gr["segmenty"][len(gr["segmenty"])-1-i].x-20+tlo_x), int(gr["segmenty"][len(gr["segmenty"])-1-i].y-20+tlo_y), gr["segmenty"][len(gr["segmenty"])-1-i].size * 2, gr["segmenty"][len(gr["segmenty"])-1-i].size * 2))
			except KeyError:
				continue
		if((i==id_gracza)):
			try:
				gr = gracze[id_gracza]
				if(round(gr["punkty"])<0):
					return False
				if(round(gr["punkty"])<350 and round(gr["punkty"])>=0):
					for i in range(len(gr["segmenty"])):
						pygame.draw.ellipse(okno, gr["segmenty"][len(gr["segmenty"])-1-i].color, (375-int(gr["segmenty"][0].x-gr["segmenty"][len(gr["segmenty"])-1-i].x)-20, 208-int(gr["segmenty"][0].y-gr["segmenty"][len(gr["segmenty"])-1-i].y)-20, gr["segmenty"][len(gr["segmenty"])-1-i].size * 2, gr["segmenty"][len(gr["segmenty"])-1-i].size * 2))
			except KeyError:
				continue
	# rysuj tabelę wyników
	posortowani_gracze = list(reversed(sorted(gracze, key=lambda x: gracze[x]["punkty"])))
	tytul = CZCIONKA_ZEGARA.render("Tablica wyników", 1, (255,255,255))
	start_y = 25
	x = W - tytul.get_width() - 10
	okno.blit(tytul, (x, 5))

	losuj = min(len(gracze), 5)
	for licz, i in enumerate(posortowani_gracze[:losuj]):
		tab_wyn = CZCIONKA_PUNKTOW.render(str(licz+1) + ". " + str(gracze[i]["nazwa"]), 1, (255,255,255))
		okno.blit(tab_wyn, (x, start_y + licz * 20))

	# rysuj zegar
	tekst_zegara = CZCIONKA_ZEGARA.render("Czas: " + czas(czas_gry), 1, (255,255,255))
	okno.blit(tekst_zegara,(10,10))
	# rysuj punkty
	pkt = CZCIONKA_ZEGARA.render("Punkty: " + str(round(punkty)),1,(255,255,255))
	okno.blit(pkt,(10,15 + pkt.get_height()))
	pygame.display.update()
	return True

def main(nazwa,okno,tlo_x,tlo_y):
	"""
	rozpoczyna grę, posiada główną pętlę gry

	:param gracze: lista słowników reprezentujących graczy
	:return: None
	"""
	global gracze
	# polaczenie z serwerem
	serwer = Polaczenie()
	id_gracza = serwer.polacz(nazwa)
	jedzenie, gracze, czas_gry = serwer.wyslij("get")
	szybkosc={0,0}
	# ustawienie zegara
	zegar = pygame.time.Clock()
	gracz = gracze[id_gracza]
	tlo_x=-(gracz["segmenty"][0].x-375)
	tlo_y=-(gracz["segmenty"][0].y-208)
	run = True
	while run:
		zegar.tick(60) # 60 fps
		gracz = gracze[id_gracza]
		predkosc = V_POCZATKOWE

		# odczytywanie klawiszy
		klawisze = pygame.key.get_pressed()

		dane = ""
		# rucha bazujący na klawiszach
		turn_speed = math.pi / 80
		if klawisze[pygame.K_LEFT] or klawisze[pygame.K_a]:
			gracz["segmenty"][0].angle -= turn_speed
		if klawisze[pygame.K_RIGHT] or klawisze[pygame.K_d]:
			gracz["segmenty"][0].angle += turn_speed
		else:
			gracz["predkosc"] = 2
		gracz["segmenty"][0].speed = gracz["predkosc"]
		
		
		tlo_x -= gracz["segmenty"][0].x_vel
		tlo_y -= gracz["segmenty"][0].y_vel
		dane = "move"
		for i in range(len(gracz["segmenty"])):
			dane+= " " + str(gracz["segmenty"][i].x) + " " + str(gracz["segmenty"][i].y)+ " " + str(gracz["segmenty"][i].angle)+ " " + str(gracz["segmenty"][i].speed)
		# wyślij dane do serwera i otrzymaj dane graczy
		jedzenie, gracze, czas_gry, szybkosc = serwer.wyslij(dane)
		# odśwież widok
		run = odswiez_widok(gracze, jedzenie, czas_gry, gracz["punkty"],okno,int(tlo_x),int(tlo_y),id_gracza,serwer)
		for zdarzenie in pygame.event.get():
			# zamknij okno jeżeli gracz kliknie x
			if zdarzenie.type == pygame.QUIT:
				run = False

			if zdarzenie.type == pygame.KEYDOWN:
				# zamknij okno jeżeli gracz kliknie esc
				if zdarzenie.key == pygame.K_ESCAPE:
					run = False
					
	serwer.rozlacz()
	pygame.display.quit()

class GUI(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		
		przycisk = QtWidgets.QPushButton('GRAJ', self)
		przycisk.clicked.connect(self.graj)
		przycisk.resize(przycisk.sizeHint())
		przycisk.resize(100,32)
		przycisk.move(220, 240)
		przycisk2 = QtWidgets.QPushButton('JAK GRAĆ', self)
		przycisk2.clicked.connect(self.jak_grac)
		przycisk2.resize(przycisk2.sizeHint())
		przycisk2.move(220, 282)
		przycisk2.resize(100,32)
		self.setGeometry(710, 390, 550, 405)
		tlo_gui = QtGui.QImage("logo.jpg")
		skaluj = tlo_gui.scaled(QtCore.QSize(550,405)) # dopasuj obraz do rozmiaru okna
		palette = QtGui.QPalette()
		palette.setBrush(QtGui.QPalette.Window, QtGui.QBrush(skaluj))				 
		self.setPalette(palette)
		self.setWindowTitle('Slither.io')
		self.show()
	
	def graj(self):
		NazwijWeza.main(self)

	def jak_grac(self):
		JakGrac.main(self)
	

class NazwijWeza(QtWidgets.QDialog):
	def __init__(self, parent = None):
		super(NazwijWeza, self).__init__(parent)
		QtWidgets.QDialog.__init__(self, parent)
		self.setWindowTitle('Nazwij węża')
		self.setFixedSize(200,110)
		self.setModal(True)
		self.tekst = QtWidgets.QTextEdit()
		self.tekst.setAutoFillBackground(True)
		self.przyciski = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal, self)
		self.przyciski.accepted.connect(self.graj)
		self.przyciski.rejected.connect(self.click_cancel)
		windowLayout = QtWidgets.QVBoxLayout()
		windowLayout.addWidget(self.tekst)
		windowLayout.addWidget(self.przyciski)
		self.setLayout(windowLayout)
	def main(parent = None):
		dialog = NazwijWeza(parent)
		dialog.show()
		dialog.exec()
	def graj(self):
		linia = self.tekst.document().toPlainText()
		# start okna w lewym górnym rogu
		os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0,30)
		# start okna pygame
		okno = pygame.display.set_mode((W,H))
		pygame.display.set_caption("Slither.io")
		self.accept()
		main(linia,okno,0,0)
	def click_cancel(self):
		self.reject()
	
app = QtWidgets.QApplication(sys.argv)
ex = GUI()
sys.exit(app.exec_())
