# Create MITM instance

This SOP covers creation of a pod on kubernetes cluster where all the required steps should be performed on to enable logging and visibility.

## Create migration workspace namespace
```
cat << EOF | oc create -f -
kind: Namespace
apiVersion: v1
metadata:
  name: migration-workspace
EOF
```

## Oc login to the namespace
```
oc project migration-workspace
```

## Create Pod with an image that contains all the required tools to perform the migration

```                                                          
cat << EOF | oc create -f -         
apiVersion: apps/v1
kind: Deployment
metadata:
  name: migration-deployment
spec:
  selector:
    matchLabels:
      app: migration-deployment
  template:
    metadata:
        labels:
            app: migration-deployment
    spec:
        containers:
            - resources: {}
              stdin: true
              name: migration-container
              env:
               - name: AWS_CONFIG_FILE
                 value: /home/migration/.config
               - name: AWS_PAGER
                 value: ""
               - name: AWS_SHARED_CREDENTIALS_FILE
                 value: /home/migration/.credentials
               - name: KUBECONFIG
                 value: /home/migration/.kube/config
              command:
                - /bin/sh
              ports:
                - containerPort: 80
                  protocol: TCP
              imagePullPolicy: Always
              tty: true
              image: 'quay.io/mstoklus/migration-tool:v0.0.1'
EOF
```