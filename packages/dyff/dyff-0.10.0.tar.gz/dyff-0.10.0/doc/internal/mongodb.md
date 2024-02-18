# MongoDB datastore backend

We're going to use MongoDB as our FOSS datastore solution. Although our data is arguably relational-enough to justify an RDBMS, we don't expect to do complex dynamic queries on it and we're early enough in the lifecycle of this project that having a looser data schema is probably a net win in terms of productivity.

We're going to administer MongoDB on k8s using the [Percona Server for MongoDB Operator](https://github.com/percona/percona-server-mongodb-operator) . Percona maintains a FOSS\* distribution of MongoDB that includes some enterprise features that are not available in the standard MongoDB Community distribution. Their k8s operator also seems better supported after a brief inspection.

# k8s deployment

## Get deployment files

You can use the script `mongodb/fetch-deploy-files-from-upstream.sh` to get the k8s deployment files for the operator. **You only need to do this if you want to merge in changes from upstream. Be aware this will overwrite the existing files, including any modifications we've made.**

```bash
mongodb $ GITHUB_PERSONAL_ACCESS_TOKEN=ghp_XXX ./fetch-deploy-files-from-upstream.sh
```

where the GitHub PAT needs permission to read public repositories. The token is needed only to avoid API rate-limiting.

## Change cluster name

The default is `my-cluster-name`, and we change it to `dyff-datastore`. The second command removes the backup files.

```bash
mongodb $ find deploy/**/*.yaml -type f -exec sed -i .bak 's/my-cluster-name/dyff-datastore/g' {} \;
mongodb $ find deploy/**/*.yaml.bak -type f -exec rm {} +
```

## Install the operator

Reference: https://docs.percona.com/percona-operator-for-mongodb/kubernetes.html

```bash
mongodb $ kubectl apply --server-side -f deploy/crd.yaml
mongodb $ kubectl create namespace mongodb
mongodb $ kubectl apply -f deploy/rbac.yaml -n mongodb
mongodb $ kubectl apply -f deploy/operator.yaml -n mongodb
```

## Configure MongoDB

See comments beginning with `[dyff]` in the `deploy/cr.yaml` file.

## Configure backups

Reference: https://docs.percona.com/percona-operator-for-mongodb/backups-storage.html

### Create GCP bucket

```bash
$ python -m alignmentlabs.dyff.bin.gcloud.storage.create_bucket --category="mongodb-backup"
gs://alignmentlabs-mongodb-backup-91bc39417d1295ce
```

### Create service account

```bash
$ gcloud iam service-accounts create mongodb-backup --project=dyff-354017
Created service account [mongodb-backup].
```

(Setup GCloud roles in console)

- Storage Admin: `alignmentlabs-mongodb-backup-*`

### Create placeholder secret for storage access

```bash
mongodb $ kubectl apply -f deploy/backup-s3.yaml -n mongodb
```

### Add HMAC key for storage access

Reference: https://cloud.google.com/storage/docs/authentication/managing-hmackeys#command-line

```bash
mongodb $ gcloud storage hmac create mongodb-backup@dyff-354017.iam.gserviceaccount.com
kind: storage#hmacKey
metadata:
  accessId: XXXXXXXXXX
  etag: YjM4MDI2YzA=
  id: dyff-354017/XXXXXXXXXX
  kind: storage#hmacKeyMetadata
  projectId: dyff-354017
  selfLink: https://www.googleapis.com/storage/v1/projects/dyff-354017/hmacKeys/XXXXXXXXXX
  serviceAccountEmail: mongodb-backup@dyff-354017.iam.gserviceaccount.com
  state: ACTIVE
  timeCreated: '2023-08-26T05:08:27.383000+00:00'
  updated: '2023-08-26T05:08:27.383000+00:00'
secret: XXXXXXXXXX
```

```bash
mongodb $ python ../scripts/k8s-secret-data.py set --secret=dyff-datastore-backup-s3 --key=AWS_ACCESS_KEY_ID --value=$(echo -n <HMAC accessId> | base64) --namespace=mongodb
mongodb $ python ../scripts/k8s-secret-data.py set --secret=dyff-datastore-backup-s3 --key=AWS_SECRET_ACCESS_KEY --value=$(echo -n <HMAC secret> | base64) --namespace=mongodb
```

### Configure custom resource

```yaml
backup:
  enabled: true
  image: percona/percona-backup-mongodb:2.0.4
  serviceAccountName: percona-server-mongodb-operator
  storages:
    # [dyff] Backup to GCS through the s3-compatible API
    gs-dyff-datastore:
    type: s3
    s3:
      endpointUrl: https://storage.googleapis.com
      bucket: alignmentlabs-mongodb-backup-91bc39417d1295ce
      credentialsSecret: dyff-datastore-backup-s3
      region: us-central1
      prefix: "dyff-datastore/"
      uploadPartSize: 10485760
      maxUploadParts: 10000
      storageClass: STANDARD
      insecureSkipTLSVerify: false
```

### Create cluster user secrets

Don't do anything! Let the operator generate random passwords when it sees the secret doesn't exist.

### Create the DB cluster

```bash
mongodb $ kubectl apply -f deploy/cr.yaml -n mongodb
```

### `mongodb-admin` service account

Service account is created by RBAC config. Still need the IAM service account.

```bash
$ kubectl apply -f k8s/rbac/mongodb/mongodb-admin.yaml
serviceaccount/mongodb-admin created
role.rbac.authorization.k8s.io/mongodb-admin-role-namespaced created
rolebinding.rbac.authorization.k8s.io/mongodb-admin-rolebinding-namespaced created

$ gcloud iam service-accounts create mongodb-admin --project=dyff-354017
Created service account [mongodb-admin].
```

(Setup GCloud roles in console)

- Kubernetes Engine Viewer
  - See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
- Cloud Datastore User
- Storage Admin

Note: Specify the namespace in `"serviceAccount:dyff-354017.svc.id.goog[mongodb/mongodb-admin]"`; the part in brackets is `[namespace/serviceaccount]`.

```bash
$ gcloud iam service-accounts add-iam-policy-binding mongodb-admin@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[mongodb/mongodb-admin]"
Updated IAM policy for serviceAccount [mongodb-admin@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[mongodb/mongodb-admin]
  role: roles/iam.workloadIdentityUser
etag: BwYEAEXIucs=
version: 1

$ kubectl annotate serviceaccount mongodb-admin --namespace mongodb iam.gke.io/gcp-service-account=mongodb-admin@dyff-354017.iam.gserviceaccount.com
serviceaccount/mongodb-admin annotated
```

### Quick check

```bash
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_DATABASE_ADMIN_USER
databaseAdmin
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_DATABASE_ADMIN_PASSWORD
<PASSWORD>
% kubectl run -i --rm --tty percona-client --image=percona/percona-server-mongodb:4.4.18-18 --restart=Never -- bash -il
Warning: Autopilot set default resource requests for Pod default/percona-client, as resource requests were not specified. See http://g.co/gke/autopilot-defaults
If you don't see a command prompt, try pressing enter.
[mongodb@percona-client /]$
[mongodb@percona-client /]$ mongo "mongodb+srv://databaseAdmin:<PASSWORD>@dyff-datastore-rs0.mongodb.svc.cluster.local/admin?replicaSet=rs0&ssl=false"
...
---
rs0:PRIMARY>
```

```bash
% kubectl cluster-info
Kubernetes control plane is running at https://104.154.52.38
GLBCDefaultBackend is running at https://104.154.52.38/api/v1/namespaces/kube-system/services/default-http-backend:http/proxy
KubeDNS is running at https://104.154.52.38/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
KubeDNSUpstream is running at https://104.154.52.38/api/v1/namespaces/kube-system/services/kube-dns-upstream:dns/proxy
Metrics-server is running at https://104.154.52.38/api/v1/namespaces/kube-system/services/https:metrics-server:/proxy
```

# Data migration

## Prerequisites

### Build container for running migration script

```bash
code % gcloud builds submit --config dyff/gcloud/build/dev-base.yaml .
```

### How to get a shell for running migration script

```bash
% kubectl run -it --rm migrate --image=us-central1-docker.pkg.dev/dyff-354017/dyff-system/alignmentlabs/dyff/dev-base -n mongodb --overrides='{"spec": {"serviceAccount": "mongodb-admin"}}' -- bash
```

## Generate ID re-mapping file

**WARNING: The remapping file is used in multiple steps of the migration process and must not change after you have started moving data. The version used in the actual migration is in source control in `/dyff/scripts/mongodb-id-remapping.json`. This step is documented for completeness, but you probably should not re-generate the remapping file.**

```bash
root@migrate:/alignment-labs/dyff# python3 scripts/build-entity-id-remapping.py scripts/mongodb-id-remapping.json
```

## Migrate the datastore entities

```bash
root@migrate:/alignment-labs/dyff# python3 scripts/migrate-gcds-to-mongodb.py scripts/mongodb-id-remapping.json
```

## Migrate the GCS data

This can run locally if you have appropriate GCS permissions.

```bash
% python scripts/migrate-gcs-data.py scripts/mongodb-id-remapping.json
```

## Delete old data

TODO

## Create users

### Create k8s secret to store user credentials and generate password

```bash
dyff % kubectl apply -f k8s/deploy/mongodb/user-query-backend.yaml
secret/query-backend created
dyff % python scripts/k8s-secret-data.py set --secret=query-backend-mongodb --key=DYFF_MONGODB__QUERY_BACKEND_CREDENTIALS__PASSWORD --random_bytes=32
dyff % python scripts/k8s-secret-data.py get --secret=query-backend-mongodb --key=DYFF_MONGODB__QUERY_BACKEND_CREDENTIALS__PASSWORD
<USER_PASSWORD>
```

### Create MongoDB user

```bash
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_USER_ADMIN_USER
userAdmin
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_USER_ADMIN_PASSWORD
<USERADMIN_PASSWORD>
% kubectl run -i --rm --tty percona-client --image=percona/percona-server-mongodb:4.4.18-18 --restart=Never -- bash -il
Warning: Autopilot set default resource requests for Pod default/percona-client, as resource requests were not specified. See http://g.co/gke/autopilot-defaults
If you don't see a command prompt, try pressing enter.
[mongodb@percona-client /]$
[mongodb@percona-client /]$ mongo "mongodb+srv://userAdmin:<USERADMIN_PASSWORD>@dyff-datastore-rs0.mongodb.svc.cluster.local/admin?replicaSet=rs0&ssl=false"
...
---
rs0:PRIMARY> use users
switched to db users
rs0:PRIMARY> db.createUser(
... {
... user: "query-backend",
... pwd: "<USER_PASSWORD>",
... roles: [ { role: "read", db: "workflows" } ]
... }
... )
Successfully added user: {
        "user" : "query-backend",
        "roles" : [
                {
                        "role" : "read",
                        "db" : "workflows"
                }
        ]
}
rs0:PRIMARY>
```

### Login as MongoDB user

```bash
[mongodb@percona-client /]$ mongo "mongodb+srv://<USERNAME>:<PASSWORD>@dyff-datastore-rs0.mongodb.svc.cluster.local/<DATABASE>?replicaSet=rs0&ssl=false&authSource=users"
```

## Migrate auth data

### Create k8s secret to store user credentials and generate password

```bash
dyff % kubectl apply -f k8s/deploy/mongodb/user-auth-backend.yaml
secret/auth-backend-mongodb created
dyff % python scripts/k8s-secret-data.py set --secret=auth-backend-mongodb --key=DYFF_MONGODB__AUTH_BACKEND_CREDENTIALS__PASSWORD --random_bytes=32
dyff % python scripts/k8s-secret-data.py get --secret=auth-backend-mongodb --key=DYFF_MONGODB__AUTH_BACKEND_CREDENTIALS__PASSWORD
<USER_PASSWORD>
```

### Create MongoDB user

```bash
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_USER_ADMIN_USER
userAdmin
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_USER_ADMIN_PASSWORD
<USERADMIN_PASSWORD>
% kubectl run -i --rm --tty percona-client --image=percona/percona-server-mongodb:4.4.18-18 --restart=Never -- bash -il
Warning: Autopilot set default resource requests for Pod default/percona-client, as resource requests were not specified. See http://g.co/gke/autopilot-defaults
If you don't see a command prompt, try pressing enter.
[mongodb@percona-client /]$
[mongodb@percona-client /]$ mongo "mongodb+srv://userAdmin:<USERADMIN_PASSWORD>@dyff-datastore-rs0.mongodb.svc.cluster.local/admin?replicaSet=rs0&ssl=false"
...
---
rs0:PRIMARY> use users
switched to db users
rs0:PRIMARY> db.createUser(
... {
... user: "auth-backend",
... pwd: "<USER_PASSWORD>",
... roles: [ { role: "readWrite", db: "accounts" } ]
... }
... )
Successfully added user: {
        "user" : "auth-backend",
        "roles" : [
                {
                        "role" : "readWrite",
                        "db" : "accounts"
                }
        ]
}
rs0:PRIMARY>
```

## Kafka Sink

### Create k8s secret to store user credentials and generate password

```bash
dyff % kubectl apply -f k8s/deploy/mongodb/user-workflows-sink.yaml
secret/workflows-sink-mongodb created
dyff % python scripts/k8s-secret-data.py set --secret=workflows-sink-mongodb --key=DYFF_MONGODB__WORKFLOWS_SINK_CREDENTIALS__PASSWORD --random_bytes=32
dyff % python scripts/k8s-secret-data.py get --secret=workflows-sink-mongodb --key=DYFF_MONGODB__WORKFLOWS_SINK_CREDENTIALS__PASSWORD
<USER_PASSWORD>
```

### Create MongoDB user

```bash
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_USER_ADMIN_USER
userAdmin
% python scripts/k8s-secret-data.py get --namespace=mongodb --secret=dyff-datastore-secrets --key=MONGODB_USER_ADMIN_PASSWORD
<USERADMIN_PASSWORD>
% kubectl run -i --rm --tty percona-client --image=percona/percona-server-mongodb:4.4.18-18 --restart=Never -- bash -il
Warning: Autopilot set default resource requests for Pod default/percona-client, as resource requests were not specified. See http://g.co/gke/autopilot-defaults
If you don't see a command prompt, try pressing enter.
[mongodb@percona-client /]$
[mongodb@percona-client /]$ mongo "mongodb+srv://userAdmin:<USERADMIN_PASSWORD>@dyff-datastore-rs0.mongodb.svc.cluster.local/admin?replicaSet=rs0&ssl=false"
...
---
rs0:PRIMARY> use users
switched to db users
rs0:PRIMARY> db.createUser(
... {
... user: "workflows-sink",
... pwd: "<USER_PASSWORD>",
... roles: [ { role: "readWrite", db: "workflows" } ]
... }
... )
Successfully added user: {
        "user" : "workflows-sink",
        "roles" : [
                {
                        "role" : "readWrite",
                        "db" : "workflows"
                }
        ]
}
rs0:PRIMARY>
```
