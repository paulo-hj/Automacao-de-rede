import telnetlib

HOST = "10.50.50.50"

tn = telnetlib.Telnet(HOST)
tn.read_until(b":")
tn.write(b"digistar\n")

tn.write(b"enable\n")

tn.write(b"digistar\n")



saida = tn.read_until(b'#').decode()
print(saida)

tn.write(b"onu status 2/3\n")

saida = tn.read_until(b'#').decode()
print(saida)



        #tn.read_until(':'.encode())
        #tn.write((self.usuario+'\n').encode())
        #tn.read_until(':'.encode())

