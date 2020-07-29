"""
main server script for running slither.io server

can handle multiple/infinite connections on the same
local network
"""
import time
import math
import random
import socket
from _thread import *
import _pickle as pickle
from bs4 import BeautifulSoup
from Segment import Segment

# stworzenie serwera
Sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
Sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Stałe
with open("config.xml") as f:
	content = f.read()

xml = BeautifulSoup(content,features="html.parser")

PORT = int(xml.server.port.contents[0])

R_STARTOWE = int(xml.server.start_radius.contents[0])

CZAS = 60 * int(xml.server.round_time.contents[0])


W = int(xml.server.w.contents[0])
H = int(xml.server.h.contents[0])

NAZWA_HOSTA = socket.gethostname()
SERWER_IP = socket.gethostbyname(NAZWA_HOSTA)

# start serwera
try:
	Sckt.bind((SERWER_IP, PORT))
except socket.error as e:
	print(str(e))
	print("[SERWER] Serwer nie mógł zostać uruchomiony.")
	quit()

Sckt.listen()  # czekaj na połączenia

print(f"[SERWER] Serwer wystartował na IP {SERWER_IP}")

# zmienne
gracze = {}
jedzenie = []
polaczenia = 0
_id = 0
kolory = [(255,0,0), (255, 128, 0), (255,255,0), (128,255,0),(0,255,0),(0,255,128),(0,255,255),(0, 128, 255), (0,0,255), (128,0,255), (128,0,255),(255,0,255), (255,0,128),(128,128,128), (255,255,255)]
start = False
stat_time = 0
czas_gry = "Gra rozpocznie się wkrótce..."


# FUNKCJE
def jedz(gracze, jedzenie):
	"""
	sprawdza czy gracz napotkał jedzenie

	:param gracze: słownik graczy
	:param jedzenie: lista jedzenia
	:return: None
	"""
	for gracz in gracze:
		gr = gracze[gracz]
		x = gr["segmenty"][0].x
		y = gr["segmenty"][0].y
		for kuleczka in jedzenie:
			kulka_x = kuleczka[0]
			kulka_y = kuleczka[1]
			
			odleglosc = math.sqrt((x - kulka_x)**2 + (y-kulka_y)**2)
			if (odleglosc <= gr["segmenty"][0].size):
				gr["punkty"] = gr["punkty"] + 0.5
				if gr["punkty"]%3==0:
					seg = Segment(gr["segmenty"][len(gr["segmenty"])-1].x,
						gr["segmenty"][len(gr["segmenty"])-1].y,
						gr["segmenty"][len(gr["segmenty"])-1].size,
						gr["segmenty"][len(gr["segmenty"])-1].color)
					gr["segmenty"].append(seg)
				jedzenie.remove(kuleczka)

def kolizja_ze_scianami(x, y, r):
	if x - r < 0:
		return True
	if x + r > W:
		return True
	
	if y - r < 0:
		return True
	if y + r > H:
		return True

def granica(gracze):
	for gracz in gracze:
		p = gracze[gracz]
		if(kolizja_ze_scianami(p["segmenty"][0].x, p["segmenty"][0].y, R_STARTOWE)):
			gracze[gracz]["punkty"] = -10
			kolor = gracze[gracz]["segmenty"][0].color
			x, y = tutaj_ulokuj_gracza(gracze)
			segmenty = []
			for i in range(3):
				seg = Segment(x, y, R_STARTOWE, kolor)
				segmenty.append(seg)
			gracze[gracz]["segmenty"] = segmenty
			print(f"[GRA] " + gracze[gracz]["nazwa"] + " UDERZYŁ W ŚCIANĘ")

def zderzenie(gracze):
	"""
	obsługuje zderzenie dwóch graczy

	:param gracze: słownik
	:return: None
	"""
	posortowani_gracze = sorted(gracze, key=lambda x: gracze[x]["punkty"])
	for x, gracz1 in enumerate(posortowani_gracze):
		for gracz2 in posortowani_gracze[x+1:]:
			for seg1 in gracze[gracz1]["segmenty"]:
				for seg2 in gracze[gracz2]["segmenty"]:
					glowa1x = gracze[gracz1]["segmenty"][0].x
					glowa1y = gracze[gracz1]["segmenty"][0].y
					glowa2x = gracze[gracz2]["segmenty"][0].x
					glowa2y = gracze[gracz2]["segmenty"][0].y
					if seg1.x!=glowa1x and seg1.y!=glowa1y and seg2.x!=glowa2x and seg2.y!=glowa2y:
						gr1_x = seg1.x
						gr1_y = seg1.y

						gr2_x = seg2.x
						gr2_y = seg2.y
						
						odleglosc = math.sqrt((glowa1x - gr2_x)**2 + (glowa1y-gr2_y)**2)
						if odleglosc <= seg2.size + seg1.size:
							gracze[gracz2]["punkty"] = math.sqrt(gracze[gracz2]["punkty"]**2 + gracze[gracz1]["punkty"]**2) # dodawanie powierzchni
							gracze[gracz1]["punkty"] = -10
							kolor = gracze[gracz1]["segmenty"][0].color
							x, y = tutaj_ulokuj_gracza(gracze)
							segmenty = []
							for i in range(3):
								seg = Segment(x, y, R_STARTOWE, kolor)
								segmenty.append(seg)
							gracze[gracz1]["segmenty"] = segmenty
							print(f"[GRA] " + gracze[gracz2]["nazwa"] + " POKONAŁ " + gracze[gracz1]["nazwa"])
						odleglosc = math.sqrt((glowa2x - gr1_x)**2 + (glowa2y-gr1_y)**2)
						if odleglosc <= seg2.size + seg1.size:
							gracze[gracz1]["punkty"] = math.sqrt(gracze[gracz2]["punkty"]**2 + gracze[gracz1]["punkty"]**2) # dodawanie powierzchni
							gracze[gracz2]["punkty"] = -10
							kolor = gracze[gracz2]["segmenty"][0].color
							x, y = tutaj_ulokuj_gracza(gracze)
							segmenty = []
							for i in range(3):
								seg = Segment(x, y, R_STARTOWE, kolor)
								segmenty.append(seg)
							gracze[gracz2]["segmenty"] = segmenty
							print(f"[GRA] " + gracze[gracz1]["nazwa"] + " POKONAŁ " + gracze[gracz2]["nazwa"])

def zderzenie_kol(x1, y1, r1, x2, y2, r2):
	a = x1 - x2
	b = y1 - y2
	c = math.sqrt(math.pow(a, 2) + math.pow(b, 2))
	if c <= r1 + r2:
		return True

def ugotuj(jedzenie, n):
	"""
	tworzy jedzenie na planszy

	:param jedzenie: lista, do której dodaje się jedzenie
	:param n: liczba jedzenia do przygotowania
	:return: None
	"""
	for i in range(n):
		while True:
			stop = True
			x = random.randrange(10,W-10)
			y = random.randrange(10,H-10)
			for gracz in gracze:
				p = gracze[gracz]
				odleglosc = math.sqrt((x - p["segmenty"][0].x)**2 + (y-p["segmenty"][0].y)**2)
				if odleglosc <= R_STARTOWE + p["punkty"]:
					stop = False
			if stop:
				break

		jedzenie.append((x,y, random.choice(kolory)))


def tutaj_ulokuj_gracza(gracze):
	"""
	Wybiera lokalizację dla nowego gracza tak, aby nie powstał w miejscu, 
	w którym znajdują się inni gracze

	:param gracze: słownik
	:return: tuple(x,y)
	"""
	while True:
		stop = True
		x = random.randrange(0,W)
		y = random.randrange(0,H)
		for gracz in gracze:
			p = gracze[gracz]
			for seg in p["segmenty"]:
				odleglosc = math.sqrt((x - seg.x)**2 + (y-seg.y)**2)
				if odleglosc <= R_STARTOWE + p["punkty"]:
						stop = False
						break
		if stop:
			break
	return (x, y)


def watek_klienta(conn, _id):
	"""
	włącza się dla każdego połączonego gracza

	:param con: adres IP połączenia
	:param _id: int
	:return: None
	"""
	global polaczenia, gracze, jedzenie, czas_gry, start

	id_gracza = _id

	# otrzymanie nazwy gracza
	dane = conn.recv(16)
	nazwa = dane.decode("utf-8")
	print("[LOG]", nazwa, "połączył się z serwerem.")

	# tworzenie gracza
	kolor = kolory[id_gracza]
	x, y = tutaj_ulokuj_gracza(gracze)
	segmenty = []
	for i in range(3):
		seg = Segment(x, y, R_STARTOWE, kolor)
		segmenty.append(seg)
	gracze[id_gracza] = {"predkosc":2,"punkty":0,"nazwa":nazwa,"segmenty":segmenty}

	# wyślij dane o graczu
	conn.send(str.encode(str(id_gracza)))

	# serwer otrzymuje komendy od klienta
	# rozsyła potem dane do wszystkich klientów
	'''
	polecenia zaczynają się od:
	move
	get
	id - zwraca id gracza
	'''
	while True:

		if start:
			czas_gry = round(time.time()-start_time)
			# jeżeli czas rundy minie gra się zatrzymuje
			if czas_gry >= CZAS:
				start = False
		try:
			# otrzymaj dane od graczy
			dane = conn.recv(4096)
			if not dane:
				break
			dane = dane.decode("utf-8")
			# znajdź komendy z otrzymanych danych
			if dane.split(" ")[0] == "move":
				rozdziel = dane.split(" ")
				gracz=gracze[id_gracza]
				lx=[]
				ly=[]
				langle=[]
				lspeed=[]
				for i in range(len(rozdziel)):
					if i!=0 and i%4==0:
						lspeed.append(int(rozdziel[i]))
					if i!=0 and i%4==1:
						lx.append(float(rozdziel[i]))
					if i!=0 and i%4==2:
						ly.append(float(rozdziel[i]))
					if i!=0 and i%4==3:
						langle.append(float(rozdziel[i]))
				for i in range(len(gracz["segmenty"])):
					gracz["segmenty"][i].x = lx[i]
					gracz["segmenty"][i].y = ly[i]
					gracz["segmenty"][i].angle = langle[i]
					gracz["segmenty"][i].speed = lspeed[i]
				# Efekt węża
				for i in range(len(gracz["segmenty"])-1):
					dx = gracz["segmenty"][i].x - gracz["segmenty"][i+1].x
					dy = gracz["segmenty"][i].y - gracz["segmenty"][i+1].y
					new_angle = math.atan2(dy, dx)
					gracz["segmenty"][i+1].angle = new_angle
					gracz["segmenty"][i+1].speed = gracz["predkosc"]
				# Ograniczenie odległości pomiędzy segmentami
				limit = 12
				for i in range(len(gracz["segmenty"])-1):
					x1 = gracz["segmenty"][i].x
					y1 = gracz["segmenty"][i].y
					r1 = gracz["segmenty"][i].size - limit
					x2 = gracz["segmenty"][i+1].x
					y2 = gracz["segmenty"][i+1].y
					r2 = gracz["segmenty"][i+1].size - limit

					if zderzenie_kol(x1, y1, r1, x2, y2, r2):
						gracz["segmenty"][i+1].speed = 0
						
				for seg in gracz["segmenty"]:
					seg.update()
				# sprawdzaj czy gracz może zjeść tylko gdy gra jest aktywna
				if start:
					jedz(gracze, jedzenie)
					zderzenie(gracze)
					granica(gracze)
				# jeżeli ilość jedzenia < 300 ugotuj więcej
				if len(jedzenie) < 300:
					ugotuj(jedzenie, random.randrange(150,200))
					print("[GRA] Dodanie pokarmu.")
				velocity={gracz["segmenty"][0].x_vel,gracz["segmenty"][0].y_vel}
				wyslij_dane = pickle.dumps((jedzenie, gracze, czas_gry,velocity))

			elif dane.split(" ")[0] == "id":
				wyslij_dane = str.encode(str(id_gracza))

			else:
				# jeżeli brak dopasowanych komend wyślij dane o grze
				wyslij_dane = pickle.dumps((jedzenie, gracze, czas_gry))
			# wyślij dane do klientów
			conn.send(wyslij_dane)

		except Exception as e:
			print(e)
			break  # jeżeli jest wyjątek rozłącz gracza

		time.sleep(0.001)

	# Gdy użytkownik się rozłączy
	print("[ROZŁĄCZENIE] Nazwa:", nazwa, ", Id:", id_gracza, "został rozłączony.")

	polaczenia -= 1
	del gracze[id_gracza]  # usuń gracza z listy graczy
	conn.close()  # zamknij połączenie


#przygotuj plansze
ugotuj(jedzenie, random.randrange(300,350))

print("[GRA] Tworzenie poziomu...")
print("[SERWER] Oczekiwanie na graczy...")

# Oczekiwanie na nowe polączenia
while True:
	
	host, addr = Sckt.accept()
	print("[POŁACZENIE] Połaczono z:", addr)

	# wystartuj grę jeżeli gracz się połączy
	if addr[0] == SERWER_IP and not(start):
		start = True
		start_time = time.time()
		print("[ROZPOCZĘCIE] Gra wystartowała.")

	# zwiększ ilość połączeń, id, wystartuj wątek dla gracza
	polaczenia += 1
	start_new_thread(watek_klienta,(host,_id))
	_id += 1

# gdy serwer się wyłączy
print("[SERWER] Serwer wyłączony.")
