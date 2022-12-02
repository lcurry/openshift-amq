[[_TOC_]]

# Overview

This repo provides templates for an Openshift ActiveMQ deployment along with use case examples. The purpose of this repository is to provide a production ready baseline that teams can fork and expand to their own needs.

It is recommended that an application team take ownership of the AMQ Broker artifacts and customize those artifacts as needed and store in source control to allow quick and easy create and restore of the AMQ Broker. The AMQ BRoker instance "infrastructure as code" will become just another component within the wider application source code repository for a particular app, owned and maintained by the app team. 

This repository provides:

* Base templates for the AMQ Artemis broker `/amq-broker`
* Sample applications for the consumer and the publisher sides of AMQ
* Sample pipeline with SSL certificate request automation. `.gitlab-ci.yml.template`
* Reference Scripts to generate certificates using Venafi API (the LMCO enterprise certificate authority) 

# Getting started

This section discusses the repository content and the primary configuration settings to consider changing for your particular application and usage of AMQ Broker.

## Repository contents

This repository includes several components:

* Openshift template deployment and pipeline `amq-broker`
* Sample AMQ consumer code and container `amq-consumer`
* Sample AMQ publisher code and container `amq-publisher`
* Openshift template teployment to enable RH-SSO integration `rh-sso-integration`

# AMQ Broker on Openshift template (persistent, non-clustered, SSL, local users)

For a simple development instance of AMQ broker see `amq-broker/ActiveMQArtemis_broker.yaml`

The goal for this template is to allow you to deploy a simple AMQ broker in your project by just applying a yaml template located in the `amq-broker` folder.

The deployment yaml file will instantiate an instance of AMQ Broker having the following qualities:

* persistent - Uses persistent storage.  This means if the broker goes down with unconsumed messages on queues, the messages will not be lost.  When the Broker comes back up those messages will still be available for consumption.
* non-clustered - Only single insance of AMQ Broker is available.  A single instance is adequate for most applications. Only under the highest throughput/availability requirements would you need a cluster of >1 brokers.  A single broker has the advantage of less complexity and less network traffic (chattiness) between broker instances.
* SSL - The Broker is installed with SSL enabled on the Admin console (web ui) and the AMQ protocol connector (connections from clients).
* local users - The authentication mechanism is the default locally defined users.  These users are set at install time and specified

## AMQ Broker Production Considerations

This section discusses some factors to consider when deploying AMQ Broker to Prod environments.
A good reference for information related to sizing AMQ BRoker on Openshift can be found here

https://access.redhat.com/documentation/en-us/red_hat_amq/2021.q3/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp

Factors to consider when deploying AMQ Broker include the following:

### Storage

The size and storage class of the Persistent Volume Claim (PVC) required by each broker in a deployment for persistent storage.

How much persist storage you allocate to the broker will depend on how many messages (amount) you wish to store on broker before failing to take more messages. When consumers are not keeping up with producers, at some point the broker will run out disk to write messages. So many factors impact this descision beginning with the type of application, message availability, and the expected downtime for message consumers. The rate of messages being created and number of message consumers all contribute to this decision.
In AMQ Broker 7.10, if you want to configure the following items, you must add the appropriate configuration to the main CR instance before deploying the CR for the first time.

A good reference for information related to storage :
https://access.redhat.com/documentation/en-us/red_hat_amq/2021.q3/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp#assembly-br-broker-storage-requirements-operator_broker-ocp

### Scalability  / HA

Openshift will by default perform health checks and automatically restart the broker it goes down for any reason. To provide high availability for AMQ Broker on OpenShift Container Platform, you can run multiple broker Pods in a broker cluster This can be specified within the CR yaml file.
There are tradeoffs of increased complexity and network "chattiness" when running a cluster of multiple broker instances.
Generally, the recommended starting point for production deployment is a single AMQ Broker cluster. Only after analyzing and testing your application's unique messaging requirements, will you be able to determine  whether a single broker instance is adequate, or whether you will need to scale to multiple brokers.
Should you decide to go with a deployment size of >1  (two or more active broker instances), consumsers and producers can connect to either broker to consume/produce messages for added availability. Messages are available on both brokers and get forwarded between brokers automatically as needed based on demand from consumers.
Below from CR 'size' is where the size of the broker cluster is configured:

``` yaml
spec:
  deploymentPlan:
    size: 1
    image: placeholder
    requireLogin: false
    persistenceEnabled: true
    journalType: nio
    messageMigration: true
```

See deploying clustered brokers:
https://access.redhat.com/documentation/en-us/red_hat_amq_broker/7.10/html/deploying_amq_broker_on_openshift/deploying-broker-on-ocp-using-operator_broker-ocp#proc_br-deploying-clustered-brokers_broker-ocp

### Memory / CPU

Memory and CPU (limits and requests) can be specified in the CR for a broker deployment.
Again, this is highly dependent on the maximum number of in-flight messages your broker will need
to handle, as well as size of messages. We recommend a good starting in production for a broker
with relatively high messaging requirements to start with requests of 512M-1024M memory and 1-2 cores CPU, and a limit of 1-2 GB memory, and 2-4 cores CPU.

For further info see:
https://access.redhat.com/documentation/en-us/red_hat_amq/2021.q3/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp#assembly-br-configuring-resource-limits-and-requests-operator_broker-ocp

### Security
The CR (yaml) provided to instantiate AMQ Broker will specify SSL Enabled on endpoints. 
You will need to create custom Certs for the broker.
A reference for creating  certs via venafi can be found in the '.gitlab-ci.yml.template' file provided in the repo.


# Deployment Steps 

This section discusses the order and steps for deploying an instance of AMQ Broker into your own Openshift namespace using the cluster-wide AMQ Broker operator.  

## Create certificates for AMQ Broker 

The procedure in this section shows how to configure one-way Transport Layer Security (TLS) to secure a broker-client connection. In one-way TLS, only the broker presents a certificate. This certificate is used by the client to authenticate the broker.  Although only the broker presents certificates in one-way TLS, the deployment requires you create two secrets in Openshift (steps described below) that contain the server-side broker certificates - one secret holds certs associated with connection from messaging clients AMQP(s), and another secret will hold certs associated with for client connections to the admin console (HTTPs). 

Red Hat Documentation is here for crating a self-signed cert and configuring a secret to hold the cert at the broker.  
https://access.redhat.com/documentation/en-us/red_hat_amq_broker/7.10/html-single/deploying_amq_broker_on_openshift/index#proc-br-configuring-one-way-tls_broker-ocp

You may follow the above instructions "Configuring one-way TLS" to create your own self-signed certs. Note self-signed certs should be used for Development environment only, and not recommended for production.

Note when you issue the 'oc create secret generic <secret name>' to create the secret that holds the certs in Openshift, the name of the secrets should match the 'sslSecret' specified in two places in the 'ActiveMQArtemis_broker.yaml' file. 

For a production deployment, you will likely want to use a real certificate created in Venafi.  The instructions 
for creating cert are included here, as well as reference scripts to create certs through Venafi API are included in this repo.

## Information on certificate SAN 

When requesting certificate for the AMQ Broker use the following names below as the Common Name when creating the certificate. The following applies and will be specific based on your \<broker-name\> and \<your-namespace\>.  Broker name is found in the yaml [file](/amq-broker/ActiveMQArtemis_broker.yaml) used to create the broker, and namespace is the project name you are deploying into.
> Note: To keep it simple, we will make the namespace name and broker name the same.

|                 |  Common Name | Subject Alternative Names  |
|-----------------|--------------|-----------------|
| AMQ Broker |```<broker-name>-amq-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com```|```<broker-name>-amq-0-svc, <broker-name>-amq-0-svc.<your-namespace>.svc, <broker-name>-amq-0-svc.<your-namespace>.svc.cluster.local```|
| Web Console     |```<broker-name>-wconsj-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com```|```<broker-name>-wconsj-0-svc, <broker-name>-wconsj-0-svc.<your-namespace>.svc, <broker-name>-wconsj-0-svc.<your-namespace>.svc.cluster.local```|

You will receive 2 files one for each certificate that should be named as follows:

``` Text

<broker-name>-amq-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com.pfx
<broker-name>-wconsj-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com.pfx

```

You can view the details of the each cert with the following commands:

``` Shell

keytool -list -v -keystore <broker-name>-amq-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com.pfx
keytool -list -v -keystore <broker-name>-wconsj-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com.pfx

```

You should be able to see information such as CommonName, SubjectAlternativeName, Signature algorithm, etc.

## **Running get_venafi_cert.py**

You should have Python3 installed along with the `requests` library, once you do you will need to set the following environment variables in your terminal:

``` bash
VENAFI_USER     = #Your venafi Username
VENAFI_PASSWORD = #Your venafi account password
PROJECT_NAME    = #Openshift project (Namespace) your project is deployed in
```

You will need to download the cert for venafi server and place it on file system to be used as trusted CA:

``` bash

curl -o ./amq-broker/lm_ca.pem http://crl.external.lmco.com/trust/pem/combined/Combined_pem.pem
```

Running the script `python3 script/get_venafi_cert.py` will download two files to the working folder:


``` text
amq-<PROJECT NAME>.pfx
web-<PROJECT NAME>.pfx
```

## Create keystore for broker and web console

In this step we will create broker and web console keystore from the .pfx *PKCS12* certs. The following command uses the 'keytool' command to create the keystore from the cert for broker and web console.

``` Shell

keytool -importkeystore -srckeystore  <exising cert .pfx file PKCS12 format> -srcalias <Subject name in cert> -srcstorepass <the certs key password> -srcstoretype pkcs12 -destkeystore broker.ks -destalias broker -deststoretype JKS -deststorepass <destination keystore password shuld be same as key trustStorePassword>

```

The same command format (different arguments) can be used to generate the keystore for the web console. Examples of each are given below.

> NOTE:  use same password for the new destination keystore that was used for the original key. The keystore password and the cert key password should be the same.

For example here as an example command-line for createing keystore for the broker:

``` Shell

keytool -importkeystore -srckeystore  iof-amq-0-svc-rte-iof.apps.ocp-uge1-dev.ecs.us.lmco.com.pfx -srcalias iof-amq-0-svc-rte-iof.apps.ocp-uge1-dev.ecs.us.lmco.com -srcstorepass <keystore password> -srcstoretype pkcs12 -destkeystore broker.ks -destalias broker -deststoretype JKS -deststorepass <keystore password>

```

The output keystore will go to a file broker.ks

And here as an example command-line for createing keystore for the web console:

``` Shell

keytool -importkeystore -srckeystore  iof-wconsj-0-svc-rte-iof.apps.ocp-uge1-dev.ecs.us.lmco.com.pfx -srcalias iof-wconsj-0-svc-rte-iof.apps.ocp-uge1-dev.ecs.us.lmco.com -srcstorepass <keystore password> -srcstoretype pkcs12 -destkeystore console.ks -destalias console -deststoretype JKS -deststorepass <keystore password>

```

The output keystore will go to the file **console.ks**

## Create secrets in Openshift to hold the keystores for broker and web console

In this step we will create the secrets in openshift containing the keystore files for broker and web console. This step is very important.  If 'sslEnabled: true' in your AMQ Broker CR, then failure to create properly named openshift secret(s) - prior to deployment - will result in deployment failure of the broker. 

The secrets we are including in our deployment will include both the  keystores and their respective passwords. One secret is used on the route that handles AMQP(S) messaging traffic to the broker (acceptor), and the other secret is used on the route that will handle HTTPS traffic for the admin console. Use the following commands to create both secrets:
>Be sure you run these commands from the same directory where the keystore (.ks) files exist, and to replace \<password\> with your password for the cert, and \<broker-name\> with the name you used when you created the broker.

``` shell
oc project <your namespace>

oc create secret generic <your broker-name>-amq-secret --from-file=broker.ks=.\/broker.ks --from-file=client.ts=.\/broker.ks --from-literal=keyStorePassword=<keystore password> --from-literal=trustStorePassword=<truststore password>

oc create secret generic <your broker-name>-amq-secret-wsconsj --from-file=broker.ks=.\/console.ks --from-file=client.ts=.\/console.ks --from-literal=keyStorePassword=<keystore password> --from-literal=trustStorePassword=<truststore password> --from-literal=AMQ_CONSOLE_ARGS="--ssl-key /etc/<your broker-name>-amq-secret-wsconsj-volume/broker.ks --ssl-key-password <truststore password> --ssl-trust /etc/<your broker-name>-amq-secret-wsconsj-volume/client.ts --ssl-trust-password <truststore password>"
```

> When creating a secret, OpenShift requires you to specify both a key store and a trust store. The trust store key is generically named client.ts. For one-way TLS between the broker and a client, a trust store is not actually required. However, to successfully generate the secret, you need to specify some valid store file as a value for client.ts. The preceding step provides a "dummy" value for client.ts by reusing the previously-generated broker key store file. This is sufficient to generate a secret with all of the credentials required for one-way TLS.

# Integration with RH-SSO 
This section will describe the steps required for integration with RH-SSO for Authentication.  This section assumes the previous sections have been implemented and you have a running broker with properly configured certificates. Also, you should have a separate namespace where RH-SSO is installed. 

For detailed instructions on applying CRs to integrate AMQ Broker with RH-SSO see
'rh-sso-integration/README.md'


# Local Deployments for testing

## Prereq

* Python3
* stomp.py library installed
* Openshift CLI (oc.exe)

## Sample AMQ consumer

To connect to a queue you can run the command below:

``` shell
python3 ./amq-consumer/amq-consumer.py --host="localhost" --port="61613" --queue="queue1"
```

To connect to a topic you can run the command below:

``` shell
python3 ./amq-consumer/amq-consumer.py --host="localhost" --port="61613" --queue="/topic/topic1"
```

You will see the application enter the read loop which will immediately print to the terminal any message that's received on the queue/topic that you subscribed to.

## Sample AMQ Publisher code

To connect to a queue you can run the command below:

``` shell
python3 ./amq-publisher/amq-publisher.py --host="localhost" --port="61613" --queue="queue1"
```

To connect to a topic you can run the command below:

``` shell
python3  ./amq-publisher/amq-publisher.py --host="localhost" --port="61613" --queue="/topic/topic1"
```

You will see the application send a single message to the queue/topic that you pointed it to and exit.

# Running the sample code locally with Docker

Using Docker containers will enable you to run the AMQ environment in your laptop and setup more complex simulations like multi sub/pub and fanout. Our reccomendation is that you create a dedicated docker network and connect all containers to it.

## Create a Docker Network

``` shell
docker network create amq
```

## AMQ-Server

``` shell
docker run -d --name activemq-server --network=amq -p 8161:8161 -p 61613:61613 lmregistry.us.lmco.com/lmc.eo.swf.lmified/ext.hub.docker.com/rmohr/activemq:latest
```

## Consumer

The Consumer Docker image will by default attempt to connect to a server named `activemq-server`, if you are running the server command as above you should not have any issues **as long as both containers are in the same Docker network**.

``` shell
docker run --name amq-consumer --network=amq amq-consumer
```

TODO: theres no output to standard out due to the way the threading is handled by the library. looking into how to get it working.

## Publisher

The Publisher Docker image will by default attempt to connect to a server named `activemq-server`, if you are running the server command as above you should not have any issues **as long as both containers are in the same Docker network**.

``` shell
docker run --name amq-publisher --network=amq amq-publisher
```

TODO: theres no output to standard out due to the way the threading is handled by the library. looking into how to get it working.