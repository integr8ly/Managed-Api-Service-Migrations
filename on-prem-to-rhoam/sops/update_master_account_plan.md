# Update master account plan
This sop covers updating master account plan on 3scale instance to the "Enterprise" one
## Envs
```
THREESCALE_NAMESPACE=<namespace where 3scale is installed>
```
## Update master account plan
```
oc rsh -n $THREESCALE_NAMESPACE -c system-provider dc/system-app bash -c 'bundle exec rails runner "svc = Account.master.services.first; svc.update_attribute(:default_application_plan, svc.application_plans.find_by(system_name: \"enterprise\"))"'
```

