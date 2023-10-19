# Use uma imagem base do Python
FROM python:3
# Copie o arquivo main.py para a pasta /app no contêiner
COPY main.py /app/
# Defina o diretório de trabalho
WORKDIR /app
# Instale a biblioteca Pandas
RUN pip install pandas
# Execute o arquivo main.py quando o contêiner for iniciado
CMD ["python", "main.py"]