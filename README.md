# calculadora-lucro-trade
Cálcula o lucro de trades a partir da planilha de movimentações disponibilizada pela B3 em https://www.investidor.b3.com.br/

No site https://www.investidor.b3.com.br/, acesse a aba de movimentações e filtre pelo tipo de movimentação "Compra/Venda".
Aperte no botão de download e selecione a opção "Planilha de Excel".

No código, substitua o valor da constante 'EXCEL_PATH' pelo caminho para o arquivo baixado.
Recomenda-se preencher as colunas "Quantidade" e "Valor da Operação" que não possuírem valor, caso contrário, o resultado final não será exato.

Instale a única dependência: pandas, usando o comando `pip install pandas`.
Por fim, execute o código.




# Docker

docker build -t calculadora-lucro-trade .
docker run calculadora-lucro-trade
