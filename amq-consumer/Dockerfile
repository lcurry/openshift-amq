FROM lmregistry.us.lmco.com/lmc.eo.swf.lmified/ext.hub.docker.com/library/python:latest
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt && \
    mkdir /certs && \
    curl -o /certs/Combined_pem.pem http://crl.external.lmco.com/trust/pem/combined/Combined_pem.pem
COPY amq-consumer.py /app
CMD [ "python3","/app/amq-consumer.py", "--server_url=activemq-server" ]