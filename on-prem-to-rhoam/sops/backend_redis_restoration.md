# Redis migration
The steps below descirbe how to migrate backend redis 3scale instance from on prem 3scale to RHOAM 3scale.

General flow is to create a snapshot of desired Redis state and then leverage Cloud Resource Operator to restore Redis state from the snapshot provided.

Snapshot can be obtained with two approaches:
#### Approach #1
- rdb dump file pushed to S3 bucket
- restoring Redis instance from S3 dump
- saving a snapshot of restored instance

#### Approach #2
- snapshot from the desired Redis state is taken and copied over to RHOAMs AWS region
- Follow this guide from the `Edit Redis CR to prevent recreation during restoration` step

## Pre-reqs
- aws cli logged in (must be in the same zone as RHOAM installation is)
- Redis backup .rdb stored locally
- Be oc logged in to your OSD cluster with RHOAM fully installed
- jq (although all commands that use jq can be skipped and UI can be used instead)
- 3scale instance on destination cluster must be scaled down (including 3scale operator)
```
oc scale deployment threescale-operator-controller-manager-v2 -n redhat-rhoam-3scale-operator --replicas=0
```
```
oc scale dc/{system-memcache,zync-database,apicast-production,apicast-staging,backend-cron,backend-listener,backend-worker,backend-redis,system-app,system-memcache,system-mysql,system-redis,system-sidekiq,system-sphinx,zync,zync-database,zync-que} -n redhat-rhoam-3scale --replicas=0
```
- RHOAM must be scaled down
```
oc scale deployment rhmi-operator -n redhat-rhoam-operator --replicas=0
```

## Creating S3 bucket with required policy
### Export following ENVs:

- <b>BUCKETNAME</b> - desired S3 bucket name
- <b>REGION</b> - must be the same as the region RHOAM is installed in.
In case you are not sure what the region is, run the following command against OSD cluster with RHOAM installed on it:
```
REGION=$(oc get infrastructure cluster -o json | jq -r '.status.platformStatus.aws.region')
echo "Your region is $REGION"
```
- <b>RDBDUMPNAME</b> - name of the .rdb dump you have stored locally (include .rdb extension)
- <b>REDISCLUSTERID</b> - name of temporary Redis instance
- <b>SNAPSHOTNAME</b> - name of the snapshot to be created

### Create bucket used as a storage for your rdb dump file. This is done in order to create Redis using the .rdb file
```
aws s3 mb s3://$BUCKETNAME --region $REGION
```
### Block public access to the bucket
```
aws s3api put-public-access-block \
    --bucket $BUCKETNAME \
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```
### Put bucket policy to allow creation of Redis
```
cat <<EOF | aws s3api put-bucket-policy --bucket $BUCKETNAME --policy file:///dev/stdin
{
    "Version": "2012-10-17",
    "Id": "Policy15397346",
    "Statement": [
        {
            "Sid": "Stmt15399483",
            "Effect": "Allow",
            "Principal": {
                "Service": "$REGION.elasticache-snapshot.amazonaws.com"
            },
            "Action": [
                "s3:GetObject",
                "s3:ListBucket",
                "s3:GetBucketAcl"
            ],
            "Resource": [
                "arn:aws:s3:::$BUCKETNAME",
                "arn:aws:s3:::$BUCKETNAME/$RDBDUMPNAME",
                "arn:aws:s3:::$BUCKETNAME/$RDBDUMPNAME"
            ]
        }
    ]
}
EOF
```
### Put your .rdb file inside the bucket
```
aws s3api put-object --bucket $BUCKETNAME --key $RDBDUMPNAME --body $RDBDUMPNAME
```
## Create Redis from the .rdb dump file store in s3 bucket
### Get Subnet group name
```
BACKEND_REDIS_ID=$(oc get redis/threescale-backend-redis-rhoam -n redhat-rhoam-operator -o json | jq -r '.metadata.annotations.resourceIdentifier')
REDISCLUSTER_SUBNET_GROUP_NAME=$(aws elasticache describe-cache-clusters | jq --arg BACKEND_REDIS_ID "$BACKEND_REDIS_ID" '.CacheClusters | map(select(.ReplicationGroupId == $BACKEND_REDIS_ID))[0].CacheSubnetGroupName' -r)
```
### Create Redis from snapshot in s3 bucket
```
aws elasticache create-cache-cluster \
--cache-cluster-id $REDISCLUSTERID \
--cache-node-type cache.t3.micro \
--cache-subnet-group-name $REDISCLUSTER_SUBNET_GROUP_NAME \
--engine redis \
--engine-version 6.2 \
--num-cache-nodes 1 \
--snapshot-arns arn:aws:s3:::$BUCKETNAME/$RDBDUMPNAME
```
## Wait for Redis to be ready
```
aws elasticache describe-cache-clusters --cache-cluster-id $REDISCLUSTERID | jq '.CacheClusters[0].CacheClusterStatus'
```
## Create snapshot from restored Redis
```
aws elasticache create-snapshot --cache-cluster-id $REDISCLUSTERID --snapshot-name $SNAPSHOTNAME
```
## Wait for snapshot creation to report completed
```
aws elasticache describe-snapshots --snapshot-name $SNAPSHOTNAME | jq '.Snapshots[0].SnapshotStatus'
```
## Delete created Redis instance
Note: As precaution, please double check envs used
```
aws elasticache delete-cache-cluster --cache-cluster-id $REDISCLUSTERID
```
## Delete s3 bucket and objects
Note: As precaution, please double check envs used
- Remove object:
```
aws s3 rm s3://$BUCKETNAME --recursive
```
- Delete bucket
```
aws s3api delete-bucket --bucket $BUCKETNAME
```
## Restoring Redis on destination cluster via CRO

### Edit Redis CR to prevent recreation during restoration
```
oc patch redis/threescale-backend-redis-rhoam -n redhat-rhoam-operator -p '{"spec":{"skipCreate":true}}' --type merge 
```
### Retrieve AWS_REDIS_ID from backend redis secret
```
AWS_REDIS_ID=$(oc get redis/threescale-backend-redis-rhoam -n redhat-rhoam-operator -o json | jq -r '.metadata.annotations.resourceIdentifier')
```
### Get VPC security group IDs from existing Elasticache
```
SECURITY_GROUP_IDS=$(aws elasticache describe-cache-clusters | jq --arg AWS_REDIS_ID "$AWS_REDIS_ID" '.CacheClusters | map(select(.ReplicationGroupId == $AWS_REDIS_ID))[0].SecurityGroups[].SecurityGroupId' -r | tr '\n' ' ' | sed -e 's/[[:space:]]$//')
```
### Get Subnet group name from existing Elasticache
```
CACHE_SUBNET_GROUP_NAME=$(aws elasticache describe-cache-clusters | jq --arg AWS_REDIS_ID "$AWS_REDIS_ID" '.CacheClusters | map(select(.ReplicationGroupId == $AWS_REDIS_ID))[0].CacheSubnetGroupName' -r)
```
### Delete RHOAMs Redis
```
aws elasticache delete-replication-group --replication-group-id $AWS_REDIS_ID 
```
### Wait for Redis to be fully deleted
```
aws elasticache describe-replication-groups --replication-group-id $AWS_REDIS_ID | jq '.ReplicationGroups[0].Status'
```
The above command should return "is not found error"

### Restore Redis from snapshot
```
aws elasticache create-replication-group \
	--replication-group-id $AWS_REDIS_ID \
	--replication-group-description "A Redis replication group" \
	--engine Redis \
	--num-cache-clusters 2 \
	--snapshot-retention-limit 30 \
	--automatic-failover-enabled \
	--cache-subnet-group-name $CACHE_SUBNET_GROUP_NAME \
	--security-group-ids $SECURITY_GROUP_IDS \
	--snapshot-name $SNAPSHOTNAME
```
### Wait for Redis to be fully restored
```
aws elasticache describe-replication-groups --replication-group-id $AWS_REDIS_ID | jq '.ReplicationGroups[0].Status'
```
Above should return "available"

### Revert Redis CR Change
```
oc patch redis/threescale-backend-redis-rhoam -n redhat-rhoam-operator -p '{"spec":{"skipCreate":false}}' --type merge 
```
### Scale back RHOAM
```
oc scale deployment rhmi-operator -n redhat-rhoam-operator --replicas=1
```
### Scale back 3scale operator and 3scale instance
```
oc scale deployment threescale-operator-controller-manager-v2 -n redhat-rhoam-3scale-operator --replicas=1
```
```
oc scale dc/{system-memcache,zync-database,apicast-production,apicast-staging,backend-cron,backend-listener,backend-worker,backend-redis,system-app,system-memcache,system-mysql,system-redis,system-sidekiq,system-sphinx,zync,zync-database,zync-que} -n redhat-rhoam-3scale --replicas=1
```
### Wait for 3scale to fully restore, you can do this by checking installation state on rhmi CR:
```
oc get rhmi -n redhat-rhoam-operator -o json | jq -r '.items[0].status.stage'
```
Desired state is "completed". Please ensure to run the above command after a minute or two after scaling back RHOAM to trully reflect RHOAM state.
