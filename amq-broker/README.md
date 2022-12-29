[[_TOC_]]

# AMQ Broker deployment Overview

The CR defined in 'ActiveMQArtemis_broker.yaml' defines a reasonably configured
AMQ Broker suitable for a production deployment.
The AMQ Broker acceptor and and admin console are the two primary 
incoming connectivity points for AMQ Broker from both internal (To openshift)
and external clients.
See 'acceptors' and 'console' configuration in the 'ActiveMQArtemis_broker.yaml'

## Pre-requisite Create certificates for AMQ Broker 

The two incoming connections for AMQ Broker that must be configured are the
AMQ Broker acceptor and  admin console. 

The secret specified in the yaml file 'sslSecret' will specify where the 
certificate is configured 

You must generate this secret yourself. It is not automatically created.

For both one-way and two-way TLS, you complete the configuration by generating a secret that stores the credentials required for a successful TLS handshake between the broker and the client. This is the secret name that you must specify in the sslSecret parameter of your secured acceptor and admin console. 

The secret must contain a Base64-encoded broker key store (both one-way and two-way TLS), a Base64-encoded broker trust store (two-way TLS only), and the corresponding passwords for these files, also Base64-encoded. 

**Important when creating the secret 
Make sure the secret name in the sslSecret parameter of your secured acceptor and admin console
match the name(s) of the secrets your create to hold the certificates.

### Create certificates for AMQ Broker 

The procedure in this section shows how to configure one-way Transport Layer Security (TLS) to secure a broker-client connection. In one-way TLS, only the broker presents a certificate. This certificate is used by the client to authenticate the broker.  Although only the broker presents certificates in one-way TLS, the deployment requires you create two secrets in Openshift (steps described below) that contain the server-side broker certificates - one secret holds certs associated with connection from messaging clients AMQP(s), and another secret will hold certs associated with client connections to the admin console (HTTPs). 

Red Hat Documentation is [here](https://access.redhat.com/documentation/en-us/red_hat_amq_broker/7.10/html-single/deploying_amq_broker_on_openshift/index#proc-br-configuring-one-way-tls_broker-ocp) for crating a self-signed cert and configuring a secret to hold the cert at the broker.  

You may follow the above instructions "Configuring one-way TLS" to create your own self-signed certs. Note self-signed certs should be used for Development environment only, and not recommended for production, and may present problems in the browser related to connecting to insecure site.

Note when you issue the 'oc create secret generic <secret name>' to create the secret that holds the certs in Openshift, the name of the secrets should match the 'sslSecret' specified in two places in the 'ActiveMQArtemis_broker.yaml' file. 

For a production deployment, you will likely want to use a real certificate created in Venafi.  The instructions 
for creating cert are included here, as well as a reference python [script](../script/get_venafi_cert.py) to create certs through Venafi API are included in this repo.

### Information on certificate SAN 

When creating certificate for the AMQ Broker, use the following names as Common Name (CN) when creating the certificate. The value will be specific based on your \<broker-name\> and \<your-namespace\>.  Broker name is selected when you apply the CR yaml [file](./ActiveMQArtemis_broker.yaml) used to create the broker, and namespace is the Openshift project name you are deploying into.
> Note: To keep it simple, we will make the namespace name and broker name the same.

|                 |  Common Name | Subject Alternative Names  |
|-----------------|--------------|-----------------|
| AMQ Broker |```<broker-name>-amq-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com```|```<broker-name>-amq-0-svc, <broker-name>-amq-0-svc.<your-namespace>.svc, <broker-name>-amq-0-svc.<your-namespace>.svc.cluster.local```|
| Web Console     |```<broker-name>-wconsj-0-svc-rte-<your-namespace>.apps.ocp-uge1-dev.ecs.us.lmco.com```|```<broker-name>-wconsj-0-svc, <broker-name>-wconsj-0-svc.<your-namespace>.svc, <broker-name>-wconsj-0-svc.<your-namespace>.svc.cluster.local```|

### **Running get_venafi_cert.py** To create certificates 

You can create certificates yourself using your own procedure and following the above recommended 
values for CommonName and SubjectAlternativeName, or you can utilize scripts included in this repo.

If you choose to use the scripts, this section assumes your execution environment will need to be a Linux bash environment.
You should have Python3 installed along with the `requests` library, once you do you will need to set the following environment variables in your terminal:

``` bash
VENAFI_USER     = #Your venafi Username
VENAFI_PASSWORD = #Your venafi account password
PROJECT_NAME    = #Openshift project (Namespace) your project is deployed in
BROKER_NAME = #The Broker name used in ActiveMQArtemis CR  
CERT_PASS = #The password you wish to use password and keystore password of generated certificate
OCP_CLUSTER = # short name identifies the cluster you are targetting used to build the cert SAN e.g. ocp-uge1-dev, ocp-ugw1-dev, ocp-uge1-prd, ocp-ugw1-prd)
```

Export above variables using command line.  For example:
``` bash
export VENAFI_USER=xxx
export VENAFI_PASSWORD=xxx
export PROJECT_NAME=my-project
export BROKER_NAME=my-broker
export CERT_PASS=changeit
export OCP_CLUSTER=ocp-uge1-dev    
```

From the root directory (of this repo) create a 'certs' folder to hold certs created by the script.

``` bash
mkdir certs
```

You will need to download the cert for venafi server and place it on file system to be used as trusted CA:

``` bash

curl -o ./amq-broker/lm_ca.pem http://crl.external.lmco.com/trust/pem/combined/Combined_pem.pem
```

Run the script to generate certifcats via Venafi. Note this python script run HTTP requests 
on the Venafi API and requires elevated permissions. The normal default permissions likely
will not allow you to call the API  and you may get permission (403) return code in which 
case you will need to use a VENAFI_USER with proper permissions.

Below is an example of the command being run and the output of a successful execution (note the file names of certs maybe different depending on broker name, project name).

``` bash
$  python3 script/get_venafi_cert.py  --password=$CERT_PASS
Logging in to Venafi!
Send Authorize request to Venafi
Status code: 200
Reason: OK
Creating Certificate
Success
Downloading Certificate: amq-my-broker.pfx
Success
Creating Certificate
Success
Downloading Certificate: web-my-broker.pfx
Success

```

 This script will interact with Venafi API to download two files to the 'certs' folder:


``` text
amq-${BROKER_NAME}.pfx
web-${BROKER_NAME}.pfx
```

To view and verify the certs you can use the 'keytool -list' command:

``` bash

keytool -list -v -keystore ./certs/amq-${BROKER_NAME}.pfx -storepass $CERT_PASS -storetype PKCS12
```
For example:
``` bash

keytool -list -v -keystore ./certs/web-${BROKER_NAME}.pfx -storepass $CERT_PASS -storetype PKCS12
```

Make note of the SubjectAlternativeName as this will need to match the value of the route HOST/PORT
once broker is deployed. 

Generate keystore for broker and console  :

``` bash
keytool -importkeystore -srckeystore ./certs/amq-${BROKER_NAME}.pfx -srcstorepass $CERT_PASS -srcstoretype pkcs12 -destkeystore ./certs/broker.ks -deststoretype JKS -deststorepass $CERT_PASS  
  
keytool -importkeystore -srckeystore ./certs/web-${BROKER_NAME}.pfx -srcstorepass $CERT_PASS -srcstoretype pkcs12 -destkeystore ./certs/console.ks -deststoretype JKS -deststorepass $CERT_PASS

```
You should get a message that the import command completed successfully. Note there may be a warning 
about proprietary format of the generated keystore file (JKS) rather than the industry standard PKCS12.
The warning is ok to ignore. 
If above execute successfully, you will have the AMQ Broker's certificate in the './certs/broker.ks' and the AMQ Broker console certificate in the './certs/console.ks'.

Create the secrets to hold the broker and console certs. Note when creating the secret, OpenShift requires you to specify both a key store and a trust store. The trust store key is generically named client.ts. For one-way TLS between the broker and a client, a trust store is not actually required. However, to successfully generate the secret, you need to specify some valid store file as a value for client.ts. The preceding step provides a "dummy" value for client.ts by reusing the previously-generated server-side key store file. This is sufficient to generate a secret with all of the credentials required for one-way TLS.

``` bash

oc create secret generic ${BROKER_NAME}-secret --from-file=broker.ks=./certs/broker.ks --from-file=client.ts=./certs/broker.ks  --from-literal=keyStorePassword=$CERT_PASS --from-literal=trustStorePassword=$CERT_PASS

oc create secret generic ${BROKER_NAME}-wsconsj --from-file=broker.ks=./certs/console.ks --from-file=client.ts=./certs/console.ks --from-literal=keyStorePassword=$CERT_PASS --from-literal=trustStorePassword=$CERT_PASS --from-literal=AMQ_CONSOLE_ARGS="--ssl-key /etc/${BROKER_NAME}-wsconsj-volume/broker.ks --ssl-key-password $CERT_PASS --ssl-trust /etc/${BROKER_NAME}-wsconsj-volume/client.ts --ssl-trust-password $CERT_PASS"
 

```

If above execute successfully, you will have the AMQ Broker's certificate stored in Openshift secret '$APP_NAME-secret'
and the AMQ Broker console certificate (plus required AMQ_CONSOLE_ARGS) stored in the Openshift secret '$APP_NAME-wsconsj'.
To check the values of these secrets:

``` bash
oc get secret/${BROKER_NAME}-secret -o yaml
oc get secret/${BROKER_NAME}-wsconsj -o yaml
```

Note: the values shown for above will be base64 encoded. To verify the decrypted values you can view these secrets from
the Openshift console.

## Deploy the broker      

The goal for this template is to allow you to deploy a simple AMQ broker in your project by just applying the yaml templates located in the `amq-broker` folder. You should have the oc tool installed or execute a container image that already has it.

BROKER_NAME is the name you want your broker to have
For example, if you wish to deploy a broker names 'my-broker' you can run the following:

``` shell
export BROKER_NAME=my-broker
oc process -f ./amq-broker/ActiveMQArtemis_broker.yaml -p BROKER_NAME=$BROKER_NAME | oc apply -f -

```

To then check the status of the broker:

``` shell
oc describe ActiveMQArtemis/$BROKER_NAME
```

And to see the logs for a broker pod

``` shell
oc logs -f $BROKER_NAME-ss-0
```

## Accessing the broker via a route 
To access the broker you can go the the Openshift console -> Networking -> Routes 
The URL for the route named 'my-broker-wconsj-0-svc-rte' will take you to the admin console.
The URL for the route named 'my-broker-amq-0-svc-rte' can be used by a consumer/producer app
to connect to the messaging broker via AMQP or one of the other supported protocols specified in the 
acceptor in the [ActiveMQArtemis CR](./ActiveMQArtemis_broker.yaml). 

## Validate the Broker 

You can use the 'artemis' command-line tool that ships with AMQ Broker to test the broker deployment. Further information on producing and consuming test messages using the command-line tool for AMQ can be found [here](https://access.redhat.com/documentation/en-us/red_hat_amq/2020.q4/html-single/getting_started_with_amq_broker/index#producing-consuming-test-messages-getting-started) The tool comes with the full AMQ installation and can be
installed and run from your local desktop environment. 

Pre-Requisite : OpenJDK 11 or higher.  If not installed you can download the media from [here](https://developers.redhat.com/products/openjdk/download) (requires authentication with Red Hat portal)

Install AMQ Broker : download the media [here](https://archive.apache.org/dist/activemq/activemq-artemis/2.27.1/apache-artemis-2.27.1-bin.zip) 


The validation steps (run on desktop outside cluster) require username/password authentication (by specifying the --user and --password parameters to the 'artemis' tool) below. See the next section for [more information](#amq-broker-authentication) on where (secret) the user/password for communication with the broker is found by default. 

Also you need to have the broker (trusted CA) certificate downloaded to point command to the downloaded trustStorePath, along with correct trustStorePassword, and AMQ Broker password.  

You can verify you have correct cert by viewing the output of the following command 

Confirm the SAN match the fully qualified hostname of the route/URL you are trying to connect to.
Note the certicate can be downloaded from the Openshift secret associated with the broker. The secret named ${BROKER_NAME}-secret, file Save file data named client.ts.  Verify the certificate is accurate as follows:

```
keytool -list -v -keystore client.ts -storepass ${CERT_PASS}
```

Get the route URL for the ${BROKER_NAME}-amq-0-svc-rte :

```
oc get route
export ROUTE_URL="value of route url"
export CERT_LOCATION="C:/Users/n3682e/software/apache-artemis-2.27.1/bin/client.ts"
export CERT_PASS="password used to encrypt the truststore"
export AMQ_CLUSTER_USER="see value for this variable found in secret ${BROKER_NAME}-credentials-secret"
export AMQ_CLUSTER_PASSWORD="see value for this variable in secret ${BROKER_NAME}-credentials-secret"

```


Send 10 messages to broker on queue "test" using CORE protocol:

```
.\artemis producer --url "tcp://${ROUTE_URL}:443?verifyHost=false&sslEnabled=true&trustStorePath={CERT_LOCATION}&trustStorePassword=${CERT_PASS}" --user ${AMQ_CLUSTER_USER} --password AMQ_CLUSTER_PASSWORD --text-size 100 --message-count 10 --destination queue://test


```

or using AMQP protocol (instead of CORE):

```
.\artemis producer --url "amqps://${ROUTE_URL}:443?transport.verifyHost=false&transport.trustStoreLocation=${CERT_LOCATION}&transport.trustStorePassword=${CERT_PASS}" --user ${AMQ_CLUSTER_USER} --password AMQ_CLUSTER_PASSWORD --text-size 100 --message-count 10 --destination queue://amqp-test --protocol amqp
```

Receive all 10 messages:

```
.\artemis consumer --url "tcp://${ROUTE_URL}:443?verifyHost=false&sslEnabled=true&trustStorePath=${CERT_LOCATION}&trustStorePassword=${CERT_PASS}" --user ${AMQ_CLUSTER_USER} --password AMQ_CLUSTER_PASSWORD --message-count 10 --destination queue://test

```

or through AMQP protocol:

```
.\artemis consumer --url "amqps://${ROUTE_URL}:443?transport.verifyHost=false&transport.trustStoreLocation=${CERT_LOCATION}&transport.trustStorePassword=${CERT_PASS}" --user ${AMQ_CLUSTER_USER} --password AMQ_CLUSTER_PASSWORD --message-count 10 --destination queue://amqp-test --protocol amqp
```

## AMQ Broker Authentication 

Openshift security Authentication is based on JAAS.  
By default, AMQ Broker access is controlled by a very basic JAAS Login module (propertiesLoginModule) 
in a very simple manner. By defining 'adminUser' and 'adminPassword'.  In the sample [ActiveMQArtemis CR](./ActiveMQArtemis_broker.yaml) 

the values are not specified, so random values are generated automatically by the operator and stored in a secrets named ${BOKER_NAME}-credentials-secret.  The value in AMQ_USER and AMQ_PASSWORD can be used to login to the admin console. Also in the  ${BOKER_NAME}-credentials-secret
there will be auto-created AMQ_CLUSTER_USER and AMQ_CLUSTER_PASSWORD that can be used by a consumer/producer app 
to access the broker messaging route.

### Local Authentication via Property (flat) file

If you wish to have more control over the users defined for the broker, one way to do so is to customize the JAAS propertiesLoginModule via a CR that can be applied to the namespace.  
This very simple mechanism for specifying users/passwords locally with the broker, and is explained further [here](https://access.redhat.com/documentation/en-us/red_hat_amq_broker/7.10/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp#proc-br-configuring-security-operator_broker-ocp)

There is a sample ActiveMQArtemisSecurity CR file included [here](./amq-security.yml) for specifying this simple file-based form of Authentication should your application choose to take this approach. 

### Authentication via RH-SSO 

For authentication that does not rely on locally stored user/passwords and instead uses a (external) third party Identity management application as the source of truth (RH-SSO) you can follow the setup explained [here](../rh-sso-integration/README.md) 

## Further Testing the broker from external client application (Java)

Go to the [repo](https://gitlab.us.lmco.com/force1/paas/middleware/amq-client-app) holding java test client, clone repo locally, and follow the README for building and running client 

## Delete the broker 

To delete the broker that has been installed:

``` shell

oc process -f ./amq-broker/ActiveMQArtemis_broker.yaml -p BROKER_NAME=$BROKER_NAME | oc delete -f -

```
Also, the PVC does not get deleted with above commands so its a good idea to delete the persistent 
volume PVC if you do not wish any of the broker's file system to persist.

``` shell
oc get pvc 
oc delete pvc/${BROKER_NAME}-${BROKER_NAME}-ss-0
```


