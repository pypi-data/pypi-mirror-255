General Design Principles
=========================


Data Model
----------


REST-y API and data model
~~~~~~~~~~~~~~~~~~~~~~~~~

We generally adhere to REST design, where users control the platform by creating, modifying, and querying presistent resources.

Exception: API usability is more important than 100% RESTful-ness.


Data schemas
~~~~~~~~~~~~

All data objects have explicit schemas and can be converted to and from JSON data automatically. Schemas are defined using Pydantic data models. JSON is the standard data interchange format used for Kafka messages and service APIs.


Data schema versioning
~~~~~~~~~~~~~~~~~~~~~~

The schema has a *version* and a *revision*. The *revision* is incremented for incompatible changes that have a limited scope but nevertheless require data migration. The *version* is incremented for wholesale changes that would require major updates to client code. We hope that *version* will never have to be ``> 1``.

Schema changes that are both forward- and backward-compatible may be made without a *revision* increment. For example, a new optional field may be added.


Immutable data
~~~~~~~~~~~~~~

Data objects are mostly *immutable*. Each object has a unique ID, and the essential properties of an object with a given ID will never change after it has been created. Immutability is **essential** for reproducibility and long-term integrity of audit results. If two evaluations are run on a dataset with a given ID, we know for sure that they saw the same input examples, because the dataset can't be changed once created.

There are two primary exceptions: *status* information and *tags*. Every core resource has fields like ``.status`` and ``.reason`` that describe progress of the associated workflow. These obviously change during execution. In addition, core objects have some "tag" fields such as ``.labels`` that can be used to add metadata to an object after it has been created. This separation of immutable and mutable properties is strongly influenced by Kubernetes.

Data objects never totally disappear, we simply set their status to ``Deleted``, possibly delete the actual data associated with the object (such as a dataset or model weights), and forbid using them in new workflows. This way, all references to those objects remain valid.


Data object versioning
~~~~~~~~~~~~~~~~~~~~~~

.. note::

    This is not implemented yet but is on the roadmap.

Data objects can belong to a "version group" of related objects. For example, a dataset might be updated periodically with new instances. Each of these updates produces a new, immutable object with a unique ID. The version group is just an annotation that says that all of these objects are related. Following a Docker-like model, users can annotate objects in the version group with named tags such as ``latest`` to help users query them.


Distributed System Architecture
-------------------------------


Reconciliation-based execution control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Services that control computational work make their decisions by comparing the current state of the system to a desired state and taking actions to reconcile the two.

This is how Kubernetes works, too, and it just makes a lot of distributed system problems much easier to think about. For example, restarting after an error becomes fairly trivial, because it's impossible to "miss" any events during the downtime.


Message ordering, at-least-once delivery, and consumer idempotence
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Services communicate through messages sent via a Kafka broker. We design all of the Dyff services to maintain the following properties:

    1. All message consumers see messages about a given entity in the same order

    2. Messages are delivered at-least-once

    3. The current system state can be reconstructed by re-playing all the messages

At-least-once delivery semantics imply that all message consumers must be *idempotent* to duplicate message delivery.

To maintain the at-least-once invariant, message consumers have to be structured in a particular way. Specifically, they have to process messages with the following steps:

    1. Receive new incoming message

    2. Take all appropriate actions (including sending more messages) and make sure they succeeded

    3. "Commit" the incoming message so that it won't be acted on again

The "commit" step is usually acknowledging receipt of the message to Kafka, which increments the consumer's "index" in the topic and prevents that message from being replayed if the consumer reconnects. It could also be a local operation; for example, the ``orchestrator`` commits some actions by updating its local KV store. The point is that the commit happens *after* we're sure that the message has been fully processed. Any crash before the commit step will result in all of the actions being tried again.


Data persistence, eventual consistency, command-query responsibility segregation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``workflows.state`` Kafka topic is the *source of truth* for the current system state. It is replicated in the Kafka broker and backed up regularly.

Every downstream view of the system state derives from ``workflows.state``. For example, we have a MongoDB instance for querying objects in the system, but it is populated from ``workflows.state`` messages. User commands don't modify the MongoDB directly; they generate messages that eventually propagate to the DB. This general pattern is called command-query responsibility segregation (CQRS).

A consequence of this is that the global system state is inherently *eventually consistent*; it takes time for messages to propagate to downstream data views. Services that need strongly consistent datastores manage these themselves. For example, the ``orchestrator`` has a local strongly consistent KV store for keeping track of scheduling information, so that workflows aren't scheduled twice if duplicate messages are generated. Likewise, the ``api-server`` owns the authorization database and communicates with it using strongly consistent semantics.


Security
--------


TLS authentication
~~~~~~~~~~~~~~~~~~

The external API is HTTPS-only. We use ``cert-manager`` and ``letsencrypt`` to issue SSL certificates.


Least-privilege service accounts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

All services run with fine-grained service accounts that grant them the minimal permissions they need to accomplish their tasks.


Token-based authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~

API clients authenticate with bearer tokens. These are JWT tokens that contain a cryptographically-signed list of access grants. Tokens for user accounts contain a secret that can be compared to the authorization database. This allows for revoking specific user tokens. Other services use ephemeral tokens, which do not contain a secret and cannot be revoked, but which generally have a short valid lifetime.


Role-based access control (RBAC)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tokens grant permissions using an RBAC system. Access to API endpoints is granted by resource, by resource owner, by resource type, and by function. For example, a token might grant permission to:

    1. ``create`` (function) an ``Evaluation`` (type) in account ``"myaccount"`` (owner);

    2. ``consume`` (function) any ``Dataset`` (type) owned by account ``"public"`` (owner); and

    3. ``consume`` (function) the ``InferenceService`` (type) with ID ``"abc123"`` (resource).

Together, these grants are sufficient to evaluate ``"abc123"`` on any ``"public"`` dataset, using computational resources allocated to ``"myaccount"``.
