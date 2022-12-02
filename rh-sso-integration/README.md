# amq-broker
For further information in applying RH-SSO resources such as realm, client, and users to a RH-SSO instance
see:

https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#realm-cr

The goal for these template is to allow you to deploy the resources needed to an existing RH-SSO instance 
to create the needed constructs to host AMQ Broker integration .

You should have the oc tool installed or execute a container image that already has it.


## Creating a realm custom resource 

For further information on creating a realm CR instance see:

https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#realm-cr

To appply the CR to create a realm in an existing RH-SSO instance,
run the following command.  

If you used the non-default value for RH_SSO_NAME on deployment of 
RH-SSO 
To designate the RH-SSO instance on which to apply the realm, you
will pass in the parameter RH_SSO_NAME.  

To get list of Keycloak instances
``` shell
oc get keycloak -n <RH-SSO namespace>
```

Check the value of "Name:" 
``` shell
oc describe keycloak <CR-name> -n <RH-SSO namespace>
```

The value for "Name:" is the <CR-name> and should be used when you deploy
the realm.   If you used 'keycloak' as the CR-name this is the default and you do not need to specify
RH_SSO_NAME.  

The following command can be used to deploy the realm. 

``` shell
oc process -f  .\rh-sso-integration\rhsso-realm.yaml  -p RH_SSO_NAME=<CR-name>  | oc apply -f - -n <RH-SSO namespace>

```

To see the resource properly provisioned 

``` shell
oc get keycloakrealm -n <RH-SSO namespace>
oc describe keycloakrealm <CR-name>-realm  -n <RH-SSO namespace>


```

## Creating a client custom resource 


For further information on creating a client CR instance see:

https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#client-cr

You can use the Operator to create clients in Red Hat Single Sign-On as defined by a custom resource. 
The following command can be used to deploy the realm. Only pass RH_SSO_NAME parameter if using non-default
name. 

``` shell
oc process -f  .\rh-sso-integration\rhsso-client.yaml  -p RH_SSO_NAME=<CR-name>  | oc apply -f - -n <RH-SSO namespace>

```

To see the resource properly provisioned 

``` shell
oc get keycloakclient -n <RH-SSO namespace>
oc describe keycloakclient artemis-broker -n <RH-SSO namespace>

```

After a client is created, the Operator creates a Secret containing the Client ID and the client’s secret
using the following naming pattern: keycloak-client-secret-artemis-broker. For example:


## Creating a user custom resource

For further information on creating a user CR instance see:

https://access.redhat.com/documentation/en-us/red_hat_single_sign-on/7.6/html/server_installation_and_configuration_guide/operator#user-cr

``` shell
oc process -f .\rh-sso-integration\rhsso-users.yaml -p RH_SSO_NAME=<CR-name> | oc apply -f - -n <RH-SSO namespace>
```
To see the resource properly provisioned 

``` shell
oc get keycloakuser -n <RH-SSO namespace>
oc describe keycloakuser admin -n <RH-SSO namespace>
oc describe keycloakuser consumer -n <RH-SSO namespace>
oc describe keycloakuser producer -n <RH-SSO namespace>
```

After a user is created, the Operator creates a Secret using the following naming pattern: credential-<realm name>-<username>-<namespace>, containing the username and, if it has been specified in the CR credentials attribute, the password. 
Here is an example of the secret name for admin user when default 'keycloak' was used for RH_SSO_NAME :
 'credential-keycloak-realm-admin-rh-sso'


## Apply Security to AMQ Broker 

Apply RH-SSO Security Login Module to the existing AMQ Broker 
Make sure you are applying into the AMQ Broker namespace.

``` shell
oc process -f .\rh-sso-integration\amq-rhsso-security.yaml -p RH_SSO_NAME=<CR-name> | oc apply -f - -n <AMQ Broker namespace>
```

