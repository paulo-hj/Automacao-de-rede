import telnetlib
from tkinter import *
from tkinter import ttk, messagebox
#from awesometkinter import *
import awesometkinter as atk
import tkinter.filedialog #Selecionar diretório.
#import tkinter.scrolledtext as tkst
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
        self.tn.write(b"session-timeout 0\n")

    def verificarSinal(self):
        posicao = self.entradaPosicaoOnu.get()
        comando = "onu status {}\n".format(posicao).encode()
        self.tn.write(b""+comando)
        saida = self.tn.read_until(b'#').decode()
        self.saidaSinalOnu["text"] = "{}".format(str(saida))

    def carregarBarraProgresso(self):
        self.barraProgresso.stop()
        for x in range(20):
            self.barraProgresso['value'] += 5
            self.segundaTela.update_idletasks()
            time.sleep(0.09)
        self.geraRelatCliente()

    def selecionarDiretorio(self):
        opcoes = {}
        nomeDiretorio= tkinter.filedialog.askdirectory(**opcoes)
        self.saidaDiretorio["text"] = nomeDiretorio

    def procurarOnu(self):
        self.tn.write(b"onu show discovered\n")
        saida = self.tn.read_until(b'#').decode()
        self.lista = saida.split(" ", 11)
        self.lista = self.lista[11].split("\r", 1)
        self.saidaMacOnu["text"] = self.lista[0]

    def copiarMac(self):
        self.quartaTela.clipboard_clear()
        self.quartaTela.clipboard_append(self.lista[0])
        self.quartaTela.update() #Salva o Ctrl+C mesmo se o programa fecha

class EntPlaceHold(Entry): #Deixa um texto dentro da entry, por enquanto só está sendo utilizado na tela de sinal.
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
    def printPdf(self):   
        webbrowser.open(self.nomeDiretorio+"\\ONU Digistar.pdf")

    def geraRelatCliente(self):
        try:
            self.c = canvas.Canvas(self.nomeDiretorio+"\\ONU Digistar.pdf")
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
                saida = str(self.tn.read_until(b'#').decode())
                if len(saida) == 186 or len(saida) == 191:
                    lista = saida.split("N", 3)
                    texto = str(lista[0] + lista[1] + lista[2])
                    lista2 = texto.split("\r", 1)
                    lista.append(texto.split("d", 2))
                    texto2 = str(lista[2])
                    lista = texto2.split("I", 1)
                    self.c.drawString(25, pularLinhaTexto, lista2[0])
                    self.c.rect(25, pularLinhaTraço, 545, 1, fill= True, stroke=True)
                    self.c.drawString(115, pularLinhaTexto, lista[0])
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
            self.printPdf()
        except:
            messagebox.showerror(title="Erro", message="Por favor, informe o caminho do arquivo.")

class Interface():
    def telaPrincipal(self):
        primeiraTela = Tk()
        primeiraTela.geometry("950x600+210+60")
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
        botaoTelaProvisionarOnu = atk.Button3d(self.frameVertical, text="PROVISIONAR ONU", bg="#233237", command=self.telaProvisionar)
        botaoTelaProvisionarOnu.place(relx=0.13, rely=0.04, relwidth=0.73, relheight=0.1)
        botaoTelaSinal = atk.Button3d(self.frameVertical, text="SINAL DA ONU", bg="#233237", command=self.telaSinal)
        botaoTelaSinal.place(relx=0.13, rely=0.15, relwidth=0.73, relheight=0.1)
        botaoTelaVlan = atk.Button3d(self.frameVertical, text="VLAN's UPLINK", bg="#233237", command=self.telaVlan)
        botaoTelaVlan.place(relx=0.13, rely=0.26, relwidth=0.73, relheight=0.1)
        #Criação das entradas dos dados.
        #Balão de mensagem.
        atk.tooltip(botaoTelaProvisionarOnu, "Autoriza ONU em modo bridge")
        atk.tooltip(botaoTelaSinal, "Verifica os sinais das onu")
        atk.tooltip(botaoTelaVlan, "Verifica todas as vlan criadas")

    def telaSinal(self):
        self.segundaTela = Toplevel() #Deixa essa janela como prioridade.
        self.segundaTela.geometry("730x599+430+60")
        self.segundaTela.iconbitmap(default="icone\\logo.ico")
        self.segundaTela.title("Sinais das ONU's")
        self.segundaTela.configure(background="#9099A2") #"gray20" and "#2F4F4F"
        self.segundaTela.resizable(width=False, height=False)
        self.segundaTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.segundaTela.focus_force() #Força o foco nessa janela.
        self.segundaTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.framesTelaSinal()
        self.widgetsTelaSinal()
    
    def framesTelaSinal(self):
        self.esquerdaFrameSinal = Frame(self.segundaTela, borderwidth=2, relief="solid", bg='#233237')
        self.esquerdaFrameSinal.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        self.direitaFrameSinal = Frame(self.segundaTela, borderwidth=2, relief="solid", bg='#233237')
        self.direitaFrameSinal.place(relx=0.8489, rely=0, relwidth=0.15, relheight=1.005)
        self.linhaFrameSinal = Frame(self.segundaTela, borderwidth=5, relief="solid", bg='#233237')
        self.linhaFrameSinal.place(relx=0.15, rely=0.5, relwidth=0.7, relheight=0.005)

    def widgetsTelaSinal(self):
        #*Primeiro Frame
        #Criação dos texto.
        Label(self.segundaTela, text="Informe a porta e posição da ONU", font="verdana 14 bold", background="#9099A2").place(relx=0.243, rely=0.03)
        #Criação das entradas dos dados.
        self.entradaPosicaoOnu = EntPlaceHold(self.segundaTela, 'Ex: 2/4')
        self.entradaPosicaoOnu.place(relx=0.475, rely=0.11, relwidth=0.055, relheight=0.043)
        #Criação dos botões.
        botaoVerificar = atk.Button3d(self.segundaTela, text="Verificar sinal", command=self.verificarSinal)
        botaoVerificar.place(relx=0.439, rely=0.188, relwidth=0.13, relheight=0.075)
        #Criação das saídas dos dados.
        self.saidaSinalOnu = Label(self.segundaTela, text="", font="arial 9 bold", anchor=N, background="#9099A2")#2F4F4F
        self.saidaSinalOnu.place(relx=0.18, rely=0.28, relwidth=0.65, relheight=0.2)
        #Balão de mensagem.
        atk.tooltip(botaoVerificar, "Verifica o sinal da ONU informada acima")

        #Criação dos texto.
        #Label(self.segundaTela, text="Relatório", font="verdana 13 bold", background="#2F4F4F").place(relx=0.42, rely=0.07)
        Label(self.segundaTela, text="Gerar PDF com os sinais de todas as ONU's", font="verdana 13 bold", background="#9099A2").place(relx=0.21, rely=0.535)
        Label(self.segundaTela, text="Defina a pasta que deseja salvar o arquivo", font="arial 8", background="#9099A2").place(relx=0.271, rely=0.625)
        Label(self.segundaTela, text="0%", font="arial 6", background="#9099A2").place(relx=0.235, rely=0.942)
        Label(self.segundaTela, text="100%", font="arial 6", background="#9099A2", foreground="green").place(relx=0.73, rely=0.942)
        #Criação das saídas dos dados.
        self.saidaDiretorio = Label(self.segundaTela, text="", font="arial 8", background="#E9C893")
        self.saidaDiretorio.place(relx=0.275, rely=0.655, relwidth=0.37)
        #Criação dos botões.
        botaoDefinirDiretorio = atk.Button3d(self.segundaTela, text="Definir", command=self.selecionarDiretorio)
        botaoDefinirDiretorio.place(relx=0.645, rely=0.64, relwidth=0.09, relheight=0.059)
        botaoGerarPdf = atk.Button3d(self.segundaTela, text="Gerar PDF", command=self.carregarBarraProgresso)
        botaoGerarPdf.place(relx=0.44, rely=0.78, relwidth=0.12, relheight=0.075)
        #Barra de progresso.
        self.barraProgresso = ttk.Progressbar(self.segundaTela, orient=HORIZONTAL, length=380, mode='determinate')
        self.barraProgresso.place(relx=0.24, rely=0.91)
        #Balão de mensagem.
        atk.tooltip(botaoDefinirDiretorio, "Selecione o diretório que deseja salvar o arquivo")
        atk.tooltip(botaoGerarPdf, 'Gera um arquivo com nome padrão de "ONU Digistar.pdf"')

    def telaVlan(self):
        self.terceiraTela = Toplevel() #Deixa essa janela como prioridade.
        self.terceiraTela.geometry("730x599+430+60")
        self.terceiraTela.iconbitmap(default="icone\\logo.ico")
        self.terceiraTela.title("Vlan's bridge/...")
        self.terceiraTela.configure(background="#9099A2") #"gray20" and "#2F4F4F"
        self.terceiraTela.resizable(width=False, height=False)
        self.terceiraTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.terceiraTela.focus_force() #Força o foco nessa janela.
        self.terceiraTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.framesTelaVlan()

    def framesTelaVlan(self):
        self.esquerdaFrameVlan = Frame(self.terceiraTela, borderwidth=2, relief="solid", bg='#233237')
        self.esquerdaFrameVlan.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        self.direitaFrameVlan = Frame(self.terceiraTela, borderwidth=2, relief="solid", bg='#233237')
        self.direitaFrameVlan.place(relx=0.8489, rely=0, relwidth=0.15, relheight=1.005)
        self.linhaFrameVlan = Frame(self.terceiraTela, borderwidth=5, relief="solid", bg='#233237')
        self.linhaFrameVlan.place(relx=0.15, rely=0.5, relwidth=0.7, relheight=0.005)

    def telaProvisionar(self):
        self.quartaTela = Toplevel() #Deixa essa janela como prioridade.
        self.quartaTela.geometry("730x599+430+60")
        self.quartaTela.iconbitmap(default="icone\\logo.ico")
        self.quartaTela.title("Provisionar")
        self.quartaTela.configure(background="#9099A2") #"gray20" and "#2F4F4F"
        self.quartaTela.resizable(width=False, height=False)
        self.quartaTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.quartaTela.focus_force() #Força o foco nessa janela.
        self.quartaTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.framesTelaProvisionar()
        self.widgetsTelaProvisionar()

    def framesTelaProvisionar(self):
        self.esquerdaFrameProvisionar = Frame(self.quartaTela, borderwidth=2, relief="solid", bg='#233237')
        self.esquerdaFrameProvisionar.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        self.direitaFrameProvisionar = Frame(self.quartaTela, borderwidth=2, relief="solid", bg='#233237')
        self.direitaFrameProvisionar.place(relx=0.8489, rely=0, relwidth=0.15, relheight=1.005)
        self.primeiroPassoFrame = Frame(self.quartaTela, borderwidth=2, relief="solid", bg='#9099A2')
        self.primeiroPassoFrame.place(relx=0.149, rely=0.113, relwidth=0.701, relheight=0.3)

        #self.linhaFrameProvisionar = Frame(self.quartaTela, borderwidth=5, relief="solid", bg='#233237')
        #self.linhaFrameProvisionar.place(relx=0.15, rely=0.5, relwidth=0.7, relheight=0.005)

    def widgetsTelaProvisionar(self):
        #Criação dos texto.
        Label(self.quartaTela, text="Provisionar ONU", font="verdana 14 bold", background="#9099A2").place(relx=0.375, rely=0.03)
        Label(self.quartaTela, text="1º", font="arial 9 bold", background="#9099A2").place(relx=0.17, rely=0.097)
        #Criação das saídas dos dados.
        self.saidaMacOnu = Label(self.primeiroPassoFrame, text="", background="#fff", anchor=N)
        self.saidaMacOnu.place(relx=0.378, rely=0.53, relwidth=0.241)
        #, relheight=0.12
        #Criação dos botões.
        botaoProcurarOnu = atk.Button3d(self.primeiroPassoFrame, text="Procurar", command=self.procurarOnu)
        botaoProcurarOnu.place(relx=0.426, rely=0.23, relwidth=0.14, relheight=0.22)
        self.botaoCopiarMac = Button(self.primeiroPassoFrame, text="Copiar", font="arial 7 bold", command=self.copiarMac)
        self.botaoCopiarMac.place(relx=0.625, rely=0.5286, relwidth=0.08, relheight=0.13)
        #Criação das entradas dos dados.
        #Balão de mensagem.
        atk.tooltip(botaoProcurarOnu, "Procura ONU a serem provisionadas")

class Main(Comandos, Interface, Relatorios):
    def __init__(self):
        self.conectar()
        self.login()
        self.telaPrincipal()
        #self.telaSinal()

Main()