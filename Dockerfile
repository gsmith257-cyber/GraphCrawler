FROM python:3.9.15-alpine3.16
ADD requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
WORKDIR /workspace
ADD . /app
ENTRYPOINT ["python3", "/app/graphCrawler.py"] 
