.. _dyff-resource-lifecycle:

The Dyff Resource Lifecycle
===========================

Every core Dyff resource has ``.status`` and ``.reason`` fields that are set by the platform to record the progress of the resource workflow. The following diagram shows the possible paths that the ``.status`` of a resource can take. The boxes with thick edges represent "terminal" statuses. ``Deleted`` is a special status that we will describe at the end of this section.

.. Note: Must use HTML 'href' here, as Sphinx :ref: doesn't work in GraphViz.
..       For hrefs in SVG images:
..         * The CWD is 'html/_img', so most hrefs will start with '../'.
..         * 'target' must set; '_top' seems to work.
.. digraph:: dyff_resource_lifecycle
    :name: Dyff Recource Lifecycle

    node [ordering=in];
    newrank=true;
    rankdir=TB;
    splines=ortho;

    {
        rank=same;

        "Created" [
            label="Created",
            shape="box",
            target="_top",
        ];

        "Admitted" [
            label="Admitted",
            shape="box",
            target="_top",
        ];

        "Success" [
            label="Complete /\nReady",
            shape="box",
            target="_top",
            style="bold",
        ];

        "Deleted" [
            label="Deleted",
            shape="box",
            target="_top",
            style="dashed",
        ];
    }

    "Failure" [
        label="Failed /\nError",
        shape="box",
        target="_top",
        style="bold",
    ];

    "Terminated" [
        label="Terminated",
        shape="box",
        target="_top",
        style="bold",
    ];

    Created -> Admitted;
    Admitted -> Success;
    Success -> Deleted;

    Created -> Failure;
    Admitted -> Failure;

    Failure -> Deleted;
    Terminated -> Deleted;

    Created -> Success;
    Created -> Terminated;
    Created -> Deleted;


    Admitted -> Terminated;
    Admitted -> Deleted;

    Success -> Failure [style=invis, weight=10];
    Failure -> Terminated [style=invis, weight=10]

.. end of graph -- graphviz thinks the next paragraph is part of the graph spec without this comment


 When you create a new resource specification in the Dyff platform, you can think of this as informing the Dyff platform that you wish for a resource with the specification you provide to exist in a "success" status -- either ``Complete`` or ``Ready``. We call the process of progressing a resource from the ``Created`` status to a terminal status the **workflow** associated with that resource. For example, the ``Evaluation`` workflow requires spinning up one or more replicas of an ``InferenceService``, feeding data to them from a ``Dataset``, and storing and verifying the outputs. (This idea of the system trying to "reconcile" the status of a resource is borrowed from how the Kubernetes platform works.)

The ``.status`` field records the last "milestone" in the workflow that has been reached. When you create a resource, it starts its lifecycle in the ``Created`` status. The ``Created`` status means that the resource specification has been added to the Dyff datastore, but no work has been done yet.

Many workflows require some computational work to happen on the Dyff platform. The ``Admitted`` status means that this computational work has begun. Specifically, it means that computation resources have been created in the Kubernetes cluster that hosts all of the Dyff platform instance's workloads. Some workflows do not result in any computation on the Dyff platform. For example, when uploading a ``Dataset``, the only "work" that happens is uploading the data from your local filesystem to URLs obtained from the Dyff API. Thus, this workflow never enters the ``Admitted`` status.

Terminal statuses can be divided into "success", "failure", and "early termination". The names of these statuses depend on the nature of the workflow. For workflows perform a computational "job", like ``Evaluations``, the success status is called ``Complete``, and the failure status is called ``Failed``. For workflows that produce an artifact that is meant to be consumed by other workflows, such as building an ``InferenceService``, the success status is called ``Ready`` and the failure status is called ``Error``. Any workflow that has not reached a terminal status may be terminated by the user, or sometimes by the Dyff platform, in which case it enters the ``Terminated`` status.


``Created`` status
------------------

The ``Created`` status means that the resource specification has been added to the Dyff datastore, but no work has been done yet. The following ``reason`` values are associated with the ``Created`` status:

    ``None``
        The ``reason`` will be ``None`` if the Dyff platform has not yet processed the resource specification. This is the ``reason`` you will see in the resource specification returned by the resource creation endpoints.

    ``QuotaLimit``
        This means that the workflow is waiting to be admitted because admitting it would cause computational resource use to exceed one or more quotas that are set for your account. For example, you may have a quota of 1 GPU on your account. If you create two ``Evaluation`` resources that each require a GPU, one of those resources will wait in the ``Created`` status with ``reason = QuotaLimit``.

    ``UnsatisfiedDependency``
        This means that your workflow depends on a resource that has not yet reached an appropriate success status. For example, you might create a ``Report`` that references the results of an ``Evaluation`` when that evaluation is still running. The report will wait in the ``Created`` status with ``reason = UnsatisfiedDepencency`` until the evaluation completes successfully.


``Admitted`` status
-------------------

The ``Admitted`` status means that computational work has begun in support of the workflow. Currently, the ``reason`` will always be ``None`` in the ``Admitted`` status.

    ``None``
        The ``reason`` will be ``None`` if the workflow is in the first "stage" of its computation. Most workflows have only one computational step, so their ``reason`` will always be ``None`` in the ``Admitted`` status.

    .. ``Unverified``
    ..     This means that an ``Evaluation`` workflow has finished processing the input data, but the inference outputs have not yet been verified for completeness and correctness.


``Ready`` and ``Completed`` status
----------------------------------

These statuses indicate that the workflow completed successfully. The ``reason`` will be ``None``.


``Failed`` and ``Error`` status
-------------------------------

These statuses indicate that something went wrong. They will always have an associated ``reason``.

    ``SchemaError``
        Applies to: all resources

        This means that there was an error when creating the Kubernetes resource manifests needed to run the computational workloads for the workflow. This is usually due to a bug in the Dyff platform; please report this to the developers.

    ``FailedDependency``
        Applies to: all resources

        This means that the workflow depends on a resource that is in a failed or deleted status.

    ``InferenceFailed``
        Applies to: ``Evaluation``

        The inference step of an evaluation workflow failed. Typically, this indicates a problem with the underlying inference service. For example, it may have raised an exception for one of the inference inputs, or it might have taken too long to return a response, resulting in a timeout error.

    ``VerificationFailed``
        Applies to: ``Evaluation``

        The verification step of an evaluation workflow failed. For example, there may be missing or duplicated responses. Usually, this is due to an internal error in the platform, as the inference step is supposed to check for these errors and retry the problematic instances. The verification step is a fail-safe that is expected to always succeed.

    ``BuildFailed``
        Applies to: ``InferenceService``

        This is seen when an ``InferenceService`` calls for building a Docker container and the container build failed.

    ``FetchFailed``
        Applies to: ``Model``

        This is seen when a ``Model`` calls for fetching model data from a remote source (e.g., downloading neural network weights from HuggingFace) and the fetch operation failed.

    ``RunFailed``
        Applies to: ``Report``

        There was an error while running a report.
