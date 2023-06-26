# Retrieving required secrets from the cluster

This SOP covers retrieving the required secrets

## Expose env
```
NAMESPACE=<the namespace where 3scale instance is running>
```
Run the following command to retrieve secrets:
```
# 3scale Secrets
oc get secrets system-seed -n $NAMESPACE -o json | jq -r 'del(.metadata.ownerReferences,.metadata.selfLink,.metadata.namespace,.metadata.uid,.metadata.resourceVersion)' > system-seed.json

oc get secrets system-events-hook -n $NAMESPACE  -o json | jq -r 'del(.metadata.ownerReferences,.metadata.selfLink,.metadata.namespace,.metadata.uid,.metadata.resourceVersion)' > system-events-hook.json

oc get secrets system-app -n $NAMESPACE -o json | jq -r 'del(.metadata.ownerReferences,.metadata.selfLink,.metadata.namespace,.metadata.uid,.metadata.resourceVersion)' > system-app.json

oc get secrets system-recaptcha -n $NAMESPACE -o json | jq -r 'del(.metadata.ownerReferences,.metadata.selfLink,.metadata.namespace,.metadata.uid,.metadata.resourceVersion)' > system-recaptcha.json

oc get secrets system-master-apicast -n $NAMESPACE -o json | jq -r 'del(.metadata.ownerReferences,.metadata.selfLink,.metadata.namespace,.metadata.uid,.metadata.resourceVersion)' > system-master-apicast.json

oc get secrets system-memcache -n $NAMESPACE -o json | jq -r 'del(.metadata.ownerReferences,.metadata.selfLink,.metadata.namespace,.metadata.uid,.metadata.resourceVersion)' > system-memcache.json
```