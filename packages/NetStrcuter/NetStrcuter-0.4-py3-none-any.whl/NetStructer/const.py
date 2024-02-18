import socket
import pickle as json
from threading import Thread
from cryptography.fernet import Fernet
from time import sleep

__session__ = {}

class _encryption:

	def __init__(self,key=b'Tq_hBOzVozSYvyX8cvvqGZrmzkgaGssB99-azrqCleg='):
		self.__Key = Fernet(key)

	def encrypt(self,data:bytes):
		try:
			return self.__Key.encrypt(data)
		except:
			raise KeyError(f'bad key {self.__code}')

	def decrypt(self,data:bytes):
		try:
			return self.__Key.decrypt(data)
		except:
			raise KeyError(f'bad key {self.__code}')

class Bridge:

	def __init__(self,server,code=b'Tq_hBOzVozSYvyX8cvvqGZrmzkgaGssB99-azrqCleg='):
		assert server.type is socket.SOCK_STREAM and server.family is socket.AF_INET,'Bridge accepts only TCP server'
		self.__server = server
		self.__end_of_bytes = b'<end_of_bytes>'
		self.__enc = _encryption(key=code)
		self.data = b''

	def Link(addr):
		soc = socket.socket()
		soc.connect(addr)
		return Bridge(soc)

	def Check(data):
		try:
			json.dumps(data)
			return True
		except:
			return False

	def SendBuffer(self,buffer):
		try:
			if Bridge.Check(buffer):
				Buffer = self.__enc.encrypt(json.dumps(buffer))
				self.__server.send(Buffer+self.__end_of_bytes)
				return len(buffer)
			else:
				raise ValueError(f"can't not encode {buffer}")
		except TypeError:
			raise ValueError(f"can't not encode {buffer}")
		except ConnectionResetError:
			raise ConnectionResetError('the session has closed!')

	def RecvBuffer(self,buffer=1024,buffer_size=-1):
		try:
			while self.__end_of_bytes not in self.data:
				self.data += self.__server.recv(buffer)
				if len(self.data) >= buffer_size and buffer_size != -1:
					raise Error.BufferDataError(f'the data bigger than {buffer_size}')
			later_bit = self.data[self.data.find(self.__end_of_bytes)+len(self.__end_of_bytes):]
			pyl = json.loads(self.__enc.decrypt(self.data[:self.data.find(self.__end_of_bytes)]))
			self.data = later_bit
			return pyl
		except ConnectionResetError:
			raise ConnectionResetError('the session has closed!')

	def Close(self):
		self.__server.close()

	def TimeOut(self,out):
		self.__server.settimeout(out) 
		
class Error:

	class ServerInitializeError:

		def __init__(self,er):
			self.er = er
			
	class BufferDataError:
	
		def __init__(self,er):
			self.er = er
		
__run__ = True
		
class Server:

	def __init__(self,addr):
		self.addr = addr
		self.ip , self.port = addr[::1]
		self.loop = 0 

	def __tunnel__(ser,session):
		global sessions 
		while __run__:
			try:
				client , addr = ser.accept()
				session[addr[0]] = Bridge(client)
			except OSError:
				break

	def initialize(self):
		self.ser = socket.socket()
		self.ser.bind(self.addr)
		self.ser.listen()

	def listen(self):
		global __session__
		if hasattr(self,'ser'):
			Thread(target=Server.__tunnel__,args=(self.ser,__session__)).start()
			return Container()
		else:
			raise Error.ServerInitializeError('the initialize function must be called')
			
	def listen_on(self,func):
		global __session__
		if hasattr(self,'ser'):
			Thread(target=func,args=(self.ser,__session__,)).start()
		else:
			Error.ServerInitializeError('the initialize function must be called')
			
	def stop(self):
		global __run__
		__run__ = False
		sleep(1.5)
		self.ser.close()
				
class Container:

	def __init__(self):
		pass
		
	def __getitem__(self,key):
		if type(key) in [str,int]:
			return __session__[key] if key in __session__.keys() else None
		else:
			raise ValueError('')
		
	def __setitem__(self,key,value):
		global __session__
		__session__[key] = value
		
	def __enter__(self):
		return self
		
	def __exit__(self,x,y,z):
		pass
		
	def get(self,parm):
		return self.__getitem__(parm)
	
	def all(self):
		return [x for x in __session__.values()]
		
	def count(self):
		return len(__session__)
		
	def pop(self,parm):
		return __session__.pop(parm)
	
	def clear(self):
		__session__.clear()
		return None