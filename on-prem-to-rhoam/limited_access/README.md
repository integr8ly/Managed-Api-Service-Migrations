# Red Hat has limited access to customer data

This document describes the necessary steps that are required in order to migrate from on-prem to RHOAM with Red Hat having limited access to customer's AWS account. 

</b> Note: The following steps are subject to change </b>

## Checklist

<b> [Migration tracker](./task_checklist.md#tracker-for-limited-access-migration) </b> 

# Before migration pre-requisites 

These steps must be completed a day (or more) before the migration starts. All of the steps listed in this section are not service affecting and are done in order to minimize the time it takes to migrate.

# Red Hat pre-requistes

### Pre-requisite 1

<b> Owner </b>: Red Hat - BU/SRE-P

<b> Goal </b>: Provide RHOAM Eng team with the access to:

- Destination AWS account
- Destination cluster kubeadmin access
---
### Pre-requisite 2

<b> Owner </b>: Red Hat - RHOAM Eng

<b> Goal </b>: Confirm access to the resources from Pre-requisite 1

---
### Pre-requisite 3

<b> Owner </b>: Red Hat - RHOAM Eng

<b> Goal </b>: Create migration cluster and:

- Confirm access to it
- Install 3scale version matching the source 3scale version using -mas channel

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#initial-install) </b> 

---
### Pre-requisite 4

<b> Owner </b>: Red Hat - RHOAM Eng

<b> Goal </b>: Configure stand alone VPC

<b> [SOP Link](../sops/create_standalone_vpc.md#create-standalone-vpc-and-associated-aws-network-components) </b> 

---
### Pre-requisite 5

<b> Owner </b>: Red Hat - RHOAM Eng

<b> Goal </b>: On migration cluster AWS account standalone VPC create the following:

- System database matching the same type and version that's used on source cluster
- Two Redis instances with version matching RHOAM version
- In case if the system database is not PostgreSQL database type, provision PostgreSQL - this database will be used as the destination database during conversion from MySQL or Oracle to PostgreSQL

---
### Pre-requisite 6

<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Create MITM instance

<b> [SOP Link](../sops/mitm.md#create-mitm-instance) </b> 


# Customer / Red Hat pre-requisites


### Pre-requisite 1

<b> Owner </b>: Customer

<b> Goal </b>: Create an S3 bucket with 3scale secrets in it

<b> [SOP Link](../sops/pull_threescale_secrets.md#retrieving-required-secrets-from-the-cluster) </b> 

---
### Pre-requisite 2

<b> Owner </b>: Customer

<b> Goal </b>: Provide RHOAM Eng with the access to the S3 bucket

---

### Pre-requisite 3

<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Confirm that the access to the S3 is correct and that the bucket contents can be pulled

<b> [SOP Link](../sops/pull-push-S3-contents.md#pull-from-s3-bucket) </b> 

---
### Pre-requisite 4

<b> Owner </b>: Customer

<b> Goal </b>: Configure IDP on the destination cluster and confirm that the cluster is accessible via the IDP created

---
### Pre-requisite 5 - <b> OPTIONAL </b>

<b> Owner </b>: Customer

<b> Goal </b>: Create custom domain CR on destination cluster 

---
### Pre-requisite 6

<b> Owner </b>: Customer

<b> Goal </b>: Trigger RHOAM installation, ensure that the following configuration is correct:

- SMTP
- Custom domain
- Notification email address
- Quota
---
### Pre-requisite 7

<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale down RHOAM Operator as soon as the APIManager is created on destination cluster

<b> [SOP Link](../sops/scale_rhoam_when_apimanager_is_created.md#scale-down-rhoam-when-apimanager-is-created-and-scaling-rhoam-back-if-needed) </b> 

---
### Pre-requisite 8

<b> Owner </b>: Customer

<b> Goal </b>: Confirm that there's a rollback procedure in place in case of migration failure


# Migration

Once all of the pre-requisites are met the migration can start

## Source cluster

Below are the steps to be performed on source cluster

---
### Step 1
<b> Owner </b>: Customer

<b> Goal </b>: Prepare 3scale instance for the migration:

- Stop traffic going to 3scale instance
- Clear the job queue or accept the potential data loss
- Scale down 3scale instance

To check the status of the 3scale queues follow the SOP:

<b> [SOP Link](../sops/sidekiq_queue_status.md#check-the-3scale-queues-status) </b>

---
### Step 2
<b> Owner </b>: Customer

<b> Goal </b>: Perform data dump from:
- System database
- Backend Redis instance
- Scale down 3scale instance


## Migration cluster

Below are the steps to be performed on the migration cluster

### Step 3
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Source system database with the dump provided by the customer

<b> [SOP Link](../sops/source_mysql_db.md#source-mysql-57-data-and-bump-the-engine-version-from-5738-to-8028) </b>

---
### Step 4
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Upgrade the MySQL version from 5.28 to 8.X

<b> [SOP Link](../sops/source_mysql_db.md#bump-mysql-engine-version) </b>

---
### Step 5
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Migrate from MySQL to PostgreSQL

<b> [SOP Link](../sops/mysql_to_postgres_migration.md#migrate-data-in-mysql-database-to-empty-postgres-database) </b>

---
### Step 6
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Edit master routes and customer tenant/tenants admin routes

<b> [SOP Link](../sops/update_routes_in_3scale.md#update-the-master-and-admin-portal-routes-via-sql-commands) </b>

---
### Step 7
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale down 3scale instance

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#scale-down-3scale-instance) </b>

---

### Step 8
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Copy secrets from source to migration cluster and plug in AWS system database and Redises to 3scale instance

<b> Copy secrets: </b>

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#move-secrets-from-local-to-migration-cluster-and-plug-in-aws-resources) </b>

<b> Plug in external databases to 3scale </b>

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#plug-in-system-db-backendlistener-and-backend-worker-to-3scale-instance) </b>

---
### Step 9
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale up 3scale and confirm apis are accessible via master api calls

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#scale-up-3scale-instance-and-confirm-its-working-as-expected) </b>

---
### Step 10
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Perform 3scale updates up to version matching current RHOAM 3scale version

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#upgrade-3scale-to-desired-version) </b>

---
### Step 11
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale 3scale down and update master and customer tenant/tenants admin portal route to the route matching destination cluster 

<b> Scale 3scale down: </b>

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#scale-down-3scale-instance) </b>

<b> Update master and customer tenant/tenants admin portal routes </b>

<b> [SOP Link](../sops/update_routes_in_3scale.md#update-the-master-and-admin-portal-routes-via-sql-commands) </b>

---
### Step 12
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Perform backup of Postgres database and put backup in S3 bucket (if needed)

<b> [SOP Link](../sops/source_and_dump_postgres.md#backup-postgres-db-to-psql-file) </b>



## Production cluster

Below are the steps required to be performed against production cluster and AWS account

---
### Step 13
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale 3scale down and push Postgres database dump to destination cluster via throwaway pod

<b> Scale down 3scale instance </b>

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#scale-down-3scale-instance) </b>

<b> Source system database with the PostgreSQL dump </b>

<b> [SOP Link](../sops/source_and_dump_postgres.md#source-psql-backup-to-postgres-db) </b>

---
### Step 14
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Recover backend backend Redis

<b> [SOP Link](../sops/backend_redis_restoration.md#redis-migration) </b>

---
### Step 15
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Copy secrets from local to destination cluster

<b> [SOP Link](../sops/move_secrets_from_local_to_cluster.md#move-secrets-from-local-to-migration-cluster-and-plug-in-aws-resources) </b>

---
### Step 16
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale up 3scale and provide routes to the customer so that they can configure their systems with the new routes

<b> [SOP Link](../sops/create_initial_3scale_and_upgrade.md#scale-up-3scale-instance-and-confirm-its-working-as-expected) </b>

---
### Step 17
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Set master account plan to "Enterprise"

<b> [SOP Link](../sops/update_master_account_plan.md) </b>

---
### Step 18
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Confirm 3scale is up and running, navigate to customer tenant/s (impresonate) make few api calls etc


---
### Step 19
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Create RHOAM default tenant

<b> [SOP Link](../sops/create_rhoam_default_tenant.md) </b>

---
### Step 20
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Scale up RHOAM

<b> [SOP Link](../sops/scale_rhoam_when_apimanager_is_created.md#scale-rhoam-operator-up) </b>

---
### Step 21
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Wait for RHOAM Operator to finish installation

---
### Step 22
<b> Owner </b>: RHOAM Eng

<b> Goal </b>: Create SSO integration on additional tenant

<b> [SOP Link](../sops/create_sso_integration.md) </b>

---
### Step 23
<b> Owner </b>: Customer

<b> Goal </b>: Publish SSO Integration by logging to 3scale and testing SSO Integration

---
### Step 24
<b> Owner </b>: Customer

<b> Goal </b>: Perform verification steps

---
### Step 25
<b> Owner </b>: Customer

<b> Goal </b>: Update systems to point to new routes

---