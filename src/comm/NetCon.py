import os
import network
import time
import Log

class NetCon:
	FILE_NET_CON = "net_con"
	PATH_NET_CON = "/" + FILE_NET_CON
	CONN_RETRIES = 5
	
	def __init__(self, net_con_dir, ap_cfg, log_en):
		self.RootDir = net_con_dir
		self.Connected = False
		self.ApSsid = ap_cfg[0]
		self.ApPwd = ap_cfg[1]
		self.ApIp = ap_cfg[2]
		self.Log = Log.Log("NetCon", log_en)
	
	def AccessPointStart(self):
		self.Log.Print("Starting AP mode. SSID: {}, IP: {}".format(self.ApSsid, self.ApIp))
		self.NetIf = network.WLAN(network.AP_IF)
		self.NetIf.ifconfig((self.ApIp, '255.255.255.0', '192.168.0.1', '192.168.0.1'))
		self.NetIf.active(True)
		self.NetIf.config(essid=self.ApSsid, password=self.ApPwd)
		
		
	def AccessPointStop(self):
		self.Log.Print("Stopping AP mode.")
		self.NetIf.disconnect()
		self.NetIf.active(False)

	def StationSettingsStore(self, ssid, pwd):
		self.Log.Print("Storing station settings.")
		self.__NetConFileWrite(ssid, pwd)
	
	def StationSettingsReset(self):
		self.Log.Print("Resetting station settings.")
		self.__NetConFileDelete()
		
	def StationSettingsAreSet(self):
		return self.__NetConFileExists()
	
	def StationStart(self):
		if (self.__NetConFileExists() == False):
			self.Log.Print("No station settings stored.")
			return False
		elif (self.Connected == True):
			self.Log.Print("Already connected.")
			return False
		else:
			ssid, pwd = self.__NetConFileRead()
			self.Log.Print("Starting station mode. Connecting to SSID: {}".format(ssid))
			self.NetIf = network.WLAN(network.STA_IF)
			self.NetIf.active(True)
			
			# Attempt to connect to the configured AP, if
			# the attempt fails retry.
			i = 0
			while i < self.CONN_RETRIES:
				self.NetIf.connect(ssid, pwd)
				time.sleep(5)					
				self.Connected = self.NetIf.isconnected()
				if (self.Connected == True):
					self.Log.Print("Connected. ifconfig: {}".format(self.NetIf.ifconfig()))
					break
				else:
					self.Log.Print("Failed to connect.")
					i = i + 1
					self.Log.Print("Connect retries remaining: {}".format((self.CONN_RETRIES - i)))

			return self.Connected
	
	def StationStop(self):
		self.NetIf.disconnect()
		self.NetIf.active(False)
		self.Log.Print("Stopping station mode.")
		if(self.Connected == True):
			self.Log.Print("Disconnected.")
			self.Connected = False
		
		

	def __NetConFileExists(self):
		ls_dir = os.listdir(self.RootDir)
		self.Log.Print("Directory {} contains {}.".format(self.RootDir, ls_dir), "FileExists")
		for node in ls_dir:
			self.Log.Print("File {}".format(node), "FileExists")
			if (self.FILE_NET_CON in node):
				return True;

		return False;
	
	def __NetConFileWrite(self, ssid, pwd):
		f = open(self.RootDir + self.PATH_NET_CON, 'w')
		f.write(ssid + '\n')
		f.write(pwd + '\n')
		f.close()
	
	def __NetConFileRead(self):
		f = open(self.RootDir + self.PATH_NET_CON, 'r')
		ssid = f.readline().strip('\n')
		pwd = f.readline().strip('\n')
		f.close()
		self.Log.Print("SSID: {}, PWD: {}".format(ssid, pwd), "FileRead")
		return ssid, pwd
	
	def __NetConFileDelete(self):
		self.Log.Print("Deleting file {}".format(self.RootDir + self.PATH_NET_CON))
		try:
			os.remove(self.RootDir + self.PATH_NET_CON)
		except:
			pass

