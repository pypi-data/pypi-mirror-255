Dyff Operator
=============

The Dyff Operator is the "kernel" of the platform. A Kubernetes `operator <https://kubernetes.io/docs/concepts/extend-kubernetes/operator/>`_ is simply a daemon process called a *controller* that watches the k8s system state for events pertaining to certain `custom resources <https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/>`_ and responds by taking actions via the k8s API.

The Dyff Operator controls the following Dyff k8s Custom Resource kinds:

    * ``Audit`` -- ``audits.dyff.io``
    * ``Evaluation`` -- ``evaluations.dyff.io``
    * ``InferenceService`` -- ``inferenceservices.dyff.io``
    * ``InferenceSession`` -- ``inferencesessions.dyff.io``
    * ``Model`` -- ``models.dyff.io``
    * ``Report`` -- ``reports.dyff.io``

We use the generic term *workflows* to refer to the computational work implied by one of these resources. For example, the *evaluation workflow* consists of:

    1. Starting a ``Deployment`` with one or more replicas of an *inference runner* container, and an associated k8s ``Service`` to provide a web interface;
    2. starting a ``Job`` that wraps an *evaluation client* container, which loads data from a dataset and performs inference on it by making HTTP requests to the inference service; and
    3. once the client job is finished, starting a ``Job`` that wraps an *output verification* container, which checks that the output of the client job is complete and correctly formatted.

When an ``Evaluation`` resource is created, the controller sees this event and creates the k8s resources needed for steps (1) and (2). The controller then watches the ``Job`` resource that wraps the evaluation client. When the job status reaches a completed state, the controller creates the additional k8s resources needed for step (3). Throughout the process, the controller sets `conditions <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#typical-status-properties>`_ on the ``/status`` subresource to indicate progress of the workflow or to signal failures.

The "steps" of each workflow are implemented as arbitrary executable programs packaged as Docker images. Currently, this code lives under ``dyff/apps``:

    ``evaluation_client``
        The "client" part of an Evaluation. Reads data from a dataset, makes inference API calls over HTTP, and writes the inference outputs to another dataset.

    ``fetch_model``
        Downloads an ML model into storage.

    ``mocks/inferenceservice``
        A mock inference service for testing.

    ``run_report``
        Does the computational work of a Report. Reads output data from an Evaluation, applies a scoring Rubric, and writes the results to another dataset.

    ``runners/vllm``
        The "server" part of an Evaluation. Uses the vLLM package to run LLMs.

    ``verify_evaluation_output``
        Checks that Evaluation outputs are complete and correctly formatted.


Design Guidelines
-----------------

Dyff Operator developers should familiarize themselves with the `Kubernetes API conventions <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md>`_ . We don't follow these to the letter, but they should be the default starting point for designing new functionality.


The Dyff Operator is a standalone component
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most important design principal for the Dyff Operator is that it should be useful by itself, using only the k8s API implemented by ``kubectl``.

    Components of the Dyff Operator MUST NOT interact with any Dyff Platform services that are not managed by the Dyff Operator itself.

..

    Dyff Operator components MUST NOT depend on the ``dyff-api`` package, only the ``dyff`` package (client components).

..

    Dyff Custom Resources MUST contain all information necessary to run the workflow.

    Specifically: If a resource A depends on a resource B, then any information about B needed to execute A should be included in the manifest of A. Workflows must not assume that other referenced resources will be present in the k8s system database.


Workflows and Workflow Steps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The controller executes workflows by creating one or more Pods that run Docker containers that implement the steps fo the workflow and passing them appropriate arguments and configuration information. The Pods usually are managed indirectly via a ``Job`` or other container resource. The controller may also create other k8s resources like ``ConfigMap``.

    Workflow Steps MUST exit with an appropriate integer status code, either zero for "sucess" or non-zero for "failure".

    Rationale: This is necessary for container resources like ``Job`` to respond to failure statuses.

..

    Workflow Steps MUST NOT interact with the Kubernetes API.


Communicating Workflow Status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Dyff Custom Resources MUST use `k8s status conditions <https://github.com/kubernetes/community/blob/master/contributors/devel/sig-architecture/api-conventions.md#typical-status-properties>`_ to indicate the progress of the workflow.

    Example:

    .. code-block:: yaml

        status:
          conditions:
            - lastTransitionTime: "2023-12-13T18:27:59Z"
              message: Evaluation is complete
              reason: Complete
              status: "True"
              type: Complete
            - lastTransitionTime: "2023-12-13T18:07:35Z"
              message: Evaluation is complete
              reason: Complete
              status: "False"
              type: Failed


Example Dyff Resource Manifest
------------------------------

This is an example of an ``Evaluation`` manifest. This example includes the ``/status`` subresource, which is managed by the Dyff Operator.

.. literalinclude :: evaluation.yaml
    :language: yaml
