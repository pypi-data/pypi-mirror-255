# Design notes for `dyff` user-facing API

## General

The user-facing API is implemented with gcloud serverless endpoints (either Cloud Functions or Cloud Run) accepting HTTP requests.

Functions that trigger a task in the dyff system (e.g., evaluating a model on a dataset) do so by creating a record describing the task in the Datastore DB inside a transaction. If the record already exists, the function aborts. (Or maybe re-starts the task if it failed previously.)

A daemon running in k8s notices new tasks and creates the necessary k8s resources to complete them. The code running on k8s updates the Datastore record as the task progresses.

User-facing queries will simply pull data from the Firestore DB. Full result sets will be stored in Cloud Storage and referenced in the DB.

Datastore is a typical hierarchical key-value store DB. The data that the user submits to the API should map directly to fields in the DB records (although more fields will be added by the dyff system to record progress, results, etc.).

## API Support for User Tasks

### Upload a model

We can accept models in three different forms, in decreasing order of generality:

1. A Docker image that runs a BentoML Service (basically an HTTP server that supports particular requests).
2. A "Bento", which is an archive that contains all the files needed to build the Docker image.
3. A model in a supported ML framework

Eventually, we will support all ML frameworks that BentoML supports. Currently, we support only the `transformers` framework (and only models for the `image-classification` task).

The API endpoint should require and validate all the model metadata that we need. It returns an upload URL and security token to the client. It creates a `Model` entity in the DB, which triggers k8s to watch the upload process and finish packaging the model when uploading is finished.

### Upload a dataset

Same basic workflow as uploading a model.

### Order an evaluation

The user specifies:

1. The ID of a model that they have access to
2. The ID of a dataset that they have access to
3. Possibly additional evaluation criteria beyond the "standard" ones

The API endpoint checks whether all or part of the requested evaluation has already been run. It creates a new `Evaluation` entity in the DB for the missing parts.

### Query/Delete entities

The user can query and delete entities in (their account in) the DB. The k8s daemon watches for deletions and makes sure that all related processes are stopped and all stored data is deleted.

### Query results

The user can also query evaluation results. These might not be stored in the DB due to the higher cost of storage, so the query might entail loading data from a Cloud Storage bucket into an in-memory DB.
