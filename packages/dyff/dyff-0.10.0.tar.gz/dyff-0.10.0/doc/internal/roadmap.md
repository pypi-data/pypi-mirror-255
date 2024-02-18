# Alpha Deployment

## [ ] Missing features

- [ ] API changes
  - [ ] Use s3 signed links for large data transfers
- [ ] Add support for user-authored `Reports` and `Rubrics`
- [ ] Add ability to "subscribe" to audits (c.f. event-driven architecture and workflows)

## [ ] Security

- [ ] Fine-grained access control for API tokens
  - [ ] Design/document user roles (e.g., "Audit Reader", "Audit Creator", ...)
  - [ ] Grant access to resources by pattern (e.g., `audits/public/*`)
  - [ ] Restrict user tokens to list of accounts. Default: `[your-account, public]`
  - [ ] Restrict ephemeral service account tokens to specific resources
- [ ] Isolation for untrusted code
  - [ ] Identify and document which components are untrusted
  - [ ] Untrusted components needing API access communicate through sidecar proxy that has an ephemeral token granting exactly the required permissions.
  - [ ] Untrusted pods have no GCP service account privileges
  - [ ] Default `deny-all` network policies; per-component whitelists as needed
  - [ ] All untrusted code should have reasonable timeouts set
- [ ] Data verification
  - [ ] Untrusted (user-uploaded) data is verified against schema and sanity checks before accepting into system.
- [ ] Resource usage tracking and quotas for user accounts

## [ ] Developer experience

- [ ] Documentation
  - [ ] Tutorial on `jupyter-book` audits
  - [ ] Tutorial on `Report` and `Rubric` authoring
  - [ ] Document data exchange schemas
- [ ] Testing tools
  - [ ] Test suite to verify data schema compliance
  - [ ] Test suite to verify inference service API compliance

## [ ] Web UI

- [ ] Public website
  - [ ] Landing page with links to docs and data views
- [ ] Account dashboard
  - [ ] Create / update / delete accounts
  - [ ] Separate authentication for user login (i.e., not using API key)
  - [ ] Issue / revoke API keys on account
- [ ] Data views
  - [ ] Something like the Cloud Datastore dashboard, but with appropriate viewing restrictions according to account privileges
  - [ ] Hub for exploring published audits

# Open Source Publication

## Architecture changes

- [ ] Replace status-watching with event-driven architecture (probably using RabbitMQ or Kafka)
- [ ] Argo Workflows for orchestrating multi-step jobs (e.g., Evaluation -> Report -> Audit)
  - Might be superflous with the event-driven architecture

## Deployment

- [ ] "One-click" Terraform deployment on GCP with current dependencies

# Open Source v1.0

## Multi-Cloud Support

- [ ] "One-click" Terraform deployment on AWS (at least)
- [ ] Options for infrastructure dependencies
  - [ ] Data store
    - [ ] At least one FOSS solution that can run in k8s -- probably MongoDB
      - [ ] k8s deployment
      - [ ] Example configuration for backups
    - [ ] Support for managed services?
  - [ ] Persistent storage
    - [ ] s3-like interface for all major providers
    - [ ] Is there an open-source s3 solution? Alternative is probably k8s persistent volumes
  - [ ] Artifact / Docker registry

## User management

- [ ] OAuth2 / external identity providers
- [ ] User sign-up / account management Web UI

## Community

- [ ] Define a contribution process
- [ ] Plan / personnel for community engagement
- [ ] Plan / personnel for responding to issues
