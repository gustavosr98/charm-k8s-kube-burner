# charm-k8s-kube-burner

## Developing

Requires
- Python
- Charmcraft
- LXD
- Juju
- Kubernetes

Deploy benchmark charmed kubernetes target

```
juju deploy charmed-kubernetes --overlay .juju/overlays/k8s-lma-overlay.yaml --debug
```

Create and activate a virtualenv with the development requirements:

```
virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

Deploy charm on an existing k8s juju model

```
charmcraft pack
juju deploy ./charm-k8s-kube-burner_ubuntu-20.04-amd64.charm --resource kube-burner-image=quay.io/cloud-bulldozer/kube-burner:latest
```

### Useful commands

Kubernetes
```
# Switch namespace
kubectl config set-context --current --namespace=<namespace>

# Get logs
kubectl logs charm-k8s-kube-burner-0 --all-containers

# List containers of a pod
kubectl get pods charm-k8s-kube-burner-0 -o jsonpath='{.spec.containers[*].name}'

# Get a shell of the charm workload container
kubectl exec charm-k8s-kube-burner-0 --container kube-burner --stdin --tty -- /bin/bash

kubectl cp /usr/bin/nano charm-k8s-kube-burner/0:/usr/bin/nano --container kube-burner
```

Charm development
```
# Send nano to charm agent container
juju scp /usr/bin/nano charm-k8s-kube-burner/0:/usr/bin/nano

# Get a shell of the charm agent
juju ssh charm-k8s-kube-burner/0

# Edit code inside of charm agent 
nano /var/lib/juju/agents/unit-charm-k8s-kube-burner-0/charm/src/charm.py
```

## Code overview

TEMPLATE-TODO: 
One of the most important things a consumer of your charm (or library)
needs to know is what set of functionality it provides. Which categories
does it fit into? Which events do you listen to? Which libraries do you
consume? Which ones do you export and how are they used?

## Intended use case

TEMPLATE-TODO:
Why were these decisions made? What's the scope of your charm?

## Roadmap

If this Charm doesn't fulfill all of the initial functionality you were
hoping for or planning on, please add a Roadmap or TODO here

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

    ./run_tests
