# Install 3scale Operator matching source version and upgrade to RHOAMs matching version

This SOP covers installation of 3scale that matches the source 3scale version and upgrading 3scale to RHOAM version.

# Export envs

```
NAMESPACE=migration
```

# Initial install

## Create new project
```
oc new-project migration
oc project migration
```
## Create subscription to install 3scale operator 0.8.4
```
cat << EOF | oc create -f - -n $NAMESPACE
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
    name: 3scale-operator
spec:
  channel: threescale-2.11
  installPlanApproval: Automatic
  name: 3scale-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: 3scale-operator.v0.8.4-0.1655690146.p
EOF
```
## Create Operator Group:
```
cat << EOF | oc create -f - -n $NAMESPACE
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
    name: 3scale-operator-og
spec:
  targetNamespaces:
    - $NAMESPACE
  upgradeStrategy: Default
EOF
```
## Confirm operator is successfully installed:
```
oc get deployment threescale-operator-controller-manager-v2 -n $NAMESPACE -o json | jq -r '.status.readyReplicas'
```
Should return 1.
## Create dummy s3 secret
```
oc apply -f - -n $NAMESPACE <<EOF   
---
apiVersion: v1
kind: Secret
metadata:
  creationTimestamp: null
  name: aws-auth
stringData:
  AWS_ACCESS_KEY_ID: something
  AWS_SECRET_ACCESS_KEY: something
  AWS_BUCKET: something
  AWS_REGION: us-east-1
type: Opaque
EOF
```
## Create APIM
Retrieve the wildcard domain:
```
oc get routes console -n openshift-console -o json | jq -r '.status.ingress[0].routerCanonicalHostname'
```
And strip the `router-default.` from it and use as value in the wildcard domain below.
Create APIManager
```
oc apply -f - -n $NAMESPACE <<EOF                                                             
---             
apiVersion: apps.3scale.net/v1alpha1
kind: APIManager
metadata:
  name: 3scale
spec:
  wildcardDomain: DOMAIN
  resourceRequirementsEnabled: false                
  system:
    fileStorage:
      simpleStorageService:
        configurationSecretRef:
          name: aws-auth
EOF
```
## Confirm 3scale is fully installed
```
oc get apimanager 3scale -o json | jq -r '.status.deployments'
```
All deployments should be marked as "ready"

At this point 3scale installation is completed.

---
# Scale down 3scale instance

This part of SOP covers how to scale down 3scale instance.

## Envs

```
OPERATOR_NAMESPACE=<namespace where operator lives>
```
```
THREESCALE_NAMESPACE=<namespace where 3scale is>
```
## Scale down 3scale operator
```
oc scale deployment threescale-operator-controller-manager-v2 -n $OPERATOR_NAMESPACE --replicas=0
```
## Scale down 3scale instance
```
oc scale dc/{system-memcache,zync-database,apicast-production,apicast-staging,backend-cron,backend-listener,backend-worker,backend-redis,system-app,system-memcache,system-mysql,system-redis,system-sidekiq,system-sphinx,zync,zync-database,zync-que} -n $THREESCALE_NAMESPACE --replicas=0
```
## Confirm 3scale is scaled down
```
oc get pods -n $THREESCALE_NAMESPACE
```
All pods should be showing 0/X

---

# Move secrets from local to migration cluster and plug in AWS resources
This part of SOP covers moving the secrets to migration cluster.

## Env
```
THREESCALE_NAMESPACE=<namespace where 3scale instance is running>
```
## Apply secrets
```
oc apply -f system-seed.json -n $THREESCALE_NAMESPACE
oc apply -f system-master-apicast.json -n $THREESCALE_NAMESPACE
oc apply -f system-events-hook.json -n $THREESCALE_NAMESPACE
oc apply -f system-app.json -n $THREESCALE_NAMESPACE    
oc apply -f system-recaptcha.json -n $THREESCALE_NAMESPACE
oc apply -f system-memcache.json -n $THREESCALE_NAMESPACE
```
# Plug in system db, backendlistener and backend worker to 3scale instance

This part of SOP covers pluggin in 3scale system database, backend redis and system redis AWS resources to 3scale instance.

## Patch system-database secret

### Envs
```
POSTGRES_HOST=<HOST URL OF THE SYSTEM DB IN AWS>
```
```
POSTGRES_USER=<USER IN POSTGRES DB>
```
```
POSTGRES_PASSWORD=<PASSWORD IN POSTGRES DB>
```
```
POSTGRES_DATABASE_NAME=<Name of the database>
```
### Patching secret
Patch system-database secret URL:
```
echo -n "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:5432/$POSTGRES_DATABASE_NAME" | base64 -w 0 | xargs -I URL_IN_DATA oc patch secret system-database -n $THREESCALE_NAMESPACE -p '{"data":{"URL": "URL_IN_DATA"}}'
```
Patch system-database secret USER:
```
echo -n "$POSTGRES_USER" | base64 -w 0 | xargs -I DB_USER_IN_DATA oc patch secret system-database -n $THREESCALE_NAMESPACE -p '{"data":{"DB_USER": "DB_USER_IN_DATA"}}'
```
Patch system-database secret PASSWORD:
```
echo -n "$POSTGRES_PASSWORD" | base64 -w 0 | xargs -I DB_PASSWORD_IN_DATA oc patch secret system-database -n $THREESCALE_NAMESPACE -p '{"data":{"DB_PASSWORD": "DB_PASSWORD_IN_DATA"}}'
```

## Patch backend redis secret

### Envs
```
BACKEND_REDIS_HOST=<host of the backend redis>
```
### Patch the secret
Redis storage URL:

```
echo -n "redis://$BACKEND_REDIS_HOST:6379/0" | base64 -w 0 | xargs -I REDIS_STORAGE_URL_IN_DATA oc patch secret backend-redis -n $THREESCALE_NAMESPACE -p '{"data":{"REDIS_STORAGE_URL": "REDIS_STORAGE_URL_IN_DATA"}}'
```

Redis queues url:
```
echo -n "redis://$BACKEND_REDIS_HOST:6379/1" | base64 -w 0 | xargs -I REDIS_QUEUES_URL_IN_DATA oc patch secret backend-redis -n $THREESCALE_NAMESPACE -p '{"data":{"REDIS_QUEUES_URL": "REDIS_QUEUES_URL_IN_DATA"}}'
```
## Patch system redis secret

### Envs
```
SYSTEM_REDIS_HOST=<host of the system redis>
```
### Patch the secret

URL:

```
echo -n "redis://$SYSTEM_REDIS_HOST:6379/1" | base64 -w 0 | xargs -I URL_IN_DATA oc patch secret system-redis -n $THREESCALE_NAMESPACE -p '{"data":{"URL": "URL_IN_DATA"}}'
```
MESSAGE bus URL:
```
echo -n "redis://$SYSTEM_REDIS_HOST:6379/1" | base64 -w 0 | xargs -I MBUS_URL_IN_DATA oc patch secret system-redis -n $THREESCALE_NAMESPACE -p '{"data":{"MESSAGE_BUS_URL": "MBUS_URL_IN_DATA"}}'
```
## Patch APIManager to use external resources
Add the following to the spec of APIM
```
highAvailability:
    enabled: true
```

---

# Scale up 3scale instance and confirm it's working as expected

This part of SOP covers how to scale down 3scale instance.

## Envs

```
OPERATOR_NAMESPACE=<namespace where operator lives>
```
```
THREESCALE_NAMESPACE=<namespace where 3scale is>
```
## Scale up 3scale operator
```
oc scale deployment threescale-operator-controller-manager-v2 -n $OPERATOR_NAMESPACE --replicas=1
```
## Scale up 3scale instance
```
oc scale dc/{system-memcache,system-sphinx,zync-database} -n $THREESCALE_NAMESPACE --replicas=1
```
## Confirm 3scale is scaled up
```
oc get apimanager 3scale -o json -n $THREESCALE_NAMESPACE | jq -r '.status.deployments'
```
All deployments should be marked as ready

## Re-sync routes
```
oc exec -t $(oc get pods -l 'deploymentConfig=system-sidekiq' -o json -n $THREESCALE_NAMESPACE | jq '.items[0].metadata.name' -r) -n $THREESCALE_NAMESPACE -- bash -c "bundle exec rake zync:resync:domains"
```
# Confirm 3scale api call works as expected by fetching list of accounts
## Envs
```
THREESCALE_NAMESPACE=<Namespace of 3scale instance>
```
## Confirm master api calls work 
```
MASTER_TOKEN=$(oc get secrets/system-seed -n $THREESCALE_NAMESPACE -o template --template={{.data.MASTER_ACCESS_TOKEN}} | base64 -d)
```
```
MASTER_ROUTE=$(oc get route -n migration | grep master |awk '{print $2}')
```
Make the API call:
```
curl -v  -X GET "https://$MASTER_ROUTE/admin/api/accounts.xml" -d "access_token=$MASTER_TOKEN"
```

# Upgrade 3scale to desired version
## Pre-req
- know which version of 3scale is RHOAM using currently

## From 2.11 > 2.12
### Envs
```
THREESCALE_NAMESPACE=<3scale instance ns>
```
### Update subscription to 2.12
```
oc patch sub 3scale-operator -n $THREESCALE_NAMESPACE --type=merge --patch '{"spec":{"channel": "threescale-2.12"}}'
```
### Patch system redis
Remove MESSAGE_BUS mentions from the system-redis secret
```
oc patch secret system-redis -n $THREESCALE_NAMESPACE --type=json -p='[{"op": "remove", "path": /data/MESSAGE_BUS_URL}]'
oc patch secret system-redis -n $THREESCALE_NAMESPACE --type=json -p='[{"op": "remove", "path": /data/MESSAGE_BUS_NAMESPACE}]'
oc patch secret system-redis -n $THREESCALE_NAMESPACE --type=json -p='[{"op": "remove", "path": /data/MESSAGE_BUS_SENTINEL_ROLE}]'
oc patch secret system-redis -n $THREESCALE_NAMESPACE --type=json -p='[{"op": "remove", "path": /data/MESSAGE_BUS_SENTINEL_HOSTS}]'
```
Confirm all mentions of MESSAGE_BUS are gone:
```
oc get secret system-redis -n $THREESCALE_NAMESPACE -o yaml | grep MESSAGE_BUS
```
Should return no value.
### Confirm upgrade has finished
```
oc get apimanager 3scale -n $THREESCALE_NAMESPACE -o json | jq -r '.status.deployments'
```
Should return all deployments as "ready"

###
Confirm that master api works as expected
```
curl -v  -X GET "https://$MASTER_ROUTE/admin/api/accounts.xml" -d "access_token=$MASTER_TOKEN"
```
## From 2.12 to 2.13
```
oc patch sub 3scale-operator -n $THREESCALE_NAMESPACE --type=merge --patch '{"spec":{"channel": "threescale-2.13"}}'
```
### Confirm upgrade has finished
```
oc get apimanager 3scale -n $THREESCALE_NAMESPACE -o json | jq -r '.status.deployments'
```
Should return all deployments as "ready"

### Confirm that master api works as expected
```
curl -v  -X GET "https://$MASTER_ROUTE/admin/api/accounts.xml" -d "access_token=$MASTER_TOKEN"
```
## From 2.13 to mas release
Due to the fact that -mas 2.13 doesn't have proper replaces we need to remove the operator and re-install it

### Remove subscription
```
oc delete sub 3scale-operator -n $THREESCALE_NAMESPACE
```
```
oc delete csv 3scale-operator.v0.10.1-0.1675914645.p -n $THREESCALE_NAMESPACE
```
### Create subscription
```
cat << EOF | oc create -f - -n $NAMESPACE
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
    name: 3scale-operator
spec:
  channel: threescale-mas
  installPlanApproval: Automatic
  name: 3scale-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: 3scale-operator.v0.11.1-mas
EOF
```
### Confirm upgrade has finished
```
oc get apimanager 3scale -n $THREESCALE_NAMESPACE -o json | jq -r '.status.deployments'
```
Should return all deployments as "ready"

### Confirm that master api works as expected
```
curl -v  -X GET "https://$MASTER_ROUTE/admin/api/accounts.xml" -d "access_token=$MASTER_TOKEN"
```
---