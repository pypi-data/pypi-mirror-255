# Database

We're adopting Google Firestore in Datastore Mode ("Datastore") as the primary DB.

The Datastore data model is essentially JSON, where JSON `object` == Datastore `Entity`. We use Datastore UIDs as unique identifiers for our objects throughout the system. All entities are associated with an enclosing `Account`. The identifier of an entity is a string of the form `account-id/entity-id`. Data associated with entities is stored in corresponding GCS buckets at a path like `gs://bucket/account-id/entity-id`.

There is a special `Account` with the ID `public` (because you can also specify your own IDs; strings won't clash with auto-IDs because the auto-IDs are `int`s). We will keep all public Datasets and Models in the `public` account, and they will be accessible to all other accounts. Integers are valid Cloud Storage object names, and the auto-IDs have good dispersion properties because that's also important to Datastore.

## Authentication and security

Users execute tasks in our system by making DB queries and creating new entities in the database. Thus, DB access is our single point of authentication. We need to verify that users are allowed to access the entity IDs that they specify in submitted tasks. Users will authenticate to a single Account (for example, `example-account`). By default, they will have permission to access any entities under that account, i.e., with IDs of the form `example-account/something`. All Accounts also have permission to access entities under the `public` account (e.g., `public/something`). Access to entities under any other accounts will be blocked.

All internal system resources (everything in `Kubernetes Engine (gke/k8s)`, `Cloud Storage (gcs)`, and `Artifact Registry`) are considered privileged and users should never be able to manipulate them directly. Network egress should be **completely disabled** for everything running in `k8s`. Network ingress should be enabled **only** for Pods that are fetching Datasets and Models. Egress from Artifact Registry should be **completely disabled**. Egress from GCS should be **completely disabled**.

## DB Schema

Note that Entities can be repeated because each instance has a unique key. Each of the embedded entities has a `status` field that allows the system to atomically record the progress of any related work. There is a separate `error` field that records the last error encountered during processing (if any). This is separate from `status` so that if an error occurs during a multi-step pipeline, `status` can be set to the last good state (e.g., a model was fetched successfully but packaging failed).

```
Account: entity
{
    Dataset: entity
    {
        status: string {"created", "admitted", "ready", "fetch_failed"}
    }

    Model: entity
    {
        status: string {"created", "admitted", "ready", "fetch_failed"}
    }

    InferenceService: entity
    {
        status: string {"created", "admitted", "ready", "build_failed"}
    }

    Evaluation: entity
    {
        status: string {"created", "admitted", "completed", "failed"}

        dataset_id: int
        filter_expression: string

        model_id: int

        Result: entity
        {

        }
    }
}
```

I'm not exactly sure how to store evaluation results. One option is to have one nested Result entity per instance. This gives maximum query capability, but could incur non-trivial query costs because there would be a lot of entities. At the other extreme, the results might not be stored in the DB at all, and instead could be stored as an archive in a bucket. If we wanted interactive queries, we could load the results into an in-memory database as needed. We could run offline "reports" over many result sets if we want to answer system-wide questions (like, "what is the most difficult instance in ImageNet?"). A middle ground could be that selected aggregate results are stored in the DB for quick access, and the full result set is stored in a bucket.

## How system components interact with the DB

When a new task is ordered (for example, starting an evaluation), the system first attempts to create a new Evaluation entity in the `created` state within a transaction. If the transaction fails, the object already exists, and we assume it is already being managed by another process.

The `orchestrator` daemon periodically checks for entities with the `created` status. When it finds one, it determines whether any additional processing is necessary. If so, it changes the status to `admitted` and creates one or more k8s resources describing the work to be done. Otherwise, it sets the entity status to `ready`.

Work tasks are represented as k8s custom resources. For example, an Evaluation entity might correspond to the following k8s resource:

```yaml
apiVersion: alignmentlabs.dyff/v1
kind: Evaluation
metadata:
  labels:
    app: evaluation
    component: evaluation
    account: public
    evaluation: "5634161670881280"
  name: evaluation-public-5634161670881280
spec:
  dataset: public/5646488461901824
  datasetConfiguration:
    filters:
      - field: "category"
        relation: "=="
        value: "weather"
      - field: "corruption"
        relation: "=="
        value: "frost"
      - field: "intensity"
        relation: "=="
        value: 5
      - field: "label"
        relation: "=="
        value: "n01440764"
  model: public/5631671361601536
  task: image-classification
```

Work tasks are handled using the k8s Operator pattern. Each custom resource has an associated controller process. These are implemented using the `kopf` k8s operator framework. The controller decides what to do next by querying the `status` field of the DB entity, and they update `status` as each processing step is completed. The processing tasks should be idempotent and resumable. When started, they should first check if the task is in a consistent state (e.g., `fetched`, not `fetching`) and roll back to the last consistent state if necessary. They should attempt to do the rollback in their shutdown handler, but should also handle the case where the rollback doesn't happen on shutdown. They then proceed from the last consistent state.

The user-facing API simply manages entities in the DB. To create a new task, it creates a new entity with the `created` status. A daemon in k8s periodically queries for new entities and starts the corresponding tasks. Checking only the `status` is a "projection query" and only counts as a single read, so it's basically free.

# Specification 0.2

We have decided to make individual pieces of input data the basic object of evaluation. This will enable much richer analyses than thinking in terms of datasets, and it plays nicely with the requirements of k8s apps, which work best when we can stream data to a pool of interchangeable workers.

## Proposed Data Model

Notation: `ObjectID` means the `sha256` hash of some `Object`.

An `Item` is a singular, atomic piece of data that can be input to a machine learning model. Examples: an image, a piece of text, a video.

```json
# Item
{
    "type": "Image", "Text", ...
    "bytes": raw bytes of the item
}
```

`Item`s are stored in `s3` buckets, in files named with their `ItemID`. Somewhere, there is a database that records which bucket contains which `Item`s.

A `ModelOutput` describes the value and semantics of one output of an ML model. `ModelOutput`s are specified as "JSON-encoded objects", which specify a type and a set of keyword arguments (all the information needed to instantiate an object in Python). The arguments may be literals or recursive objects.

- Perhaps singletons could be written like `{"Label": "cat"}` to save space

```json
# ModelOutputs
{
    "type": "Label",
    "label": "cat"
},
{
    "type": "Scores",
    "kind": "logits",
    "scores": [-1, 1, 0.5]
},
{
    "type": "Detection",
    "geometry": {
        "type": "Rectangle",
        "x": 42,
        "y": 43,
        "height": 44,
        "width": 45
    },
    "label": "dog"
},
{
    "type": "Segmentation",
    "mask": <image representation of correct segmentation>
}
```

An `Instance` is one or more `ItemID`s together with 0 or more `ModelOutput`s called "targets". In the case that there is more than one input or more than one target, they are provided in a dictionary with standardized keys that indicate their semantics.

```json
# Instance
{
    "inputs": ItemID | Dict[str, ItemID]
    "targets": ModelOutput | Dict[str, ModelOutput]
}
```

A `Dataset` is a collection of `Instance`s together with metadata describing their attribution, the circumstances of their collection, and any additional information such as the semantics of the labels. The same `Instance` may appear in multiple `Dataset`s.

A `Metric` is a function that takes lists of actual and target outputs and returns some description of the model's performance on that metric. The description will generally be a rich object. For example, the `ClassificationAccuracy` metric would return a confusion matrix.

A `Task` is a `Dataset` together with a collection of `Metric`s. The `Task` may also include metadata as appropriate.

# ~~Specification 0.1~~

Model outputs consist of:

- The identifier of the input instance
- A semantic description of the model's output
- Metadata about the input instance

The full metadata about the input instance would include information about the dataset, but this is too big to include in every model output record (e.g., descriptions of the interpretation of each label in ImageNet -- great white shark, white shark, man-eater, man-eating shark, Carcharodon carcharias; tiger shark, Galeocerdo cuvieri; hammerhead, hammerhead shark; etc.).

I'm imagining that each Dataset will support one or more Tasks, such as classification, object detection, etc. So the model output record should include the task that the model was solving at the time that it generated the output. The "canonical" input instance might contain information that is not to be used for some tasks. For example, an image+text dataset might be used to evaluate image classification. The semantic hash of an instance should incorporate all of the data (both image and text), but we might present only the image part to the model.

```json
{
  "model": "docker image uid",
  "input": "instance uid",
  "outputs": [
    {
      "task": "classification",
      "label": 1,
      "scores": {
        "values": [-1, 1, 0.5],
        "kind": "logits"
      }
    }
  ],
  "input_metadata": {
    "dataset": "imagenet-c-brightness-1",
    "fields": ["image"],
    "targets": [
      {
        "task": "classification",
        "label": 1
      }
    ]
  }
}
```

Ideally, we would want outputs to be composable. Object detection, for example, entails making multiple classifications about different sub-parts of the image. We'd like to re-use the "classification" structure here:

```json
{
  "model": "docker image uid",
  "input": "instance uid",
  "output": {
    "detections": [
      {
        "x": 42,
        "y": 43,
        "height": 44,
        "width": 45,
        "classification": {
          "label": 1,
          "scores": {
            "values": [-1, 1, 0.5],
            "kind": "logits"
          }
        }
      }
    ]
  }
}
```
