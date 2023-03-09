# Scale down RHOAM when APIManager is created and scaling RHOAM back if needed

This SOP covers scaling down RHOAM operator when 3scale APIManager CR is created

## Pre-req
- RHOAM installation is triggered

## Watch for APIManager and scale down RHOAM operator as soon as APIManager is created

```
until oc get apimanager 3scale -n redhat-rhoam-3scale; do 
    echo "APIManager isn't created yet" 
    sleep 2 
done
echo "APIManager is present. Scaling down RHOAM"
oc scale deployment rhmi-operator -n redhat-rhoam-operator --replicas=0
```
# Scale RHOAM operator up
```
oc scale deployment rhmi-operator -n redhat-rhoam-operator --replicas=1
```