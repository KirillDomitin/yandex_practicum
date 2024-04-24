FROM python:3.11

# папка, в которой будут размещаться файлы проекта внутри контейнера
WORKDIR /opt/etl

COPY requirements.txt requirements.txt
RUN  pip install --upgrade pip --no-cache-dir \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

# как запускать ваш сервис
ENTRYPOINT ["python", "main.py"]
