import telnetlib
from tkinter import *
from tkinter import ttk
from tkinter import font
from awesometkinter import *
import awesometkinter as atk
import time
#Imports necessários para gerar um arquivo pdf.
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4 #Para as folhas.
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Image
import webbrowser

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
        posicao = self.entradaPosicaoOnu.get()
        comando = "onu status {}\n".format(posicao).encode()
        self.tn.write(b""+comando)
        saida = self.tn.read_until(b'#').decode()
        self.primeiraOnu["text"] = "{}".format(str(saida))

    def carregarBarraProgresso(self):
        for x in range(20):
            self.barraProgresso['value'] +=5
            self.segundaTela.update_idletasks()
            time.sleep(0.09)
        #self.barraProgresso.stop()
        self.geraRelatCliente()


#Deixa um texto dentro da entry, por enquanto sóe está sendo utilizado na tela de sinal.

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

class Relatorios():
    def printCliente(self):
        webbrowser.open("ONU Digistar.pdf")

    def geraRelatCliente(self):
        self.c = canvas.Canvas("ONU Digistar.pdf")
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(200, 790, "Sinais das ONU's")
        porta = 1
        onu = 1
        pularLinhaTexto = 733
        pularLinhaTraço = 720
        self.c.setFont("Helvetica", 10)
        while onu < 17: #onu < 17:
            lista2= ['d']
            comando = "onu status {}/{}\n".format(porta,onu).encode()
            self.tn.write(b""+comando)
            self.saida = str(self.tn.read_until(b'#').decode())
            #print(len(self.saida))
            #print(self.saida)
            if len(self.saida) == 186 or len(self.saida) == 191:
                lista = self.saida.split("N", 3)
                texto = str(lista[0] + lista[1] + lista[2])
                lista2 = texto.split("\r", 1)
                lista.append(texto.split("d", 2))
                texto2 = str(lista[2])
                lista = texto2.split("I", 1)
                self.c.drawString(25, pularLinhaTexto, lista2[0])
                self.c.rect(25, pularLinhaTraço, 545, 1, fill= True, stroke=True)
                self.c.drawString(115, pularLinhaTexto, lista[0])
                #time.sleep(5)
                pularLinhaTexto = pularLinhaTexto - 30
                pularLinhaTraço = pularLinhaTraço - 30
                onu = onu + 1
            else:
                onu = onu + 1
            if onu == 17 and porta < 8: #onu == 17 and porta < 8:
                porta = porta + 1
                onu = 1

        #self.c.rect(20, 720, 550, 200, fill= False, stroke=True)
        self.c.showPage()
        self.c.showPage()
        self.c.save()
        self.printCliente()

class Interface():
    def telaPrincipal(self):
        primeiraTela = Tk()
        primeiraTela.geometry("750x550+350+110")
        primeiraTela.iconbitmap(default="icone\\logo.ico")
        primeiraTela.title("BRCOM - OLT Digistar")
        primeiraTela.configure(background="#2F4F4F")
        #primeiraTela.resizable(width=False, height=False)
        self.primeiraTela = primeiraTela
        self.framesTelaPrincipal()
        self.widgetsTelaPrincipal()
        primeiraTela.mainloop()

    def framesTelaPrincipal(self):
        self.frameVertical = atk.Frame3d(self.primeiraTela, bg='#2F4F4F')
        self.frameVertical.place(relx=0, rely=0.225, relwidth=0.23, relheight=0.78)
        self.frameHorizontal = atk.Frame3d(self.primeiraTela, bg='#2F4F4F')
        self.frameHorizontal.place(relx=0, rely=0, relwidth=1.002, relheight=0.23)
        #self.frameQuadrado = Frame(self.primeiraTela, borderwidth=1, relief="solid")
        #self.frameQuadrado.place(relx=0.004, rely=0.004, relwidth=0.223, relheight=0.221)
        self.frameTela = atk.Frame3d(self.primeiraTela, bg='#9099A2')
        self.frameTela.place(relx=0.23, rely=0.2299, relwidth=0.771, relheight=0.776)

    def widgetsTelaPrincipal(self):
        #Criação dos texto.

        #Criação das saídas dos dados.
        #Criação dos botões.
        atk.Button3d(self.frameVertical, text="PROVISIONAR ONU", bg="#233237", command=self.telaSinal).place(relx=0.13, rely=0.04, relwidth=0.73, relheight=0.1)
        atk.Button3d(self.frameVertical, text="SINAL DA ONU", bg="#233237", command=self.telaSinal).place(relx=0.13, rely=0.15, relwidth=0.73, relheight=0.1)
        atk.Button3d(self.frameVertical, text="VLAN's UPLINK", bg="#233237", command=self.telaSinal).place(relx=0.13, rely=0.26, relwidth=0.73, relheight=0.1)
        #Criação das entradas dos dados.

    def telaSinal(self):
        segundaTela = Tk()
        segundaTela.geometry("500x450+350+110")
        #segundaTela.iconbitmap(default="icone\\logo.ico")
        segundaTela.title("Sinais das ONU's")
        segundaTela.configure(background="#2F4F4F") #"gray20" and "#2F4F4F"
        #segundaTela.resizable(width=False, height=False)
        self.segundaTela = segundaTela
        self.framesTelaSinal()
        self.widgetsTelaSinal()
        segundaTela.mainloop()
    
    def framesTelaSinal(self):
        self.primeiroFrame = atk.Frame3d(self.segundaTela, bg='#2F4F4F')
        self.primeiroFrame.place(relx=0.005, rely=0.005, relwidth=0.988, relheight=0.6)
        self.segundoFrame = atk.Frame3d(self.segundaTela, bg='#2F4F4F')
        self.segundoFrame.place(relx=0.005, rely=0.6, relwidth=0.988, relheight=0.4)

    def widgetsTelaSinal(self):
        #*Primeiro Frame
        #Criação dos texto.
        Label(self.primeiroFrame, text="Informe a porta e posição da ONU", font="verdana 13 bold", background="#2F4F4F").place(relx=0.17, rely=0.04)
        #Criação das saídas dos dados.
        self.primeiraOnu = Label(self.primeiroFrame, text="", font="arial 9 bold", anchor=N, background="#2F4F4F")
        self.primeiraOnu.place(relx=0.12, rely=0.55, relwidth=0.76, relheight=0.4)
        #Criação dos botões.
        self.botaoVerificar = atk.Button3d(self.primeiroFrame, text="Verificar sinal", command=self.verificarSinal)
        self.botaoVerificar.place(relx=0.4, rely=0.34, relwidth=0.19, relheight=0.14)
        #Criação das entradas dos dados.
        self.entradaPosicaoOnu = EntPlaceHold(self.primeiroFrame, 'Ex: 2/4')
        self.entradaPosicaoOnu.place(relx=0.45, rely=0.18, relwidth=0.09, relheight=0.08)
        #Balão de mensagem.
        atk.tooltip(self.botaoVerificar, "Verifica o sinal da ONU informada acima.")

        #*Segundo Frame
        #Criação dos texto.
        Label(self.segundoFrame, text="Relatório", font="verdana 13 bold", background="#2F4F4F").place(relx=0.42, rely=0.07)
        Label(self.segundoFrame, text="Se preferir, gere um PDF com os sinais de todas as ONU's.", 
        font="calibre 9", background="#2F4F4F").place(relx=0.16, rely=0.29)
        #Criação das saídas dos dados.
        #Criação dos botões.
        atk.Button3d(self.segundoFrame, text="Gerar", command=self.carregarBarraProgresso).place(relx=0.44, rely=0.47, relwidth=0.14, relheight=0.22)
        #Barra de progresso.
        self.barraProgresso = ttk.Progressbar(self.segundoFrame, orient=HORIZONTAL, length=300, mode='determinate')
        self.barraProgresso.place(relx=0.2, rely=0.75)

class Main(Comandos, Interface, Relatorios):
    def __init__(self):
        #self.conectar()
        #self.login()
        self.telaPrincipal()
        #self.verificarSinal()
        #self.telaSinal()

Main()
