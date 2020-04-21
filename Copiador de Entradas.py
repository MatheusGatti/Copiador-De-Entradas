from iqoptionapi.stable_api import IQ_Option
import time
import logging
import os
import datetime
import getpass

class Logs:
    def __init__(self):
        super().__init__()
        self.criarPasta()
        self.ativarLog()

    def criarPasta(self):
        if not os.path.exists("Logs/"):
            os.mkdir("Logs")

    def ativarLog(self):
        arquivo = "Logs/{}.log".format(datetime.datetime.now().strftime("%d-%m-%Y"))
        level = logging.ERROR
        formato = "%(asctime)s %(levelname)s: %(message)s"
        data = "%d-%m-%Y %H:%M:%S"
        logging.basicConfig(filename=arquivo, level=level, format=formato, datefmt=data)

class IQOption:
    def __init__(self, email, senha):
        super().__init__()
        self.email = email
        self.senha = senha
        self.api = IQ_Option(self.email, self.senha)

    def definirConfiguracoes(self, ativo, timeframe, posicao):
        self.ativo = ativo
        self.timeframe = int(timeframe)
        self.posicao = int(posicao)

    def efetuarLogin(self):
        self.conectado, erro = self.api.connect()
        if self.conectado == False:
            logging.error("Erro ao tentar entrar na conta IQ Option -> {}".format(str(erro)))
            return False
        else:
            logging.info("Sucesso ao entrar na conta IQ Option")
            return True
    
    def checarAtivo(self, ativo):
        ativos = self.api.get_all_open_time()
        if ativos["digital"][ativo]["open"]:
            logging.info("Ativo encontrado")
            return True
        else:
            logging.error("O ativo {} nao foi encontrado".format(str(ativo)))
            return False
    
    def contaReal(self):
        self.api.change_balance("REAL")
    
    def contaDemo(self):
        self.api.change_balance("PRACTICE")
    
    def pegarSaldo(self):
        return self.api.get_balance()
    
    def pegarMoeda(self):
        return self.api.get_currency()
    
    def setEntrada(self, entrada):
        try:
            entrada = float(entrada)
        except:
            logging.error("Nao foi possivel definir o preco de entrada")
            return False
        if isinstance(entrada, float):
            self.entrada = entrada
            return True
        else:
            logging.error("Nao foi possivel definir o preco de entrada")
            return False

    def copiarEntradas(self):
        tempo = "PT{}M".format(str(self.timeframe))
        self.api.subscribe_live_deal("live-deal-digital-option", self.ativo, tempo, 10)
        entradas = self.api.get_live_deal("live-deal-digital-option", self.ativo, tempo)
        while True:
            time.sleep(3)
            entradas = self.api.get_live_deal("live-deal-digital-option", self.ativo, tempo)
            if len(entradas) >= 1:
                usuario = self.api.pop_live_deal("live-deal-digital-option", self.ativo, tempo)
                posicao = self.api.request_leaderboard_userinfo_deals_client(usuario["user_id"], usuario["country_id"])
                nome = str(usuario["name"])
                posicao = posicao["result"]["entries_by_country"]["0"]["position"]
                acao = usuario["instrument_dir"]
                if posicao <= int(self.posicao):
                    print("Abriu ordem: {} ({} mundial) -> {}".format(nome, str(posicao), acao.upper()))
                    _, ordem_id = self.api.buy_digital_spot(self.ativo, self.entrada, acao, self.timeframe)
                    if ordem_id != "error":
                        while True:
                            verificar_ordem, ganhou = self.api.check_win_digital_v2(ordem_id)
                            if verificar_ordem == True:
                                break
                        if ganhou < 0:
                            logging.info("---> Voce perdeu {}{}".format(
                                str(self.pegarMoeda()),
                                str(round(abs(ganhou), 2))
                            ))
                            print("---> Você perdeu {}{}".format(
                                str(self.pegarMoeda()),
                                str(round(abs(ganhou), 2))
                            ))
                        else:
                            logging.info("---> Voce ganhou {}{}".format(
                                str(self.pegarMoeda()),
                                str(round(abs(ganhou), 2))
                            ))
                            print("---> Você ganhou {}{}".format(
                                str(self.pegarMoeda()),
                                str(round(abs(ganhou), 2))
                            ))
                    else:
                        logging.error("Nao foi possivel abrir uma ordem")
                        print("---> Não foi possivel abrir uma ordem")
                else:
                    logging.info("Deixou passar: {} ({} mundial) -> {}".format(nome, str(posicao), acao.upper()))
                    print("Deixou passar: {} ({} mundial) -> {}".format(nome, str(posicao), acao.upper()))

class Configuracoes:
    def __init__(self):
        super().__init__()
    
    def setAtivo(self, ativo):
        if len(ativo) <= 0:
            logging.error("Ativo nao reconhecido")
            return False
        else:
            logging.info("Ativo definido como {}".format(str(ativo)))
            self.ativo = ativo
            return True
    
    def getAtivo(self):
        return self.ativo
    
    def setTimeframe(self, timeframe):
        try:
            timeframe = int(timeframe)
        except:
            logging.error("Timeframe nao reconhecido")
            return False
        if isinstance(timeframe, int):
            if int(timeframe) == 5 or int(timeframe) == 1:
                logging.info("Timeframe definido para {} minutos".format(str(timeframe)))
                self.timeframe = timeframe
                return True
            else:
                logging.error("O timeframe pode ser apenas de 1 ou 5 minutos")
                return False
        else:
            logging.error("Timeframe nao reconhecido")
            return False

    def getTimeframe(self):
        return self.timeframe
    
    def setPosicao(self, posicao):
        try:
            posicao = int(posicao)
        except:
            logging.error("Posicao nao reconhecido")
            return False
        if isinstance(posicao, int):
            self.posicao = posicao
            logging.info("Posicao definida para {}".format(str(posicao)))
            return True
        else:
            logging.error("Posicao nao reconhecido")
            return False
    
    def getPosicao(self):
        return self.posicao

def main():
    logs = Logs()
    logging.info("Robo iniciado com sucesso")
    print("Seja bem vindo ao copiador de entradas IQ Option, você está utilizando a versão 1.0.\n")
    print("Para verificar atualizações vá até a página principal do robô:")
    print("----> https://github.com/MatheusGatti/Copiador-De-Entradas\n\n")
    email = input("----> Digite seu e-mail da IQ Option: ")
    print("\nPor segurança iremos esconder sua senha\n")
    senha = getpass.getpass("----> Digite sua senha IQ Option: ")
    IQ = IQOption(email, senha)
    login = IQ.efetuarLogin()
    if login == False:
        print("\n----> Ocorreu algum erro ao entrar na sua conta IQ Option, verifique se digitou os dados corretamente ou se possui a autenticação de 2 (dois) fatores ativada")
        input("\nAperte qualquer tecla para sair..")
        exit()
    else:
        print("\n----> Parabéns, você entrou na IQ Option")
    print("\nAgora, configure de acordo com seu gosto..")
    configuracao = Configuracoes()
    ativo = input("\n----> Escolha apenas um ativo digital (exemplo = EURUSD): ")
    while IQ.checarAtivo(ativo) == False:
        print("\nAtivo não encontrado, escolha outro")
        ativo = input("\n----> Escolha apenas um ativo digital (exemplo = EURUSD): ")
    configuracao.setAtivo(ativo)
    timeframe = input("\n----> Escolha um timeframe (1 ou 5 minutos): ")
    while configuracao.setTimeframe(timeframe) == False:
        print("\nVerifique se digitou apenas números")
        print("Obs: só estamos trabalhando com 1 ou 5 minutos")
        timeframe = input("\n----> Escolha um timeframe (1 ou 5 minutos): ")
    posicao = input("\n----> Escolha até que posição mundialmente você aceitará receber ordem (exemplo = 100): ")
    while configuracao.setPosicao(posicao) == False:
        print("\nVerifique se digitou apenas números")
        posicao = input("\n----> Escolha até que posição mundialmente você aceitará receber ordem (exemplo = 100): ")
    IQ.definirConfiguracoes(configuracao.getAtivo(), configuracao.getTimeframe(), configuracao.getPosicao())
    tipoConta = input("\n----> Você deseja operar na conta real ou demo? ")
    while True:
        if tipoConta.upper() == "REAL":
            IQ.contaReal()
            break
        elif tipoConta.upper() == "DEMO":
            IQ.contaDemo()
            break
        else:
            print("\nVocê tem apenas 2 opções, escolha uma -> REAL ou DEMO")
            tipoConta = input("\n----> Você deseja operar na conta real ou demo? ")
    print("\nVocê tem {}{} em sua conta".format(
        str(IQ.pegarMoeda()),
        str(IQ.pegarSaldo())
    ))
    entrada = input("\n----> Escolha o valor da entrada (caso deseje utilizar centavos em vez da vírgula (,) utilize ponto (.)): ")
    while IQ.setEntrada(entrada) == False:
        print("\nVerifique se digitou apenas números")
        print("Em vez de utilizar vírgula (,) utilize pontos (.)")
        print("Exemplo: 10.30 = 10 reais e 30 centavos")
        print("Exemplo: 1024.15 = 1024 reais e 15 centavos")
        entrada = input("\n----> Escolha o valor da entrada (caso deseje utilizar centavos em vez da vírgula (,) utilize ponto (.)): ")
    input("\n----> Aperte qualquer tecla para iniciar\n")
    IQ.copiarEntradas()

if __name__ == "__main__":
    main()