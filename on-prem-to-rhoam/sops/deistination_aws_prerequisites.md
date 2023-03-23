# Pre-requisites steps for destination AWS Account

## Create and configure an S3 bucket in the cluster region

REGION=$(oc get infrastructure cluster -o json | jq -r '.status.platformStatus.aws.region')

export BUCKETNAME=<bucket-name>

```
aws s3 mb s3://$BUCKETNAME --region $REGION
```

## Create a user and add pre-requisite permissions

export TEMP_AWS_USERNAME=temp-migration-user
export AWS_ACCOUNT=<account number>

Create the user
```
aws iam create-user --user-name $TEMP_AWS_USERNAME
```
ELASTICACHEPOLICY=temp-migration-elasticache
Create elasticache policy
```
aws iam create-policy --policy-name $ELASTICACHEPOLICY --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["elasticache:DescribeReplicationGroups","elasticache:ModifyReplicationGroup","elasticache:DescribeSnapshots","elasticache:CreateReplicationGroup","elasticache:DeleteReplicationGroup","elasticache:DescribeCacheClusters","elasticache:CreateSnapshot","elasticache:DeleteCacheCluster","elasticache:CreateCacheCluster"],"Resource":"*"}]}'
```

```
aws iam attach-user-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/$ELASTICACHEPOLICY --user-name $TEMP_AWS_USERNAME
```

BUCKETPOLICY=temp-migration-bucket

Create s3 bucket policy for created bucket
```
aws iam create-policy --policy-name $BUCKETPOLICY --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["S3:PutObject","S3:ListBucket","S3:DeleteBucket","S3:CreateBucket","S3:PutBucketPolicy","S3:GetObject","S3:DeleteObject","S3:PutPublicAccessBlock"],"Resource":["arn:aws:s3:::'$BUCKETNAME'","arn:aws:s3:::'$BUCKETNAME'/*"]}]}'

```

Add the bucket policy to the user.

```
aws iam attach-user-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/$BUCKETPOLICY --user-name $TEMP_AWS_USERNAME
```

Create the access keys
```
aws iam create-access-key --user-name $TEMP_AWS_USERNAME
```

Make a note of the access key id for deletion later

Output should be provided to the user who will complete the migration.
