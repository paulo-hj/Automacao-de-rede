from msilib.schema import ComboBox
import telnetlib
from tkinter import *
from tkinter import ttk, messagebox
from tkinter import font
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

class Conexao():
    def conectar(self):
        HOST = "10.50.50.50"
        self.tn = telnetlib.Telnet(HOST)

    def login(self):
        self.tn.read_until(b":")
        self.tn.write(b"digistar\n")
        self.tn.write(b"enable\n")
        self.tn.write(b"digistar\n")
        self.tn.write(b"session-timeout 0\n")
        saida = self.tn.read_until(b'#').decode()
        saida = self.tn.read_until(b'#').decode()
        print(saida)

class Comandos():
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
        self.nomeDiretorio= tkinter.filedialog.askdirectory(**opcoes)
        self.saidaDiretorio["text"] = self.nomeDiretorio

    def procurarOnu(self):
        try:
            self.tn.write(b"onu show discovered\n")
            saidaProcurarOnu = self.tn.read_until(b'#').decode()
            self.listaOnu = saidaProcurarOnu.split(" ", 11) #Filtra quantas ONU estão conectadas.
            nporta = self.listaOnu[3] #Para filtrar a porta que a ONU está conectada.
            nporta = nporta.split(":", 1)
            self.saidaPortaOlt["text"] = nporta[0] #Printa porta que ONU está conectada.
            self.saidaQuantOnu["text"] = self.listaOnu[10] #Printa quantas ONU estão conectadas.
            self.listaMacOnu = self.listaOnu[11].split("\r", 1) #Filtra mac da ONU achada.
            self.saidaMacOnu["text"] = self.listaMacOnu[0] #Printa Mac da ONU achada.
        except:
            self.saidaQuantOnu["text"] = "0"
            self.saidaPortaOlt["text"] = "0"
            self.saidaMacOnu["text"] = "Nenhuma"

    def copiarMac(self):
        try:
            self.quartaTela.clipboard_clear()
            self.quartaTela.clipboard_append(self.listaMacOnu[0]) #Copia Mac da ONU achada.
            self.quartaTela.update() #Salva o Ctrl+C mesmo se o programa fecha
        except:
            messagebox.showerror(title="Erro", message="Nenhum MAC para ser copiado.")

    def limparTelaProcurarOnu(self):
        self.listaMacOnu = []
        self.widgetsTelaProvisionarOnu()

    def verificarPorta(self):
        self.tn.write(b"onu set ?\n")
        saidaVerificarPorta = self.tn.read_until(b'#').decode()
        print(saidaVerificarPorta)
        self.listaPorta = saidaVerificarPorta.split(" ", 11)
        listaPortaOlt = self.listaPorta[10].split("/", 1)
        self.saidaPortaOlt["text"] = listaPortaOlt[0]

    def provisionarOnu(self):
        #self.marca = self.listBoxMarcaOnu.get(ACTIVE)
        try:
            quantMac = self.listaMacOnu[0] #Usado para fazer a validação com o try se a ONU foi achada ou não.
            if self.radioButtonSelecionado.get() == 1:
                if len(self.entradaLoginOnu.get()) > 1 and len(self.vlan) > 1:#or
                    comando = "onu set {0} {1} \n".format(self.listaPorta[10], self.listaMacOnu[0]).encode()
                    self.tn.write(b""+comando)
                    saidaProvisionarOnu = self.tn.read_until(b'#').decode()
                    print(saidaProvisionarOnu)
                else:
                    messagebox.showerror(title="Erro", message="Informe todos os campos obrigatórios.")
            elif self.radioButtonSelecionado.get() == 2:
                if len(self.entradaLoginOnu.get()) > 1 or len(self.vlan) > 1:#or
                    print("teste")
                else:
                    messagebox.showerror(title="Erro", message="Informe todos os campos obrigatórios.")
            else:
                messagebox.showerror(title="Erro", message="Informe todos os campos obrigatórios.")
        except:
            messagebox.showerror(title="Erro", message="É necessário primeiro procurar a ONU.")

    def listaListBoxVlan(self):
        self.listaVlan = ["131", "132", "133", "134", "135", "136", "137", "138","141", "142", "143", "144", "145", "146", "147", "148",
         "151", "152", "153", "154", "155", "156", "157", "158", "161", "162", "163", "164", "165", "166", "167", "168", 
         "341", "342", "343", "344", "345", "346", "347", "348", "351", "352", "353", "354", "355", "356", "357", "358",
          "361", "362", "363", "364", "365", "366", "367", "368", "521", "522", "523", "524", "525", "526", "527", "528"]
        self.nintVar = tkinter.IntVar(value=self.listaVlan)
        
    def listaListBox(self):
        listaMarcaOnu = ["Digistar" ,"Huawei" ,"Unne", "IntelBras", "Tp-link", "Cianet", "Shoreline", "Stavix"]
        for i in listaMarcaOnu:
            self.listBoxMarcaOnu.insert(END, i)

    def verificarOpcaoVlan(self, event):
        indices = self.listBoxVlan.curselection()
        if len(indices) > 0 :
            self.vlan = ",".join([self.listBoxVlan.get(i) for i in indices])
            self.verificaOpcaoRamal()
            self.verificaopcaoSplitterAndPortaCto()
        else:
            pass
            '''
        vlan = int(self.listBoxVlan.get(ACTIVE))
        print(vlan)
        if vlan >= 141 and vlan <= 148:
            self.saidaRamal["text"] = "14"
        '''

    def verificaOpcaoRamal(self):
            vlan = self.vlan
            if int(vlan) >= 131 and int(vlan) <= 138:
                self.saidaRamal["text"] = "13"
            elif int(vlan) >= 141 and int(vlan) <= 148:
                self.saidaRamal["text"] = "14"
            elif int(vlan) >= 151 and int(vlan) <= 158:
                self.saidaRamal["text"] = "15"
            elif int(vlan) >= 161 and int(vlan) <= 168:
                self.saidaRamal["text"] = "16"
            elif int(vlan) >= 341 and int(vlan) <= 348:
                self.saidaRamal["text"] = "34"
            elif int(vlan) >= 351 and int(vlan) <= 358:
                self.saidaRamal["text"] = "35"
            elif int(vlan) >= 361 and int(vlan) <= 368:
                self.saidaRamal["text"] = "36"
            elif int(vlan) >= 521 and int(vlan) <= 528:
                self.saidaRamal["text"] = "52"
 
    def verificaopcaoSplitterAndPortaCto(self):
        dicionarioSplitter = {"141":"0-1-P7-D17-T3-R14-C1", "142":"0-0-T3-R14-C2", "143":"3", "144":"4"}
        splitter = dicionarioSplitter[self.vlan]
        self.saidaSplitter["text"] = splitter
        dicionarioPortaCto = {"141":["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"], 
                                "142":["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"], 
                                "143":["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"],
                                "144":["1", "2", "3", "4"]}
        self.listaPortaCto = dicionarioPortaCto[self.vlan]
        self.widgetsTelaProvisionarComboBox()
        #self.quartaTela.update()

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
        esquerdaFrameSinal = Frame(self.segundaTela, borderwidth=2, relief="solid", bg='#233237')
        esquerdaFrameSinal.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameSinal = Frame(self.segundaTela, borderwidth=2, relief="solid", bg='#233237')
        direitaFrameSinal.place(relx=0.8489, rely=0, relwidth=0.15, relheight=1.005)
        linhaFrameSinal = Frame(self.segundaTela, borderwidth=5, relief="solid", bg='#233237')
        linhaFrameSinal.place(relx=0.15, rely=0.5, relwidth=0.7, relheight=0.005)

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
        esquerdaFrameVlan = Frame(self.terceiraTela, borderwidth=2, relief="solid", bg='#233237')
        esquerdaFrameVlan.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameVlan = Frame(self.terceiraTela, borderwidth=2, relief="solid", bg='#233237')
        direitaFrameVlan.place(relx=0.8489, rely=0, relwidth=0.15, relheight=1.005)
        linhaFrameVlan = Frame(self.terceiraTela, borderwidth=5, relief="solid", bg='#233237')
        linhaFrameVlan.place(relx=0.15, rely=0.5, relwidth=0.7, relheight=0.005)

    def telaProvisionar(self):
        self.quartaTela = Toplevel() #Deixa essa janela como prioridade.
        self.quartaTela.geometry("730x599+430+60")
        self.quartaTela.iconbitmap(default="icone\\logo.ico")
        self.quartaTela.title("Provisionar ONU")
        self.quartaTela.configure(background="#9099A2") #"gray20" and "#2F4F4F"
        self.quartaTela.resizable(width=False, height=False)
        self.quartaTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.quartaTela.focus_force() #Força o foco nessa janela.
        self.quartaTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.listaPortaCto = []
        self.vlan = ""
        self.radioButtonSelecionado = IntVar() #Variavel para receber a opção do modo da onu, bridge ou pppoe.
        self.listaListBoxVlan()
        self.framesTelaProvisionar()
        self.widgetsTelaProvisionarOnu()
        self.widgetsTelaProvisionarFrameDentro() #Função criada para poder limpar campos específicos.
        self.widgetsTelaProvisionarComboBox()
        self.listaListBox()

    def framesTelaProvisionar(self):
        esquerdaFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=2, relief="solid", bg='#233237')
        esquerdaFrameProvisionarOnu.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=2, relief="solid", bg='#233237')
        direitaFrameProvisionarOnu.place(relx=0.8489, rely=0, relwidth=0.15, relheight=1.005)
        linhaFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=1, relief="solid", background="#9099A2")
        linhaFrameProvisionarOnu.place(relx=0.149, rely=0.056, relwidth=0.701, relheight=1)
        self.dentroFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=1, relief="solid", background="#9099A2")
        self.dentroFrameProvisionarOnu.place(relx=0.149, rely=0.35, relwidth=0.701, relheight=2)

    def widgetsTelaProvisionarOnu(self):
        #Criação dos texto.
        Label(self.quartaTela, text="Provisionamento em espera", font="verdana 14 bold", background="#9099A2").place(relx=0.289, rely=0.03)
        labelQuantOnu = Label(self.quartaTela, text="Quant.", font="arial 10 bold", background="#9099A2")
        labelQuantOnu.place(relx=0.415, rely=0.132)
        labelPortaOlt = Label(self.quartaTela, text="Porta na OLT", font="arial 9 bold", background="#9099A2")
        labelPortaOlt.place(relx=0.529, rely=0.134)
        labelMac = Label(self.quartaTela, text="MAC", font="arial 9 bold", background="#9099A2")
        labelMac.place(relx=0.429, rely=0.173)
        #Criação das saídas dos dados.
        self.saidaQuantOnu = Label(self.quartaTela, text="", background="#fff", anchor=N)
        self.saidaQuantOnu.place(relx=0.479, rely=0.13, relwidth=0.035, relheight=0.031)
        self.saidaPortaOlt = Label(self.quartaTela, text="", background="#fff", anchor=N)
        self.saidaPortaOlt.place(relx=0.637, rely=0.13, relwidth=0.035, relheight=0.031)
        self.saidaMacOnu = Label(self.quartaTela, text="", background="#fff", anchor=N)
        self.saidaMacOnu.place(relx=0.4801, rely=0.17, relwidth=0.136, relheight=0.031)
        #Criação dos botões.
        botaoProcurarOnu = atk.Button3d(self.quartaTela, text="Procurar", command=self.procurarOnu)
        botaoProcurarOnu.place(relx=0.315, rely=0.135, relwidth=0.1, relheight=0.065)
        botaoCopiarMac = Button(self.quartaTela, text="Copiar", font="arial 7 bold", command=self.copiarMac)
        botaoCopiarMac.place(relx=0.621, rely=0.168, relwidth=0.0528, relheight=0.0341)
        botaoLimparMac = Button(self.quartaTela, text="Limpar", font="arial 7 bold", command=self.limparTelaProcurarOnu)
        botaoLimparMac.place(relx=0.677, rely=0.168, relwidth=0.0528, relheight=0.034)
        botaoProvisionar = atk.Button3d(self.quartaTela, text="Provisionar", bg="#2F4F4F", command=self.provisionarOnu)
        botaoProvisionar.place(relx=0.45, rely=0.88, relwidth=0.13, relheight=0.071)
        #Balão de mensagem.
        atk.tooltip(labelQuantOnu, "Quantidade de ONU que não foram provisionadas")
        atk.tooltip(labelMac, "MAC da ONU")
        atk.tooltip(botaoProcurarOnu, "Procura ONU que não foram provisionadas")
        atk.tooltip(botaoCopiarMac, "Cópia o MAC da ONU")
        atk.tooltip(botaoLimparMac, "Limpa todos os campos")
        atk.tooltip(labelPortaOlt, "Porta na OLT que a ONU está conectada")
        atk.tooltip(botaoProvisionar, "Provisiona a ONU achada acima")

    def widgetsTelaProvisionarFrameDentro(self):
        #Criação dos texto.
        Label(self.quartaTela, text="Provisionar ONU", font="verdana 14 bold", background="#9099A2").place(relx=0.375, rely=0.325)
        Label(self.dentroFrameProvisionarOnu, text="Modo da ONU", font="arial 11 bold", background="#9099A2").place(relx=0.391, rely=0.032)
        Label(self.dentroFrameProvisionarOnu, text="Login", font="arial 12 bold", background="#9099A2").place(relx=0.12, rely=0.09)
        Label(self.dentroFrameProvisionarOnu, text="Vlan", font="arial 12 bold", background="#9099A2").place(relx=0.46, rely=0.09)
        Label(self.dentroFrameProvisionarOnu, text="Marca", font="arial 12 bold", background="#9099A2").place(relx=0.75, rely=0.09)
        Label(self.dentroFrameProvisionarOnu, text="Ramal", font="arial 12 bold", background="#9099A2").place(relx=0.117, rely=0.19)
        Label(self.dentroFrameProvisionarOnu, text="Splitter", font="arial 12 bold", background="#9099A2").place(relx=0.45, rely=0.19)
        Label(self.dentroFrameProvisionarOnu, text="Porta da CTO", font="arial 12 bold", background="#9099A2").place(relx=0.73, rely=0.19)
        labelAstModoOnu = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#9099A2", foreground="red")
        labelAstModoOnu.place(relx=0.59, rely=0.031)
        labelAstLogin = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#9099A2", foreground="red")
        labelAstLogin.place(relx=0.21, rely=0.09)
        labelAstVlan = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#9099A2", foreground="red")
        labelAstVlan.place(relx=0.532, rely=0.09)
        labelAstRamal = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#9099A2", foreground="red")
        labelAstRamal.place(relx=0.216, rely=0.19)
        labelAstSplitter = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#9099A2", foreground="red")
        labelAstSplitter.place(relx=0.562, rely=0.19)
        labelAstPortaCto = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#9099A2", foreground="red")
        labelAstPortaCto.place(relx=0.9344, rely=0.189)
        #Criação das entradas dos dados.
        self.entradaLoginOnu = Entry(self.dentroFrameProvisionarOnu, bd=3, justify=CENTER)
        self.entradaLoginOnu.place(relx=0.043, rely=0.11, relheight=0.02)

        #Criação de listbox.
        self.listBoxVlan = tkinter.Listbox(self.dentroFrameProvisionarOnu, justify=CENTER, width=6, height=4, listvariable=self.nintVar)
        self.listBoxVlan.place(relx=0.461, rely=0.11)
        self.listBoxVlan.bind('<<ListboxSelect>>', self.verificarOpcaoVlan)

        self.listBoxMarcaOnu = Listbox(self.dentroFrameProvisionarOnu, justify=CENTER, width=11, height=4)
        self.listBoxMarcaOnu.place(relx=0.746, rely=0.11)
        #self.listBoxPortaCto = Listbox(self.dentroFrameProvisionarOnu, justify=CENTER, width=5, height=4)
        #self.listBoxPortaCto.place(relx=0.8, rely=0.211)
        #Criação de barra de rolagem.
        barraRolagemVlan = Scrollbar(self.dentroFrameProvisionarOnu, orient="vertical")
        self.listBoxVlan.configure(yscroll=barraRolagemVlan.set)
        barraRolagemVlan.place(relx=0.54, rely=0.11, relwidth=0.025,relheight=0.057)

        barraRolagemMarcaOnu = Scrollbar(self.dentroFrameProvisionarOnu, orient="vertical")
        self.listBoxMarcaOnu.configure(yscroll=barraRolagemMarcaOnu.set)
        barraRolagemMarcaOnu.place(relx=0.883, rely=0.11, relwidth=0.025,relheight=0.057)

        #Criação das saídas dos dados.
        self.saidaRamal = Label(self.dentroFrameProvisionarOnu, text="", background="#fff", anchor=CENTER)
        self.saidaRamal.place(relx=0.135, rely=0.211, relwidth=0.07)
        self.saidaSplitter = Label(self.dentroFrameProvisionarOnu, text="", background="#fff", anchor=CENTER)
        self.saidaSplitter.place(relx=0.398, rely=0.211, relwidth=0.239)

        #Criação de radio button.
        radioBridge = Radiobutton(self.dentroFrameProvisionarOnu, text="Bridge  |", value=1, variable=self.radioButtonSelecionado, background="#9099A2")
        radioBridge.place(relx=0.37, rely=0.05)
        radioPppoe = Radiobutton(self.dentroFrameProvisionarOnu, text="PPPOE", value=2, variable=self.radioButtonSelecionado, background="#9099A2")
        radioPppoe.place(relx=0.5, rely=0.05)

        #Criação de combo box.
        #self.portaCto = ttk.Combobox(self.dentroFrameProvisionarOnu, values=self.listaPortaCto)
        #self.portaCto.place(relx=0.7, rely=0.211)
        #Criação dos botões.
        #Balão de mensagem.
        atk.tooltip(labelAstModoOnu, "Campo obrigatório")
        atk.tooltip(labelAstLogin, "Campo obrigatório")
        atk.tooltip(labelAstVlan, "Campo obrigatório")
        atk.tooltip(labelAstRamal, "Campo obrigatório")
        atk.tooltip(labelAstSplitter, "Campo obrigatório")
        atk.tooltip(labelAstPortaCto, "Campo obrigatório")

    def widgetsTelaProvisionarComboBox(self):
        self.portaCto = ttk.Combobox(self.dentroFrameProvisionarOnu, values=self.listaPortaCto, justify=CENTER)
        self.portaCto.set("0")
        self.portaCto.place(relx=0.793, rely=0.211, relwidth=0.085)


class Main(Conexao, Comandos, Interface, Relatorios):
    def __init__(self):
        self.conectar()
        self.login()
        self.telaPrincipal()
        #self.telaSinal()

Main()