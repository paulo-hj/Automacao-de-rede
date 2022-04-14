import telnetlib
from tkinter import *
from turtle import title

class Comandos():
    def conectar(self):
        HOST = "10.50.50.50"
        self.tn = telnetlib.Telnet(HOST)

    def login(self):
        self.tn.read_until(b":")
        self.tn.write(b"digistar\n")
        self.tn.write(b"enable\n")
        self.tn.write(b"digistar\n")
        saida = self.tn.read_until(b'#').decode()
        print(saida)

    def verificarSinal(self):
        porta = 0
        onu = 1
        while onu < 17:
            comando = "onu status {}/{}\n".format(porta,onu).encode()
            self.tn.write(b""+comando)
            saida = self.tn.read_until(b'#').decode()
            print(saida)
            onu = onu + 1
            if onu == 17 and porta < 8:
                porta = porta + 1
                onu = 1

class Interface():
    def telaPrincipal(self):
        primeiraTela = Tk()
        primeiraTela.geometry("700x500+350+110")
        primeiraTela.title("BRCOM - OLT Digistar")
        #primeiraTela.configure(background="")
        primeiraTela.resizable(width=False, height=False)
        primeiraTela.mainloop()

class Main(Comandos, Interface):
    def __init__(self):
        self.telaPrincipal()
        #self.conectar()
        #self.login()
        #self.verificarSinal()


Main()
