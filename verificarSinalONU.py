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
        while onu < 3: #onu < 17:
            comando = "onu status {}/{}\n".format(porta,onu).encode()
            self.tn.write(b""+comando)
            saida = self.tn.read_until(b'#').decode()
            self.primeiraOnu["text"] = "{}".format(str(saida))
            #print(saida)
            onu = onu + 1
            if onu == 3 and porta < 2: #onu == 17 and porta < 8:
                porta = porta + 1
                onu = 1

class Interface():
    def telaPrincipal(self):
        primeiraTela = Tk()
        primeiraTela.geometry("700x500+350+110")
        primeiraTela.title("BRCOM - OLT Digistar")
        #primeiraTela.configure(background="")
        primeiraTela.resizable(width=False, height=False)
        self.primeiraTela = primeiraTela
        self.widgetsTelaPrincipal()
        self.conectar()
        self.login()
        primeiraTela.mainloop()

    def widgetsTelaPrincipal(self):
        #Criação dos texto.
        Label(self.primeiraTela, text="Verificar sinal das ONU's").pack()
        #Criação dos botões.
        Button(self.primeiraTela, text="Verificar sinais das ONU", command=self.telaSinal).pack()
        #Criação das saídas dos dados.

    def telaSinal(self):
        segundaTela = Tk()
        segundaTela.geometry("700x500+350+110")
        segundaTela.title("Sinais das ONU's")
        segundaTela.resizable(width=False, height=False)
        self.segundaTela = segundaTela
        self.widgetsTelaSinal()
        self.verificarSinal()
        segundaTela.mainloop()

    def widgetsTelaSinal(self):
        self.primeiraOnu = Label(self.segundaTela, text="", width=97, height=32)
        self.primeiraOnu.pack()


class Main(Comandos, Interface):
    def __init__(self):
        self.telaPrincipal()
        #self.conectar()
        #self.login()
        #self.verificarSinal()


Main()
