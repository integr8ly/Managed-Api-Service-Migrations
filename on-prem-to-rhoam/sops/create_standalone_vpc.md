# Create standalone VPC and associated AWS network components

This SOP covers the AWS commands needed to create a standalone VPC, subnets, route table, security group, and peering connection. It also covers the prerequisites needed to install a RDS and ElastiCache instance in the standalone VPC 

## Prerequisites
- AWS CLI login
- OpenShift-created cluster VPC to establish a peering connection with

## Create and configure the VPC
### Create the standalone VPC
```
STANDALONE_VPC_ID=$(aws ec2 create-vpc \
    --cidr-block 10.2.0.0/26 \
    --tag-specification 'ResourceType=vpc,Tags=[{Key=Name,Value=StandaloneVPC}]' \
    --query Vpc.VpcId --output text)
```
### Enable DNS hostnames and DNS resolution on standalone VPC
```
aws ec2 modify-vpc-attribute \
    --vpc-id $STANDALONE_VPC_ID \
    --enable-dns-hostnames "{\"Value\":true}"
```
```
aws ec2 modify-vpc-attribute \
    --vpc-id $STANDALONE_VPC_ID \
    --enable-dns-support "{\"Value\":true}"
```

## Create 2 private subnets
Note: Make sure to replace the <region-of-standalone-vpc> with the region the standalone VPC is in
```
REGION=<region-of-standalone-vpc>
```
```
STANDALONE_SUBNET_1_ID=$(aws ec2 create-subnet \
    --vpc-id $STANDALONE_VPC_ID \
    --cidr-block 10.2.0.0/27 \
    --availability-zone ${REGION}a \
    --tag-specification 'ResourceType=subnet,Tags=[{Key=Name,Value=StandaloneVPC-PrivateSubnet1}]' \
    --query 'Subnet.SubnetId' --output text)
```
```
STANDALONE_SUBNET_2_ID=$(aws ec2 create-subnet \
    --vpc-id $STANDALONE_VPC_ID \
    --cidr-block 10.2.0.32/27 \
    --availability-zone ${REGION}b \
    --tag-specification 'ResourceType=subnet,Tags=[{Key=Name,Value=StandaloneVPC-PrivateSubnet2}]' \
    --query 'Subnet.SubnetId' --output text)
```

## Create and configure the security group
### Create the security group
```
STANDALONE_SECURITY_GROUP_ID=$(aws ec2 create-security-group \
    --group-name standalonesecuritygroup --description "security group for standalone VPC" \
    --vpc-id $STANDALONE_VPC_ID \
    --tag-specification 'ResourceType=security-group,Tags=[{Key=Name,Value=StandaloneVPC-SecurityGroup}]' \
    --query 'GroupId' --output text)
```
### Add inbound rule to security group
```
aws ec2 authorize-security-group-ingress \
    --group-id $STANDALONE_SECURITY_GROUP_ID --protocol -1 \
    --cidr 10.0.0.0/16
```
Note: specifying `-1` for the protocol indicates the rule should be applied for all traffic

## Create and accept peering connection
### Create the peering connection
First get the ID of the cluster VPC which can be found using the `red-hat-managed` tag and assign the value to an environment variable
```
CLUSTER_VPC_ID=$(aws ec2 describe-vpcs \
    --filters Name=tag:red-hat-managed,Values=true \
    --query 'Vpcs[].VpcId[]' --output text)
```
Now create the peering connection
```
PEERING_CONNECTION_ID=$(aws ec2 create-vpc-peering-connection \
    --vpc-id $STANDALONE_VPC_ID \
    --peer-vpc-id $CLUSTER_VPC_ID \
    --query 'VpcPeeringConnection.VpcPeeringConnectionId' --output text)
```
### Accept the peering connection
```
aws ec2 accept-vpc-peering-connection \
    --vpc-peering-connection-id $PEERING_CONNECTION_ID
```

## Update route tables
### Update standalone VPC route table(s)
First get the ID(s) of the route table(s) associated with the standalone VPC
```
aws ec2 describe-route-tables --filters Name=vpc-id,Values=$STANDALONE_VPC_ID --query 'RouteTables[].RouteTableId' --output text
```
For each of the returned route tables, create a route linking cluster VPC and peering connection

Make sure to update the value of STANDALONE_RT_ID as needed for each of the returned route tables
```
STANDALONE_RT_ID=<cluster-route-table-id-from-output>
```
```
aws ec2 create-route --route-table-id $STANDALONE_RT_ID --destination-cidr-block 10.0.0.0/16 --vpc-peering-connection-id $PEERING_CONNECTION_ID
```

### Update cluster VPC route table(s)
First get the ID(s) of the route table(s) associated with the cluster VPC
```
aws ec2 describe-route-tables --filters Name=vpc-id,Values=$CLUSTER_VPC_ID --query 'RouteTables[].RouteTableId' --output text
```
For each of the returned route tables, create a route linking cluster VPC and peering connection

Make sure to update the value of CLUSTER_RT_ID as needed for each of the returned route tables
```
CLUSTER_RT_ID=<cluster-route-table-id-from-output>
```
```
aws ec2 create-route --route-table-id $CLUSTER_RT_ID --destination-cidr-block 10.2.0.0/26 --vpc-peering-connection-id $PEERING_CONNECTION_ID
```

## Create RDS subnet group
```
aws rds create-db-subnet-group \
    --db-subnet-group-name standalonesubnetgroup \
    --db-subnet-group-description "Subnet group created for standalone VPC" \
    --subnet-ids '["'${STANDALONE_SUBNET_1_ID}'","'${STANDALONE_SUBNET_2_ID}'"]'
```

## Create ElastiCache subnet group
```
aws elasticache create-cache-subnet-group \
    --cache-subnet-group-name standalonesubnetgroup \
    --cache-subnet-group-description "Subnet group created for standalone VPC" \
    --subnet-ids '["'${STANDALONE_SUBNET_1_ID}'","'${STANDALONE_SUBNET_2_ID}'"]'
```