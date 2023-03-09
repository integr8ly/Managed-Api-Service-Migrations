# Move secrets from local to migration cluster and plug in AWS resources
This part of SOP covers moving the secrets to production cluster.

```
# apply secrets to both rhoam operator namespace and 3scale namespace as they backup & restore to each other
oc apply -f system-seed.json -n redhat-rhoam-operator
oc apply -f system-master-apicast.json -n redhat-rhoam-operator
oc apply -f system-seed.json -n redhat-rhoam-3scale
oc apply -f system-master-apicast.json -n redhat-rhoam-3scale

# apply remainder secrets to rhoam 3scale namespace
oc apply -f system-events-hook.json -n redhat-rhoam-3scale
oc apply -f system-app.json -n redhat-rhoam-3scale              
oc apply -f system-recaptcha.json -n redhat-rhoam-3scale
oc apply -f system-memcache.json -n redhat-rhoam-3scale
```