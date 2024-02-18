## Create APIs

```
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind Audit --plural audits
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind Evaluation --plural evaluations
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind Report --plural reports
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind InferenceService --plural inferenceservices
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind Model --plural models
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind Dataset --plural datasets
% operator-sdk create api --controller --resource --group dyff --version v1alpha1 --kind InferenceSession --plural inferencesessions
```

## GCloud IAM

There is a 30-character limit for GCloud IAM service account names.

````
% gcloud iam service-accounts create dyffop-controller-manager --project=dyff-354017
Created service account [dyffop-controller-manager].

(Setup GCloud roles in console)
* Kubernetes Engine Viewer
  * See: https://www.fairwinds.com/blog/how-we-manage-kubernetes-rbac-and-iam-roles-on-gke
* Cloud Datastore User

```bash
% gcloud iam service-accounts add-iam-policy-binding dyffop-controller-manager@dyff-354017.iam.gserviceaccount.com --role roles/iam.workloadIdentityUser --member "serviceAccount:dyff-354017.svc.id.goog[default/dyffop-controller-manager]"
Updated IAM policy for serviceAccount [dyffop-controller-manager@dyff-354017.iam.gserviceaccount.com].
bindings:
- members:
  - serviceAccount:dyff-354017.svc.id.goog[default/dyffop-controller-manager]
  role: roles/iam.workloadIdentityUser
etag: BwYBkcddqIM=
version: 1
% kubectl annotate serviceaccount dyff-operator-controller-manager --namespace dyff-operator-system iam.gke.io/gcp-service-account=dyffop-controller-manager@dyff-354017.iam.gserviceaccount.com
serviceaccount/dyff-operator-controller-manager annotated
````

# Deployment

## Build docker container (GCloud)

```bash
go % make gcloud-build
```

## Deploy the operator (in current Kubernetes context)

```bash
go % make deploy
```

# Troubleshooting

## `"Reflector ListAndWatch" error`

Sometimes you will see this error on operator startup:

```bash
I0728 21:56:20.769790       1 trace.go:219] Trace[1721745152]: "Reflector ListAndWatch" name:pkg/mod/k8s.io/client-go@v0.26.7/tools/cache/reflector.go:169 (28-Jul-2023 21:56:10.669) (total time: 10100ms):
Trace[1721745152]: ---"Objects listed" error:<nil> 9899ms (21:56:20.569)
Trace[1721745152]: [10.100041582s] [10.100041582s] END
```

AFAICT the error is harmless, but I'm recording relevant info here for posterity.

This seems to come up intermittently with various kubebuilder/operator-sdk operators. What little I can gather from the Web suggest the problem is trying to watch too many things at once and getting a timeout. See: https://prog.world/stepping-on-a-rake-experience-writing-kubernetes-operator/ for the following workaround:

```bash
[In main.go]
mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{
    ...
    ClientDisableCacheFor: []client.Object{
	    &corev1.ConfigMap{},
		&corev1.Pod{},
		&corev1.Secret{},
		&appsv1.Deployment{},
		&rbacv1.ClusterRole{},
		&rbacv1.ClusterRoleBinding{},
		&rbacv1.Role{},
		&rbacv1.RoleBinding{},
	},
```

This only made a difference for me in combination with adding label selectors to the Watches for each controller (which is a good idea anyway). Not sure if that was just a coincidence.
