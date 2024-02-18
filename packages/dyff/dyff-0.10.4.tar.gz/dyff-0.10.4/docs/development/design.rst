Dyff Design Overview
====================

The Dyff Platform consists of two major components:

    ``dyff-operator``
        A Kubernetes `operator <https://kubernetes.io/docs/concepts/extend-kubernetes/operator/>`_ that manages a set of `custom resources <https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/>`_ . The Dyff Operator launches "workflows" composed of one or more "workflow steps" in response to creation of Dyff k8s resources.

    ``dyff-api``
        A full-featured cloud platform and Web API built around the Dyff Operator functionality. The Dyff API components include an API server, message broker, database, and various internal services that coordinate platform operations. An ``orchestrator`` service creates and manages Dyff k8s resources via the k8s API in response to Dyff API actions, and the Dyff Operator in turn does the actual work in response to these k8s resources.


Dyff Service Diagram
--------------------

This diagram summarizes the various services that make up the Dyff Platform and their interactions.

:download:`Download as PDF <dyff-service-diagram.pdf>`

.. image:: dyff-service-diagram.svg


Workflow Walkthrough
--------------------

The main task of the Dyff Platform is to execute a few different types of *workflows* on behalf of platform users. A workflow is a sequence of computational steps that realize one stage of the overall :ref:`audit pipeline <dyff-core-resources>`.

Here is a sketch of what happens when the user wants to execute an Evaluation:

    1. The user calls the ``client.evaluations.create()`` method on an instance of the Python API client.

    2. The client sends a ``POST /evaluations`` request to the ``api-server``.

    3. The ``api-server`` checks that the user-supplied bearer token grants the required permissions to create the requested Evaluation.

    4. The ``api-server`` assigns an ID to the new Evaluation, resolves references to other resources by making database queries, populates a complete new Evaluation object, produces a Create event to the ``workflows.events`` topic with the new Evaluation object, and returns the Evaluation object to the client.

    5. The ``workflows-aggregator`` consumes the ``workflows.events`` message and upserts the corresponding Evaluation object in the ``workflows.state`` topic. The ``workflows.state`` topic has ``cleanup.policy = compact`` set, so it only retains the most recent version of each object.

    6. The ``workflows-sink`` service consumes the ``workflows.state`` message and puts the updated Evaluation object in the database.

    7. Concurrently, the ``orchestrator`` consumes the ``workflows.state`` message and sees that the entity has ``.status = Created``. The orchestrator checks whether scheduling preconditions are met -- whether all dependencies are in ``.status = Ready`` and whether the user account's quotas can accommodate the workflow. If preconditions are satisfied, the orchestrator creates an ``Evaluation`` k8s resource in the cluster and produces a status change message to ``workflows.events`` like ``ID: {"status": "Admitted"}``.

    8. The ``workflows-aggregator`` updates the corresponding full object in ``workflows.state`` with the new status, and the ``workflows-sink`` propagates this change to the database.

    9. The ``dyff-operator`` sees the new ``Evaluation`` k8s resource and creates other k8s resources to execute the various steps in the Evaluation workflow. In the first step, it creates an ``InferenceSession`` k8s resource for the inference "server", and a Job running the ``evaluation_client`` image for the inference "client". ``InferenceSession`` is another k8s custom resource, and it triggers the ``dyff-operator`` to create a Deployment containing replicas of the inference model and a Service exposing the replicas on the internal network. The operator watches the client Job, and when it is complete, it starts the second step, where a ``verify_evaluation_output`` Job checks the output for completeness. As each step completes, the operator sets the ``.status.conditions`` of the k8s resource to record the progress of the workflow.

    10. The ``workflows-informer`` service watches for changes to the status of the k8s resources through the k8s API "watch" mechanism. When the k8s resource status changes, it produces a corresponding message to ``workflows.events``, such as ``ID: {"status": "Admitted", "reason": "Unverified"}`` or ``ID: {"status": "Complete"}``.

    11. Eventually, the Evaluation workflow is finished. The user calls ``client.evaluations.get(ID)``, which sends a ``GET /evaluations/ID`` request to ``api-server``, which queries the database and returns the Evaluation object with that ID. If the evaluation was successful, the object will have ``.status = Complete``.
