# On-prem to RHOAM migrations

 The owner of each migration step in the process will vary based on the level of access granted by the customer, however, the general flow remains the same and it is a matter of who is going to go through each SOP.

# Migration Paths

Following tables shows possible migration paths based on the access level given to Red Hat

| Step | Limited access | Further limits on access |  No access  |
|--------------|--------------|----------|---|
|Performing pre-requisite steps by both parties, Red Hat and the customer |Red Hat / Customer|Red Hat / Customer|Red Hat / Customer|
|Disable services so that there's no more traffic going to 3scale|Customer|Customer|Customer|
|Confirming that the job queue is empty or relatively low and acceptance on data loss of any job that has not been processed|Customer|Customer|Customer|
|Scaling down 3scale instance|Customer|Customer|Customer|
|Performing dumps|Customer|Customer|Customer|
|Creation of migration cluster|Red Hat|Red Hat|Customer|
|Connecting migration cluster to AWS account|Red Hat|Red Hat|Customer|
|Restoring system database on migration AWS account|Red Hat|Red Hat|Customer|
|Data manipulation|Red Hat|Red Hat|Customer|
|Connecting the system database and empty redis instance to migration|Red Hat|Red Hat|Customer|
|Going through 3scale|Red Hat|Red Hat|Customer|
|Data manipulation to ensure the routes will match the destination cluster|Red Hat|Red Hat|Customer|
|System database dump from migration cluster|Red Hat|Red Hat|Customer|
|Seeding the destination cluster system database|Red Hat|Red Hat|Customer|
|Restoring backend worker Redis instance to restore analytics data|Red Hat|Customer|Customer|
|Configuring 3scale at destination cluster|Red Hat|Red Hat|Red Hat|
|Restoring backend worker Redis instance to restore analytics data|Red Hat|Customer|Customer|
|Testing and publishing the SSO integrations|Customer|Customer|Customer|
|Verification of the installation of 3scale and RHOAM|Red Hat / Customer|Red Hat / Customer|Red Hat / Customer|
|Updates to customer systems to point to the new routes|Customer|Customer|Customer|

# Migrations per migration path

## <b> [Red Hat has limited access to customer data](./limited_access/README.md#red-hat-has-limited-access-to-customer-data) </b> 

This migration path is limiting Red Hat interactions with customers AWS accounts to a ceratin degree

#### Permissions required
- Full access to source and destination S3
- Full access to destination Elasticache
- Full access to destination OSD cluster

#### Customer interactions required

- Agreement on pre-requisites between Red Hat and the Customer
- Agreement on SMTP, Alerting email address and custom domain
- Agreement on the timing given to drain 3scale queues
- Providing Red Hat with system database, redis and 3scale secrets dump from source cluster
- Publishing and verifying the SSO integration flow
- Verification of the destination 3scale instance
- Configuring customer systems prior and post migration

## <b> [Red Hat has limited amount of permissions to customer data (extended limitations)](./extended_limit_on_access/README.md#red-hat-has-limited-amount-of-permissions-to-customer-data-extended-limitations) </b>  

This migration path is further limiting Red Hat interactions with customers AWS accounts to a certain degree (not entirerly)

#### Permissions required
- Full access to source and destination S3
- Full access to destination OSD cluster

#### Customer interactions required

- Agreement on pre-requisites between Red Hat and the Customer
- Agreement on SMTP, Alerting email address and custom domain
- Agreement on the timing given to drain 3scale queues
- Providing Red Hat with system database, redis and 3scale secrets dump from source cluster
- Performing Redis backup and restore in order to restore analytics
- Publishing and verifying the SSO integration flow
- Verification of the destination 3scale instance
- Configuring customer systems prior and post migration

## <b> [Red Hat has no permissions to customer data](./no_access/README.md#red-hat-has-no-permissions-to-customer-data) </b>  

This migration path is entirely removing the AWS access requirement by Red Hat.

#### Permissions required
- Full access to destination OSD/OCP cluster

#### Customer interactions required

- Agreement on pre-requisites between Red Hat and the Customer
- Agreement on SMTP, Alerting email address and custom domain
- Agreement on the timing given to drain 3scale queues
- Performing datbase dumps and recovery on migration cluster (the cluster that used in between source and destination cluster to perform necessary upgrades and data manipulation) these include:

    -  initial system database dump
    -  initial redis dump
    -  initial 3scale secrets dump
    -  recovering 3scale databases on AWS account connected to migration cluster
    - performing database conversion (in case if initial system database is using MySQL or Oracle)
    - performing required database updates while updating 3scale from source matching version to RHOAM matchign version
    - performing system database dump from migration cluster
    - restoring RHOAMs 3scale system database from the dump from migration cluster
    - restoring RHOAMs 3scale redis instance to migrate analytics

- Publishing and verifying the SSO integration flow
- Verification of the destination 3scale instance
- Configuring customer systems prior and post migration

# Common pre-requisite steps to all migration paths

These are the prequisites that must be confirmed before starting the migration

## Access levels

- Migration
    - Migration cluster access - Red Hat / Customer - dependant on migration path used
    - Migration AWS account - Red Hat / Customer - dependant on migration path used
- Production
    - Production cluster access - the access required by Red Hat and the customer regardless of migration path used
    - Production AWS account - Red Hat / Customer - dependant on migration path used

## Pre-migration pre-requisites
These are listed under each migration path seperately as it depends on permissions and agreements made between Red Hat and the Customer

# Common migration steps for all migration paths

These are steps that are in common in each of the migration paths chosen, the steps may vary a little but generally, the owner of step changes depending on the migration path used

- Performing pre-requisite steps by both parties, Red Hat and the customer
- Disable services so that there's no more traffic going to 3scale
- Confirming that the job queue is empty or relatively low and acceptance on data loss of any job that has not been processed
- Scaling down 3scale instance
- Performing dumps of:
    - system database
    - backend redis database
    - 3scale secrets
- Creation of migration cluster (done prior to migration)
- Connecting migration cluster to AWS account
- Installing source matching version of 3scale on migration cluster
- Restoring system database on migration AWS account with step in between dependant on the type of database used:
    - if MySQL or Oracle is used the database must be converted to PostgreSQL prior to conencting to 3scale
- Data manipulation to ensure routes in the system database match the new domain (of migration cluster)
- Connecting the system database and empty redis instance to migration cluster 3scale instance
- Going through 3scale updates following 3scale docs on changes required. This step covers upgrading 3scale from source version to destination matching version
- Data manipulation to ensure the routes will match the destination cluster.
- System database dump from migration cluster
- Seeding the destination cluster system database with the data from migration cluster
- Restoring backend worker Redis instance to restore analytics data
- Pushing secrets to the destination cluster
- Restoring 3scale at destination cluster
- Configuring 3scale at destination cluster to ensure that:
    - master account is using correct application plan
    - master account is accessible
    - RHOAMs default tenant is created
    - SSO integrations on customer tenants are created
- Customer testing and publishing the SSO integrations
- Customer and Red Hat verifies the installation of 3scale and RHOAM
- Customer updates their systems to point to the new routes
