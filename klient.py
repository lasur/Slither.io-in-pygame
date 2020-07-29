import socket
import _pickle as pickle


class Polaczenie:
	"""
	klasa służąca do łączenia z serwerem oraz do wysyłania i otrzymywania 
	z niego informacji

	need to hardcode the host attirbute to be the server's ip
	"""
	def __init__(self):
		self.klient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = "192.168.56.1"
		self.port = 5555
		self.addr = (self.host, self.port)

	def polacz(self, nazwa):
		"""
		łączy z serwerem i zwraca ID połączonego gracza
		:param nazwa: str
		:return: int reprezentujący id
		"""
		self.klient.connect(self.addr)
		self.klient.send(str.encode(nazwa))
		wartosc = self.klient.recv(8)
		return int(wartosc.decode())

	def rozlacz(self):
		"""
		rozłącza z serwerem
		:return: None
		"""
		self.klient.close()

	def wyslij(self, dane, pick=False):
		"""
		wysyła informacje na serwer

		:param dane: str
		:param pick: boolean if should pickle or not
		:return: str
		"""
		try:
			if pick:
				self.klient.send(pickle.dumps(dane))
			else:
				self.klient.send(str.encode(dane))
			odpowiedz = self.klient.recv(2048*8)
			try:
				odpowiedz = pickle.loads(odpowiedz)
			except Exception as e:
				print(e)

			return odpowiedz
		except socket.error as e:
			print(e)