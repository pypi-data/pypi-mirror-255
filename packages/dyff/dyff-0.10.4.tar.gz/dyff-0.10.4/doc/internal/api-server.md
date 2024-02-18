# Installing the dyff API server

For `v0`, we're going to use the GKE Ingress managed service. For the open-source version, this can be replaced by something like `nginx` that we provision manually.

We will use `cert-manager` to manage SSL certificates, and we will use Let's Encrypt as the CA.

## Google Load Balancers

The HTTPS ingress is created using a k8s Ingress spec:

```bash
% kubectl apply -f k8s/deploy/api-server-ingress.yaml
```

### HTTP Redirect

We want the API to be HTTPS-only, but cert-manager needs to communicate via HTTP to bootstrap the certificate. So we create a _2nd_ load balancer that redirects HTTP traffic:

https://cloud.google.com/load-balancing/docs/https/setting-up-http-https-redirect#for_existing_load_balancers

### References

This tutorial is **mostly** corrrect, but GKE Autopilot requires some special configuration when installing `cert-manager`:

- https://cert-manager.io/docs/tutorials/getting-started-with-cert-manager-on-google-kubernetes-engine-using-lets-encrypt-for-ingress-ssl/

## Create static IP address

```bash
% gcloud compute addresses create dyff-api-server-ip --global
Created [https://www.googleapis.com/compute/v1/projects/dyff-354017/global/addresses/dyff-api-server-ip].
% gcloud compute addresses list
NAME                ADDRESS/RANGE  TYPE      PURPOSE  NETWORK  REGION  SUBNET  STATUS
dyff-api-server-ip  34.120.199.41  EXTERNAL
```

Associate the static IP address with `apis.alignmentlabs.ai`

## Test connectivity

```bash
% kubectl apply -f k8s/deploy/test/api-server-mock.yaml
deployment.apps/api-server created
service/api-server created
% kubectl apply -f k8s/deploy/api-server-ingress.yaml
ingress.networking.k8s.io/api-server-ingress created
% curl http://34.120.199.41
Hello, world!
Version: 1.0.0
Hostname: api-server-747bcbb6ff-fp5hv
```

To delete test resources:

```bash
% kubectl delete ingress api-server-ingress
ingress.networking.k8s.io "api-server-ingress" deleted
% kubectl delete service api-server
service "api-server" deleted
% kubectl delete deployment api-server
deployment.apps "api-server" deleted
```

## Install `cert-manager`

### !!! Don't install from static configuration !!!

Installing by applying the static configuration doesn't work in GKE Autopilot. Symptoms are:

```bash
% kubectl apply -f k8s/deploy/test/issuer-letsencrypt-staging.yaml
Error from server (InternalError): error when creating "k8s/deploy/test/issuer-letsencrypt-staging.yaml": Internal error occurred: failed calling webhook "webhook.cert-manager.io": failed to call webhook: Post "https://cert-manager-webhook.cert-manager.svc:443/mutate?timeout=10s": x509: certificate signed by unknown authority
```

```bash
% kubectl logs cert-manager-cainjector-5697bc65d9-xpzgb -n cert-manager
I0320 19:54:29.216231       1 start.go:126] "starting" version="v1.11.0" revision="2a0ef53b06e183356d922cd58af2510d8885bef5"
I0320 19:54:30.268075       1 request.go:682] Waited for 1.030013772s due to client-side throttling, not priority and fairness, request: GET:https://10.108.0.1:443/apis/cilium.io/v2alpha1?timeout=32s
I0320 19:54:30.423976       1 leaderelection.go:248] attempting to acquire leader lease kube-system/cert-manager-cainjector-leader-election...
E0320 19:54:30.434830       1 leaderelection.go:334] error initially creating leader election record: leases.coordination.k8s.io is forbidden: User "system:serviceaccount:cert-manager:cert-manager-cainjector" cannot create resource "leases" in API group "coordination.k8s.io" in the namespace "kube-system": GKE Warden authz [denied by managed-namespaces-limitation]: the namespace "kube-system" is managed and the request's verb "create" is denied
```

Basically, the default configuration tries to create resources in `kube-system` namespace, which isn't allowed in GKE Autopilot.

### Install via Helm

See: https://cert-manager.io/docs/installation/compatibility/#gke-autopilot

See: https://cert-manager.io/docs/installation/helm/

Add Helm repository:

```bash
% helm repo add jetstack https://charts.jetstack.io
"jetstack" has been added to your repositories
```

Install `cert-manager`:

```bash
% helm install cert-manager jetstack/cert-manager --namespace cert-manager --create-namespace --version 1.11 --set installCRDs=true --set global.leaderElection.namespace=cert-manager
```

The flag `--set global.leaderElection.namespace=cert-manager` tells `cert-manager` to creates its resources in namespace `cert-manager` rather than the default of `kube-system`.

## Create `Issuer`

### Test:

You want to use the Let's Encrypt "staging" CA for testing to avoid getting rate-limited.

```bash
% kubectl apply -f k8s/deploy/test/api-server-issuer-letsencrypt.yaml
issuer.cert-manager.io/api-server-letsencrypt-staging created
```

To use the test issuer, you need to change the `cert-manager.io/issuer` annotation in `k8s/deploy/api-server-ingress.yaml` to `api-server-letsencrypt-staging` (note the `-staging` suffix).

### Production:

```bash
% kubectl apply -f k8s/deploy/api-server-issuer-letsencrypt.yaml
issuer.cert-manager.io/api-server-letsencrypt created
```

## Create placeholder `Secret`

```bash
% kubectl apply -f k8s/deploy/api-server-secret-placeholder.yaml
secret/api-server-letsencrypt created
```

## Create/modify the `Ingress` to support TLS

```bash
% kubectl apply -f k8s/deploy/api-server-ingress.yaml
ingress.networking.k8s.io/api-server-ingress created
```

Note the annotation `cert-manager.io/issuer: api-server-letsencrypt` in the manifest.

## Management

To force certificate renewal:

```bash
% cmctl renew api-server-key
```

## Deployment

### `api-server` service account

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

### `report-reader` service account

```bash
% gcloud iam service-accounts create report-reader --project=dyff-354017
Created service account [report-reader].
```

(Setup GCloud roles in console)

- Storage Object Viewer -- is-reports-bucket

### Create placeholder `Secret` for key signing

```bash
% kubectl apply -f k8s/deploy/api-key-signing-secret-placeholder.yaml
secret/api-key-signing created
```

### Populate `Secret` data

```bash
% python scripts/rotate-api-key-signing-secret.py
```

### Deploy the API server

```bash
% kubectl apply -f k8s/deploy/api-server.yaml
```

### Reconfigure the `Ingress`

If you already created the GKE `Ingress` resource, you need to **delete it and re-create it** after creating the `api-server` `Deployment` so that the `Ingress` picks up the non-default `readinessProbe` endpoint (we use `/health` instead of the default of `/`). See: https://stackoverflow.com/a/61614106

Note: We could also configure the health check in a separate `BackendConfig` resource (which is specific to GKE). See: https://stackoverflow.com/a/71406914

### Issue an API key

```bash
% python scripts/rotate-account-api-key.py --account=<account_id> --api=dyff
```

## Troubleshooting

### Running the server locally for testing

```bash
% uvicorn alignmentlabs.dyff.web.test.server:app --reload --ssl-keyfile=dyff/test/localhost+2-key.pem --ssl-certfile=dyff/test/localhost+2.pem --log-level=debug
```

If you are testing with the API client, you will need to instantiate the client with `verify_ssl_certificates=False`.

### Problems with SSL

See: https://cert-manager.io/docs/tutorials/getting-started-with-cert-manager-on-google-kubernetes-engine-using-lets-encrypt-for-ingress-ssl/#troubleshooting

### Getting the name of the GKE load balancer

```bash
% kubectl get ingress sample-ingress -o jsonpath='{.metadata.annotations.ingress\.kubernetes\.io/url-map}'
```

### 502 Bad Gateway error

See: https://www.willianantunes.com/blog/2021/05/gke-ingress-how-to-fix-a-502-bad-gateway-error/

### `ChunkedEncodingError` on large data streams

The Google Load Balancer has a `backend_timeout` that defaults to 30s. Large uploads/downloads may exceed this limit. I increased it to 120s.

See: https://gitlab.com/AlignmentLabs/dyff/-/issues/43

### azure.core.exceptions.ServiceRequestError: Bearer token authentication is not permitted for non-TLS protected (non-https) URLs.

You provided an API key to a client application that is supposed to be communicating unauthenticated with the api-server-proxy on localhost.

```
Traceback (most recent call last):
  File "/usr/local/lib/python3.8/runpy.py", line 194, in _run_module_as_main
    return _run_code(code, main_globals, None,
  File "/usr/local/lib/python3.8/runpy.py", line 87, in _run_code
    exec(code, run_globals)
  File "/usr/local/lib/python3.8/site-packages/alignmentlabs/dyff/bin/run_jupyterbook.py", line 104, in <module>
    absl.app.run(main)
  File "/usr/local/lib/python3.8/site-packages/absl/app.py", line 308, in run
    _run_main(main, args)
  File "/usr/local/lib/python3.8/site-packages/absl/app.py", line 254, in _run_main
    sys.exit(main(argv))
  File "/usr/local/lib/python3.8/site-packages/alignmentlabs/dyff/bin/run_jupyterbook.py", line 51, in main
    data = dyff.auditprocedures.download(audit.auditProcedure)
  File "/usr/local/lib/python3.8/site-packages/alignmentlabs/apis/dyff/_generated/operations/_patch.py", line 288, in download
    stream = super().download(path)
  File "/usr/local/lib/python3.8/site-packages/azure/core/tracing/decorator.py", line 76, in wrapper_use_tracer
    return func(*args, **kwargs)
  File "/usr/local/lib/python3.8/site-packages/alignmentlabs/apis/dyff/_generated/operations/_operations.py", line 1034, in download
    pipeline_response: PipelineResponse = self._client._pipeline.run(  # pylint: disable=protected-access
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/_base.py", line 213, in run
    return first_node.send(pipeline_request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/_base.py", line 70, in send
    response = self.next.send(request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/_base.py", line 70, in send
    response = self.next.send(request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/_base.py", line 70, in send
    response = self.next.send(request)
  [Previous line repeated 2 more times]
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/policies/_redirect.py", line 181, in send
    response = self.next.send(request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/policies/_retry.py", line 489, in send
    raise err
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/policies/_retry.py", line 467, in send
    response = self.next.send(request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/policies/_authentication.py", line 113, in send
    self.on_request(request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/policies/_authentication.py", line 87, in on_request
    self._enforce_https(request)
  File "/usr/local/lib/python3.8/site-packages/azure/core/pipeline/policies/_authentication.py", line 53, in _enforce_https
    raise ServiceRequestError(
azure.core.exceptions.ServiceRequestError: Bearer token authentication is not permitted for non-TLS protected (non-https) URLs.
```
