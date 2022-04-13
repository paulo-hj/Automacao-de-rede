import telnetlib

HOST = "10.50.50.50"

tn = telnetlib.Telnet(HOST)
tn.read_until(b":")
tn.write(b"digistar\n")

tn.write(b"enable\n")

tn.write(b"digistar\n")



saida = tn.read_until(b'#').decode()
print(saida)

while i <= 10:
    comando = "onu status 2/{}\n".format(i).encode()
    tn.write(b""+comando)
    i = i + 1
    saida = tn.read_until(b'#').decode()
    print(saida)

