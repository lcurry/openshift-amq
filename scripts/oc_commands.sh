#!/bin/bash
BROKER_KEYSTORE_PASSWORD=`curl --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" "https://gitlab.us.lmco.com/api/v4/projects/79139/variables/CERT_PASS"|jq .value`
BROKER_KEYSTORE_PASSWORD=`curl --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" "https://gitlab.us.lmco.com/api/v4/projects/79139/variables/CERT_PASS"|jq .value`
oc login --token=$OSH_TOKEN --server=$SERVER_URL --insecure-skip-tls-verify
oc project $PROJECT_NAME
oc create secret generic $APP_NAME-secret --from-file=broker.ks=broker.ks --from-file=client.ts=broker.ks  --from-literal=keyStorePassword=$BROKER_KEYSTORE_PASSWORD --from-literal=trustStorePassword=$BROKER_KEYSTORE_PASSWORD
oc create secret generic $APP_NAME-wsconsj --from-file=broker.ks=console.ks --from-file=client.ts=console.ks --from-literal=keyStorePassword=$WEB_KEYSTORE_PASSWORD --from-literal=trustStorePassword=$WEB_KEYSTORE_PASSWORD --from-literal=AMQ_CONSOLE_ARGS="--ssl-key /etc/$APP_NAME-wsconsj-volume/broker.ks --ssl-key-password $WEB_KEYSTORE_PASSWORD --ssl-trust /etc/$APP_NAME-wsconsj-volume/client.ts --ssl-trust-password $WEB_KEYSTORE_PASSWORD"
  