import telnetlib

HOST = "10.50.50.50"
tn = telnetlib.Telnet(HOST)
tn.read_until(b":")
tn.write(b"digistar\n")

tn.write(b"enable\n")

tn.write(b"digistar\n")

saida = tn.read_until(b'#').decode()
print(saida)

def comandoOnu():
    i = 1
    j = 0
    while i < 17:
        comando = "onu status {}/{}\n".format(j,i).encode()
        tn.write(b""+comando)
        saida = tn.read_until(b'#').decode()
        print(saida)
        i = i + 1
        if i == 17 and j < 8:
            j = j + 1
            i = 1

comandoOnu()
