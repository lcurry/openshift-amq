[[_TOC_]]

# AMQ Broker deployment Overview

The CR defined in 'ActiveMQArtemis_broker.yaml' defines a reasonably configured
AMQ Broker suitable for a production deployment.
The AMQ Broker acceptor and and admin console are the two primary 
incoming connectivity points for AMQ Broker from both internal (To openshift)
and external clients.
See 'acceptors' and 'console' configuration in the 'ActiveMQArtemis_broker.yaml'

## pre-requisite install secrets

The two incoming connections for AMQ Broker that must be configured are the
AMQ Broker acceptor and  admin console. 

The secret specified in the yaml file 'sslSecret' will specify where the 
certificate is configured 

You must generate this secret yourself. It is not automatically created.

For both one-way and two-way TLS, you complete the configuration by generating a secret that stores the credentials required for a successful TLS handshake between the broker and the client. This is the secret name that you must specify in the sslSecret parameter of your secured acceptor and admin console. 

The secret must contain a Base64-encoded broker key store (both one-way and two-way TLS), a Base64-encoded broker trust store (two-way TLS only), and the corresponding passwords for these files, also Base64-encoded. 

There is more information on generating these secrets in the primary README root folder of this repo.

**Important when creating the secret 
Make sure the secret name in the sslSecret parameter of your secured acceptor and admin console
match the name(s) of the secrets your create to hold the certificates.


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


## Further Testing the broker from external client application (Java)

Go to the repo holding java test client, clone repo locally, and follow the README for building and running client 

https://gitlab.us.lmco.com/force1/paas/middleware/amq-client-app


## Delete the broker 

To delete the broker that has been installed:

``` shell

oc process -f ./amq-broker/ActiveMQArtemis_broker.yaml -p BROKER_NAME=$BROKER_NAME | oc delete -f -

```

