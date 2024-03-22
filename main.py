import os
import pandas as pd

from src.stuff import get_operations, merge_operacoes
from src.calculo_ir import CalculoIr
from src.relatorio import relatorio_txt
# Obtém o caminho do diretório atual do script
script_dir = os.path.dirname(os.path.abspath(__file__))

name_file = "negociacao-fevereiro-2024.xlsx";

# Checa se o arquivo movimentacao.xlsx existe
if not os.path.exists(os.path.join(script_dir, "files", name_file)):
    print("Arquivo movimentacao.xlsx não encontrado.")
    exit()

EXCEL_PATH = os.path.join(script_dir, "files", name_file)


def importar_negociacoes():
    print('Iniciando importação...')
    from src.importador_negociacao_b3 import ImportadorNegociacaoB3
    importador = ImportadorNegociacaoB3()

    df_importadas = importador.busca_trades(EXCEL_PATH)
    df = get_operations()
    df = merge_operacoes(df, df_importadas)

    calculo_ir = CalculoIr(df=df)
    result = calculo_ir.calcula()
    
    if os.path.exists(os.path.join(script_dir, "files", "result.xlsx")):
        os.remove(os.path.join(script_dir, "files", "result.xlsx"))
    result.to_excel(os.path.join(script_dir, "files", "result.xlsx"))
    print('Resultado gravado em result.xlsx')

    

importar_negociacoes()