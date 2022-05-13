import psycopg2
from credenciaisBd import *

class BancoDeDados():
    def conectarBd(self):
        self.conn = psycopg2.connect(
            host = a,
            dbname = aa,
            user = aaa,
            password = aaaa,
            port = aaaaa
        )
        self.cursor = self.conn.cursor()
        print("Conectado ao BD")

    def adicionarOnuDb(self, login, porta_posicao_onu, vlan, porta_cto, ramal, splitter, 
        modo_onu, mac, marca, porta_olt, usuario, data_hora):
        #Adiciona a tabela ONU.
        self.cursor.execute("INSERT INTO onu (login, porta_posicao_onu, vlan, porta_cto,"
        " ramal, splitter, modo_onu, mac, marca, porta_olt, usuario, data_hora) VALUES" 
        "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);", (login, porta_posicao_onu, 
        vlan, porta_cto, ramal, splitter, modo_onu, mac, marca, porta_olt, usuario, data_hora))
        self.conn.commit()

    def bdPortaPosicao(self, login):
        self.cursor.execute("SELECT porta_posicao_onu FROM onu WHERE login=%s ;",(login,))
        return self.cursor.fetchall()

    def dbComandoDeletarOnu(self, login):
        self.cursor.execute("SELECT vlan, porta_posicao_onu, mac, splitter, porta_cto, marca, modo_onu FROM onu WHERE login=%s ;",(login,))
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

    def bdSair(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        print("Fechando BD")
