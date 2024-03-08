# Usa a imagem oficial do Python como base
FROM python:3.9

# Define o diretório de trabalho no contêiner
WORKDIR /app

# Copia o arquivo requirements.txt para o contêiner
COPY requirements.txt .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Adiciona o código do aplicativo ao contêiner
COPY . /app

# Comando para executar quando o contêiner for iniciado
CMD ["python", "main.py"]