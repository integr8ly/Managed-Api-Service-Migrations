# Pull from S3 bucket
This SOP covers on how to pull from S3 bucket

## Pre-requisites
- AWS CLI
- AWS logged in to the desired S3 AWS account

## Envs
```
BUCKET_NAME=<name of the source bucket>
```

## Steps
- Fetch the bucket contents to confirm that all required data is there:
```
aws s3 ls s3://$BUCKET_NAME 
```
- Fetch the bucket contents:

<b> For specific file in the bucket </b>
```
aws s3 cp s3://$BUCKET_NAME/<file_name> ./<file_name>
```
<b> Sync all the files from bucket to local folder </b>
```
aws s3 sync s3://$BUCKET_NAME ./
```

# Push to S3 bucket

<b> Note: Ensure bucket policies are configured </b>

<b> For specific file going in to the bucket </b>
```
aws s3 cp ./<file_name> s3://$BUCKET_NAME/<file_name>
```
<b> Sync all the files from local folder to bucket </b>
```
aws s3 sync <files_dir> s3://$BUCKET_NAME
```