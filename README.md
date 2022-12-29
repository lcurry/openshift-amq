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
A good reference for information related to sizing AMQ BRoker on Openshift can be found [here](https://access.redhat.com/documentation/en-us/red_hat_amq/2021.q3/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp)

Factors to consider when deploying AMQ Broker include the following:

### Storage

The size and storage class of the Persistent Volume Claim (PVC) required by each broker in a deployment for persistent storage.

How much persist storage you allocate to the broker will depend on how many messages (amount) you wish to store on broker before failing to take more messages. When consumers are not keeping up with producers, at some point the broker will run out disk to write messages. So many factors impact this descision beginning with the type of application, message availability, and the expected downtime for message consumers. The rate of messages being created and number of message consumers all contribute to this decision.
In AMQ Broker 7.10, if you want to configure the following items, you must add the appropriate configuration to the main CR instance before deploying the CR for the first time.

A good reference for information related to storage can be found [here](https://access.redhat.com/documentation/en-us/red_hat_amq/2021.q3/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp#assembly-br-broker-storage-requirements-operator_broker-ocp)

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

See deploying clustered brokers [here](https://access.redhat.com/documentation/en-us/red_hat_amq_broker/7.10/html/deploying_amq_broker_on_openshift/deploying-broker-on-ocp-using-operator_broker-ocp#proc_br-deploying-clustered-brokers_broker-ocp)

### Memory / CPU

Memory and CPU (limits and requests) can be specified in the CR for a broker deployment.
Again, this is highly dependent on the maximum number of in-flight messages your broker will need
to handle, as well as size of messages. We recommend a good starting in production for a broker
with relatively high messaging requirements to start with requests of 512M-1024M memory and 1-2 cores CPU, and a limit of 1-2 GB memory, and 2-4 cores CPU.

For further info see the following [link](https://access.redhat.com/documentation/en-us/red_hat_amq/2021.q3/html/deploying_amq_broker_on_openshift/assembly-br-configuring-operator-based-deployments_broker-ocp#assembly-br-configuring-resource-limits-and-requests-operator_broker-ocp)

### Security
The CR (yaml) provided to instantiate AMQ Broker will specify SSL Enabled on endpoints. 
You will need to create custom Certs for the broker.
A reference for creating  certs via venafi can be found in the '.gitlab-ci.yml.template' file provided in the repo.

### Service Mesh 
Since AMQ Broker supports configuration of SSL at the broker, the project has been given a waver for deployment with Service mesh. All testing/validation of AMQ Broker has been done with Service mesh disabled.  If there is a *-smcp namespace with network policies enabled  then the routes created by the AMQ Broker Operator will not be accessable from browser.  
 
For namespaces that have a cooresponding *-smcp namespace, a workaround is to remove the service mesh member roll (smmr)  from the -smcp  project , essentially disabling the smcp. Alternatively, a proper fix would be to create a Virtualsvcs that uses the correct gateways and creates routes in the smcp namespace. Testing has not yet been done with routes hosted by Servicemesh Gateway.  For more information on Service mesh available at following links:

[Confluence : How to setup HTTPS in OCP 4 with Istio](https://docs.us.lmco.com/display/ITO/How+to+setup+HTTPS+in+OCP4+with+Istio)

[Confluence : Creating multiple Domains / Routes with Istio](https://docs.us.lmco.com/pages/viewpage.action?pageId=484319875)

[Service Entry and Gateways Istio documenation](https://istio.io/latest/docs/reference/config/networking/service-entry/)


# Deployment Steps 

This section discusses the order and steps for deploying an instance of AMQ Broker into your own Openshift namespace using the cluster-wide AMQ Broker operator.  

## Create certificates for AMQ Broker 
Detailed steps and instructions for installing certificates can be found in the AMQ Broker specific [README found here](amq-broker/README.md#pre-requisite-create-certificates-for-amq-broker).

This will provide information and requirements for creating certificates and also creating the openshift resources 
(secrets) required to hold the certificates you create. 


## Deploy the broker 

Once the Secrets have been setup with the certificates.
To deploy the broker go to the README in the amq-broker sub-folder in this repo  [here](amq-broker/README.md#deploy-the-broker)


## Validate Broker 

At this point before proceeding with further security configuration, It is a a good idea to validate the broker using a consumer/producer application.

See the README in the amq-broker sub-folder in this repo [here](amq-broker/README.md#validate-the-broker) for information 
on commands to run to validate the broker by sending and consuming messages.


## Apply Security configuration to integrate with RH-SSO 

Once the broker is running and validated, you have the option to utilize the out-of-the-box simple authentication mechanism where users/passwords/roles are defined locally to the broker in local properties file.  This default authentication is applied with initial broker setup [defined here](amq-broker/README.md#local-authentication-via-property-flat-file) and can be further customized with a 'ActiveMQArtemisSecurity'. See sample CR [here](amq-broker/amq-security.yml). 

Similar Steps can be applied to [validate broker](#validate-broker) using the simple 'artemis' command line tool by simply changing the user/password used by the command. 


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