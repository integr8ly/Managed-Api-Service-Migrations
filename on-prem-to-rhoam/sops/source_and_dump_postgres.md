# Backup Postgres DB and source Postgres backup

This SOP is broken up into two parts. The first section details the `oc` commands needed to dump the Postgres DB to a `.psql` file. The second section details how to source that `.psql` backup into an existing Postgres DB.

## Prerequisites
- `oc` logged in to the engineering cluster connected to the standalone VPC to perform the backup
- `oc` logged in to the production cluster connected to perform the sourcing of the backup

## Backup Postgres DB to `.psql` file
Before proceeding with the backup, confirm you are `oc` logged in to the _**engineering**_ cluster

### Get Postgres DB credentials from 3scale system-database Secret
Make sure to replace the <namespace-placeholder> with the actual namespace containing the 3scale system-database Secret
```
NAMESPACE=<namespace-placholder>

DB_HOST=$(oc get secrets/system-database -n $NAMESPACE -o template --template={{.data.URL}} | base64 --decode | cut -d '@' -f 2 | cut -d ':' -f 1)
DB_PORT=$(oc get secrets/system-database -n $NAMESPACE -o template --template={{.data.URL}} | base64 --decode | cut -d ':' -f 4 | cut -d '/' -f 1)
DB_USER=$(oc get secrets/system-database -n $NAMESPACE -o template --template={{.data.DB_USER}} | base64 --decode)
DB_PASSWORD=$(oc get secrets/system-database -n $NAMESPACE -o template --template={{.data.DB_PASSWORD}} | base64 --decode)
DATABASE_NAME=$(oc get secrets/system-database -n $NAMESPACE -o template --template={{.data.URL}} | base64 --decode | cut -d '/' -f 4)
```

### Create a throwaway Postgres 13.8 client on engineering cluster
```
oc create namespace postgres-client
oc project postgres-client
oc new-app --image-stream="openshift/postgresql:13-el8" -e POSTGRESQL_USER=postgresuser -e POSTGRESQL_PASSWORD=password -e POSTGRESQL_DATABASE=sample
```

### Backup Postgres to local machine using `pg_dump`
```
oc exec $(oc get pods --no-headers | awk '{print $1}') -- env PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -c $DATABASE_NAME > 2-system_database_backup.psql
```

### Confirm that `pg_dump` wasn't interrupted
```
tail 2-system_database_backup.psql
```
Confirm that the output ends with:
```
--
-- PostgreSQL database dump complete
--
```
Note: If the above line isn't present at the end of the output, `pg_dump` was interrupted during the backup and needs to be run again.

## Source `.psql` backup to Postgres DB
Before proceeding with sourcing the backup, confirm you are `oc` logged in to the _**production**_ cluster

### Get Postgres DB credentials from RHOAM threescale-postgres-rhoam Secret
Make sure to update the value of the `NAMESPACE` var if needed
```
NAMESPACE=redhat-rhoam-operator

DB_HOST=$(oc get secrets/threescale-postgres-rhoam -n $NAMESPACE -o template --template={{.data.host}} | base64 --decode)
DB_PORT=$(oc get secrets/threescale-postgres-rhoam -n $NAMESPACE -o template --template={{.data.port}} | base64 --decode)
DB_USER=$(oc get secrets/threescale-postgres-rhoam -n $NAMESPACE -o template --template={{.data.username}} | base64 --decode)
DB_PASSWORD=$(oc get secrets/threescale-postgres-rhoam -n $NAMESPACE -o template --template={{.data.password}} | base64 --decode)
DATABASE_NAME=$(oc get secrets/threescale-postgres-rhoam -n $NAMESPACE -o template --template={{.data.database}} | base64 --decode)
```

### Create a throwaway Postgres 13.8 client on production cluster
```
oc create namespace postgres-client
oc project postgres-client
oc new-app --image-stream="openshift/postgresql:13-el8" -e POSTGRESQL_USER=postgresuser -e POSTGRESQL_PASSWORD=password -e POSTGRESQL_DATABASE=sample
```

### Source the `.psql` file
Note: If the database $DATABASE_NAME doesn't exist you will first need to log in to the Postgres instance and create it
```
oc exec -i $(oc get pods --no-headers | awk '{print $1}') -- env PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DATABASE_NAME < system_database_backup.psql
```

### Cleanup throwaway Postgres client if it is no longer needed
```
oc project default
oc delete namespace postgres-client
```