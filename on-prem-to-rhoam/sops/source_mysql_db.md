# Source MySQL 5.7 data and bump the engine version from 5.7.38 to 8.0.28

This SOP details the `oc` and `aws` commands needed to source data to a MySQL 5.7 RDS and upgrade the MySQL engine version from 5.7.38 to 8.0.28

## Prerequisites
- Standalone VPC created in AWS account
- 5.7.z MySQL RDS created in standalone VPC
- `.sql` created by `mysqldump` on local machine
- `oc` logged in to the cluster connected to the standalone VPC
- AWS CLI login

## Source MySQL data
### Create a throwaway MySQL client on the cluster
```
oc create namespace mysql-client
oc project mysql-client
oc new-app mysql:5.7 -e MYSQL_ROOT_PASSWORD=Password1
```

### Edit the database name in the `.sql` backup (if needed)
If the sourced MySQL database will eventually be converted to a Postgres database to be consumed by RHOAM, the name of the database should be `postgres`. In order to prepare for this scenario, manually edit the third line of the `.sql` backup file to be:
```
-- Host: 127.0.0.1    Database: postgres
```

### Copy `.sql` file to mysql pod
Once the mysql pod is ready:
```
oc rsync /path/to/sql/dir $(oc get pods --no-headers | awk '{print $1}'):/tmp
```
Note: it may take a few minutes to copy the `.sql` file to the pod

### Login to RDS and source the `.sql` file
Once the `.sql` file has been copied to the pod, `oc rsh` into the pod
```
oc rsh $(oc get pods --no-headers | awk '{print $1}')
```
Next `cd` to the directory containing the copied `.sql` file
```
cd /tmp/path/to/sql/dir
```
Now connect to the AWS RDS - make sure to replace the placeholders with valid credentials and to enter the password running the command
```
mysql -h <rds-hostname> -u <username> -P 3306 -p
```
Connect to the database you want to source to (if it doesn't exist, create it using `CREATE DATABASE <database-name>`)
```
USE <databasename>;
```
Source the file using the filename of the `.sql` copied to the pod
```
source <.sql-filename>;
```
Once the database has been source, disconnect from the database and exit the pod
```
\q
exit
```

## Bump MySQL engine version
### Get the RDS instance identifier and assign it to an environment variable
```
MYSQL_IDENTIFIER=$(aws rds describe-db-instances --filter Name=engine,Values=mysql --query 'DBInstances[].DBInstanceIdentifier' --output text)
```

### Update the database engine version to MySQL 8.0.28
```
aws rds modify-db-instance \
    --db-instance-identifier $MYSQL_IDENTIFIER \
    --engine-version 8.0.28 \
    --allow-major-version-upgrade \
    --apply-immediately
```

### Monitor upgrading status
The following command can be used to monitor the status of the upgrade which can take 5-30 minutes depending on the size of the database
```
aws rds describe-db-instances --filter Name=db-instance-id,Values=$MYSQL_IDENTIFIER --query 'DBInstances[].DBInstanceStatus' --output text
```