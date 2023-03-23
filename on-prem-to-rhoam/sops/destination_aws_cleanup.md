# Steps to clean-up pre-reqs for destination AWS Account

## Cleanup the user and permission

export TEMP_AWS_USERNAME=temp-migration-user
export AWS_ACCESS_KEY=<noted from pre-requisite steps>
export BUCKETNAME=<bucket name from pre-requisite steps>


Delete the access key but retain the users and permissions
```
aws iam delete-access-key --access-key-id $ACCESS_KEY_ID --user-name $TEMP_AWS_USERNAME
```

ELASTICACHEPOLICY=temp-migration-elasticache
BUCKETPOLICY=temp-migration-bucket

Detach and Delete the policy
```
aws iam detach-user-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/$ELASTICACHEPOLICY --user-name $TEMP_AWS_USERNAME && \
aws iam delete-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/$ELASTICACHEPOLICY && \
aws iam detach-user-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/$BUCKETPOLICY --user-name $TEMP_AWS_USERNAME && \
aws iam delete-policy --policy-arn arn:aws:iam::$AWS_ACCOUNT:policy/$BUCKETPOLICY
```

Delete the user
```
aws iam delete-user --user-name $TEMP_AWS_USERNAME
```

Delete s3 bucket and objects

Remove object:
```
aws s3 rm s3://$BUCKETNAME --recursive
```

Delete bucket
```
aws s3api delete-bucket --bucket $BUCKETNAME
```