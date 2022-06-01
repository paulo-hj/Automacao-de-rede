import psycopg2
from credenciaisBd import *
from tkinter import messagebox

class BdFiltroOnu():
    def bdListarTodasOnu(self):
        self.cursor.execute("SELECT * FROM onu;")
        return self.cursor.fetchall()
    
    def bdVerificarQuantOnuProv(self):
        self.cursor.execute("SELECT id_onu FROM onu;")
        return self.cursor.fetchall()

    def bdVerificarQuantOnuVlan(self, vlan):
        self.cursor.execute("SELECT id_onu FROM onu WHERE vlan=%s ;",(vlan,))
        return self.cursor.fetchall()

    def bdVerificarQuantOnuRamal(self, ramal):
        self.cursor.execute("SELECT id_onu FROM onu WHERE ramal=%s ;",(ramal,))
        return self.cursor.fetchall()

    def bdVerificarQuantOnuMarca(self, marca):
        self.cursor.execute("SELECT id_onu FROM onu WHERE marca=%s ;",(marca,))
        return self.cursor.fetchall()

    def bdFiltrarLoginOnu(self, login):
        self.cursor.execute("SELECT porta_posicao_onu, vlan, porta_cto, ramal, path, modo_onu, mac, marca, usuario, data_hora FROM onu WHERE login=%s ;",(login,))
        return self.cursor.fetchall()

    def bdFiltrarVlanOnu(self, vlan):
        self.cursor.execute("SELECT login, porta_posicao_onu, porta_cto, ramal, path, modo_onu, mac, marca, usuario, data_hora FROM onu WHERE vlan=%s ;",(vlan,))
        return self.cursor.fetchall()
    
    def bdFiltrarRamalOnu(self, ramal):
        self.cursor.execute("SELECT login, porta_posicao_onu, vlan, porta_cto, path, modo_onu, mac, marca, usuario, data_hora FROM onu WHERE ramal=%s ;",(ramal,))
        return self.cursor.fetchall()
    
    def bdFiltrarMarcaOnu(self, marca):
        self.cursor.execute("SELECT login, porta_posicao_onu, vlan, porta_cto, ramal, path, modo_onu, mac, usuario, data_hora FROM onu WHERE marca=%s ;",(marca,))
        return self.cursor.fetchall()

class BancoDeDados(BdFiltroOnu):
    def conectarBd(self):
        try:
            self.conn = psycopg2.connect(
                host = a,
                dbname = aa,
                user = aaa,
                password = aaaa,
                port = aaaaa
            )
            self.cursor = self.conn.cursor()
            print("Conectado ao BD")
        except:
            #print("teste")
            messagebox.showerror(title="Erro", message="É necessário primeiro procurar a ONU.")

    def adicionarOnuDb(self, login, porta_posicao_onu, vlan, porta_cto, ramal, path, 
        modo_onu, mac, marca, porta_olt, usuario, data_hora):
        #Adiciona a tabela ONU.
        self.cursor.execute("INSERT INTO onu (login, porta_posicao_onu, vlan, porta_cto,"
        " ramal, path, modo_onu, mac, marca, porta_olt, usuario, data_hora) VALUES" 
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (login, porta_posicao_onu, 
        vlan, porta_cto, ramal, path, modo_onu, mac, marca, porta_olt, usuario, data_hora))
        self.conn.commit()

    def bdPortaPosicao(self, login):
        self.cursor.execute("SELECT porta_posicao_onu FROM onu WHERE login=%s ;",(login,))
        return self.cursor.fetchall()

    def dbComandoDeletarOnu(self, login):
        self.cursor.execute("SELECT vlan, porta_posicao_onu, mac, path, porta_cto, marca, modo_onu FROM onu WHERE login=%s ;",(login,))
        return self.cursor.fetchall()
    
    def dbDeletarOnu(self, login):
        self.cursor.execute("DELETE FROM onu WHERE login=%s ;",(login,))
        self.conn.commit()

    def bdAddPortaCto(self, portaCto, vlan):
        comando = "UPDATE porta_cto SET porta_"+portaCto+"={} WHERE id_vlan={};".format(portaCto, vlan)
        self.cursor.execute(comando)
        self.conn.commit()

    def bdExclPortaCto(self, portaCto, vlan):
        comando = "UPDATE porta_cto SET porta_"+portaCto+"=0 WHERE id_vlan={};".format(vlan)
        self.cursor.execute(comando)
        self.conn.commit()

    def bdListarPortaCto(self, vlan):
        self.cursor.execute("SELECT porta_1, porta_2, porta_3, porta_4, porta_5, porta_6, porta_7,"
        " porta_8, porta_9, porta_10, porta_11, porta_12, porta_13, porta_14, porta_15, porta_16 "
        "FROM porta_cto WHERE id_vlan=%s ;",(vlan,))
        return self.cursor.fetchall()

    def bdAddLog(self, listalog):
        comando = "UPDATE log SET listalog={} WHERE id_log=1;".format(listalog)
        self.cursor.execute(comando)
        self.conn.commit()

    def bdListaLog(self):
        self.cursor.execute("SELECT listalog FROM log WHERE id_log=%s ;",(1,))
        return self.cursor.fetchall()

    def bdCarregarDadosOnuAtt(self, login):
        self.cursor.execute("SELECT vlan, path, porta_cto, ramal, marca FROM onu WHERE login=%s ;",(login,))
        return self.cursor.fetchall()

    def dbCAttDadosOnu(self, loginAtt, vlan, path, portaCto, ramal, marca, login):
        self.cursor.execute("UPDATE onu SET login=%s, vlan=%s, path=%s, porta_cto=%s, ramal=%s, marca=%s WHERE login=%s;",(loginAtt, vlan, path, portaCto, ramal, marca, login))
        self.conn.commit()

    def bdListarLogin(self): #Excluir caso não for utilizar o auto complete.
        self.cursor.execute("SELECT login FROM onu;")
        return self.cursor.fetchall()

    def bdGerarRelatSinais(self):
        self.cursor.execute("SELECT login, porta_posicao_onu FROM onu;")
        return self.cursor.fetchall()

    def bdSair(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print("Fechando BD")
