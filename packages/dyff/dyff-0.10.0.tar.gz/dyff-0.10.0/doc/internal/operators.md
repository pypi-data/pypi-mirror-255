# Kafka

## Install Strimzi Kafka operator via Helm

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

# TODO: Install via Operator Lifecycle Management operator

NOTE: OLM is not working out on GKE Autopilot at the moment. I believe this is due to an issue in OLM (see: https://github.com/operator-framework/operator-lifecycle-manager/issues/2976). I think we should try to use OLM on future deployments, but for now we've had to use the Helm method described above.

We're going to try using OperatorHub.io to manage third-party k8s operators. This requires the Operator Lifecycle Management (OLM) operator to be installed in the cluster.

## Install Operator SDK Locally

See: https://sdk.operatorframework.io/docs/installation/

```bash
% brew install operator-sdk
```

Alternative (See: "Install" button at https://operatorhub.io/operator/strimzi-kafka-operator):

```bash
% curl -sL https://github.com/operator-framework/operator-lifecycle-manager/releases/download/v0.24.0/install.sh | bash -s v0.24.0
```

## Install OLM

See: https://olm.operatorframework.io/docs/getting-started/

This timed out for me on the first attempt with the default timeout of 2m, probably due to GKE Autopilot node provisioning delay. You can set the timeout to a larger number as shown here.

```bash
% operator-sdk olm install --timeout 30m
I0610 21:29:19.748652   13890 request.go:690] Waited for 1.048937292s due to client-side throttling, not priority and fairness, request: GET:https://104.154.52.38/apis/networking.gke.io/v1alpha1?timeout=32s
INFO[0001] Fetching CRDs for version "latest"
INFO[0001] Fetching resources for resolved version "latest"
I0610 21:29:29.794619   13890 request.go:690] Waited for 1.701298375s due to client-side throttling, not priority and fairness, request: GET:https://104.154.52.38/apis/batch/v1?timeout=32s
INFO[0014] Creating CRDs and resources
INFO[0014]   Creating CustomResourceDefinition "catalogsources.operators.coreos.com"
INFO[0015]   Creating CustomResourceDefinition "clusterserviceversions.operators.coreos.com"
INFO[0016]   Creating CustomResourceDefinition "installplans.operators.coreos.com"
INFO[0017]   Creating CustomResourceDefinition "olmconfigs.operators.coreos.com"
INFO[0017]   Creating CustomResourceDefinition "operatorconditions.operators.coreos.com"
INFO[0017]   Creating CustomResourceDefinition "operatorgroups.operators.coreos.com"
INFO[0017]   Creating CustomResourceDefinition "operators.operators.coreos.com"
INFO[0017]   Creating CustomResourceDefinition "subscriptions.operators.coreos.com"
INFO[0018]   Creating Namespace "olm"
INFO[0018]   Creating Namespace "operators"
INFO[0018]   Creating ServiceAccount "olm/olm-operator-serviceaccount"
INFO[0018]   Creating ClusterRole "system:controller:operator-lifecycle-manager"
INFO[0018]   Creating ClusterRoleBinding "olm-operator-binding-olm"
INFO[0018]   Creating OLMConfig "cluster"
INFO[0020]   Creating Deployment "olm/olm-operator"
INFO[0020]   Creating Deployment "olm/catalog-operator"
INFO[0020]   Creating ClusterRole "aggregate-olm-edit"
INFO[0020]   Creating ClusterRole "aggregate-olm-view"
INFO[0020]   Creating OperatorGroup "operators/global-operators"
INFO[0020]   Creating OperatorGroup "olm/olm-operators"
INFO[0020]   Creating ClusterServiceVersion "olm/packageserver"
INFO[0021]   Creating CatalogSource "olm/operatorhubio-catalog"
INFO[0021] Waiting for deployment/olm-operator rollout to complete
INFO[0021]   Waiting for Deployment "olm/olm-operator" to rollout: 0 of 1 updated replicas are available
INFO[0027]   Deployment "olm/olm-operator" successfully rolled out
INFO[0027] Waiting for deployment/catalog-operator rollout to complete
INFO[0027]   Deployment "olm/catalog-operator" successfully rolled out
INFO[0027] Waiting for deployment/packageserver rollout to complete
INFO[0027]   Waiting for Deployment "olm/packageserver" to appear
INFO[0031]   Waiting for Deployment "olm/packageserver" to rollout: 0 of 2 updated replicas are available
INFO[0041]   Deployment "olm/packageserver" successfully rolled out
INFO[0044] Successfully installed OLM version "latest"

NAME                                            NAMESPACE    KIND                        STATUS
catalogsources.operators.coreos.com                          CustomResourceDefinition    Installed
clusterserviceversions.operators.coreos.com                  CustomResourceDefinition    Installed
installplans.operators.coreos.com                            CustomResourceDefinition    Installed
olmconfigs.operators.coreos.com                              CustomResourceDefinition    Installed
operatorconditions.operators.coreos.com                      CustomResourceDefinition    Installed
operatorgroups.operators.coreos.com                          CustomResourceDefinition    Installed
operators.operators.coreos.com                               CustomResourceDefinition    Installed
subscriptions.operators.coreos.com                           CustomResourceDefinition    Installed
olm                                                          Namespace                   Installed
operators                                                    Namespace                   Installed
olm-operator-serviceaccount                     olm          ServiceAccount              Installed
system:controller:operator-lifecycle-manager                 ClusterRole                 Installed
olm-operator-binding-olm                                     ClusterRoleBinding          Installed
cluster                                                      OLMConfig                   Installed
olm-operator                                    olm          Deployment                  Installed
catalog-operator                                olm          Deployment                  Installed
aggregate-olm-edit                                           ClusterRole                 Installed
aggregate-olm-view                                           ClusterRole                 Installed
global-operators                                operators    OperatorGroup               Installed
olm-operators                                   olm          OperatorGroup               Installed
packageserver                                   olm          ClusterServiceVersion       Installed
operatorhubio-catalog                           olm          CatalogSource               Installed
```

# Kafka

## Install Strimzi operator from OperatorHub

See: "Install" button at https://operatorhub.io/operator/strimzi-kafka-operator

```bash
% kubectl create -f https://operatorhub.io/install/strimzi-kafka-operator.yaml
```
