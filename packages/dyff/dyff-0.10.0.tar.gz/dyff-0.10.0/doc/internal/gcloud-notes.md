# gcloud Resources

## Project Info

PROJECT_ID = dyff-354017

LOCATION = us-central1

GKE cluster: mvp-1

MVP Test Account UUID: 8fef979f-75c0-4b08-99fa-326ba33596f8

## Google Storage buckets:

- `datasets`
  - `gs://alignmentlabs-datasets-a1d118148ee7550e`
- `models`
  - `gs://alignmentlabs-models-b10436edfc47d3c1`
- `inferenceservices`
  - `gs://alignmentlabs-inferenceservices-3ac808007f2667b9`
- `outputs`
  - `gs://alignmentlabs-outputs-6f70a71477535211`
- `rawdata`
  - `gs://alignmentlabs-rawdata-14a802b4b854421f`
  - FIXME: accidentally created as multi-region; need to migrate
- `reports`
  - `gs://alignmentlabs-reports-c1caea9ce5861c9e`
  - Note: This one uses a random hash key. That will be standard practice going forward.

## GKE Service Accounts

- `model-runner`
  - Storage Object Viewer: `-datasets-` and `-models-`
  - Storage Object Creator: `-outputs-`
  - `model-runner@dyff-354017.iam.gserviceaccount.com`
- `data-fetcher`
  - Storage Object Viewer: `-rawdata-`
  - Storage Object Creator: `-rawdata-`
  - `data-fetcher@dyff-354017.iam.gserviceaccount.com`

## Artifact Registries

- `dyff-system`
  - `us-central1-docker.pkg.dev/dyff-354017/dyff-system/`
  - Docker repository
- `dyff-models`
  - `us-central1-docker.pkg.dev/dyff-354017/dyff-models/`
  - Docker repository

# Setup Walkthroughs

## Artifact Registry

```bash
gcloud services enable artifactregistry.googleapis.com
gcloud artifacts repositories create dyff-system --repository-format=docker --location=us-central1 --description="dyff system images"
gcloud artifacts repositories create dyff-models --repository-format=docker --location=us-central1 --description="upload for model images"
```

## Cloud build the `benchmark` image

```bash
gcloud builds submit --config gcloud/build/benchmark.yaml .
```

Note that the cloudbuild `.yaml` file must end with a blank line or it will "fail to parse as a dictionary"

### Inspect the Docker repository

```bash
gcloud artifacts docker images list us-central1-docker.pkg.dev/dyff-354017/dyff-system
```

## GCS Buckets

Bucket names must be _globally unique_ and are publicly visible.

**I have changed my mind about the naming convention. Going forward, the hex-suffix will be a random hex token of length 16 characters (8 bytes), such as generated in Python by `secrets.hex_token(8)`.**

~~I've adopted the following naming convention:~~

```bash
$ echo "alignmentlabs-datasets-$(echo -n 'alignmentlabs-datasets-public-0' | shasum -a 256 | head -c 16)"
alignmentlabs-datasets-a1d118148ee7550e
```

That is, `alignmentlabs-<category>-<first 16 hex chars of sha256 hash of full identifier>`. Make sure not to include a newline in the thing-being-hashed when doing it on the command line.

(I think it's prudent not to advertise their exact contents publicly because some of them will be sensitive)

### Create bucket: `alignmentlabs-datasets-public-0`:

```bash
$ echo "alignmentlabs-datasets-$(echo -n 'alignmentlabs-datasets-public-0' | shasum -a 256 | head -c 16)"
alignmentlabs-datasets-a1d118148ee7550e
$ gsutil mb -p dyff-354017 -c standard -l us-central1 -b on gs://alignmentlabs-datasets-a1d118148ee7550e
```

### Example of renaming a bucket:

```bash
$ gcloud alpha storage cp --recursive gs://alignmentlabs-datasets-08cd5f0c067369c8/* gs://alignmentlabs-datasets-a1d118148ee7550e
$ gcloud alpha storage rm --recursive gs://alignmentlabs-datasets-08cd5f0c067369c8
```

### Upload the "ingested" `imagenet-c-brightness-1` dataset:

```bash
$ gsutil cp -r imagenet-c-brightness-1 gs://alignmentlabs-datasets-a1d118148ee7550e/
```

### Create bucket: `alignmentlabs-models-public-0`

```bash
$ echo "alignmentlabs-models-$(echo -n 'alignmentlabs-models-public-0' | shasum -a 256 | head -c 16)"
alignmentlabs-models-b10436edfc47d3c1
$ gsutil mb -p dyff-354017 -c standard -l us-central1 -b on gs://alignmentlabs-models-b10436edfc47d3c1
```

### Upload the `resnet-50` model:

```bash
$ gsutil cp -r resnet-50 gs://alignmentlabs-models-b10436edfc47d3c1/
```

### Create bucket: `alignmentlabs-outputs-temp-0`

```bash
echo "alignmentlabs-outputs-$(echo -n 'alignmentlabs-outputs-temp-0' | shasum -a 256 | head -c 16)"
alignmentlabs-outputs-6f70a71477535211
$ gsutil mb -p dyff-354017 -c standard -l us-central1 -b on gs://alignmentlabs-outputs-6f70a71477535211
```

## Create GKE Workload Identity

See: https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity

### Create `model-runner` k8s service account:

```bash
$ kubectl create serviceaccount model-runner --namespace default
serviceaccount/model-runner created
```

### Create `model-runner` gcloud IAM service account:

```bash
$ gcloud iam service-accounts create model-runner --project=dyff-354017
Created service account [model-runner].
```

### Grant read access to datasets bucket:

I did this through the console because I couldn't figure out how to set up the access conditions through the CLI.

- TODO: figure out how to automate on the command line

See: https://tsmx.net/accessing-a-single-bucket-in-gcs/

- Copy the service account email address (Service Accounts tab)
- Add the service account email as a principal (IAM tab)
- Role: Storage Object Viewer
- Conditions: `is-datasets-bucket`
  - Condition type: Name
  - Operator: Starts with
  - Value: `projects/_/buckets/alignmentlabs-datasets-`

Similar setup for reading `-models-` buckets and for writing `-outputs-` buckets. Note that `write` permission does not grant `delete` (overwrite) permission, which I think is a good thing.

### Create IAM policy binding between gcloud service account and k8s service account

```bash
$ gcloud iam service-accounts add-iam-policy-binding model-runner@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/model-runner]"
Updated IAM policy for serviceAccount [model-runner@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/model-runner]
  role: roles/iam.workloadIdentityUser
etag: BwXijUEUIXQ=
version: 1
```

Annotate the Kubernetes service account with the email address of the IAM service account.

```bash
$ kubectl annotate serviceaccount model-runner --namespace default iam.gke.io/gcp-service-account=model-runner@dyff-354017.iam.gserviceaccount.com
serviceaccount/model-runner annotated
```

### Testing:

```bash
$ kubectl apply -f gcloud/k8s/workload-identity-test.yaml
Warning: Autopilot set default resource requests for Pod default/workload-identity-test, as resource requests were not specified. See http://g.co/gke/autopilot-defaults.
pod/workload-identity-test created
```

(Wait for startup)

```bash
$ kubectl exec -it gcloud/k8s/workload-identity-test --namespace default -- /bin/bash
```

```bash
$ curl -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/service-accounts/
default/
model-runner@dyff-354017.iam.gserviceaccount.com/
```

```bash
$ gsutil cp gs://alignmentlabs-datasets-08cd5f0c067369c8/imagenet-c-brightness-1/dataset_dict.json .
Copying gs://alignmentlabs-datasets-08cd5f0c067369c8/imagenet-c-brightness-1/dataset_dict.json...
/ [1 files][   20.0 B/   20.0 B]
Operation completed over 1 objects/20.0 B.
root@workload-identity-test:/work# ls
dataset_dict.json
```

### `data-fetcher` service account

```bash
$ kubectl create serviceaccount data-fetcher --namespace default
$ gcloud iam service-accounts create data-fetcher --project=dyff-354017
```

(Setup roles in console)

```bash
$ gcloud iam service-accounts add-iam-policy-binding data-fetcher@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/data-fetcher]"
$ kubectl annotate serviceaccount data-fetcher --namespace default iam.gke.io/gcp-service-account=data-fetcher@dyff-354017.iam.gserviceaccount.com
```

### `dataset-ingester` service account

```bash
$ kubectl create serviceaccount dataset-ingester --namespace default
$ gcloud iam service-accounts create dataset-ingester --project=dyff-354017
```

(Setup roles in console)

- Read: `alignmentlabs-rawdata-*`
- Read/Write: `alignmentlabs-datasets-*`

```bash
$ gcloud iam service-accounts add-iam-policy-binding dataset-ingester@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/dataset-ingester]"
$ kubectl annotate serviceaccount dataset-ingester --namespace default iam.gke.io/gcp-service-account=dataset-ingester@dyff-354017.iam.gserviceaccount.com
```

## Running Jobs

### Run `benchmark` job

```bash
kubectl apply -f gcloud/k8s/run-model-test.yaml
```

(The next morning)

```bash
$ kubectl get job
NAME        COMPLETIONS   DURATION   AGE
benchmark   1/1           7h7m       16h
```

### Run `fetch_data` job

Build

```bash
$ gcloud builds submit --config gcloud/build/fetch-data.yaml .
```

Run

```bash
$ python3 -m alignmentlabs.dyff.bin.gcloud.k8s.fetch_data_job --source="https://zenodo.org/api/records/2235448" --source_kind=zenodo --upload_bucket=alignmentlabs-rawdata-14a802b4b854421f --create
```

Cleanup

```bash
$ python3 -m alignmentlabs.dyff.bin.gcloud.k8s.fetch_data_job --source="https://zenodo.org/api/records/2235448" --source_kind=zenodo --upload_bucket=alignmentlabs-rawdata-14a802b4b854421f --delete
```

## Install the Evaluation operator

See: https://kopf.readthedocs.io/en/stable/ (especially Tutorial)

### Install CustomResourceDefinitions

```bash
$ kubectl apply -f k8s/crd/kopf-peering.yaml
customresourcedefinition.apiextensions.k8s.io/clusterkopfpeerings.kopf.dev created
customresourcedefinition.apiextensions.k8s.io/kopfpeerings.kopf.dev created
unable to recognize "k8s/crd/kopf-peering.yaml": no matches for kind "ClusterKopfPeering" in version "kopf.dev/v1"
unable to recognize "k8s/crd/kopf-peering.yaml": no matches for kind "KopfPeering" in version "kopf.dev/v1"

$ kubectl apply -f k8s/crd/kopf-peering.yaml
customresourcedefinition.apiextensions.k8s.io/clusterkopfpeerings.kopf.dev unchanged
customresourcedefinition.apiextensions.k8s.io/kopfpeerings.kopf.dev unchanged
clusterkopfpeering.kopf.dev/default created
kopfpeering.kopf.dev/default created

$ kubectl apply -f k8s/crd/evaluation.yaml
customresourcedefinition.apiextensions.k8s.io/evaluations.alignmentlabs.dyff created

$ kubectl apply -f k8s/crd/model.yaml
customresourcedefinition.apiextensions.k8s.io/models.alignmentlabs.dyff created

$ kubectl apply -f k8s/crd/inference-service.yaml
customresourcedefinition.apiextensions.k8s.io/inferenceservices.alignmentlabs.dyff created

$ kubectl apply -f k8s/crd/dataset.yaml
customresourcedefinition.apiextensions.k8s.io/datasets.alignmentlabs.dyff created
```

### `k8s-operator-evaluation` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/evaluation.yaml
serviceaccount/k8s-operator-evaluation created
clusterrole.rbac.authorization.k8s.io/k8s-operator-evaluation-role-cluster created
role.rbac.authorization.k8s.io/k8s-operator-evaluation-role-namespaced created
clusterrolebinding.rbac.authorization.k8s.io/k8s-operator-evaluation-rolebinding-cluster created
rolebinding.rbac.authorization.k8s.io/k8s-operator-evaluation-rolebinding-namespaced created

$ gcloud iam service-accounts create k8s-operator-evaluation --project=dyff-354017
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User

```bash
$ gcloud iam service-accounts add-iam-policy-binding k8s-operator-evaluation@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/k8s-operator-evaluation]"

$ kubectl annotate serviceaccount k8s-operator-evaluation --namespace default iam.gke.io/gcp-service-account=k8s-operator-evaluation@dyff-354017.iam.gserviceaccount.com
```

### `orchestrator` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/orchestrator.yaml
serviceaccount/orchestrator created
clusterrole.rbac.authorization.k8s.io/orchestrator-role-cluster created
role.rbac.authorization.k8s.io/orchestrator-role-namespaced created
clusterrolebinding.rbac.authorization.k8s.io/orchestrator-rolebinding-cluster created
rolebinding.rbac.authorization.k8s.io/orchestrator-rolebinding-namespaced created

$ gcloud iam service-accounts create orchestrator --project=dyff-354017
Created service account [orchestrator].
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User
  - Needs to change status Created -> Admitted

```bash
$ gcloud iam service-accounts add-iam-policy-binding orchestrator@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/orchestrator]"

$ kubectl annotate serviceaccount orchestrator --namespace default iam.gke.io/gcp-service-account=orchestrator@dyff-354017.iam.gserviceaccount.com
```

### `report-runner` service account

```bash
$ kubectl create serviceaccount report-runner --namespace default

$ gcloud iam service-accounts create report-runner --project=dyff-354017
```

(Setup roles in console)

- Storage Admin: `alignmentlabs-outputs-*`
- Cloud Datastore Viewer

```bash
$ gcloud iam service-accounts add-iam-policy-binding report-runner@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/report-runner]"

$ kubectl annotate serviceaccount report-runner --namespace default iam.gke.io/gcp-service-account=report-runner@dyff-354017.iam.gserviceaccount.com
```

### `evaluation-client` service account

```bash
$ kubectl create serviceaccount evaluation-client --namespace default

$ gcloud iam service-accounts create evaluation-client --project=dyff-354017
```

(Setup roles in console)

- Storage Object Viewer: `alignmentlabs-datasets-*`
- Storage Object Admin: `alignmentlabs-outputs-*`
- Cloud Datastore Viewer

```bash
$ gcloud iam service-accounts add-iam-policy-binding evaluation-client@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/evaluation-client]"

$ kubectl annotate serviceaccount evaluation-client --namespace default iam.gke.io/gcp-service-account=evaluation-client@dyff-354017.iam.gserviceaccount.com
```

### `k8s-operator-model` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/model.yaml
serviceaccount/k8s-operator-model created
clusterrole.rbac.authorization.k8s.io/k8s-operator-evaluation-role-cluster configured
role.rbac.authorization.k8s.io/k8s-operator-model-role-namespaced created
clusterrolebinding.rbac.authorization.k8s.io/k8s-operator-model-rolebinding-cluster created
rolebinding.rbac.authorization.k8s.io/k8s-operator-model-rolebinding-namespaced created

$ gcloud iam service-accounts create k8s-operator-model --project=dyff-354017
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User

```bash
$ gcloud iam service-accounts add-iam-policy-binding k8s-operator-model@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/k8s-operator-model]"

$ kubectl annotate serviceaccount k8s-operator-model --namespace default iam.gke.io/gcp-service-account=k8s-operator-model@dyff-354017.iam.gserviceaccount.com
```

### `model-fetcher` service account

```bash
$ kubectl create serviceaccount model-fetcher --namespace default

$ gcloud iam service-accounts create model-fetcher --project=dyff-354017
```

(Setup roles in console)

- Storage Object Admin: `alignmentlabs-models-*`

```bash
$ gcloud iam service-accounts add-iam-policy-binding model-fetcher@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/model-fetcher]"

$ kubectl annotate serviceaccount model-fetcher --namespace default iam.gke.io/gcp-service-account=model-fetcher@dyff-354017.iam.gserviceaccount.com
```

### `k8s-operator-inference-service` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/inference-service.yaml
serviceaccount/k8s-operator-inference-service created
clusterrole.rbac.authorization.k8s.io/k8s-operator-inference-service-role-cluster configured
role.rbac.authorization.k8s.io/k8s-operator-inference-service-role-namespaced created
clusterrolebinding.rbac.authorization.k8s.io/k8s-operator-inference-service-rolebinding-cluster created
rolebinding.rbac.authorization.k8s.io/k8s-operator-inference-service-rolebinding-namespaced created

$ gcloud iam service-accounts create k8s-operator-inference-service --project=dyff-354017
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User

```bash
$ gcloud iam service-accounts add-iam-policy-binding k8s-operator-inference-service@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/k8s-operator-inference-service]"

$ kubectl annotate serviceaccount k8s-operator-inference-service --namespace default iam.gke.io/gcp-service-account=k8s-operator-inference-service@dyff-354017.iam.gserviceaccount.com
```

### `inference-service-builder` service account

```bash
$ kubectl create serviceaccount inference-service-builder --namespace default

$ gcloud iam service-accounts create inference-service-builder --project=dyff-354017

$ gcloud artifacts repositories add-iam-policy-binding dyff-models --location us-central1 --role roles/artifactregistry.writer --member "serviceAccount:inference-service-builder@dyff-354017.iam.gserviceaccount.com"
```

(Setup roles in console)

- Storage Object Admin: `alignmentlabs-models-*`
- Cloud Build Editor/Viewer (https://stackoverflow.com/a/55635575)

```bash
$ gcloud iam service-accounts add-iam-policy-binding inference-service-builder@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/inference-service-builder]"

$ kubectl annotate serviceaccount inference-service-builder --namespace default iam.gke.io/gcp-service-account=inference-service-builder@dyff-354017.iam.gserviceaccount.com
```

```bash
$ kubectl create serviceaccount model-container-builder --namespace default

$ gcloud iam service-accounts create model-container-builder --project=dyff-354017

$ gcloud artifacts repositories add-iam-policy-binding dyff-models --location us-central1 --role roles/artifactregistry.writer --member "serviceAccount:model-container-builder@dyff-354017.iam.gserviceaccount.com"
```

(Setup roles in console)

- Storage Object Viewer: `alignmentlabs-models-*`

```bash
$ gcloud iam service-accounts add-iam-policy-binding model-container-builder@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/model-container-builder]"

$ kubectl annotate serviceaccount model-container-builder --namespace default iam.gke.io/gcp-service-account=model-container-builder@dyff-354017.iam.gserviceaccount.com
```

### `k8s-operator-report` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/report.yaml
serviceaccount/k8s-operator-report created
clusterrole.rbac.authorization.k8s.io/k8s-operator-report-role-cluster configured
role.rbac.authorization.k8s.io/k8s-operator-report-role-namespaced created
clusterrolebinding.rbac.authorization.k8s.io/k8s-operator-report-rolebinding-cluster created
rolebinding.rbac.authorization.k8s.io/k8s-operator-report-rolebinding-namespaced created

$ gcloud iam service-accounts create k8s-operator-report --project=dyff-354017
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User

```bash
$ gcloud iam service-accounts add-iam-policy-binding k8s-operator-report@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/k8s-operator-report]"

$ kubectl annotate serviceaccount k8s-operator-report --namespace default iam.gke.io/gcp-service-account=k8s-operator-report@dyff-354017.iam.gserviceaccount.com
```

### Build operator image

```bash
$ gcloud builds submit --config gcloud/build/evaluation-operator.yaml .
```

### Deploy operator

```bash
$ kubectl apply -f k8s/deploy/evaluation.yaml
```

### Test

From example:

```bash
$ kubectl create -f k8s/examples/evaluation.yaml
```

## Building model containers

We use Cloud Build tasks triggered from k8s to build model containers.

We tried [Kaniko](https://github.com/GoogleContainerTools/kaniko#running-kaniko-in-a-kubernetes-cluster) for this purpose, but it doesn't support the `docker buildx` features used by BentoML

### `model-container-builder` service account

```bash
$ kubectl create serviceaccount model-container-builder --namespace default

$ gcloud iam service-accounts create model-container-builder --project=dyff-354017

$ gcloud artifacts repositories add-iam-policy-binding dyff-models --location us-central1 --role roles/artifactregistry.writer --member "serviceAccount:model-container-builder@dyff-354017.iam.gserviceaccount.com"
```

(Setup roles in console)

- Storage Object Viewer: `alignmentlabs-models-*`

```bash
$ gcloud iam service-accounts add-iam-policy-binding model-container-builder@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/model-container-builder]"

$ kubectl annotate serviceaccount model-container-builder --namespace default iam.gke.io/gcp-service-account=model-container-builder@dyff-354017.iam.gserviceaccount.com
```

## Datastore DB

Created in console in multi-region `nam5` (because it contains `us-central1` and there is no single-region option for `us-central1`). Using `Datastore` mode because we want transactions.

### Create custom indexes:

```
gcloud datastore indexes create dyff/gcloud/datastore/index.yaml
```

## Audits

### Create buckets

```bash
% python -m alignmentlabs.dyff.bin.gcloud.storage.create_bucket --category=auditprocedures
gs://alignmentlabs-auditprocedures-785edd14c3c3f3c9
% python -m alignmentlabs.dyff.bin.gcloud.storage.create_bucket --category=auditreports
gs://alignmentlabs-auditreports-ef7dbc082d83b281
```

### CRD

```bash
% kubectl apply -f k8s/crd/audit.yaml
customresourcedefinition.apiextensions.k8s.io/audits.alignmentlabs.dyff created
```

### k8s-operator-audit service account

```bash
$ kubectl apply -f k8s/rbac/audit.yaml
serviceaccount/k8s-operator-audit created
clusterrole.rbac.authorization.k8s.io/k8s-operator-audit-role-cluster created
role.rbac.authorization.k8s.io/k8s-operator-audit-role-namespaced created
clusterrolebinding.rbac.authorization.k8s.io/k8s-operator-audit-rolebinding-cluster created
rolebinding.rbac.authorization.k8s.io/k8s-operator-audit-rolebinding-namespaced created

$ gcloud iam service-accounts create k8s-operator-audit --project=dyff-354017
Created service account [k8s-operator-audit].
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User

```bash
$ gcloud iam service-accounts add-iam-policy-binding k8s-operator-audit@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/k8s-operator-audit]"
Updated IAM policy for serviceAccount [k8s-operator-audit@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/k8s-operator-audit]
  role: roles/iam.workloadIdentityUser
etag: BwX4FrWr1sA=
version: 1
$ kubectl annotate serviceaccount k8s-operator-audit --namespace default iam.gke.io/gcp-service-account=k8s-operator-audit@dyff-354017.iam.gserviceaccount.com
serviceaccount/k8s-operator-audit annotated
```

### GitLab pull secret

For now, we have a free-tier Gitlab.com SaaS account, so we're not allowed to create "project access tokens". Instead, we created a self-managed "service account" Gitlab user with the email address `audit-notebook-reader@alignmentlabs.ai` and generated a personal access token for that account (looks like `glpat-<base64>`).

```bash
% kubectl apply -f k8s/deploy/gitlab-pull-secret-placeholder.yaml
secret/gitlab-pull created
% python scripts/k8s-secret-data.py set --secret=gitlab-pull --key=ALIGNMENTLABS_GITLAB_AUDIT_READER_ACCESS_TOKEN --value='glpat-XXXX'
% python scripts/k8s-secret-data.py get --secret=gitlab-pull --key=ALIGNMENTLABS_GITLAB_AUDIT_READER_ACCESS_TOKEN
glpat-XXXX
```

### `NetworkPolicy`

We apply a "least-privilege" `NetworkPolicy` to the Pods that run the Audits. The policy:

- Denies all ingress
- Allows egress only to:
  - The `api-server` Service (via Pod selector)
  - The GKE internal DNS services -- note that this includes both the standard `kube-dns` **as well as** a GKE-specific thing called `node-local-dns`.
  - The GKE metadata services needed for Workload Identity.

```bash
% kubectl apply -f k8s/network/audit.yaml
```

## API docs

```bash
% python -m alignmentlabs.dyff.bin.gcloud.storage.create_bucket --category=webassets
gs://alignmentlabs-webassets-1d32cd9a736e4614
```
