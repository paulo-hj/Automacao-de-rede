from operator import index
import telnetlib
from tkinter import *
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font
from unittest import TestResult
#from awesometkinter import *
import awesometkinter as atk
import tkinter.filedialog #Selecionar diretório.
#import tkinter.scrolledtext as tkst
import time
#Imports necessários para gerar um arquivo pdf.
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4 #Para as folhas.
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Image
import webbrowser
from PIL import ImageTk, Image
import base64 #Necessário para utilizar imagens dentro do código sem dá erro na hora de compilar.

#Banco de dados
from BD import *

from datetime import datetime

from verificarPeriferico import *

class Conexao():
    def conectarOlt(self):
        HOST = "10.50.50.50"
        self.tn = telnetlib.Telnet(HOST)

    def loginOlt(self):
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
        try:
            login = self.entradaPosicaoOnu.get()
            listaPortaPosicao = self.bdPortaPosicao(login)
            portaPosicao = listaPortaPosicao[0][0]
            comando = "onu status {} \n".format(portaPosicao).encode()
            self.tn.write(b""+comando)
            saida = self.tn.read_until(b'#').decode()
            self.saidaSinalOnu["text"] = "{}".format(str(saida))
            self.listaLog.append("Verificado sinal do login "+ login +" - Data/Hora: " + self.infoDataHora() + " - Usuário: ")
            self.addLog()
        except:
            self.saidaSinalOnu["text"] = ""
            messagebox.showerror(title="Erro", message="Informe um login válido.")

    def carregarBarraProgresso(self, nVezes):
        for x in range(nVezes):
            self.barraProgresso['value'] += 5
            self.relatoriosTela.update_idletasks()
            time.sleep(0.09)

    def selecionarDiretorio(self):
        opcoes = {}
        self.nomeDiretorio = tkinter.filedialog.askdirectory(**opcoes)
        self.saidaDiretorio["text"] = self.nomeDiretorio

    def procurarOnu(self):
        try:
            self.tn.write(b"onu show discovered\n")
            saidaProcurarOnu = self.tn.read_until(b'#').decode()
            self.listaOnu = saidaProcurarOnu.split(" ", 11) #Filtra quantas ONU estão conectadas.
            self.nporta = self.listaOnu[3] #Para filtrar a porta que a ONU está conectada.
            self.nporta = self.nporta.split(":", 1)
            self.saidaPortaOlt["text"] = self.nporta[0] #Printa porta que ONU está conectada.
            self.saidaQuantOnu["text"] = self.listaOnu[10] #Printa quantas ONU estão conectadas.
            self.listaMacOnu = self.listaOnu[11].split("\r", 1) #Filtra mac da ONU achada.
            self.saidaMacOnu["text"] = self.listaMacOnu[0] #Printa Mac da ONU achada.
            self.verificarPorta()
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

    def verificarPorta(self): #Verifica porta e posição que a onu está conectada.
        self.tn.write(b"onu set ?\n")
        saidaVerificarPorta = self.tn.read_until(b'#').decode()
        self.listaPorta = saidaVerificarPorta.split(" ", 11) #self.listaPorta[10] guarda a porta e posição.
        self.listaPortaOlt = self.listaPorta[10].split("/", 1)
        self.saidaPortaOlt["text"] = self.listaPortaOlt[0]
        self.tn.read_until(b'#').decode()
    
    def verificarGem(self, porta):
        if len(porta) < 2:
            return "50"+porta
        else:
            return "5"+porta

    def provisionarOnu(self):
        msgTratamentoErro = "É necessário preencher ou corrigir os campos baixo:"
        contTratamentoErro = 0
        login = self.entradaLoginOnu.get()
        dataHora = str(self.infoDataHora())
        try:
            quantMac = self.listaMacOnu[0] #Usado para fazer a validação com o try se a ONU foi achada ou não.
            if self.radioButtonSelecionado.get() != 1 and self.radioButtonSelecionado.get() != 2:
                msgTratamentoErro = msgTratamentoErro + "\nModo da ONU"
                contTratamentoErro = contTratamentoErro + 1
            if len(login) <= 0:
                msgTratamentoErro = msgTratamentoErro + "\nLogin"
                contTratamentoErro = contTratamentoErro + 1
            if len(self.vlan) <= 0:
                msgTratamentoErro = msgTratamentoErro + "\nVlan"
                contTratamentoErro = contTratamentoErro + 1
            if int(self.comboBoxPortaCto.get()) <= 0:
                msgTratamentoErro = msgTratamentoErro + "\nPorta da CTO"
                contTratamentoErro = contTratamentoErro + 1
            if len(login) > 30:
                msgTratamentoErro = msgTratamentoErro + "\nO login não pode ter mais de 30 caracteres."
                contTratamentoErro = contTratamentoErro + 1
            if contTratamentoErro > 0:
                messagebox.showerror(title="Erro", message=msgTratamentoErro)
            if contTratamentoErro == 0:
                if self.radioButtonSelecionado.get() == 1:
                    comandoAddOnu = "onu set {} {}\n".format(self.listaPorta[10], self.listaMacOnu[0]).encode()
                    self.tn.write(b""+comandoAddOnu)
                    self.tn.read_until(b'#').decode()
                    gpon = "gpon-"+self.listaPortaOlt[0]
                    gem = self.verificarGem(self.listaPortaOlt[1])
                    comandoAddBridge = "bridge add {} onu {} gem {} gtp 1 vlan {}\n".format(gpon, self.listaPortaOlt[1], gem, self.vlan).encode()
                    self.tn.write(b""+comandoAddBridge)
                    self.tn.read_until(b'#').decode()
                    modo = "Bridge"
                    self.listaLog.append("Provisionada ONU do login "+ login +" em modo bridge - Data/Hora: " + dataHora + " - Usuário: ")
                    self.addLog()
                elif self.radioButtonSelecionado.get() == 2:
                    comandoAddOnu = "onu set {} {}\n".format(self.listaPorta[10], self.listaMacOnu[0]).encode()
                    self.tn.write(b""+comandoAddOnu)
                    self.tn.read_until(b'#').decode()
                    gpon = "gpon-"+self.listaPortaOlt[0]
                    gem = self.verificarGem(self.listaPortaOlt[1])
                    comandoAddBridge = "bridge add {} onu {} gem {} gtp 1 vlan {} pppoe-ia\n".format(gpon, self.listaPortaOlt[1], gem, self.vlan).encode()
                    self.tn.write(b""+comandoAddBridge)
                    self.tn.read_until(b'#').decode()
                    modo = "PPPoE"
                    self.listaLog.append("Provisionada ONU do login "+ login +" em modo PPPoE - Data/Hora: " + dataHora + " - Usuário: ")
                    self.addLog()
                textoAguarde = "Aguarde"
                ponto = ""
                cont = 0
                contCor = 0
                for i in range(16):
                    if cont > 3:
                        if contCor == 4:
                            self.saidaAguardandoBotao["fg"] = "orange"
                        elif contCor == 8:
                            self.saidaAguardandoBotao["fg"] = "yellow"
                        elif contCor ==  12:
                            self.saidaAguardandoBotao["fg"] = "green"
                        textoAguarde = "Aguarde"
                        ponto = ""
                        cont = 0
                    self.saidaAguardandoBotao["text"] = textoAguarde = textoAguarde + ponto
                    self.saidaAguardandoBotao.update()
                    ponto = "."
                    cont += 1
                    contCor += 1
                    time.sleep(1)
                self.adicionarOnuDb(login, self.listaPorta[10], int(self.vlan), int(self.comboBoxPortaCto.get()), self.ramal, 
                self.path, modo, self.listaMacOnu[0], self.listBoxMarcaOnu.get(ACTIVE), int(self.nporta[0]), "paulo", dataHora)
                self.bdExclPortaCto(self.comboBoxPortaCto.get(), int(self.vlan))
                time.sleep(1)
                self.limparTelaProcurarOnu()
                self.saidaAguardandoBotao["text"] = ""
                self.saidaAguardandoBotao.update()
                self.widgetsButtonVerificarSinal()
        except:
            messagebox.showerror(title="Erro", message="É necessário primeiro procurar a ONU.")

    def listaListBoxVlan(self):
        self.listaVlan = ["131", "132", "133", "134", "135", "136", "137", "138","141", "142", "143", "144", "145", "146", "147", "148",
         "151", "152", "153", "154", "155", "156", "157", "158", "161", "162", "163", "164", "165", "166", "167", "168", 
         "341", "342", "343", "344", "345", "346", "347", "348", "351", "352", "353", "354", "355", "356", "357", "358",
          "361", "362", "363", "364", "365", "366", "367", "368", "521", "522", "523", "524", "525", "526", "527", "528"] 
        
    def listaListBoxMarcaOnu(self):
        listaMarcaOnu = ["Digistar" ,"Huawei", "ZTE" ,"Unne", "IntelBras", "Tp-link", "Cianet GW24AC", "Cianet GB01", "Shoreline", "Stavix", "China Mobile", "MaxPrint"]
        return listaMarcaOnu
    
    def preencherListaMarca(self, listaMarcaOnu):
        for i in listaMarcaOnu:
            self.listBoxMarcaOnu.insert(END, i)

    def verificarOpcaoVlan(self, event):
        indices = self.listBoxVlan.curselection()
        if len(indices) > 0 :
            self.vlan = ",".join([self.listBoxVlan.get(i) for i in indices])
            self.verificaOpcaoRamal()
            self.verificarPath()
            self.verificarPortaCto(self.vlan)
        else:
            pass
        
    def verificaOpcaoRamal(self):
            vlan = self.vlan
            if int(vlan) >= 131 and int(vlan) <= 138:
                self.ramal = "13"
                if self.verificarTela == 1 and self.verificarTela2 == 2: #Utilizada essas duas variaveis para saber se a requisição vem da tela de provisionar ou de dados.
                    self.saidaRamal["text"] = "13"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "13"
            elif int(vlan) >= 141 and int(vlan) <= 148:
                self.ramal = "14"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "14"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "14"
            elif int(vlan) >= 151 and int(vlan) <= 158:
                self.ramal = "15"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "15"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "15"
            elif int(vlan) >= 161 and int(vlan) <= 168:
                self.ramal = "16"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "16"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "16"
            elif int(vlan) >= 341 and int(vlan) <= 348:
                self.ramal = "34"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "34"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "34"
            elif int(vlan) >= 351 and int(vlan) <= 358:
                self.ramal = "35"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "35"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "35"
            elif int(vlan) >= 361 and int(vlan) <= 368:
                self.ramal = "36"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "36"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "36"
            elif int(vlan) >= 521 and int(vlan) <= 528:
                self.ramal = "52"
                if self.verificarTela == 1 and self.verificarTela2 == 2:
                    self.saidaRamal["text"] = "52"
                elif self.verificarTela == 2 and self.verificarTela2 == 1:
                    self.labelRamalDadosAtt["text"] = "52"

    def verificarPath(self):
        dicionarioPath = {"131":"0-1-P8-D24-T3-R13-C1", "132":"0-1-P8-D24-T3-R13-C2", "133":"0-1-P8-D24-T3-R13-C3",
        "134":"0-1-P8-D24-T3-R13-C4", "135":"0-1-P8-D24-T3-R13-C5", "136":"0-1-P8-D24-T3-R13-C6", "137":"0-1-P8-D24-T3-R13-C7", 
        "138":"0-1-P8-D24-T3-R13-C8", "141":"0-1-P7-D17-T3-R14-C1", "142":"0-1-P7-D17-T3-R14-C2", "143":"0-1-P7-D17-T3-R14-C3", 
        "144":"0-1-P7-D17-T3-R14-C4", "145":"0-1-P7-D17-T3-R14-C5", "146":"0-1-P7-D17-T3-R14-C6", "147":"0-1-P7-D17-T3-R14-C7", 
        "148":"0-1-P7-D17-T3-R14-C8", "151":"0-1-P3-D28-T3-R15-C1", "152":"0-1-P3-D28-T3-R15-C2", "153":"0-1-P3-D28-T3-R15-C3",
        "154":"0-1-P3-D28-T3-R15-C4", "155":"0-1-P3-D28-T3-R15-C5", "156":"0-1-P3-D28-T3-R15-C6", "157":"0-1-P3-D28-T3-R15-C7",
        "158":"0-1-P3-D28-T3-R15-C8", "161":"0-1-P6-D27-T3-R16-C1", "162":"0-1-P6-D27-T3-R16-C2", "163":"0-1-P6-D27-T3-R16-C3",
        "164":"0-1-P6-D27-T3-R16-C4", "165":"0-1-P6-D27-T3-R16-C5", "166":"0-1-P6-D27-T3-R16-C6", "167":"0-1-P6-D27-T3-R16-C7",
        "168":"0-1-P6-D27-T3-R16-C8", "341":"0-1-P4-D29-T3-R34-C1", "342":"0-1-P4-D29-T3-R34-C2", "343":"0-1-P4-D29-T3-R34-C3",
        "344":"0-1-P4-D29-T3-R34-C4", "345":"0-1-P4-D29-T3-R34-C5", "346":"0-1-P4-D29-T3-R34-C6", "347":"0-1-P4-D29-T3-R34-C7",
        "348":"0-1-P4-D29-T3-R34-C8", "351":"0-1-P1-D30-T3-R35-C1", "352":"0-1-P1-D30-T3-R35-C2", "353":"0-1-P1-D30-T3-R35-C3",
        "354":"0-1-P1-D30-T3-R35-C4", "355":"0-1-P1-D30-T3-R35-C5", "356":"0-1-P1-D30-T3-R35-C6", "357":"0-1-P1-D30-T3-R35-C7", 
        "358":"0-1-P1-D30-T3-R35-C8", "361":"0-1-P5-D32-T3-R36-C1", "362":"0-1-P5-D32-T3-R36-C2", "363":"0-1-P5-D32-T3-R36-C3",
        "364":"0-1-P5-D32-T3-R36-C4", "365":"0-1-P5-D32-T3-R36-C5", "366":"0-1-P5-D32-T3-R36-C6", "367":"0-1-P5-D32-T3-R36-C7",
        "368":"0-1-P5-D32-T3-R36-C8", "521":"0-1-P8-D31-T3-R52-C1", "522":"0-1-P8-D31-T3-R52-C2", "523":"0-1-P8-D31-T3-R52-C3",
        "524":"0-1-P8-D31-T3-R52-C4", "525":"0-1-P8-D31-T3-R52-C5", "526":"0-1-P8-D31-T3-R52-C6", "527":"0-1-P8-D31-T3-R52-C7",
        "528":"0-1-P8-D31-T3-R52-C8"}
        self.path = dicionarioPath[self.vlan]
        if self.verificarTela == 1 and self.verificarTela2 == 2:
            self.saidaPath["text"] = self.path
        elif self.verificarTela == 2 and self.verificarTela2 == 1:
            self.labelPathDadosAtt["text"] = self.path

    def verificarPortaCto(self, vlan):
        cont = 0
        tuplaPortasDisponiveis = self.bdListarPortaCto(vlan)
        listaPortasDisponiveis = list(tuplaPortasDisponiveis[0])
        for x in listaPortasDisponiveis:
            if x == "0":
                del listaPortasDisponiveis[cont]
            cont += 1
        self.listaPortaCto = listaPortasDisponiveis
        if self.verificarTela == 1 and self.verificarTela2 == 2:
            self.widgetsTelaProvisionarComboBox()
        elif self.verificarTela == 2 and self.verificarTela2 == 1:
            self.widgetsAtualizarDadosComboBox()

    def infoDataHora(self):
        dataEHora = datetime.now()
        dataEHora = dataEHora.strftime("%d/%m/%Y - %H:%M")
        return dataEHora

    def listaListBoxRelatorios(self):
        listaTiposRelatorios = ["-------------------------------------------", "Sinais das ONU's", "-------------------------------------------",
        "Todas as ONU's", "-------------------------------------------","Log", "-------------------------------------------", "Todas as Vlan's",
         "-------------------------------------------"]
        for i in listaTiposRelatorios:
            self.listBoxRelatorio.insert(END, i)

    def deletarOnu(self):
        try:
            login = self.entradaLoginDeletarOnu.get()
            loginDelete = self.entradaLoginDeletarOnu.get()
            escolha = messagebox.askyesno("Deletar ONU", 'Deseja deletar o login: "{}" ?'.format(loginDelete))
            if escolha == True:
                listaOnuVlanPortaposicaoMacPcto = self.dbComandoDeletarOnu(login)
                vlan = str(listaOnuVlanPortaposicaoMacPcto[0][0])
                portaPosicao = listaOnuVlanPortaposicaoMacPcto[0][1]
                mac = listaOnuVlanPortaposicaoMacPcto[0][2]
                path = listaOnuVlanPortaposicaoMacPcto[0][3]
                portaCto = str(listaOnuVlanPortaposicaoMacPcto[0][4])
                marca = listaOnuVlanPortaposicaoMacPcto[0][5]
                modoOnu = listaOnuVlanPortaposicaoMacPcto[0][6]
                listaPortaPosicao = portaPosicao.split("/", 1)
                gem = self.verificarGem(listaPortaPosicao[1])
                deleteBridge = "bridge delete gpon-{}-{}-{}-{}\n".format(listaPortaPosicao[0], listaPortaPosicao[1], gem, vlan).encode()
                self.tn.write(b""+deleteBridge)
                self.tn.read_until(b'#').decode()
                deleteOnu = "onu delete {}\n".format(portaPosicao).encode()
                self.tn.write(b""+deleteOnu)
                self.tn.read_until(b'#').decode()
                self.dbDeletarOnu(login)
                self.entradaLoginDeletarOnu.delete(0, END)
                self.entradaLoginDeletarOnu.focus()
                self.saidaOnuDeletada["text"] = ("Status: Sucesso\n\n Informações\n--------------------------------------------------------------------------------------------------------------------------------\n Login: " +
                 loginDelete + "\n--------------------------------------------------------------------------------------------------------------------------------\n Vlan: " + vlan + 
                 "\n--------------------------------------------------------------------------------------------------------------------------------\n Mac: " +
                  mac + "\n--------------------------------------------------------------------------------------------------------------------------------\n Path: " +
                  path + "\n--------------------------------------------------------------------------------------------------------------------------------\n Porta/Posição: " + portaPosicao + 
                  "\n--------------------------------------------------------------------------------------------------------------------------------\n Porta da CTO: " + portaCto + 
                  "\n--------------------------------------------------------------------------------------------------------------------------------\n Modo da ONU: " +
                  modoOnu + "\n--------------------------------------------------------------------------------------------------------------------------------\n Marca: " +
                  marca)
                self.bdAddPortaCto(portaCto, int(vlan))
                self.listaLog.append("Deletada ONU do login "+ loginDelete +" - Data/Hora: " + self.infoDataHora() + " - Usuário: ")
                self.addLog()
            else:
                self.entradaLoginDeletarOnu.delete(0, END)
                self.entradaLoginDeletarOnu.focus()
        except:
            self.saidaOnuDeletada["text"] = ""
            self.entradaLoginDeletarOnu.delete(0, END)
            self.entradaLoginDeletarOnu.focus()
            messagebox.showerror(title="Erro", message="Informe um login válido")

    def verificarSinalUltimaOnuProv(self):
        comando = "onu status {} \n".format(self.listaPorta[10]).encode()
        self.tn.write(b""+comando)
        saida = self.tn.read_until(b'#').decode()
        self.saidaSinalUltimaOnu["text"] = "{}".format(str(saida))

    def acessarGerWeb(self):
        self.listaLog.append("Acesso ao site - Data/Hora: " + self.infoDataHora() + " - Usuário: ")
        webbrowser.open("http://10.50.50.50/cgi-bin/p?logon.pt")
        self.addLog()
    
    def addLog(self):
        cont = 0
        log = "'{"
        for x in self.listaLog:
            if len(self.listaLog[cont]) > 0: #Transforma a lista em string para poder add no BD.
                log += self.listaLog[cont]
                log += "--"
                cont += 1
            else:
                break
        log += "}'"
        self.verificarLogCheio(cont, log)

    def returnBdListaLog(self):
        returnBdTuplaLog = self.bdListaLog()
        returnBdListaLog = returnBdTuplaLog[0][0][0]
        returnBdListaLog = returnBdListaLog.split("--")
        del(returnBdListaLog[-1])
        self.listaLog = returnBdListaLog
    
    def verificarLogCheio(self, cont, log):
        if cont > 50:
            log = "'{"+"Resete - " + self.infoDataHora() + "--"+"}'"
            del(self.listaLog[1:51])
            self.bdAddLog(log)
        else:
            self.bdAddLog(log)

class InformacoesOlt():
    def infoUptimeOlt(self):
        self.tn.write(b"show uptime\n")
        uptimeOlt = self.tn.read_until(b'#').decode()
        listaUptimeOlt = uptimeOlt.split(" ", 5)
        self.saidaUptime["text"] = listaUptimeOlt[4] + " dias"

    def infoMemoriaOlt(self):
        self.tn.write(b"show memory\n")
        memoriaOlt = self.tn.read_until(b'#').decode()
        listaMemoria = memoriaOlt.split(":", 2)
        listaMemoria = listaMemoria[1].split(" ", 1)
        self.saidaMemoria["text"] = "Total     |   Usada    |    Livre\n                          " + listaMemoria[1]

    def infoTemperaturaOlt(self):
        self.tn.write(b"show temperature\n")
        temperaturaOlt = self.tn.read_until(b'#').decode()
        listaTemperaturaOlt = temperaturaOlt.split(" ", 4)
        self.saidaTemperatura["text"] = listaTemperaturaOlt[3] + "  ºC"

    def infoLog(self):
        listaReversa = list(reversed(self.listaLog))
        for i in listaReversa:
            self.listBoxLog.insert(END, i)

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
    def verificarOpcaoRelatorio(self):
        tipoDeRelatorio = ""
        self.barraProgresso.stop()
        tipoDeRelatorio = self.listBoxRelatorio.get(ACTIVE)
        if tipoDeRelatorio == "Todas as ONU's" or tipoDeRelatorio == "Log":
                messagebox.showinfo(title="Em desenvolvimento", message="Contate o suporte pelo email: paulo.junior.ph@gmail.com"
                "\npara verificar em qual versão dos sistema está função estará disponível.")
        elif len(self.nomeDiretorio) == 0:
            messagebox.showerror(title="Erro", message="Por favor, informe o caminho do arquivo.")
        elif tipoDeRelatorio != "Sinais das ONU's" and tipoDeRelatorio != "Todas as Vlan's":
            messagebox.showerror(title="Erro", message="Escolha o modelo de relatório.")
        else:
            self.carregarBarraProgresso(14)
            if tipoDeRelatorio == "Sinais das ONU's":
                self.gerarRelatSinais()
            elif tipoDeRelatorio == "Todas as Vlan's":
                self.gerarRelatVlan()

    def gerarRelatSinais(self):
        listaRelatSinais = []
        cont = 0
        self.c = canvas.Canvas(self.nomeDiretorio+"\\Sinais das ONU - OLT Digistar.pdf")
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(200, 790, "Sinais das ONU's")
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(25, 820, self.infoDataHora())
        pularLinhaTexto = 700
        pularLinhaTraço = 690
        self.c.setFont("Helvetica", 10)
        self.c.drawString(40, 733, "LOGIN")
        self.c.drawString(275, 733, "STATUS")
        self.c.drawString(455, 733, "OLT Rx         ONU Rx")
        self.c.rect(25, 720, 545, 1, fill= True, stroke=True)
        listaRelatSinais = self.bdGerarRelatSinais()
        for i in listaRelatSinais:
            comando = "onu status {}\n".format(listaRelatSinais[cont][1]).encode()
            self.tn.write(b""+comando)
            saida = str(self.tn.read_until(b'#').decode())
            saida = saida.replace("onu status "+listaRelatSinais[cont][1]+"\r\n", "")
            saida = saida.replace("\r\n", "")
            saida = saida.replace("ONU  Link  FEC       OLT Rx Power  ONU Rx Power  Firmware upgrade  Progress", "")
            saida = saida.replace(listaRelatSinais[cont][1]+"  ", "")
            saida = saida.replace(" Disabled  ", "                                                   ")
            saida = saida.replace("Inactive", "")
            saida = saida.replace("\rdigistar#", "")
            self.c.drawString(30, pularLinhaTexto, listaRelatSinais[cont][0])
            self.c.drawString(270, pularLinhaTexto, saida)
            self.c.rect(25, pularLinhaTraço, 545, 1, fill= True, stroke=True)
            pularLinhaTexto = pularLinhaTexto - 30
            pularLinhaTraço = pularLinhaTraço - 30
            cont += 1
        self.c.showPage()
        self.c.showPage()
        self.c.save()
        self.carregarBarraProgresso(6)
        self.listaLog.append("Gerado relatório de sinais  - Data/Hora: " + self.infoDataHora() + " - Usuário: ")
        self.addLog()
        webbrowser.open(self.nomeDiretorio+"\\Sinais das ONU - OLT Digistar.pdf")
    
    def gerarRelatVlan(self):
        linha = 863
        cont = 0
        self.c = canvas.Canvas(self.nomeDiretorio+"\\VLANs - OLT Digistar.pdf")
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(190, 790, "VLANs - OLT Digistar")
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(25, 820, self.infoDataHora())
        comando = "bridge show ?\n".encode()
        self.tn.write(b""+comando)
        saida = str(self.tn.read_until(b'#').decode())
        saida = saida.replace("bridge show ?", "")
        saida = saida.replace("BRIDGE  Bridge identifier", "")
        saida = saida.replace("eth-6-60", "")
        saida = saida.replace("eth-6-61", "")
        saida = saida.replace("onu     Show information about onu", "")
        saida = saida.replace("ports   Show information about onu UNI ports", "")
        saida = saida.replace("<cr>", "")
        contLinhasVlan = saida.count("\r\n") 
        listaSaida = saida.split("\r\n", contLinhasVlan)
        for i in listaSaida:
            self.c.drawString(15, linha, listaSaida[cont])
            linha = linha - 30
            cont = cont + 1
            if cont == 28:
                break
        linha = 745
        for i in listaSaida:
            self.c.drawString(270, linha, listaSaida[cont])
            linha = linha - 30
            cont = cont + 1
            if cont == 52:
                break
        linha = 745
        for i in listaSaida:
            self.c.drawString(510, linha, listaSaida[cont])
            linha = linha - 30
            cont = cont + 1
            if cont == 76:
                break
        self.c.showPage() #Segunda página.
        linha = 795
        self.c.setFont("Helvetica-Bold", 10)
        for i in listaSaida:
            self.c.drawString(25, linha, listaSaida[cont])
            linha = linha - 30
            cont = cont + 1
            if cont == 102:
                break
        linha = 795
        for i in listaSaida:
            self.c.drawString(270, linha, listaSaida[cont])
            linha = linha - 30
            cont = cont + 1
            if cont == 128:
                break
        linha = 795
        for i in listaSaida:
            self.c.drawString(510, linha, listaSaida[cont])
            linha = linha - 30
            cont = cont + 1
            if cont == contLinhasVlan:
                break
        if cont >= 154: #Criação de uma terceira página, na espera de mais VLANs.
            cont = 154
            self.c.showPage() #Terceira página.
            linha = 795
            self.c.setFont("Helvetica-Bold", 10)
            for i in listaSaida:
                self.c.drawString(25, linha, listaSaida[cont])
                linha = linha - 30
                cont = cont + 1
                if cont == contLinhasVlan:
                    break
        self.carregarBarraProgresso(6)
        self.c.showPage()
        self.c.save()
        self.listaLog.append("Gerado relatório de VLANs  - Data/Hora: " + self.infoDataHora() + " - Usuário: ")
        self.addLog()
        webbrowser.open(self.nomeDiretorio+"\\VLANs - OLT Digistar.pdf")

class FiltrarOnu():
    def listarTodasOnuTelaDados(self):
        cont = 0
        quantOnuProv = self.bdVerificarQuantOnuProv()
        self.txtDadosOnu.configure(state="normal")
        self.txtDadosOnu.delete(1.0, END)
        infoOnu = self.bdListarTodasOnu()
        infoOnu = list(reversed(infoOnu))
        for i in quantOnuProv:
            login = infoOnu[cont][1]
            portaPosicao = infoOnu[cont][2]
            vlan = str(infoOnu[cont][3])
            portaCto = str(infoOnu[cont][4])
            ramal = infoOnu[cont][5]
            path = infoOnu[cont][6]
            modoOnu = infoOnu[cont][7]
            mac = infoOnu[cont][8]
            marca = infoOnu[cont][9]
            portaOlt = str(infoOnu[cont][10])
            usuario = infoOnu[cont][11]
            dataHora = infoOnu[cont][12]
            textoInfoOnu = "\n\n                      Login: "+login+"\n\n  Modo da Onu: "+modoOnu+"      Vlan: "+vlan+"       Porta/Posição: "+portaPosicao+"\n  Ramal: "+ramal+"               Path: "+path+"\n  Porta da CTO: "+portaCto+"    MAC: "+mac+"    Marca: "+marca+"\n\n  Usuário: "+usuario+"       Data/Hora: "+dataHora
            self.txtDadosOnu.insert(INSERT, textoInfoOnu)
            self.txtDadosOnu.insert(INSERT, "\n\n________________________________________________________________\n")
            cont += 1
        self.txtDadosOnu.configure(state="disabled")

    def filtrarOnu(self):
        login = self.entradaProcuraOnu.get()
        if login == "           LOGIN":
            self.comboBoxRamalTelaDados.set("Ramal")
            self.comboBoxVlanTelaDados.set("VLAN")
            self.comboBoxMarcaTelaDados.set("Marca")
            self.listarTodasOnuTelaDados()
        else:
            try:
                listaInfoOnu = self.bdFiltrarLoginOnu(login)
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                portaPosicao = listaInfoOnu[0][0]
                vlan = str(listaInfoOnu[0][1])
                portaCto = str(listaInfoOnu[0][2])
                ramal = listaInfoOnu[0][3]
                path = listaInfoOnu[0][4]
                modoOnu = listaInfoOnu[0][5]
                mac = listaInfoOnu[0][6]
                marca = listaInfoOnu[0][7]
                usuario = listaInfoOnu[0][8]
                dataHora = listaInfoOnu[0][9]
                textoInfoOnu = "\n\n                      Login: "+login+"\n\n  Modo da Onu: "+modoOnu+"      Vlan: "+vlan+"       Porta/Posição: "+portaPosicao+"\n  Ramal: "+ramal+"               Path: "+path+"\n  Porta da CTO: "+portaCto+"    MAC: "+mac+"    Marca: "+marca+"\n\n  Usuário: "+usuario+"       Data/Hora: "+dataHora
                self.txtDadosOnu.insert(INSERT, textoInfoOnu)
                self.txtDadosOnu.insert(INSERT, "\n\n________________________________________________________________\n")
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxRamalTelaDados.set("Ramal")
                self.comboBoxVlanTelaDados.set("VLAN")
                self.comboBoxMarcaTelaDados.set("Marca")
                self.widgetsEntradaTelaDados()
            except:
                self.comboBoxRamalTelaDados.set("Ramal")
                self.comboBoxVlanTelaDados.set("VLAN")
                self.comboBoxMarcaTelaDados.set("Marca")
                self.widgetsEntradaTelaDados()
                messagebox.showerror(title="Erro", message="ONU não encontrada!\nVerifique o login!")
                self.listarTodasOnuTelaDados()

    def filtrarPorVlan(self, event):
        cont = 0
        vlan = self.vlanSelecionada.get()
        if vlan == "VLAN":
            self.listarTodasOnuTelaDados()
        else:
            try:
                quantOnuProv = self.bdVerificarQuantOnuVlan(vlan)
                listaInfoOnu = self.bdFiltrarVlanOnu(vlan)
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                listaInfoOnu = list(reversed(listaInfoOnu))
                for i in quantOnuProv:
                    login = listaInfoOnu[cont][0]
                    portaPosicao = listaInfoOnu[cont][1]
                    portaCto = str(listaInfoOnu[cont][2])
                    ramal = listaInfoOnu[cont][3]
                    path = listaInfoOnu[cont][4]
                    modoOnu = listaInfoOnu[cont][5]
                    mac = listaInfoOnu[cont][6]
                    marca = listaInfoOnu[cont][7]
                    usuario = listaInfoOnu[cont][8]
                    dataHora = listaInfoOnu[cont][9]
                    textoInfoOnu = "\n\n                      Login: "+login+"\n\n  Modo da Onu: "+modoOnu+"      Vlan: "+vlan+"       Porta/Posição: "+portaPosicao+"\n  Ramal: "+ramal+"               Path: "+path+"\n  Porta da CTO: "+portaCto+"    MAC: "+mac+"    Marca: "+marca+"\n\n  Usuário: "+usuario+"       Data/Hora: "+dataHora
                    self.txtDadosOnu.insert(INSERT, textoInfoOnu)
                    self.txtDadosOnu.insert(INSERT, "\n\n________________________________________________________________\n")
                    cont += 1
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxRamalTelaDados.set("Ramal")
                self.comboBoxMarcaTelaDados.set("Marca")
                self.widgetsEntradaTelaDados()
            except:
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxRamalTelaDados.set("Ramal")
                self.comboBoxMarcaTelaDados.set("Marca")
                self.widgetsEntradaTelaDados()

    def filtrarPorRamal(self, event):
        cont = 0
        ramal = self.ramalSelecionado.get()
        quantOnuProv = self.bdVerificarQuantOnuRamal(ramal)
        if ramal == "Ramal":
            self.listarTodasOnuTelaDados()
        else:
            try:
                infoOnu = self.bdFiltrarRamalOnu(ramal)
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                infoOnu = list(reversed(infoOnu))
                for i in quantOnuProv:
                    login = infoOnu[cont][0]
                    portaPosicao = infoOnu[cont][1]
                    vlan = str(infoOnu[cont][2])
                    portaCto = str(infoOnu[cont][3])
                    path = infoOnu[cont][4]
                    modoOnu = infoOnu[cont][5]
                    mac = infoOnu[cont][6]
                    marca = infoOnu[cont][7]
                    usuario = infoOnu[cont][8]
                    dataHora = infoOnu[cont][9]
                    textoInfoOnu = "\n\n                      Login: "+login+"\n\n  Modo da Onu: "+modoOnu+"      Vlan: "+vlan+"       Porta/Posição: "+portaPosicao+"\n  Ramal: "+ramal+"               Path: "+path+"\n  Porta da CTO: "+portaCto+"    MAC: "+mac+"    Marca: "+marca+"\n\n  Usuário: "+usuario+"       Data/Hora: "+dataHora
                    self.txtDadosOnu.insert(INSERT, textoInfoOnu)
                    self.txtDadosOnu.insert(INSERT, "\n\n________________________________________________________________\n")
                    cont += 1
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxVlanTelaDados.set("VLAN")
                self.comboBoxMarcaTelaDados.set("Marca")
                self.widgetsEntradaTelaDados()
            except:
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxVlanTelaDados.set("VLAN")
                self.comboBoxMarcaTelaDados.set("Marca")
                self.widgetsEntradaTelaDados()

    def filtrarPorMarca(self, event):
        cont = 0
        marca = self.marcaSelecionada.get()
        quantOnuProv = self.bdVerificarQuantOnuMarca(marca)
        if marca == "Marca":
            self.listarTodasOnuTelaDados()
        else:
            try:
                infoOnuMarca = self.bdFiltrarMarcaOnu(marca)
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                infoOnuMarca = list(reversed(infoOnuMarca))
                for i in quantOnuProv:
                    login = infoOnuMarca[cont][0]
                    portaPosicao = infoOnuMarca[cont][1]
                    vlan = str(infoOnuMarca[cont][2])
                    portaCto = str(infoOnuMarca[cont][3])
                    ramal = infoOnuMarca[cont][4]
                    path = infoOnuMarca[cont][5]
                    modoOnu = infoOnuMarca[cont][6]
                    mac = infoOnuMarca[cont][7]
                    usuario = infoOnuMarca[cont][8]
                    dataHora = infoOnuMarca[cont][9]
                    textoInfoOnu = "\n\n                      Login: "+login+"\n\n  Modo da Onu: "+modoOnu+"      Vlan: "+vlan+"       Porta/Posição: "+portaPosicao+"\n  Ramal: "+ramal+"               Path: "+path+"\n  Porta da CTO: "+portaCto+"    MAC: "+mac+"    Marca: "+marca+"\n\n  Usuário: "+usuario+"       Data/Hora: "+dataHora
                    self.txtDadosOnu.insert(INSERT, textoInfoOnu)
                    self.txtDadosOnu.insert(INSERT, "\n\n________________________________________________________________\n")
                    cont += 1
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxVlanTelaDados.set("VLAN")
                self.comboBoxRamalTelaDados.set("Ramal")
                self.widgetsEntradaTelaDados()
            except:
                self.txtDadosOnu.configure(state="normal")
                self.txtDadosOnu.delete(1.0, END)
                self.txtDadosOnu.configure(state="disabled")
                self.comboBoxVlanTelaDados.set("VLAN")
                self.comboBoxRamalTelaDados.set("Ramal")
                self.widgetsEntradaTelaDados()

class Func():
    def carregarDadosOnu(self):
        try:
            self.loginAttDados = self.entradaLoginAtualizarDados.get()
            lista = self.bdCarregarDadosOnuAtt(self.loginAttDados)
            self.vlan = lista[0][0]
            self.vlan1 = self.vlan #Criado para recuperar a porta da vlan na função atualizarDadosOnuAba.
            pathAttDados = lista[0][1]
            self.portaCtoAttDados = str(lista[0][2])
            ramalAttDados = lista[0][3]
            marcaAttDados = lista[0][4]
            self.entradaLoginDadosAtt.delete(0, END)
            self.entradaLoginDadosAtt.insert(END, self.loginAttDados)
            self.labelPathDadosAtt["text"] = pathAttDados
            self.labelRamalDadosAtt["text"] = ramalAttDados
            #self.entradaMarcaDadosAtt.delete(0, END)
            #self.entradaMarcaDadosAtt.insert(END, self.marcaAttDados)
            self.verificarPortaCto(self.vlan)
            self.comboBoxMarcaAtt.set(marcaAttDados)
            self.comboBoxPortaCtoAtt.set(self.portaCtoAttDados)
            self.verificarDadosCarregados = 1

        except:
            self.entradaLoginAtualizarDados.delete(0, END)
            self.entradaLoginDadosAtt.delete(0, END)
            self.widgetsAtualizarDadosLabelEntrada()
            self.comboBoxPortaCtoAtt.set("0")
            self.comboBoxMarcaAtt.set("")
            self.verificarDadosCarregados = 0
            messagebox.showerror(title="Erro", message="Informe um login válido")

    def atualizarDadosOnuAba(self):
        self.entradaLoginAtualizarDados.delete(0, END)
        if self.verificarDadosCarregados == 1:
            self.bdAddPortaCto(self.portaCtoAttDados, int(self.vlan1))
            portaCto = self.comboBoxPortaCtoAtt.get()
            loginAtt = self.entradaLoginDadosAtt.get()
            marcaAtt = str(self.comboBoxMarcaAtt.get())
            self.dbCAttDadosOnu(loginAtt, int(self.vlan), self.labelPathDadosAtt["text"], portaCto, self.labelRamalDadosAtt["text"], marcaAtt, self.loginAttDados)
            self.bdExclPortaCto(portaCto, int(self.vlan))
            self.entradaLoginDadosAtt.delete(0, END)
            self.widgetsAtualizarDadosLabelEntrada()
            self.comboBoxPortaCtoAtt.set("0")
            self.comboBoxMarcaAtt.set("")
            self.verificarDadosCarregados = 0

            messagebox.showinfo("Informações atualizadas", "As informações foram atualizadas com sucesso!\nLogin: "+self.loginAttDados+ "=> Login: "+loginAtt)
            self.listaLog.append("Alterado dados do login "+self.loginAttDados+" para login: "+loginAtt+" - Data/Hora: " +self.infoDataHora()+ " - Usuário: ")

        else:
            messagebox.showerror(title="Erro", message="Primeiro informe a ONU")
    '''
    def listaAutoComplete(self): Excluir caso não for utilizar o auto complete.
        listaLogin = []
        cont = 0
        listaTuplaLogin = self.bdListarLogin()
        quantOnuProv = self.bdVerificarQuantOnuProv()
        for i in quantOnuProv:
            loginsStr = listaTuplaLogin[cont][0]
            listaLogin.append(loginsStr)
            cont += 1
        return listaLogin
    '''

    #def displayControlA(self, event):
    '''
    def configDisplay(self):
        """Display configs"""
        display = self.sinalTela
        display.bind('<Return>', self.verificarSinal)
        #display.bind('<KP_Enter>', self.verificarSinal)
    '''

class Interface():
    def telaPrincipal(self):
        primeiraTela = Tk()
        primeiraTela.geometry("950x600+210+60")
        primeiraTela.iconbitmap(default="icone\\logo.ico")
        primeiraTela.title("BROLT") #CleverOLT ERP    OU     ControlOLT ERP
        primeiraTela.configure(background="#062F4F")
        #primeiraTela.resizable(width=False, height=False)
        self.primeiraTela = primeiraTela
        self.imgOlt = PhotoImage(file="imagens/imgOlt.png")
        #self.barraDeMenuTelaPrincipal()
        self.framesTelaPrincipal()
        self.widgetsTelaPrincipal()
        self.infoUptimeOlt()
        self.infoTemperaturaOlt()
        self.infoMemoriaOlt()
        primeiraTela.mainloop()

    def framesTelaPrincipal(self):
        self.frameVertical = atk.Frame3d(self.primeiraTela, bg='#062F4F')
        self.frameVertical.place(relx=0, rely=0.225, relwidth=0.23, relheight=0.78)
        self.frameHorizontal = atk.Frame3d(self.primeiraTela, bg='#062F4F')
        self.frameHorizontal.place(relx=0, rely=0, relwidth=1.002, relheight=0.23)
        self.frameTela = atk.Frame3d(self.primeiraTela, bg='#d9d9d9')
        self.frameTela.place(relx=0.23, rely=0.2299, relwidth=0.771, relheight=0.776)
        self.frameLinhaTelaPrincipal = atk.Frame3d(self.frameVertical, bg='#38576b')
        self.frameLinhaTelaPrincipal.place(relx=0.04, rely=0.68, relwidth=0.92, relheight=0.055)

        #Imagens
        #imagemOltDigistar = Label(self.frameTela, image=self.imgOlt)
        #imagemOltDigistar.place(relx=0.105, rely=0.05)

        self.imgLogoG = PhotoImage(file="imagens/pngLogoTelaPrincipal.png")
        canvas = Canvas(self.frameHorizontal,  bd=0, highlightthickness=0, width=self.imgLogoG.width(), height=self.imgLogoG.height())
        canvas.create_image(0, 0, anchor='nw',image=self.imgLogoG)
        canvas.place(x=90, y=13)

        #self.primeiraTela.attributes('-alpha', 0.7)

    def widgetsTelaPrincipal(self):
        #Criação dos texto.
        Label(self.frameTela, text="Uptime:", font="Ivy 10 bold", background="#d9d9d9").place(relx=0.154, rely=0.223)
        Label(self.frameTela, text="Temperatura:", font="Ivy 10 bold", background="#d9d9d9").place(relx=0.154, rely=0.2848)
        Label(self.frameTela, text="Memória:", font="Ivy 10 bold", background="#d9d9d9").place(relx=0.518, rely=0.224)
        Label(self.frameVertical, text="BROLT  v2.1.2", font="Ivy 9 bold", background="#062F4F").place(relx=0.3, rely=0.945)
        #Criação das saídas dos dados.
        self.saidaUptime = Label(self.frameTela, text="", background="#d9d9d9", font="Ivy 10")
        self.saidaUptime.place(relx=0.228, rely=0.224)
        self.saidaTemperatura = Label(self.frameTela, text="", background="#d9d9d9", font="Ivy 10")
        self.saidaTemperatura.place(relx=0.28, rely=0.2845)
        self.saidaMemoria = Label(self.frameTela, text="", background="#d9d9d9", anchor=N, font="Ivy 9")
        self.saidaMemoria.place(relx=0.602, rely=0.226, relwidth=0.235, relheight=0.1)
        #Criação dos botões.
        botaoTelaDadosOnu = atk.Button3d(self.frameVertical, text="PROVISIONADAS", bg="#38576b", command=self.telaDadosClientes)
        botaoTelaDadosOnu.bind('<Enter>', lambda e: botaoTelaDadosOnu.configure(cursor = "hand2"))
        botaoTelaDadosOnu.place(relx=0.13, rely=0.055, relwidth=0.73, relheight=0.1)
        botaoTelaProvisionarOnu = atk.Button3d(self.frameVertical, text="PROVISIONAR ONU", bg="#38576b", command=self.telaProvisionar)
        botaoTelaProvisionarOnu.bind('<Enter>', lambda e: botaoTelaProvisionarOnu.configure(cursor = "hand2"))
        botaoTelaProvisionarOnu.place(relx=0.13, rely=0.175, relwidth=0.73, relheight=0.1)
        botaoTelaSinal = atk.Button3d(self.frameVertical, text="VERIFICAR SINAL", bg="#38576b", command=self.telaSinal)
        botaoTelaSinal.bind('<Enter>', lambda e: botaoTelaSinal.configure(cursor = "hand2"))
        botaoTelaSinal.place(relx=0.13, rely=0.294, relwidth=0.73, relheight=0.1)
        botaoTelaDeletarOnu = atk.Button3d(self.frameVertical, text="Deletar ONU", bg="#38576b", command=self.telaDeletarOnu)
        botaoTelaDeletarOnu.bind('<Enter>', lambda e: botaoTelaDeletarOnu.configure(cursor = "hand2"))
        botaoTelaDeletarOnu.place(relx=0.13, rely=0.413, relwidth=0.73, relheight=0.1)
        botaoLog = Button(self.frameTela, text="Log", font="Ivy 8 bold", background="#38576b", foreground="#d9d9d9", command=self.telaLog, cursor = "hand2")
        botaoLog.place(relx=0.155, rely=0.37, relwidth=0.051, relheight=0.058)
        botaoWeb = Button(self.frameTela, text="Web", font="Ivy 8 bold", background="#38576b", foreground="#d9d9d9", command=self.acessarGerWeb, cursor = "hand2")
        botaoWeb.place(relx=0.218, rely=0.37, relwidth=0.051, relheight=0.058)
        botaoTelaRelatorios = atk.Button3d(self.frameVertical, text="RELATÓRIOS", bg="#38576b", command=self.telaRelatorios)
        botaoTelaRelatorios.bind('<Enter>', lambda e: botaoTelaRelatorios.configure(cursor = "hand2"))
        botaoTelaRelatorios.place(relx=0.13, rely=0.535, relwidth=0.73, relheight=0.1)
        botaoTelaSobre = atk.Button3d(self.frameVertical, text="SOBRE O SISTEMA", bg="#38576b", command=self.telaSobre)
        botaoTelaSobre.bind('<Enter>', lambda e: botaoTelaSobre.configure(cursor = "hand2"))
        botaoTelaSobre.place(relx=0.13, rely=0.775, relwidth=0.73, relheight=0.1)
        #Criação das entradas dos dados.
        #Balão de mensagem.
        atk.tooltip(botaoTelaDadosOnu, "Verificar todas as onu's provisionadas")
        atk.tooltip(botaoTelaProvisionarOnu, "Autorizar onu em modo Bridge ou PPPoE")
        atk.tooltip(botaoTelaSinal, "Verificar os sinais das onu's")
        atk.tooltip(botaoTelaDeletarOnu, "Deletar onu")
        atk.tooltip(botaoTelaRelatorios, "Gerar relatórios em PDF")

    def barraDeMenuTelaPrincipal(self):
        barramenus = Menu(self.primeiraTela) #Cria uma barra de menus.

        arquivomenu = Menu(barramenus) #Cria uma coluna dentro do menu.
        arquivomenu = Menu(arquivomenu, tearoff=0) #Tira um tracejado que vem por padrão nos menu.
        barramenus.add_cascade(label="Arquivo", menu=arquivomenu) #Da um nome a o menu e diz que vai ser em forma de cascata.
        #arquivomenu.add_command(label="Novo")", command=principal) #Cria submenus.
        arquivomenu.add_separator()
        confmenu = Menu(barramenus)
        confmenu = Menu(confmenu, tearoff=0) #Tira um tracejado que vem por padrão nos menu.
        barramenus.add_cascade(label="Configurações", menu=confmenu)
        confmenu.add_command(label="Cores")#, command=self.telaEscolherCores)

        sobremenu = Menu(barramenus)
        sobremenu = Menu(sobremenu, tearoff=0) #Tira um tracejado que vem por padrão nos menu.
        barramenus.add_cascade(label="Ajuda", menu=sobremenu)
        #sobremenu.add_command(label="Código fonte", command=senha)
        #sobremenu.add_command(label="Introdução", command=comousar)
        self.primeiraTela.config(menu=barramenus)

    def telaSinal(self):
        self.sinalTela = Toplevel() #Deixa essa janela como prioridade.
        self.sinalTela.geometry("730x599+430+60")
        self.sinalTela.iconbitmap(default="icone\\logo.ico")
        self.sinalTela.title("Sinais das ONU's")
        self.sinalTela.configure(background="#d9d9d9") #"gray20" and "#2F4F4F"
        self.sinalTela.resizable(width=False, height=False)
        self.sinalTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.sinalTela.focus_force() #Força o foco nessa janela.
        self.sinalTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.sinalTela.bind('<Return>', self.teclaEnterVerificarSinal)
        self.framesTelaSinal()
        self.widgetsTelaSinal()
    
    def framesTelaSinal(self):
        esquerdaFrameSinal = Frame(self.sinalTela, borderwidth=0, relief="solid", bg='#062F4F')
        esquerdaFrameSinal.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameSinal = Frame(self.sinalTela, borderwidth=0, relief="solid", bg='#062F4F')
        direitaFrameSinal.place(relx=0.8489, rely=0, relwidth=0.151, relheight=1.005)
        linhaFrameSinal = Frame(self.sinalTela, borderwidth=1, relief="solid", background="#d9d9d9")
        linhaFrameSinal.place(relx=0.149, rely=0.056, relwidth=0.701, relheight=1)

    def widgetsTelaSinal(self):
        #*Primeiro Frame
        #Criação dos texto.
        Label(self.sinalTela, text="Verificar sinal da ONU", font="Ivy 14 bold", background="#d9d9d9").place(relx=0.3615, rely=0.03)
        Label(self.sinalTela, text="Informe o login", font="Ivy 12 bold", background="#d9d9d9").place(relx=0.4195, rely=0.14)
        #Criação das entradas dos dados.
        self.entradaPosicaoOnu = Entry(self.sinalTela, bd=3, justify=CENTER, font="Ivy 10")
        self.entradaPosicaoOnu.place(relx=0.426, rely=0.19, relwidth=0.152, relheight=0.038)
        self.entradaPosicaoOnu.focus()
        #self.entradaPosicaoOnu.bind('<Control-a>', self.displayControlA)
        #Criação dos botões.
        botaoVerificar = atk.Button3d(self.sinalTela, text="Verificar", command=self.verificarSinal)
        botaoVerificar.bind('<Enter>', lambda e: botaoVerificar.configure(cursor = "hand2"))
        botaoVerificar.place(relx=0.437, rely=0.295, relwidth=0.13, relheight=0.071)
        #Criação das saídas dos dados.
        self.saidaSinalOnu = Label(self.sinalTela, text="", font="Ivy 11 bold", anchor=N, background="#d9d9d9")
        self.saidaSinalOnu.place(relx=0.174, rely=0.43, relwidth=0.65, relheight=0.32)
        #Balão de mensagem.
        atk.tooltip(botaoVerificar, "Verifica o sinal da ONU informada acima")

    def telaRelatorios(self):
        self.relatoriosTela = Toplevel() #Deixa essa janela como prioridade.
        self.relatoriosTela.geometry("730x599+430+60")
        self.relatoriosTela.iconbitmap(default="icone\\logo.ico")
        self.relatoriosTela.title("Relatórios")
        self.relatoriosTela.configure(background="#d9d9d9") #"gray20" and "#2F4F4F"
        self.relatoriosTela.resizable(width=False, height=False)
        self.relatoriosTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.relatoriosTela.focus_force() #Força o foco nessa janela.
        self.relatoriosTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.relatoriosTela.bind('<Return>', self.teclaEnterRelatorios)
        self.nomeDiretorio = "C:\\Users\\Public\\Desktop"
        self.framesTelaRelatorios()
        self.widgetsTelaRelatorios()
        self.listaListBoxRelatorios()

    def framesTelaRelatorios(self):
        esquerdaFrameRelatorios = Frame(self.relatoriosTela, borderwidth=0, relief="solid", bg='#062F4F')
        esquerdaFrameRelatorios.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameRelatorios = Frame(self.relatoriosTela, borderwidth=0, relief="solid", bg='#062F4F')
        direitaFrameRelatorios.place(relx=0.8489, rely=0, relwidth=0.151, relheight=1.005)
        linhaFrameRelatorios = Frame(self.relatoriosTela, borderwidth=1, relief="solid", background="#d9d9d9")
        linhaFrameRelatorios.place(relx=0.149, rely=0.056, relwidth=0.701, relheight=1)

    def widgetsTelaRelatorios(self):
        #Criação de texto.
        Label(self.relatoriosTela, text="Gerar relatório", font="Ivy 14 bold", background="#d9d9d9").place(relx=0.405, rely=0.03)
        Label(self.relatoriosTela, text="Defina a pasta que deseja salvar o arquivo", font="Ivy 9 bold", background="#d9d9d9").place(relx=0.281, rely=0.135)
        Label(self.relatoriosTela, text="Escolha um modelo de relatório", font="Ivy 9 bold", background="#d9d9d9").place(relx=0.371, rely=0.31)
        Label(self.relatoriosTela, text="0%", font="Ivy 6", background="#d9d9d9").place(relx=0.235, rely=0.942)
        Label(self.relatoriosTela, text="100%", font="Ivy 6", background="#d9d9d9", foreground="green").place(relx=0.73, rely=0.942)
        #Criação das entrada dos dados.
        self.saidaDiretorio = Label(self.relatoriosTela, text="C:\\Users\\Public\\Desktop", font="Ivy 8", background="#E9C893")
        self.saidaDiretorio.place(relx=0.285, rely=0.167, relwidth=0.37)
        #Criação dos botões.
        botaoDefinirDiretorio = atk.Button3d(self.relatoriosTela, text="Definir", command=self.selecionarDiretorio)
        botaoDefinirDiretorio.bind('<Enter>', lambda e: botaoDefinirDiretorio.configure(cursor = "hand2"))
        botaoDefinirDiretorio.place(relx=0.657, rely=0.151, relwidth=0.09, relheight=0.063)
        botaoGerarPdf = atk.Button3d(self.relatoriosTela, text="Gerar PDF", command=self.verificarOpcaoRelatorio)
        botaoGerarPdf.bind('<Enter>', lambda e: botaoGerarPdf.configure(cursor = "hand2"))
        botaoGerarPdf.place(relx=0.44, rely=0.7, relwidth=0.12, relheight=0.075)
        #Balão de mensagem.
        atk.tooltip(botaoDefinirDiretorio, "Selecione o diretório que deseja salvar o arquivo")
        atk.tooltip(botaoGerarPdf, 'Gera um arquivo com nome padrão de "ONU Digistar.pdf"')
        #Criação de list box.
        self.listBoxRelatorio = Listbox(self.relatoriosTela, justify=CENTER, width=25, height=10, bg="#9099A2", font="Ivy 10 bold", bd=2, cursor = "hand2")
        self.listBoxRelatorio.place(relx=0.375, rely=0.35)
        #Barra de progresso.
        self.barraProgresso = ttk.Progressbar(self.relatoriosTela, orient=HORIZONTAL, length=380, mode='determinate')
        self.barraProgresso.place(relx=0.24, rely=0.91)

    def telaProvisionar(self):
        self.quartaTela = Toplevel() #Deixa essa janela como prioridade.
        self.quartaTela.geometry("730x599+430+60")
        self.quartaTela.iconbitmap(default="icone\\logo.ico")
        self.quartaTela.title("Provisionar ONU")
        self.quartaTela.configure(background="#d9d9d9") #"gray20" and "#2F4F4F"
        self.quartaTela.resizable(width=False, height=False)
        self.quartaTela.transient(self.primeiraTela) #Diz que essa janela vem da tela principal.
        self.quartaTela.focus_force() #Força o foco nessa janela.
        self.quartaTela.grab_set() #Impede que alguma coisa seja digitada fora dessa janela.
        self.listaPortaCto = []
        self.verificarTela = 1 #Para dividir a mesma função na tela de provisionar ONU e na tela de dados.
        self.verificarTela2 = 2
        self.vlan = ""
        self.radioButtonSelecionado = IntVar() #Variavel para receber a opção do modo da onu, bridge ou pppoe.
        self.framesTelaProvisionar()
        self.widgetsTelaProvisionarOnu()
        self.widgetsTelaProvisionarFrameDentro() #Função criada para poder limpar campos específicos.
        self.widgetsTelaProvisionarComboBox()
        self.preencherListaMarca(self.listaListBoxMarcaOnu())

    def framesTelaProvisionar(self):
        esquerdaFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=0, relief="solid", bg='#062F4F')
        esquerdaFrameProvisionarOnu.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=0, relief="solid", bg='#062F4F')
        direitaFrameProvisionarOnu.place(relx=0.8489, rely=0, relwidth=0.151, relheight=1.005)
        linhaFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=1, relief="solid", background="#d9d9d9")
        linhaFrameProvisionarOnu.place(relx=0.149, rely=0.056, relwidth=0.701, relheight=1)
        self.dentroFrameProvisionarOnu = Frame(self.quartaTela, borderwidth=1, relief="solid", background="#d9d9d9")
        self.dentroFrameProvisionarOnu.place(relx=0.149, rely=0.35, relwidth=0.701, relheight=2)

    def widgetsTelaProvisionarOnu(self):
        #Criação dos texto.
        Label(self.quartaTela, text="Provisionamento em espera", font="Ivy 14 bold", background="#d9d9d9").place(relx=0.318, rely=0.03)
        labelQuantOnu = Label(self.quartaTela, text="Quant.", font="arial 10 bold", background="#d9d9d9")
        labelQuantOnu.place(relx=0.415, rely=0.132)
        labelPortaOlt = Label(self.quartaTela, text="Porta na OLT", font="arial 9 bold", background="#d9d9d9")
        labelPortaOlt.place(relx=0.529, rely=0.134)
        labelMac = Label(self.quartaTela, text="MAC", font="arial 9 bold", background="#d9d9d9")
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
        botaoProcurarOnu.bind('<Enter>', lambda e: botaoProcurarOnu.configure(cursor = "hand2"))
        botaoProcurarOnu.place(relx=0.315, rely=0.135, relwidth=0.1, relheight=0.065)
        botaoCopiarMac = Button(self.quartaTela, text="Copiar", font="arial 7 bold", command=self.copiarMac)
        botaoCopiarMac.bind('<Enter>', lambda e: botaoCopiarMac.configure(cursor = "hand2"))
        botaoCopiarMac.place(relx=0.621, rely=0.168, relwidth=0.0528, relheight=0.0341)
        botaoLimparMac = Button(self.quartaTela, text="Limpar", font="arial 7 bold", command=self.limparTelaProcurarOnu)
        botaoLimparMac.bind('<Enter>', lambda e: botaoLimparMac.configure(cursor = "hand2"))
        botaoLimparMac.place(relx=0.677, rely=0.168, relwidth=0.0528, relheight=0.034)
        botaoProvisionar = atk.Button3d(self.quartaTela, text="Provisionar", bg="#2F4F4F", command=self.provisionarOnu)
        botaoProvisionar.bind('<Enter>', lambda e: botaoProvisionar.configure(cursor = "hand2"))
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
        Label(self.quartaTela, text="Provisionar ONU", font="Ivy 14 bold", background="#d9d9d9").place(relx=0.39, rely=0.325)
        Label(self.dentroFrameProvisionarOnu, text="Modo da ONU", font="arial 11 bold", background="#d9d9d9").place(relx=0.391, rely=0.032)
        Label(self.dentroFrameProvisionarOnu, text="Login", font="arial 12 bold", background="#d9d9d9").place(relx=0.13, rely=0.09) 
        Label(self.dentroFrameProvisionarOnu, text="Vlan", font="arial 12 bold", background="#d9d9d9").place(relx=0.46, rely=0.09)
        Label(self.dentroFrameProvisionarOnu, text="Marca", font="arial 12 bold", background="#d9d9d9").place(relx=0.76, rely=0.09)
        Label(self.dentroFrameProvisionarOnu, text="Ramal", font="arial 12 bold", background="#d9d9d9").place(relx=0.12, rely=0.19)
        Label(self.dentroFrameProvisionarOnu, text="Path", font="arial 12 bold", background="#d9d9d9").place(relx=0.47, rely=0.19)
        Label(self.dentroFrameProvisionarOnu, text="Porta da CTO", font="arial 12 bold", background="#d9d9d9").place(relx=0.73, rely=0.19)
        labelAstModoOnu = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#d9d9d9", foreground="red")
        labelAstModoOnu.place(relx=0.59, rely=0.031)
        labelAstLogin = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#d9d9d9", foreground="red")
        labelAstLogin.place(relx=0.22, rely=0.09)
        labelAstVlan = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#d9d9d9", foreground="red")
        labelAstVlan.place(relx=0.532, rely=0.09)
        labelAstPortaCto = Label(self.dentroFrameProvisionarOnu, text="*", font="arial 12 bold", background="#d9d9d9", foreground="red")
        labelAstPortaCto.place(relx=0.9344, rely=0.189)
        #Criação das entradas dos dados.
        self.entradaLoginOnu = Entry(self.dentroFrameProvisionarOnu, bd=3, justify=CENTER, font="Ivy 10")
        self.entradaLoginOnu.place(relx=0.07, rely=0.11, relwidth=0.218, relheight=0.02) 
        #Criação de listbox.
        self.nintVar = tkinter.IntVar(value=self.listaVlan)
        self.listBoxVlan = tkinter.Listbox(self.dentroFrameProvisionarOnu, justify=CENTER, width=6, height=4, listvariable=self.nintVar, cursor = "hand2")
        self.listBoxVlan.place(relx=0.461, rely=0.11)
        self.listBoxVlan.bind('<<ListboxSelect>>', self.verificarOpcaoVlan)
        self.listBoxMarcaOnu = Listbox(self.dentroFrameProvisionarOnu, justify=CENTER, width=11, height=4, cursor = "hand2")
        self.listBoxMarcaOnu.place(relx=0.72, rely=0.11, relwidth=0.18)
        #Criação de barra de rolagem.
        barraRolagemVlan = Scrollbar(self.dentroFrameProvisionarOnu, orient="vertical")
        self.listBoxVlan.configure(yscroll=barraRolagemVlan.set)
        barraRolagemVlan.place(relx=0.54, rely=0.11, relwidth=0.025,relheight=0.057)
        barraRolagemMarcaOnu = Scrollbar(self.dentroFrameProvisionarOnu, orient="vertical")
        self.listBoxMarcaOnu.configure(yscroll=barraRolagemMarcaOnu.set)
        barraRolagemMarcaOnu.place(relx=0.9, rely=0.11, relwidth=0.03,relheight=0.057)
        #Criação das saídas dos dados.
        self.saidaRamal = Label(self.dentroFrameProvisionarOnu, text="", background="#fff", anchor=CENTER)
        self.saidaRamal.place(relx=0.138, rely=0.211, relwidth=0.07, relheight=0.0165)
        self.saidaPath = Label(self.dentroFrameProvisionarOnu, text="", background="#fff", anchor=CENTER)
        self.saidaPath.place(relx=0.387, rely=0.211, relwidth=0.26, relheight=0.0165)
        self.saidaAguardandoBotao = Label(self.dentroFrameProvisionarOnu, text="", font="Ivy 10 bold", background="#d9d9d9", fg="red")
        self.saidaAguardandoBotao.place(relx=0.78, rely=0.27)
        #Criação de radio button.
        radioBridge = Radiobutton(self.dentroFrameProvisionarOnu, text="Bridge  |", value=1, variable=self.radioButtonSelecionado, background="#d9d9d9", cursor = "hand2")
        radioBridge.place(relx=0.37, rely=0.05)
        radioPppoe = Radiobutton(self.dentroFrameProvisionarOnu, text="PPPOE", value=2, variable=self.radioButtonSelecionado, background="#d9d9d9", cursor = "hand2")
        radioPppoe.place(relx=0.5, rely=0.05)
        #Criação dos botões.
        #Balão de mensagem.
        atk.tooltip(labelAstModoOnu, "Campo obrigatório")
        atk.tooltip(labelAstLogin, "Campo obrigatório")
        atk.tooltip(labelAstVlan, "Campo obrigatório")
        atk.tooltip(labelAstPortaCto, "Campo obrigatório")

    def widgetsTelaProvisionarComboBox(self):
        self.comboBoxPortaCto = ttk.Combobox(self.dentroFrameProvisionarOnu, state="readonly", values=self.listaPortaCto, justify=CENTER, cursor = "hand2")
        self.comboBoxPortaCto.set("0")
        self.comboBoxPortaCto.place(relx=0.793, rely=0.211, relwidth=0.085)

    def widgetsButtonVerificarSinal(self):
        botaoVerificarSinalOnuProvisionada = Button(self.quartaTela, text="VERIFICAR\nSINAL", font="Ivy 7", command=self.telaVerificarSinalUltimaOnu)
        botaoVerificarSinalOnuProvisionada.bind('<Enter>', lambda e: botaoVerificarSinalOnuProvisionada.configure(cursor = "hand2"))
        botaoVerificarSinalOnuProvisionada.place(relx=0.7, rely=0.895, relwidth=0.078, relheight=0.045)
        atk.tooltip(botaoVerificarSinalOnuProvisionada, "Verificar sinal da ONU que acabou de ser provisionada")
    
    def telaVerificarSinalUltimaOnu(self):
        loginOnu = self.entradaLoginOnu.get()
        self.ultimaOnuSinalTela = Toplevel()
        self.ultimaOnuSinalTela.geometry("400x250+595+230")
        self.ultimaOnuSinalTela.iconbitmap(default="icone\\logo.ico")
        self.ultimaOnuSinalTela.title("Sinal do cliente: {}".format(loginOnu))
        self.ultimaOnuSinalTela.configure(background="#d9d9d9")
        self.ultimaOnuSinalTela.resizable(width=False, height=False)
        self.ultimaOnuSinalTela.transient(self.primeiraTela)
        self.ultimaOnuSinalTela.focus_force()
        self.ultimaOnuSinalTela.grab_set()
        self.widgetstelaVerificarSinalUltimaOnu()
        self.verificarSinalUltimaOnuProv()

    def widgetstelaVerificarSinalUltimaOnu(self):
        self.saidaSinalUltimaOnu = Label(self.ultimaOnuSinalTela, text="", font="Ivy 9 bold", anchor=N, background="#d9d9d9")
        self.saidaSinalUltimaOnu.place(relx=0.05, rely=0.06, relwidth=0.9, relheight=0.7)
        atualizarUltimoSinal = atk.Button3d(self.ultimaOnuSinalTela, text="Atualizar", command=self.verificarSinalUltimaOnuProv)
        atualizarUltimoSinal.bind('<Enter>', lambda e: atualizarUltimoSinal.configure(cursor = "hand2"))
        atualizarUltimoSinal.place(relx=0.41, rely=0.8, relwidth=0.175, relheight=0.147)
        
    def telaLog(self):
        self.logTela = Toplevel()
        self.logTela.geometry("730x599+430+60")
        self.logTela.iconbitmap(default="icone\\logo.ico")
        self.logTela.title("Log da OLT")
        self.logTela.configure(background="#9099A2")
        self.logTela.resizable(width=False, height=False)
        self.logTela.transient(self.primeiraTela)
        self.logTela.focus_force()
        self.logTela.grab_set()
        self.widgetsTelaLog()
        self.infoLog()

    def widgetsTelaLog(self):
        #Saida de texto.
        self.listBoxLog = Listbox(self.logTela, justify=CENTER, font="Ivy 10",width=104, height=35, background="#d9d9d9")
        self.listBoxLog.place(relx=0, rely=0)

    def telaDeletarOnu(self):
        self.deletarOnuTela = Toplevel()
        self.deletarOnuTela.geometry("730x599+430+60")
        self.deletarOnuTela.iconbitmap(default="icone\\logo.ico")
        self.deletarOnuTela.title("Deletar ONU")
        self.deletarOnuTela.configure(background="#d9d9d9")
        self.deletarOnuTela.resizable(width=False, height=False)
        self.deletarOnuTela.transient(self.primeiraTela)
        self.deletarOnuTela.focus_force()
        self.deletarOnuTela.grab_set()
        self.deletarOnuTela.bind('<Return>', self.teclaEnterDeletarOnu)
        self.framesTelaDeletarOnu()
        self.widgetsTelaDeletarOnu()

    def framesTelaDeletarOnu(self):
        esquerdaFrameDeletarOnu = Frame(self.deletarOnuTela, borderwidth=0, relief="solid", bg='#062F4F')
        esquerdaFrameDeletarOnu.place(relx=0, rely=0, relwidth=0.15, relheight=1.005)
        direitaFrameDeletarOnu = Frame(self.deletarOnuTela, borderwidth=0, relief="solid", bg='#062F4F')
        direitaFrameDeletarOnu.place(relx=0.8489, rely=0, relwidth=0.151, relheight=1.005)
        linhaFrameDeletarOnu = Frame(self.deletarOnuTela, borderwidth=1, relief="solid", background="#d9d9d9")
        linhaFrameDeletarOnu.place(relx=0.149, rely=0.056, relwidth=0.701, relheight=1)
    
    def widgetsTelaDeletarOnu(self):
        #Criação dos texto.
        Label(self.deletarOnuTela, text="Deletar ONU", font="Ivy 15 bold", background="#d9d9d9").place(relx=0.418, rely=0.03)
        Label(self.deletarOnuTela, text="Informe o login", font="Ivy 12 bold", background="#d9d9d9").place(relx=0.42, rely=0.14)
        #Criação de entrada de dados.
        self.entradaLoginDeletarOnu = Entry(self.deletarOnuTela, bd=3, justify=CENTER, font="Ivy 10")
        self.entradaLoginDeletarOnu.place(relx=0.426, rely=0.19, relwidth=0.152, relheight=0.038)
        self.entradaLoginDeletarOnu.focus()
        #Criação de botões.
        botaoDeletarOnu = atk.Button3d(self.deletarOnuTela, text="Deletar", bg="#B82601", command=self.deletarOnu)
        botaoDeletarOnu.bind('<Enter>', lambda e: botaoDeletarOnu.configure(cursor = "hand2"))
        botaoDeletarOnu.place(relx=0.437, rely=0.295, relwidth=0.13, relheight=0.071)
        #Balão de mensagem.
        atk.tooltip(botaoDeletarOnu, "Deletar ONU do login informado acima")
        #Saída de dados.
        self.saidaOnuDeletada = Label(self.deletarOnuTela, text="", font="Ivy 10 bold", anchor=N, background="#d9d9d9")
        self.saidaOnuDeletada.place(relx=0.174, rely=0.41, relwidth=0.65, relheight=0.55)

    def telaDadosClientes(self):
        self.dadosOnuCliente = Toplevel()
        self.dadosOnuCliente.geometry("730x599+430+60")
        self.dadosOnuCliente.iconbitmap(default="icone\\logo.ico")
        self.dadosOnuCliente.title("Provisionadas")
        self.dadosOnuCliente.configure(background="#062F4F")
        self.dadosOnuCliente.resizable(width=False, height=False)
        self.dadosOnuCliente.transient(self.primeiraTela)
        self.dadosOnuCliente.focus_force()
        self.dadosOnuCliente.grab_set()
        self.dadosOnuCliente.bind('<Return>', self.teclaEnterFiltrarTodasOnu)
        self.listaPortaCto = []
        self.verificarTela = 2
        self.verificarTela2 = 1
        self.verificarDadosCarregados = 0 #Verificar se dados da onu foram carregados para serem atualizados.
        self.abasTelaDadosOnu()
        self.framesTelaDadosOnu()
        self.widgetsEntradaTelaDados()
        self.widgetsTelaDadosOnu()
        self.comboBoxRamalTelaDados["values"] =  ["Ramal", "13", "14", "15", "16", "34", "35", "36", "52"]
        self.listaMarcaTelaDados = self.listaListBoxMarcaOnu()
        listaStringVlan = ["VLAN"]
        listaStringMarca = ["Marca"]
        self.comboBoxVlanTelaDados["values"] = listaStringVlan + self.listaVlan
        self.comboBoxMarcaTelaDados["values"] = listaStringMarca + self.listaMarcaTelaDados
        self.listarTodasOnuTelaDados()
        self.widgetsAtualizardadosOnu()
        self.widgetsAtualizarDadosLabelEntrada()
        self.widgetsAtualizarDadosComboBox()

    def abasTelaDadosOnu(self):
        #Criação de abas.
        self.abas = ttk.Notebook(self.dadosOnuCliente) #Chamando a função para criar as abas.
        self.abas.place(relx=0.1499, rely=0, relwidth=0.71, relheight=1.005)
        #1º aba
        self.abaProvisionadas = Frame(self.abas, borderwidth=0, relief="solid", bg='#062F4F') #Criando a primeira aba.
        self.abas.add(self.abaProvisionadas, text="Provisionadas") #Dando um nome da primeira aba.
        #2º aba
        self.atualizarDadosOnu = Frame(self.abas, borderwidth=0, relief="solid", bg='#d9d9d9')
        self.abas.add(self.atualizarDadosOnu, text="Atualizar informações")
        self.atualizarDadosOnu.bind('<1>', lambda e: print("teste"))#self.dadosOnuCliente.bind('<Return>', self.teclaEnterCarregarDados))

    def framesTelaDadosOnu(self):
        linhaFrameAtualizarDados = Frame(self.atualizarDadosOnu, borderwidth=1, relief="solid", background="#d9d9d9")
        linhaFrameAtualizarDados.place(relx=0, rely=0.056, relwidth=1.1, relheight=1.1)
        esquerdaFrameDadosOnu = Frame(self.dadosOnuCliente, borderwidth=0, relief="solid", bg='#062F4F')#062F4F')38576b
        esquerdaFrameDadosOnu.place(relx=0, rely=0, relwidth=0.1515, relheight=1.005)
        direitaFrameDadosOnu = Frame(self.dadosOnuCliente, borderwidth=0, relief="solid", bg='#062F4F')
        direitaFrameDadosOnu.place(relx=0.8474, rely=0, relwidth=0.1525, relheight=1.005)
        linhaSeparaFiltrosFrameDadosOnu = Frame(self.abaProvisionadas, borderwidth=1, relief="solid", background="#9099A2")
        linhaSeparaFiltrosFrameDadosOnu.place(relx=0.372, rely=0, relwidth=0.002, relheight=0.0791)

    def widgetsEntradaTelaDados(self):
        self.entradaProcuraOnu = EntPlaceHold(self.abaProvisionadas, "           LOGIN")
        self.entradaProcuraOnu.place(relx=0.01, rely=0.024, relwidth=0.2)

    def widgetsTelaDadosOnu(self):
        #Criação de label.
        #Criação de entrada de dados.
        #Criação de botões.
        self.botaoProcurarOnu = atk.Button3d(self.abaProvisionadas, text="Procurar", bg="#38576b", command=self.filtrarOnu)
        self.botaoProcurarOnu.bind('<Enter>', lambda e: self.botaoProcurarOnu.configure(cursor = "hand2"))
        self.botaoProcurarOnu.place(relx=0.22, rely=0.009, relwidth=0.136, relheight=0.0645)
        #Criação de saída de textos.
        self.txtDadosOnu = Text(self.abaProvisionadas, state="disabled", width=64, height=33, bg="#d9d9d9", cursor = "arrow")
        self.txtDadosOnu.place(relx=0, rely=0.08)
        #Criação de combo box VLAN.
        self.vlanSelecionada = tkinter.StringVar()
        self.comboBoxVlanTelaDados = ttk.Combobox(self.abaProvisionadas, justify=CENTER, width=5, height=3, textvariable=self.vlanSelecionada, cursor = "hand2")
        self.comboBoxVlanTelaDados.set("VLAN")
        self.comboBoxVlanTelaDados.place(relx=0.6, rely=0.021)
        self.comboBoxVlanTelaDados.bind('<<ComboboxSelected>>', self.filtrarPorVlan)
        #Criação de combo box ramal.
        self.ramalSelecionado = tkinter.StringVar()
        self.comboBoxRamalTelaDados = ttk.Combobox(self.abaProvisionadas, justify=CENTER, width=6, height=3, textvariable=self.ramalSelecionado, cursor = "hand2")
        self.comboBoxRamalTelaDados.set("Ramal")
        self.comboBoxRamalTelaDados.place(relx=0.395, rely=0.021)
        self.comboBoxRamalTelaDados.bind('<<ComboboxSelected>>', self.filtrarPorRamal)
        #Criação de combo box marca.
        self.marcaSelecionada = tkinter.StringVar()
        self.comboBoxMarcaTelaDados = ttk.Combobox(self.abaProvisionadas, justify=CENTER, width=10, height=3, textvariable=self.marcaSelecionada, cursor = "hand2")
        self.comboBoxMarcaTelaDados.set("Marca")
        self.comboBoxMarcaTelaDados['state'] = 'readonly' #Proibi a mudança de valor escrevendo.
        self.comboBoxMarcaTelaDados.place(relx=0.78, rely=0.021, relwidth=0.185)
        self.comboBoxMarcaTelaDados.bind('<<ComboboxSelected>>', self.filtrarPorMarca)

    def widgetsAtualizardadosOnu(self):
        #Criação dos texto.
        Label(self.atualizarDadosOnu, text="Atualizar informações da ONU", font="Ivy 14 bold", background="#d9d9d9").place(relx=0.22, rely=0.03)
        Label(self.atualizarDadosOnu, text="Selecione a ONU", font="Ivy 12 bold", background="#d9d9d9").place(relx=0.365, rely=0.14)
        Label(self.atualizarDadosOnu, text="Login", font="arial 12 bold", background="#d9d9d9").place(relx=0.1, rely=0.3)
        Label(self.atualizarDadosOnu, text="VLAN", font="arial 12 bold", background="#d9d9d9").place(relx=0.45, rely=0.3)
        Label(self.atualizarDadosOnu, text="Marca", font="arial 12 bold", background="#d9d9d9").place(relx=0.785, rely=0.3)
        Label(self.atualizarDadosOnu, text="Ramal", font="arial 12 bold", background="#d9d9d9").place(relx=0.09, rely=0.52)
        Label(self.atualizarDadosOnu, text="Path", font="arial 12 bold", background="#d9d9d9").place(relx=0.455, rely=0.52)
        Label(self.atualizarDadosOnu, text="Porta da CTO", font="arial 12 bold", background="#d9d9d9").place(relx=0.735, rely=0.52)
        #Criação das entradas dos dados.
        self.entradaLoginAtualizarDados = Entry(self.atualizarDadosOnu, bd=3, justify=CENTER, font="Ivy 10")
        self.entradaLoginAtualizarDados.place(relx=0.3875, rely=0.19, relwidth=0.215, relheight=0.038)
        self.entradaLoginAtualizarDados.focus()
        self.entradaLoginDadosAtt = Entry(self.atualizarDadosOnu, bd=3, justify=CENTER, font="Ivy 10")
        self.entradaLoginDadosAtt.place(relx=0.043, rely=0.35, relwidth=0.215, relheight=0.038)
        #self.entradaMarcaDadosAtt =  Entry(self.atualizarDadosOnu, bd=3, justify=CENTER, font="Ivy 10")
        #self.entradaMarcaDadosAtt.place(relx=0.731, rely=0.35, relwidth=0.215, relheight=0.038)
        #Criação de listbox.
        self.nAttintVar = tkinter.IntVar(value=self.listaVlan)
        self.listBoxVlan = tkinter.Listbox(self.atualizarDadosOnu, justify=CENTER, width=6, height=4, listvariable=self.nAttintVar, cursor = "hand2")
        self.listBoxVlan.place(relx=0.458, rely=0.35)
        self.listBoxVlan.bind('<<ListboxSelect>>', self.verificarOpcaoVlan)
        #Criação de barra de rolagem.
        barraRolagemVlan = Scrollbar(self.atualizarDadosOnu, orient="vertical")
        self.listBoxVlan.configure(yscroll=barraRolagemVlan.set)
        barraRolagemVlan.place(relx=0.535, rely=0.35, relwidth=0.026,relheight=0.119)
        #Criação dos botões.
        botaoCarregarDados = atk.Button3d(self.atualizarDadosOnu, text="Carregar Dados", command=self.carregarDadosOnu)
        botaoCarregarDados.bind('<Enter>', lambda e: botaoCarregarDados.configure(cursor = "hand2"))
        botaoCarregarDados.place(relx=0.395, rely=0.235, relwidth=0.203, relheight=0.071)
        botaoAtualizarDados = atk.Button3d(self.atualizarDadosOnu, text="Atualizar", command=self.atualizarDadosOnuAba)
        botaoAtualizarDados.bind('<Enter>', lambda e: botaoAtualizarDados.configure(cursor = "hand2"))
        botaoAtualizarDados.place(relx=0.395, rely=0.68, relwidth=0.203, relheight=0.071)
        #Balão de mensagem.
        atk.tooltip(botaoCarregarDados, "Carregar dados da ONU")

    def widgetsAtualizarDadosLabelEntrada(self):
        #Criação das saídas dos dados.
        self.labelRamalDadosAtt =  Label(self.atualizarDadosOnu, text="", background="#fff", bd=3, justify=CENTER)
        self.labelRamalDadosAtt.place(relx=0.1, rely=0.57, relwidth=0.075, relheight=0.035)
        self.labelPathDadosAtt = Label(self.atualizarDadosOnu, text="", background="#fff", bd=3, justify=CENTER)
        self.labelPathDadosAtt.place(relx=0.365, rely=0.57, relwidth=0.26, relheight=0.035)
    
    def widgetsAtualizarDadosComboBox(self):
        #Criação de porta da cto combo box.
        self.comboBoxPortaCtoAtt = ttk.Combobox(self.atualizarDadosOnu, state="readonly", values=self.listaPortaCto, justify=CENTER, cursor = "hand2")
        self.comboBoxPortaCtoAtt.set("0")
        self.comboBoxPortaCtoAtt.place(relx=0.8, rely=0.57, relwidth=0.085)
        #Criação de marca combo box.
        self.comboBoxMarcaAtt = ttk.Combobox(self.atualizarDadosOnu, state="readonly", values=self.listaMarcaTelaDados, justify=CENTER, cursor = "hand2")
        self.comboBoxMarcaAtt.place(relx=0.75, rely=0.35, relwidth=0.185)

    def telaSobre(self):
        self.sobreTela = Toplevel()
        self.sobreTela.geometry("330x299+430+60")
        self.sobreTela.iconbitmap(default="icone\\logo.ico")
        self.sobreTela.title("Sobre")
        self.sobreTela.configure(background="#d9d9d9")
        self.sobreTela.resizable(width=False, height=False)
        #self.sobreTela.transient(self.primeiraTela)
        #self.sobreTela.focus_force()
        #self.sobreTela.grab_set()
        #self.sobreTela.bind('<Return>', self.teclaEnterDeletarOnu)
        self.framesTelaSobre()
        self.widgetsTelaSobre()
    
    def framesTelaSobre(self):
        pass

    def widgetsTelaSobre(self):
        pass

class Main(Conexao, Comandos, Interface, Relatorios, InformacoesOlt, BancoDeDados, BdFiltroOnu, FiltrarOnu, Func, VerificarTecla):
    def __init__(self):
        #Realizar função que ping para o dns da google, assim saberemos se o computador está ou não com conexão a internet.
        self.conectarOlt()
        self.loginOlt()
        self.conectarBd()
        self.returnBdListaLog()
        self.listaListBoxVlan()
        self.telaPrincipal()
        self.bdSair()

Main()