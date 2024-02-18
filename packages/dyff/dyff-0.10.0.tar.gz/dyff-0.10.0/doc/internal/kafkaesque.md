# Install Strimzi Kafka operator via Helm

See: https://strimzi.io/docs/operators/latest/deploying.html#deploying-cluster-operator-helm-chart-str

```bash
% helm repo add strimzi https://strimzi.io/charts/
"strimzi" has been added to your repositories
% helm repo update
```

```bash
% helm install strimzi-operator strimzi/strimzi-kafka-operator
W0615 12:08:33.321690   32588 warnings.go:70] Autopilot increased resource requests for Deployment default/strimzi-cluster-operator to meet requirements. See http://g.co/gke/autopilot-resources
NAME: strimzi-operator
LAST DEPLOYED: Thu Jun 15 12:08:28 2023
NAMESPACE: default
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Thank you for installing strimzi-kafka-operator-0.35.1

To create a Kafka cluster refer to the following documentation.

https://strimzi.io/docs/operators/latest/deploying.html#deploying-cluster-operator-helm-chart-str
```

TODO: We should probably install the operator in a non-default namespace.

## Caveats:

### GKE default storage class `standard-rwo` uses SSDs

To get HDDs, you need to use the `standard` storage class.

### Must remove PV finalizer manually to delete them

See: https://github.com/kubernetes/kubernetes/issues/69697#issuecomment-448541618

```bash
kubectl patch pv pvc-1d6f435d-accf-4eec-b8b6-5f4bdfdf13ed -p '{"metadata":{"finalizers":null}}'
```

You must also delete the associated PVCs.

# Deploy Kafka cluster

```bash
% kubectl apply -f k8s/deploy/kafka/kafka.yaml
```

# Restructure repo to accommodate Java code

So, we're going to have to use Java/Scala for the Kafka Streams library `:(`

To support that in the repo, we're going to modify the structure to replace the `src/` directory with `python/` and `java/`. We need to modify a bunch of paths:

```bash
% grep -n -r --exclude-dir=.git --exclude-dir=doc --exclude-dir=test --exclude-dir=.mypy_cache --exclude='*__pycache__*' --exclude='*.egg-info*' 'src' .
./docker/Dockerfile-run-report:7:COPY audit/src/ /alignment-labs/audit/src/
./docker/Dockerfile-run-report:9:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-run-report:11:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-run-report:13:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-fetch-data:21:COPY src/ /alignment-labs/dyff/
./docker/Dockerfile-ingest-dataset:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-ingest-dataset:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-dyff-api-server:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-dyff-api-server:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-dyff-api-server:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-api-server-proxy:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-api-server-proxy:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-api-server-proxy:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-report-operator:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-report-operator:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-report-operator:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-report-operator:19:ENTRYPOINT [ "kopf", "run", "src/alignmentlabs/dyff/k8s/controllers/report.py" ]
./docker/Dockerfile-evaluation-client:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-evaluation-client:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-evaluation-client:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-build-bentoml-service:14:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-build-bentoml-service:17:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-build-bentoml-service:19:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-prepare-inference-task:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-prepare-inference-task:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-inference-service-operator:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-inference-service-operator:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-inference-service-operator:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-inference-service-operator:19:ENTRYPOINT [ "kopf", "run", "src/alignmentlabs/dyff/k8s/controllers/inference_service.py" ]
./docker/Dockerfile-model-operator:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-model-operator:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-model-operator:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-model-operator:19:ENTRYPOINT [ "kopf", "run", "src/alignmentlabs/dyff/k8s/controllers/model.py" ]
./docker/Dockerfile-verify-evaluation-output:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-verify-evaluation-output:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-verify-evaluation-output:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-benchmark:13:COPY src/ /alignment-labs/dyff/
./docker/Dockerfile-audit-operator:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-audit-operator:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-audit-operator:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-audit-operator:19:ENTRYPOINT [ "kopf", "run", "src/alignmentlabs/dyff/k8s/controllers/audit.py" ]
./docker/Dockerfile-orchestrator:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-orchestrator:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-orchestrator:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-evaluation-operator:6:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-evaluation-operator:9:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-evaluation-operator:11:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-evaluation-operator:19:ENTRYPOINT [ "kopf", "run", "src/alignmentlabs/dyff/k8s/controllers/evaluation.py" ]
./docker/Dockerfile-fetch-model:12:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-fetch-model:15:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-fetch-model:17:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-run-audit:14:COPY audit/src/ /alignment-labs/audit/src/
./docker/Dockerfile-run-audit:16:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-run-audit:18:COPY dyff/src/ /alignment-labs/dyff/src/
./docker/Dockerfile-run-audit:20:COPY models/src/ /alignment-labs/models/src/
./docker/Dockerfile-run-jupyterbook:24:COPY audit/src/ ${INSTALLDIR}/audit/src/
./docker/Dockerfile-run-jupyterbook:26:COPY core/src/ ${INSTALLDIR}/core/src/
./docker/Dockerfile-run-jupyterbook:28:COPY dyff/src/ ${INSTALLDIR}/dyff/src/
./docker/Dockerfile-run-jupyterbook:30:COPY models/src/ ${INSTALLDIR}/models/src/
./docker/Dockerfile-clone-audit-procedure:7:COPY core/src/ /alignment-labs/core/src/
./docker/Dockerfile-clone-audit-procedure:9:COPY dyff/src/ /alignment-labs/dyff/src/
./setup.py:45:  packages=find_namespace_packages(where="src"),
./setup.py:46:  package_dir={"": "src"},
```

Happily, most of the necessary changes are in the Dockerfiles:

```bash
% sed -i '.bak' 's/dyff\/src/dyff\/python/g' docker/*
```

Then, if you're happy with the result:

```bash
% rm docker/*.bak
```

Finally, change `setup.py` package search paths as appropriate.

# Kafka CLI for development

## Ephemeral shell

```bash
% kubectl run kafka-cli -it --rm --image=us-central1-docker.pkg.dev/dyff-354017/dyff-system/alignmentlabs/dyff/kafka-cli --command -- bash -il
```

## Deploy

```bash
% kubectl apply -f k8s/deploy/kafka/cli.yaml
```

## Connect

```bash
% kubectl exec -it kafka-cli -- bash
```

## Commands

### Consumer

```bash
root@kafka-cli:/opt/kafka_2.13-3.4.0# bin/kafka-console-consumer.sh --bootstrap-server dyff-kafka-bootstrap:9092 --topic test.workflows.state --from-beginning
```

### Producer

TODO

# Deploy KStreams Apps

## Workflows Aggregator

### `workflows-aggregator` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/api-server.yaml
serviceaccount/api-server created
role.rbac.authorization.k8s.io/api-server-role-namespaced created
rolebinding.rbac.authorization.k8s.io/api-server-rolebinding-namespaced created

$ gcloud iam service-accounts create api-server --project=dyff-354017
Created service account [api-server].
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User
- Storage Admin

```bash
$ gcloud iam service-accounts add-iam-policy-binding api-server@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/api-server]"
Updated IAM policy for serviceAccount [api-server@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/api-server]
  role: roles/iam.workloadIdentityUser
etag: BwX3blo76s4=
version: 1

$ kubectl annotate serviceaccount api-server --namespace default iam.gke.io/gcp-service-account=api-server@dyff-354017.iam.gserviceaccount.com
serviceaccount/api-server annotated
```

## GCloud Datastore Kafka Connector (TEMPORARY)

### Service account `datastore-user`

```bash
% kubectl create serviceaccount datastore-user --namespace default
serviceaccount/datastore-user created
% gcloud iam service-accounts create datastore-user --project=dyff-354017
Created service account [datastore-user].
```

(Setup roles in console)

- Cloud Datastore User

```bash
% gcloud iam service-accounts add-iam-policy-binding datastore-user@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/datastore-user]"
Updated IAM policy for serviceAccount [datastore-user@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/datastore-user]
  role: roles/iam.workloadIdentityUser
etag: BwYAUdznQqs=
version: 1
% kubectl annotate serviceaccount datastore-user --namespace default iam.gke.io/gcp-service-account=datastore-user@dyff-354017.iam.gserviceaccount.com
serviceaccount/datastore-user annotated
```

### Deploy connector

```bash
% gcloud builds submit --config dyff/gcloud/build/gcloud-datastore-kafka-connector.yaml .
% kubectl apply -f dyff/k8s/deploy/gcloud-datastore-kafka-connector.yaml
```

# Workflows informer

This component monitors k8s resource for status changes and propagates them to the events topic.

## `workflows-informer` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f apps/workflows_informer/deploy/rbac.yaml
serviceaccount/workflows-informer created
clusterrole.rbac.authorization.k8s.io/workflows-informer created
clusterrolebinding.rbac.authorization.k8s.io/workflows-informer created

$ gcloud iam service-accounts create workflows-informer --project=dyff-354017
Created service account [workflows-informer].
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke

```bash
$ gcloud iam service-accounts add-iam-policy-binding workflows-informer@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/workflows-informer]"
Updated IAM policy for serviceAccount [workflows-informer@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/workflows-informer]
  role: roles/iam.workloadIdentityUser
etag: BwYJrWSw3Tg=
version: 1

$ kubectl annotate serviceaccount workflows-informer --namespace default iam.gke.io/gcp-service-account=workflows-informer@dyff-354017.iam.gserviceaccount.com
serviceaccount/workflows-informer annotated
```

# Scala VSCode plugins

## Notes for Mac

To make the "Metals" language plugin work, you need to point its Java Home setting to:

```bash
% /usr/libexec/java_home
/opt/homebrew/Cellar/openjdk/20.0.1/libexec/openjdk.jdk/Contents/Home
```

You also need to open a _separate VSCode window_ pointed at the `java/` subdirectory, because Metals can't handle the `pom.xml` file not being in a workspace root directory. Adding the subdirectory in an existing workspace that already contains the enclosing `dyff` directory doesn't work.

I filed a feature request here: https://github.com/scalameta/metals-feature-requests/issues/346

# Kafka Troubleshooting

## Restarting Kafka components

The Strimzi operator has its own CR called `StrimziPodSet` that is similar to a `Deployment` / `StatefulSet`. You can trigger a restart of Zookeeper or the Kafka broker by deleting the corresponding `StrimziPodSet`.

## Zookeeper stuck in CrashLoop

We observed a failure where Zookeeper replicas fail to establish connections amongst themselves, leading to failed ready probes and crashing in a loop that never resolves itself. This occurred following an apparently spontaneous failure of the ZK pods.

We added the following to `k8s/deploy/kafka/kafka.yaml` while troubleshooting this:

```yaml
spec:
  ...
  zookeeper:
    ...
    # I suspect that ZK can get into a crash loop because of startup latency
    # This is an attempt to mitigate that. Note it will extend restart downtime.
    readinessProbe:
      initialDelaySeconds: 60
      timeoutSeconds: 30
    livenessProbe:
      initialDelaySeconds: 60
      timeoutSeconds: 30
    # Per: https://github.com/strimzi/strimzi-kafka-operator/issues/3692#issuecomment-696952238
    # Not sure whether this was actually necessary
    jvmOptions:
      javaSystemProperties:
        - name: zookeeper.ssl.hostnameVerification
          value: "false"
        - name: zookeeper.ssl.quorum.hostnameVerification
          value: "false"
```

This change, in combination with deleting the Zookeeper `StimziPodSet`, resolved the problem. It's not clear whether the config changes were necessary, or whether restarting ZK would have been enough. There were some `Connection refused` errors in ZK pods that suggested an authentication problem, which was the motivation for disable hostname verification. Also, giving more time for the ready / live probes is intended to reduce the chance of entering a crash loop if the ZK pods are slow to start for some reason.
