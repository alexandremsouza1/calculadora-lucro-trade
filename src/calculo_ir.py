import datetime
import calendar
import pandas as pd
from dateutil.relativedelta import relativedelta

from src.tipo_ticker import TipoTicker
from src.stuff import tipo_ticker, vendas_no_mes


class CalculoIr():
    df: pd.DataFrame
    vendas: dict = dict()
    prejuizo_acumulado: dict = {}
    datas: list = []
    mes_do_relatorio : str

    def __init__(self, df):
        self.df = df

    def calcula(self):
        print('Iniciando cálculo...')
        
        movimentacao_group = self.df.groupby('ticker')

        for ticker, item_movimentacao_group in movimentacao_group:
            compra = self._retorna_item_grupo_por_operacao(item_movimentacao_group, 'Compra')
            venda = self._retorna_item_grupo_por_operacao(item_movimentacao_group, 'Venda')
            
            if compra is None or venda is None:
                print(f"Erro: Não foi encontrada uma compra ou uma venda para o ticker {ticker}")
                continue
            
            compra_preco = compra['valor']
            compra_data = compra['data']
            lucro = round(venda['valor'] - compra_preco, 2)
            is_day_trade = venda['data'] == compra_data

            if is_day_trade:
                print(f"Day trade de {venda['qtd']} ações de {ticker}: Lucro/Prejuízo: {lucro} : Calculo {venda['valor']} - {compra_preco}")
            else:  # Swing trade
                print(f"Swing trade de {venda['qtd']} ações de {ticker}: Lucro/Prejuízo: {lucro} : Calculo {venda['valor']} - {compra_preco}")

        print('Cálculo concluído.')
        return self.df
    
    def _retorna_item_grupo_por_operacao(self, grupo, operacao):
        for _, data in grupo.iterrows():
            if data['operacao'] == operacao:
                return data

    def calcula_prejuizo_acumulado(self, data, tipo):
        prejuizo_acumulado = self.calcula_prejuizo_por_tipo(data, tipo)

        if self.__tem_prejuizo_no_mes_anterior(tipo, data):
            prejuizo_acumulado = prejuizo_acumulado + self.__prejuizo_no_mes_anterior(tipo, data)

        return prejuizo_acumulado

    def calcula_ir_a_pagar_no_mes(self, data):
        ir_a_pagar = 0.0
        for tipo in TipoTicker:
            prejuizo_acumulado = self.calcula_prejuizo_acumulado(data, tipo)
            ir_a_pagar += calcula_ir_a_pagar(prejuizo_acumulado, tipo,
                                             self.total_vendido_no_mes_por_tipo(data)[TipoTicker.ACAO_OU_ETF])
        return ir_a_pagar

    def calcula_dedo_duro_no_mes(self, data):
        porcentagem_dedo_duro = 0.005 / 100.0
        return sum(operacao_de_venda['preco_medio_venda'] * operacao_de_venda['qtd_vendida']
                   for operacao_de_venda in vendas_no_mes(self.df, data.year, data.month)) * porcentagem_dedo_duro

    def calcula_prejuizo_por_tipo(self, data, tipo):
        return sum([venda['resultado_apurado'] for venda in self.vendas[self.__get_date_key__(data)][tipo]])

    def __tem_prejuizo_no_mes_anterior(self, tipo, data):
        if self.__prejuizo_no_mes_anterior(tipo, data) < 0:
            return True
        return False

    def __prejuizo_no_mes_anterior(self, tipo, data):
        mes_anterior = self.__get_date_key__(data + relativedelta(months=-1))
        if mes_anterior in self.prejuizo_acumulado:
            return self.prejuizo_acumulado[mes_anterior][tipo]
        return 0.0

    def __get_date_key__(self, data):
        return str(data.month) + '/' + str(data.year)

    def __seta_prejuizo_acumulado(self, data, tipo, prejuizo):
        if not self.__get_date_key__(data) in self.prejuizo_acumulado:
            self.prejuizo_acumulado[self.__get_date_key__(data)] = {}

        self.prejuizo_acumulado[self.__get_date_key__(data)][tipo] = prejuizo

    def __seta_vendas_no_mes(self, data, vendas_no_mes):
        self.vendas[self.__get_date_key__(data)] = {}

        for tipo in TipoTicker:
            self.vendas[self.__get_date_key__(data)][tipo] = []

        for venda in vendas_no_mes:
            ticker = venda['ticker']
            self.vendas[self.__get_date_key__(data)][tipo_ticker(ticker)].append(venda)

    def total_vendido_no_mes_por_tipo(self, data):
        total_vendido_no_mes = {}

        for tipo in self.vendas[self.__get_date_key__(data)]:
            total_vendido_no_mes[tipo] = sum([venda['qtd_vendida'] * venda['preco_medio_venda']
                                        for venda in self.vendas[self.__get_date_key__(data)][tipo]])
        return total_vendido_no_mes

    def vendas_no_mes_por_tipo(self, data):
        return self.vendas[self.__get_date_key__(data)]

    def possui_vendas_no_mes(self, data):
        for tipo in TipoTicker:
            if len(self.vendas[self.__get_date_key__(data)][tipo]):
                return True

        return False


def calcula_ir_a_pagar(lucro, tipo, vendas_acoes_no_mes=None):
    if lucro > 0:
        if tipo == TipoTicker.ACAO_OU_ETF:
            if vendas_acoes_no_mes > 20000.0:
                return lucro * 0.15
            else:
                return 0.0
        if tipo == TipoTicker.BDR \
                or tipo == TipoTicker.FUTURO \
                or tipo == TipoTicker.OPCAO:
            return lucro * 0.15
        if tipo == TipoTicker.FII or tipo == TipoTicker.FIP:
            return lucro * 0.2
        if tipo == TipoTicker.FIPIE:
            return 0.0
    return 0.0


