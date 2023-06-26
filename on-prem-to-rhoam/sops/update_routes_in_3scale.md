# Update the master and admin portal routes via SQL commands

## Cluster Preparation
* Create a temporary namespace
```
oc new-project migration
```
* Create a throwaway postgres pod
```
oc new-app postgresql POSTGRESQL_USER=throwaway POSTGRESQL_PASSWORD=throwaway POSTGRESQL_DATABASE=throwaway -n migration
```

## Terminal Environment Preparation
* Set DB Connection details
```
POSTGRES_HOST=<db_host>
POSTGRES_PORT=<db_port>
POSTGRES_DATABASE_NAME=<db_name>
POSTGRES_USER=<db_user>
POSTGRES_PASSWORD=<db_password>
```
* Set Wildcard Domain 
  * NOTE: The following will use the cluster default route name. Set to custom domain if using custom domain.
```
 WILDCARD_DOMAIN=$(oc get routes console -n openshift-console -o json | jq -r '.status.ingress[0].routerCanonicalHostname' | sed -e "s/^router-default.//")
```

* Set Tenant Org Name
```
 TENANT_ORG_NAME=<org_name>
```
## Update the master portal route
* View current master route
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c  "SELECT domain, self_domain FROM accounts WHERE org_name = 'Master Account';"
```

* Run query to update master route 
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c "UPDATE accounts SET domain = 'master.$WILDCARD_DOMAIN', self_domain = 'master.$WILDCARD_DOMAIN' WHERE org_name = 'Master Account';"
```

* Verify master route is updated
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c  "SELECT domain, self_domain FROM accounts WHERE org_name = 'Master Account';"
```
## Update admin route
* View current admin route
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c  "SELECT id, self_domain FROM accounts WHERE org_name = '$TENANT_ORG_NAME';"
```
* Set the ID of the tenant to update
```
TENANT_ID=<id>
```
* Run query to update admin route
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c "UPDATE accounts SET self_domain = lower('$TENANT_ORG_NAME-admin.$WILDCARD_DOMAIN') WHERE id = '$TENANT_ID';"
```
* To update the dev portal run
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c "UPDATE accounts SET domain = lower('$TENANT_ORG_NAME.$WILDCARD_DOMAIN') WHERE id = '$TENANT_ID';"
```

* Verify admin route is updated
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c  "SELECT id, self_domain FROM accounts WHERE org_name = '$TENANT_ORG_NAME';"
```

* Verify dev portal route is updated
```
oc exec deploy/postgresql -- env PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DATABASE_NAME -c  "SELECT id, domain FROM accounts WHERE org_name = '$TENANT_ORG_NAME';"
```

## Cluster cleanup
* Delete temporary namespace
```
oc delete project migration
```