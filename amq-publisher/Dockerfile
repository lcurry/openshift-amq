FROM lmregistry.us.lmco.com/lmc.eo.swf.lmified/ext.hub.docker.com/library/python:latest
WORKDIR /app
COPY ./requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt && \
    mkdir /certs && \
    curl -o /certs/Combined_pem.pem http://crl.external.lmco.com/trust/pem/combined/Combined_pem.pem
COPY amq-publisher.py .
CMD [ "python3","/app/amq-publisher.py", "--server_url=activemq-server" ]