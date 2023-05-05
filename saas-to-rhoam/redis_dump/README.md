# redis dump

**WARNING:** These scripts are proof of concept and not complete.
Please refer [MGDAPI-5322](https://issues.redhat.com/browse/MGDAPI-5322) for more information.

This set of scripts is used to pull metrics from the 3scale redis and migrate them to a new instances.

The scripts are design to be run as a pod on cluster.
To run locally there are a number environment variables that need to be set. 

The best way to run them locally is by using podman.

## Running Locally

### Target Redis
There needs to be access the target redis locally if using the default configuration.
This can be done by setting up a port forward using `kubectl`.
Personal I use `k9s` to manage this work but the command for `kubectl` would be something like: `kubectl port-forward <pod-name> <local port>:<remote port>`.
The default configuration assumes the port to be `6379`.

### Build the image
From the project root run:

```shell
podman build -t redis_dump:latest .
```

### Pull script
Start the script by calling.
```shell
podman kube play --net=host pullfile.yaml
```

Check pod logs for completion.
```shell
podman pod logs -f foobar
```

Copy the json file form the container.
```shell
podman cp foobar-container:/app/data.json data.json
```

Clean up the pods once finished.
```shell
podman kube down pullfile.yaml
```

### Push script
Start the script by calling.
```shell
podman kube play --net=host pushfile.yaml
```

Check pod logs for completion.
```shell
podman pod logs -f foobar
```

Clean up the pods once finished.
```shell
podman kube down pullfile.yaml
```

### Seed Script
The seed script is design to add volume to a redis instance for checking performances of other scripts.
It is a test script and does not produce a 3scale usable redis instances. 

A local redis instance can be configured using the following.
The volume is required if doing a large number of entries as the default container storage will fill.
```shell
podman volume create redisVol
podman run --rm --name redis-server -p 6379:6379 -v redisVol:/data:z redis
```

Set up the pod:
```shell
podman kube play --net=host --start=false seedfile.yaml
```

Added the seed file.
```shell
podman cp seed.json foobar-container:/app/seed.json
```

Start the pod.
```shell
podman pod start foobar
```

Check logs for completed message.
```shell
podman pod logs -f foobar
```

Clean the pod up once finished.
```shell
podman kube down  seedfile.yaml
```
