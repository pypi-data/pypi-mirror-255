### `dyff-admin` service account

```bash
$ kubectl create serviceaccount dyff-admin --namespace default
serviceaccount/dyff-admin created

$ gcloud iam service-accounts create dyff-admin --project=dyff-354017
Created service account [dyff-admin].
```

(Setup roles in console)

- Storage Admin

```bash
$ gcloud iam service-accounts add-iam-policy-binding dyff-admin@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/dyff-admin]"
Updated IAM policy for serviceAccount [dyff-admin@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/dyff-admin]
  role: roles/iam.workloadIdentityUser
etag: BwYLVQgX5VA=
version: 1

$ kubectl annotate serviceaccount dyff-admin --namespace default iam.gke.io/gcp-service-account=dyff-admin@dyff-354017.iam.gserviceaccount.com
serviceaccount/dyff-admin annotated
```
