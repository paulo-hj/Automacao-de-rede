import telnetlib
from tkinter import *
import awesometkinter as atk
from tkinter import tix

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

class EntPlaceHold(Entry):
    def __init__(self, master=None, placeholder= 'PLACEHOLDER', color= 'gray'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind('<FocusIn>', self.foc_in)
        self.bind('<FocusOut>', self.foc_out)

        self.put_placeholder()
    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color
    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()

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
        #Criação das saídas dos dados.
        #Criação dos botões.
        Button(self.primeiraTela, text="Verificar sinais das ONU", command=self.telaSinal).pack()
        #Criação das entradas dos dados.

    def telaSinal(self):
        segundaTela = tix.Tk()
        segundaTela.geometry("500x450+350+110")
        segundaTela.iconbitmap(default="icone\\logo.ico")
        segundaTela.title("Sinais das ONU's")
        segundaTela.configure(background="#2F4F4F") #"gray20"
        #s = ttk.Style()
        #s.theme_use('default')
        #segundaTela.resizable(width=False, height=False)
        self.segundaTela = segundaTela
        self.framesTelaSinal()
        self.widgetsTelaSinal()
        segundaTela.mainloop()
    
    def framesTelaSinal(self):
        self.primeiroFrame = atk.Frame3d(self.segundaTela, bg='#2F4F4F')
        self.primeiroFrame.place(relx=0.005, rely=0.005, relwidth=0.988, relheight=0.7)
        self.segundoFrame = atk.Frame3d(self.segundaTela, bg='#2F4F4F')
        self.segundoFrame.place(relx=0.005, rely=0.7, relwidth=0.988, relheight=0.3)

    def widgetsTelaSinal(self):
        #*Primeiro Frame
        #Criação dos texto.
        Label(self.primeiroFrame, text="Informe a porta e posição da ONU", font="verdana 13 bold", background="#2F4F4F").place(relx=0.17, rely=0.04)
        Label(self.primeiroFrame, text="Exemplo: 2/1", font="verdana 7", background="#2F4F4F").place(relx=0.55, rely=0.19)
        #Criação das saídas dos dados.
        self.primeiraOnu = Label(self.primeiroFrame, text="", font="arial 9 bold", anchor=N, background="#2F4F4F")
        self.primeiraOnu.place(relx=0.12, rely=0.55, relwidth=0.76, relheight=0.4)
        #Criação dos botões.
        self.botaoVerificar = atk.Button3d(self.primeiroFrame, text="Verificar sinal", command=self.verificarSinal)
        self.botaoVerificar.place(relx=0.4, rely=0.34, relwidth=0.19, relheight=0.13)
        #Criação das entradas dos dados.
        self.entradaPosicaoOnu = Entry(self.primeiroFrame, font="verdana 11 bold")
        self.entradaPosicaoOnu.place(relx=0.45, rely=0.18, relwidth=0.09, relheight=0.08)
        #Balão de mensagem.
        self.balaoBotaoVerificar = tix.Balloon(self.primeiroFrame)
        msg_balao_apagar = "Verificar o sinal da ONU informada acima."
        self.balaoBotaoVerificar.subwidget('label')['image'] = BitmapImage()  #Tira a seta do balão
        self.balaoBotaoVerificar.bind_widget(self.botaoVerificar, balloonmsg=msg_balao_apagar)

        #*Segundo Frame
        #Criação dos texto.
        Label(self.segundoFrame, text="Relatório", font="verdana 13 bold", background="#2F4F4F").place(relx=0.4, rely=0.07)
        Label(self.segundoFrame, text="Se preferir, gere um PDF com os sinais de todas as ONU's.", 
        font="calibre 9", background="#2F4F4F").place(relx=0.16, rely=0.32)
        #Criação das saídas dos dados.
        #Criação dos botões.
        atk.Button3d(self.segundoFrame, text="Gerar", command=self.verificarSinal).place(relx=0.42, rely=0.56, relwidth=0.14, relheight=0.3)

class Main(Comandos, Interface):
    def __init__(self):
        #self.conectar()
        #self.login()
        self.telaSinal()
        #self.telaPrincipal()
        #self.verificarSinal()

Main()
