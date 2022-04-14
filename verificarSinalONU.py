import telnetlib
from tkinter import *

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
        #posicao = input("Informe a posição da ONU - Eemplo-> 2/1\n")
        posicao = self.entradaPosicaoOnu.get()
        comando = "onu status {}\n".format(posicao).encode()
        self.tn.write(b""+comando)
        saida = self.tn.read_until(b'#').decode()
        self.primeiraOnu["text"] = "{}".format(str(saida))

    def verificarTodosSinais(self):
        porta = 0
        onu = 1
        while onu < 3: #onu < 17:
            comando = "onu status {}/{}\n".format(porta,onu).encode()
            self.tn.write(b""+comando)
            saida = self.tn.read_until(b'#').decode()
            #self.primeiraOnu["text"] = "{}".format(str(saida))
            print(saida)
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
        segundaTela.mainloop()

    def widgetsTelaSinal(self):
        Label(self.segundaTela, text="Informe a posição da ONU\nEemplo-> 2/1")
        self.entradaPosicaoOnu = Entry(self.segundaTela)
        self.entradaPosicaoOnu.pack()
        Button(self.segundaTela, text="Verificar sinal", command=self.verificarSinal).pack()
        self.primeiraOnu = Label(self.segundaTela, text="", width=50, height=10)
        self.primeiraOnu.pack()

class Main(Comandos, Interface):
    def _init_(self):      
        self.conectar()
        self.login()
        self.telaPrincipal()
        #self.verificarSinal()

Main()
