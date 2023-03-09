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
MYSQL_DB_HOST=<MySQL_db_host>
MYSQL_DATABASE_NAME=<MySQL_db_name>
MYSQL_DB_USER=<MySQL_db_user>
MYSQL_DB_PASSWORD=<MySQL_db_password>
```
```
DB_HOST=<Postgres_db_host>
DATABASE_NAME=<Postgres_db_name>
DB_USER=<Postgres_db_user>
DB_PASSWORD=<Postgres_db_password>
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
      FROM mysql://$MYSQL_DB_USER:$MYSQL_DB_PASSWORD@$MYSQL_DB_HOST/$MYSQL_DATABASE_NAME
      INTO postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST/$DATABASE_NAME

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