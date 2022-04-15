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
        primeiraTela.iconbitmap(default="icone\\logo.ico")
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
        segundaTela.geometry("500x450+350+110")
        segundaTela.iconbitmap(default="icone\\logo.ico")
        segundaTela.title("Sinais das ONU's")
        #segundaTela.resizable(width=False, height=False)
        self.segundaTela = segundaTela
        self.framesTelaSinal()
        self.widgetsTelaSinal()
        segundaTela.mainloop()
    
    def framesTelaSinal(self):
        self.primeiroFrame = Frame(self.segundaTela, borderwidth=2, relief="solid", background="#191970")
        self.primeiroFrame.place(relx=0.005, rely=0.005, relwidth=0.988, relheight=0.5)

    def widgetsTelaSinal(self):
        Label(self.primeiroFrame, text="Informe a porta e posição da ONU", font="arial 14 bold", background="#191970").place(relx=0.18, rely=0.03)
        Label(self.primeiroFrame, text="Exemplo: 2/1", font="arial 7", background="#191970").place(relx=0.54, rely=0.2)
        self.entradaPosicaoOnu = Entry(self.primeiroFrame, font="Calibre 12 bold")
        self.entradaPosicaoOnu.place(relx=0.47, rely=0.19, relwidth=0.07, relheight=0.1)
        Button(self.primeiroFrame, text="Verificar sinal", command=self.verificarSinal).place(relx=0.42, rely=0.35)
        self.primeiraOnu = Label(self.primeiroFrame, text="", font="arial 9 bold", anchor=N, background="#191970")
        self.primeiraOnu.place(relx=0.12, rely=0.47, relwidth=0.76, relheight=0.4)
        Label(self.primeiroFrame, text="", background="#191970").place(relx=0.82, rely=0.5, relwidth=0.12, relheight=0.12)

class Main(Comandos, Interface):
    def __init__(self):
        self.conectar()
        self.login()
        self.telaSinal()
        #self.verificarSinal()

Main()
