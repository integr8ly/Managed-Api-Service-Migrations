# Migrate data in MySQL database to empty Postgres database

This SOP details the steps required to migrate data from a MySQL 8 database to PostgreSQL 13 database using `pgloader`

## Prerequisites
- MySQL 8 database with sourced data
- Empty Postgres 13 database
- `oc` logged in to the cluster connected which can reach both databases

## Create a Namespace to perform the migration in
```
cat << EOF | oc create -f -
kind: Namespace
apiVersion: v1
metadata:
  name: pgloader-migration
EOF
```

## Create a Secret containing the connection details
Set MySQL and Postgres DB connection details
```
MYSQL_HOST=<MySQL_db_host>
MYSQL_DATABASE_NAME=<MySQL_db_name>
MYSQL_USER=<MySQL_db_user>
MYSQL_PASSWORD=<MySQL_db_password>
```
```
POSTGRES_HOST=<Postgres_db_host>
POSTGRES_DATABASE_NAME=<Postgres_db_name>
POSTGRES_USER=<Postgres_db_user>
POSTGRES_PASSWORD=<Postgres_db_password>
```

```
cat << EOF | oc create -f - -n pgloader-migration
kind: Secret
apiVersion: v1
metadata:
  name: pgloader-config-file
  namespace: pgloader-migration
stringData:
  3scale.load: |
    LOAD DATABASE
      FROM mysql://$MYSQL_USER:$MYSQL_PASSWORD@$MYSQL_HOST/$MYSQL_DATABASE_NAME
      INTO postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST/$POSTGRES_DATABASE_NAME

    WITH prefetch rows = 10000, no truncate, create tables, include drop, create indexes, reset sequences, foreign keys, downcase identifiers, preserve index names
    ;
EOF
```
  
## Create a Job to perform the migration
```
cat << EOF | oc create -f - -n pgloader-migration
kind: Job
apiVersion: batch/v1
metadata:
  name: pgloader
  namespace: pgloader-migration
spec:
  backoffLimit: 1
  completions: 1
  template:
    spec:
      containers:
        - name: pgloader
          image: docker.io/dimitri/pgloader:v3.6.7
          command: ["pgloader"]
          args: ["--verbose","/home/3scale.load"]
          volumeMounts:
            - name: config-file
              mountPath: "/home"
              readOnly: true
          securityContext:
            allowPrivilegeEscalation: false
            runAsNonRoot: true
      volumes:
        - name: config-file
          secret:
            secretName: pgloader-config-file
      restartPolicy: Never
EOF
```

### Note: Migrating Large Databases
When using pgloader to migrate large databases (greater than 1-2 GBs), the Job might fail because the Pod that is running the Job may run out of memory. A potential workaround in this scenario is to edit the `pgloader-config-file` Secret and decrease the `prefetch rows` value to `1000`. Then delete the existing (failed) Job and recreate it.

## Remove the namespace
Remove the namespace when job completes
```
oc delete project pgloader-migration
```