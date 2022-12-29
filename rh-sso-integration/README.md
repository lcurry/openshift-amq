[[_TOC_]]

# AMQ Broker Integration with RH-SSO
This section will describe the steps required for integration with RH-SSO for Authentication.  This section assumes the previous sections have been implemented and you have a running broker with properly configured certificates. Also, you should have working instance of RH-SSO installed and available, preferrably in a seperate namespace where you have project admin access and network reachable from the AMQ Broker namespace. 

For further information in applying RH-SSO resources such as realm, client, and users to a RH-SSO instance
see following [Red Hat documentation](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#realm-cr)

The goal for these template is to allow you to deploy the resources needed to an existing RH-SSO instance and AMQ Broker instance, to create the needed constructs to integrate the AMQ Broker with RH-SSO to perform Authentication .

You should have the oc tool installed or execute a container image that already has it.


## Creating a realm custom resource 

For further information on creating a realm CR instance see the [following](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#realm-cr)

To appply the CR to create a realm in an existing RH-SSO instance, run the following command.  

If you used the non-default value for RH_SSO_NAME on deployment of RH-SSO 
To designate the RH-SSO instance on which to apply the realm, you will pass in the parameter RH_SSO_NAME.  

To get list of Keycloak instances
``` shell
oc get keycloak -n <RH-SSO namespace>
```

Check the value of "Name:" 
``` shell
oc describe keycloak <CR-name> -n <RH-SSO namespace>
```

The value for "Name:" is the <CR-name> and should be used when you deploy
the realm.   If you used 'rh-sso' as the CR-name this is the default and you do not need to specify
RH_SSO_NAME.  

You will also set parameter BROKER_NAME as the value of the name used to deploy the AMQ Broker. 
Revisit the deployment steps of [AMQ Broker here](../amq-broker/README.md).  and determine what you used for BROKER_NAME by 
inspecting the CR details 

Check the value of "Name:" 
``` shell
oc get ActiveMQArtemis -n <AMQ Broker namespace> 
oc describe ActiveMQArtemis <CR-name> -n <AMQ Broker namespace>
```

The BROKER_NAME parameter is used to specify the name of the realm. The realm name needs to be unique to RH-SSO. 
See the realm [template](./rhsso-realm.yaml) for details. 

To apply the CR in the realm template run the following:

``` shell
export RH_SSO_NAME=rh-sso
export BROKER_NAME=my-broker
oc process -f  .\rh-sso-integration\rhsso-realm.yaml  -p RH_SSO_NAME=$RH_SSO_NAME -p BROKER_NAME=$BROKER_NAME | oc apply -f - -n <RH-SSO namespace>

```

To see the realm resource properly provisioned 

``` shell
oc get keycloakrealm -n <RH-SSO namespace>
oc describe keycloakrealm ${BROKER_NAME}-realm  -n <RH-SSO namespace>


```

## Creating a client custom resource 


For further information on creating a client CR instance see:

https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#client-cr

You can use the Operator to create clients in Red Hat Single Sign-On as defined by a custom resource. 
The following command can be used to deploy the clients. One RH-SSO Client is used for broker, and one 
is used for AMQ Console. Only pass RH_SSO_NAME parameter if using non-default name. 

``` shell
oc process -f  .\rh-sso-integration\rhsso-client-broker.yaml  -p RH_SSO_NAME=$RH_SSO_NAME -p BROKER_NAME=$BROKER_NAME | oc apply -f - -n <RH-SSO namespace>

oc process -f  .\rh-sso-integration\rhsso-client-console.yaml -p RH_SSO_NAME=$RH_SSO_NAME -p BROKER_NAME=$BROKER_NAME | oc apply -f - -n <RH-SSO namespace>


```

To see the resource properly provisioned 

``` shell
oc get keycloakclient -n <RH-SSO namespace>
oc describe keycloakclient amq-broker -n <RH-SSO namespace>

oc describe keycloakclient amq-console -n <RH-SSO namespace>

```

After a client is created, the Operator creates a Secret containing the Client ID and the client’s secret
using e.g. the following naming pattern: 'keycloak-client-secret-artemis-broker'.

You can also login to RH-SSO as 'admin' and go to the clientId just created to verify the client is created properly in RH-SSO.


## Creating a user custom resource

For further information on creating a user CR instance see Red Hat documentation [here](https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#user-cr)

``` shell
oc process -f .\rh-sso-integration\rhsso-users.yaml -p RH_SSO_NAME=$RH_SSO_NAME -p BROKER_NAME=$BROKER_NAME | oc apply -f - -n <RH-SSO namespace>
```
To see the resource properly provisioned 

``` shell
oc get keycloakuser -n <RH-SSO namespace>
oc describe keycloakuser admin -n <RH-SSO namespace>
oc describe keycloakuser consumer -n <RH-SSO namespace>
oc describe keycloakuser producer -n <RH-SSO namespace>
```

Note if you choose "value: secret" for password in the [user](./rhsso-users.yaml) CR then after a user is created, the Operator creates a Secret using the following naming pattern: credential-<realm name>-<username>-<namespace>, containing the username and, if "value: secret" has been specified in the CR credentials attribute, the password. 
Otherwise, if no "value: secret" has been specified, the password for these users will be set to the value specified in the CR.

## Apply Security to AMQ Broker 

Apply RH-SSO Security Login Module to the existing AMQ Broker.  The custom resource is of kind ActiveMQArtemisSecurity.
Make sure you are applying into the AMQ Broker namespace.

``` shell
oc process -f .\rh-sso-integration\amq-rhsso-security.yaml -p BROKER_NAME=$BROKER_NAME | oc apply -f - -n <AMQ Broker namespace>
```

Give the AMQ Broker pod time to re-start and re-initialize completely before moving on to the steps below of trying to validate web console or broker.  You should see pod 'oc get pods' report back with STATUS "Running".  

## Validate Web console login 

Go to the AMQ BRoker route for the admin console e.g. in the Openshift console find the route for 
the console having naming convention ${BROKER_NAME}-wconsj-0-svc-rte.
Client the URL to take you to login for AMQ Admin console. This should now re-direct you
to RH-SSO login screen where you are asked to enter user/password. 
You may enter any of the users created in RH-SSO e.g. amqadmin, amqconsumer, amqproducer.  
All have default password 'secret' as specified in the (already applied) KeycloakUser resources in 'rhsso-users.yaml'. 

## Validate Broker user for Producer/Consumer (machine-to-machine authentication)

Your custom applications (message consumer and producers) must authenticate against the broker, and to 
do so they need to be assigned user/password for initial connectivity to the broker.  The credentials will be
assigned to the apps and used by the apps to connect to the broker.  On connection, these apps pass in user/password to the
standart AMQ / JMS API. How this is done in code is different depending on the implementation language.  

To validate this is working as expected you can 
first login to the pod running AMQ Broker. For example (your command may look slightly different depending on the broker name)

``` shell

oc rsh my-broker-ss-0
cd amq-broker/bin

```
Change directories as shown above into the directory where the 'artemis' tool is located.  This tool can simulate an
AMQ BRoker consumer/producer. 

To run the command as a producer run the following:

``` shell
./artemis producer --verbose --user amqproducer --password secret  --destination address.helloworld --message-count 10 --url tcp://my-broker-amq-0-svc:61617 --protocol amqp

```
From another shell you can run a consumer to consume the messages just generated. E.g. 

``` shell
./artemis consumer --verbose --user amqconsumer --password secret  --destination address.helloworld --message-count 10 --url tcp://my-broker-amq-0-svc:61617 --protocol amqp

```
